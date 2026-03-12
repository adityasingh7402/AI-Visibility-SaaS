"""
GEO Platform — API Middleware
HMAC authentication + request ID injection + request logging.
"""

import hashlib
import hmac
import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings

log = structlog.get_logger()


class HMACAuthMiddleware(BaseHTTPMiddleware):
    """Verify HMAC signature on incoming requests from Node.js.

    Headers required:
      X-Signature: HMAC-SHA256 hex digest of body
      X-Timestamp: Unix timestamp (reject if >30s old)
    """

    # Skip auth for these paths
    SKIP_PATHS = {"/health", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip auth for health/docs
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        settings = get_settings()

        # Step 1: Check required headers
        signature = request.headers.get("X-Signature", "")
        timestamp = request.headers.get("X-Timestamp", "")

        if not signature or not timestamp:
            log.warning("hmac_missing_headers", path=request.url.path)
            return Response(content='{"error": "Missing auth headers"}', status_code=401)

        # Step 2: Reject stale requests (>30 seconds)
        try:
            request_age = abs(time.time() - float(timestamp))
            if request_age > 30:
                log.warning("hmac_stale_request", age_seconds=round(request_age))
                return Response(content='{"error": "Request expired"}', status_code=401)
        except ValueError:
            return Response(content='{"error": "Invalid timestamp"}', status_code=401)

        # Step 3: Verify HMAC signature
        body = await request.body()
        payload = f"{timestamp}.{body.decode()}"
        expected = hmac.new(
            settings.hmac_secret_key.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            log.warning("hmac_invalid_signature", path=request.url.path)
            return Response(content='{"error": "Invalid signature"}', status_code=401)

        return await call_next(request)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Inject unique request ID into every request for tracing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4())[:8])

        # Bind to structlog context for all downstream logs
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Log request completion
        log.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            elapsed_ms=round(elapsed_ms),
        )

        response.headers["X-Request-Id"] = request_id
        return response
