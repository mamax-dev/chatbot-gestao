import re,unicodedata
from functools import lru_cache
from .config import DOCUMENT_PATH

def normalize(text):
    text=unicodedata.normalize('NFKD',(text or '').lower())
    text=''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+',' ',text).strip()
@lru_cache(maxsize=1)
def load_document():
    from striprtf.striprtf import rtf_to_text
    text=rtf_to_text(DOCUMENT_PATH.read_text(encoding='latin-1')).strip()
    if not text:raise RuntimeError('O arquivo instrucoes.rtf está vazio.')
    return text
def blocks_from_text(text):return [x.strip() for x in re.split(r'\n+',text) if x.strip()]
def is_heading(block):
    clean=block.strip();letters=''.join(c for c in clean if c.isalpha())
    return bool(letters) and len(clean)<=80 and clean==clean.upper()
def sections_from_text(text):
    out=[];heading='DOCUMENTO';content=[]
    for block in blocks_from_text(text):
        if is_heading(block):
            if content:out.append((heading,content))
            heading,content=block,[]
        else:content.append(block)
    if content:out.append((heading,content))
    return out
