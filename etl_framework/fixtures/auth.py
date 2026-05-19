import uuid
import pytest
from api import ApiClient
from api.auth import AuthClient
from config.settings import SUPERADMIN_EMAIL, SUPERADMIN_PASSWORD


@pytest.fixture(scope="session")
def user_credentials():
    return {
        "email": f"test_{uuid.uuid4().hex[:8]}@dndtest.com",
        "password": "testpassword123",
    }


@pytest.fixture(scope="session")
def auth_token(user_credentials):
    client = AuthClient()
    r = client.register(user_credentials["email"], user_credentials["password"])
    assert r.status_code == 201, f"Регистрация не удалась: {r.text}"
    r = client.login(user_credentials["email"], user_credentials["password"])
    assert r.status_code == 200, f"Логин не удался: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def api_client(auth_token):
    return ApiClient(token=auth_token)


@pytest.fixture(scope="session")
def second_auth_token():
    email = f"test2_{uuid.uuid4().hex[:8]}@dndtest.com"
    client = AuthClient()
    r = client.register(email, "testpassword123")
    assert r.status_code == 200
    r = client.login(email, "testpassword123")
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def second_api_client(second_auth_token):
    return ApiClient(token=second_auth_token)


@pytest.fixture(scope="session")
def superadmin_token():
    r = AuthClient().login(SUPERADMIN_EMAIL, SUPERADMIN_PASSWORD)
    assert r.status_code == 200, f"Логин суперадмина не удался: {r.text}"
    return r.json()["access_token"]
