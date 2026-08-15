import time
from threading import Lock
from .config import CACHE_TTL_SECONDS,CACHE_VERSION
from .text import normalize
store={};lock=Lock()
def key(q):return CACHE_VERSION+':'+normalize(q)
def get(q):
    with lock:
        item=store.get(key(q))
        if not item:return None
        ts,val=item
        if time.time()-ts>CACHE_TTL_SECONDS:store.pop(key(q),None);return None
        return {**val,'cached':True}
def put(q,val):
    if val.get('status')=='answered' and val.get('evidence'):
        with lock:store[key(q)]=(time.time(),{**val,'cached':False})
