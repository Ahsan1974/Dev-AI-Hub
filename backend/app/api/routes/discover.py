"""Homepage, free tools and static discovery metadata."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import HomeServiceDep
from app.core.enums import (
    PRICING_STATUS_DESCRIPTIONS,
    PRICING_STATUS_LABELS,
    FREE_PRICING_STATUSES,
)
from app.core.pagination import DataResponse
from app.schemas.home import FreeToolsResponse, HomeResponse
from app.services.workflows import POPULAR_SEARCHES, STACK_AREAS, WORKFLOWS

router = APIRouter(tags=["discovery"])


@router.get(
    "/home",
    response_model=DataResponse[HomeResponse],
    summary="Everything the homepage renders",
)
async def home(service: HomeServiceDep) -> DataResponse[HomeResponse]:
    return DataResponse(data=await service.home())


@router.get(
    "/free-tools",
    response_model=DataResponse[FreeToolsResponse],
    summary="Free tools grouped by how they are free",
)
async def free_tools(
    service: HomeServiceDep,
    category: str | None = Query(None, description="Restrict to a category slug."),
    limit: int = Query(12, ge=1, le=48),
) -> DataResponse[FreeToolsResponse]:
    return DataResponse(data=await service.free_tools(category, limit))


@router.get(
    "/meta",
    response_model=DataResponse[dict],
    summary="Static taxonomy metadata",
    description="Pricing vocabulary, workflows and stack areas used by the UI.",
)
async def meta() -> DataResponse[dict]:
    return DataResponse(
        data={
            "pricing_statuses": [
                {
                    "value": value,
                    "label": label,
                    "description": PRICING_STATUS_DESCRIPTIONS[value],
                    "is_free": value in FREE_PRICING_STATUSES,
                }
                for value, label in PRICING_STATUS_LABELS.items()
            ],
            "workflows": [workflow.model_dump() for workflow in WORKFLOWS],
            "stack_areas": STACK_AREAS,
            "popular_searches": POPULAR_SEARCHES,
        }
    )
