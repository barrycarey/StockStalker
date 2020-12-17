from unittest import TestCase
from unittest.mock import MagicMock

from stockstalker.parsers.walmart_parser import WalmartParser


class TestWalmartParser(TestCase):

    def test__get_sku_from_product_page_return_sku(self):
        parser = WalmartParser(MagicMock())
