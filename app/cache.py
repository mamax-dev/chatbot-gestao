import time
from threading import Lock

from .config import CACHE_TTL_SECONDS
from .document import normalize

_cache: dict[str, tuple[float, dict]] = {}
_lock = Lock()


def get_cached(question: str) -> dict | None:
    key = normalize(question)
    with _lock:
        saved = _cache.get(key)
        if not saved:
            return None
        created, value = saved
        if time.time() - created > CACHE_TTL_SECONDS:
            _cache.pop(key, None)
            return None
        return {**value, "cached": True}


def set_cached(question: str, value: dict) -> None:
    with _lock:
        _cache[normalize(question)] = (time.time(), {**value, "cached": False})
