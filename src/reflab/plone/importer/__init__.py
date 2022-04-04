# -*- coding: utf-8 -*-
from asyncio.log import logger
from . import config
from . import env
from . import logging
import os
import json
import transaction
from plone import api


class Importer(object):

    def __init__(self, app, config_file_path):
        confs = config.load_from_file(config_file_path)

        # Logging
        self.logger = logging.init_logger(confs['logging']['file'])
        self.logger.info(f"Initializing importer from {config_file_path}")

        # App and portal
        app = env.init_app(app)
        portal_path = confs['destination']['portal']
        _portal = app.unrestrictedTraverse(portal_path, None)
        if _portal is None:
            raise ValueError(f"Unable to find a portal at {portal_path}")
        self.portal = env.init_portal(_portal)

        # Tasks
        self.subtasks = confs['subtasks']

        # Fields deserializer
        self.deserializers = confs['deserializers']

        # Data source
        _source = confs['source']['directory']
        if not os.path.exists(_source):
            raise ValueError(f'Missing data source dir at {_source}')
        self.source = _source

        # Destination
        self.destination_container = self._traverse(self.portal, confs['destination']['container'])
        # Running options
        self.run_create = bool(confs['main']['create'])
        self.delete_existing = bool(confs['main']['delete_existing'])

    def _traverse(self, container, path):
        # Traversing from portal with a relative path
        if path.startswith('/'):
            path = path[1:]
        return container.unrestrictedTraverse(path, None)

    def _read_data(self, path):
        """ read data.json from file system"""
        data_path = os.path.join(path, 'data.json')
        if os.path.exists(data_path):
            with open(data_path, 'r') as infile:
                data = json.load(infile)
        else:
            self.logger.warning("Missing data.json (%s)" % data_path)
            data = None

        # Add the id from the directory name
        # TODO: manage an extra validity check here?
        if data:
            data['id'] = os.path.split(path)[-1]     

        return data


    def _deserialize_fields(self, fields):
        result = {}
        for name, info in fields.items():
            field_type = info['type']
            field_value = info['value']
            if field_type in self.deserializers:
                result[name] = self.deserializers.get(field_type)(field_value)
            else:
                self.logger.warning(f"Missing serailizer for {field_type}")
        return result

    def _create(self, container, data):
        """ add a content inside a container object and populate using data """
        id = data['id']
        if not id in container.objectIds():
            attributes = self._deserialize_fields(data['fields'])
            # need a better solution
            if 'id' in attributes.keys(): del(attributes['id'])
            print("portal type is => " + data['portal_type'])
            api.content.create(
                container = container,
                type = data['portal_type'],
                id = data['id'],
                **attributes
            )
            self.logger.info(f"Created {id} in {'/'.join(container.getPhysicalPath())}")
        else:
            self.logger.warning(f"Already exists {id} in {'/'.join(container.getPhysicalPath())}")

    def walk_source(self):
        """ Returns the existing container object with the data to be used"""
        container = None
        data = None
        for root, dirs, files in os.walk(self.source):
            path = os.path.relpath(root, self.source)
            if path == '.':
                continue

            parent_path = os.path.dirname(path)
            container = self._traverse(self.destination_container, parent_path)
            data = self._read_data(root)
            yield container, data

    def run(self):
        # getting items inside
        if self.delete_existing:
            contents = [x.getObject() for x in api.content.find(context=self.destination_container, depth=1)]
            self.logger.info(f"Deleting all items in desitnation folder")
            api.content.delete(objects=contents, check_linkintegrity=False)

        if self.run_create:
            self.logger.info('Starting creation')
            for container, data in self.walk_source():
                self.logger.info(f"Create with {container} and {data}")
                if container and data:
                    self._create(container, data)

            transaction.commit()        
            self.logger.info('Completed creation')