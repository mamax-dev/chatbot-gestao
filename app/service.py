import asyncio

from .business_config import load_business
from .cache import get, put
from .conversation import local_reply
from .faq import lookup
from .text import normalize

COMPLEX_MARKERS = {
    "explique", "por que", "porque", "resuma", "compare", "relacione",
    "analise", "interprete", "justifique", "sintetize", "como a",
}


def is_open_question(question):
    normalized = normalize(question)
    return any(marker in normalized for marker in COMPLEX_MARKERS)


def sync_answer(question):
    direct = local_reply(question)
    if direct:
        return {
            "answer": direct, "evidence": "", "status": "answered",
            "cached": False, "source": "local",
        }

    # Open/interpretive questions go to cache/Gemini before literal FAQ lookup.
    if is_open_question(question):
        cached = get(question)
        if cached:
            return cached
        try:
            from .gemini import ask
            result = ask(question)
        except Exception as exc:
            print(f"GeminiError {type(exc).__name__}: {str(exc)[:300]}")
            result = None
        if result:
            put(question, result)
            return result
        return {
            "answer": load_business()["conversa"]["indisponibilidade_ia"],
            "evidence": "", "status": "absent", "cached": False,
            "source": "fallback",
        }

    faq = lookup(question)
    if faq:
        return faq

    cached = get(question)
    if cached:
        return cached
    try:
        from .gemini import ask
        result = ask(question)
    except Exception as exc:
        print(f"GeminiError {type(exc).__name__}: {str(exc)[:300]}")
        result = None
    if result:
        put(question, result)
        return result
    return {
        "answer": load_business()["conversa"]["indisponibilidade_ia"],
        "evidence": "", "status": "absent", "cached": False,
        "source": "fallback",
    }


async def answer(question):
    return await asyncio.to_thread(sync_answer, question.strip())
