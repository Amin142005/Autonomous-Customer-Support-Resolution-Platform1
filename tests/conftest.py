"""Fixtures for offline test harness.

Every test that imports from this ``conftest`` gets:
- A ``mock_settings`` fixture backed by a ``tmp_path`` log directory.
- A ``test_app`` FastAPI application with those settings injected.
- An async ``test_client`` (``httpx.AsyncClient`` with ``ASGITransport``).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from backend.app.core.config import Settings, get_settings
from backend.app.main import create_app


@pytest.fixture
def mock_settings(tmp_path: Path) -> Settings:
    """Return a Settings instance with all paths pointing to tmp_path.

    This avoids writing real log / data files inside the project tree and
    keeps every test run isolated.
    """
    # Point log and data directories inside the temporary directory
    log_dir = tmp_path / "logs"
    data_dir = tmp_path / "data"
    log_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    settings = Settings(
        APP_ENV="testing",
        APP_NAME="CloudDesk Test",
        APP_VERSION="0.0.0",
        DEBUG=True,
        CORS_ORIGINS="*",
        LOG_LEVEL="DEBUG",
        LOG_FORMAT="json",
        LOG_DIR=str(log_dir),
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
    )
    return settings


@pytest.fixture(autouse=True)
def _patch_settings(monkeypatch: pytest.MonkeyPatch, mock_settings: Settings) -> None:
    """Override the cached ``get_settings`` so the app uses the test settings."""

    # Override get_settings to return our test instance
    original_get_settings = get_settings

    def _test_get_settings() -> Settings:
        return mock_settings

    monkeypatch.setattr("backend.app.core.config.get_settings", _test_get_settings)
    # Also clear the lru_cache on the original so any leftover call returns ours
    original_get_settings.cache_clear()


@pytest.fixture
async def test_app(mock_settings: Settings) -> AsyncGenerator:  # noqa: ARG001
    """Build a fresh FastAPI app for each test."""
    app = create_app()
    async with LifespanManager(app):
        yield app


@pytest.fixture
async def test_client(test_app) -> AsyncGenerator:  # noqa: ARG001
    """Async HTTP client wired to the test app via ASGI transport."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client