import random
from typing import List, Text, Dict, NoReturn, Optional

import requests
from bs4 import BeautifulSoup, Tag

from stockstalker.common.logging import log
from stockstalker.product_info import ProductInfo
from stockstalker.services.notification_svc import NotificationSvc
from stockstalker.parsers.parser_base import ParserBase
from requests.exceptions import Timeout, ConnectionError

from stockstalker.util.constants import USER_AGENTS


class NeweggParser(ParserBase):
    def __init__(
            self,
            notification_svc: NotificationSvc,
            search_pages: List[Text] = None,
            product_pages: List[Text] = None,
            ignore_urls: List[Text] = None,
            ignore_title_keywords: List[Text] = None
    ):
        super().__init__(notification_svc, search_pages, product_pages, ignore_urls=ignore_urls,
                         ignore_title_keywords=ignore_title_keywords)

    def add_search_pages(self, url: Text) -> NoReturn:
        super().add_search_pages(url)

    def add_product_page(self, url: Text) -> NoReturn:
        super().add_product_page(url)

    def parse_search_page(self, page: BeautifulSoup) -> List[ProductInfo]:
        results = []
        result_container = page.find('div', {'class': 'list-wrap'})
        search_results = result_container.findAll('div', {'class': 'item-cell'})
        for r in search_results:
            ad_box = r.find('a', {'class': 'txt-ads-box'})
            if ad_box:
                log.info('Skipping ad in search results')
                continue
            product_data = self._get_product_data_from_search_result(r)
            if product_data:
                results.append(product_data)
        return results

    def parse_product_page(self, page: BeautifulSoup) -> Optional[ProductInfo]:
        if self._is_combo_page(page):
            return
        product_info = ProductInfo(
            url=None,
            title=page.find('h1', {'class': 'product-title'}).text,
            in_stock=self._is_in_stock_product_page(page),
            sku=self._get_sku_from_product_page(page),
            price=self._get_price_from_product_page(page)
        )
        if self.is_ignored(product_info):
            return None
        
        return product_info

    def check_stock(self) -> NoReturn:
        results = self.check_search_pages()
        results += self.check_product_pages()
        for r in results:
            if r.in_stock:
                self.notification_svc.send_notificaiton(self.format_notification(r.to_dict()), r.url)

    def check_search_pages(self) -> List[ProductInfo]:
        all_results = []
        for page in self.search_pages:
            page_source = self._load_page(page)
            if not page_source:
                log.error('Did not get page source.  Skipping %s', page)
                continue
            page = BeautifulSoup(page_source)
            all_results += self.parse_search_page(page)
        return all_results

    def check_product_pages(self) -> List[ProductInfo]:
        all_results = []
        for url in self.product_pages:
            log.info('Checking product page: %s', url)
            page_source = self._load_page(url)
            url = BeautifulSoup(page_source)
            result = self.parse_product_page(url)
            if result:
                result.url = url
                all_results.append(result)
        return all_results

    def _get_product_data_from_search_result(self, search_result: Tag) -> Optional[ProductInfo]:
        title, url = self._get_title_and_url_from_search_result(search_result)
        result = ProductInfo(
            title=title,
            url=url,
            in_stock=self._is_in_stock(search_result)
        )
        if self.is_ignored(result):
            return

        return result

    def _get_title_and_url_from_search_result(self, item: Tag):
        info_box = item.find('div', {'class': 'item-info'})
        if not info_box:
            log.error('Did not locate product info box')
            return None, None
        product_link = info_box.find('a', {'class': 'item-title'})
        if not product_link:
            log.error('Did not locate product link')
            return None, None
        url = product_link['href']
        title = product_link.text
        return title, url

    def _is_in_stock(self, search_result: Tag) -> bool:

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
        price_box = page.find('li', {'class': 'price-current'})
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

    def _load_page(self, url: Text) -> Optional[Text]:
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            r = requests.get(url, headers)
        except (ConnectionError, Timeout):
            log.error('Failed to load URL: %s', url)
            return
        if r.status_code != 200:
            log.error('Unexpected Status Code %s for URL %s', r.status_code, url)
            return
        return r.text

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