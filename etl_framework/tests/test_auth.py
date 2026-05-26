import uuid
import pytest
from api import ApiClient
from api.auth import AuthClient


@pytest.fixture
def smoke_user(admin_token):
    email = f"smoke_{uuid.uuid4().hex[:8]}@dndtest.com"
    r = AuthClient().register(email, "testpassword123")
    assert r.status_code == 201, f"Регистрация не удалась: {r.text}"
    data = r.json()
    yield email, data
    ApiClient(token=admin_token).admin.delete_user(data["id"])


@pytest.mark.smoke
def test_api_is_alive():
    r = AuthClient().health_check()
    assert r.status_code == 200


@pytest.mark.smoke
def test_register_new_user(smoke_user):
    email, data = smoke_user
    assert "id" in data
    assert data["email"] == email
    assert "is_superadmin" in data


@pytest.mark.smoke
def test_login_returns_token(auth_token):
    assert isinstance(auth_token, str) and len(auth_token) > 10


@pytest.mark.smoke
def test_get_current_user(api_client, user_credentials):
    r = api_client.auth.get_me()
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == user_credentials["email"]
    assert "id" in data


@pytest.mark.regression
def test_register_duplicate_email_fails(user_credentials):
    r = AuthClient().register(user_credentials["email"], user_credentials["password"])
    assert r.status_code in (400, 409, 422)


@pytest.mark.regression
def test_login_wrong_password_fails(user_credentials):
    r = AuthClient().login(user_credentials["email"], "totally_wrong_password")
    assert r.status_code in (400, 401, 403)


@pytest.mark.regression
def test_login_nonexistent_user_fails():
    r = AuthClient().login("nobody_at_all@dndtest.com", "somepassword")
    assert r.status_code in (400, 401, 403, 404)


@pytest.mark.regression
def test_protected_route_without_token_fails():
    r = AuthClient().get_me()
    assert r.status_code in (401, 403, 422)


@pytest.mark.regression
def test_register_short_password_fails():
    r = AuthClient().register(f"short_{uuid.uuid4().hex[:6]}@dndtest.com", "abc")
    assert r.status_code in (400, 422)
