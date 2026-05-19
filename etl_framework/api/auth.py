import requests
from .base import BaseClient


class AuthClient(BaseClient):
    def health_check(self):
        return requests.get(self._url("/health"), timeout=self.timeout)

    def register(self, email: str, password: str):
        return requests.post(
            self._url("/auth/register"),
            json={"email": email, "password": password},
            timeout=self.timeout,
        )

    def login(self, email: str, password: str):
        return requests.post(
            self._url("/auth/login"),
            json={"email": email, "password": password},
            timeout=self.timeout,
        )

    def get_me(self):
        return requests.get(self._url("/auth/me"), headers=self.headers, timeout=self.timeout)
