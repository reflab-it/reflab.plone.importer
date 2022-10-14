import configparser
from importlib import import_module


def load_from_file(path):

    config_parser = configparser.SafeConfigParser()
    config_parser.read(path)

    # Convert as a dict
    config  = {}
    for section in config_parser.sections():
        section_items = config_parser.items(section)
        config_items = {}
        for k, v in section_items:
            if '\n' in v:
                v_as_list = [i for i in v.split('\n') if i]
                config_items[k] = v_as_list
            else:
                config_items[k]=  v

        config[section] = config_items

    for name, module in config['tasks'].items():
        config['tasks'][name] = import_module(module).task

    for name, module in config['deserializers'].items():
        config['deserializers'][name] = import_module(module).deserialize

    for name, module in config['converters'].items():
        config['converters'][name] = import_module(module).convert

    return config
