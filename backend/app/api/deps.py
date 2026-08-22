"""FastAPI dependencies wiring services to the request-scoped session."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.category_service import CategoryService
from app.services.collection_service import CollectionService
from app.services.comparison_service import ComparisonService
from app.services.home_service import HomeService
from app.services.recommendation_service import RecommendationService
from app.services.search_service import SearchService
from app.services.stack_service import StackService
from app.services.tool_service import ToolService

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_tool_service(session: DbSession) -> ToolService:
    return ToolService(session)


def get_category_service(session: DbSession) -> CategoryService:
    return CategoryService(session)


def get_search_service(session: DbSession) -> SearchService:
    return SearchService(session)


def get_recommendation_service(session: DbSession) -> RecommendationService:
    return RecommendationService(session)


def get_comparison_service(session: DbSession) -> ComparisonService:
    return ComparisonService(session)


def get_collection_service(session: DbSession) -> CollectionService:
    return CollectionService(session)


def get_home_service(session: DbSession) -> HomeService:
    return HomeService(session)


def get_stack_service(session: DbSession) -> StackService:
    return StackService(session)


ToolServiceDep = Annotated[ToolService, Depends(get_tool_service)]
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]
RecommendationServiceDep = Annotated[
    RecommendationService, Depends(get_recommendation_service)
]
ComparisonServiceDep = Annotated[ComparisonService, Depends(get_comparison_service)]
CollectionServiceDep = Annotated[CollectionService, Depends(get_collection_service)]
HomeServiceDep = Annotated[HomeService, Depends(get_home_service)]
StackServiceDep = Annotated[StackService, Depends(get_stack_service)]
