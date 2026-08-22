from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.category import CategoryWithCount
from app.schemas.collection import CollectionOut
from app.schemas.tool import ToolSummary
from app.services.workflows import Workflow


class PlatformStats(BaseModel):
    tools: int
    free_tools: int
    categories: int
    collections: int
    verified_tools: int


class ToolSection(BaseModel):
    slug: str
    title: str
    description: str
    tools: list[ToolSummary] = Field(default_factory=list)
    total: int = 0


class HomeResponse(BaseModel):
    stats: PlatformStats
    featured_free: list[ToolSummary]
    popular_categories: list[CategoryWithCount]
    recently_added: list[ToolSummary]
    #: Empty until real people save tools - the UI hides the section instead of
    #: inventing popularity numbers.
    developer_favorites: list[ToolSummary]
    favorites_available: bool
    workflows: list[Workflow]
    collections: list[CollectionOut]
    popular_searches: list[str]


class FreeToolsResponse(BaseModel):
    sections: list[ToolSection]
    categories: list[CategoryWithCount]
    active_category: str | None = None
    total_free_tools: int = 0
