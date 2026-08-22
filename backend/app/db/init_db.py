"""Schema bootstrap helpers.

PostgreSQL deployments use Alembic. ``create_all`` exists for SQLite dev and for
the test suite, where migrations would only slow the feedback loop.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.base import Base
from app.models import *  # noqa: F401,F403  - registers every mapper


async def create_all(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def drop_all(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
