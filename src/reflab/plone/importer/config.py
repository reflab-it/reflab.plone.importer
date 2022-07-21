import configparser
from importlib import import_module


def load_from_file(path):

    config_parser = configparser.SafeConfigParser()
    config_parser.read(path)

    # Convert as a dict
    config = {s: dict(config_parser.items(s))
              for s in config_parser.sections()}

    # Convert specific options
    config['main']['create'] = bool(config['main']['create'])

    for name, module in config['subtasks'].items():
        config['subtasks'][name] = import_module(module).task

    for name, module in config['deserializers'].items():
        config['deserializers'][name] = import_module(module).deserialize

    for name, module in config['converters'].items():
        config['converters'][name] = import_module(module).convert

    return config
