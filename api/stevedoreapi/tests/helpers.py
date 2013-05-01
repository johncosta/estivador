import falcon

from ..resources import TaskResource, ResultResource, ResultDetailResource


class TestTaskResource(TaskResource):
    def __init__(self):
        self.called = False
        super(TestTaskResource, self).__init__()

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

    def __init__(self):
        self.called = False
        super(TestResultResource, self).__init__()

    def on_get(self, req, resp, result_id=None):
        self.called = True
        return super(TestResultResource, self).on_get(
            req, resp, result_id=result_id)


class TestResultDetailResource(ResultDetailResource):

    def __init__(self):
        self.called = False
        super(TestResultDetailResource, self).__init__()

    # Field names ordered differently than in uri template
    def on_get(self, req, resp, result_id, detail_id=None):
        self.called = True

        return super(TestResultDetailResource, self).on_get(
            req, resp, result_id, detail_id=detail_id)
