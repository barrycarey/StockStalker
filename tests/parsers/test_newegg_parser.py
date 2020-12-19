import os
from unittest import TestCase, mock
from unittest.mock import MagicMock
from requests.exceptions import ConnectionError, Timeout
from bs4 import BeautifulSoup

from stockstalker.parsers.newegg_parser import NeweggParser

def get_mock_response(*args, **kwargs):
    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

    if args[0] == 'http://badresponse.com':
        return MockResponse('<html></html>', 500)
    if args[0] == 'http://goodresponse.com':
        return MockResponse('<html></html>', 200)

class TestNeweggParser(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestNeweggParser, self).__init__(*args, **kwargs)
        self.parser = NeweggParser(MagicMock(), "newegg")

    def get_product_page_in_stock(self):
        with open(os.path.join(self.get_example_page_dir(), 'newegg_product_instock.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_product_page_out_of_stock(self):
        with open(os.path.join(self.get_example_page_dir(), 'newegg_product_out_of_stock.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_search_page(self):
        with open(os.path.join(self.get_example_page_dir(), 'newegg_search_page.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_search_result(self):
        with open(os.path.join(self.get_example_page_dir(), 'newegg_search_result.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_search_result_out_of_stock(self):
        with open(os.path.join(self.get_example_page_dir(), 'newegg_search_result_out_of_stock.html'), 'r') as f:
            return BeautifulSoup(f.read(), 'html.parser')

    def get_combo_product_page(self):
        with open(os.path.join(self.get_example_page_dir(), 'newegg_combo_page.html'), 'r') as f:
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



    def test__is_combo_page_no_breadcrumbs(self):
        page = self.get_combo_product_page()
        crumbs = page.find('ol', {'class': 'breadcrumb'})
        crumbs.decompose()
        self.assertTrue(self.parser._is_combo_page(page))

    def test__is_combo_page_no_current_item_return_true(self):
        page = self.get_combo_product_page()
        crumbs = page.find('ol', {'class': 'breadcrumb'})
        current = crumbs.find('li', {'class': 'is-current'})
        current.decompose()
        self.assertTrue(self.parser._is_combo_page(page))

    def test__is_combo_page_combo_not_in_title_return_false(self):
        page = self.get_combo_product_page()
        crumbs = page.find('ol', {'class': 'breadcrumb'})
        current = crumbs.find('li', {'class': 'is-current'})
        current.string = 'dummy'
        self.assertFalse(self.parser._is_combo_page(page))

    def test__is_combo_page_combo_in_title_return_true(self):
        page = self.get_combo_product_page()
        self.assertTrue(self.parser._is_combo_page(page))

    @mock.patch('stockstalker.parsers.newegg_parser.requests.get', side_effect=get_mock_response)
    def test__load_page_bad_status_return_none(self, mocked_res):
        self.assertIsNone(self.parser._load_page('http://badresponse.com'))

    @mock.patch('stockstalker.parsers.newegg_parser.requests.get', side_effect=get_mock_response)
    def test__load_page_bad_status_return_text(self, mocked_res):
        self.assertEqual(self.parser._load_page('http://goodresponse.com'), '<html></html>')

    @mock.patch('stockstalker.parsers.newegg_parser.requests.get')
    def test__load_page_exception_return_none(self, mocked_res):
        mocked_res.side_effect = ConnectionError()
        self.assertIsNone(self.parser._load_page('http://badresponse.com'))


    def test__is_in_stock_product_page_out_of_stock_false(self):
        page = self.get_product_page_out_of_stock()
        self.assertFalse(self.parser._is_in_stock_product_page(page))

    def test__is_in_stock_product_page_add_to_cart_btn_true(self):
        page = self.get_product_page_in_stock()
        self.assertTrue(self.parser._is_in_stock_product_page(page))

    def test__is_in_stock_product_page_multi_btn_true(self):
        page = BeautifulSoup("<div id='ProductBuy'><button>Notify</button><button>Add to Cart</button></div>", 'html.parser')
        self.assertTrue(self.parser._is_in_stock_product_page(page))

    def test__get_sku_from_product_page_no_breadcrumb_none(self):
        page = self.get_combo_product_page()
        crumbs = page.find('ol', {'class': 'breadcrumb'})
        crumbs.decompose()
        self.assertIsNone(self.parser._get_sku_from_product_page(page))

    def test__get_sku_from_product_page_return_sku(self):
        page = self.get_product_page_in_stock()
        self.assertEqual(self.parser._get_sku_from_product_page(page), 'N82E16883360054')

    def test__get_price_from_product_page_no_box_return_none(self):
        page = self.get_product_page_in_stock()
        page.find('div', {'class': 'product-buy-box'}).decompose()
        self.assertIsNone(self.parser._get_price_from_product_page(page))

    def test__get_price_from_product_page_return_price(self):
        page = self.get_product_page_in_stock()
        self.assertEqual('2,199', self.parser._get_price_from_product_page(page))

    def test__get_title_from_search_result_no_info_return_none(self):
        page = self.get_search_result()
        page.find('div', {'class': 'item-info'}).decompose()
        title = self.parser._get_title_from_search_result(page)
        self.assertIsNone(title)

    def test__get_title_from_search_result_no_link_none(self):
        page = self.get_search_result()
        page.find('div', {'class': 'item-info'}).find('a', {'class': 'item-title'}).decompose()
        title = self.parser._get_title_from_search_result(page)
        self.assertIsNone(title)

    def test__get_title_from_search_result_get_title(self):
        page = self.get_search_result()
        title = self.parser._get_title_from_search_result(page)
        expected = 'ABS Gladiator Gaming PC - Intel i7 10700K'
        self.assertEqual(title, expected)


    def test__get_url_from_search_result_get_url_and_title(self):
        page = self.get_search_result()
        url = self.parser._get_url_from_search_result(page)
        expected = 'https://www.newegg.com/abs-ali469/p/N82E16883360054?Item=N82E16883360054'
        self.assertEqual(url, expected)

    def test__is_in_stock_search_result_no_button_area_return_false(self):
        page = self.get_search_result()
        page.find('div', {'class': 'item-button-area'}).decompose()
        self.assertFalse(self.parser._is_in_stock_search_result(page))

    def test__is_in_stock_search_result_no_button_return_false(self):
        page = self.get_search_result()
        page.find('div', {'class': 'item-button-area'}).find('button').decompose()
        self.assertFalse(self.parser._is_in_stock_search_result(page))

    def test__is_in_stock_search_result_different_btn_text_return_false(self):
        page = self.get_search_result_out_of_stock()
        self.assertFalse(self.parser._is_in_stock_search_result(page))

    def test__is_in_stock_product_page_valid_true(self):
        page = self.get_product_page_in_stock()
        self.assertTrue(self.parser._is_in_stock_product_page(page))

    def test__get_price_from_search_result_in_stock(self):
        page = self.get_search_result()
        self.assertEqual('2,199', self.parser._get_price_from_search_result(page))

    def test__get_price_from_search_result_out_of_stock(self):
        page = self.get_search_result_out_of_stock()
        self.assertIsNone(self.parser._get_price_from_search_result(page))

    def test__get_title_from_product_page_valid_return_title(self):
        page = self.get_product_page_in_stock()
        expected = 'ABS Gladiator Gaming PC - Intel i7 10700K - GeForce RTX 3080 - G.Skill TridentZ RGB 16GB DDR4 3200MHz - 1TB Intel M.2 NVMe SSD - Cooler Master MasterLiquid ML240L RGB V2'
        self.assertEqual(expected, self.parser._get_title_from_product_page(page))

    def test__get_title_from_product_page_missing_title_return_none(self):
        page = self.get_product_page_in_stock()
        page.find('h1', {'class': 'product-title'}).decompose()
        self.assertIsNone(self.parser._get_title_from_product_page(page))