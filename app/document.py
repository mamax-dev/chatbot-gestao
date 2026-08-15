import re, unicodedata
from functools import lru_cache
from .config import DOCUMENT_PATH

def normalize(text:str)->str:
    text=unicodedata.normalize('NFKD',text.lower())
    text=''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+',' ',text).strip()

@lru_cache(maxsize=1)
def load_document()->str:
    from striprtf.striprtf import rtf_to_text
    if not DOCUMENT_PATH.exists(): raise RuntimeError('Arquivo instrucoes.rtf não encontrado.')
    text=rtf_to_text(DOCUMENT_PATH.read_text(encoding='latin-1')).strip()
    if not text: raise RuntimeError('O arquivo instrucoes.rtf está vazio.')
    return text

def blocks_from_text(text:str)->list[str]:
    return [x.strip() for x in re.split(r'\n+',text) if x.strip()]

def retrieve_passages(question:str,limit:int=10)->list[str]:
    terms={w for w in normalize(question).split() if len(w)>2}
    ranked=[]
    for i,b in enumerate(blocks_from_text(load_document())):
        words=set(normalize(b).split()); score=len(terms&words)
        if score: ranked.append((score,-i,b))
    ranked.sort(reverse=True)
    return [b for _,_,b in ranked[:limit]]

def is_heading(block: str) -> bool:
    """Recognize standalone document headings without mistaking normal sentences for headings."""
    clean = block.strip()
    letters = ''.join(ch for ch in clean if ch.isalpha())
    return bool(letters) and len(clean) <= 80 and clean == clean.upper()


def sections_from_text(text: str) -> list[tuple[str, list[str]]]:
    """Group each heading with every following paragraph until the next heading."""
    sections: list[tuple[str, list[str]]] = []
    heading = "DOCUMENTO"
    content: list[str] = []
    for block in blocks_from_text(text):
        if is_heading(block):
            if content:
                sections.append((heading, content))
            heading, content = block, []
        else:
            content.append(block)
    if content:
        sections.append((heading, content))
    return sections
