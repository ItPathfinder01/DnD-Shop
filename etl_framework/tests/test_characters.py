import pytest  # test framework — provides markers and test discovery
from utils.api_client import (
    get_my_character,   # GET /characters/me — returns the current user's character
    update_character,   # PUT /characters/me — updates fields on the current user's character
    get_characters,     # GET /characters   — returns all characters except the current user's
    transfer_money,     # POST /characters/me/transfer/money — sends currency to another character
    create_character,   # POST /characters  — creates a new character for the current user
)


@pytest.mark.smoke
def test_character_was_created(character):  # "character" fixture from conftest.py creates the character before the test
    assert character is not None  # the fixture must have returned a non-null value
    assert "id" in character  # every character in the database must have a unique ID
    assert "name" in character  # every character must have a name


@pytest.mark.smoke
def test_get_my_character(auth_token, character):
    r = get_my_character(auth_token)  # send GET /characters/me with the Bearer token
    assert r.status_code == 200  # the server should find the character and return it
    assert r.json()["id"] == character["id"]  # the returned ID must match the one we created in the fixture


@pytest.mark.regression
def test_character_has_required_fields(character):
    required = {"id", "name", "race", "age", "gold", "silver", "copper", "platinum", "electrum"}  # all fields a D&D character must have
    missing = required - character.keys()  # set difference: fields in "required" that are not in the character dict
    assert not missing, f"Отсутствуют поля: {missing}"  # fail with a clear message listing the missing fields


@pytest.mark.regression
def test_character_initial_currency(character):
    assert character["gold"] == 10000  # we set gold=10000 in test_character.json — verify it was saved correctly
    assert character["platinum"] == 0  # platinum was set to 0 in the template — should remain 0


@pytest.mark.regression
def test_update_character_description(auth_token):
    new_desc = "Updated by automated test"  # the new description string we want to save
    r = update_character(auth_token, {"description": new_desc})  # send PUT /characters/me with only the description field
    assert r.status_code == 200  # the update should succeed
    assert r.json()["description"] == new_desc  # the returned object must reflect the change we just made


@pytest.mark.regression
def test_get_all_characters_returns_list(auth_token, second_character):  # second_character ensures there is at least one other character
    r = get_characters(auth_token)  # send GET /characters — should return other players' characters
    assert r.status_code == 200  # the endpoint must respond successfully
    assert isinstance(r.json(), list)  # the response body must be a JSON array


@pytest.mark.regression
def test_second_character_not_in_own_list(auth_token, character, second_character):
    # GET /characters returns everyone EXCEPT the current user's character.
    # This test verifies that the API correctly excludes the caller's own character.
    r = get_characters(auth_token)  # fetch the list of other characters
    own_id = character["id"]  # the ID of our own character (should NOT appear in the list)
    ids = [c["id"] for c in r.json()]  # extract just the IDs from all returned characters
    assert own_id not in ids  # our own character must be absent from the list


@pytest.mark.regression
def test_cannot_create_second_character(auth_token):
    # Each user account can only have one character.
    # This test verifies that trying to create a second one is rejected.
    r = create_character(auth_token, {
        "name": f"Duplicate {id(object())}",  # use id(object()) for a unique name — avoids false failures from name conflicts
        "race": "Elf",  # any valid race
        "age": 100,  # any valid age
        "description": "Should fail — user already has a character",  # describes the intent
    })
    assert r.status_code in (400, 409, 422)  # the API must reject the second character creation


@pytest.mark.regression
def test_transfer_gold_to_second_character(auth_token, character, second_character):
    gold_before = character["gold"]  # save the sender's gold balance before the transfer
    r = transfer_money(auth_token, {
        "to_character_id": second_character["id"],  # the ID of the character that will receive the money
        "platinum": 0,  # no platinum transferred
        "gold": 1,  # transfer exactly 1 gold coin
        "electrum": 0,  # no electrum transferred
        "silver": 0,  # no silver transferred
        "copper": 0,  # no copper transferred
    })
    assert r.status_code == 200  # the transfer must succeed

    r2 = get_my_character(auth_token)  # fetch the sender's character again to check the updated balance
    assert r2.json()["gold"] == gold_before - 1  # the sender should have exactly 1 less gold after the transfer
