"""Search orchestration: query understanding, retrieval, facets."""

from __future__ import annotations

import time
from dataclasses import replace

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import (
    PRICING_STATUS_LABELS,
    TagKind,
)
from app.core.pagination import PageParams, PaginationMeta
from app.repositories.category_repository import CategoryRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.tool_repository import ToolRepository
from app.schemas.category import CategoryWithCount
from app.schemas.search import (
    FacetValue,
    FilterOptions,
    SearchFacets,
    SearchMeta,
    SearchResponse,
    SuggestItem,
    SuggestResponse,
    ToolFilters,
)
from app.schemas.tag import TagWithCount
from app.schemas.tool import ToolSummary
from app.services.intent import TaxonomyIndex, extract_intent
from app.utils.text import FREE_INTENT_WORDS

SORT_LABELS = {
    "relevance": "Best match",
    "featured": "Recommended",
    "most_free": "Most free",
    "newest": "Recently added",
    "name": "Name (A-Z)",
    "verified": "Recently verified",
}


class SearchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tools = ToolRepository(session)
        self.categories = CategoryRepository(session)
        self.tags = TagRepository(session)

    async def _taxonomy(self) -> TaxonomyIndex:
        return TaxonomyIndex(
            await self.categories.list_all(), await self.tags.list_all()
        )

    async def search(
        self, filters: ToolFilters, params: PageParams, *, with_facets: bool = True
    ) -> SearchResponse:
        started = time.perf_counter()
        query = (filters.q or "").strip()

        tokens: list[str] = []
        interpreted: list[str] = []
        free_intent = False
        suggestions: list[str] = []

        if query:
            index = await self._taxonomy()
            intent = extract_intent(query, index)
            free_intent = intent.free_intent
            # "free" is an intent, not a search term - it never appears in the
            # tool text and would otherwise dilute ranking.
            tokens = [word for word in intent.keywords if word not in FREE_INTENT_WORDS]
            interpreted = tokens
            suggestions = [
                *(f"category:{slug}" for slug in intent.categories[:3]),
                *(f"tech:{slug}" for slug in intent.technologies[:3]),
            ]
            if filters.sort == "featured":
                filters = replace(filters, sort="relevance")
            if free_intent and not filters.pricing and not filters.free_only:
                filters = replace(filters, free_only=True)

        stmt, score, engine = self.tools.build_search(filters, tokens)
        tools, total = await self.tools.paginate(stmt, params, filters.sort, score)

        facets = None
        if with_facets:
            facets = SearchFacets(pricing=await self._pricing_facets(filters))

        meta = SearchMeta(
            query=query or None,
            interpreted_keywords=interpreted,
            detected_free_intent=free_intent,
            engine=engine,
            took_ms=int((time.perf_counter() - started) * 1000),
            suggestions=suggestions,
        )
        return SearchResponse(
            data=[ToolSummary.from_model(tool) for tool in tools],
            pagination=PaginationMeta.build(params, total).model_dump(),
            meta=meta,
            facets=facets,
        )

    async def _pricing_facets(self, filters: ToolFilters) -> list[FacetValue]:
        """Counts per pricing status, ignoring the pricing filter itself."""
        neutral = replace(filters, pricing=[], free_only=False, q=None)
        counts = await self.tools.pricing_facets(neutral)
        return [
            FacetValue(
                value=status,
                label=PRICING_STATUS_LABELS[status],
                count=counts.get(status, 0),
            )
            for status in PRICING_STATUS_LABELS
        ]

    async def filter_options(self) -> FilterOptions:
        categories = await self.categories.list_all()
        category_counts = await self.categories.counts()
        tags = await self.tags.list_all()
        tag_counts = await self.tags.counts()
        pricing_counts = await self.tools.pricing_facets(ToolFilters())

        def tags_of(kind: str) -> list[TagWithCount]:
            items = [
                TagWithCount(
                    id=tag.id,
                    name=tag.name,
                    slug=tag.slug,
                    kind=tag.kind,
                    tool_count=tag_counts.get(tag.id, 0),
                )
                for tag in tags
                if tag.kind == kind
            ]
            return sorted(items, key=lambda t: (-t.tool_count, t.name))

        return FilterOptions(
            pricing=[
                FacetValue(
                    value=status,
                    label=label,
                    count=pricing_counts.get(status, 0),
                )
                for status, label in PRICING_STATUS_LABELS.items()
            ],
            categories=[
                CategoryWithCount(
                    **{
                        key: getattr(category, key)
                        for key in (
                            "id",
                            "name",
                            "slug",
                            "description",
                            "group",
                            "icon",
                            "sort_order",
                        )
                    },
                    tool_count=category_counts.get(category.id, (0, 0))[0],
                    free_tool_count=category_counts.get(category.id, (0, 0))[1],
                )
                for category in categories
            ],
            technologies=tags_of(TagKind.TECHNOLOGY),
            features=tags_of(TagKind.FEATURE),
            platforms=tags_of(TagKind.PLATFORM),
            integrations=tags_of(TagKind.INTEGRATION),
            sorts=[
                FacetValue(value=value, label=label, count=0)
                for value, label in SORT_LABELS.items()
            ],
        )

    async def suggest(self, q: str, *, limit: int = 8) -> SuggestResponse:
        """Typeahead suggestions for the search box.

        Typing ``UML`` should surface PlantUML, draw.io, Mermaid and the
        Diagrams & UML category — not only exact name prefixes.
        """
        query = (q or "").strip()
        if len(query) < 1:
            return SuggestResponse(data=[])

        items: list[SuggestItem] = []
        seen_tools: set[str] = set()
        seen_categories: set[str] = set()

        # Direct tool matches first (name / tagline / search text).
        for tool in await self.tools.suggest(query, limit=limit):
            seen_tools.add(tool.slug)
            items.append(
                SuggestItem(
                    type="tool",
                    label=tool.name,
                    subtitle=tool.tagline or None,
                    slug=tool.slug,
                    query=tool.name,
                )
            )

        # Category name/slug matches.
        needle = query.lower()
        for category in await self.categories.list_all():
            if needle not in category.name.lower() and needle not in category.slug:
                continue
            if category.slug in seen_categories:
                continue
            seen_categories.add(category.slug)
            items.append(
                SuggestItem(
                    type="category",
                    label=category.name,
                    subtitle=category.group or "Category",
                    slug=category.slug,
                    query=category.name,
                )
            )

        # Intent expansion: "uml" → PlantUML / Mermaid style tools via taxonomy.
        index = await self._taxonomy()
        intent = extract_intent(query, index)
        related_tokens = list(
            dict.fromkeys(
                [
                    *intent.keywords,
                    *intent.categories,
                    *intent.features,
                    *intent.technologies,
                ]
            )
        )
        for token in related_tokens[:6]:
            if token.lower() == needle:
                continue
            for tool in await self.tools.suggest(token, limit=3):
                if tool.slug in seen_tools:
                    continue
                seen_tools.add(tool.slug)
                items.append(
                    SuggestItem(
                        type="tool",
                        label=tool.name,
                        subtitle=tool.tagline or f"Related to “{query}”",
                        slug=tool.slug,
                        query=tool.name,
                    )
                )
                if len([i for i in items if i.type == "tool"]) >= limit:
                    break
            if len([i for i in items if i.type == "tool"]) >= limit:
                break

            for category in await self.categories.list_all():
                if category.slug != token and token not in category.slug:
                    continue
                if category.slug in seen_categories:
                    continue
                seen_categories.add(category.slug)
                items.append(
                    SuggestItem(
                        type="category",
                        label=category.name,
                        subtitle=category.group or "Category",
                        slug=category.slug,
                        query=category.name,
                    )
                )

        # Always offer running the raw query itself.
        if query:
            items.append(
                SuggestItem(
                    type="query",
                    label=f"Search for “{query}”",
                    subtitle="Full search results",
                    query=query,
                )
            )

        # Keep the list short and stable: tools, then categories, then query.
        tools = [i for i in items if i.type == "tool"][:limit]
        categories = [i for i in items if i.type == "category"][:3]
        queries = [i for i in items if i.type == "query"][:1]
        return SuggestResponse(data=[*tools, *categories, *queries])
