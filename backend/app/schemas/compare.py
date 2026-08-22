from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.tool import ToolDetail

MAX_COMPARE_TOOLS = 4

CellKind = Literal["bool", "text", "list", "price", "unknown"]


class CompareRequest(BaseModel):
    slugs: list[str] = Field(min_length=2, max_length=MAX_COMPARE_TOOLS)

    @field_validator("slugs")
    @classmethod
    def _unique(cls, value: list[str]) -> list[str]:
        seen: list[str] = []
        for slug in value:
            slug = slug.strip().lower()
            if slug and slug not in seen:
                seen.append(slug)
        if len(seen) < 2:
            raise ValueError("Provide at least two distinct tools to compare.")
        return seen


class CompareCell(BaseModel):
    kind: CellKind = "text"
    value: bool | str | list[str] | None = None
    #: Present when the answer is genuinely unknown rather than negative.
    note: str | None = None


class CompareRow(BaseModel):
    key: str
    label: str
    group: str
    cells: list[CompareCell]


class CompareResponse(BaseModel):
    tools: list[ToolDetail]
    rows: list[CompareRow]
    missing_slugs: list[str] = Field(default_factory=list)
