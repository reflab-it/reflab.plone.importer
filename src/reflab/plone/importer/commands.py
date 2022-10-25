import os

from . import Importer

_DEFAULT_CFG_NAME = 'import.cfg'

def run_import(self, arg):
    """ The command expect only one optional argument to a configuration file;
        if missing checks for a file named 'import.cfg' in the current dir
    """
    arguments = [a for a in arg.split() if a]

    config_file_path = None
    if os.path.exists(_DEFAULT_CFG_NAME):
        config_file_path = os.path.abspath(_DEFAULT_CFG_NAME)

    if len(arguments) > 0:
        path_arg = arguments[0]
        if not os.path.exists(arguments[0]):
            raise FileNotFoundError(f'File does not exists: f{path_arg}')
        else:
            config_file_path = os.path.abspath(path_arg)

    if not config_file_path:
        raise FileNotFoundError(f"Create a file with name '{_DEFAULT_CFG_NAME}' in this directory or specify a path as argument")


    cmdline = (
        self.get_startup_cmd(
            self.options.python,
            "import Zope2; "
            "app = Zope2.app(); "
            "from reflab.plone.importer import Importer; "
            f"importer = Importer(app, '{config_file_path}'); "
            "importer.run(); "
        )
    )
    os.system(cmdline)