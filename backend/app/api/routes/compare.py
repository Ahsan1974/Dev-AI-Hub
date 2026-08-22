from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import ComparisonServiceDep
from app.core.pagination import DataResponse
from app.schemas.compare import CompareRequest, CompareResponse

router = APIRouter(prefix="/compare", tags=["compare"])


@router.post(
    "",
    response_model=DataResponse[CompareResponse],
    summary="Compare up to four tools",
    description=(
        "Unknown values are returned as `kind: \"unknown\"` so a data gap is never "
        "rendered as a missing feature."
    ),
)
async def compare(
    service: ComparisonServiceDep, payload: CompareRequest
) -> DataResponse[CompareResponse]:
    return DataResponse(data=await service.compare(payload))


@router.get(
    "",
    response_model=DataResponse[CompareResponse],
    summary="Compare via query string",
    description="Shareable form: `/api/compare?slugs=cursor&slugs=cline`.",
)
async def compare_get(
    service: ComparisonServiceDep,
    slugs: Annotated[list[str], Query(min_length=2, max_length=4)],
) -> DataResponse[CompareResponse]:
    return DataResponse(data=await service.compare(CompareRequest(slugs=slugs)))
