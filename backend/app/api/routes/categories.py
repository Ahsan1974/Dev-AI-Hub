from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CategoryServiceDep
from app.core.pagination import DataResponse, Page, PageParams, page_params
from app.schemas.category import CategoryWithCount
from app.schemas.search import ToolFilters, tool_filters
from app.schemas.tool import ToolSummary

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "",
    response_model=DataResponse[list[CategoryWithCount]],
    summary="List categories with tool counts",
)
async def list_categories(
    service: CategoryServiceDep,
) -> DataResponse[list[CategoryWithCount]]:
    return DataResponse(data=await service.list_categories())


@router.get(
    "/{slug}",
    response_model=DataResponse[CategoryWithCount],
    summary="Category details",
    responses={404: {"description": "Category not found"}},
)
async def get_category(
    service: CategoryServiceDep, slug: str
) -> DataResponse[CategoryWithCount]:
    return DataResponse(data=await service.get(slug))


@router.get(
    "/{slug}/tools",
    response_model=Page[ToolSummary],
    summary="Tools in a category",
    responses={404: {"description": "Category not found"}},
)
async def category_tools(
    service: CategoryServiceDep,
    slug: str,
    filters: Annotated[ToolFilters, Depends(tool_filters)],
    params: Annotated[PageParams, Depends(page_params)],
) -> Page[ToolSummary]:
    _, page = await service.tools_in_category(slug, filters, params)
    return page
