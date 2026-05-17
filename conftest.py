import uuid
import pytest
from utils.api_client import register, login, create_character
from utils.helpers import load_json


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: быстрые проверки что API отвечает")
    config.addinivalue_line("markers", "regression: детальные проверки бизнес-логики")
    config.addinivalue_line("markers", "integration: тесты с реальным API DnD Shop")


# ─── Первый пользователь ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def user_credentials():
    return {
        "email": f"test_{uuid.uuid4().hex[:8]}@dndtest.com",
        "password": "testpassword123",
    }


@pytest.fixture(scope="session")
def auth_token(user_credentials):
    r = register(user_credentials["email"], user_credentials["password"])
    assert r.status_code == 200, f"Регистрация не удалась: {r.text}"
    r = login(user_credentials["email"], user_credentials["password"])
    assert r.status_code == 200, f"Логин не удался: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def character(auth_token):
    data = load_json("test_character.json")
    data["name"] = f"Tester {uuid.uuid4().hex[:6]}"
    r = create_character(auth_token, data)
    assert r.status_code == 200, f"Создание персонажа не удалось: {r.text}"
    return r.json()


# ─── Второй пользователь (для тестов передачи предметов/денег) ────────────────

@pytest.fixture(scope="session")
def second_auth_token():
    email = f"test2_{uuid.uuid4().hex[:8]}@dndtest.com"
    r = register(email, "testpassword123")
    assert r.status_code == 200
    r = login(email, "testpassword123")
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def second_character(second_auth_token):
    data = load_json("test_character.json")
    data["name"] = f"Receiver {uuid.uuid4().hex[:6]}"
    r = create_character(second_auth_token, data)
    assert r.status_code == 200, f"Создание второго персонажа не удалось: {r.text}"
    return r.json()
