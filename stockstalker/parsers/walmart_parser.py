import random
from typing import Text, List, Dict, NoReturn, Optional

import requests
from bs4 import BeautifulSoup, Tag
from requests import Timeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from stockstalker.common.logging import log
from stockstalker.parsers.parser_base import ParserBase
from stockstalker.models.product_info import ProductInfo
from stockstalker.services.notification_svc import NotificationSvc
from stockstalker.util.constants import USER_AGENTS


class WalmartParser(ParserBase):

    def __init__(
            self,
            notification_svc: NotificationSvc,
            name: Text,
            search_pages: List[Text] = None,
            product_pages: List[Text] = None,
            ignore_urls=None,
            ignore_title_keywords=None
    ):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        #self.web_driver = webdriver.Chrome(options=options)
        super().__init__(notification_svc, name, search_pages, product_pages, ignore_urls, ignore_title_keywords)

    def check_product_pages(self) -> List[ProductInfo]:
        all_results = []
        for url in self.product_pages:
            log.info('Checking product page: %s', url)
            page_source = self._load_page(url)
            page = BeautifulSoup(page_source, 'html.parser')

            result = self.parse_product_page(page)
            if result:
                result.url = url
                all_results.append(result)
        return all_results

    def _load_page(self, url: Text) -> Optional[Text]:
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            r = requests.get(url, headers=headers, cookies={'next-day': 'null|true|true|null|1608350760'})
        except (ConnectionError, Timeout):
            log.error('Failed to load URL: %s', url)
            return
        if r.status_code != 200:
            log.error('Unexpected Status Code %s for URL %s', r.status_code, url)
            return
        return r.text

    def _get_price_from_search_result(self, item: Tag) -> Optional[Text]:
        price_block = item.find('span', {'class': 'price-main-block'})
        if not price_block:
            log.error('Failed to find price Block')
            return
        price_group = price_block.find('span', {'class', 'price-group'})
        if not price_group:
            log.error('Failed to find price group')
            return
        return price_group.text

    def _is_in_stock_search_result(self, item: Tag) -> bool:
        for btn in item.findAll('button'):
            if 'add to cart' in btn.text.lower():
                return True
            return False

    def _get_title_from_search_result(self, item: Tag) -> Optional[Text]:
        title_link_a = item.find('a', {'class': 'product-title-link'})
        if not title_link_a:
            log.error('Failed to find title link')
            return
        return title_link_a.text

    def _get_url_from_search_result(self, item: Tag) -> Optional[Text]:
        title_link_a = item.find('a', {'class': 'product-title-link'})
        if not title_link_a:
            log.error('Failed to find title link')
            return
        link = title_link_a['href']
        if 'walmart.com' not in link:
            link = 'https://walmart.com/' + link

        return link

    def _get_title_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        title_box = page.find('h1', {'class': 'prod-ProductTitle'})
        if not title_box:
            log.error('Failed to find title box')
            return
        return title_box.text

    def _is_in_stock_product_page(self, page: BeautifulSoup) -> bool:
        product_overview = page.find('div', id='product-overview')
        if not product_overview:
            log.error('Failed to find product overview')
            return False
        for btn in product_overview.findAll('button', {'data-tl-id': 'ProductPrimaryCTA-cta_add_to_cart_button'}):
            btn_text = btn.text.strip('\n')
            if btn_text.lower() == 'add to cart':
                return True
        return False

    def _get_sku_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        product_overview = page.find('div', id='product-overview')
        if not product_overview:
            log.error('Failed to find product overview')
            return
        item_number_box = product_overview.find('div', {'class': 'wm-item-number'})
        if not item_number_box:
            log.error('Failed to find item number box')
            return
        sku = item_number_box.text
        sku = sku.replace('Walmart # ', '').replace(' ', '').strip('\n')
        return sku

    def _get_price_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        product_overview = page.find('div', id='product-overview')
        if not product_overview:
            log.error('Failed to find product overview')
            return
        price_section = page.find('section', {'class': 'prod-PriceSection'})
        if not price_section:
            log.error('Failed to find price section')
            return
        price_section = price_section.find('span', {'class': 'price'})
        price = ''
        price += price_section.find('span', {'class': 'price-currency'}).text
        price += price_section.find('span', {'class': 'price-characteristic'}).text
        price += price_section.find('span', {'class': 'price-mark'}).text
        price += price_section.find('span', {'class': 'price-mantissa'}).text
        return price

    def _get_search_results(self, page: BeautifulSoup) -> List[Tag]:
        result_box = page.find('div', {'class': 'search-result-listview-items'})
        if not result_box:
            log.error('Failed to find search result box')
            return []
        return result_box.findAll('div', {'data-automation-id' :'search-result-listview-item'})

    def _is_sponsored_search_result(self, result: Tag) -> bool:
        matches = result.findAll(text='Sponsored Product')
        return len(matches) > 0



