"""CloudDesk Support Platform — FastAPI application.

Startup:
1. Loads typed settings from environment / .env
2. Configures structured JSON logging
3. Sets up CORS (from settings.cors_origins_list)
4. Registers API routes (imported lazily to keep startup fast)

Shutdown:
- Graceful cleanup (close DB connections, flush logs)
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import Settings, get_settings
from .core.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan: startup and shutdown hooks."""
    # ── Startup ──────────────────────────────────────────────────────────
    settings: Settings = get_settings()
    app.state.settings = settings  # type: ignore[attr-defined]

    setup_logging(settings)

    logger.info(
        f"{settings.APP_NAME} v{settings.APP_VERSION} starting",
        extra={
            "event": "app.starting",
            "environment": settings.APP_ENV,
            "version": settings.APP_VERSION,
        },
    )

    # Ensure data and log directories exist
    from pathlib import Path

    Path("data").mkdir(parents=True, exist_ok=True)
    Path(settings.LOG_DIR).mkdir(parents=True, exist_ok=True)

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info(
        "Shutting down",
        extra={"event": "app.shutting_down"},
    )


def create_app() -> FastAPI:
    """Build and return the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url=f"{settings.API_PREFIX}/docs" if settings.is_development else None,
        redoc_url=f"{settings.API_PREFIX}/redoc" if settings.is_development else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Health route (minimal, no auth) ─────────────────────────────────
    @app.get("/health/live")
    async def health_live() -> dict:
        return {"status": "ok", "service": settings.APP_NAME}

    @app.get("/health/ready")
    async def health_ready() -> dict:
        # For now, readiness is the same as liveness.
        # Later phases will add DB/Redis checks here.
        return {"status": "ready", "service": settings.APP_NAME}

    return app


app = create_app()
