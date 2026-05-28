import pytest
import allure
from utils.helpers import extract_items
from config.settings import API_BASE_URL


@allure.feature("Shop")
@allure.story("Magic items")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_magic_items_returns_results(api_client):
    with allure.step(f"GET {API_BASE_URL}/shop/magic-items"):
        r = api_client.shop.get_shop_magic_items()
    assert r.status_code == 200
    with allure.step("Проверяем что магазин содержит хотя бы один магический предмет"):
        assert len(extract_items(r.json())) > 0


@allure.feature("Shop")
@allure.story("Equipment")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_equipment_returns_results(api_client):
    with allure.step(f"GET {API_BASE_URL}/shop/equipment"):
        r = api_client.shop.get_shop_equipment()
    assert r.status_code == 200
    with allure.step("Проверяем что магазин содержит хотя бы один предмет снаряжения"):
        assert len(extract_items(r.json())) > 0


@allure.feature("Shop")
@allure.story("Filters")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_magic_item_filters_endpoint(api_client):
    with allure.step(f"GET {API_BASE_URL}/shop/magic-items/filters"):
        r = api_client.shop.get_magic_item_filters()
    assert r.status_code == 200
    with allure.step("Проверяем что ответ является словарём"):
        assert isinstance(r.json(), dict)


@allure.feature("Shop")
@allure.story("Filters")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_equipment_filters_endpoint(api_client):
    with allure.step(f"GET {API_BASE_URL}/shop/equipment/filters"):
        r = api_client.shop.get_equipment_filters()
    assert r.status_code == 200
    with allure.step("Проверяем что ответ является словарём"):
        assert isinstance(r.json(), dict)


@allure.feature("Shop")
@allure.story("Magic items")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_magic_items_have_required_fields(api_client):
    with allure.step(f"GET {API_BASE_URL}/shop/magic-items — проверяем обязательные поля"):
        items = extract_items(api_client.shop.get_shop_magic_items().json())
        for item in items[:10]:
            assert "id" in item, f"Нет поля id: {item}"
            assert "title" in item or "name" in item, f"Нет названия: {item}"


@allure.feature("Shop")
@allure.story("Equipment")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_equipment_has_required_fields(api_client):
    with allure.step(f"GET {API_BASE_URL}/shop/equipment — проверяем обязательные поля"):
        items = extract_items(api_client.shop.get_shop_equipment().json())
        for item in items[:10]:
            assert "id" in item
            assert "title" in item or "name" in item


@allure.feature("Shop")
@allure.story("Filters")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_filter_magic_items_by_rarity(api_client):
    rarities = api_client.shop.get_magic_item_filters().json().get("rarities", [])
    if not rarities:
        pytest.skip("Нет доступных редкостей")
    with allure.step(f"GET {API_BASE_URL}/shop/magic-items?rarity={rarities[0]}"):
        r = api_client.shop.get_shop_magic_items(params={"rarity": rarities[0]})
    assert r.status_code == 200
    with allure.step(f"Проверяем что фильтр по rarity={rarities[0]} вернул результаты"):
        assert len(extract_items(r.json())) > 0


@allure.feature("Shop")
@allure.story("Filters")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_filter_equipment_by_category(api_client):
    categories = api_client.shop.get_equipment_filters().json().get("categories", [])
    if not categories:
        pytest.skip("Нет доступных категорий")
    with allure.step(f"GET {API_BASE_URL}/shop/equipment?category={categories[0]}"):
        r = api_client.shop.get_shop_equipment(params={"category": categories[0]})
    assert r.status_code == 200
    with allure.step(f"Проверяем что фильтр по category={categories[0]} вернул результаты"):
        assert len(extract_items(r.json())) > 0


@allure.feature("Shop")
@allure.story("Magic items")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_search_magic_items(api_client):
    with allure.step(f"GET {API_BASE_URL}/shop/magic-items?search=sword"):
        r = api_client.shop.get_shop_magic_items(params={"search": "sword"})
    assert r.status_code == 200


@allure.feature("Shop")
@allure.story("Magic items")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_pagination_limits_results(api_client):
    with allure.step(f"GET {API_BASE_URL}/shop/magic-items?per_page=5"):
        r = api_client.shop.get_shop_magic_items(params={"per_page": 5})
    assert r.status_code == 200
    with allure.step("Проверяем что сервер вернул не более 5 предметов"):
        assert len(extract_items(r.json())) <= 5


@allure.feature("Shop")
@allure.story("Bargain")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_bargain_returns_valid_response(api_client, character):
    with allure.step(f"POST {API_BASE_URL}/shop/bargain — бросаем кубики"):
        r = api_client.shop.bargain()
    assert r.status_code == 200
    data = r.json()
    with allure.step("Проверяем что ответ содержит данные о броске"):
        assert isinstance(data, dict), f"Ожидался dict, получили: {type(data)}"
        has_roll_data = any(k in data for k in ("player_roll", "roll", "multiplier", "result"))
        assert has_roll_data, f"Неожиданный формат ответа bargain: {data}"
