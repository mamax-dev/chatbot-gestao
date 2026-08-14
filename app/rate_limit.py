import time
from collections import defaultdict, deque
from threading import Lock

from .config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

_successes: dict[str, deque] = defaultdict(deque)
_lock = Lock()


def can_use_ai(identifier: str) -> bool:
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    with _lock:
        bucket = _successes[identifier]
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        return len(bucket) < RATE_LIMIT_REQUESTS


def record_ai_success(identifier: str) -> None:
    with _lock:
        _successes[identifier].append(time.time())
