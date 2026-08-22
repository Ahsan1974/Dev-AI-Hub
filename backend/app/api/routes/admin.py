"""Administrative write API.

Every route requires ``X-Admin-Api-Key``. When ``ADMIN_API_KEY`` is unset the
whole surface returns 401, so a default deployment exposes no destructive
endpoint at all.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import CollectionServiceDep, DbSession, ToolServiceDep
from app.core.pagination import DataResponse
from app.core.security import require_admin
from app.models.category import Category
from app.models.tag import Tag
from app.repositories.category_repository import CategoryRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.category import CategoryCreate, CategoryOut
from app.schemas.collection import CollectionDetail, CollectionWrite
from app.schemas.tag import TagCreate, TagOut
from app.schemas.tool import ToolDetail, ToolPatch, ToolWrite
from app.utils.text import slugify

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
    responses={401: {"description": "Missing or invalid admin API key"}},
)

AdminKey = Annotated[str, Depends(require_admin)]


@router.post(
    "/tools",
    response_model=DataResponse[ToolDetail],
    status_code=status.HTTP_201_CREATED,
    summary="Create a tool",
)
async def create_tool(
    service: ToolServiceDep, payload: ToolWrite
) -> DataResponse[ToolDetail]:
    return DataResponse(data=await service.create(payload))


@router.patch(
    "/tools/{slug}",
    response_model=DataResponse[ToolDetail],
    summary="Update a tool, its pricing, free access or verification",
)
async def update_tool(
    service: ToolServiceDep, slug: str, payload: ToolPatch
) -> DataResponse[ToolDetail]:
    return DataResponse(data=await service.update(slug, payload))


@router.delete(
    "/tools/{slug}",
    response_model=DataResponse[dict],
    summary="Delete a tool",
)
async def delete_tool(service: ToolServiceDep, slug: str) -> DataResponse[dict]:
    await service.delete(slug)
    return DataResponse(data={"slug": slug, "deleted": "true"})


@router.post(
    "/tools/{slug}/feature",
    response_model=DataResponse[ToolDetail],
    summary="Feature or unfeature a tool",
)
async def feature_tool(
    service: ToolServiceDep, slug: str, featured: bool = True
) -> DataResponse[ToolDetail]:
    return DataResponse(data=await service.update(slug, ToolPatch(featured=featured)))


@router.post(
    "/tools/{slug}/deactivate",
    response_model=DataResponse[ToolDetail],
    summary="Hide a tool without deleting it",
)
async def deactivate_tool(service: ToolServiceDep, slug: str) -> DataResponse[ToolDetail]:
    return DataResponse(data=await service.update(slug, ToolPatch(is_active=False)))


@router.post(
    "/categories",
    response_model=DataResponse[CategoryOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
)
async def create_category(
    session: DbSession, payload: CategoryCreate
) -> DataResponse[CategoryOut]:
    repo = CategoryRepository(session)
    category = Category(
        name=payload.name,
        slug=payload.slug or slugify(payload.name),
        description=payload.description,
        group=payload.group,
        icon=payload.icon,
        sort_order=payload.sort_order,
    )
    await repo.add(category)
    await session.commit()
    return DataResponse(data=CategoryOut.model_validate(category))


@router.post(
    "/tags",
    response_model=DataResponse[TagOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create a tag",
)
async def create_tag(session: DbSession, payload: TagCreate) -> DataResponse[TagOut]:
    repo = TagRepository(session)
    slug = payload.slug or slugify(payload.name)
    existing = await repo.get(str(payload.kind), slug)
    if existing is not None:
        return DataResponse(data=TagOut.model_validate(existing))
    tag = Tag(name=payload.name, slug=slug, kind=str(payload.kind))
    await repo.add(tag)
    await session.commit()
    return DataResponse(data=TagOut.model_validate(tag))


@router.post(
    "/collections",
    response_model=DataResponse[CollectionDetail],
    status_code=status.HTTP_201_CREATED,
    summary="Create a curated collection",
)
async def create_collection(
    service: CollectionServiceDep, payload: CollectionWrite
) -> DataResponse[CollectionDetail]:
    return DataResponse(data=await service.create(payload))
