import logging
import config
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOG_LEVEL = logging.DEBUG


def configure_logger(cls=None, log_level=None, stream_handling=True):
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


def create_db_session(database=None, database_options=None):

    if not database:
        database = config.DEFAULT_DATABASE
    if not database_options:
        database_options = config.DEFAULT_DATABASE_OPTIONS

    # create the initial connection
    engine = create_engine(database, **database_options)
    # Create all tables stored in this metadata.
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def close_db_session(session):
    try:
        session.close()
    except:
        pass
    return
