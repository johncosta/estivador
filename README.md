Estivador
=========

The intent behind this project is to create an easy to use interface for
running arbitrary and presumably long running distributed tasks (or jobs).  It
also provides a framework for executing these arbitrary and distributed
tasks built on top of the [Docker](http://www.docker.io/) containers.

Central Job Manager
===================

![overview](waas-cjm.jpg "stevedore")

* Web UI: Web interface for humans wrapping the REST API
* REST API: Interface for interacting with the CJM
* Datastore: Tracks operational data for tasks run by the CJM
* Queue: Queue of tasks to be executed
* Workers: Light wrapper around Docker container API

How it works
============

1. You first create a docker image locally with the technology of your choice.

2. Register your job by passing the name of your container.  Once the container
image has been downloaded into the local repository, it will be available for
use by the CJM, central job manager.

3. Execute tasks.  Submit the  image to be executed, the number of executions
required for the container image, and any additional parameters.

4.  The CJM keeps track of which container ran, how many executions occurred,
the time it took to execute, and the status of the execution.

API Specification
=================

#### GET /task/ ####
Returns a set of available tasks

##### Response #####

Field | Description
:-----|------------
Id    | unique identifier for the task
Name  | human identifiable name. (unique, but not a key)

#### POST /task/ ####
Creates a new task in the system which becomes available to run.  When the task
is submitted, a job is started to pull the image into the logical respoitory.
Once complete, the task is now available for use.

##### Request #####

Field | Description | Notes
:-----|-------------|--------
repository | docker repository location (example: johncosta/redis) | required
name       | human identifiable name. (unique, but not a key)      | default: repository value

##### Response #####

Field   | Description
:-------|------------
task_id | unique identifier for the created task
status  |  SUBMITTED, IMPORTING, READY, ERROR

#### POST /task/{task_id}/ ####
Executes the requested operation for the task.

##### Operations #####
Operation | Description
:---------|------------
RUN       | Executes task {times} number of times

##### Request (RUN) #####

Field | Description | Notes
:-----|-------------|-------
task_id   | id of the task to operate on | Required as part of the post id
operation | RUN | (Optional) Default is RUN
times     | Number of times to execute | (Optional) Default is 1

##### Response (RUN) #####

Field   | Description
:-------|------------
result_id | unique id for the results related to executed tasks

#### GET /task/{task_id}/ ####
Returns any detail related to the task

#### GET /result/ ####
Returns set of results

#### GET /result/{result_id}/ ####
Returns data associated to the result

##### Response #####

Field   | Description
:-------|------------
result_id         | id of the result
task_id           | id of the task executed
status            | COMPLETE, QUEUED, RUNNING, ERROR, CANCELLED, KILLED
submitted_at      | epoch time UTC, when the tasks where submitted
start             | epoch time UTC, when the tasks where started
end               | epoch time UTC, when all the tasks where complete
duration          | seconds of execution, end minus start

#### GET /result/{result_id}/detail/ ####
Returns a set of individual result details

#### GET /result/{result_id}/detail/{detail_id}/ ####
Returns the detail for the specific result detail.

##### Response #####

Field   | Description
:-------|------------
result_id         | id of the result
detail_id         | id of the result detail
task_id           | id of the task executed
status            | COMPLETE, QUEUED, RUNNING, ERROR, CANCELLED, KILLED
submitted_at      | epoch time UTC, when the tasks where submitted
start             | epoch time UTC, when the tasks where started
end               | epoch time UTC, when all the tasks where complete
duration          | seconds of execution, end minus start
