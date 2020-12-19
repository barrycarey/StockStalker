import random
from typing import List, Text, NoReturn, Optional

import requests
from bs4 import BeautifulSoup, Tag

from stockstalker.common.logging import log
from stockstalker.models.product_info import ProductInfo
from stockstalker.services.notification_svc import NotificationSvc
from stockstalker.parsers.parser_base import ParserBase
from requests.exceptions import Timeout, ConnectionError

from stockstalker.util.constants import USER_AGENTS


class NeweggParser(ParserBase):

    def __init__(
            self,
            notification_svc: NotificationSvc,
            name: Text,
            search_pages: List[Text] = None,
            product_pages: List[Text] = None,
            ignore_urls: List[Text] = None,
            ignore_title_keywords: List[Text] = None
    ):
        super().__init__(notification_svc, name, search_pages, product_pages, ignore_urls=ignore_urls,
                         ignore_title_keywords=ignore_title_keywords)


    def add_search_pages(self, url: Text) -> NoReturn:
        super().add_search_pages(url)

    def add_product_page(self, url: Text) -> NoReturn:
        super().add_product_page(url)

    def check_product_pages(self) -> List[ProductInfo]:
        all_results = []
        for url in self.product_pages:
            log.info('Checking product page: %s', url)
            page_source = self._load_page(url)
            page = BeautifulSoup(page_source, 'html.parser')

            if self._is_combo_page(page):
                continue

            result = self.parse_product_page(page)
            if result:
                result.url = url
                all_results.append(result)
        return all_results

    def _get_title_from_search_result(self, item: Tag) -> Optional[Text]:
        info_box = item.find('div', {'class': 'item-info'})
        if not info_box:
            log.error('Did not locate product info box')
            return None
        product_link = info_box.find('a', {'class': 'item-title'})
        if not product_link:
            log.error('Did not locate product link')
            return None

        return product_link.text

    def _get_price_from_search_result(self, item: Tag) -> Optional[Text]:
        price_box = item.find('li', {'class': 'price-current'})
        if not price_box:
            log.error('Failed to find price box')
            return
        price_strong = price_box.find('strong')

        return price_strong.text if price_strong else None

    def _get_url_from_search_result(self, item: Tag) -> Optional[Text]:
        info_box = item.find('div', {'class': 'item-info'})
        if not info_box:
            log.error('Did not locate product info box')
            return None
        product_link = info_box.find('a', {'class': 'item-title'})
        if not product_link:
            log.error('Did not locate product link')
            return None
        return product_link['href']

    def _is_in_stock_search_result(self, search_result: Tag) -> bool:

        btn_box = search_result.find('div', {'class': 'item-button-area'})
        if not btn_box:
            log.error('Did not find button box')
            return False
        btn = btn_box.find('button')
        if not btn:
            log.error('Did not find button')
            return False
        log.debug('Button Text: %s', btn.text)
        if btn.text.lower().strip() == 'add to cart':
            return True
        else:
            return False

    def _get_title_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        title_box = page.find('h1', {'class': 'product-title'})
        if not title_box:
            log.error('Failed to find title box')
            return
        return title_box.text

    def _is_in_stock_product_page(self, page: BeautifulSoup) -> bool:
        buy_box = page.find('div', {'id': 'ProductBuy'})
        if not buy_box:
            return False
        buy_btns = buy_box.findAll('button')
        if not buy_btns:
            return False
        add_to_cart = next((b for b in buy_btns if b.text.strip().lower() == 'add to cart'), None)
        return True if add_to_cart else False

    def _get_sku_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        breadcrumb_box = page.find('ol', {'class': 'breadcrumb'})
        if not breadcrumb_box:
            log.error('Failed to get breadcrumb box from page')
            return
        sku_box = breadcrumb_box.find('li', {'class': 'is-current'})
        if not sku_box:
            log.error('Failed to find SKU box')
            return
        sku_text_box = sku_box.find('em')
        if not sku_text_box:
            log.error('Failed to find SKU text box')
            return
        sku = sku_text_box.text
        log.debug('Found SKU %s', sku)
        return sku

    def _get_price_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        buy_box = page.find('div', {'class': 'product-buy-box'})
        if not buy_box:
            log.error('Failed to find buy box')
            return
        price_box = buy_box.find('li', {'class': 'price-current'})
        if not price_box:
            log.error('Failed to find price box')
            return
        price_text_box = price_box.find('strong')
        if not price_text_box:
            log.error('Failed to find price text box')
            return
        price = price_text_box.text
        log.debug('Price is %s', price)
        return price

    def _get_search_results(self, page: BeautifulSoup) -> List[Tag]:
        result_container = page.find('div', {'class': 'list-wrap'})
        return result_container.findAll('div', {'class': 'item-cell'})

    def _is_combo_page(self, page: BeautifulSoup) -> bool:
        """
        Check if a given page is a combo product page.  The layout is completely different so parsing will fail
        :rtype: bool
        :param page: BeatufilSoup Object
        """
        breadcrumbs = page.find('ol', {'class': 'breadcrumb'})
        if not breadcrumbs:
            log.debug('Failed to find breadcrumbs, assuming combo page')
            return True
        current_item = breadcrumbs.find('li', {'class': 'is-current'})
        if not current_item:
            log.debug('Failed to current item in breadcrumbs, assuming combo page')
            return True
        if 'combo' in current_item.text.lower():
            log.debug('Current page is combo page')
            return True
        return False

    def _is_sponsored_search_result(self, result: Tag) -> bool:
        ad_box = result.find('a', {'class': 'txt-ads-box'})
        if ad_box:
            log.info('Skipping ad in search results')
            return True
        return False
