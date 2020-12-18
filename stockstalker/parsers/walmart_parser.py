from typing import Text, List, Dict, NoReturn, Optional

from bs4 import BeautifulSoup, Tag

from stockstalker.common.logging import log
from stockstalker.parsers.parser_base import ParserBase
from stockstalker.product_info import ProductInfo
from stockstalker.services.notification_svc import NotificationSvc


class WalmartParser(ParserBase):

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

    def parse_search_page(self, page: BeautifulSoup) -> List[Dict]:
        pass

    def parse_product_page(self, page: BeautifulSoup) -> Dict:
        pass

    def check_stock(self) -> NoReturn:
        pass

    def check_search_pages(self) -> List[ProductInfo]:
        pass

    def check_product_pages(self) -> List[ProductInfo]:
        pass

    def _load_page(self, url: Text) -> Text:
        pass

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

    def _is_in_stock_product_page(self, page: BeautifulSoup) -> bool:
        product_overview = page.find('div', id='product-overview')
        if not product_overview:
            log.error('Failed to find product overview')
            return
        for btn in product_overview.findAll('button', {'data-tl-id': 'ProductPrimaryCTA-cta_add_to_cart_button'}):
            print(btn.text)
            if btn.text.lower() == 'add to cart':
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


    def _is_sponsored_search_result(self, result: Tag) -> bool:
        matches = result.findAll(text='Sponsored Product')
        return len(matches) > 0

    def __init__(self, notification_svc: NotificationSvc, search_pages: List[Text] = None,
                 product_pages: List[Text] = None, ignore_urls=None, ignore_title_keywords=None):
        super().__init__(notification_svc, search_pages, product_pages, ignore_urls, ignore_title_keywords)

