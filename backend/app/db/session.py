"""Async engine / session wiring."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.db.runtime_db import prepare_sqlite_database

# Serverless hosts are read-only except /tmp — materialise the DB before the engine opens.
prepare_sqlite_database()


def build_engine(url: str | None = None, **kwargs: Any) -> AsyncEngine:
    url = url or settings.database_url
    options: dict[str, Any] = {"echo": settings.db_echo, "future": True}
    if url.startswith("postgresql"):
        options.update(pool_size=10, max_overflow=20, pool_pre_ping=True)
    options.update(kwargs)
    return create_async_engine(url, **options)


engine: AsyncEngine = build_engine()

SessionFactory = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a request-scoped session."""
    async with SessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
