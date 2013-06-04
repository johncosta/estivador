import time
import random
import docker

from . import constants
from . import utils
from .models import Task
from requests import HTTPError

random.seed()


def execute_worker(*args, **kwargs):

    sleeptime = random.randint(0, 5)
    time.sleep(sleeptime)

    return sleeptime


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
            client.pull(task.repository, tag=None, registry=None)
        except HTTPError, httpe:
            print("Error: {0}".format(httpe))
            task.update_status(session, constants.ERROR)
        else:
            task.update_status(session, constants.COMPLETE)

    except Exception, e:
        print("Error: {0}".format(e))
    finally:
        utils.close_db_session(session)