import pytest


@pytest.mark.smoke
def test_character_was_created(character):
    assert character is not None
    assert "id" in character
    assert "name" in character


@pytest.mark.smoke
def test_get_my_character(api_client, character):
    r = api_client.characters.get_my_character()
    assert r.status_code == 200
    assert r.json()["id"] == character["id"]


@pytest.mark.regression
def test_character_has_required_fields(character):
    required = {"id", "name", "race", "age", "gold", "silver", "copper", "platinum", "electrum"}
    missing = required - character.keys()
    assert not missing, f"Отсутствуют поля: {missing}"


@pytest.mark.regression
def test_character_initial_currency(character):
    assert character["gold"] == 10000
    assert character["platinum"] == 0


@pytest.mark.regression
def test_update_character_description(api_client):
    new_desc = "Updated by automated test"
    r = api_client.characters.update_character({"description": new_desc})
    assert r.status_code == 200
    assert r.json()["description"] == new_desc


@pytest.mark.regression
def test_get_all_characters_returns_list(api_client, second_character):
    r = api_client.characters.get_characters()
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.regression
def test_second_character_not_in_own_list(api_client, character, second_character):
    """GET /characters возвращает всех, кроме персонажа текущего пользователя."""
    r = api_client.characters.get_characters()
    own_id = character["id"]
    ids = [c["id"] for c in r.json()]
    assert own_id not in ids


@pytest.mark.regression
def test_cannot_create_second_character(api_client):
    r = api_client.characters.create_character({
        "name": f"Duplicate {id(object())}",
        "race": "Elf",
        "age": 100,
        "description": "Should fail — user already has a character",
    })
    assert r.status_code in (400, 409, 422)


@pytest.mark.regression
def test_transfer_gold_to_second_character(api_client, character, second_character):
    gold_before = character["gold"]
    r = api_client.characters.transfer_money({
        "to_character_id": second_character["id"],
        "platinum": 0,
        "gold": 1,
        "electrum": 0,
        "silver": 0,
        "copper": 0,
    })
    assert r.status_code == 200

    r2 = api_client.characters.get_my_character()
    assert r2.json()["gold"] == gold_before - 1
