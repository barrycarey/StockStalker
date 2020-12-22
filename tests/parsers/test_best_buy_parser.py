import os
from unittest import TestCase
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from stockstalker.parsers.best_buy_parser import BestBuyParser


class TestBestBuyParser(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestBestBuyParser, self).__init__(*args, **kwargs)
        self.parser = BestBuyParser(MagicMock(), "newegg")

    def get_product_page_in_stock(self):
        with open(os.path.join(self.get_example_page_dir(), 'bestbuy_product_instock.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_product_page_out_of_stock(self):
        with open(os.path.join(self.get_example_page_dir(), 'bestbuy_product_out_of_stock.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_search_page(self):
        with open(os.path.join(self.get_example_page_dir(), 'bestbuy_search_page.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_search_result(self):
        with open(os.path.join(self.get_example_page_dir(), 'bestbuy_search_result.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_search_result_out_of_stock(self):
        with open(os.path.join(self.get_example_page_dir(), 'best_buy_search_result_out_of_stock.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_search_result_sponsored(self):
        print(os.getcwd())
        with open(os.path.join(self.get_example_page_dir(), 'bestbuy_search_result_sponsored.html'), 'r') as f:
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

    def test__is_in_stock_search_result_true(self):
        search_result = self.get_search_result()
        self.assertTrue(self.parser._is_in_stock_search_result(search_result))

    def test__is_in_stock_search_result_false(self):
        search_result = self.get_search_result_out_of_stock()
        self.assertFalse(self.parser._is_in_stock_search_result(search_result))

    def test__is_in_stock_search_result_no_buttons_false(self):
        search_result = self.get_search_result()
        for btn in search_result.findAll('button'):
            btn.decompose()
        self.assertFalse(self.parser._is_in_stock_search_result(search_result))

    def test__get_title_from_search_result_no_title_box_none(self):
        search_result = self.get_search_result()
        search_result.find('h4', {'class': 'sku-header'}).decompose()
        self.assertIsNone( self.parser._get_title_from_search_result(search_result))

    def test__get_title_from_search_result_return_title(self):
        search_result = self.get_search_result()
        expected = 'XFX - AMD Radeon RX 580 GTS Black Edition 8GB GDDR5 PCI Express 3.0 Graphics Card - Black'
        self.assertEqual(expected, self.parser._get_title_from_search_result(search_result))

    def test__get_url_from_search_result_no_title_box_none(self):
        search_result = self.get_search_result()
        search_result.find('h4', {'class': 'sku-header'}).decompose()
        self.assertIsNone( self.parser._get_url_from_search_result(search_result))

    def test__get_url_from_search_result_return_title(self):
        search_result = self.get_search_result()
        expected = 'https://bestbuy.com/site/xfx-amd-radeon-rx-580-gts-black-edition-8gb-gddr5-pci-express-3-0-graphics-card-black/6092641.p?skuId=6092641'
        self.assertEqual(expected, self.parser._get_url_from_search_result(search_result))

    def test__get_price_from_search_result_valid_return_true(self):
        search_result = self.get_search_result()
        self.assertEqual('$229.99', self.parser._get_price_from_search_result(search_result))

    def test__get_price_from_search_result_missing_price_box_return_none(self):
        search_result = self.get_search_result()
        search_result.find('div', 'priceView-customer-price').decompose()
        self.assertIsNone(self.parser._get_price_from_search_result(search_result))

    def test__get_title_from_product_page_in_stock(self):
        page = self.get_product_page_in_stock()
        expected = 'XFX - AMD Radeon RX 580 GTS Black Edition 8GB GDDR5 PCI Express 3.0 Graphics Card - Black'
        self.assertEqual(expected, self.parser._get_title_from_product_page(page))

    def test__is_in_stock_product_page_true(self):
        page = self.get_product_page_in_stock()
        self.assertTrue(self.parser._is_in_stock_product_page(page))

    def test__is_in_stock_product_page_false(self):
        page = self.get_product_page_out_of_stock()
        self.assertFalse(self.parser._is_in_stock_product_page(page))

    def test__get_sku_from_product_page(self):
        page = self.get_product_page_in_stock()
        self.assertEqual('6092641', self.parser._get_sku_from_product_page(page))

    def test__get_price_from_product_page_in_stock(self):
        page = self.get_product_page_in_stock()
        self.assertEqual('$229.99', self.parser._get_price_from_product_page(page))

