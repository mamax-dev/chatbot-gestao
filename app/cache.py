import time
from threading import Lock
from .config import CACHE_TTL_SECONDS,CACHE_VERSION
from .document import normalize
_cache={}; _lock=Lock()
def _key(q): return f'{CACHE_VERSION}:{normalize(q)}'
def get_cached(q):
    with _lock:
        item=_cache.get(_key(q))
        if not item:return None
        created,value=item
        if time.time()-created>CACHE_TTL_SECONDS:
            _cache.pop(_key(q),None);return None
        return {**value,'cached':True}
def set_cached(q,value):
    # Only complete, grounded answers. Never cache errors, ambiguous or absent decisions.
    if value.get('status')!='answered' or not value.get('evidence') or not value.get('complete',True): return
    with _lock:_cache[_key(q)]=(time.time(),{**value,'cached':False})
