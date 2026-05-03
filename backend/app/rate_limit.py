from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status

from .config import (
    AUTH_RATE_LIMIT,
    AUTH_RATE_WINDOW_SECONDS,
    CHAT_RATE_LIMIT,
    CHAT_RATE_WINDOW_SECONDS,
    IMPORT_RATE_LIMIT,
    IMPORT_RATE_WINDOW_SECONDS,
)

_REQUEST_LOG: dict[str, deque[datetime]] = defaultdict(deque)


def _hit(bucket: str, limit: int, window_seconds: int) -> None:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=window_seconds)
    queue = _REQUEST_LOG[bucket]
    while queue and queue[0] < window_start:
        queue.popleft()
    if len(queue) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment and try again.",
        )
    queue.append(now)


def _client_key(request: Request, prefix: str) -> str:
    host = request.client.host if request.client else "unknown"
    return f"{prefix}:{host}"


def limit_auth(request: Request) -> None:
    _hit(_client_key(request, "auth"), AUTH_RATE_LIMIT, AUTH_RATE_WINDOW_SECONDS)


def limit_chat(request: Request) -> None:
    _hit(_client_key(request, "chat"), CHAT_RATE_LIMIT, CHAT_RATE_WINDOW_SECONDS)


def limit_import(request: Request) -> None:
    _hit(_client_key(request, "import"), IMPORT_RATE_LIMIT, IMPORT_RATE_WINDOW_SECONDS)


def reset_rate_limits() -> None:
    _REQUEST_LOG.clear()
