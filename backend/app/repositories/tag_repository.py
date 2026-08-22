from __future__ import annotations

from sqlalchemy import func, select

from app.models.associations import tool_tags
from app.models.tag import Tag
from app.models.tool import Tool
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository):
    async def list_by_kind(self, kind: str) -> list[Tag]:
        result = await self.session.execute(
            select(Tag).where(Tag.kind == kind).order_by(Tag.name)
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[Tag]:
        result = await self.session.execute(select(Tag).order_by(Tag.kind, Tag.name))
        return list(result.scalars().all())

    async def get(self, kind: str, slug: str) -> Tag | None:
        result = await self.session.execute(
            select(Tag).where(Tag.kind == kind, Tag.slug == slug)
        )
        return result.scalars().one_or_none()

    async def counts(self) -> dict[int, int]:
        stmt = (
            select(tool_tags.c.tag_id, func.count(Tool.id))
            .select_from(tool_tags)
            .join(Tool, Tool.id == tool_tags.c.tool_id)
            .where(Tool.is_active.is_(True))
            .group_by(tool_tags.c.tag_id)
        )
        result = await self.session.execute(stmt)
        return {row[0]: int(row[1]) for row in result.all()}

    async def add(self, tag: Tag) -> Tag:
        self.session.add(tag)
        await self.session.flush()
        return tag
