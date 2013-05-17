import json
import time

from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base

from . import constants

Base = declarative_base()


class Task(Base):

    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    repository = Column(String(100), nullable=True, unique=True)
    name = Column(String(100), nullable=True)

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
            # todo use a logger
            print e
            raise e

        return task, created

    @classmethod
    def find_by_id(cls, session, task_id, task=None):
        """
        :returns task: Returns task for task_id
        """
        try:
            task = session.query(Task).filter_by(id=task_id).one()
        except Exception, e:
            # todo use a logger
            print e
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
            # todo use a logger
            print e
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
                               name=self.name))


class Result(Base):

    __tablename__ = 'result'

    id = Column(Integer, primary_key=True)
    task_id = ForeignKey(Task)
    status = Column(String(10), nullable=True, default=constants.INIT)
    submitted_at = Column(Integer, nullable=False, default=int(time.time()))
    start = Column(Integer, nullable=True, default=int(time.time()),
                   onupdate=func.unix_timestamp())
    end = Column(Integer, nullable=True, default=int(time.time()),
                 onupdate=func.unix_timestamp())
    duration = Column(Integer, nullable=True)


class ResultDetail(Base):

    __tablename__ = 'result_detail'

    id = Column(Integer, primary_key=True)
    result_id = ForeignKey(Result)
    status = Column(String(10), nullable=True, default=constants.INIT)
    submitted_at = Column(Integer, nullable=False, default=int(time.time()))
    start = Column(Integer, nullable=True, default=int(time.time()),
                   onupdate=func.unix_timestamp())
    end = Column(Integer, nullable=True, default=int(time.time()),
                 onupdate=func.unix_timestamp())
    duration = Column(Integer, nullable=True)
