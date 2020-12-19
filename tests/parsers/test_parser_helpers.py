from unittest import TestCase

from stockstalker.common.exceptions import NoNotificationAgents
from stockstalker.models.parser_config import ParserConfig
from stockstalker.parsers.newegg_parser import NeweggParser
from stockstalker.parsers.parser_helpers import get_parser_by_name, parser_factory


class TestParserHelpers(TestCase):

    def test_parser_factory_no_notification_agents(self):
        config = ParserConfig(
            name='test',
            links={},
            ignore_title_keywords=[],
            ignore_urls=[],
            notification_agents=[]

        )
        self.assertRaises(NoNotificationAgents, parser_factory, config)

    def test_parser_factory_invalid_notification_agents(self):
        config = ParserConfig(
            name='newegg',
            links={},
            ignore_title_keywords=[],
            ignore_urls=[],
            notification_agents=[{'name': 'discord', }]

        )
        self.assertRaises(NoNotificationAgents, parser_factory, config)

    def test_parser_factory_valid(self):

        self.assertIsInstance(parser_factory(get_parser_config()), NeweggParser)

    def test_get_parser_by_name_lower(self):
        parser_config = get_parser_config()
        parser_config.name = 'newegg'
        self.assertIsInstance(get_parser_by_name(parser_config), NeweggParser)

    def test_get_parser_by_name_upper(self):
        parser_config = get_parser_config()
        parser_config.name = 'NEWEGG'
        self.assertIsInstance(get_parser_by_name(parser_config), NeweggParser)

    def test_get_parser_by_name_non_exist(self):
        parser_config = get_parser_config()
        parser_config.name = 'dummy'
        self.assertRaises(ValueError, get_parser_by_name, parser_config)


def get_parser_config():
    return ParserConfig(
            name='newegg',
            links={'search_pages': [], 'product_pages': []},
            ignore_title_keywords=[],
            ignore_urls=[],
            notification_agents=[{'name': 'discord', 'webhook': 'test'}]

        )