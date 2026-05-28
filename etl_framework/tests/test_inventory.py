import pytest
import allure
from utils.helpers import extract_items
from config.settings import API_BASE_URL


def _first_shop_item_id(api_client) -> int:
    items = extract_items(api_client.shop.get_shop_magic_items().json())
    assert items, "Магазин пуст — тест невозможен"
    return items[0]["id"]


@allure.feature("Inventory")
@allure.story("Get inventory")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_get_inventory_returns_list(api_client, character):
    with allure.step(f"GET {API_BASE_URL}/inventory"):
        r = api_client.inventory.get_inventory()
    assert r.status_code == 200
    with allure.step("Проверяем что инвентарь возвращает список"):
        assert isinstance(r.json(), list)


@allure.feature("Inventory")
@allure.story("Add item")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_add_item_to_inventory(api_client, character):
    item_id = _first_shop_item_id(api_client)
    with allure.step(f"POST {API_BASE_URL}/inventory — добавляем magic_item id={item_id}"):
        r = api_client.inventory.add_to_inventory({"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1})
    assert r.status_code in (200, 201)
    inv_item = r.json()
    with allure.step("Проверяем что созданная запись содержит id"):
        assert "id" in inv_item
    with allure.step(f"DELETE {API_BASE_URL}/inventory/{inv_item['id']} — очистка"):
        api_client.inventory.delete_from_inventory(inv_item["id"])


@allure.feature("Inventory")
@allure.story("Add item")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_inventory_item_has_required_fields(api_client, character):
    item_id = _first_shop_item_id(api_client)
    with allure.step(f"POST {API_BASE_URL}/inventory — добавляем magic_item id={item_id}"):
        r = api_client.inventory.add_to_inventory({"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1})
    inv_item = r.json()
    with allure.step("Проверяем наличие полей: id, item_type, quantity"):
        for field in ("id", "item_type", "quantity"):
            assert field in inv_item, f"Отсутствует поле: {field}"
    with allure.step(f"DELETE {API_BASE_URL}/inventory/{inv_item['id']} — очистка"):
        api_client.inventory.delete_from_inventory(inv_item["id"])


@allure.feature("Inventory")
@allure.story("Delete item")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_delete_item_from_inventory(api_client, character):
    item_id = _first_shop_item_id(api_client)
    with allure.step(f"POST {API_BASE_URL}/inventory — добавляем предмет для удаления"):
        inv_item_id = api_client.inventory.add_to_inventory(
            {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1}
        ).json()["id"]
    with allure.step(f"DELETE {API_BASE_URL}/inventory/{inv_item_id}"):
        r = api_client.inventory.delete_from_inventory(inv_item_id)
    assert r.status_code == 200
    with allure.step("Проверяем что предмет исчез из инвентаря"):
        remaining_ids = [i["id"] for i in api_client.inventory.get_inventory().json()]
        assert inv_item_id not in remaining_ids


@allure.feature("Inventory")
@allure.story("Add item")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_add_same_item_twice_increments_quantity(api_client, character):
    item_id = _first_shop_item_id(api_client)
    payload = {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1}
    with allure.step(f"POST {API_BASE_URL}/inventory — добавляем предмет первый раз"):
        r1 = api_client.inventory.add_to_inventory(payload)
    assert r1.status_code in (200, 201)
    inv_item = r1.json()
    with allure.step(f"POST {API_BASE_URL}/inventory — добавляем тот же предмет второй раз"):
        api_client.inventory.add_to_inventory(payload)
    with allure.step("Проверяем что quantity увеличился до >= 2"):
        inventory = api_client.inventory.get_inventory().json()
        matching = [i for i in inventory if i.get("shop_item_id") == item_id and i.get("item_type") == "magic_item"]
        assert matching, "Предмет не найден в инвентаре"
        assert matching[0]["quantity"] >= 2, "Количество не увеличилось"
    with allure.step(f"DELETE {API_BASE_URL}/inventory/{inv_item['id']} — очистка"):
        api_client.inventory.delete_from_inventory(inv_item["id"])
