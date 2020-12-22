import random
from typing import List, Text, NoReturn, Dict, Optional

import requests
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent
from requests import Timeout, ConnectionError

from stockstalker.common.logging import log
from stockstalker.models.product_info import ProductInfo
from stockstalker.services.notification_svc import NotificationSvc
from stockstalker.util.constants import USER_AGENTS


class ParserBase:
    def __init__(
            self,
            notification_svc: NotificationSvc,
            name: Text,
            search_pages: List[Text] = None,
            product_pages: List[Text] = None,
            ignore_urls=None,
            ignore_title_keywords=None
    ):
        if ignore_urls is None:
            ignore_urls = []
        if ignore_title_keywords is None:
            ignore_title_keywords = []
        self.ignore_title_keywords = ignore_title_keywords
        self.ignore_urls = ignore_urls
        self.product_pages = product_pages
        self.notification_svc = notification_svc
        self.search_pages = search_pages
        self.notification_sent_urls = []

    def add_search_pages(self, url: Text) -> NoReturn:
        self.search_pages.append(url)

    def add_product_page(self, url: Text) -> NoReturn:
        self.product_pages.append(url)

    def notify_in_stock(self, products: List[ProductInfo]):
        for product in products:
            if product.in_stock:
                self.notification_svc.send_notificaiton(self.format_notification(product.to_dict()), product.url)

    def is_ignored(self, data: ProductInfo) -> bool:
        for kw in self.ignore_title_keywords:
            if kw.lower() in data.title.lower():
                log.debug('Ignore keyword %s | %s', kw, data.title)
                return True
        if data.url in self.ignore_urls:
            log.debug('Product URL in ignore list')
            return True
        if data.url in self.notification_sent_urls:
            log.debug('Already sent notification for this product')
            return True
        return False

    def parse_search_page(self, page: BeautifulSoup) -> List[ProductInfo]:
        products = []
        search_results = self._get_search_results(page)
        log.info('Loaded %s search results', len(search_results))
        for r in search_results:
            if self._is_sponsored_search_result(r):
                continue
            product_data = self._get_product_data_from_search_result(r)
            if product_data:
                products.append(product_data)
        return products

    def parse_product_page(self, page: BeautifulSoup) -> ProductInfo:

        product_info = ProductInfo(
            url=None,
            title=self._get_title_from_product_page(page),
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
        self.notify_in_stock(results)

    def check_search_pages(self) -> List[ProductInfo]:
        all_results = []
        for page in self.search_pages:
            log.info('Checking search page: %s', page)
            page_source = self._load_page(page)
            if not page_source:
                log.error('Did not get page source.  Skipping %s', page)
                continue
            page = BeautifulSoup(page_source, 'html.parser')
            all_results += self.parse_search_page(page)
        for r in all_results:
            log.debug(r)
        return all_results

    def check_product_pages(self) -> List[ProductInfo]:
        raise NotImplementedError

    def _load_page(self, url: Text, user_agent=None) -> Optional[Text]:
        ua = UserAgent(cache=False)
        try:
            headers = {'User-Agent': user_agent or ua.chrome}
            log.debug('User Agent: %s', headers['User-Agent'])
            r = requests.get(url, headers=headers)
        except (ConnectionError, Timeout):
            log.error('Failed to load URL: %s', url)
            return
        if r.status_code != 200:
            log.error('Unexpected Status Code %s for URL %s', r.status_code, url)
            return
        return r.text

    def _get_product_data_from_search_result(self, search_result: Tag) -> Optional[ProductInfo]:
        result = ProductInfo(
            title=self._get_title_from_search_result(search_result),
            url=self._get_url_from_search_result(search_result),
            in_stock=self._is_in_stock_search_result(search_result),
            price=self._get_price_from_search_result(search_result)
        )
        if self.is_ignored(result):
            return

        return result

    def _is_in_stock_search_result(self, page: BeautifulSoup) -> bool:
        raise NotImplementedError

    def _get_title_from_search_result(self, item: Tag) -> Optional[Text]:
        raise NotImplementedError

    def _get_url_from_search_result(self, item: Tag) -> Optional[Text]:
        raise NotImplementedError

    def _get_price_from_search_result(self, item: Tag) -> Optional[Text]:
        raise NotImplementedError

    def _get_title_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        raise NotImplementedError

    def _is_in_stock_product_page(self, page: BeautifulSoup) -> bool:
        raise NotImplementedError

    def _get_sku_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        raise NotImplementedError

    def _get_price_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        raise NotImplementedError

    def _get_search_results(self, page: BeautifulSoup) -> List[Tag]:
        raise NotImplementedError

    def _is_sponsored_search_result(self, result: Tag) -> bool:
        raise NotImplementedError

    def format_notification(self, data: ProductInfo):
        msg = '**Instock Alert**\n{title}\n{url}'.format(**data)
        return msg