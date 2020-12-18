from unittest import TestCase

from stockstalker.parsers.newegg_parser import NeweggParser
from stockstalker.parsers.parser_helpers import get_parser_by_name


class Test(TestCase):

    def test_parser_factory(self):
        self.fail()

    def test_get_parser_by_name_lower(self):
        result = get_parser_by_name('newegg')
        self.assertIsInstance(result, NeweggParser)

    def test_get_parser_by_name_upper(self):
        result = get_parser_by_name('NEWEGG')
        self.assertIsInstance(result, NeweggParser)

    def test_get_parser_by_name_non_exist(self):
        self.assertRaises(ValueError, get_parser_by_name, 'DUMMY')

