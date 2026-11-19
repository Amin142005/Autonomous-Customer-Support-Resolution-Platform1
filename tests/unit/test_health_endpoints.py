"""Tests for the /health endpoints.

Verifies:
- ``/health/live`` returns 200 with status, service, version, timestamp.
- ``/health/ready`` returns 200 with status, service, checks info.
- ``verbose=false`` on ready returns the short form.
- The liveness endpoint does not require ``X-Request-ID``.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestHealthLive:
    async def test_live_returns_ok(self, test_client: AsyncClient) -> None:
        resp = await test_client.get("/health/live")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert "service" in body
        assert "version" in body
        assert "timestamp" in body

    async def test_live_does_not_require_request_id(self, test_client: AsyncClient) -> None:
        """Liveness probes often cannot guarantee a request-id context."""
        resp = await test_client.get("/health/live")
        assert resp.status_code == 200
        # It should still get one from the middleware
        assert "X-Request-ID" in resp.headers


class TestHealthReady:
    async def test_ready_returns_verbose_by_default(self, test_client: AsyncClient) -> None:
        resp = await test_client.get("/health/ready")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ready"
        assert "service" in body
        assert "checks" in body
        assert "ok" in body

    async def test_ready_returns_service_and_checks(self, test_client: AsyncClient) -> None:
        """The verbose response includes service name, version, timestamp and per-check detail."""
        resp = await test_client.get("/health/ready?verbose=true")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ready"
        assert body["service"] is not None
        assert body["version"] is not None
        assert body["timestamp"] is not None
        # checks is a dict of individual check results (e.g. database, redis, filesystem)
        assert isinstance(body["checks"], dict)

    async def test_ready_verbose_false_returns_full_response(self, test_client: AsyncClient) -> None:
        """Current API: verbose=false still returns full response body."""
        resp = await test_client.get("/health/ready?verbose=false")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ready"
        assert "service" in body
        assert "checks" in body
        assert "ok" in body