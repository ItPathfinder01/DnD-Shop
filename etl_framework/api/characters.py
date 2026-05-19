import requests
from .base import BaseClient


class CharacterClient(BaseClient):
    def create_character(self, data: dict):
        return requests.post(self._url("/characters"), json=data, headers=self.headers, timeout=self.timeout)

    def get_my_character(self):
        return requests.get(self._url("/characters/me"), headers=self.headers, timeout=self.timeout)

    def update_character(self, data: dict):
        return requests.put(self._url("/characters/me"), json=data, headers=self.headers, timeout=self.timeout)

    def get_characters(self):
        return requests.get(self._url("/characters"), headers=self.headers, timeout=self.timeout)

    def transfer_money(self, data: dict):
        return requests.post(
            self._url("/characters/me/transfer/money"),
            json=data,
            headers=self.headers,
            timeout=self.timeout,
        )

    def transfer_item(self, data: dict):
        return requests.post(
            self._url("/characters/me/transfer/item"),
            json=data,
            headers=self.headers,
            timeout=self.timeout,
        )
