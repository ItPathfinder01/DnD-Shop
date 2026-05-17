import uuid
import pytest
from utils.api_client import health_check, register, login, get_me


@pytest.mark.smoke
def test_api_is_alive():
    r = health_check()
    assert r.status_code == 200


@pytest.mark.smoke
def test_register_new_user():
    email = f"smoke_{uuid.uuid4().hex[:8]}@dndtest.com"
    r = register(email, "testpassword123")
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert data["email"] == email
    assert "is_superadmin" in data


@pytest.mark.smoke
def test_login_returns_token(auth_token):
    assert isinstance(auth_token, str) and len(auth_token) > 10


@pytest.mark.smoke
def test_get_current_user(auth_token, user_credentials):
    r = get_me(auth_token)
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == user_credentials["email"]
    assert "id" in data


@pytest.mark.regression
def test_register_duplicate_email_fails(user_credentials):
    r = register(user_credentials["email"], user_credentials["password"])
    assert r.status_code in (400, 409, 422)


@pytest.mark.regression
def test_login_wrong_password_fails(user_credentials):
    r = login(user_credentials["email"], "totally_wrong_password")
    assert r.status_code in (400, 401, 403)


@pytest.mark.regression
def test_login_nonexistent_user_fails():
    r = login("nobody_at_all@dndtest.com", "somepassword")
    assert r.status_code in (400, 401, 403, 404)


@pytest.mark.regression
def test_protected_route_without_token_fails():
    r = get_me("")
    assert r.status_code in (401, 403, 422)


@pytest.mark.regression
def test_register_short_password_fails():
    r = register(f"short_{uuid.uuid4().hex[:6]}@dndtest.com", "abc")
    assert r.status_code in (400, 422)
