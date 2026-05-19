from .auth import AuthClient
from .characters import CharacterClient
from .shop import ShopClient
from .inventory import InventoryClient
from .admin import AdminClient


class ApiClient:
    def __init__(self, token: str = None):
        self.auth = AuthClient(token=token)
        self.characters = CharacterClient(token=token)
        self.shop = ShopClient(token=token)
        self.inventory = InventoryClient(token=token)
        self.admin = AdminClient(token=token)
