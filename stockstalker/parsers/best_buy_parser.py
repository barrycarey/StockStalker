from typing import List, Text, NoReturn, Dict

from bs4 import Tag, BeautifulSoup

from stockstalker.services.notification_svc import NotificationSvc
from stockstalker.parsers.parser_base import ParserBase


class BestBuyParser(ParserBase):
    def __init__(
            self,
            notification_svc: NotificationSvc,
            search_pages: List[Text] = None,
            product_pages: List[Text] = None,
            web_driver: Text = None):

        super().__init__(notification_svc, search_pages, product_pages, web_driver)




    def _get_cart_text_search_page(self, item: Tag) -> Text:
        button_box = item.find('div', {'class': 'sku-list-item-button'})
        add_to_cart_btn = button_box.find('button')
        return add_to_cart_btn.text

    def parse_search_pages(self, page) -> List[Dict]:
        results = []
        search_results = page.find('ol', {'class': 'sku-item-list'})
        items = search_results.findAll('li', {'class': 'sku-item'})
        for i in items:
            results.append(self._get_product_data_from_search_result(i))
        return results

    def check_stock(self) -> NoReturn:
        for page in self.search_pages:
            page_source = self._load_page(page)
            page = BeautifulSoup(page_source)
            product_data = self.parse_search_pages(page)
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
    search_pages = [
        'https://www.bestbuy.com/site/searchpage.jsp?st=rtx+3080&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys']
    product_pages = [
        'https://www.bestbuy.com/site/evga-geforce-rtx-3080-xc3-ultra-gaming-10gb-gddr6-pci-express-4-0-graphics-card/6432400.p?skuId=6432400'
    ]

    parser = BestBuyParser(None, search_pages=search_pages, web_driver=r"C:\chromedriver\chromedriver.exe")
    parser.check_stock()