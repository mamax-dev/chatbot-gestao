import re
import unicodedata
from functools import lru_cache

from striprtf.striprtf import rtf_to_text

from .config import DOCUMENT_PATH


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


@lru_cache(maxsize=1)
def load_document() -> str:
    if not DOCUMENT_PATH.exists():
        raise RuntimeError("Arquivo instrucoes.rtf não encontrado.")
    content = rtf_to_text(DOCUMENT_PATH.read_text(encoding="latin-1")).strip()
    if not content:
        raise RuntimeError("O arquivo instrucoes.rtf está vazio.")
    return content


def paragraphs() -> list[str]:
    text = load_document()
    return [p.strip() for p in re.split(r"\n+", text) if len(p.strip()) > 20]


def retrieve_passages(question: str, limit: int = 5) -> list[str]:
    terms = {term for term in normalize(question).split() if len(term) > 2}
    ranked = []
    for index, paragraph in enumerate(paragraphs()):
        words = set(normalize(paragraph).split())
        score = len(terms & words)
        if score:
            ranked.append((score, -index, paragraph))
    ranked.sort(reverse=True)
    return [item[2] for item in ranked[:limit]]
