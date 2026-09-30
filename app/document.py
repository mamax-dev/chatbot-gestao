from functools import lru_cache
from .config import DOCUMENT_PATH
@lru_cache(maxsize=1)
def load_document():
    from striprtf.striprtf import rtf_to_text
    text=rtf_to_text(DOCUMENT_PATH.read_text(encoding='latin-1')).strip()
    if not text:raise RuntimeError('O arquivo instrucoes.rtf está vazio.')
    return text
