"""Query construction for tools: filtering, ranking, facets.

Search runs on PostgreSQL full-text search when available and falls back to a
portable LIKE-based scorer so the project still boots on SQLite.
"""

from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import Select, and_, case, func, literal, or_, select
from sqlalchemy.orm import selectinload

from app.core.enums import (
    FREE_PRICING_STATUSES,
    PRICING_FREENESS_RANK,
    TagKind,
)
from app.core.pagination import PageParams
from app.models.category import Category
from app.models.tag import Tag
from app.models.tool import Tool
from app.repositories.base import BaseRepository
from app.schemas.search import ToolFilters

#: Weights applied to the portable LIKE scorer.
_NAME_WEIGHT = 12
_TAGLINE_WEIGHT = 6
_DOCUMENT_WEIGHT = 3


class ToolRepository(BaseRepository):
    # ------------------------------------------------------------------ base

    @staticmethod
    def _eager(stmt: Select) -> Select:
        return stmt.options(
            selectinload(Tool.categories),
            selectinload(Tool.tags),
            selectinload(Tool.pricing_plans),
            selectinload(Tool.free_access_grants),
        )

    @staticmethod
    def _active() -> Select:
        return select(Tool).where(Tool.is_active.is_(True))

    # --------------------------------------------------------------- filters

    def _apply_filters(self, stmt: Select, filters: ToolFilters) -> Select:
        if filters.categories:
            stmt = stmt.where(
                Tool.categories.any(Category.slug.in_(filters.categories))
            )
        for kind, values in (
            (TagKind.TECHNOLOGY, filters.technologies),
            (TagKind.FEATURE, filters.features),
            (TagKind.PLATFORM, filters.platforms),
            (TagKind.INTEGRATION, filters.integrations),
        ):
            if values:
                stmt = stmt.where(
                    Tool.tags.any(and_(Tag.kind == kind, Tag.slug.in_(values)))
                )
        if filters.pricing:
            stmt = stmt.where(Tool.pricing_status.in_(filters.pricing))
        if filters.free_only:
            stmt = stmt.where(Tool.pricing_status.in_(FREE_PRICING_STATUSES))
        for column, value in (
            (Tool.is_open_source, filters.open_source),
            (Tool.has_api, filters.has_api),
            (Tool.has_free_api, filters.has_free_api),
            (Tool.has_mcp, filters.has_mcp),
            (Tool.has_agent, filters.has_agent),
            (Tool.has_local_model, filters.has_local_model),
            (Tool.featured, filters.featured),
        ):
            if value is not None:
                stmt = stmt.where(column.is_(value))
        return stmt

    @staticmethod
    def _freeness_rank():
        return case(PRICING_FREENESS_RANK, value=Tool.pricing_status, else_=0)

    def _apply_sort(self, stmt: Select, sort: str, score=None) -> Select:
        if sort == "relevance" and score is not None:
            return stmt.order_by(
                score.desc(), Tool.featured.desc(), Tool.name.asc()
            )
        if sort == "newest":
            return stmt.order_by(Tool.created_at.desc(), Tool.id.desc())
        if sort == "name":
            return stmt.order_by(func.lower(Tool.name).asc())
        if sort == "most_free":
            return stmt.order_by(
                self._freeness_rank().desc(), Tool.featured.desc(), Tool.name.asc()
            )
        if sort == "verified":
            return stmt.order_by(
                Tool.last_verified_at.desc().nullslast(), Tool.name.asc()
            )
        return stmt.order_by(
            Tool.featured.desc(), self._freeness_rank().desc(), Tool.name.asc()
        )

    # ---------------------------------------------------------------- search

    def _postgres_score(self, tokens: Sequence[str]):
        query = " ".join(tokens)
        tsquery = func.plainto_tsquery(literal("english"), literal(query))
        tsvector = func.to_tsvector(literal("english"), Tool.search_text)
        return func.ts_rank(tsvector, tsquery) * 10, tsvector.op("@@")(tsquery)

    def _like_score(self, tokens: Sequence[str]):
        """Portable scorer: weighted token hits across name/tagline/document."""
        score = literal(0)
        conditions = []
        for token in tokens:
            pattern = f"%{token}%"
            name_hit = Tool.name.ilike(pattern)
            tagline_hit = Tool.tagline.ilike(pattern)
            doc_hit = Tool.search_text.ilike(pattern)
            score = (
                score
                + case((name_hit, _NAME_WEIGHT), else_=0)
                + case((tagline_hit, _TAGLINE_WEIGHT), else_=0)
                + case((doc_hit, _DOCUMENT_WEIGHT), else_=0)
            )
            conditions.append(doc_hit)
        return score, or_(*conditions) if conditions else literal(True)

    def build_search(
        self, filters: ToolFilters, tokens: Sequence[str]
    ) -> tuple[Select, Any, str]:
        """Return (statement, score expression, engine name)."""
        stmt = self._active()
        engine = "portable_like"
        score = None

        if tokens:
            if self.is_postgres:
                pg_score, pg_match = self._postgres_score(tokens)
                like_score, like_match = self._like_score(tokens)
                # FTS handles stemming; LIKE catches partial identifiers such as
                # "postgres" inside "PostgreSQL".
                score = pg_score + like_score
                stmt = stmt.where(or_(pg_match, like_match))
                engine = "postgres_fts"
            else:
                score, match = self._like_score(tokens)
                stmt = stmt.where(match)

        stmt = self._apply_filters(stmt, filters)
        return stmt, score, engine

    # ----------------------------------------------------------------- reads

    async def count(self, stmt: Select) -> int:
        subquery = stmt.with_only_columns(Tool.id).order_by(None).subquery()
        result = await self.session.execute(
            select(func.count()).select_from(subquery)
        )
        return int(result.scalar_one())

    async def paginate(
        self, stmt: Select, params: PageParams, sort: str, score=None
    ) -> tuple[list[Tool], int]:
        total = await self.count(stmt)
        ordered = self._apply_sort(stmt, sort, score)
        ordered = self._eager(ordered).offset(params.offset).limit(params.limit)
        result = await self.session.execute(ordered)
        return list(result.scalars().unique().all()), total

    async def list_tools(
        self, filters: ToolFilters, params: PageParams
    ) -> tuple[list[Tool], int]:
        stmt = self._apply_filters(self._active(), filters)
        return await self.paginate(stmt, params, filters.sort)

    async def get_by_slug(self, slug: str) -> Tool | None:
        stmt = self._eager(select(Tool).where(Tool.slug == slug))
        result = await self.session.execute(stmt)
        return result.scalars().unique().one_or_none()

    async def suggest(self, query: str, *, limit: int = 8) -> list[Tool]:
        """Prefix/substring matches for search typeahead."""
        pattern = f"%{query.strip()}%"
        score = (
            case((Tool.name.ilike(f"{query.strip()}%"), 30), else_=0)
            + case((Tool.name.ilike(pattern), 20), else_=0)
            + case((Tool.tagline.ilike(pattern), 10), else_=0)
            + case((Tool.search_text.ilike(pattern), 5), else_=0)
        )
        stmt = (
            self._eager(self._active())
            .where(
                or_(
                    Tool.name.ilike(pattern),
                    Tool.tagline.ilike(pattern),
                    Tool.search_text.ilike(pattern),
                )
            )
            .order_by(score.desc(), Tool.featured.desc(), Tool.name.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_id(self, tool_id: int) -> Tool | None:
        stmt = self._eager(select(Tool).where(Tool.id == tool_id))
        result = await self.session.execute(stmt)
        return result.scalars().unique().one_or_none()

    async def get_many_by_slugs(self, slugs: Sequence[str]) -> list[Tool]:
        if not slugs:
            return []
        stmt = self._eager(select(Tool).where(Tool.slug.in_(list(slugs))))
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_many_by_ids(self, ids: Sequence[int]) -> list[Tool]:
        if not ids:
            return []
        stmt = self._eager(select(Tool).where(Tool.id.in_(list(ids))))
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def all_active(self, limit: int | None = None) -> list[Tool]:
        """Full candidate set for in-process scoring (recommendations)."""
        stmt = self._eager(self._active())
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def featured(self, limit: int = 8) -> list[Tool]:
        stmt = (
            self._eager(self._active().where(Tool.featured.is_(True)))
            .order_by(self._freeness_rank().desc(), Tool.name.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def featured_free(self, limit: int = 8) -> list[Tool]:
        stmt = (
            self._eager(
                self._active().where(
                    Tool.pricing_status.in_(FREE_PRICING_STATUSES)
                )
            )
            .order_by(
                Tool.featured.desc(),
                self._freeness_rank().desc(),
                Tool.name.asc(),
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def recently_added(self, limit: int = 8) -> list[Tool]:
        stmt = (
            self._eager(self._active())
            .order_by(Tool.created_at.desc(), Tool.id.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def by_pricing_status(
        self, statuses: Sequence[str], limit: int = 12, category: str | None = None
    ) -> list[Tool]:
        stmt = self._active().where(Tool.pricing_status.in_(list(statuses)))
        if category:
            stmt = stmt.where(Tool.categories.any(Category.slug == category))
        stmt = (
            self._eager(stmt)
            .order_by(Tool.featured.desc(), Tool.name.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def free_api_tools(
        self, limit: int = 12, category: str | None = None
    ) -> list[Tool]:
        stmt = self._active().where(Tool.has_free_api.is_(True))
        if category:
            stmt = stmt.where(Tool.categories.any(Category.slug == category))
        stmt = (
            self._eager(stmt)
            .order_by(Tool.featured.desc(), Tool.name.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def alternatives(self, tool: Tool, limit: int = 6) -> list[Tool]:
        """Tools sharing categories, ranked by category then feature overlap."""
        category_ids = [category.id for category in tool.categories]
        if not category_ids:
            return []
        feature_ids = [tag.id for tag in tool.tags if tag.kind == TagKind.FEATURE]

        stmt = (
            self._eager(self._active())
            .where(Tool.id != tool.id)
            .where(Tool.categories.any(Category.id.in_(category_ids)))
        )
        result = await self.session.execute(stmt)
        candidates = list(result.scalars().unique().all())

        def overlap(candidate: Tool) -> tuple[int, int, int]:
            shared_categories = len(
                {c.id for c in candidate.categories} & set(category_ids)
            )
            shared_features = len(
                {t.id for t in candidate.tags if t.kind == TagKind.FEATURE}
                & set(feature_ids)
            )
            return (
                shared_categories,
                shared_features,
                PRICING_FREENESS_RANK.get(candidate.pricing_status, 0),
            )

        candidates.sort(key=lambda item: (overlap(item), item.featured), reverse=True)
        return candidates[:limit]

    # ---------------------------------------------------------------- facets

    async def pricing_facets(self, filters: ToolFilters) -> dict[str, int]:
        stmt = self._apply_filters(self._active(), filters)
        subquery = stmt.with_only_columns(
            Tool.id, Tool.pricing_status
        ).order_by(None).subquery()
        result = await self.session.execute(
            select(subquery.c.pricing_status, func.count()).group_by(
                subquery.c.pricing_status
            )
        )
        return {row[0]: int(row[1]) for row in result.all()}

    async def total_count(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Tool).where(Tool.is_active.is_(True))
        )
        return int(result.scalar_one())

    async def free_count(self) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Tool)
            .where(
                Tool.is_active.is_(True),
                Tool.pricing_status.in_(FREE_PRICING_STATUSES),
            )
        )
        return int(result.scalar_one())

    # --------------------------------------------------------------- writes

    async def add(self, tool: Tool) -> Tool:
        self.session.add(tool)
        await self.session.flush()
        return tool

    async def delete(self, tool: Tool) -> None:
        await self.session.delete(tool)
        await self.session.flush()
