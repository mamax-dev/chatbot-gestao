import time
from threading import Lock

from .config import CACHE_TTL_SECONDS, CACHE_VERSION
from .document import normalize

_cache: dict[str, tuple[float, dict]] = {}
_lock = Lock()


def _key(question: str) -> str:
    return f"{CACHE_VERSION}:{normalize(question)}"


def get_cached(question: str) -> dict | None:
    with _lock:
        saved = _cache.get(_key(question))
        if not saved:
            return None
        created, value = saved
        if time.time() - created > CACHE_TTL_SECONDS:
            _cache.pop(_key(question), None)
            return None
        return {**value, "cached": True}


def set_cached(question: str, value: dict) -> None:
    # Erros e respostas sem evidência nunca entram no cache.
    if value.get("status") not in {"answered", "absent", "ambiguous"}:
        return
    if value.get("status") == "answered" and not value.get("evidence"):
        return
    with _lock:
        _cache[_key(question)] = (time.time(), {**value, "cached": False})
