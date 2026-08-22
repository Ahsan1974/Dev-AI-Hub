from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import RecommendationServiceDep, StackServiceDep
from app.core.pagination import DataResponse
from app.core.security import rate_limit
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    StackRequest,
    StackResponse,
)
from app.services.llm import get_provider

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post(
    "",
    response_model=DataResponse[RecommendationResponse],
    dependencies=[Depends(rate_limit)],
    summary="Recommend tools for a task",
    description=(
        "Rule-based scoring: category 30, keywords 25, technology 20, features 15, "
        "pricing 10. Only the dimensions your request expresses count towards the "
        "percentage. No API key required."
    ),
)
async def recommend(
    service: RecommendationServiceDep, payload: RecommendationRequest
) -> DataResponse[RecommendationResponse]:
    return DataResponse(data=await service.recommend(payload))


@router.post(
    "/ai",
    response_model=DataResponse[RecommendationResponse],
    dependencies=[Depends(rate_limit)],
    summary="LLM-assisted recommendations (falls back to rules)",
    description=(
        "Reserved for LLM re-ranking. Until a provider is configured this returns "
        "the deterministic result and says so in `meta.notes`."
    ),
)
async def recommend_with_llm(
    service: RecommendationServiceDep, payload: RecommendationRequest
) -> DataResponse[RecommendationResponse]:
    result = await service.recommend(payload)
    provider = get_provider()
    if not provider.available:
        result.meta.notes.append(
            "No LLM provider is configured, so the deterministic ranking was used."
        )
    return DataResponse(data=result)


@router.post(
    "/stack",
    response_model=DataResponse[StackResponse],
    dependencies=[Depends(rate_limit)],
    summary="Build a personal AI developer stack",
)
async def build_stack(
    service: StackServiceDep, payload: StackRequest
) -> DataResponse[StackResponse]:
    return DataResponse(data=await service.build(payload))
