from unittest import TestCase
from pez.config import get_configuration, DEFAULT_MAX_COUNT


class ConfigurationTestCase(TestCase):
    
    def test_max_count_defaults_on_zero(self):
        config = get_configuration(dict(PEZ_MAX_COUNT='0'))
        self.assertEqual(config.get('max_count'), DEFAULT_MAX_COUNT)

    def test_shall_fail_wrong_max_count(self):
        with self.assertRaises(ValueError):
            config = get_configuration(dict(PEZ_MAX_COUNT='WRONG'))

