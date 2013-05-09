import falcon
import redis
import rq

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .. import jobs
from .. import config
from .. import utils
from ..models import Base, Task

from . import utils as api_utils


class GenericResource(object):
    """ All the standard resource things that every task should have

        * logging
        * database connection
    """
    def __init__(self):
        self.logger = utils.configure_logger(self.__class__)

        engine = create_engine('sqlite:///stevedore.db', echo=False,
                               pool_recycle=3600, echo_pool=True)
        # Create all tables stored in this metadata.
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        #session = Session()
        #Session.configure(bind=engine)


class TaskResource(GenericResource):

    def __init__(self):
        super(TaskResource, self).__init__()

        self.redis_config = config.DEFAULT
        self.q = self._create_queue()

    def _create_queue(self, name='default', *args, **kwargs):
        """ Using a default set of configuration, configure and instantiate
        a queue

        :params kwargs: pass any valid redis.StrictRedis configuration to alter
         the default values

        """
        self.redis_config.update(**kwargs)
        q = rq.Queue(name=name, connection=redis.StrictRedis(
            **self.redis_config))

        return q

    def _execute_task(self, resp, task_id, times, operation):
        resp.status = falcon.HTTP_200
        #resp.location = '/%s/things/%s' % (user_id, proper_thing.id)
        self.logger.debug("Queuing job: {0}".format(
            jobs.execute_worker.__name__))

        for i in range(0, times):
            self.q.enqueue(jobs.execute_worker, task_id, operation)

        return resp

    def _create_new_task(self, resp, repository, name):
        """ Store a new task object """
        self.logger.debug("Creating new task for ({0}, {1})".format(
            repository, name))

        task, created = Task.create_unique_task(repository, name)
        if created:
            resp.status = falcon.HTTP_201
        else:
            resp.status = falcon.HTTP_409

        resp.location = '/%s/task/%s/' % (resp, task.id)
        return resp

    def on_get(self, req, resp, task_id=None):
        """ Handles GET requests """
        tasks = []
        if task_id:
            self.logger.debug("Looking for Task with id: {0}".format(task_id))
            task = Task.find_by_id(task_id)
            resp.body = task.serialize()
        else:
            self.logger.debug("Looking for all Tasks")
            tasks.extend(Task.find_all())
            resp.body = Task.serialize_tasks(tasks)
            self.logger.debug("Found tasks: {0}".format(tasks))

        if len(tasks) > 0:
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404

        return resp

    def on_post(self, req, resp, task_id=None):
        """ Handles request/response for POSTs to /Task

        Without a Task ID:
         * Creates a new task in the system which becomes available to run.
         When the task is submitted, a job is started to pull the image into
         the logical repository. Once complete, the task is now available for
         use.

        With a Task ID:
         * Executes the requested operation for the task.
        """
        self.logger.debug("Entering on_post")
        self.logger.debug("Headers: {0}".format(req._headers))
        raw_json = api_utils._read_stream(req, self.logger)
        parsed_json = api_utils._raw_to_dict(raw_json, self.logger)

        try:

            if task_id:
                operation = parsed_json.get('operation', "RUN")
                times = parsed_json.get('times', 1)
                resp = self._execute_task(resp, task_id, times, operation)
            else:
                repository = parsed_json.get('repository', None)
                name = parsed_json.get('name', None)
                resp = self._create_new_task(resp, repository, name)
        except Exception, e:
            self.logger.error(e)

        self.logger.debug("Exiting on_post")
        return resp


class ResultResource(GenericResource):

    def __init__(self):
        super(ResultResource, self).__init__()

    def on_get(self, req, resp, result_id=None):
        """Handles GET requests"""
        self.logger.debug("get: result")
        resp.status = falcon.HTTP_200
        resp.body = 'Results!'


class ResultDetailResource(GenericResource):

    def __init__(self):
        super(ResultDetailResource, self).__init__()

    def on_get(self, req, resp, result_id, detail_id=None):
        """Handles GET requests"""
        self.logger.debug("get: result detail")
        resp.status = falcon.HTTP_200
        resp.body = 'Result Details!'
