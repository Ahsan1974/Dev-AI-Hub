"""Aggregates the homepage and the free-tools landing page."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PricingStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.collection_repository import CollectionRepository
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.tool_repository import ToolRepository
from app.schemas.category import CategoryWithCount
from app.schemas.collection import CollectionOut
from app.schemas.home import (
    FreeToolsResponse,
    HomeResponse,
    PlatformStats,
    ToolSection,
)
from app.schemas.tool import ToolSummary
from app.services.category_service import CategoryService
from app.services.workflows import POPULAR_SEARCHES, WORKFLOWS

FREE_SECTIONS: list[dict[str, str]] = [
    {
        "slug": "completely-free",
        "title": "Completely free",
        "description": "No paid plan required. The free offering does not expire.",
    },
    {
        "slug": "open-source",
        "title": "Open source",
        "description": (
            "Source available and self-hostable. Model, hosting or API costs may "
            "still apply."
        ),
    },
    {
        "slug": "generous-free-tiers",
        "title": "Generous free tiers",
        "description": "A recurring free tier you can use indefinitely within limits.",
    },
    {
        "slug": "free-credits",
        "title": "Free credits",
        "description": "A limited allowance of credits to try the product.",
    },
    {
        "slug": "free-developer-apis",
        "title": "Free developer APIs",
        "description": "Programmatic access available on a free plan.",
    },
]


class HomeService:
    def __init__(self, session: AsyncSession) -> None:
        self.tools = ToolRepository(session)
        self.categories = CategoryRepository(session)
        self.collections = CollectionRepository(session)
        self.favorites = FavoriteRepository(session)
        self.category_service = CategoryService(session)

    async def home(self) -> HomeResponse:
        featured_free = await self.tools.featured_free(limit=8)
        recently_added = await self.tools.recently_added(limit=8)
        categories = await self.category_service.list_categories()
        popular = sorted(categories, key=lambda c: -c.tool_count)[:12]

        favorite_counts = await self.favorites.counts_by_tool()
        favorite_tools: list[ToolSummary] = []
        if favorite_counts:
            ranked = sorted(
                favorite_counts.items(), key=lambda item: item[1], reverse=True
            )[:8]
            models = await self.tools.get_many_by_ids([tool_id for tool_id, _ in ranked])
            order = {tool_id: index for index, (tool_id, _) in enumerate(ranked)}
            models.sort(key=lambda tool: order.get(tool.id, 999))
            favorite_tools = [ToolSummary.from_model(tool) for tool in models]

        collections = await self.collections.list_all(featured_only=True)
        total = await self.tools.total_count()
        free_total = await self.tools.free_count()
        verified = [tool for tool in await self.tools.all_active() if tool.last_verified_at]

        return HomeResponse(
            stats=PlatformStats(
                tools=total,
                free_tools=free_total,
                categories=len(categories),
                collections=len(await self.collections.list_all()),
                verified_tools=len(verified),
            ),
            featured_free=[ToolSummary.from_model(tool) for tool in featured_free],
            popular_categories=popular,
            recently_added=[ToolSummary.from_model(tool) for tool in recently_added],
            developer_favorites=favorite_tools,
            favorites_available=bool(favorite_tools),
            workflows=WORKFLOWS,
            collections=[
                CollectionOut(
                    id=collection.id,
                    name=collection.name,
                    slug=collection.slug,
                    description=collection.description,
                    icon=collection.icon,
                    is_featured=collection.is_featured,
                    tool_count=len(collection.tools),
                )
                for collection in collections
            ],
            popular_searches=POPULAR_SEARCHES,
        )

    async def free_tools(
        self, category: str | None = None, limit: int = 12
    ) -> FreeToolsResponse:
        sections: list[ToolSection] = []
        section_sources = {
            "completely-free": lambda: self.tools.by_pricing_status(
                [PricingStatus.FREE_FOREVER], limit, category
            ),
            "open-source": lambda: self.tools.by_pricing_status(
                [PricingStatus.OPEN_SOURCE], limit, category
            ),
            "generous-free-tiers": lambda: self.tools.by_pricing_status(
                [PricingStatus.FREE_TIER], limit, category
            ),
            "free-credits": lambda: self.tools.by_pricing_status(
                [PricingStatus.FREE_CREDITS, PricingStatus.BYOK], limit, category
            ),
            "free-developer-apis": lambda: self.tools.free_api_tools(limit, category),
        }

        for definition in FREE_SECTIONS:
            tools = await section_sources[definition["slug"]]()
            sections.append(
                ToolSection(
                    slug=definition["slug"],
                    title=definition["title"],
                    description=definition["description"],
                    tools=[ToolSummary.from_model(tool) for tool in tools],
                    total=len(tools),
                )
            )

        all_categories = await self.category_service.list_categories()
        with_free: list[CategoryWithCount] = [
            item for item in all_categories if item.free_tool_count > 0
        ]
        return FreeToolsResponse(
            sections=sections,
            categories=sorted(with_free, key=lambda c: -c.free_tool_count),
            active_category=category,
            total_free_tools=await self.tools.free_count(),
        )
