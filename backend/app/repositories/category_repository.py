from __future__ import annotations

from sqlalchemy import func, select

from app.core.enums import FREE_PRICING_STATUSES
from app.models.associations import tool_categories
from app.models.category import Category
from app.models.tool import Tool
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository):
    async def list_all(self) -> list[Category]:
        result = await self.session.execute(
            select(Category).order_by(Category.sort_order, Category.name)
        )
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalars().one_or_none()

    async def get_many_by_slugs(self, slugs: list[str]) -> list[Category]:
        if not slugs:
            return []
        result = await self.session.execute(
            select(Category).where(Category.slug.in_(slugs))
        )
        return list(result.scalars().all())

    async def counts(self) -> dict[int, tuple[int, int]]:
        """category_id -> (active tool count, free tool count)."""
        stmt = (
            select(
                tool_categories.c.category_id,
                func.count(Tool.id),
                func.count(Tool.id).filter(
                    Tool.pricing_status.in_(FREE_PRICING_STATUSES)
                ),
            )
            .select_from(tool_categories)
            .join(Tool, Tool.id == tool_categories.c.tool_id)
            .where(Tool.is_active.is_(True))
            .group_by(tool_categories.c.category_id)
        )
        result = await self.session.execute(stmt)
        return {row[0]: (int(row[1]), int(row[2])) for row in result.all()}

    async def add(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.flush()
        return category
