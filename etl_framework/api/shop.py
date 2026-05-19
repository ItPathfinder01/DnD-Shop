import requests
from .base import BaseClient


class ShopClient(BaseClient):
    def get_magic_item_filters(self):
        return requests.get(self._url("/shop/magic-items/filters"), headers=self.headers, timeout=self.timeout)

    def get_equipment_filters(self):
        return requests.get(self._url("/shop/equipment/filters"), headers=self.headers, timeout=self.timeout)

    def get_shop_magic_items(self, params: dict = None):
        return requests.get(
            self._url("/shop/magic-items"),
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )

    def get_shop_equipment(self, params: dict = None):
        return requests.get(
            self._url("/shop/equipment"),
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )

    def bargain(self):
        return requests.post(self._url("/shop/bargain"), headers=self.headers, timeout=self.timeout)

    def purchase(self, items: list):
        return requests.post(self._url("/shop/purchase"), json=items, headers=self.headers, timeout=self.timeout)
