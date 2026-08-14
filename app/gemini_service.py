import asyncio
import os
from enum import Enum

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .cache import get_cached, set_cached
from .config import AMBIGUOUS, GEMINI_MODEL, QUOTA_MESSAGE, REFUSAL, TECHNICAL_MESSAGE
from .document import load_document, retrieve_passages
from .local_answers import find_local_answer, is_broad_question
from .prompt import SYSTEM_INSTRUCTION


class AnswerStatus(str, Enum):
    ANSWERED = "answered"
    ABSENT = "absent"
    AMBIGUOUS = "ambiguous"


class GroundedAnswer(BaseModel):
    status: AnswerStatus
    answer: str = Field(min_length=1)
    evidence: str = ""


class QuotaExceededError(RuntimeError):
    pass


def is_quota_error(exc: Exception) -> bool:
    message = str(exc).upper()
    return (
        getattr(exc, "status_code", None) == 429
        or getattr(exc, "code", None) == 429
        or "429" in message
        or "RESOURCE_EXHAUSTED" in message
        or "QUOTA" in message
        or "RATE LIMIT" in message
    )


def parse_response(response) -> GroundedAnswer:
    if response.parsed is not None:
        return response.parsed
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("O modelo retornou uma resposta vazia.")
    return GroundedAnswer.model_validate_json(text)


def normalize_model_result(parsed: GroundedAnswer) -> dict:
    status = parsed.status.value
    answer = parsed.answer.strip()
    evidence = parsed.evidence.strip()

    if status == AnswerStatus.ABSENT.value:
        answer, evidence = REFUSAL, ""
    elif status == AnswerStatus.AMBIGUOUS.value:
        answer, evidence = AMBIGUOUS, ""
    elif not evidence:
        raise RuntimeError("Resposta fundamentada sem evidência documental.")

    return {
        "answer": answer,
        "evidence": evidence,
        "status": status,
        "cached": False,
        "source": "gemini",
    }


def select_context(question: str) -> str | None:
    if is_broad_question(question):
        return load_document()
    passages = retrieve_passages(question)
    return "\n\n".join(passages) if passages else None


def _generate_sync(question: str) -> dict:
    question = question.strip()

    local_result = find_local_answer(question)
    if local_result:
        return local_result

    cached = get_cached(question)
    if cached:
        return cached

    context = select_context(question)
    if not context:
        result = {
            "answer": REFUSAL,
            "evidence": "",
            "status": AnswerStatus.ABSENT.value,
            "cached": False,
            "source": "retrieval",
        }
        set_cached(question, result)
        return result

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não foi configurada.")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"DOCUMENTO:\n---\n{context}\n---\n\nPERGUNTA DO USUÁRIO:\n{question}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=1200,
                thinking_config=types.ThinkingConfig(thinking_level="low"),
                response_mime_type="application/json",
                response_schema=GroundedAnswer,
            ),
        )
        result = normalize_model_result(parse_response(response))
        set_cached(question, result)
        return result
    except Exception as exc:
        safe_detail = str(exc).replace("\n", " ")[:500]
        print(f"GeminiError type={type(exc).__name__} detail={safe_detail}")
        if is_quota_error(exc):
            raise QuotaExceededError(QUOTA_MESSAGE) from exc
        raise RuntimeError(TECHNICAL_MESSAGE) from exc


async def generate_answer(question: str) -> dict:
    return await asyncio.to_thread(_generate_sync, question)
