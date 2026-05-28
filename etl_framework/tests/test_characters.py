import pytest
import allure
from config.settings import API_BASE_URL


@allure.feature("Characters")
@allure.story("Create character")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_character_was_created(character):
    with allure.step("Проверяем что персонаж создан и содержит id и name"):
        assert character is not None
        assert "id" in character
        assert "name" in character


@allure.feature("Characters")
@allure.story("Get character")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_get_my_character(api_client, character):
    with allure.step(f"GET {API_BASE_URL}/characters/me"):
        r = api_client.characters.get_my_character()
    assert r.status_code == 200
    with allure.step(f"Проверяем что id персонажа совпадает с id={character['id']}"):
        assert r.json()["id"] == character["id"]


@allure.feature("Characters")
@allure.story("Get character")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_character_has_required_fields(character):
    required = {"id", "name", "race", "age", "gold", "silver", "copper", "platinum", "electrum"}
    with allure.step(f"Проверяем наличие обязательных полей: {required}"):
        missing = required - character.keys()
        assert not missing, f"Отсутствуют поля: {missing}"


@allure.feature("Characters")
@allure.story("Create character")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_character_initial_currency(character):
    with allure.step("Проверяем стартовую валюту: gold=10000, platinum=0"):
        assert character["gold"] == 10000
        assert character["platinum"] == 0


@allure.feature("Characters")
@allure.story("Update character")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_update_character_description(api_client):
    new_desc = "Updated by automated test"
    with allure.step(f"PUT {API_BASE_URL}/characters/me — обновляем description"):
        r = api_client.characters.update_character({"description": new_desc})
    assert r.status_code == 200
    with allure.step(f"Проверяем что description обновился на '{new_desc}'"):
        assert r.json()["description"] == new_desc


@allure.feature("Characters")
@allure.story("Get character")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_get_all_characters_returns_list(api_client, second_character):
    with allure.step(f"GET {API_BASE_URL}/characters"):
        r = api_client.characters.get_characters()
    assert r.status_code == 200
    with allure.step("Проверяем что ответ является списком"):
        assert isinstance(r.json(), list)


@allure.feature("Characters")
@allure.story("Get character")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_second_character_not_in_own_list(api_client, character, second_character):
    with allure.step(f"GET {API_BASE_URL}/characters"):
        r = api_client.characters.get_characters()
    with allure.step(f"Проверяем что собственный персонаж id={character['id']} не входит в список"):
        ids = [c["id"] for c in r.json()]
        assert character["id"] not in ids


@allure.feature("Characters")
@allure.story("Create character")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_cannot_create_second_character(api_client):
    with allure.step(f"POST {API_BASE_URL}/characters — попытка создать второго персонажа"):
        r = api_client.characters.create_character({
            "name": f"Duplicate {id(object())}",
            "race": "Elf",
            "age": 100,
            "description": "Should fail — user already has a character",
        })
    with allure.step("Проверяем что API отклонил запрос (400/409/422)"):
        assert r.status_code in (400, 409, 422)


@allure.feature("Characters")
@allure.story("Transfer")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_transfer_gold_to_second_character(api_client, character, second_character):
    gold_before = character["gold"]
    with allure.step(f"POST {API_BASE_URL}/characters/me/transfer/money — переводим 1 gold персонажу id={second_character['id']}"):
        r = api_client.characters.transfer_money({
            "to_character_id": second_character["id"],
            "platinum": 0,
            "gold": 1,
            "electrum": 0,
            "silver": 0,
            "copper": 0,
        })
    assert r.status_code == 200
    with allure.step(f"Проверяем что gold уменьшился с {gold_before} до {gold_before - 1}"):
        r2 = api_client.characters.get_my_character()
        assert r2.json()["gold"] == gold_before - 1
