import pytest  # test framework — provides markers and test discovery
from utils.api_client import (
    get_shop_magic_items,    # GET /shop/magic-items  — paginated list of D&D magic items
    get_shop_equipment,      # GET /shop/equipment    — paginated list of D&D equipment
    get_magic_item_filters,  # GET /shop/magic-items/filters — available types and rarities
    get_equipment_filters,   # GET /shop/equipment/filters   — available categories and properties
    bargain,                 # POST /shop/bargain — rolls two d20 dice and returns a price multiplier
)
from utils.helpers import extract_items  # helper that handles both list and paginated {"items": [...]} responses


@pytest.mark.smoke
def test_magic_items_returns_results(auth_token):
    r = get_shop_magic_items(auth_token)  # send GET /shop/magic-items with no filters
    assert r.status_code == 200  # the endpoint must respond successfully
    assert len(extract_items(r.json())) > 0  # the shop must contain at least one magic item


@pytest.mark.smoke
def test_equipment_returns_results(auth_token):
    r = get_shop_equipment(auth_token)  # send GET /shop/equipment with no filters
    assert r.status_code == 200  # the endpoint must respond successfully
    assert len(extract_items(r.json())) > 0  # the shop must contain at least one equipment item


@pytest.mark.smoke
def test_magic_item_filters_endpoint(auth_token):
    r = get_magic_item_filters(auth_token)  # send GET /shop/magic-items/filters
    assert r.status_code == 200  # the endpoint must respond successfully
    assert isinstance(r.json(), dict)  # the response must be a JSON object (not a list)


@pytest.mark.smoke
def test_equipment_filters_endpoint(auth_token):
    r = get_equipment_filters(auth_token)  # send GET /shop/equipment/filters
    assert r.status_code == 200  # the endpoint must respond successfully
    assert isinstance(r.json(), dict)  # the response must be a JSON object (not a list)


@pytest.mark.regression
def test_magic_items_have_required_fields(auth_token):
    items = extract_items(get_shop_magic_items(auth_token).json())  # fetch all magic items and normalize the response format
    for item in items[:10]:  # check only the first 10 items to keep the test fast
        assert "id" in item, f"Нет поля id: {item}"  # every item must have a database ID
        assert "title" in item or "name" in item, f"Нет названия: {item}"  # item must have at least one name field


@pytest.mark.regression
def test_equipment_has_required_fields(auth_token):
    items = extract_items(get_shop_equipment(auth_token).json())  # fetch all equipment and normalize the response format
    for item in items[:10]:  # check only the first 10 items
        assert "id" in item  # every equipment item must have a database ID
        assert "title" in item or "name" in item  # equipment must have at least one name field


@pytest.mark.regression
def test_filter_magic_items_by_rarity(auth_token):
    rarities = get_magic_item_filters(auth_token).json().get("rarities", [])  # get the list of valid rarity values from the API
    if not rarities:  # if the API returned no rarities, we cannot run this test
        pytest.skip("Нет доступных редкостей")  # skip gracefully instead of failing (skip ≠ failure)
    r = get_shop_magic_items(auth_token, params={"rarity": rarities[0]})  # filter by the first available rarity
    assert r.status_code == 200  # the filtered request must succeed
    assert len(extract_items(r.json())) > 0  # the filter must return at least one matching item


@pytest.mark.regression
def test_filter_equipment_by_category(auth_token):
    categories = get_equipment_filters(auth_token).json().get("categories", [])  # get the list of valid category values
    if not categories:  # if no categories are available, skip the test
        pytest.skip("Нет доступных категорий")
    r = get_shop_equipment(auth_token, params={"category": categories[0]})  # filter equipment by the first available category
    assert r.status_code == 200  # the filtered request must succeed
    assert len(extract_items(r.json())) > 0  # the filter must return at least one matching item


@pytest.mark.regression
def test_search_magic_items(auth_token):
    r = get_shop_magic_items(auth_token, params={"search": "sword"})  # search for items containing "sword" in their name/description
    assert r.status_code == 200  # the search endpoint must respond successfully (we don't assert results — "sword" may not exist)


@pytest.mark.regression
def test_pagination_limits_results(auth_token):
    r = get_shop_magic_items(auth_token, params={"per_page": 5})  # request only 5 items per page
    assert r.status_code == 200  # the paginated request must succeed
    items = extract_items(r.json())  # normalize the response (list or paginated object)
    assert len(items) <= 5  # the server must respect the per_page limit and return no more than 5 items


@pytest.mark.regression
def test_bargain_returns_valid_response(auth_token, character):  # character fixture ensures the user has a character (may be required by the API)
    r = bargain(auth_token)  # send POST /shop/bargain — triggers two d20 dice rolls on the server
    assert r.status_code == 200  # the bargain must complete successfully
    data = r.json()  # parse the response body
    assert isinstance(data, dict), f"Ожидался dict, получили: {type(data)}"  # the response must be a JSON object
    has_roll_data = any(k in data for k in ("player_roll", "roll", "multiplier", "result"))  # check for at least one expected key
    assert has_roll_data, f"Неожиданный формат ответа bargain: {data}"  # fail with a clear message if no known keys are present
