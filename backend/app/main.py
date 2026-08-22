"""DevAI Hub API entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.routes import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.db.init_db import create_all
from app.db.session import engine
from app.schemas.common import ErrorResponse

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger("devai_hub")


@asynccontextmanager
async def lifespan(_: FastAPI):
    # SQLite is the zero-setup path, so create its schema on boot.
    # PostgreSQL is owned by Alembic and is never touched implicitly.
    if settings.is_sqlite:
        await create_all(engine)
        logger.info("SQLite schema ensured at %s", settings.database_url)

    if settings.auto_seed:
        from sqlalchemy import func, select

        from app.db.session import SessionFactory
        from app.models.tool import Tool
        from app.seed import seed

        async with SessionFactory() as session:
            count = await session.scalar(select(func.count()).select_from(Tool))
            if not count:
                logger.info("Empty catalogue detected — running auto-seed")
                report = await seed(session)
                logger.info("Auto-seed complete: %s", report.render())
            else:
                logger.info("Catalogue already has %s tools — skipping auto-seed", count)

    yield
    await engine.dispose()


DESCRIPTION = """
Discover the right AI tools for every developer task.

**Free-first**: every tool carries a standardised pricing status
(`FREE_FOREVER`, `FREE_TIER`, `FREE_CREDITS`, `FREE_TRIAL`, `OPEN_SOURCE`,
`BYOK`, `PAID_ONLY`) plus structured free-access limits, so a trial is never
presented as "free".

**Explainable**: recommendations come from transparent rule-based scoring, not a
black box, and every response says which signals matched.

**Honest about data**: pricing that has not been verified is reported as
unavailable rather than guessed.
"""

app = FastAPI(
    title=settings.app_name,
    description=DESCRIPTION,
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    # Preview + production Vercel apps (personal deploys).
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Api-Key", "X-Client-Id"],
    max_age=600,
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get(f"{settings.api_prefix}/health", tags=["system"], summary="Health check")
async def health() -> dict:
    return {
        "data": {
            "status": "ok",
            "version": settings.version,
            "environment": settings.environment,
            "database": "postgresql" if not settings.is_sqlite else "sqlite",
            "admin_api": "enabled" if settings.admin_enabled else "disabled",
        }
    }
