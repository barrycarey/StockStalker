from unittest import TestCase
from unittest.mock import MagicMock

from stockstalker.parsers.parser_base import ParserBase
from stockstalker.product_info import ProductInfo


class TestParserBase(TestCase):

    def test__is_ignored_has_keyword(self):
        parser_base = ParserBase(MagicMock(), ignore_title_keywords=['red'])
        info = ProductInfo(
            title='Test Product - Red Widget',
            url='test.com'
        )
        self.assertTrue(parser_base.is_ignored(info))

    def test__is_ignored_no_keyword(self):
        parser_base = ParserBase(MagicMock(), ignore_title_keywords=['green'])
        info = ProductInfo(
            title='Test Product - Red Widget',
            url='test.com'
        )
        self.assertFalse(parser_base.is_ignored(info))

    def test__is_ignored_url(self):
        parser_base = ParserBase(MagicMock())
        parser_base.ignore_urls = ['https://example.com']
        info = ProductInfo(
            title='Test Product - Red Widget',
            url='https://example.com'
        )
        self.assertTrue(parser_base.is_ignored(info))

    def test__is_ignored_non_url(self):
        parser_base = ParserBase(MagicMock())
        parser_base.ignore_urls = ['https://example.com']
        info = ProductInfo(
            title='Test Product - Red Widget',
            url='https://google.com'
        )
        self.assertFalse(parser_base.is_ignored(info))

    def test__is_ignored_notification_sent_url(self):
        parser_base = ParserBase(MagicMock())
        parser_base.notification_sent_urls.append('https://example.com')
        info = ProductInfo(
            title='Test Product - Red Widget',
            url='https://example.com'
        )
        self.assertTrue(parser_base.is_ignored(info))