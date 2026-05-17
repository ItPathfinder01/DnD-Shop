import uuid  # standard library module for generating universally unique identifiers
import pytest  # the test framework — we use it for fixtures and configuration hooks
from utils.api_client import register, login, create_character  # HTTP functions that call the DnD Shop API
from utils.helpers import load_json  # helper that reads a JSON file from the testdata folder


def pytest_configure(config):
    # This is a special pytest hook called once before any tests run.
    # We use it to register our custom markers so pytest doesn't warn about unknown marks.
    config.addinivalue_line("markers", "smoke: быстрые проверки что API отвечает")  # register "smoke" marker
    config.addinivalue_line("markers", "regression: детальные проверки бизнес-логики")  # register "regression" marker
    config.addinivalue_line("markers", "integration: тесты с реальным API DnD Shop")  # register "integration" marker


# ─── First user ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")  # scope="session" means this fixture is created once and shared across ALL tests
def user_credentials():
    # Generate a unique email address using a random UUID snippet.
    # uuid.uuid4() creates a random UUID; .hex converts it to a 32-char hex string; [:8] takes the first 8 chars.
    # This guarantees a fresh email on every pytest run, so we never hit "user already exists" errors.
    return {
        "email": f"test_{uuid.uuid4().hex[:8]}@dndtest.com",  # unique email, e.g. test_a3f9b1c2@dndtest.com
        "password": "testpassword123",  # fixed password used for all test users
    }


@pytest.fixture(scope="session")  # also session-scoped — the token is reused by all tests that need auth
def auth_token(user_credentials):  # depends on user_credentials, so pytest injects it automatically
    r = register(user_credentials["email"], user_credentials["password"])  # call POST /auth/register
    assert r.status_code == 200, f"Регистрация не удалась: {r.text}"  # abort the entire session if registration fails
    r = login(user_credentials["email"], user_credentials["password"])  # call POST /auth/login
    assert r.status_code == 200, f"Логин не удался: {r.text}"  # abort if login fails
    return r.json()["access_token"]  # extract the JWT token string from the response and return it


@pytest.fixture(scope="session")  # session-scoped — character is created once and reused across all character/inventory tests
def character(auth_token):  # depends on auth_token to make authenticated requests
    data = load_json("test_character.json")  # read the character template from testdata/test_character.json
    data["name"] = f"Tester {uuid.uuid4().hex[:6]}"  # override the name with a unique value to avoid duplicate-name conflicts
    r = create_character(auth_token, data)  # call POST /characters with the prepared data
    assert r.status_code == 200, f"Создание персонажа не удалось: {r.text}"  # abort if character creation fails
    return r.json()  # return the created character object (dict with id, name, gold, etc.)


# ─── Second user (needed for money/item transfer tests) ───────────────────────

@pytest.fixture(scope="session")  # session-scoped — the second token is created once and shared
def second_auth_token():
    email = f"test2_{uuid.uuid4().hex[:8]}@dndtest.com"  # unique email for the second test user
    r = register(email, "testpassword123")  # register the second user via POST /auth/register
    assert r.status_code == 200  # fail fast if registration fails
    r = login(email, "testpassword123")  # log in as the second user via POST /auth/login
    assert r.status_code == 200  # fail fast if login fails
    return r.json()["access_token"]  # return the JWT token for the second user


@pytest.fixture(scope="session")  # session-scoped — second character is created once
def second_character(second_auth_token):  # depends on second_auth_token to authenticate the request
    data = load_json("test_character.json")  # read the same character template
    data["name"] = f"Receiver {uuid.uuid4().hex[:6]}"  # give the second character a unique name starting with "Receiver"
    r = create_character(second_auth_token, data)  # call POST /characters for the second user
    assert r.status_code == 200, f"Создание второго персонажа не удалось: {r.text}"  # abort if creation fails
    return r.json()  # return the second character object (used in transfer tests)
