from unittest import TestCase
from unittest.mock import MagicMock

from stockstalker.parsers.parser_base import ParserBase
from stockstalker.models.product_info import ProductInfo


class TestParserBase(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestParserBase, self).__init__(*args, **kwargs)
        self.parser = ParserBase(MagicMock(), "walmart")

    def test__is_ignored_has_keyword(self):
        self.parser.ignore_title_keywords = ['red']
        info = ProductInfo(
            title='Test Product - Red Widget',
            url='test.com'
        )
        self.assertTrue(self.parser.is_ignored(info))

    def test__is_ignored_no_keyword(self):
        self.parser.ignore_title_keywords = ['green']
        info = ProductInfo(
            title='Test Product - Red Widget',
            url='test.com'
        )
        self.assertFalse(self.parser.is_ignored(info))

    def test__is_ignored_url(self):

        self.parser.ignore_urls = ['https://example.com']
        info = ProductInfo(
            title='Test Product - Red Widget',
            url='https://example.com'
        )
        self.assertTrue(self.parser.is_ignored(info))

    def test__is_ignored_non_url(self):
        self.parser.ignore_urls = ['https://example.com']
        info = ProductInfo(
            title='Test Product - Red Widget',
            url='https://google.com'
        )
        self.assertFalse(self.parser.is_ignored(info))

    def test__is_ignored_notification_sent_url(self):

        self.parser.notification_sent_urls.append('https://example.com')
        info = ProductInfo(
            title='Test Product - Red Widget',
            url='https://example.com'
        )
        self.assertTrue(self.parser.is_ignored(info))