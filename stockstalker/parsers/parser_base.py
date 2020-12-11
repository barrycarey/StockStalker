from typing import List, Text, NoReturn, Dict

from bs4 import BeautifulSoup
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
            ignore_urls: List[Text] = None,
            ignore_title_keywords=None
    ):
        """

        :param notification_svc: Service to send out notifications
        :type notification_svc: NotificationSvc
        :param search_pages: List of search result pages to parse
        :type search_pages: List[Text]
        :param product_pages: List of product pages to parse
        :type product_pages: List[Text]
        :param web_driver: Path to the web driver path used be selinum
        :type web_driver: Text
        :param ignore_urls: URLs to ignore when checking search results
        :type ignore_urls: List[Text]
        :param ignore_title_keywords: Ignore search results with any of these keywords in title
        :type ignore_title_keywords: List[Text]
        """
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
        """
        Add a new search page to check stock status
        :param url: URL of the search page
        :type url: Text
        """
        self.search_pages.append(url)

    def add_product_page(self, url: Text) -> NoReturn:
        """
        Add a new product page to monitor
        :param url: URL to page
        :type url: Text
        """
        self.product_pages.append(url)

    def is_ignored(self, data: ProductInfo) -> bool:
        """
        Check if a given product should be ignored based on defined ignore URLs and keywords
        :param data: The product data to check
        :type data: ProductInfo
        :return: bool
        :rtype: bool
        """
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

    def parse_search_page(self, page: BeautifulSoup) -> List[ProductInfo]:
        """
        Take the Beautiful Soup object of a search page and parse out the product data
        :rtype: List[ProductInfo]
        :param page: BeautifulSoup Page
        :type page: BeautifulSoup
        """
        raise NotImplementedError

    def parse_product_page(self, page: BeautifulSoup) -> List[ProductInfo]:
        """
        Take a given product page and parse out the details
        :param page: BeautifulSoup page
        :type page: BeautifulSoup
        """
        raise NotImplementedError

    def check_stock(self) -> NoReturn:
        """
        For logic to run checks of all product and search pages
        """
        raise NotImplementedError

    def check_search_pages(self) -> List[ProductInfo]:
        """
        Check all registered Search Pages
        """
        raise NotImplementedError

    def check_product_pages(self) -> List[ProductInfo]:
        """
        Check all registered product pages
        """
        raise NotImplementedError

    def _load_page(self, url: Text) -> Text:
        """
        Loads the provided URL in selenium
        :rtype: Text
        """
        self.web_driver.get(url)
        return self.web_driver.page_source

    def format_notification(self, data: ProductInfo):
        msg = '**Instock Alert**\n{title}\n{url}'.format(**data)
        return msg