from __future__ import annotations

from sqlalchemy import delete, func, select

from app.models.favorite import Favorite
from app.repositories.base import BaseRepository


class FavoriteRepository(BaseRepository):
    """Anonymous, client-id scoped favourites.

    The browser keeps the authoritative copy in localStorage; syncing here is
    opt-in and becomes user-scoped once accounts exist.
    """

    async def tool_ids(self, client_id: str) -> list[int]:
        result = await self.session.execute(
            select(Favorite.tool_id)
            .where(Favorite.client_id == client_id)
            .order_by(Favorite.created_at.desc())
        )
        return [int(row[0]) for row in result.all()]

    async def add(self, client_id: str, tool_id: int) -> None:
        exists = await self.session.execute(
            select(Favorite.id).where(
                Favorite.client_id == client_id, Favorite.tool_id == tool_id
            )
        )
        if exists.scalars().first() is not None:
            return
        self.session.add(Favorite(client_id=client_id, tool_id=tool_id))
        await self.session.flush()

    async def remove(self, client_id: str, tool_id: int) -> None:
        await self.session.execute(
            delete(Favorite).where(
                Favorite.client_id == client_id, Favorite.tool_id == tool_id
            )
        )
        await self.session.flush()

    async def counts_by_tool(self) -> dict[int, int]:
        """Real save counts. Zero rows means the UI shows nothing - never fakes."""
        result = await self.session.execute(
            select(Favorite.tool_id, func.count()).group_by(Favorite.tool_id)
        )
        return {int(row[0]): int(row[1]) for row in result.all()}
