import re
from .business_config import load_business
from .text import normalize

def validate_answer(question:str,answer:str,context:list):
    if not answer or len(answer.strip())<8: return False,'empty_or_short'
    if len(answer)>2400: return False,'too_long'
    if answer.rstrip().endswith((',',':',';','-')): return False,'possibly_truncated'
    if not context: return False,'no_context'
    cfg=load_business(); allowed_text=' '.join(x['text'] for x in context)
    allowed_money=set(re.findall(r'R\$\s*\d+(?:[.,]\d+)?',allowed_text))
    cited_money=set(re.findall(r'R\$\s*\d+(?:[.,]\d+)?',answer))
    if not cited_money.issubset(allowed_money): return False,'unsupported_money'
    known={normalize(s['nome']) for s in cfg['servicos']}
    q=normalize(question); a=normalize(answer)
    requested=[name for name in known if any(w in q for w in name.split() if len(w)>4)]
    if requested and any(not any(w in a for w in name.split() if len(w)>4) for name in requested): return False,'missing_requested_subject'
    return True,'ok'
