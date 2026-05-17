import requests
from config.settings import API_BASE_URL, API_TIMEOUT


def _url(path: str) -> str:
    return f"{API_BASE_URL}{path}"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def health_check():
    return requests.get(_url("/health"), timeout=API_TIMEOUT)


# ─── Auth ─────────────────────────────────────────────────────────────────────

def register(email: str, password: str):
    return requests.post(_url("/auth/register"), json={"email": email, "password": password}, timeout=API_TIMEOUT)


def login(email: str, password: str):
    return requests.post(_url("/auth/login"), json={"email": email, "password": password}, timeout=API_TIMEOUT)


def get_me(token: str):
    return requests.get(_url("/auth/me"), headers=_auth(token), timeout=API_TIMEOUT)


# ─── Characters ───────────────────────────────────────────────────────────────

def create_character(token: str, data: dict):
    return requests.post(_url("/characters"), json=data, headers=_auth(token), timeout=API_TIMEOUT)


def get_my_character(token: str):
    return requests.get(_url("/characters/me"), headers=_auth(token), timeout=API_TIMEOUT)


def update_character(token: str, data: dict):
    return requests.put(_url("/characters/me"), json=data, headers=_auth(token), timeout=API_TIMEOUT)


def get_characters(token: str):
    return requests.get(_url("/characters"), headers=_auth(token), timeout=API_TIMEOUT)


def transfer_money(token: str, data: dict):
    return requests.post(_url("/characters/me/transfer/money"), json=data, headers=_auth(token), timeout=API_TIMEOUT)


def transfer_item(token: str, data: dict):
    return requests.post(_url("/characters/me/transfer/item"), json=data, headers=_auth(token), timeout=API_TIMEOUT)


# ─── Shop ─────────────────────────────────────────────────────────────────────

def get_magic_item_filters(token: str):
    return requests.get(_url("/shop/magic-items/filters"), headers=_auth(token), timeout=API_TIMEOUT)


def get_equipment_filters(token: str):
    return requests.get(_url("/shop/equipment/filters"), headers=_auth(token), timeout=API_TIMEOUT)


def get_shop_magic_items(token: str, params: dict = None):
    return requests.get(_url("/shop/magic-items"), headers=_auth(token), params=params, timeout=API_TIMEOUT)


def get_shop_equipment(token: str, params: dict = None):
    return requests.get(_url("/shop/equipment"), headers=_auth(token), params=params, timeout=API_TIMEOUT)


def bargain(token: str):
    return requests.post(_url("/shop/bargain"), headers=_auth(token), timeout=API_TIMEOUT)


def purchase(token: str, items: list):
    return requests.post(_url("/shop/purchase"), json=items, headers=_auth(token), timeout=API_TIMEOUT)


# ─── Inventory ────────────────────────────────────────────────────────────────

def get_inventory(token: str):
    return requests.get(_url("/inventory"), headers=_auth(token), timeout=API_TIMEOUT)


def add_to_inventory(token: str, data: dict):
    return requests.post(_url("/inventory"), json=data, headers=_auth(token), timeout=API_TIMEOUT)


def delete_from_inventory(token: str, item_id: int):
    return requests.delete(_url(f"/inventory/{item_id}"), headers=_auth(token), timeout=API_TIMEOUT)
