"""Pagination primitives shared by every list endpoint."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

from app.core.config import settings

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class PageParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def page_params(
    page: int = Query(1, ge=1, description="1-indexed page number."),
    page_size: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Items per page.",
    ),
) -> PageParams:
    return PageParams(page=page, page_size=page_size)


class PaginationMeta(BaseModel):
    page: int = Field(..., examples=[1])
    page_size: int = Field(..., examples=[24])
    total: int = Field(..., examples=[100])
    total_pages: int = Field(..., examples=[5])
    has_next: bool
    has_previous: bool

    @classmethod
    def build(cls, params: PageParams, total: int) -> "PaginationMeta":
        total_pages = ceil(total / params.page_size) if params.page_size else 0
        return cls(
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_previous=params.page > 1,
        )


class Page(BaseModel, Generic[T]):
    """Envelope used by every collection endpoint."""

    data: list[T]
    pagination: PaginationMeta

    @classmethod
    def build(cls, items: list[T], params: PageParams, total: int) -> "Page[T]":
        return cls(data=items, pagination=PaginationMeta.build(params, total))


class DataResponse(BaseModel, Generic[T]):
    """Envelope used by single-resource endpoints."""

    data: T
