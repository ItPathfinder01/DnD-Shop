import requests  # third-party library for making HTTP requests (GET, POST, PUT, DELETE)
from config.settings import API_BASE_URL, API_TIMEOUT  # central config: server URL and timeout value


def _url(path: str) -> str:
    # Concatenate the base URL with the endpoint path.
    # Example: _url("/auth/login") → "http://localhost:8000/auth/login"
    # The leading underscore signals that this is a private helper, not part of the public API.
    return f"{API_BASE_URL}{path}"


def _auth(token: str) -> dict:
    # Build the Authorization header required by every protected endpoint.
    # The DnD Shop API uses Bearer token authentication (JWT).
    # Example output: {"Authorization": "Bearer eyJhbGci..."}
    return {"Authorization": f"Bearer {token}"}


def health_check():
    # Send a GET request to /health — a public endpoint that returns 200 if the server is running.
    # No auth header needed because this endpoint is open to everyone.
    return requests.get(_url("/health"), timeout=API_TIMEOUT)


# ─── Auth ─────────────────────────────────────────────────────────────────────

def register(email: str, password: str):
    # Send a POST request to create a new user account.
    # The body is serialized to JSON automatically by the `json=` parameter.
    # Returns the raw Response object so the caller can inspect status_code and .json().
    return requests.post(_url("/auth/register"), json={"email": email, "password": password}, timeout=API_TIMEOUT)


def login(email: str, password: str):
    # Send a POST request to authenticate an existing user.
    # On success the API returns {"access_token": "...", "token_type": "bearer"}.
    # The caller extracts ["access_token"] to get the JWT for subsequent requests.
    return requests.post(_url("/auth/login"), json={"email": email, "password": password}, timeout=API_TIMEOUT)


def get_me(token: str):
    # Send a GET request to /auth/me — returns the profile of the currently authenticated user.
    # Requires a valid Bearer token in the Authorization header.
    return requests.get(_url("/auth/me"), headers=_auth(token), timeout=API_TIMEOUT)


# ─── Characters ───────────────────────────────────────────────────────────────

def create_character(token: str, data: dict):
    # Send a POST request to create a new D&D character for the authenticated user.
    # `data` is the character payload (name, race, age, gold, etc.) from test_character.json.
    return requests.post(_url("/characters"), json=data, headers=_auth(token), timeout=API_TIMEOUT)


def get_my_character(token: str):
    # Send a GET request to retrieve the character that belongs to the authenticated user.
    return requests.get(_url("/characters/me"), headers=_auth(token), timeout=API_TIMEOUT)


def update_character(token: str, data: dict):
    # Send a PUT request to update fields on the current user's character.
    # Only the fields included in `data` are updated; others keep their current values.
    return requests.put(_url("/characters/me"), json=data, headers=_auth(token), timeout=API_TIMEOUT)


def get_characters(token: str):
    # Send a GET request to list all characters EXCEPT the current user's own character.
    # Used to find other players' characters (e.g., to send them money or items).
    return requests.get(_url("/characters"), headers=_auth(token), timeout=API_TIMEOUT)


def transfer_money(token: str, data: dict):
    # Send a POST request to transfer currency from the current character to another.
    # `data` must contain "to_character_id" and all five currency fields (platinum, gold, etc.).
    return requests.post(_url("/characters/me/transfer/money"), json=data, headers=_auth(token), timeout=API_TIMEOUT)


def transfer_item(token: str, data: dict):
    # Send a POST request to transfer an inventory item to another character.
    # `data` must contain "to_character_id", "inventory_item_id", and "quantity".
    return requests.post(_url("/characters/me/transfer/item"), json=data, headers=_auth(token), timeout=API_TIMEOUT)


# ─── Shop ─────────────────────────────────────────────────────────────────────

def get_magic_item_filters(token: str):
    # Send a GET request to retrieve the available filter options for magic items.
    # The response contains lists of types and rarities that can be passed as query params.
    return requests.get(_url("/shop/magic-items/filters"), headers=_auth(token), timeout=API_TIMEOUT)


def get_equipment_filters(token: str):
    # Send a GET request to retrieve the available filter options for equipment.
    # The response contains categories, weapon properties, and masteries.
    return requests.get(_url("/shop/equipment/filters"), headers=_auth(token), timeout=API_TIMEOUT)


def get_shop_magic_items(token: str, params: dict = None):
    # Send a GET request to list magic items from the shop.
    # Optional `params` dict is converted to URL query string by requests automatically.
    # Example: params={"rarity": "rare", "per_page": 5} → ?rarity=rare&per_page=5
    return requests.get(_url("/shop/magic-items"), headers=_auth(token), params=params, timeout=API_TIMEOUT)


def get_shop_equipment(token: str, params: dict = None):
    # Send a GET request to list equipment items from the shop.
    # Supports the same filtering and pagination params as magic items.
    return requests.get(_url("/shop/equipment"), headers=_auth(token), params=params, timeout=API_TIMEOUT)


def bargain(token: str):
    # Send a POST request to trigger the D&D bargaining mechanic.
    # The server rolls two d20 dice (player vs merchant) and returns a price multiplier.
    return requests.post(_url("/shop/bargain"), headers=_auth(token), timeout=API_TIMEOUT)


def purchase(token: str, items: list):
    # Send a POST request to buy a list of items from the shop.
    # `items` is a list of objects describing what to buy (item_type, shop_item_id, quantity).
    # The server deducts the total cost from the character's currency and adds items to inventory.
    return requests.post(_url("/shop/purchase"), json=items, headers=_auth(token), timeout=API_TIMEOUT)


# ─── Inventory ────────────────────────────────────────────────────────────────

def get_inventory(token: str):
    # Send a GET request to retrieve all items currently in the character's inventory.
    # Returns a list of inventory item objects with item details and quantities.
    return requests.get(_url("/inventory"), headers=_auth(token), timeout=API_TIMEOUT)


def add_to_inventory(token: str, data: dict):
    # Send a POST request to add an item to the inventory.
    # If the same item already exists, the API increments its quantity instead of creating a duplicate.
    # `data` must contain "item_type", "shop_item_id", and "quantity".
    return requests.post(_url("/inventory"), json=data, headers=_auth(token), timeout=API_TIMEOUT)


def delete_from_inventory(token: str, item_id: int):
    # Send a DELETE request to remove an inventory entry by its inventory item ID (not the shop item ID).
    # The item_id is embedded directly in the URL path: /inventory/{item_id}
    return requests.delete(_url(f"/inventory/{item_id}"), headers=_auth(token), timeout=API_TIMEOUT)
