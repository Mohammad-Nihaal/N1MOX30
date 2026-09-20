from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class ProductionSecurityMiddleware(BaseHTTPMiddleware):
    """Baseline production protections.

    Enabled by main.py only when ENVIRONMENT=production.
    Rate limits are intentionally conservative and should move to Redis
    before horizontal scaling.
    """

    def __init__(self, app, requests_per_minute: int = 120, max_body_bytes: int = 8 * 1024 * 1024):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.max_body_bytes = max_body_bytes
        self._hits = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_body_bytes:
                    return JSONResponse({"detail": "Request body too large."}, status_code=413)
            except ValueError:
                return JSONResponse({"detail": "Invalid content length."}, status_code=400)

        host = request.client.host if request.client else "unknown"
        now = time.monotonic()
        bucket = self._hits[host]
        cutoff = now - 60
        while bucket and bucket[0] < cutoff:
            bucket.popleft()

        if len(bucket) >= self.requests_per_minute:
            return JSONResponse({"detail": "Too many requests. Try again later."}, status_code=429)

        bucket.append(now)
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = response.headers.get("Cache-Control", "no-store") if request.url.path.startswith("/auth") else response.headers.get("Cache-Control", "public, max-age=0, must-revalidate")
        return response