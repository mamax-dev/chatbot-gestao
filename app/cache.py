import hashlib,json,time
from collections import OrderedDict
from threading import RLock
from .business_config import load_business
from .config import CACHE_TTL_SECONDS,GEMINI_MODEL
from .text import normalize
MAX_ITEMS=256; PROMPT_VERSION='predictive-v1'; _lock=RLock(); _store=OrderedDict()
def _version():
    raw=json.dumps(load_business(),ensure_ascii=False,sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()[:12]
def _key(q): return '|'.join([normalize(q),_version(),GEMINI_MODEL,PROMPT_VERSION])
def get(q):
    k=_key(q)
    with _lock:
        item=_store.get(k)
        if not item:return None
        ts,val=item
        if time.time()-ts>CACHE_TTL_SECONDS:_store.pop(k,None);return None
        _store.move_to_end(k);return {**val,'source':'cache','cached':True}
def put(q,val):
    if val.get('status')!='answered' or val.get('source')!='gemini' or not val.get('answer') or not val.get('evidence'):return False
    k=_key(q)
    with _lock:
        _store[k]=(time.time(),{**val,'cached':False});_store.move_to_end(k)
        while len(_store)>MAX_ITEMS:_store.popitem(last=False)
    return True
def clear():
    with _lock:_store.clear()
