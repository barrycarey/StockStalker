import os
from unittest import TestCase
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from stockstalker.parsers.walmart_parser import WalmartParser


class TestWalmartParser(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestWalmartParser, self).__init__(*args, **kwargs)
        self.parser = WalmartParser(MagicMock(), "walmart")

    def get_product_page_in_stock(self):
        with open(os.path.join(self.get_example_page_dir(), 'walmart_product_instock.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_product_page_out_of_stock(self):
        with open(os.path.join(self.get_example_page_dir(), 'walmart_product_out_of_stock.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_search_page(self):
        with open(os.path.join(self.get_example_page_dir(), 'walmart_search_page.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_search_result(self):
        with open(os.path.join(self.get_example_page_dir(), 'walmart_search_result.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_search_result_sponsored(self):
        print(os.getcwd())
        with open(os.path.join(self.get_example_page_dir(), 'walmart_search_result_sponsored.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_example_page_dir(self):
        """
        Hacky way to get the root test path.  Needed it since running single tests sets a different CWD
        :return:
        """
        path, tail = os.path.split(os.getcwd())
        while tail:
            if tail == 'tests':
                return os.path.join(path, tail, 'example_pages')
            path, tail = os.path.split(path)
            if not tail:
                break


    def test__is_in_stock_search_result_false(self):
        search_result = self.get_search_result()
        for btn in search_result.findAll('button'):
            btn.decompose()
        self.assertFalse(self.parser._is_in_stock_search_result(search_result))

    def test__is_in_stock_search_result_true(self):
        search_result = self.get_search_result()
        self.assertTrue(self.parser._is_in_stock_search_result(search_result))

    def test__get_title_from_search_result_valid(self):
        search_result = self.get_search_result()
        self.assertEqual('Sackboy: A Big Adventure, Sony, PlayStation 5',
                         self.parser._get_title_from_search_result(search_result))

    def test__get_title_from_search_result_no_title(self):
        search_result = self.get_search_result()
        title_link_a = search_result.find('a', {'class': 'product-title-link'})
        title_link_a.decompose()
        self.assertIsNone(self.parser._get_title_from_search_result(search_result))

    def test__get_url_from_search_result_valid(self):
        search_result = self.get_search_result()
        self.assertEqual('https://walmart.com//ip/Sackboy-A-Big-Adventure-Sony-PlayStation-5/637683053',
                         self.parser._get_url_from_search_result(search_result))

    def test__get_url_from_search_result_no_title(self):
        search_result = self.get_search_result()
        title_link_a = search_result.find('a', {'class': 'product-title-link'})
        title_link_a.decompose()
        self.assertIsNone(self.parser._get_url_from_search_result(search_result))

    def test__is_in_stock_product_page_true(self):
        page = self.get_product_page_in_stock()
        self.assertTrue(self.parser._is_in_stock_product_page(page))

    def test__is_in_stock_product_page_false(self):
        page = self.get_product_page_out_of_stock()
        self.assertFalse(self.parser._is_in_stock_product_page(page))

    def test__get_sku_from_product_page(self):
        page = self.get_product_page_in_stock()
        self.assertEqual('585806399', self.parser._get_sku_from_product_page(page))

    def test__get_price_from_product_page_valid(self):
        page = self.get_product_page_in_stock()
        self.assertEqual('$69.96', self.parser._get_price_from_product_page(page))

    def test__get_price_from_product_page_no_price(self):
        page = self.get_product_page_in_stock()
        price_tag = page.find('section', {'class': 'prod-PriceSection'})
        price_tag.decompose()
        self.assertIsNone(self.parser._get_price_from_product_page(page))

    def test__get_price_from_search_result_valid(self):
        page = self.get_search_result()
        self.assertEqual(self.parser._get_price_from_search_result(page), '$59.88')

    def test__get_price_from_search_result_no_price(self):
        page = self.get_search_result()
        price_tag = page.find('span', {'class': 'price-main-block'})
        price_tag.decompose()
        self.assertIsNone(self.parser._get_price_from_search_result(page))

    def test__is_sponsored_search_result_yes(self):
        page = self.get_search_result_sponsored()
        self.assertTrue(self.parser._is_sponsored_search_result(page))

    def test__is_sponsored_search_result_no(self):
        page = self.get_search_result()
        self.assertFalse(self.parser._is_sponsored_search_result(page))

    def test__get_title_from_product_page_valid_return_title(self):
        page = self.get_product_page_in_stock()
        self.assertEqual('Sony PlayStation 5 DualSense Wireless Controller', self.parser._get_title_from_product_page(page))

    def test__get_title_from_product_page_missing_title_return_none(self):
        page = self.get_product_page_in_stock()
        page.find('h1', {'class': 'prod-ProductTitle'}).decompose()
        self.assertIsNone(self.parser._get_title_from_product_page(page))