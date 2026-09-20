from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse


class Batch11RateLimiter:
    def __init__(
        self,
        limit: int = 120,
        window_seconds: int = 60,
    ) -> None:
        self.limit = max(1, limit)
        self.window_seconds = max(1, window_seconds)
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            events = self._events[key]

            while events and events[0] <= cutoff:
                events.popleft()

            if len(events) >= self.limit:
                return False

            events.append(now)
            return True


rate_limiter = Batch11RateLimiter(
    limit=int(os.getenv("N1MOX30_RATE_LIMIT", "120")),
    window_seconds=int(os.getenv("N1MOX30_RATE_WINDOW", "60")),
)


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")

    if forwarded:
        return forwarded.split(",")[0].strip()

    if request.client:
        return request.client.host

    return "unknown"


async def security_middleware(
    request: Request,
    call_next: Callable,
):
    path = request.url.path

    exempt = {
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    if path not in exempt:
        if not rate_limiter.allow(client_key(request)):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please retry shortly."
                },
                headers={
                    "Retry-After": "60",
                },
            )

    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(self), geolocation=()"
    )

    if (
        path.startswith("/auth/")
        or path.startswith("/users/")
        or path.startswith("/platform/")
    ):
        response.headers["Cache-Control"] = "no-store"

    return response


def validate_production_secrets(settings) -> list[str]:
    problems: list[str] = []

    environment = str(
        getattr(settings, "environment", "development")
    ).lower()

    secret = str(
        getattr(settings, "secret_key", "")
    )

    if environment == "production":
        if not secret:
            problems.append("SECRET_KEY is missing.")

        if secret.startswith(
            "n1mox30-development-change-this-before-production"
        ):
            problems.append(
                "SECRET_KEY is still using the development default."
            )

        if len(secret) < 32:
            problems.append(
                "SECRET_KEY must contain at least 32 characters."
            )

    return problems
