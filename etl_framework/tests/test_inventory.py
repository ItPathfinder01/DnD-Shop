import pytest
from utils.helpers import extract_items


def _first_shop_item_id(api_client) -> int:
    items = extract_items(api_client.shop.get_shop_magic_items().json())
    assert items, "Магазин пуст — тест невозможен"
    return items[0]["id"]


@pytest.mark.smoke
def test_get_inventory_returns_list(api_client, character):
    r = api_client.inventory.get_inventory()
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.regression
def test_add_item_to_inventory(api_client, character):
    item_id = _first_shop_item_id(api_client)
    r = api_client.inventory.add_to_inventory({"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1})
    assert r.status_code in (200, 201)
    inv_item = r.json()
    assert "id" in inv_item

    api_client.inventory.delete_from_inventory(inv_item["id"])


@pytest.mark.regression
def test_inventory_item_has_required_fields(api_client, character):
    item_id = _first_shop_item_id(api_client)
    r = api_client.inventory.add_to_inventory({"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1})
    inv_item = r.json()

    for field in ("id", "item_type", "quantity"):
        assert field in inv_item, f"Отсутствует поле: {field}"

    api_client.inventory.delete_from_inventory(inv_item["id"])


@pytest.mark.regression
def test_delete_item_from_inventory(api_client, character):
    item_id = _first_shop_item_id(api_client)
    inv_item_id = api_client.inventory.add_to_inventory(
        {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1}
    ).json()["id"]

    r = api_client.inventory.delete_from_inventory(inv_item_id)
    assert r.status_code == 200

    remaining_ids = [i["id"] for i in api_client.inventory.get_inventory().json()]
    assert inv_item_id not in remaining_ids


@pytest.mark.regression
def test_add_same_item_twice_increments_quantity(api_client, character):
    item_id = _first_shop_item_id(api_client)
    payload = {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1}

    r1 = api_client.inventory.add_to_inventory(payload)
    assert r1.status_code in (200, 201)
    inv_item = r1.json()

    api_client.inventory.add_to_inventory(payload)

    inventory = api_client.inventory.get_inventory().json()
    matching = [i for i in inventory if i.get("shop_item_id") == item_id and i.get("item_type") == "magic_item"]
    assert matching, "Предмет не найден в инвентаре"
    assert matching[0]["quantity"] >= 2, "Количество не увеличилось"

    api_client.inventory.delete_from_inventory(inv_item["id"])
