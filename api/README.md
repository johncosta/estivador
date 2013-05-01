Stevedore API
=============

#### Running the unit tests ####

`python run_tests.py`

#### Running the api locally ####

`python wsgi.py`

##### Sample Curls #####

curl -X GET http://localhost:8080/task/
curl -X GET http://localhost:8080/task/1/
curl -X POST http://localhost:8080/task/1/
curl -v --dump-header - -X POST -o - -H "Content-Type: application/json" -H "Accept: application/json" http://localhost:8080/task/1/ --data "{12312}"
curl http://localhost:8080/task/1/ --data "{12312}"  # shorter version of the above