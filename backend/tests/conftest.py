"""Test fixtures.

The seeded dataset is built once into a temporary SQLite file. Each test then
opens its own engine against that file, which keeps every test on its own event
loop and avoids cross-loop connection reuse.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.security import rate_limiter
from app.db.init_db import create_all
from app.db.session import build_engine, get_db
from app.main import app
from app.seed.seeder import seed

ADMIN_KEY = "test-admin-key"


@pytest.fixture(scope="session")
def database_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    path: Path = tmp_path_factory.mktemp("devai") / "test.db"
    url = f"sqlite+aiosqlite:///{path.as_posix()}"

    async def build() -> None:
        engine = build_engine(url)
        await create_all(engine)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            await seed(session)
        await engine.dispose()

    asyncio.run(build())
    return url


@pytest_asyncio.fixture
async def session_factory(database_url: str):
    engine = build_engine(database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db(session_factory) -> AsyncSession:
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(session_factory) -> AsyncClient:
    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    rate_limiter.reset()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http:
        yield http
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    monkeypatch.setattr(settings, "admin_api_key", ADMIN_KEY)
    return {"X-Admin-Api-Key": ADMIN_KEY}
