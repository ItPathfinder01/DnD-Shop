import requests
from .base import BaseClient


class AdminClient(BaseClient):
    def delete_user(self, user_id: int):
        return requests.delete(self._url(f"/admin/users/{user_id}"), headers=self.headers, timeout=self.timeout)
