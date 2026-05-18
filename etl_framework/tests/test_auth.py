import uuid  # used to generate unique email addresses for each test run
import pytest  # test framework — provides markers, assertions, and test discovery
from utils.api_client import health_check, register, login, get_me  # HTTP wrapper functions for auth endpoints


@pytest.mark.smoke  # "smoke" tests are fast checks that the API is alive — run these first
def test_api_is_alive():
    r = health_check()  # send GET /health — a public endpoint that requires no authentication
    assert r.status_code == 200  # 200 means the server is up and running


@pytest.mark.smoke
def test_register_new_user():
    email = f"smoke_{uuid.uuid4().hex[:8]}@dndtest.com"  # generate a unique email so this test never conflicts with previous runs
    r = register(email, "testpassword123")  # send POST /auth/register with the new credentials
    assert r.status_code == 201  # API should return 200 and the new user object
    data = r.json()  # parse the response body from JSON into a Python dict
    assert "id" in data  # the response must contain an "id" field (the user's database ID)
    assert data["email"] == email  # the returned email must match what we sent
    assert "is_superadmin" in data  # every user object must have the admin flag field


@pytest.mark.smoke
def test_login_returns_token(auth_token):  # auth_token fixture from conftest.py registers + logs in a test user
    assert isinstance(auth_token, str) and len(auth_token) > 10  # a valid JWT token is a long string (100+ chars)


@pytest.mark.smoke
def test_get_current_user(auth_token, user_credentials):  # user_credentials provides the email we registered with
    r = get_me(auth_token)  # send GET /auth/me with the Bearer token in the Authorization header
    assert r.status_code == 200  # server should recognize the token and return the user profile
    data = r.json()  # parse the response body
    assert data["email"] == user_credentials["email"]  # the returned email must match the one we used to register
    assert "id" in data  # the user object must always include the database ID


@pytest.mark.regression  # "regression" tests cover detailed business logic and edge cases
def test_register_duplicate_email_fails(user_credentials):  # use the same credentials that are already registered
    r = register(user_credentials["email"], user_credentials["password"])  # try to register the same email a second time
    assert r.status_code in (400, 409, 422)  # the API must reject duplicates with a 4xx error


@pytest.mark.regression
def test_login_wrong_password_fails(user_credentials):
    r = login(user_credentials["email"], "totally_wrong_password")  # send correct email but wrong password
    assert r.status_code in (400, 401, 403)  # the API must reject invalid credentials


@pytest.mark.regression
def test_login_nonexistent_user_fails():
    r = login("nobody_at_all@dndtest.com", "somepassword")  # use an email that was never registered
    assert r.status_code in (400, 401, 403, 404)  # the API must return an error for unknown users


@pytest.mark.regression
def test_protected_route_without_token_fails():
    r = get_me("")  # call GET /auth/me with an empty string instead of a real JWT token
    assert r.status_code in (401, 403, 422)  # the API must block unauthenticated access


@pytest.mark.regression
def test_register_short_password_fails():
    r = register(f"short_{uuid.uuid4().hex[:6]}@dndtest.com", "abc")  # password "abc" is only 3 chars; minimum is 6
    assert r.status_code in (400, 422)  # the API must reject passwords that are too short (Pydantic validation → 422)
