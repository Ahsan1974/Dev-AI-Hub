"""Tool reads and admin writes."""

from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TagKind
from app.core.errors import ConflictError, ToolNotFoundError, ValidationError
from app.core.pagination import Page, PageParams
from app.models.category import Category
from app.models.free_access import FreeAccessGrant
from app.models.pricing import PricingPlan
from app.models.tag import Tag
from app.models.tool import Tool
from app.repositories.category_repository import CategoryRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.tool_repository import ToolRepository
from app.schemas.pricing import ToolPricingResponse
from app.schemas.search import ToolFilters
from app.schemas.tool import ToolDetail, ToolPatch, ToolSummary, ToolWrite
from app.utils import presentation
from app.utils.text import slugify

_TAG_FIELDS: tuple[tuple[str, str], ...] = (
    ("technologies", TagKind.TECHNOLOGY),
    ("features", TagKind.FEATURE),
    ("platforms", TagKind.PLATFORM),
    ("integrations", TagKind.INTEGRATION),
)


def build_search_text(tool: Tool) -> str:
    """Denormalised haystack backing both search engines."""
    parts: list[str] = [
        tool.name,
        tool.tagline or "",
        tool.description or "",
        tool.long_description or "",
        tool.free_access_summary or "",
        tool.pricing_summary or "",
        tool.pricing_status.replace("_", " "),
        *(tool.best_for or []),
        *(tool.capabilities or []),
        *(category.name for category in tool.categories),
        *(tag.name for tag in tool.tags),
        *(grant.description or "" for grant in tool.free_access_grants),
        *(plan.name for plan in tool.pricing_plans),
    ]
    if tool.is_open_source:
        parts.append("open source self hosted")
    if tool.has_free_api:
        parts.append("free api")
    if tool.has_mcp:
        parts.append("mcp model context protocol")
    if tool.has_agent:
        parts.append("agent autonomous")
    if tool.has_local_model:
        parts.append("local offline model")
    return " \n".join(part for part in parts if part).lower()


