from typing import List, Text, NoReturn, Dict, Optional

from bs4 import Tag, BeautifulSoup

from stockstalker.common.logging import log
from stockstalker.models.product_info import ProductInfo
from stockstalker.services.notification_svc import NotificationSvc
from stockstalker.parsers.parser_base import ParserBase


class BestBuyParser(ParserBase):

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

    def _is_in_stock_search_result(self, page: BeautifulSoup) -> bool:
        price_block = page.find('div', {'class': 'price-block'})
        if not price_block:
            log.error('Failed to find price block')
            return False
        add_to_cart_btn = price_block.find('button', {'class': 'add-to-cart-button'})
        if not add_to_cart_btn:
            log.error('Failed to find add to cart button')
            return False
        if add_to_cart_btn.text.lower() == 'add to cart':
            return True
        return False

    def _get_title_from_search_result(self, item: Tag) -> Optional[Text]:
        title_box = item.find('h4', {'class': 'sku-header'})
        if not title_box:
            log.error('Failed to find title box')
            return
        title_a = title_box.find('a')
        if not title_a:
            log.error('Failed to find title a tag')
            return
        return title_a.text

    def _get_url_from_search_result(self, item: Tag) -> Optional[Text]:
        title_box = item.find('h4', {'class': 'sku-header'})
        if not title_box:
            log.error('Failed to find title box')
            return
        title_a = title_box.find('a')
        if not title_a:
            log.error('Failed to find title a tag')
            return
        url = title_a['href']
        if 'bestbuy.com' not in url:
            url = 'https://bestbuy.com' + url
        return url

    def _get_price_from_search_result(self, item: Tag) -> Optional[Text]:
        price_box = item.find('div', {'class': 'priceView-customer-price'})
        if not price_box:
            log.error('Failed to get price box')
            return
        price_span = price_box.find('span')
        if not price_span:
            log.error('Failed to find price span')
            return
        return price_span.text

    def _get_title_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        title_box = page.find('div', {'class': 'sku-title'})
        if not title_box:
            log.error('Failed to find title box')
            return
        return title_box.text

    def _is_in_stock_product_page(self, page: BeautifulSoup) -> bool:
        add_to_cart_box = page.find('div', {'class': 'fulfillment-add-to-cart-button'})
        if not add_to_cart_box:
            log.error('Failed to find add  to cart button')
            return False
        add_to_cart_btn = add_to_cart_box.find('button')
        if not add_to_cart_btn:
            log.error('Failed to find add to cart button')
            return False
        if add_to_cart_btn.text.lower() == 'add to cart':
            return True
        return False

    def _get_sku_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        sku_box = page.find('div', {'class': 'sku product-data'})
        if not sku_box:
            log.error('Failed to find SKU box')
            return
        sku_value = sku_box.find('span', {'class': 'product-data-value'})
        if not sku_value:
            log.error('Failed to find SKU value')
            return
        return sku_value.text.strip()

    def _get_price_from_product_page(self, page: BeautifulSoup) -> Optional[Text]:
        price_box = page.find('div', {'class': 'priceView-customer-price'})
        if not price_box:
            log.error('Failed to find price box')
            return
        price_span = price_box.find('span')
        if not price_span:
            log.error('Failed to find Price Span')
            return
        return price_span.text.strip()

    def _get_search_results(self, page: BeautifulSoup) -> List[Tag]:
        return page.findAll('li', {'class': 'sku-item'})

    def _is_sponsored_search_result(self, result: Tag) -> bool:
        pass

    def _load_page(self, url: Text, user_agent=None) -> Optional[Text]:
        # For some reason most user agents cause request to time out
        ua = 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)'
        return super(BestBuyParser, self)._load_page(url, user_agent=ua)