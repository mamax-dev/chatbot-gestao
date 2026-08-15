import time
from threading import Lock
from .config import CACHE_TTL_SECONDS,CACHE_VERSION
from .document import normalize
_cache={};_lock=Lock()
def key(q):return CACHE_VERSION+':'+normalize(q)
def get_cached(q):
    with _lock:
        item=_cache.get(key(q))
        if not item:return None
        ts,val=item
        if time.time()-ts>CACHE_TTL_SECONDS:_cache.pop(key(q),None);return None
        return {**val,'cached':True}
def set_cached(q,val):
    if val.get('status')=='answered' and val.get('evidence') and val.get('complete',True):
        with _lock:_cache[key(q)]=(time.time(),{**val,'cached':False})
