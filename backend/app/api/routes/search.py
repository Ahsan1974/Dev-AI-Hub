from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import SearchServiceDep
from app.core.pagination import DataResponse, PageParams, page_params
from app.core.security import rate_limit
from app.schemas.search import (
    FilterOptions,
    SearchResponse,
    SuggestResponse,
    ToolFilters,
    tool_filters,
)

router = APIRouter(tags=["search"])


@router.get(
    "/search",
    response_model=SearchResponse,
    dependencies=[Depends(rate_limit)],
    summary="Search tools",
    description=(
        "Full-text search across names, descriptions, categories, features, "
        "technologies, free-access text and best-for statements. Uses PostgreSQL "
        "full-text search when available and a portable scorer otherwise."
    ),
)
async def search(
    service: SearchServiceDep,
    filters: Annotated[ToolFilters, Depends(tool_filters)],
    params: Annotated[PageParams, Depends(page_params)],
) -> SearchResponse:
    return await service.search(filters, params)


@router.get(
    "/filters",
    response_model=DataResponse[FilterOptions],
    summary="Filter sidebar options",
    description="Every facet with its live tool count, in one request.",
)
async def filter_options(service: SearchServiceDep) -> DataResponse[FilterOptions]:
    return DataResponse(data=await service.filter_options())


@router.get(
    "/search/suggest",
    response_model=SuggestResponse,
    dependencies=[Depends(rate_limit)],
    summary="Search typeahead suggestions",
    description=(
        "Returns tool, category and query suggestions while typing. "
        "Example: q=UML suggests PlantUML, draw.io, Mermaid and diagram categories."
    ),
)
async def suggest(
    service: SearchServiceDep,
    q: str = "",
    limit: int = 8,
) -> SuggestResponse:
    return await service.suggest(q, limit=min(max(limit, 1), 20))
