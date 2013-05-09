import time
import random

random.seed()


def execute_worker(*args, **kwargs):

    sleeptime = random.randint(0, 5)
    time.sleep(sleeptime)

    return sleeptime
