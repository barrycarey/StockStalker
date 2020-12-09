from typing import List, Text, NoReturn, Dict

from bs4 import Tag, BeautifulSoup
from selenium import webdriver

from notification_svc import NotificationSvc


class BestBuyParser:
    def __init__(
            self,
            notification_svc: NotificationSvc,
            search_page: List[Text] = None,
            product_pages: List[Text] = None,
            web_driver: Text = None):
        self.search_page = search_page
        self.product_pages = product_pages
        self.notification_svc = notification_svc
        self.web_driver = webdriver.Chrome(executable_path=web_driver)

    def _load_page(self, url: Text):
        self.web_driver.get(url)
        return self.web_driver.page_source

    def _get_cart_text_search_page(self, item: Tag) -> Text:
        button_box = item.find('div', {'class': 'sku-list-item-button'})
        add_to_cart_btn = button_box.find('button')
        return add_to_cart_btn.text

    def add_search_page(self, url: Text) -> NoReturn:
        self.search_page.append(url)

    def add_product_page(self, url: Text) -> NoReturn:
        self.product_pages.append(url)

    def parse_search_page(self, page) -> List[Dict]:
        results = []
        search_results = page.find('ol', {'class': 'sku-item-list'})
        items = search_results.findAll('li', {'class': 'sku-item'})
        for i in items:
            results.append(self._get_product_data_from_search_result(i))
        return results

    def process_search_pages(self) -> NoReturn:
        for page in self.search_page:
            page_source = self._load_page(page)
            page = BeautifulSoup(page_source)
            product_data = self.parse_search_page(page)
            for d in product_data:
                if d['in_stock']:
                    self.notification_svc.send_notificaiton(d)

    def _get_product_data_from_search_result(self, search_result_tag: Tag) -> Dict:
        result = {
            'title': None,
            'sku': None,
            'url': None,
            'in_stock': False,
            'price': None
        }
        add_to_cart_btn_text = self._get_cart_text_search_page(search_result_tag)
        result['title'], result['url'] = self._get_title_and_url_from_search_result(search_result_tag)
        result['sku'] = self._get_sku_from_search_result(search_result_tag)
        result['price'] = self._get_price_from_search_result(search_result_tag)
        if add_to_cart_btn_text.lower() == 'sold out':
            result['in_stock'] = False
        else:
            result['in_stock'] = True

        return result

    def _get_price_from_search_result(self, item: Tag) -> Text:
        price_box = item.find('div', {'class': 'priceView-hero-price priceView-customer-price'})
        price = price_box.findAll('span')
        return price[0].text

    def _get_sku_from_search_result(self, item: Tag) -> Text:
        sku_boxes = item.findAll('div', {'class': 'sku-attribute-title'})
        for box in sku_boxes:
            if box.find('span', {'class': 'attribute-title'}).text == 'SKU:':
                return box.find('span', {'class': 'sku-value'}).text

    def _get_title_and_url_from_search_result(self, item: Tag):
        url_a = item.find('h4', {'class': 'sku-header'}).find('a')
        url = 'https://bestbuy.com' + url_a['href']
        title = url_a.text
        return title, url

    def parse_product_page(self):
        pass

if __name__ == '__main__':
    parser = BestBuyParser(None, search_page=['https://www.bestbuy.com/site/searchpage.jsp?st=rtx+3080&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys'], web_driver=r"C:\chromedriver\chromedriver.exe")
    parser.process_search_pages()