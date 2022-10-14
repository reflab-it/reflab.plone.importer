# -*- coding: utf-8 -*-
import json
import os

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

        # Tasks
        self.tasks = confs["tasks"]

        # Fields deserializer
        self.deserializers = confs["deserializers"]
        self._missing_deserializers = []

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
            data = None

        # Add the id from the directory name
        # TODO: manage an extra validity check here?
        if data:
            data["id"] = os.path.split(path)[-1]

        # Process data with a converter if defined
        try:
            converter_name = self._as_section_key_name(data["portal_type"])
        except:
            import pdb; pdb.set_trace()
            

        if converter_name in self.converters:
            data = self.converters[converter_name](data)

        # TODO
        # evaluate if deserialize_fields should be called here or in the tasks
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
        # 1) Convert the filesystem structure as a list of tuple (path, data) 
        #    Deserialize objects according to configuration
        for absolute_path in self.walk_source():
            data = self._read_data(absolute_path)
            # Todo: create a configuration of keys with objects to deserialize?
            data["fields"] = self.deserialize_fields(
                data["fields"], fs_path=absolute_path
            )
            data["properties"] = self.deserialize_fields(
                data["properties"], fs_path=absolute_path
            )            
            self.data.append((absolute_path, data))

        for field_type in self._missing_deserializers:    
            self.logger.warning(f"Missing serializer for {field_type}")

        # 2) Clean up data stored on the site
        if self.delete_existing:
            items_found = api.content.find(
                context=self.destination_container,
                depth=1
            )
            contents = [x.getObject() for x in items_found]
            self.logger.info(f"Deleting all items in destination folder")
            api.content.delete(objects=contents, check_linkintegrity=False)

        # 3) Run all the configured tasks
        task_counter = 0
        for task_name, task in self.tasks.items():
            self.running_task = task_name
            self.logger.info(f"Starting subtask: {task_name}")
            for container, data in self.walk_data():
                if container and data:
                    task(self, container, data)
                    task_counter += 1
                    if self.commit and self.commit_frequency and task_counter >= self.commit_frequency:
                        self.logger.info(f'{task_counter} taks actions run; commit...')
                        transaction.commit()
                        task_counter = 0
                        self.logger.info("...completed commit of current task actions")            

        self.running_task = None

        # 4) Commit and exit
        if self.commit:
            self.logger.info("Start commit...")
            transaction.commit()
            self.logger.info("...completed commit")
        else:
            self.logger.warning("Commit disabled; database not changed")

        self.logger.info("Completed import")
