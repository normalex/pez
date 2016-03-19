from unittest import TestCase
from pez.models import create_schema, drop_schema

class FreshSchemaTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(FreshSchemaTestCase, self).__init__(*args, **kwargs)
        drop_schema()

    def setUp(self):
        create_schema()

    def tearDown(self):
        drop_schema()


