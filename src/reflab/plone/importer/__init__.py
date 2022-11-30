# -*- coding: utf-8 -*-
import json
import os
import sys

import transaction
from plone import api

from . import config, env, logging


class Importer(object):
    def __init__(self, app, config_file_path):
        confs = config.load_from_file(config_file_path)

        # Logging
        self.logger = logging.init_logger(
            confs["logging"].get("file", "/tmp/import.log"),
            level=confs["logging"].get("level", "DEBUG"),
        )
        self.logger.info(f"Initializing importer from {config_file_path}")

        # App and portal
        app = env.init_app(app)
        portal_path = confs["destination"]["portal"]
        _portal = app.unrestrictedTraverse(portal_path, None)
        if _portal is None:
            raise ValueError(f"Unable to find a portal at {portal_path}")
        self.portal = env.init_portal(_portal)

        self.running_task = None

        # Tasks and scripts
        self.pre_scripts = confs["pre_scripts"]
        self.tasks = confs["tasks"]
        self.post_scripts = confs["post_scripts"]

        # Fields deserializer
        self.deserializers = confs["deserializers"]
        self._missing_deserializers = []
        self.deserialize_keys = confs["main"].get(
            "deserialize_keys", ["fields", "properties"]
        )

        # Data converters
        self.converters = confs["converters"]

        # Data source
        _source = confs["source"]["directory"]
        if not os.path.exists(_source):
            raise ValueError(f"Missing data source dir at {_source}")
        self.source = _source

        # Data to work on
        self.data = []

        # Destination
        self.destination_container = self._traverse(
            self.portal, confs["destination"]["container"]
        )

        # Running options
        self.delete_existing = confs["main"]["delete_existing"] == 'True' and True or False
        self.limit = int(confs["main"]["limit"])
        self.ignored_types = confs["main"].get("ignored_types", [])
        self.commit = confs["main"]["commit"] == 'True' and True or False
        self.commit_frequency = int(confs["main"]["commit_frequency"])


    def _traverse(self, container, path):
        # Traversing from portal with a relative path
        if path.startswith("/"):
            path = path[1:]
        return container.unrestrictedTraverse(path, None)

    def _as_section_key_name(self, string):
        return string.lower().strip()

    def _read_data(self, path):
        """ read data.json from file system"""
        data_path = os.path.join(path, "data.json")
        if os.path.exists(data_path):
            with open(data_path, "r") as infile:
                data = json.load(infile)
        else:
            self.logger.warning("Missing data.json (%s)" % data_path)
            return None

        # Add the id from the directory name
        # TODO: manage an extra validity check here?
        data["id"] = os.path.split(path)[-1]

        # Process data with a converter if defined
        # TODO: allow other conditions, not only on portal_type?
        converters_to_use = []
        portal_type_converter = self._as_section_key_name(data["portal_type"])
        if portal_type_converter in self.converters:
            converters_to_use.append(portal_type_converter)

        for converter_name in converters_to_use:
            data = self.converters[converter_name](data)

        return data

    def deserialize_fields(self, fields, fs_path=None):
        result = {}
        for name, info in fields.items():
            field_type = self._as_section_key_name(info["type"])
            field_value = info["value"]
            if field_type in self.deserializers:
                result[name] = self.deserializers.get(field_type)(
                    field_value, fs_path=fs_path, importer=self
                )
            else:
                if field_type not in self._missing_deserializers:
                    self._missing_deserializers.append(field_type)
        return result

    def walk_data(self):
        """ Returns the existing container object with the data to be used"""
        container = None
        data = None
        for absolute_path, data in self.data:
            relative_path = os.path.relpath(absolute_path, self.source)
            parent_path = os.path.dirname(relative_path)
            container = self._traverse(self.destination_container, parent_path)
            yield container, data

    def walk_source(self):
        """ Walk filesystem source according to limit """
        for absolute_path, dirs, files in os.walk(self.source):
            if self.limit and len(self.data) > self.limit:
                self.logger.warning(
                    f"Data ready according to limit: {self.limit}"
                )
                return

            if not self.is_valid_path(absolute_path):
                continue

            yield absolute_path

    def is_valid_path(self, path):
        relative_path = os.path.relpath(path, self.source)
        # Skip root path
        if relative_path == ".":
            return False

        # skip directories for files
        if os.path.split(relative_path)[-1].startswith("_"):
            return False

        return True

    def run(self):
        # Pre scripts
        for script_name, script in self.pre_scripts.items():
            self.logger.info(f"Run pre-script '{script_name}'...")
            script(self)
            self.logger.info(f"... done {script_name}")

        # 1) Convert the filesystem structure as a list of tuple (path, data)
        #    Deserialize objects according to configuration
        self.logger.info(f"Preparing data and deserializing fields...")
        portal_types_in_source = []
        for absolute_path in self.walk_source():
            data = self._read_data(absolute_path)
            if not data:
                continue

            if data['portal_type'] in self.ignored_types:
                continue

            if data['portal_type'] not in portal_types_in_source:
                portal_types_in_source.append(data['portal_type'])

            for deserialize_key in self.deserialize_keys:
                data[deserialize_key] = self.deserialize_fields(
                    data[deserialize_key], fs_path=absolute_path
                )

            self.data.append((absolute_path, data))

        self.logger.info(f"... done")
        self.logger.info(f"Items to process for each task: {len(self.data)}")

        # Print some useful informations before running the tasks
        for field_type in self._missing_deserializers:
            self.logger.warning(f"Missing serializer for {field_type}")

        available_types = api.portal.get_tool('portal_types').objectIds()
        for pt in portal_types_in_source:
            if pt not in available_types:
                self.logger.warning(f"Portal type {pt} not registered in the portal, it will be ignored")

        # 2) Clean up data stored on the site
        if self.delete_existing:
            self.logger.info(f"Deleting all contents in destination container...")
            items_found = api.content.find(
                context=self.destination_container,
                depth=1
            )
            contents = [x.getObject() for x in items_found]
            self.logger.info(f"Deleting all items in destination folder")
            api.content.delete(objects=contents, check_linkintegrity=False)
            self.logger.info(f"...done.")

        # 3) Run all the configured tasks
        for task_name, task in self.tasks.items():
            task_commit_counter = 0
            task_total_counter = 0
            self.running_task = task_name
            self.logger.info(f"Starting subtask: {task_name}...")
            for container, data in self.walk_data():
                if container and data:
                    try:
                        task(self, container, data)
                    except Exception as e:
                        self.logger.error(f'Failed "{task_name}" inside {container.absolute_url()} with error:\n {e}')
                    except KeyboardInterrupt:
                        sys.exit(-1)
                    task_commit_counter += 1                        
                    task_total_counter += 1
                    if self.commit and self.commit_frequency and task_commit_counter >= self.commit_frequency:
                        self.logger.info(f'{task_commit_counter} taks actions run from last commit; commit...')
                        transaction.commit()
                        task_commit_counter = 0
                        self.logger.info("...completed commit of current task actions")
                        self.logger.info(f"Task '{task_name}' progress: {task_total_counter} / {len(self.data)}")
            if self.commit:
                self.logger.info(f"Final commit of task '{task_name}'")
            self.logger.info(f"...task '{task_name}' done.")

        self.running_task = None

        # Post scripts
        for script_name, script in self.post_scripts.items():
            self.logger.info(f"Run post-script '{script_name}'...")
            script(self)
            self.logger.info(f"... done {script_name}")


        # 4) Commit and exit
        if self.commit:
            self.logger.info("Start commit...")
            transaction.commit()
            self.logger.info("...completed commit")
        else:
            self.logger.warning("Commit disabled; database not changed")

        self.logger.info("Completed import")
