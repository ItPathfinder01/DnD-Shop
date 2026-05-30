import uuid
import pytest
import allure
from api import ApiClient
from api.auth import AuthClient
from config.settings import API_BASE_URL

@pytest.fixture
def smoke_user(admin_token):
    email = f"smoke_{uuid.uuid4().hex[:8]}@dndtest.com"
    r = AuthClient().register(email, "testpassword123")
    assert r.status_code == 201, f"Регистрация не удалась: {r.text}"
    data = r.json()
    yield email, data
    ApiClient(token=admin_token).admin.delete_user(data["id"])


@allure.feature("Auth")
@allure.story("Health check")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_api_is_alive():
    with allure.step(f"GET {API_BASE_URL}/health"):
        r = AuthClient().health_check()
    assert r.status_code == 200


@allure.feature("Auth")
@allure.story("Registration")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_register_new_user(smoke_user):
    email, data = smoke_user
    with allure.step(f"Проверяем данные зарегистрированного пользователя email={email}"):
        assert "id" in data
        assert data["email"] == email
        assert "is_superadmin" in data


@allure.feature("Auth")
@allure.story("Login")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_login_returns_token(auth_token):
    with allure.step(f"POST {API_BASE_URL}/auth/login → проверяем JWT токен"):
        assert isinstance(auth_token, str) and len(auth_token) > 10


@allure.feature("Auth")
@allure.story("Login")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_get_current_user(api_client, user_credentials):
    with allure.step(f"GET {API_BASE_URL}/auth/me"):
        r = api_client.auth.get_me()
    assert r.status_code == 200
    data = r.json()
    with allure.step(f"Проверяем email={user_credentials['email']} и наличие id"):
        assert data["email"] == user_credentials["email"]
        assert "id" in data


@allure.feature("Auth")
@allure.story("Registration")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_register_duplicate_email_fails(user_credentials):
    with allure.step(f"POST {API_BASE_URL}/auth/register — повторная регистрация того же email"):
        r = AuthClient().register(user_credentials["email"], user_credentials["password"])
    assert r.status_code in (400, 409, 422)


@allure.feature("Auth")
@allure.story("Login")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_login_wrong_password_fails(user_credentials):
    with allure.step(f"POST {API_BASE_URL}/auth/login — неверный пароль"):
        r = AuthClient().login(user_credentials["email"], "totally_wrong_password")
    assert r.status_code in (400, 401, 403)


@allure.feature("Auth")
@allure.story("Login")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_login_nonexistent_user_fails():
    with allure.step(f"POST {API_BASE_URL}/auth/login — несуществующий пользователь"):
        r = AuthClient().login("nobody_at_all@dndtest.com", "somepassword")
    assert r.status_code in (400, 401, 403, 404)


@allure.feature("Auth")
@allure.story("Authorization")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_protected_route_without_token_fails():
    with allure.step(f"GET {API_BASE_URL}/auth/me — без токена"):
        r = AuthClient().get_me()
    assert r.status_code in (401, 403, 422)


@allure.feature("Auth")
@allure.story("Registration")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_register_short_password_fails():
    email = f"short_{uuid.uuid4().hex[:6]}@dndtest.com"
    with allure.step(f"POST {API_BASE_URL}/auth/register — пароль слишком короткий (3 символа)"):
        r = AuthClient().register(email, "abc")
    assert r.status_code in (400, 422)
