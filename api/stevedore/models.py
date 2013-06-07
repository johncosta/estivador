import json
import time
import logging

from sqlalchemy import (
    Column, Integer, String, ForeignKey, func)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base

from . import constants

# can't use .utils.configure_logger due to cyclical imports
logger = logging.getLogger(__name__)

Base = declarative_base()


class Task(Base):

    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    repository = Column(String(100), nullable=True, unique=True)
    name = Column(String(100), nullable=True)
    status = Column(String(10), nullable=True, default=constants.INIT)

    @classmethod
    def create_unique_task(cls, session, repository, name, task=None,
                           created=False):
        """ Creates a task, unique by repository.

        :returns task:  Created task
        :returns created: True is a task is created, false otherwise
        """
        try:
            task = session.query(Task).filter_by(repository=repository).one()
        except NoResultFound, e:
            task = Task(repository=repository, name=name)
            session.add(task)
            session.commit()
            created = True
        except Exception, e:
            logger.error(e)
            raise e

        return task, created

    @classmethod
    def find_by_id(cls, session, task_id, task=None):
        """
        :returns task: Returns task for task_id
        """
        try:
            task = session.query(Task).filter_by(id=task_id).one()
        except NoResultFound, nrf:
            pass  # return none
        except Exception, e:
            logger.error(e)
            raise e

        return task

    @classmethod
    def find_all(cls, session):
        """
        :returns task: Returns task for task_id
        """
        tasks = []
        try:
            tasks = session.query(Task).all()
        except Exception, e:
            logger.error(e)
            raise e

        return tasks

    @classmethod
    def serialize_tasks(cls, tasks):
        """ Serializes a list of Task objects

        :param tasks: List of Task objects
        :returns json serialized list of tasks:
        """
        return json.dumps([task.serialize() for task in tasks
                           if isinstance(task, Task)])

    def serialize(self):
        return json.dumps(dict(id=self.id, repository=self.repository,
                               name=self.name, status=self.status))

    def update_status(self, session, status):
        self.status = status
        # set the start/end times explicitly
        #   we can't count on onupdate
        if status == constants.RUNNING:
            self.start = int(time.time())
        if status in (constants.COMPLETE or constants.ERROR):
            self.end = int(time.time())
            self.duration = self.end - self.start
        session.add(self)
        session.commit()
        return


class Result(Base):

    __tablename__ = 'result'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))
    command = Column(String(100), nullable=False)
    status = Column(String(10), nullable=True, default=constants.INIT)
    submitted_at = Column(Integer, nullable=False, default=int(time.time()))
    start = Column(Integer, nullable=True, default=int(time.time()),
                   onupdate=int(time.time()))
    end = Column(Integer, nullable=True, default=int(time.time()),
                 onupdate=int(time.time()))
    duration = Column(Integer, nullable=True)

    @classmethod
    def serialize_results(cls, results):
        return json.dumps([result.serialize() for result in results
                           if isinstance(result, Result)])

    def serialize(self):
        return json.dumps(dict(id=self.id,
                                task_id=self.task_id,
                                command=self.command,
                                status=self.status,
                                submitted_at=self.submitted_at,
                                start=self.start,
                                end=self.end,
                                duration=self.duration))

    @classmethod
    def create_unique_result(cls, session, task_id, command, task=None,
                             created=False):
        """ Creates a task, unique by repository.

        :param task_id: results task
        :returns result:  Created Result
        :returns created: True is a task is created, false otherwise
        """
        logger.debug("Creating result: {0}, {1}".format(task_id, command))
        result = Result(task_id=task_id, command=command)
        session.add(result)
        session.commit()
        created = True

        return result, created

    def update_status(self, session, status):
        self.status = status
        # set the start/end times explicitly
        #   we can't count on onupdate
        if status == constants.RUNNING:
            self.start = int(time.time())
        if status in (constants.COMPLETE or constants.ERROR):
            self.end = int(time.time())
            self.duration = self.end - self.start
        session.add(self)
        session.commit()
        return

    @classmethod
    def find_by_id(cls, session, result_id, result=None):
        """
        :returns task: Returns task for task_id
        """
        try:
            result = session.query(Result).filter_by(id=result_id).one()
        except NoResultFound, nrf:
            pass  # return none
        except Exception, e:
            logger.error(e)
            raise e

        return result

    @classmethod
    def find_all(cls, session):
        """
        :returns task: Returns task for task_id
        """
        results = []
        try:
            results = session.query(Result).all()
        except Exception, e:
            logger.error(e)
            raise e

        return results


class ResultDetail(Base):

    __tablename__ = 'result_detail'

    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('result.id'))
    status = Column(String(10), nullable=True, default=constants.INIT)
    submitted_at = Column(Integer, nullable=False, default=int(time.time()))
    start = Column(Integer, nullable=True, default=int(time.time()),
                   onupdate=int(time.time()))
    end = Column(Integer, nullable=True, default=int(time.time()),
                 onupdate=int(time.time()))
    duration = Column(Integer, nullable=True)

    @classmethod
    def serialize_results(cls, results):
        return json.dumps([result.serialize() for result in results
                           if isinstance(result, ResultDetail)])

    def serialize(self):
        return json.dumps(dict(id=self.id,
                                result_id=self.result_id,
                                status=self.status,
                                submitted_at=self.submitted_at,
                                start=self.start,
                                end=self.end,
                                duration=self.duration))

    @classmethod
    def create_unique_resultdetail(cls, session, result_id, task=None,
                                   created=False):
        """ Creates a task, unique by repository.

        :param task_id: results task
        :returns result:  Created Result
        :returns created: True is a task is created, false otherwise
        """
        logger.debug("Creating result detail for result: {0}".format(result_id))
        result_detail = ResultDetail(result_id=result_id)
        session.add(result_detail)
        session.commit()
        created = True

        return result_detail, created

    def update_status(self, session, status):
        self.status = status
        # set the start/end times explicitly
        #   we can't count on onupdate
        if status == constants.RUNNING:
            self.start = int(time.time())
        if status in (constants.COMPLETE or constants.ERROR):
            self.end = int(time.time())
            self.duration = self.end - self.start
        session.add(self)
        session.commit()
        return

    @classmethod
    def find_by_id(cls, session, result_id, result_detail_id, result=None):
        """
        :returns task: Returns task for task_id
        """
        try:
            result = session.query(ResultDetail).filter_by(
                result_id=result_id, id=result_detail_id).one()
        except NoResultFound, nrf:
            pass  # return none
        except Exception, e:
            logger.error(e)
            raise e

        return result

    @classmethod
    def find_all(cls, session, result_id):
        """
        :returns task: Returns task for task_id
        """
        results = []
        try:
            result_details = session.query(ResultDetail).filter_by(
                result_id=result_id).all()
        except Exception, e:
            logger.error(e)
            raise e

        return result_details
