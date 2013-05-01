import falcon
import logging
import json
import socket
socket.setdefaulttimeout(10)


class GenericResource(object):
    """ All the standard resource things that every task should have

        * logging
        * database connection (TODO)
    """
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(self.LOGGING_FORMAT)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)


class TaskResource(GenericResource):

    def __init__(self):
        super(TaskResource, self).__init__()

    def on_get(self, req, resp, task_id=None):
        """Handles GET requests"""
        self.logger.debug("get: task")
        resp.status = falcon.HTTP_200

        self.logger.debug("Task ID: {0}".format(task_id))
        resp.body = 'Task Id: {0}!'.format(task_id)

    def on_post(self, req, resp, task_id=None):
        """
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
        try:
            self.logger.debug("Reading json data...")
            self.logger.debug("request: {0}".format(req))
            self.logger.debug("stream: {0}".format(req.stream))
            raw_json = req.stream.read(size=req.content_length)

            #raw_json = ''.join(req.stream.readlines())

            self.logger.debug("Done reading data: {0}".format(raw_json))
        except Exception, e:
            print "error: {0}".format(e)
            # todo use a named tuple for http errors?
            raise falcon.HTTPError(falcon.HTTP_748,
                                   'Read Error',
                                   'Could not read the request body. Must be '
                                   'them ponies again.')

        # try:
        #     thing = json.loads(raw_json, 'utf-8')
        # except ValueError:
        #     # todo use a named tuple for http errors?
        #     raise falcon.HTTPError(falcon.HTTP_753,
        #                            'Malformed JSON',
        #                            'Could not decode the request body. The '
        #                            'JSON was incorrect.')
        #
        # if not task_id:
        #     resp = self._execute_task(resp, thing)
        # else:
        #     resp = self._create_new_task(resp, thing)
        resp.status = falcon.HTTP_200
        return resp

    def _execute_task(self, resp, thing):
        resp.status = falcon.HTTP_200
        #resp.location = '/%s/things/%s' % (user_id, proper_thing.id)
        return resp

    def _create_new_task(self, resp, thing):
        resp.status = falcon.HTTP_200
        #resp.location = '/%s/things/%s' % (user_id, proper_thing.id)
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
