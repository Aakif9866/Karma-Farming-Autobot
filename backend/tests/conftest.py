"""Test setup.

Unit tests need nothing. Integration tests (marked `integration`) need Postgres+pgvector and Redis;
they use a separate `<db>_test` database (created on demand, migrated), never the dev DB.
"""

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("APP_ENV", "ci")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://kfa:kfa@localhost:5432/kfa")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")

from sqlalchemy import create_engine, make_url, text


def _test_db_url() -> str:
    url = make_url(os.environ["DATABASE_URL"])
    return url.set(database=f"{url.database}_test").render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def migrated_db() -> str:
    from alembic.config import Config

    from alembic import command

    test_url = _test_db_url()
    admin = create_engine(make_url(test_url).set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        name = make_url(test_url).database
        if not conn.scalar(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": name}):
            conn.execute(text(f'CREATE DATABASE "{name}"'))
    admin.dispose()

    cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "..", "alembic"))
    cfg.attributes["database_url"] = test_url
    command.upgrade(cfg, "head")
    return test_url


@pytest.fixture
def client(migrated_db: str) -> Iterator["TestClient"]:  # type: ignore[name-defined]  # noqa: F821
    from fastapi.testclient import TestClient

    from app.core.db import get_engine, get_sessionmaker
    from app.core.redis import get_redis
    from app.core.settings import get_settings

    os.environ["DATABASE_URL"] = migrated_db
    for cached in (get_settings, get_engine, get_sessionmaker):
        cached.cache_clear()
    get_redis().flushdb()
    with get_engine().begin() as conn:
        conn.execute(text("TRUNCATE users CASCADE"))

    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c
