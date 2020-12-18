from typing import Text, List, Dict, NoReturn, Optional

from bs4 import BeautifulSoup

from stockstalker.common.logging import log
from stockstalker.parsers.parser_base import ParserBase
from stockstalker.product_info import ProductInfo
from stockstalker.services.notification_svc import NotificationSvc


class WalmartParser(ParserBase):
    def __init__(self, notification_svc: NotificationSvc, search_pages: List[Text] = None,
                 product_pages: List[Text] = None, ignore_urls=None, ignore_title_keywords=None):
        super().__init__(notification_svc, search_pages, product_pages, ignore_urls, ignore_title_keywords)

    def add_search_pages(self, url: Text) -> NoReturn:
        super().add_search_pages(url)

    def add_product_page(self, url: Text) -> NoReturn:
        super().add_product_page(url)

    def is_ignored(self, data: ProductInfo) -> bool:
        return super().is_ignored(data)

    def parse_search_page(self, page) -> List[Dict]:
        pass

    def parse_product_page(self, page) -> Dict:
        pass

    def check_stock(self) -> NoReturn:
        pass

    def check_search_pages(self) -> List[Dict]:
        pass

    def check_product_pages(self) -> List[Dict]:
        pass

    def get_title_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        title_box = page.find('h1', {'class': 'prod-ProductTitle'})
        if not title_box:
            log.error('Failed to find product title box')
            return
        return title_box.text

    def _is_in_stock_product_page(self, page: BeautifulSoup) -> bool:
        add_to_cart_btn = page.find('button', {'data-tl-id': 'ProductPrimaryCTA-cta_add_to_cart_button'})
        if not add_to_cart_btn:
            log.error('Failed to get Add to Cart button')
            return False
        return True

    def _get_sku_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        pass