"""Anonymous favourites.

Saving a tool never requires an account. The browser owns the list; these
endpoints exist so it can be hydrated server-side and, later, synced to a real
user without a schema change.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Header

from app.api.deps import DbSession, ToolServiceDep
from app.core.errors import ValidationError
from app.core.pagination import DataResponse
from app.repositories.favorite_repository import FavoriteRepository
from app.schemas.tool import ToolSummary

router = APIRouter(prefix="/favorites", tags=["favorites"])

CLIENT_ID_HEADER = "X-Client-Id"
ClientId = Annotated[
    str | None,
    Header(alias=CLIENT_ID_HEADER, description="Anonymous browser identifier."),
]


def _require_client_id(client_id: str | None) -> str:
    if not client_id or len(client_id) > 64:
        raise ValidationError(
            f"A {CLIENT_ID_HEADER} header of at most 64 characters is required.",
            code="CLIENT_ID_REQUIRED",
        )
    return client_id


@router.post(
    "/resolve",
    response_model=DataResponse[list[ToolSummary]],
    summary="Hydrate a locally stored favourites list",
)
async def resolve_favorites(
    service: ToolServiceDep,
    slugs: Annotated[list[str], Body(embed=True, max_length=200)],
) -> DataResponse[list[ToolSummary]]:
    return DataResponse(data=await service.resolve_many(slugs))


@router.get(
    "",
    response_model=DataResponse[list[ToolSummary]],
    summary="Server-side favourites for a client id",
)
async def list_favorites(
    session: DbSession, service: ToolServiceDep, client_id: ClientId = None
) -> DataResponse[list[ToolSummary]]:
    key = _require_client_id(client_id)
    tool_ids = await FavoriteRepository(session).tool_ids(key)
    tools = await service.repo.get_many_by_ids(tool_ids)
    order = {tool_id: index for index, tool_id in enumerate(tool_ids)}
    tools.sort(key=lambda tool: order.get(tool.id, 999))
    return DataResponse(data=[ToolSummary.from_model(tool) for tool in tools])


@router.put(
    "/{slug}",
    response_model=DataResponse[dict],
    summary="Save a tool",
)
async def add_favorite(
    session: DbSession, service: ToolServiceDep, slug: str, client_id: ClientId = None
) -> DataResponse[dict]:
    key = _require_client_id(client_id)
    tool = await service.get_model_or_404(slug)
    await FavoriteRepository(session).add(key, tool.id)
    await session.commit()
    return DataResponse(data={"slug": tool.slug, "saved": True})


@router.delete(
    "/{slug}",
    response_model=DataResponse[dict],
    summary="Remove a saved tool",
)
async def remove_favorite(
    session: DbSession, service: ToolServiceDep, slug: str, client_id: ClientId = None
) -> DataResponse[dict]:
    key = _require_client_id(client_id)
    tool = await service.get_model_or_404(slug)
    await FavoriteRepository(session).remove(key, tool.id)
    await session.commit()
    return DataResponse(data={"slug": tool.slug, "saved": False})
