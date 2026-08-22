from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.collection import Collection
from app.models.tool import Tool
from app.repositories.base import BaseRepository


class CollectionRepository(BaseRepository):
    @staticmethod
    def _eager(stmt):
        return stmt.options(
            selectinload(Collection.tools).selectinload(Tool.categories),
            selectinload(Collection.tools).selectinload(Tool.tags),
            selectinload(Collection.tools).selectinload(Tool.pricing_plans),
            selectinload(Collection.tools).selectinload(Tool.free_access_grants),
        )

    async def list_all(self, featured_only: bool = False) -> list[Collection]:
        stmt = select(Collection)
        if featured_only:
            stmt = stmt.where(Collection.is_featured.is_(True))
        stmt = self._eager(stmt).order_by(Collection.sort_order, Collection.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_slug(self, slug: str) -> Collection | None:
        stmt = self._eager(select(Collection).where(Collection.slug == slug))
        result = await self.session.execute(stmt)
        return result.scalars().unique().one_or_none()

    async def add(self, collection: Collection) -> Collection:
        self.session.add(collection)
        await self.session.flush()
        return collection
