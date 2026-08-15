import re, unicodedata
INJECTION_PATTERNS=(
 r'ignore (todas |as )?instru', r'ignore previous', r'revele (o )?prompt',
 r'system prompt', r'developer mode', r'mostre (a )?chave', r'api[_ ]?key',
 r'telegram[_ ]?bot[_ ]?token', r'webhook[_ ]?secret',
)
def clean_input(text:str)->str:
    value=unicodedata.normalize('NFKC',text or '')
    value=''.join(c for c in value if c in '\n\t' or unicodedata.category(c)[0]!='C')
    return re.sub(r'[ \t]+',' ',value).strip()
def injection_suspected(text:str)->bool:
    q=clean_input(text).lower()
    return any(re.search(p,q) for p in INJECTION_PATTERNS)
