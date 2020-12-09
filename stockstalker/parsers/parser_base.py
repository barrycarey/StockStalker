from typing import List, Text, NoReturn, Dict

from selenium import webdriver

from stockstalker.common.logging import log
from stockstalker.product_info import ProductInfo
from stockstalker.services.notification_svc import NotificationSvc


class ParserBase:
    def __init__(
            self,
            notification_svc: NotificationSvc,
            search_pages: List[Text] = None,
            product_pages: List[Text] = None,
            web_driver: Text = None,
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
        self.web_driver = web_driver
        self.notification_svc = notification_svc
        self.search_pages = search_pages
        self.web_driver = webdriver.Chrome(executable_path=web_driver)
        self.notification_sent_urls = []

    def add_search_pages(self, url: Text) -> NoReturn:
        self.search_pages.append(url)

    def add_product_page(self, url: Text) -> NoReturn:
        self.product_pages.append(url)

    def is_ignored(self, data: ProductInfo) -> bool:
        print(data)
        for kw in self.ignore_title_keywords:
            if kw.lower() in data.title.lower():
                log.debug('Title contains ignore keywords %s', kw)
                return True
        if data.url in self.ignore_urls:
            log.debug('Product URL in ignore list')
            return True
        if data.url in self.notification_sent_urls:
            log.debug('Already sent notification for this product')
            return True
        return False

    def parse_search_page(self, page) -> List[Dict]:
        raise NotImplementedError

    def parse_product_page(self, page) -> Dict:
        raise NotImplementedError

    def check_stock(self) -> NoReturn:
        raise NotImplementedError

    def check_search_pages(self) -> List[Dict]:
        raise NotImplementedError

    def check_product_pages(self) -> List[Dict]:
        raise NotImplementedError

    def _load_page(self, url: Text) -> Text:
        self.web_driver.get(url)
        return self.web_driver.page_source

    def format_notification(self, data: ProductInfo):
        msg = '**Instock Alert**\n{title}\n{url}'.format(**data)
        return msg