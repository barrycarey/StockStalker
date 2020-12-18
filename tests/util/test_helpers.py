import os
from unittest import TestCase

from stockstalker.common.exceptions import InvalidConfigDirectory
from stockstalker.util.helpers import load_configs_from_dir


class TestHelpers(TestCase):
    def test_load_configs_from_dir_invalid_dir(self):
        self.assertRaises(InvalidConfigDirectory, load_configs_from_dir, '/some/bad/dir')

    def test_load_configs_from_dir_invalid_config_no_configs(self):
        configs = load_configs_from_dir(os.path.dirname(__file__))
        self.assertTrue(len(configs) == 0)

    def test_load_configs_from_dir_invalid_config_one_config(self):
        configs = load_configs_from_dir(os.path.dirname(__file__))
        self.assertTrue(len(configs) == 1)