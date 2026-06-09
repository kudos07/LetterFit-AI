"""Short-lived in-memory cache to avoid repeat Mistral calls for the same inputs."""

import hashlib
import time
from typing import Any

_CACHE: dict[str, tuple[float, Any]] = {}
DEFAULT_TTL = 600


def _cache_key(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:20]
    return f"{prefix}:{digest}"


def cache_get(prefix: str, *parts: str) -> Any | None:
    key = _cache_key(prefix, *parts)
    entry = _CACHE.get(key)
    if not entry:
        return None
    expires_at, value = entry
    if time.time() > expires_at:
        _CACHE.pop(key, None)
        return None
    return value


def cache_set(prefix: str, value: Any, *parts: str, ttl: int = DEFAULT_TTL) -> None:
    key = _cache_key(prefix, *parts)
    _CACHE[key] = (time.time() + ttl, value)
