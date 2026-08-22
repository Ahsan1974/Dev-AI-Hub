"""Idempotent database seeding from the JSON dataset in ``app/seed/data``.

Running it twice updates existing rows instead of duplicating them, so the
dataset can be edited and re-applied during development.

Data honesty rules enforced here:

* ``last_verified_at`` is only set for entries explicitly marked ``verified``,
  which means the pricing numbers were taken from the provider's own pricing
  page when the dataset was compiled. Everything else stays unverified and the
  UI says so rather than implying a checked date.
* No entry may claim a price without ``verification_source_url``.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TagKind
from app.db.init_db import create_all
from app.db.session import SessionFactory, engine
from app.models.category import Category
from app.models.collection import Collection
from app.models.free_access import FreeAccessGrant
from app.models.pricing import PricingPlan
from app.models.tag import Tag
from app.models.tool import Tool
from app.services.tool_service import build_search_text
from app.utils.text import slugify

logger = logging.getLogger("devai_hub.seed")

DATA_DIR = Path(__file__).parent / "data"

#: When this dataset was assembled from public provider pricing pages. Used as
#: ``last_verified_at`` for verified entries so staleness is measurable.
DATASET_COMPILED_AT = datetime(2026, 8, 22, tzinfo=timezone.utc)

VERIFICATION_NOTE = (
    "Compiled for the DevAI Hub seed dataset from the provider's official "
    "pricing page. AI pricing changes frequently - re-check the source before "
    "relying on it."
)

_TAG_FIELDS: tuple[tuple[str, str], ...] = (
    ("technologies", TagKind.TECHNOLOGY),
    ("features", TagKind.FEATURE),
    ("platforms", TagKind.PLATFORM),
    ("integrations", TagKind.INTEGRATION),
)

_FLAGS = (
    "is_open_source",
    "has_api",
    "has_free_api",
    "has_mcp",
    "has_agent",
    "has_local_model",
    "self_hostable",
)


@dataclass
class SeedReport:
    categories: int = 0
    tags: int = 0
    tools_created: int = 0
    tools_updated: int = 0
    collections: int = 0
    free_tools: int = 0
    verified_tools: int = 0

    def render(self) -> str:
        return (
            f"categories={self.categories} tags={self.tags} "
            f"tools_created={self.tools_created} tools_updated={self.tools_updated} "
            f"collections={self.collections} free_tools={self.free_tools} "
            f"verified_tools={self.verified_tools}"
        )


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_tool_data() -> list[dict]:
    tools: list[dict] = []
    for path in sorted((DATA_DIR / "tools").glob("*.json")):
        tools.extend(_load(path))
    return tools


class Seeder:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.report = SeedReport()
        self._categories: dict[str, Category] = {}
        self._tags: dict[tuple[str, str], Tag] = {}

    # ------------------------------------------------------------ taxonomy

    async def seed_categories(self) -> None:
        existing = {
            category.slug: category
            for category in (await self.session.execute(select(Category)))
            .scalars()
            .all()
        }
        for payload in _load(DATA_DIR / "categories.json"):
            slug = payload.get("slug") or slugify(payload["name"])
            category = existing.get(slug)
            if category is None:
                category = Category(slug=slug)
                self.session.add(category)
            category.name = payload["name"]
            category.description = payload.get("description")
            category.group = payload.get("group", "General")
            category.icon = payload.get("icon")
            category.sort_order = payload.get("sort_order", 100)
            self._categories[slug] = category
            self.report.categories += 1
        await self.session.flush()

    async def _tag(self, name: str, kind: str) -> Tag:
        slug = slugify(name)
        key = (kind, slug)
        if key in self._tags:
            return self._tags[key]
        result = await self.session.execute(
            select(Tag).where(Tag.kind == kind, Tag.slug == slug)
        )
        tag = result.scalars().one_or_none()
        if tag is None:
            tag = Tag(name=name, slug=slug, kind=kind)
            self.session.add(tag)
            await self.session.flush()
            self.report.tags += 1
        self._tags[key] = tag
        return tag

    # --------------------------------------------------------------- tools

    def _validate(self, payload: dict) -> None:
        name = payload.get("name", "<unnamed>")
        if not payload.get("website_url"):
            raise ValueError(f"{name}: website_url is required")
        priced = [
            plan
            for plan in payload.get("pricing_plans", [])
            if plan.get("price") not in (None, 0)
        ]
        if priced and not payload.get("verification_source_url"):
            raise ValueError(
                f"{name}: pricing figures require a verification_source_url"
            )

    async def _apply_tool(self, payload: dict) -> Tool:
        self._validate(payload)
        slug = payload.get("slug") or slugify(payload["name"])
        result = await self.session.execute(select(Tool).where(Tool.slug == slug))
        tool = result.scalars().one_or_none()
        if tool is None:
            # Collections are initialised up front: once the instance is
            # flushed, assigning an unloaded collection would trigger a lazy
            # load, which is not allowed inside async SQLAlchemy.
            tool = Tool(
                slug=slug,
                name=payload["name"],
                website_url=payload["website_url"],
                categories=[],
                tags=[],
                pricing_plans=[],
                free_access_grants=[],
            )
            self.session.add(tool)
            self.report.tools_created += 1
        else:
            self.report.tools_updated += 1

        tool.name = payload["name"]
        tool.tagline = payload.get("tagline", "")
        tool.description = payload.get("description", "")
        tool.long_description = payload.get("long_description")
        tool.website_url = payload["website_url"]
        tool.pricing_url = payload.get("pricing_url")
        tool.docs_url = payload.get("docs_url")
        tool.repo_url = payload.get("repo_url")
        tool.logo_url = payload.get("logo_url")
        tool.pricing_status = payload["pricing_status"]
        tool.free_access_summary = payload.get("free_access_summary")
        tool.pricing_summary = payload.get("pricing_summary")
        tool.best_for = payload.get("best_for", [])
        tool.not_ideal_for = payload.get("not_ideal_for", [])
        tool.capabilities = payload.get("capabilities", [])
        tool.featured = payload.get("featured", False)
        tool.is_active = payload.get("is_active", True)

        flags = payload.get("flags", {})
        for flag in _FLAGS:
            setattr(tool, flag, bool(flags.get(flag, False)))

        if payload.get("verified"):
            tool.last_verified_at = DATASET_COMPILED_AT
            tool.verification_source_url = payload.get(
                "verification_source_url"
            ) or payload.get("pricing_url")
            tool.verification_note = VERIFICATION_NOTE
            self.report.verified_tools += 1
        else:
            tool.last_verified_at = None
            tool.verification_source_url = payload.get("pricing_url")
            tool.verification_note = (
                "Not verified against the provider's pricing page yet. Free-access "
                "descriptions are qualitative on purpose."
            )

        tool.categories = [
            self._categories[slug_]
            for slug_ in payload.get("categories", [])
            if slug_ in self._categories
        ]
        unknown = set(payload.get("categories", [])) - set(self._categories)
        if unknown:
            raise ValueError(f"{tool.name}: unknown categories {sorted(unknown)}")

        tags: list[Tag] = []
        for field, kind in _TAG_FIELDS:
            for name in payload.get(field, []):
                tags.append(await self._tag(name, kind))
        tool.tags = tags

        tool.pricing_plans = [
            PricingPlan(
                name=plan["name"],
                price=plan.get("price"),
                currency=plan.get("currency", "USD"),
                billing_period=plan.get("billing_period", "month"),
                is_free=plan.get("is_free", plan.get("price") == 0),
                is_trial=plan.get("is_trial", False),
                is_per_seat=plan.get("is_per_seat", False),
                description=plan.get("description"),
                features=plan.get("features", []),
                sort_order=index,
            )
            for index, plan in enumerate(payload.get("pricing_plans", []))
        ]
        tool.free_access_grants = [
            FreeAccessGrant(
                type=grant.get("type", "UNKNOWN"),
                amount=grant.get("amount"),
                unit=grant.get("unit"),
                period=grant.get("period"),
                description=grant.get("description"),
                restrictions=grant.get("restrictions", []),
                requires_credit_card=grant.get("requires_credit_card"),
                expires=grant.get("expires"),
                expires_after_days=grant.get("expires_after_days"),
                sort_order=index,
            )
            for index, grant in enumerate(payload.get("free_access", []))
        ]

        await self.session.flush()
        tool.search_text = build_search_text(tool)
        return tool

    async def seed_tools(self) -> dict[str, Tool]:
        tools: dict[str, Tool] = {}
        for payload in load_tool_data():
            tool = await self._apply_tool(payload)
            tools[tool.slug] = tool
        await self.session.flush()
        return tools

    # --------------------------------------------------------- collections

    async def seed_collections(self, tools: dict[str, Tool]) -> None:
        for payload in _load(DATA_DIR / "collections.json"):
            slug = payload.get("slug") or slugify(payload["name"])
            result = await self.session.execute(
                select(Collection).where(Collection.slug == slug)
            )
            collection = result.scalars().one_or_none()
            if collection is None:
                collection = Collection(slug=slug, tools=[])
                self.session.add(collection)
            collection.name = payload["name"]
            collection.description = payload.get("description")
            collection.icon = payload.get("icon")
            collection.is_featured = payload.get("is_featured", False)
            collection.sort_order = payload.get("sort_order", 100)

            missing = [slug_ for slug_ in payload["tools"] if slug_ not in tools]
            if missing:
                raise ValueError(f"Collection {slug} references unknown tools: {missing}")
            collection.tools = [tools[slug_] for slug_ in payload["tools"]]
            self.report.collections += 1
        await self.session.flush()

    async def run(self) -> SeedReport:
        await self.seed_categories()
        tools = await self.seed_tools()
        await self.seed_collections(tools)
        from app.core.enums import FREE_PRICING_STATUSES

        self.report.free_tools = sum(
            1 for tool in tools.values() if tool.pricing_status in FREE_PRICING_STATUSES
        )
        await self.session.commit()
        return self.report


async def seed(session: AsyncSession | None = None) -> SeedReport:
    if session is not None:
        return await Seeder(session).run()
    async with SessionFactory() as owned:
        return await Seeder(owned).run()


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    await create_all(engine)
    report = await seed()
    logger.info("Seed complete: %s", report.render())
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
