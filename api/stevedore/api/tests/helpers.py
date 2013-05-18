from ..resources import TaskResource, ResultResource, ResultDetailResource


class TestTaskResource(TaskResource):
    def __init__(self, database=None, database_options=None):
        super(TestTaskResource, self).__init__(
            database=database, database_options=database_options)
        self.called = False

    # Field names ordered differently than in uri template
    def on_get(self, req, resp, task_id=None):
        self.called = True
        return super(TestTaskResource, self).on_get(
            req, resp, task_id=task_id)

    def on_post(self, req, resp, task_id=None):
        self.called = True
        return super(TestTaskResource, self).on_get(
            req, resp, task_id=task_id)


class TestResultResource(ResultResource):

    def __init__(self, database=None, database_options=None):
        super(TestResultResource, self).__init__(
            database=database, database_options=database_options)
        self.called = False

    def on_get(self, req, resp, result_id=None):
        self.called = True
        return super(TestResultResource, self).on_get(
            req, resp, result_id=result_id)


class TestResultDetailResource(ResultDetailResource):

    def __init__(self, database=None, database_options=None):
        super(TestResultDetailResource, self).__init__(
            database=database, database_options=database_options)
        self.called = False

    # Field names ordered differently than in uri template
    def on_get(self, req, resp, result_id, detail_id=None):
        self.called = True

        return super(TestResultDetailResource, self).on_get(
            req, resp, result_id, detail_id=detail_id)
