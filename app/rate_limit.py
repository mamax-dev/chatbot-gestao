import time
from collections import defaultdict, deque
from threading import Lock

from .config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

_requests: dict[str, deque] = defaultdict(deque)
_lock = Lock()


def allow(identifier: str) -> bool:
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    with _lock:
        bucket = _requests[identifier]
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_REQUESTS:
            return False
        bucket.append(now)
        return True
