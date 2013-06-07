import falcon
import redis
import rq

from .. import jobs
from .. import config
from .. import utils
from ..models import Task, Result, ResultDetail

from .. import constants
from . import utils as api_utils


class GenericResource(object):
    """ All the standard resource things that every task should have

        * logging
        * database connection configuration
    """
    def __init__(self, database=None, database_options=None):
        """
        Database configuration options can be injected to control which
        database the application connects to.

        :param database:
        :param database_options:
        :return:
        """
        self.logger = utils.configure_logger(self.__class__)
        self.database = database if database else config.DEFAULT_DATABASE
        self.database_options = (database_options if database_options
                                 else config.DEFAULT_DATABASE_OPTIONS)


class TaskResource(GenericResource):

    def __init__(self, database=None, database_options=None):
        super(TaskResource, self).__init__(
            database=database, database_options=database_options)

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

    def _execute_task(self, resp, task_id, command, times, operation,
                      session=None, result_id=None):

        self.logger.debug(
            "Entering _execute_task: \ntaskid: {0}\ncommand: {1}\ntimes: {2}"
            "\noperation: {3}".format(task_id, command, times, operation))
        if not command:
            resp.status = falcon.HTTP_400
            return resp

        # self.logger.debug("Queuing job: {0}".format(
        #     jobs.execute_worker.__name__))

        try:
            # create a result object
            session = utils.create_db_session(
                database=self.database, database_options=self.database_options)
            result, created = Result.create_unique_result(
                session, task_id, command)

            result.update_status(session, constants.RUNNING)
            for i in range(0, times):
                self.q.enqueue(jobs.execute_worker, task_id, result.id, command)
            #TODO: how do we know when these tasks are complete?

        except Exception, e:
            self.logger.error("Error: {0}".format(e))
            resp.status = falcon.HTTP_500
        finally:
            utils.close_db_session(session)

        resp.status = falcon.HTTP_200
        resp.location = '/%s/task/%s/' % (resp, result.id)

        return resp

    def _create_new_task(self, resp, repository, name, session=None):
        """ Store a new task object """
        self.logger.debug("Creating new task for ({0}, {1})".format(
            repository, name))
        try:
            session = utils.create_db_session(
                database=self.database, database_options=self.database_options)

            task, created = Task.create_unique_task(session, repository, name)

            if created:
                resp.status = falcon.HTTP_201
                self.q.enqueue(jobs.pull_docker_image,
                               args=(task.id,),
                               kwargs={
                                   'database': self.database,
                                   'database_options': self.database_options})
            else:
                resp.status = falcon.HTTP_409

            resp.location = '/%s/task/%s/' % (resp, task.id)
        except Exception, e:
            self.logger.error("Error: {0}".format(e))
            resp.status = falcon.HTTP_500
        finally:
            utils.close_db_session(session)

        return resp

    def on_get(self, req, resp, task_id=None, session=None):
        """ Handles request/response for GET to /task

        Without a task id:
         * Returns a set of available tasks

        With a task id:
         * Returns any detail related to the task
        """
        try:
            session = utils.create_db_session(
                database=self.database, database_options=self.database_options)
            if task_id:
                self.logger.debug("Looking for Task with id: {0}".format(task_id))
                task = Task.find_by_id(session, task_id)
                self.logger.debug("Found task: {0}".format(task))
                if task:
                    resp.body = task.serialize()
                    resp.status = falcon.HTTP_200
                else:
                    resp.status = falcon.HTTP_404
            else:
                self.logger.debug("Looking for all Tasks")
                tasks = []
                tasks.extend(Task.find_all(session))
                self.logger.debug("Found tasks: {0}".format(tasks))

                resp.body = Task.serialize_tasks(tasks)
                resp.status = falcon.HTTP_200
        except Exception, e:
            self.logger.error("Error: {0}".format(e))
            resp.status = falcon.HTTP_500
        finally:
            utils.close_db_session(session)

        return resp

    def on_post(self, req, resp, task_id=None):
        """ Handles request/response for POSTs to /task

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

        if task_id:
            operation = parsed_json.get('operation', "RUN")
            times = parsed_json.get('times', 1)
            command = parsed_json.get('command', None)
            resp = self._execute_task(resp, task_id, command, times, operation)
        else:
            repository = parsed_json.get('repository', None)
            name = parsed_json.get('name', None)
            command = parsed_json.get('command', None)
            resp = self._create_new_task(resp, repository, name)

        self.logger.debug("Exiting on_post")
        return resp


class ResultResource(GenericResource):

    def __init__(self, database=None, database_options=None):
        super(ResultResource, self).__init__(
            database=database, database_options=database_options)

    def on_get(self, req, resp, result_id=None):
        """Handles GET requests"""
        try:
            session = utils.create_db_session(
                database=self.database, database_options=self.database_options)
            if result_id:
                self.logger.debug("Looking for result with id: {0}".format(
                    result_id))
                result = Result.find_by_id(session, result_id)
                self.logger.debug("Found result: {0}".format(result))
                if result:
                    resp.body = result.serialize()
                    resp.status = falcon.HTTP_200
                else:
                    resp.status = falcon.HTTP_404
            else:
                self.logger.debug("Looking for all results")
                results = []
                results.extend(Result.find_all(session))
                self.logger.debug("Found results: {0}".format(results))

                resp.body = Result.serialize_results(results)
                resp.status = falcon.HTTP_200
        except Exception, e:
            self.logger.error("Error: {0}".format(e))
            resp.status = falcon.HTTP_500
        finally:
            utils.close_db_session(session)

        return resp


class ResultDetailResource(GenericResource):

    def __init__(self, database=None, database_options=None):
        super(ResultDetailResource, self).__init__(
            database=database, database_options=database_options)

    def on_get(self, req, resp, result_id, detail_id=None):
        """Handles GET requests"""
        self.logger.debug("get: result detail")
        resp.status = falcon.HTTP_200
        resp.body = 'Result Details!'

    def on_get(self, req, resp, result_id, detail_id=None):
        """Handles GET requests"""
        try:
            session = utils.create_db_session(
                database=self.database, database_options=self.database_options)
            if detail_id:
                self.logger.debug(
                    "Looking for result detail with id: {0}".format(result_id))
                result = ResultDetail.find_by_id(session, result_id, detail_id)
                self.logger.debug("Found result: {0}".format(result))
                if result:
                    resp.body = result.serialize()
                    resp.status = falcon.HTTP_200
                else:
                    resp.status = falcon.HTTP_404
            else:
                self.logger.debug("Looking for all results")
                result_details = []
                result_details.extend(ResultDetail.find_all(session, result_id))
                self.logger.debug(
                    "Found result details: {0}".format(result_details))

                resp.body = ResultDetail.serialize_results(result_details)
                resp.status = falcon.HTTP_200
        except Exception, e:
            self.logger.error("Error: {0}".format(e))
            resp.status = falcon.HTTP_500
        finally:
            utils.close_db_session(session)

        return resp