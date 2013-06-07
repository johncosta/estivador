import time
import random
import docker

from . import constants
from . import utils
from .models import Task, ResultDetail
from requests import HTTPError

random.seed()


def execute_worker(task_id, result_id, command, session=None, *args, **kwargs):

    print "Executing worker for task: {0}, result: {1}, command: {2}".format(
        task_id, result_id, command)
    database = kwargs.pop('database', None)
    database_options = kwargs.pop('database', None)

    try:
        session = utils.create_db_session(
            database=database, database_options=database_options)

        detail = ResultDetail.create_unique_resultdetail(session, result_id)

        # TODO: This will be expensive if there are a lot of workers.
        #       We should pass all the information we need
        task = Task.find_by_id(session, task_id)
        if not task:
            # todo logger
            print "Unable to find task with id: {0}".format(task_id)
            return

        client = docker.Client()
        try:
            detail.update_status(session, constants.RUNNING)
            container = client.create_container(task.repository, command)
            client.start(container)
            result = client.wait(container['Id'])
            detail.update_status(session, constants.COMPLETE)
            print result
        except HTTPError, httpe:
            print("Error: {0}".format(httpe))
            # TODO we really want to update the status of the "result"
            # elseware, maybe a cleanup job?
            #task.update_status(session, constants.ERROR)
            detail.update_status(session, constants.ERROR)
        # else:
        #     task.update_status(session, constants.COMPLETE)

    except Exception, e:
        print("Error: {0}".format(e))
    finally:
        utils.close_db_session(session)


def pull_docker_image(task_id, session=None, *args, **kwargs):
    """ Retrieves the docker image for the task specified

    While the image is being pulled, the status of the task is set to `pulling`

    * If the image is found and downloaded successfully,

    :param task_id:
    :param args:
    :param kwargs:
    :return:
    """
    # TODO add support for tags .3
    # TODO add support for registries backlog
    database = kwargs.pop('database', None)
    database_options = kwargs.pop('database', None)

    try:
        session = utils.create_db_session(
            database=database, database_options=database_options)

        task = Task.find_by_id(session, task_id)
        if not task:
            # todo logger
            print "Unable to find task with id: {0}".format(task_id)
            return

        client = docker.Client()

        task.update_status(session, constants.PULLING)
        try:
            response = client.pull(task.repository, tag=None, registry=None)
            print "Response: {0}".format(response) 
        except HTTPError, httpe:
            print("Error: {0}".format(httpe))
            task.update_status(session, constants.ERROR)
        else:
            task.update_status(session, constants.COMPLETE)

    except Exception, e:
        print("Error: {0}".format(e))
    finally:
        utils.close_db_session(session)
