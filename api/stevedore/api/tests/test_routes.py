import falcon
import falcon.testing as testing

from helpers import (
    TestTaskResource, TestResultResource, TestResultDetailResource)
from stevedore.models import Task, Result, ResultDetail
from stevedore import utils, config


"""
These tests are based off of the tests found in test_http_method_routing.py

see https://github.com/racker/falcon/blob/master/falcon/tests/test_http_method_routing.py

"""


class TaskRoutingFixture(testing.TestBase):

    database = config.TEST_DATABASE
    database_options = config.TEST_DATABASE_OPTIONS

    def before(self):
        # configure the api routes
        self.resource_task = TestTaskResource(
            database=self.database, database_options=self.database_options)
        self.api.add_route('/task/', self.resource_task)
        self.api.add_route('/task/{task_id}/', self.resource_task)

        # create any required database objects
        session = utils.create_db_session(
            database=self.database, database_options=self.database_options)
        task, created = Task.create_unique_task(
            session, "sampletask", "sampletask")
        utils.close_db_session(session)

    def test_get(self):
        self.simulate_request('/task/')
        self.assertEquals(self.srmock.status, falcon.HTTP_200)
        self.assertTrue(self.resource_task.called)

    def test_get_with_task_id(self):
        self.simulate_request('/task/1/')
        self.assertEquals(self.srmock.status, falcon.HTTP_200)
        self.assertTrue(self.resource_task.called)

    def test_post(self):
        self.simulate_request('/task/', method='POST')
        self.assertEquals(self.srmock.status, falcon.HTTP_200)
        self.assertTrue(self.resource_task.called)

    def test_post(self):
        self.simulate_request('/task/1/', method='POST')
        self.assertEquals(self.srmock.status, falcon.HTTP_200)
        self.assertTrue(self.resource_task.called)


class ResultRoutingFixture(testing.TestBase):

    database = config.TEST_DATABASE
    database_options = config.TEST_DATABASE_OPTIONS

    def before(self):
        self.resource_result = TestResultResource(
            database=self.database, database_options=self.database_options)
        self.api.add_route('/result/', self.resource_result)
        self.api.add_route('/result/{result_id}/', self.resource_result)

        session = utils.create_db_session(
            database=self.database, database_options=self.database_options)
        task, created = Task.create_unique_task(
             session, "sampletask", "sampletask")
        result, created = Result.create_unique_result(
             session, task.id, 'command')
        utils.close_db_session(session)

    def test_get(self):
        self.response = self.simulate_request('/result/')
        self.assertEquals(self.srmock.status, falcon.HTTP_200)
        self.assertTrue(self.resource_result.called)
        print self.response

    def test_get_with_result_id(self):
        self.response = self.simulate_request('/result/1/')
        self.assertEquals(self.srmock.status, falcon.HTTP_200)
        self.assertTrue(self.resource_result.called)


class ResultDetailRoutingFixture(testing.TestBase):

    database = config.TEST_DATABASE
    database_options = config.TEST_DATABASE_OPTIONS

    def before(self):
        self.resource_detail = TestResultDetailResource(
            database=self.database, database_options=self.database_options)
        self.api.add_route('/result/{result_id}/detail/', self.resource_detail)
        self.api.add_route('/result/{result_id}/detail/{detail_id}/', self.resource_detail)

        session = utils.create_db_session(
            database=self.database, database_options=self.database_options)
        task, created = Task.create_unique_task(
             session, "sampletask", "sampletask")
        result, created = Result.create_unique_result(
             session, task.id, 'command')
        resultdetail, created = ResultDetail.create_unique_resultdetail(
             session, result.id)
        utils.close_db_session(session)

    def test_get(self):
        self.simulate_request('/result/1/detail/')
        self.assertEquals(self.srmock.status, falcon.HTTP_200)
        self.assertTrue(self.resource_detail.called)

    def test_get_with_result_detail_id(self):
        self.simulate_request('/result/1/detail/1/')
        self.assertEquals(self.srmock.status, falcon.HTTP_200)
        self.assertTrue(self.resource_detail.called)
