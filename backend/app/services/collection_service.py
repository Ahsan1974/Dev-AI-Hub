from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import CollectionNotFoundError, ConflictError, ValidationError
from app.models.collection import Collection
from app.repositories.collection_repository import CollectionRepository
from app.repositories.tool_repository import ToolRepository
from app.schemas.collection import CollectionDetail, CollectionOut, CollectionWrite
from app.schemas.tool import ToolSummary
from app.utils.text import slugify


class CollectionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CollectionRepository(session)
        self.tools = ToolRepository(session)

    async def list_collections(self, featured_only: bool = False) -> list[CollectionOut]:
        collections = await self.repo.list_all(featured_only)
        return [
            CollectionOut(
                id=collection.id,
                name=collection.name,
                slug=collection.slug,
                description=collection.description,
                icon=collection.icon,
                is_featured=collection.is_featured,
                tool_count=len(collection.tools),
            )
            for collection in collections
        ]

    async def get(self, slug: str) -> CollectionDetail:
        collection = await self.repo.get_by_slug(slug)
        if collection is None:
            raise CollectionNotFoundError(
                f"No collection exists with the slug '{slug}'."
            )
        active = [tool for tool in collection.tools if tool.is_active]
        return CollectionDetail(
            id=collection.id,
            name=collection.name,
            slug=collection.slug,
            description=collection.description,
            icon=collection.icon,
            is_featured=collection.is_featured,
            tool_count=len(active),
            tools=[ToolSummary.from_model(tool) for tool in active],
        )

    async def create(self, payload: CollectionWrite) -> CollectionDetail:
        slug = payload.slug or slugify(payload.name)
        if await self.repo.get_by_slug(slug) is not None:
            raise ConflictError(f"A collection with the slug '{slug}' already exists.")
        tools = await self.tools.get_many_by_slugs(payload.tools)
        missing = set(payload.tools) - {tool.slug for tool in tools}
        if missing:
            raise ValidationError(
                "Unknown tool slugs: " + ", ".join(sorted(missing)),
                code="UNKNOWN_TOOL",
            )
        order = {slug_: index for index, slug_ in enumerate(payload.tools)}
        tools.sort(key=lambda tool: order[tool.slug])
        collection = Collection(
            name=payload.name,
            slug=slug,
            description=payload.description,
            icon=payload.icon,
            is_featured=payload.is_featured,
            sort_order=payload.sort_order,
            tools=tools,
        )
        await self.repo.add(collection)
        await self.session.commit()
        return await self.get(slug)
