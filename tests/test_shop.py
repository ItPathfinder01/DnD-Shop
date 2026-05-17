import pytest
from utils.api_client import (
    get_shop_magic_items, get_shop_equipment,
    get_magic_item_filters, get_equipment_filters,
    bargain,
)
from utils.helpers import extract_items


@pytest.mark.smoke
def test_magic_items_returns_results(auth_token):
    r = get_shop_magic_items(auth_token)
    assert r.status_code == 200
    assert len(extract_items(r.json())) > 0


@pytest.mark.smoke
def test_equipment_returns_results(auth_token):
    r = get_shop_equipment(auth_token)
    assert r.status_code == 200
    assert len(extract_items(r.json())) > 0


@pytest.mark.smoke
def test_magic_item_filters_endpoint(auth_token):
    r = get_magic_item_filters(auth_token)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)


@pytest.mark.smoke
def test_equipment_filters_endpoint(auth_token):
    r = get_equipment_filters(auth_token)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)


@pytest.mark.regression
def test_magic_items_have_required_fields(auth_token):
    items = extract_items(get_shop_magic_items(auth_token).json())
    for item in items[:10]:
        assert "id" in item, f"Нет поля id: {item}"
        assert "title" in item or "name" in item, f"Нет названия: {item}"


@pytest.mark.regression
def test_equipment_has_required_fields(auth_token):
    items = extract_items(get_shop_equipment(auth_token).json())
    for item in items[:10]:
        assert "id" in item
        assert "title" in item or "name" in item


@pytest.mark.regression
def test_filter_magic_items_by_rarity(auth_token):
    rarities = get_magic_item_filters(auth_token).json().get("rarities", [])
    if not rarities:
        pytest.skip("Нет доступных редкостей")
    r = get_shop_magic_items(auth_token, params={"rarity": rarities[0]})
    assert r.status_code == 200
    assert len(extract_items(r.json())) > 0


@pytest.mark.regression
def test_filter_equipment_by_category(auth_token):
    categories = get_equipment_filters(auth_token).json().get("categories", [])
    if not categories:
        pytest.skip("Нет доступных категорий")
    r = get_shop_equipment(auth_token, params={"category": categories[0]})
    assert r.status_code == 200
    assert len(extract_items(r.json())) > 0


@pytest.mark.regression
def test_search_magic_items(auth_token):
    r = get_shop_magic_items(auth_token, params={"search": "sword"})
    assert r.status_code == 200


@pytest.mark.regression
def test_pagination_limits_results(auth_token):
    r = get_shop_magic_items(auth_token, params={"per_page": 5})
    assert r.status_code == 200
    items = extract_items(r.json())
    assert len(items) <= 5


@pytest.mark.regression
def test_bargain_returns_valid_response(auth_token, character):
    r = bargain(auth_token)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict), f"Ожидался dict, получили: {type(data)}"
    has_roll_data = any(k in data for k in ("player_roll", "roll", "multiplier", "result"))
    assert has_roll_data, f"Неожиданный формат ответа bargain: {data}"
