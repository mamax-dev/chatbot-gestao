import re,unicodedata
from difflib import get_close_matches
ALIASES={'vcs':'voces','vc':'voces','fazem':'faz','diagnostco':'diagnostico','diagnotico':'diagnostico','formataçao':'formatacao','wi fi':'wifi'}
def normalize(text):
    text=unicodedata.normalize('NFKD',(text or '').lower());text=''.join(c for c in text if not unicodedata.combining(c));text=re.sub(r'[^a-z0-9]+',' ',text).strip()
    return ' '.join(ALIASES.get(w,w) for w in text.split())
def closest(value,choices,cutoff=.80):
    found=get_close_matches(value,choices,n=1,cutoff=cutoff);return found[0] if found else ''
