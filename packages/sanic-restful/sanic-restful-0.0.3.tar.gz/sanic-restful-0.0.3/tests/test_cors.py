import unittest
from flask import Flask
import sanic_restful
from sanic_restful.utils import cors
from nose.tools import assert_equals, assert_true


class CORSTestCase(unittest.TestCase):

    def test_crossdomain(self):

        class Foo(sanic_restful.Resource):
            @cors.crossdomain(origin='*')
            def get(self):
                return "data"

        app = Flask(__name__)
        api = sanic_restful.Api(app)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/')
            assert_equals(res.status_code, 200)
            assert_equals(res.headers['Access-Control-Allow-Origin'], '*')
            assert_equals(res.headers['Access-Control-Max-Age'], '21600')
            assert_true('HEAD' in res.headers['Access-Control-Allow-Methods'])
            assert_true('OPTIONS' in res.headers['Access-Control-Allow-Methods'])
            assert_true('GET' in res.headers['Access-Control-Allow-Methods'])

    def test_access_control_expose_headers(self):

        class Foo(sanic_restful.Resource):
            @cors.crossdomain(origin='*',
                              expose_headers=['X-My-Header', 'X-Another-Header'])
            def get(self):
                return "data"

        app = Flask(__name__)
        api = sanic_restful.Api(app)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/')
            assert_equals(res.status_code, 200)
            assert_true('X-MY-HEADER' in res.headers['Access-Control-Expose-Headers'])
            assert_true('X-ANOTHER-HEADER' in res.headers['Access-Control-Expose-Headers'])

    def test_no_crossdomain(self):

        class Foo(sanic_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = sanic_restful.Api(app)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/')
            assert_equals(res.status_code, 200)
            assert_true('Access-Control-Allow-Origin' not in res.headers)
            assert_true('Access-Control-Allow-Methods' not in res.headers)
            assert_true('Access-Control-Max-Age' not in res.headers)
