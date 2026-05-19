import uuid
import pytest
from utils.helpers import load_json


@pytest.fixture(scope="session")
def character(api_client):
    data = load_json("test_character.json")
    data["name"] = f"Tester {uuid.uuid4().hex[:6]}"
    r = api_client.characters.create_character(data)
    assert r.status_code == 200, f"Создание персонажа не удалось: {r.text}"
    return r.json()


@pytest.fixture(scope="session")
def second_character(second_api_client):
    data = load_json("test_character.json")
    data["name"] = f"Receiver {uuid.uuid4().hex[:6]}"
    r = second_api_client.characters.create_character(data)
    assert r.status_code == 200, f"Создание второго персонажа не удалось: {r.text}"
    return r.json()
