import re,unicodedata
ALIASES={'vc':'voces','vcs':'voces','voce':'voces','fazem':'faz','diagnostco':'diagnostico','diagnotico':'diagnostico'}
def normalize(text):
    value=unicodedata.normalize('NFKD',(text or '').lower())
    value=''.join(c for c in value if not unicodedata.combining(c))
    value=re.sub(r'[^a-z0-9]+',' ',value).strip()
    return ' '.join(ALIASES.get(word,word) for word in value.split())
