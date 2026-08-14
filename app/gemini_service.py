import asyncio
import os
from enum import Enum

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .cache import get_cached, set_cached
from .config import AMBIGUOUS, API_BUSY_MESSAGE, GEMINI_MODEL, REFUSAL, TECHNICAL_MESSAGE
from .document import load_document, retrieve_passages
from .local_answers import find_local_answer
from .prompt import SYSTEM_INSTRUCTION


class AnswerStatus(str, Enum):
    ANSWERED = "answered"
    ABSENT = "absent"
    AMBIGUOUS = "ambiguous"


class GroundedAnswer(BaseModel):
    status: AnswerStatus
    answer: str = Field(min_length=1)
    evidence: str = ""


class ApiBusyError(RuntimeError):
    pass


def is_rate_error(exc: Exception) -> bool:
    message = str(exc).upper()
    return (
        getattr(exc, "status_code", None) == 429
        or getattr(exc, "code", None) == 429
        or "429" in message
        or "RESOURCE_EXHAUSTED" in message
        or "RATE LIMIT" in message
        or "QUOTA" in message
    )


def parse_response(response) -> GroundedAnswer:
    if response.parsed is not None:
        return response.parsed
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("O modelo retornou uma resposta vazia.")
    return GroundedAnswer.model_validate_json(text)


def normalize_result(parsed: GroundedAnswer) -> dict:
    status = parsed.status.value
    answer = parsed.answer.strip()
    evidence = parsed.evidence.strip()
    if status == "absent":
        answer, evidence = REFUSAL, ""
    elif status == "ambiguous":
        answer, evidence = AMBIGUOUS, ""
    elif not evidence:
        raise RuntimeError("Resposta sem evidência documental.")
    return {"answer": answer, "evidence": evidence, "status": status, "cached": False, "source": "gemini"}


def select_context(question: str) -> str | None:
    passages = retrieve_passages(question)
    if passages:
        return "\n\n".join(passages)
    return None


def _generate_sync(question: str) -> dict:
    question = question.strip()

    local = find_local_answer(question)
    if local:
        return local

    cached = get_cached(question)
    if cached:
        return cached

    context = select_context(question)
    if not context:
        return {"answer": REFUSAL, "evidence": "", "status": "absent", "cached": False, "source": "retrieval"}

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não foi configurada.")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"DOCUMENTO:\n---\n{context}\n---\nPERGUNTA:\n{question}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=900,
                thinking_config=types.ThinkingConfig(thinking_level="low"),
                response_mime_type="application/json",
                response_schema=GroundedAnswer,
            ),
        )
        final = normalize_result(parse_response(response))
        set_cached(question, final)
        return final
    except Exception as exc:
        print(f"GeminiError type={type(exc).__name__} detail={str(exc).replace(chr(10), ' ')[:500]}")
        if is_rate_error(exc):
            raise ApiBusyError(API_BUSY_MESSAGE) from exc
        raise RuntimeError(TECHNICAL_MESSAGE) from exc


async def generate_answer(question: str) -> dict:
    return await asyncio.to_thread(_generate_sync, question)

# Compatibilidade com o código de rotas existente.
QuotaExceededError = ApiBusyError
