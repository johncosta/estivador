import falcon

""" To run the application locally: python wsgi.py """

# falcon.API instances are callable WSGI apps
from stevedoreapi.resources import (
    TaskResource, ResultResource, ResultDetailResource)


def check_media_type(req, resp, params):
    if not req.client_accepts_json():
        raise falcon.HTTPUnsupportedMediaType(
            'Media Type not Supported',
            'This API only supports the JSON media type.',
            'http://docs.examples.com/api/json')


wsgi_app = api = falcon.API()

# Resources are represented by long-lived class instances
task = TaskResource()
result = ResultResource()
result_detail = ResultDetailResource()

# things will handle all requests to the '/things' URL path
api.add_route('/task/', task)
api.add_route('/task/{task_id}/', task)
api.add_route('/result/', result)
api.add_route('/result/{result_id}/', result)
api.add_route('/result/{result_id}/detail/', result_detail)
api.add_route('/result/{result_id}/detail/{detail_id}/', result_detail)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, wsgi_app)
    print "Starting server http://localhost:8080"
    srv.serve_forever()
