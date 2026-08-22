from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CategoryOut(ORMModel):
    id: int
    name: str
    slug: str
    description: str | None = None
    group: str
    icon: str | None = None
    sort_order: int


class CategoryWithCount(CategoryOut):
    tool_count: int = 0
    free_tool_count: int = 0


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, max_length=140)
    description: str | None = None
    group: str = "General"
    icon: str | None = None
    sort_order: int = 100


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    group: str | None = None
    icon: str | None = None
    sort_order: int | None = None
