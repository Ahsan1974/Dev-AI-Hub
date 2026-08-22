from fastapi import APIRouter

from app.api.routes import (
    admin,
    categories,
    collections,
    compare,
    discover,
    favorites,
    recommendations,
    search,
    tools,
)

api_router = APIRouter()
api_router.include_router(discover.router)
api_router.include_router(tools.router)
api_router.include_router(categories.router)
api_router.include_router(search.router)
api_router.include_router(recommendations.router)
api_router.include_router(compare.router)
api_router.include_router(collections.router)
api_router.include_router(favorites.router)
api_router.include_router(admin.router)

__all__ = ["api_router"]
