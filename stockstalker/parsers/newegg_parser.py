from typing import List, Text, Dict, NoReturn, Optional

from bs4 import BeautifulSoup, Tag

from stockstalker.common.logging import log
from stockstalker.notifyagents.discord_agent import DiscordAgent
from stockstalker.product_info import ProductInfo
from stockstalker.services.notification_svc import NotificationSvc
from stockstalker.parsers.parser_base import ParserBase


class NeweggParser(ParserBase):
    def __init__(
            self,
            notification_svc: NotificationSvc,
            search_pages: List[Text] = None,
            product_pages: List[Text] = None,
            web_driver: Text = None,
            ignore_urls: List[Text] = None,
            ignore_title_keywords: List[Text] = None
    ):
        super().__init__(notification_svc, search_pages, product_pages, web_driver=web_driver, ignore_urls=ignore_urls,
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

    def parse_product_page(self, page: BeautifulSoup) -> ProductInfo:
        title = page.find('h1', {'class': 'product-title'}).text
        price_box = page.find('price-current')
        if price_box:
            price = price_box.find('strong').text

    def check_stock(self) -> NoReturn:
        results = self.check_search_pages()
        for r in results:
            if r.in_stock:
                self.notification_svc.send_notificaiton(self.format_notification(r.to_dict()), r.url)

    def check_search_pages(self) -> List[ProductInfo]:
        all_results = []
        for page in self.search_pages:
            page_source = self._load_page(page)
            page = BeautifulSoup(page_source)
            all_results += self.parse_search_page(page)
        return all_results

    def check_product_pages(self) -> List[Dict]:
        return super().check_product_pages()

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
        product_link = info_box.find('a', {'class': 'item-title'})
        url = product_link['href']
        title = product_link.text
        return title, url

    def _is_in_stock(self, search_result: Tag) -> bool:

        btn_box = search_result.find('div', {'class': 'item-button-area'})
        btn = btn_box.find('button')
        if not btn:
            return False
        log.debug('Button Text: %s', btn.text)
        if btn.text.lower().strip() == 'add to cart':
            return True
        else:
            return False

