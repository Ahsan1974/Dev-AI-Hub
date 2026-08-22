from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import CollectionServiceDep
from app.core.pagination import DataResponse
from app.schemas.collection import CollectionDetail, CollectionOut

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get(
    "",
    response_model=DataResponse[list[CollectionOut]],
    summary="List curated collections",
)
async def list_collections(
    service: CollectionServiceDep,
    featured: bool = Query(False, description="Only homepage collections."),
) -> DataResponse[list[CollectionOut]]:
    return DataResponse(data=await service.list_collections(featured))


@router.get(
    "/{slug}",
    response_model=DataResponse[CollectionDetail],
    summary="Collection with its tools",
    responses={404: {"description": "Collection not found"}},
)
async def get_collection(
    service: CollectionServiceDep, slug: str
) -> DataResponse[CollectionDetail]:
    return DataResponse(data=await service.get(slug))
