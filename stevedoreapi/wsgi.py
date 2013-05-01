import falcon

# falcon.API instances are callable WSGI apps
from resources import TaskResource, ResultResource


wsgi_app = api = falcon.API()

# Resources are represented by long-lived class instances
task = TaskResource()
result = ResultResource()


# things will handle all requests to the '/things' URL path
api.add_route('/task', task)
api.add_route('/result', result)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, wsgi_app)
    srv.serve_forever()