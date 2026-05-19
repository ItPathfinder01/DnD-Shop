import requests
from config.settings import API_BASE_URL, API_TIMEOUT


class BaseClient:
    def __init__(self, token: str = None):
        self.base_url = API_BASE_URL
        self.timeout = API_TIMEOUT
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"
