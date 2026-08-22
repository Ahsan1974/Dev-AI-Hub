from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import CategoryNotFoundError
from app.core.pagination import Page, PageParams
from app.repositories.category_repository import CategoryRepository
from app.repositories.tool_repository import ToolRepository
from app.schemas.category import CategoryOut, CategoryWithCount
from app.schemas.search import ToolFilters
from app.schemas.tool import ToolSummary

_FIELDS = ("id", "name", "slug", "description", "group", "icon", "sort_order")


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = CategoryRepository(session)
        self.tools = ToolRepository(session)

    async def list_categories(self) -> list[CategoryWithCount]:
        categories = await self.repo.list_all()
        counts = await self.repo.counts()
        return [
            CategoryWithCount(
                **{field: getattr(category, field) for field in _FIELDS},
                tool_count=counts.get(category.id, (0, 0))[0],
                free_tool_count=counts.get(category.id, (0, 0))[1],
            )
            for category in categories
        ]

    async def get(self, slug: str) -> CategoryWithCount:
        category = await self.repo.get_by_slug(slug)
        if category is None:
            raise CategoryNotFoundError(f"No category exists with the slug '{slug}'.")
        counts = await self.repo.counts()
        return CategoryWithCount(
            **{field: getattr(category, field) for field in _FIELDS},
            tool_count=counts.get(category.id, (0, 0))[0],
            free_tool_count=counts.get(category.id, (0, 0))[1],
        )

    async def tools_in_category(
        self, slug: str, filters: ToolFilters, params: PageParams
    ) -> tuple[CategoryOut, Page[ToolSummary]]:
        category = await self.repo.get_by_slug(slug)
        if category is None:
            raise CategoryNotFoundError(f"No category exists with the slug '{slug}'.")
        filters.categories = [*filters.categories, slug]
        tools, total = await self.tools.list_tools(filters, params)
        return (
            CategoryOut.model_validate(category),
            Page.build(
                [ToolSummary.from_model(tool) for tool in tools], params, total
            ),
        )
