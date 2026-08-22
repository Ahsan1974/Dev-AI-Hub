from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query

from app.api.deps import ToolServiceDep
from app.core.pagination import DataResponse, Page, PageParams, page_params
from app.schemas.pricing import ToolPricingResponse
from app.schemas.search import ToolFilters, tool_filters
from app.schemas.tool import ToolDetail, ToolSummary
from app.utils.presentation import verification_info

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get(
    "",
    response_model=Page[ToolSummary],
    summary="Browse tools",
    description="Paginated tool list with the full filter set applied.",
)
async def list_tools(
    service: ToolServiceDep,
    filters: Annotated[ToolFilters, Depends(tool_filters)],
    params: Annotated[PageParams, Depends(page_params)],
) -> Page[ToolSummary]:
    return await service.list_tools(filters, params)


@router.post(
    "/resolve",
    response_model=DataResponse[list[ToolSummary]],
    summary="Resolve tools by slug",
    description=(
        "Hydrates a client-side list such as favourites or recently viewed "
        "without needing an account."
    ),
)
async def resolve_tools(
    service: ToolServiceDep,
    slugs: Annotated[list[str], Body(embed=True, max_length=100)],
) -> DataResponse[list[ToolSummary]]:
    return DataResponse(data=await service.resolve_many(slugs))


@router.get(
    "/{slug}",
    response_model=DataResponse[ToolDetail],
    summary="Tool details",
    responses={404: {"description": "Tool not found"}},
)
async def get_tool(
    service: ToolServiceDep,
    slug: Annotated[str, Path(description="URL slug, e.g. `cursor`.")],
) -> DataResponse[ToolDetail]:
    return DataResponse(data=await service.get_detail(slug))


@router.get(
    "/{identifier}/alternatives",
    response_model=DataResponse[list[ToolSummary]],
    summary="Alternatives to a tool",
    description="Tools sharing categories, ranked by category and feature overlap.",
)
async def tool_alternatives(
    service: ToolServiceDep,
    identifier: str,
    limit: Annotated[int, Query(ge=1, le=24)] = 6,
) -> DataResponse[list[ToolSummary]]:
    return DataResponse(data=await service.alternatives(identifier, limit))


@router.get(
    "/{identifier}/pricing",
    response_model=DataResponse[ToolPricingResponse],
    summary="Structured pricing",
)
async def tool_pricing(
    service: ToolServiceDep, identifier: str
) -> DataResponse[ToolPricingResponse]:
    return DataResponse(data=await service.pricing(identifier))


@router.get(
    "/{identifier}/verification",
    response_model=DataResponse[dict],
    summary="Verification metadata",
)
async def tool_verification(service: ToolServiceDep, identifier: str) -> DataResponse[dict]:
    tool = await service.get_model_or_404(identifier)
    info = verification_info(tool)
    return DataResponse(
        data={
            **info.model_dump(),
            "tool_slug": tool.slug,
            "pricing_url": tool.pricing_url or tool.website_url,
        }
    )
