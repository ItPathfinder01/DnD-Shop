import pytest
from utils.api_client import (
    get_inventory, add_to_inventory, delete_from_inventory,
    get_shop_magic_items,
)
from utils.helpers import extract_items


def _first_shop_item_id(auth_token: str) -> int:
    items = extract_items(get_shop_magic_items(auth_token).json())
    assert items, "Магазин пуст — тест невозможен"
    return items[0]["id"]


@pytest.mark.smoke
def test_get_inventory_returns_list(auth_token, character):
    r = get_inventory(auth_token)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.regression
def test_add_item_to_inventory(auth_token, character):
    item_id = _first_shop_item_id(auth_token)
    r = add_to_inventory(auth_token, {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1})
    assert r.status_code in (200, 201)
    inv_item = r.json()
    assert "id" in inv_item

    delete_from_inventory(auth_token, inv_item["id"])


@pytest.mark.regression
def test_inventory_item_has_required_fields(auth_token, character):
    item_id = _first_shop_item_id(auth_token)
    r = add_to_inventory(auth_token, {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1})
    inv_item = r.json()

    for field in ("id", "item_type", "quantity"):
        assert field in inv_item, f"Отсутствует поле: {field}"

    delete_from_inventory(auth_token, inv_item["id"])


@pytest.mark.regression
def test_delete_item_from_inventory(auth_token, character):
    item_id = _first_shop_item_id(auth_token)
    inv_item_id = add_to_inventory(auth_token, {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1}).json()["id"]

    r = delete_from_inventory(auth_token, inv_item_id)
    assert r.status_code == 200

    remaining_ids = [i["id"] for i in get_inventory(auth_token).json()]
    assert inv_item_id not in remaining_ids


@pytest.mark.regression
def test_add_same_item_twice_increments_quantity(auth_token, character):
    item_id = _first_shop_item_id(auth_token)
    payload = {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1}

    r1 = add_to_inventory(auth_token, payload)
    assert r1.status_code in (200, 201)
    inv_item = r1.json()

    add_to_inventory(auth_token, payload)

    inventory = get_inventory(auth_token).json()
    matching = [i for i in inventory if i.get("shop_item_id") == item_id and i.get("item_type") == "magic_item"]
    assert matching, "Предмет не найден в инвентаре"
    assert matching[0]["quantity"] >= 2, "Количество не увеличилось"

    delete_from_inventory(auth_token, inv_item["id"])
