import logging


LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOG_LEVEL = logging.DEBUG


def configure_logger(cls, log_level=None, stream_handling=True):
    """ Takes a python class and returns a logger for that class. Convenience
    method.

    """
    logger = logging.getLogger(cls.__name__) if cls else logging.getLogger()
    log_level = DEFAULT_LOG_LEVEL if not log_level else log_level
    logger.setLevel(log_level)

    formatter = logging.Formatter(LOGGING_FORMAT)

    if stream_handling:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger