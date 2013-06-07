Stevedore API
=============

#### Running the unit tests ####

`python run_tests.py`

#### Running the api locally ####

`python wsgi.py`

#### Running the worker process locally ####

`rqworker`

##### Sample Curls #####

curl -X GET http://localhost:80/task/
curl -X GET http://localhost:80/task/1/
curl -v http://localhost:80/task/ --data '{"repository":"johncosta/fortytwo"}'  # create a resource
curl -X GET http://localhost:80/task/1/

curl http://localhost:80/task/1/ --data '{"repository":"johncosta/fortytwo"}'   # post execution


curl -X GET http://localhost:8080/task/
curl -X GET http://localhost:8080/task/1/
curl -v http://localhost:8080/task/ --data '{"repository":"johncosta/fortytwo"}'  # create a resource
curl -X GET http://localhost:8080/task/1/

curl http://localhost:8080/task/1/ --data '{"repository":"johncosta/fortytwo"}'   # post execution
