from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.enums import TagKind
from app.schemas.common import ORMModel


class TagOut(ORMModel):
    id: int
    name: str
    slug: str
    kind: str


class TagWithCount(TagOut):
    tool_count: int = 0


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, max_length=140)
    kind: TagKind = TagKind.TECHNOLOGY
