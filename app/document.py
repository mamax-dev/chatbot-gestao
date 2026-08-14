import re
import unicodedata
from functools import lru_cache

from .config import DOCUMENT_PATH


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


@lru_cache(maxsize=1)
def load_document() -> str:
    from striprtf.striprtf import rtf_to_text
    if not DOCUMENT_PATH.exists():
        raise RuntimeError("Arquivo instrucoes.rtf não encontrado.")
    text = rtf_to_text(DOCUMENT_PATH.read_text(encoding="latin-1")).strip()
    if not text:
        raise RuntimeError("O arquivo instrucoes.rtf está vazio.")
    return text


def blocks_from_text(text: str) -> list[str]:
    blocks = [item.strip() for item in re.split(r"\n+", text) if item.strip()]
    # Se o arquivo vier com poucas quebras, também separa sentenças longas.
    if len(blocks) < 8:
        blocks = [item.strip() for item in re.split(r"(?<=[.!?])\s+", text) if item.strip()]
    return blocks


def retrieve_passages(question: str, limit: int = 7) -> list[str]:
    terms = {word for word in normalize(question).split() if len(word) > 2}
    ranked = []
    for index, block in enumerate(blocks_from_text(load_document())):
        words = set(normalize(block).split())
        score = len(terms & words)
        if score:
            ranked.append((score, -index, block))
    ranked.sort(reverse=True)
    return [item[2] for item in ranked[:limit]]
