from falcon.status_codes import (
    HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_SERVICE_UNAVAILABLE
)
from webtest import TestApp, AppError
from nose_parameterized import parameterized
from mock import patch
from unittest import TestCase
from sqlalchemy.exc import DBAPIError

from test_common import FreshSchemaTestCase

from pez.webapp import application
from pez.models import create_schema, drop_schema, MAXUINT64
from pez.config import configuration


route_response_map = [
    ('/v1/forward', 1),
    ('/v1/reverse', MAXUINT64),
    ('/v2/forward?count=20', range(1, 21)),
    ('/v2/reverse?count=20', range(MAXUINT64, MAXUINT64-20, -1))
]

class PezWebAppTestCase(FreshSchemaTestCase):

    def __init__(self, *args, **kwargs):
        super(PezWebAppTestCase, self).__init__(*args, **kwargs)
        self.app = TestApp(application)

    def tearDown(self):
        super(PezWebAppTestCase, self).tearDown()
        self.app.reset()

    @parameterized.expand(route_response_map)
    def test_smoke(self, uri, result):
        response = self.app.get(uri)
        self.assertEqual(response.status, HTTP_OK)
        self.assertEqual(response.json, result)

    def test_shall_fail_on_le_zero_v2(self):
        response = self.app.get(
            '/v2/forward?count=0',
            expect_errors=True
        )
        self.assertEqual(response.status, HTTP_BAD_REQUEST)

    def test_shall_fail_on_gt_max_count_v2(self):
        max_count = configuration.get('max_count')
        response = self.app.get(
            '/v2/forward?count={0}'.format(max_count + 1),
            expect_errors=True
        )
        self.assertEqual(response.status, HTTP_BAD_REQUEST)
    
    def test_shall_fail_with_404(self):
        response = self.app.get('/WRONG_BANANAS', expect_errors=True)
        self.assertEqual(response.status, HTTP_NOT_FOUND)

    def test_shall_return_help_on_options(self):
        response = self.app.options('/v2/forward')
        self.assertEqual(response.status, HTTP_OK)
        self.assertIn(u'description', response.json)
        self.assertIn(u'verbs', response.json)

    def test_shall_return_503_on_dead_db(self):
        with patch('sqlalchemy.orm.session.Session.execute') as mock_exec:
            mock_exec.side_effect = DBAPIError('Boom', 'mock', 'mock')
            response = self.app.get(
                '/v1/forward',
                expect_errors=True
            )
            self.assertEqual(response.status, HTTP_SERVICE_UNAVAILABLE)

