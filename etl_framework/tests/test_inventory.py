import pytest  # test framework — provides markers and test discovery
from utils.api_client import (
    get_inventory,           # GET /inventory         — returns the character's full inventory list
    add_to_inventory,        # POST /inventory        — adds an item (or increments quantity if it already exists)
    delete_from_inventory,   # DELETE /inventory/{id} — removes an inventory entry by its ID
    get_shop_magic_items,    # GET /shop/magic-items  — used to find a real item ID to add to inventory
)
from utils.helpers import extract_items  # helper that handles both list and paginated {"items": [...]} responses


def _first_shop_item_id(auth_token: str) -> int:
    # Private helper that fetches the shop and returns the ID of the very first magic item.
    # Used by multiple tests to get a real, valid item ID without duplicating the fetch logic.
    items = extract_items(get_shop_magic_items(auth_token).json())  # fetch all magic items and normalize the format
    assert items, "Магазин пуст — тест невозможен"  # if the shop is empty, tests cannot proceed — fail immediately
    return items[0]["id"]  # return only the ID of the first item in the list


@pytest.mark.smoke
def test_get_inventory_returns_list(auth_token, character):  # character fixture ensures the user has a character before the test
    r = get_inventory(auth_token)  # send GET /inventory with the Bearer token
    assert r.status_code == 200  # the endpoint must respond successfully
    assert isinstance(r.json(), list)  # inventory always returns a JSON array (empty list if no items)


@pytest.mark.regression
def test_add_item_to_inventory(auth_token, character):
    item_id = _first_shop_item_id(auth_token)  # get a real item ID from the shop to use in this test
    r = add_to_inventory(auth_token, {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1})  # send POST /inventory
    assert r.status_code in (200, 201)  # 200 = updated existing, 201 = created new entry — both are valid success codes
    inv_item = r.json()  # parse the returned inventory item object
    assert "id" in inv_item  # the created/updated entry must have a database ID

    delete_from_inventory(auth_token, inv_item["id"])  # cleanup: remove the item so it doesn't affect other tests


@pytest.mark.regression
def test_inventory_item_has_required_fields(auth_token, character):
    item_id = _first_shop_item_id(auth_token)  # fetch a valid shop item ID
    r = add_to_inventory(auth_token, {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1})  # add the item
    inv_item = r.json()  # parse the inventory item from the response

    for field in ("id", "item_type", "quantity"):  # these three fields must always be present in any inventory item
        assert field in inv_item, f"Отсутствует поле: {field}"  # fail with the name of the missing field

    delete_from_inventory(auth_token, inv_item["id"])  # cleanup: remove the item after checking its fields


@pytest.mark.regression
def test_delete_item_from_inventory(auth_token, character):
    item_id = _first_shop_item_id(auth_token)  # get a valid shop item ID
    # Add the item and immediately extract the inventory entry ID from the response in one line
    inv_item_id = add_to_inventory(auth_token, {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1}).json()["id"]

    r = delete_from_inventory(auth_token, inv_item_id)  # send DELETE /inventory/{inv_item_id}
    assert r.status_code == 200  # the deletion must succeed

    remaining_ids = [i["id"] for i in get_inventory(auth_token).json()]  # fetch the inventory again and collect all remaining IDs
    assert inv_item_id not in remaining_ids  # the deleted item's ID must no longer appear in the inventory


@pytest.mark.regression
def test_add_same_item_twice_increments_quantity(auth_token, character):
    item_id = _first_shop_item_id(auth_token)  # get a valid shop item ID
    payload = {"item_type": "magic_item", "shop_item_id": item_id, "quantity": 1}  # define the payload once and reuse it

    r1 = add_to_inventory(auth_token, payload)  # add the item for the first time
    assert r1.status_code in (200, 201)  # must succeed
    inv_item = r1.json()  # save the inventory entry (we need its ID for cleanup later)

    add_to_inventory(auth_token, payload)  # add the exact same item a second time — should increment quantity, not create a duplicate

    inventory = get_inventory(auth_token).json()  # fetch the full inventory to verify the quantity
    # Find all entries that match this specific shop item and type (there should be exactly one)
    matching = [i for i in inventory if i.get("shop_item_id") == item_id and i.get("item_type") == "magic_item"]
    assert matching, "Предмет не найден в инвентаре"  # the item must exist in the inventory
    assert matching[0]["quantity"] >= 2, "Количество не увеличилось"  # after adding twice, quantity must be at least 2

    delete_from_inventory(auth_token, inv_item["id"])  # cleanup: remove the item (deletes the entry entirely)
