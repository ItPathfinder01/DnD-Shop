import requests
from .base import BaseClient


class InventoryClient(BaseClient):
    def get_inventory(self):
        return requests.get(self._url("/inventory"), headers=self.headers, timeout=self.timeout)

    def add_to_inventory(self, data: dict):
        return requests.post(self._url("/inventory"), json=data, headers=self.headers, timeout=self.timeout)

    def delete_from_inventory(self, item_id: int):
        return requests.delete(self._url(f"/inventory/{item_id}"), headers=self.headers, timeout=self.timeout)
