from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.core.db import get_session
from app.main import app
from app.models import User  # noqa: F401  -- ensure all models are registered with metadata


def _resolve_test_database_url() -> str:
    url = settings.TEST_DATABASE_URL
    if not url:
        raise RuntimeError(
            "TEST_DATABASE_URL is not set. Tests require a dedicated Postgres test database "
            "(e.g. postgresql+psycopg://scopeiq:changeme@localhost:5432/scopeiq_test)."
        )
    if url == settings.DATABASE_URL:
        raise RuntimeError(
            "TEST_DATABASE_URL must differ from DATABASE_URL — tests truncate tables."
        )
    return url


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(_resolve_test_database_url(), echo=False)
    SQLModel.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine) -> Generator[Session, None, None]:
    with Session(engine) as s:
        yield s
        s.rollback()
    with engine.begin() as conn:
        # Truncate every registered table; CASCADE handles FKs.
        tables = ", ".join(f'"{t.name}"' for t in reversed(SQLModel.metadata.sorted_tables))
        if tables:
            conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
def client(session) -> Generator[TestClient, None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
