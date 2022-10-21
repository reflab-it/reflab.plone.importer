import logging

def init_logger(path, level='DEBUG'):
    logger = logging.getLogger('reflab.plone.importer')
    level = getattr(logging, level, 'DEBUG')
    logger.setLevel(level)

    format = logging.Formatter("%(levelname)s - %(asctime)s - %(message)s")

    file_handler = logging.FileHandler(path)
    file_handler.setFormatter(format)
    logger.addHandler(file_handler)
    return logger
