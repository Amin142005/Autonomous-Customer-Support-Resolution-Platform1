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
from .middleware import RequestIdMiddleware

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

    # CORS (added first so it wraps all other middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request-ID middleware
    app.add_middleware(RequestIdMiddleware)

    # ── Health routes (no auth, no request-id logging noise) ─────────────

    @app.get("/health/live", include_in_schema=False)
    async def health_live() -> dict:
        """Liveness probe — returns 200 as long as the process is alive.

        Used by orchestrators / load-balancers to determine if the pod should
        receive traffic.  No downstream dependency checks are performed.
        """
        from datetime import datetime, timezone

        return {
            "status": "ok",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/health/ready", include_in_schema=False)
    async def health_ready(verbose: bool = False) -> dict:
        """Readiness probe — verifies that required dependencies are available.

        Returns 200 when the app is ready to handle requests. In *verbose* mode
        includes per-dependency status; in compact mode returns a single
        boolean.

        Later phases will wire real DB and Redis checks here.
        """
        from datetime import datetime, timezone

        checks: dict[str, dict] = {}

        # --- Database --------------------------------------------------------
        # P2 will replace the stub with a real connection check
        try:
            db_url = settings.DATABASE_URL
            checks["database"] = {"status": "connected", "url": db_url.rsplit("/", 1)[0] + "/***" if db_url else None}
        except Exception as exc:  # noqa: BLE001
            checks["database"] = {"status": "error", "reason": str(exc)}

        # --- Redis -----------------------------------------------------------
        # P3-3 will replace the stub with a real PING
        try:
            redis_url = settings.REDIS_URL
            checks["redis"] = {"status": "connected" if redis_url and not redis_url.startswith("redis://localhost") else "standalone"}
        except Exception as exc:  # noqa: BLE001
            checks["redis"] = {"status": "error", "reason": str(exc)}

        # --- Local file system -----------------------------------------------
        from pathlib import Path

        data_dir = Path("data")
        checks["filesystem"] = {
            "status": "ok" if data_dir.is_dir() else "error",
            "path": str(data_dir),
        }

        all_ok = all(v.get("status") in ("ok", "connected", "standalone") for v in checks.values())

        if verbose:
            return {
                "status": "ready" if all_ok else "not_ready",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checks": checks,
            }

        return {
            "status": "ready" if all_ok else "not_ready",
            "service": settings.APP_NAME,
            "checks": len(checks),
            "ok": sum(1 for v in checks.values() if v.get("status") in ("ok", "connected", "standalone")),
        }

    return app


app = create_app()
