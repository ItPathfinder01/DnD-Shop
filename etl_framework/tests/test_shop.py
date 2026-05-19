import pytest
from utils.helpers import extract_items


@pytest.mark.smoke
def test_magic_items_returns_results(api_client):
    r = api_client.shop.get_shop_magic_items()
    assert r.status_code == 200
    assert len(extract_items(r.json())) > 0


@pytest.mark.smoke
def test_equipment_returns_results(api_client):
    r = api_client.shop.get_shop_equipment()
    assert r.status_code == 200
    assert len(extract_items(r.json())) > 0


@pytest.mark.smoke
def test_magic_item_filters_endpoint(api_client):
    r = api_client.shop.get_magic_item_filters()
    assert r.status_code == 200
    assert isinstance(r.json(), dict)


@pytest.mark.smoke
def test_equipment_filters_endpoint(api_client):
    r = api_client.shop.get_equipment_filters()
    assert r.status_code == 200
    assert isinstance(r.json(), dict)


@pytest.mark.regression
def test_magic_items_have_required_fields(api_client):
    items = extract_items(api_client.shop.get_shop_magic_items().json())
    for item in items[:10]:
        assert "id" in item, f"Нет поля id: {item}"
        assert "title" in item or "name" in item, f"Нет названия: {item}"


@pytest.mark.regression
def test_equipment_has_required_fields(api_client):
    items = extract_items(api_client.shop.get_shop_equipment().json())
    for item in items[:10]:
        assert "id" in item
        assert "title" in item or "name" in item


@pytest.mark.regression
def test_filter_magic_items_by_rarity(api_client):
    rarities = api_client.shop.get_magic_item_filters().json().get("rarities", [])
    if not rarities:
        pytest.skip("Нет доступных редкостей")
    r = api_client.shop.get_shop_magic_items(params={"rarity": rarities[0]})
    assert r.status_code == 200
    assert len(extract_items(r.json())) > 0


@pytest.mark.regression
def test_filter_equipment_by_category(api_client):
    categories = api_client.shop.get_equipment_filters().json().get("categories", [])
    if not categories:
        pytest.skip("Нет доступных категорий")
    r = api_client.shop.get_shop_equipment(params={"category": categories[0]})
    assert r.status_code == 200
    assert len(extract_items(r.json())) > 0


@pytest.mark.regression
def test_search_magic_items(api_client):
    r = api_client.shop.get_shop_magic_items(params={"search": "sword"})
    assert r.status_code == 200


@pytest.mark.regression
def test_pagination_limits_results(api_client):
    r = api_client.shop.get_shop_magic_items(params={"per_page": 5})
    assert r.status_code == 200
    assert len(extract_items(r.json())) <= 5


@pytest.mark.regression
def test_bargain_returns_valid_response(api_client, character):
    r = api_client.shop.bargain()
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict), f"Ожидался dict, получили: {type(data)}"
    has_roll_data = any(k in data for k in ("player_roll", "roll", "multiplier", "result"))
    assert has_roll_data, f"Неожиданный формат ответа bargain: {data}"
