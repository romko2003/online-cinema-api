from __future__ import annotations

import os
import subprocess
from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.tests.utils import truncate_all_tables


@pytest.fixture(scope="session", autouse=True)
def _apply_migrations() -> None:
    """
    Apply migrations once per test session.
    Requires alembic.ini in repo root.
    """
    # Ensure DATABASE_URL is set for test environment
    if not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = settings.DATABASE_URL

    subprocess.run(["alembic", "upgrade", "head"], check=True)


@pytest.fixture(scope="session")
def engine():
    # Uses DATABASE_URL from env / settings (should be test DB)
    return create_async_engine(os.environ.get("DATABASE_URL", settings.DATABASE_URL), echo=False)


@pytest.fixture(scope="session")
def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture()
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        # Clean DB BEFORE each test for isolation
        await truncate_all_tables(session)
        yield session
        # Clean DB AFTER each test too (just in case)
        await truncate_all_tables(session)


@pytest.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Test client with dependency override for DB session.
    """

    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
