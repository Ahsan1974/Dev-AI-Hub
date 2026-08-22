"""Admin authentication and a pluggable in-process rate limiter.

The rate limiter keeps counters in memory, which is correct for a single
process. The interface is deliberately narrow so a Redis backed implementation
can replace it without touching call sites.
"""

from __future__ import annotations

import secrets
import time
from collections import defaultdict, deque
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.core.errors import RateLimitError, UnauthorizedError

ADMIN_API_KEY_HEADER = "X-Admin-Api-Key"

_admin_key_scheme = APIKeyHeader(name=ADMIN_API_KEY_HEADER, auto_error=False)


async def require_admin(
    api_key: Annotated[str | None, Depends(_admin_key_scheme)] = None,
) -> str:
    """Guard every mutating endpoint.

    Fails closed: if no ADMIN_API_KEY is configured the admin surface is
    unavailable rather than open.
    """
    if not settings.admin_enabled:
        raise UnauthorizedError(
            "The admin API is disabled. Set ADMIN_API_KEY to enable it.",
            code="ADMIN_DISABLED",
        )
    if not api_key or not secrets.compare_digest(api_key, settings.admin_api_key):
        raise UnauthorizedError(
            f"A valid {ADMIN_API_KEY_HEADER} header is required.",
        )
    return api_key


class RateLimiter:
    """Fixed-window-per-client limiter backed by a deque of timestamps."""

    def __init__(self, requests: int, window_seconds: int) -> None:
        self.requests = requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.monotonic()
        window = self._hits[key]
        cutoff = now - self.window_seconds
        while window and window[0] < cutoff:
            window.popleft()
        if len(window) >= self.requests:
            raise RateLimitError()
        window.append(now)

    def reset(self) -> None:
        self._hits.clear()


rate_limiter = RateLimiter(
    settings.rate_limit_requests, settings.rate_limit_window_seconds
)


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "anonymous"


async def rate_limit(request: Request) -> None:
    """Dependency applied to expensive endpoints (search, recommendations)."""
    if not settings.rate_limit_enabled:
        return
    rate_limiter.check(client_key(request))
