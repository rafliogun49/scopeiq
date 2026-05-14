from fastapi.testclient import TestClient

EMAIL = "alice@example.com"
PASSWORD = "supersecret123"


def _signup(client: TestClient, email: str = EMAIL, password: str = PASSWORD):
    return client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": password},
    )


def _login(client: TestClient, email: str = EMAIL, password: str = PASSWORD):
    return client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )


def test_signup_returns_token_and_user(client: TestClient):
    r = _signup(client)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]
    assert body["user"]["email"] == EMAIL
    assert "id" in body["user"]


def test_signup_duplicate_email_returns_409(client: TestClient):
    assert _signup(client).status_code == 201
    r = _signup(client)
    assert r.status_code == 409


def test_login_success(client: TestClient):
    assert _signup(client).status_code == 201
    r = _login(client)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["access_token"]
    assert body["user"]["email"] == EMAIL


def test_login_wrong_password_returns_401(client: TestClient):
    assert _signup(client).status_code == 201
    r = _login(client, password="not-the-password")
    assert r.status_code == 401


def test_login_unknown_email_returns_401(client: TestClient):
    r = _login(client, email="nobody@example.com")
    assert r.status_code == 401


def test_me_with_valid_token_returns_user(client: TestClient):
    token = _signup(client).json()["access_token"]
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    assert r.json()["email"] == EMAIL


def test_me_without_token_returns_401(client: TestClient):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_me_with_garbage_token_returns_401(client: TestClient):
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert r.status_code == 401
