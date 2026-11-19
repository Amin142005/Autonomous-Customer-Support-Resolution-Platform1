"""Tests for the ``RequestIdMiddleware``.

Verifies:
- A request without ``X-Request-ID`` gets a new UUID v4 assigned.
- A request with a custom ``X-Request-ID`` preserves that value.
- Each request gets a unique ID (no accidental caching).
- The header is case-insensitive on input.
- The ``/health/ready`` endpoint also receives a request-id.
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient


class TestRequestIdGeneration:
    async def test_auto_generates_uuid_v4(self, test_client: AsyncClient) -> None:
        resp = await test_client.get("/health/live")
        req_id = resp.headers.get("X-Request-ID")
        assert req_id is not None
        # Verify it is a valid UUID v4
        parsed = uuid.UUID(req_id, version=4)
        assert parsed.version == 4

    async def test_preserves_custom_request_id(self, test_client: AsyncClient) -> None:
        my_id = "my-custom-trace-001"
        resp = await test_client.get("/health/live", headers={"X-Request-ID": my_id})
        assert resp.headers.get("X-Request-ID") == my_id

    async def test_unique_per_request(self, test_client: AsyncClient) -> None:
        resp1 = await test_client.get("/health/live")
        resp2 = await test_client.get("/health/live")
        id1 = resp1.headers.get("X-Request-ID")
        id2 = resp2.headers.get("X-Request-ID")
        assert id1 != id2

    async def test_header_is_case_insensitive(self, test_client: AsyncClient) -> None:
        my_id = "lowercase-header-value"
        resp = await test_client.get("/health/live", headers={"x-request-id": my_id})
        assert resp.headers.get("X-Request-ID") == my_id

    async def test_ready_endpoint_also_gets_request_id(self, test_client: AsyncClient) -> None:
        resp = await test_client.get("/health/ready")
        assert "X-Request-ID" in resp.headers