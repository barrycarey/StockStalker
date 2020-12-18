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

    def test__is_combo_page_no_breadcrumbs(self):
        page = BeautifulSoup('')
        self.assertTrue(self.parser._is_combo_page(page))

    def test__is_combo_page_no_current_item_return_true(self):
        page = BeautifulSoup('<ol class="breadcrumb"></ol>', 'html.parser')
        self.assertTrue(self.parser._is_combo_page(page))

    def test__is_combo_page_combo_not_in_title_return_false(self):
        page = BeautifulSoup('<ol class="breadcrumb"><li class="is-current"></li></ol>', 'html.parser')
        self.assertFalse(self.parser._is_combo_page(page))

    def test__is_combo_page_combo_in_title_return_true(self):
        page = BeautifulSoup('<ol class="breadcrumb"><li class="is-current">combo</li></ol>', 'html.parser')
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

    def test__is_in_stock_product_page_no_buy_box_false(self):
        page = BeautifulSoup("<div id='NotProductBuy'></div>", 'html.parser')
        self.assertFalse(self.parser._is_in_stock_product_page(page))

    def test__is_in_stock_product_page_no_buy_button_false(self):
        page = BeautifulSoup("<div id='ProductBuy'></div>", 'html.parser')
        self.assertFalse(self.parser._is_in_stock_product_page(page))

    def test__is_in_stock_product_page_no_add_to_cart_btn_false(self):
        page = BeautifulSoup("<div id='ProductBuy'><button>Notify</button></div>", 'html.parser')
        self.assertFalse(self.parser._is_in_stock_product_page(page))

    def test__is_in_stock_product_page_add_to_cart_btn_true(self):
        page = BeautifulSoup("<div id='ProductBuy'><button>Add to Cart</button></div>", 'html.parser')
        self.assertTrue(self.parser._is_in_stock_product_page(page))

    def test__is_in_stock_product_page_multi_btn_true(self):
        page = BeautifulSoup("<div id='ProductBuy'><button>Notify</button><button>Add to Cart</button></div>", 'html.parser')
        self.assertTrue(self.parser._is_in_stock_product_page(page))

    def test__get_sku_from_product_page_no_breadcrumb_none(self):
        page = BeautifulSoup('<ol></ol>', 'html.parser')
        self.assertIsNone(self.parser._get_sku_from_product_page(page))

    def test__get_sku_from_product_page_breadcrumb_current_no_em_none(self):
        page = BeautifulSoup('<ol class="breadcrumb"><li class="is-current">12345</li></ol>', 'html.parser')
        self.assertIsNone(self.parser._get_sku_from_product_page(page))

    def test__get_sku_from_product_page_return_sku(self):
        page = BeautifulSoup('<ol class="breadcrumb"><li class="is-current"><em>12345</em></li></ol>', 'html.parser')
        self.assertEqual(self.parser._get_sku_from_product_page(page), '12345')

    def test__get_price_from_product_page_no_box_return_none(self):
        page = BeautifulSoup('<ul><li></li></ul>', 'html.parser')
        self.assertIsNone(self.parser._get_price_from_product_page(page))

    def test__get_price_from_product_page_no_text_box_return_none(self):
        page = BeautifulSoup("<ul><li class='price-current'></li></ul>", 'html.parser')
        self.assertIsNone(self.parser._get_price_from_product_page(page))

    def test__get_title_from_search_result_no_info_return_none(self):
        page = BeautifulSoup("<div></div>", 'html.parser')
        title = self.parser._get_title_from_search_result(page)
        self.assertIsNone(title)

    def test__get_title_from_search_result_no_link_none(self):
        page = BeautifulSoup("<div class='item-info></div>", 'html.parser')
        title = self.parser._get_title_from_search_result(page)
        self.assertIsNone(title)

    def test__get_title_from_search_result_get_url_and_title(self):
        page = BeautifulSoup("<div class='item-info'><a href='www.test.com' class='item-title'>Product Title</a></div>", 'html.parser')
        title = self.parser._get_title_from_search_result(page)
        self.assertEqual(title, 'Product Title')

    def test__get_url_from_search_result_no_info_return_none(self):
        page = BeautifulSoup("<div></div>", 'html.parser')
        url = self.parser._get_url_from_search_result(page)
        self.assertIsNone(url)

    def test__get_url_from_search_result_no_link_none(self):
        page = BeautifulSoup("<div class='item-info></div>", 'html.parser')
        url = self.parser._get_url_from_search_result(page)
        self.assertIsNone(url)

    def test__get_url_from_search_result_get_url_and_title(self):
        page = BeautifulSoup("<div class='item-info'><a href='www.test.com' class='item-title'>Product Title</a></div>", 'html.parser')
        url = self.parser._get_url_from_search_result(page)
        self.assertEqual(url, 'www.test.com')

    def test__is_in_stock_no_button_area_return_false(self):
        page = BeautifulSoup("<div></div>", 'html.parser')
        self.assertFalse(self.parser._is_in_stock_search_result(page))

    def test__is_in_stock_no_button_return_false(self):
        page = BeautifulSoup("<div class='item-button-area'></div>", 'html.parser')
        self.assertFalse(self.parser._is_in_stock_search_result(page))

    def test__is_in_stock_different_btn_text_return_false(self):
        page = BeautifulSoup("<div class='item-button-area'><button>Notify</button></div>", 'html.parser')
        self.assertFalse(self.parser._is_in_stock_search_result(page))

    def test__is_in_stock_valid_btn_return_true(self):
        page = BeautifulSoup("<div class='item-button-area'><button>Add to Cart</button></div>", 'html.parser')
        self.assertTrue(self.parser._is_in_stock_search_result(page))