from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Literal

from fastapi import Query
from pydantic import BaseModel, Field

from app.core.enums import PricingStatus
from app.schemas.category import CategoryWithCount
from app.schemas.tag import TagWithCount
from app.schemas.tool import ToolSummary

SortOption = Literal[
    "relevance", "newest", "name", "most_free", "featured", "verified"
]


@dataclass(slots=True)
class ToolFilters:
    """Normalised filter set shared by browse, search and free-tools."""

    q: str | None = None
    categories: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    integrations: list[str] = field(default_factory=list)
    pricing: list[str] = field(default_factory=list)
    free_only: bool = False
    open_source: bool | None = None
    has_api: bool | None = None
    has_free_api: bool | None = None
    has_mcp: bool | None = None
    has_agent: bool | None = None
    has_local_model: bool | None = None
    featured: bool | None = None
    sort: SortOption = "featured"

    @property
    def has_query(self) -> bool:
        return bool(self.q and self.q.strip())


ListParam = Annotated[list[str] | None, Query()]


def tool_filters(
    q: str | None = Query(None, description="Free text query."),
    category: ListParam = None,
    technology: ListParam = None,
    feature: ListParam = None,
    platform: ListParam = None,
    integration: ListParam = None,
    pricing: Annotated[list[PricingStatus] | None, Query()] = None,
    free_only: bool = Query(False, description="Only tools with real free access."),
    open_source: bool | None = None,
    has_api: bool | None = None,
    has_free_api: bool | None = None,
    has_mcp: bool | None = None,
    has_agent: bool | None = None,
    has_local_model: bool | None = None,
    featured: bool | None = None,
    sort: SortOption = "featured",
) -> ToolFilters:
    return ToolFilters(
        q=q,
        categories=list(category or []),
        technologies=list(technology or []),
        features=list(feature or []),
        platforms=list(platform or []),
        integrations=list(integration or []),
        pricing=[str(item) for item in (pricing or [])],
        free_only=free_only,
        open_source=open_source,
        has_api=has_api,
        has_free_api=has_free_api,
        has_mcp=has_mcp,
        has_agent=has_agent,
        has_local_model=has_local_model,
        featured=featured,
        sort=sort,
    )


class FacetValue(BaseModel):
    value: str
    label: str
    count: int


class SearchFacets(BaseModel):
    pricing: list[FacetValue] = Field(default_factory=list)
    categories: list[FacetValue] = Field(default_factory=list)
    technologies: list[FacetValue] = Field(default_factory=list)
    features: list[FacetValue] = Field(default_factory=list)
    platforms: list[FacetValue] = Field(default_factory=list)


class SearchMeta(BaseModel):
    query: str | None = None
    interpreted_keywords: list[str] = Field(default_factory=list)
    detected_free_intent: bool = False
    engine: Literal["postgres_fts", "portable_like"] = "portable_like"
    took_ms: int = 0
    suggestions: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    data: list[ToolSummary]
    pagination: dict
    meta: SearchMeta
    facets: SearchFacets | None = None


class FilterOptions(BaseModel):
    """Everything the filter sidebar needs, in one request."""

    pricing: list[FacetValue]
    categories: list[CategoryWithCount]
    technologies: list[TagWithCount]
    features: list[TagWithCount]
    platforms: list[TagWithCount]
    integrations: list[TagWithCount]
    sorts: list[FacetValue]


class SuggestItem(BaseModel):
    """One typeahead row shown while the user is typing a search."""

    type: Literal["tool", "category", "query"]
    label: str
    subtitle: str | None = None
    slug: str | None = None
    query: str | None = None


class SuggestResponse(BaseModel):
    data: list[SuggestItem]
