import time
from collections import defaultdict,deque
from threading import Lock
from .config import RATE_LIMIT_REQUESTS,RATE_LIMIT_WINDOW_SECONDS
_success=defaultdict(deque);_lock=Lock()
def can_use_ai(identifier):
    now=time.time();cutoff=now-RATE_LIMIT_WINDOW_SECONDS
    with _lock:
        q=_success[identifier]
        while q and q[0]<cutoff:q.popleft()
        return len(q)<RATE_LIMIT_REQUESTS
def record_ai_success(identifier):
    with _lock:_success[identifier].append(time.time())
