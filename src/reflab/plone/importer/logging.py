import logging

def init_logger(path):
    logger = logging.getLogger('reflab.plone.importer')
    logger.setLevel(logging.DEBUG)

    format = logging.Formatter("%(asctime)s - %(message)s")

    # stream_handler = logging.StreamHandler()
    # stream_handler.setFormatter(format)
    # logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(path)
    file_handler.setFormatter(format)
    logger.addHandler(file_handler)
    return logger