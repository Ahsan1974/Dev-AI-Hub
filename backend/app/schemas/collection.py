from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.tool import ToolSummary


class CollectionOut(ORMModel):
    id: int
    name: str
    slug: str
    description: str | None = None
    icon: str | None = None
    is_featured: bool = False
    tool_count: int = 0


class CollectionDetail(CollectionOut):
    tools: list[ToolSummary] = Field(default_factory=list)


class CollectionWrite(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    slug: str | None = Field(default=None, max_length=180)
    description: str | None = None
    icon: str | None = None
    is_featured: bool = False
    sort_order: int = 100
    tools: list[str] = Field(default_factory=list, description="Ordered tool slugs")
