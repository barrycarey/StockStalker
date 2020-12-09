from dataclasses import dataclass


@dataclass
class ProductInfo:
    title: str
    url: str
    in_stock: bool = False
    price: str = None
    sku: str = None

    def __repr__(self):
        return f'{self.title} | {self.url}'

    def to_dict(self):
        return {
            'title': self.title,
            'url': self.url,
            'in_stock': self.in_stock,
            'price': self.price,
            'sku': self.sku
        }