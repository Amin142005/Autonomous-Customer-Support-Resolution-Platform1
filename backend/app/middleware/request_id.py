"""Request-ID middleware: generate and propagate a unique identifier per request.

Behaviour:
- If the inbound request already carries `X-Request-ID`, reuse that value.
- Otherwise generate a new UUID4 value.
- Write the ID back on every response.
- Make it available on `request.state.request_id` for downstream use (logging,
  traces, etc.).
- Logs the request-id on every request in the access log line via Starlette's
  default server logger (which already prints response headers).

Permissive licence: original code for this project (MIT).
"""

from __future__ import annotations

import logging
import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a unique request identifier to every request/response."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        req_id = request.headers.get(_HEADER) or str(uuid.uuid4())

        # Make available on request state for downstream handlers
        request.state.request_id = req_id  # type: ignore[attr-defined]

        logger.debug(
            "request started",
            extra={"event": "request.start", "request_id": req_id, "method": request.method, "path": request.url.path},
        )

        response = await call_next(request)
        response.headers[_HEADER] = req_id

        logger.debug(
            "request finished",
            extra={
                "event": "request.finish",
                "request_id": req_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
            },
        )

        return response