class ToolService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ToolRepository(session)
        self.categories = CategoryRepository(session)
        self.tags = TagRepository(session)

    # ------------------------------------------------------------------ read

    async def list_tools(
        self, filters: ToolFilters, params: PageParams
    ) -> Page[ToolSummary]:
        tools, total = await self.repo.list_tools(filters, params)
        return Page.build(
            [ToolSummary.from_model(tool) for tool in tools], params, total
        )

    async def get_detail(self, slug: str) -> ToolDetail:
        tool = await self.repo.get_by_slug(slug)
        if tool is None or not tool.is_active:
            raise ToolNotFoundError(f"No tool exists with the slug '{slug}'.")
        return ToolDetail.from_model(tool)

    async def get_model_or_404(self, identifier: str | int) -> Tool:
        tool = (
            await self.repo.get_by_id(int(identifier))
            if str(identifier).isdigit()
            else await self.repo.get_by_slug(str(identifier))
        )
        if tool is None:
            raise ToolNotFoundError(f"No tool exists with the id '{identifier}'.")
        return tool

    async def alternatives(self, identifier: str | int, limit: int = 6) -> list[ToolSummary]:
        tool = await self.get_model_or_404(identifier)
        alternatives = await self.repo.alternatives(tool, limit)
        return [ToolSummary.from_model(item) for item in alternatives]

    async def pricing(self, identifier: str | int) -> ToolPricingResponse:
        tool = await self.get_model_or_404(identifier)
        has_plans = bool(tool.pricing_plans)
        return ToolPricingResponse(
            tool_slug=tool.slug,
            pricing_status=tool.pricing_status,
            pricing_summary=tool.pricing_summary
            or (None if has_plans else presentation.PRICING_UNAVAILABLE),
            plans=tool.pricing_plans,  # type: ignore[arg-type]
            pricing_url=tool.pricing_url or tool.website_url,
            last_verified_at=(
                tool.last_verified_at.isoformat() if tool.last_verified_at else None
            ),
            verification_source_url=tool.verification_source_url,
            disclaimer=(
                "AI pricing changes often. Always confirm on the provider's "
                "official pricing page before purchasing."
            ),
        )

    async def resolve_many(self, slugs: Iterable[str]) -> list[ToolSummary]:
        """Hydrate a client-side list (favourites, recently viewed) in one call."""
        requested = [slug for slug in slugs if slug]
        tools = await self.repo.get_many_by_slugs(requested)
        order = {slug: index for index, slug in enumerate(requested)}
        tools.sort(key=lambda tool: order.get(tool.slug, 10_000))
        return [ToolSummary.from_model(tool) for tool in tools]

    # ----------------------------------------------------------------- write

    async def _resolve_categories(self, slugs: list[str]) -> list[Category]:
        if not slugs:
            return []
        found = await self.categories.get_many_by_slugs(slugs)
        missing = set(slugs) - {category.slug for category in found}
        if missing:
            raise ValidationError(
                "Unknown category slugs: " + ", ".join(sorted(missing)),
                code="UNKNOWN_CATEGORY",
            )
        return found

    async def _resolve_tags(self, names: list[str], kind: str) -> list[Tag]:
        resolved: list[Tag] = []
        for name in names:
            slug = slugify(name)
            tag = await self.tags.get(kind, slug)
            if tag is None:
                tag = await self.tags.add(Tag(name=name, slug=slug, kind=kind))
            resolved.append(tag)
        return resolved

    async def _apply_payload(self, tool: Tool, payload: dict[str, Any]) -> Tool:
        scalar_fields = {
            "name",
            "tagline",
            "description",
            "long_description",
            "pricing_status",
            "free_access_summary",
            "pricing_summary",
            "best_for",
            "not_ideal_for",
            "capabilities",
            "is_open_source",
            "has_api",
            "has_free_api",
            "has_mcp",
            "has_agent",
            "has_local_model",
            "self_hostable",
            "featured",
            "is_active",
            "last_verified_at",
            "verification_note",
        }
        url_fields = {
            "website_url",
            "pricing_url",
            "docs_url",
            "repo_url",
            "logo_url",
            "verification_source_url",
        }

        for field, value in payload.items():
            if field in scalar_fields:
                setattr(tool, field, value)
            elif field in url_fields:
                setattr(tool, field, str(value) if value is not None else None)

        if "categories" in payload:
            tool.categories = await self._resolve_categories(payload["categories"] or [])
        for field, kind in _TAG_FIELDS:
            if field in payload:
                keep = [tag for tag in tool.tags if tag.kind != kind]
                tool.tags = keep + await self._resolve_tags(payload[field] or [], kind)

        if "pricing_plans" in payload:
            tool.pricing_plans = [
                PricingPlan(
                    **{
                        **plan,
                        "price": plan.get("price"),
                        "billing_period": str(plan.get("billing_period", "month")),
                    }
                )
                for plan in payload["pricing_plans"] or []
            ]
        if "free_access" in payload:
            tool.free_access_grants = [
                FreeAccessGrant(**{**grant, "type": str(grant.get("type", "UNKNOWN"))})
                for grant in payload["free_access"] or []
            ]

        await self.session.flush()
        tool.search_text = build_search_text(tool)
        await self.session.flush()
        return tool

    async def create(self, payload: ToolWrite) -> ToolDetail:
        slug = payload.slug or slugify(payload.name)
        if await self.repo.get_by_slug(slug) is not None:
            raise ConflictError(f"A tool with the slug '{slug}' already exists.")

        # Collections are initialised here so that assigning them later, after
        # the instance has been flushed, does not trigger an async lazy load.
        tool = Tool(
            slug=slug,
            name=payload.name,
            website_url=str(payload.website_url),
            pricing_status=str(payload.pricing_status),
            categories=[],
            tags=[],
            pricing_plans=[],
            free_access_grants=[],
        )
        self.session.add(tool)
        data = payload.model_dump(exclude={"slug"})
        data["pricing_status"] = str(payload.pricing_status)
        await self._apply_payload(tool, data)
        await self.session.commit()
        refreshed = await self.repo.get_by_slug(slug)
        assert refreshed is not None
        return ToolDetail.from_model(refreshed)

    async def update(self, slug: str, patch: ToolPatch) -> ToolDetail:
        tool = await self.repo.get_by_slug(slug)
        if tool is None:
            raise ToolNotFoundError(f"No tool exists with the slug '{slug}'.")
        changes = patch.changes()
        if "pricing_status" in changes and changes["pricing_status"] is not None:
            changes["pricing_status"] = str(changes["pricing_status"])
        await self._apply_payload(tool, changes)
        await self.session.commit()
        refreshed = await self.repo.get_by_slug(slug)
        assert refreshed is not None
        return ToolDetail.from_model(refreshed)

    async def delete(self, slug: str) -> None:
        tool = await self.repo.get_by_slug(slug)
        if tool is None:
            raise ToolNotFoundError(f"No tool exists with the slug '{slug}'.")
        await self.repo.delete(tool)
        await self.session.commit()
