import pytest
from fastapi.testclient import TestClient

from app.core.db import get_sessionmaker
from app.core.security import hash_password
from app.core.settings import get_settings
from app.repositories import users
from app.services.auth import ensure_admin

pytestmark = pytest.mark.integration


def _make_user(email: str = "me@example.com", password: str = "pw-123456") -> None:
    with get_sessionmaker()() as db:
        users.create(db, email=email, password_hash=hash_password(password))
        db.commit()


def test_me_requires_login(client: TestClient) -> None:
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "UNAUTHENTICATED"


def test_login_me_logout(client: TestClient) -> None:
    _make_user()
    r = client.post("/api/v1/auth/login", json={"email": "ME@example.com", "password": "pw-123456"})
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "me@example.com"  # citext: case-insensitive match

    assert client.get("/api/v1/auth/me").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401


def test_wrong_password_and_rate_limit(client: TestClient) -> None:
    _make_user()
    limit = get_settings().login_max_attempts
    for _ in range(limit):
        r = client.post("/api/v1/auth/login", json={"email": "me@example.com", "password": "no"})
        assert r.status_code == 401
    # Even the right password is refused once the limit is hit.
    r = client.post("/api/v1/auth/login", json={"email": "me@example.com", "password": "pw-123456"})
    assert r.status_code == 429
    assert r.json()["error"]["code"] == "RATE_LIMITED"


def test_ensure_admin_is_idempotent(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "admin-pass-123")
    get_settings.cache_clear()
    settings = get_settings()
    with get_sessionmaker()() as db:
        assert ensure_admin(db, settings) is True
        assert ensure_admin(db, settings) is False
    r = client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": "admin-pass-123"}
    )
    assert r.status_code == 200
