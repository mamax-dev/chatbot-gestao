import asyncio
import os
import random
import time
from enum import Enum

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .cache import get_cached, set_cached
from .config import AI_RETRY_ATTEMPTS, AI_RETRY_BASE_SECONDS, AMBIGUOUS, API_BUSY_MESSAGE, GEMINI_MODEL, REFUSAL, TECHNICAL_MESSAGE
from .document import load_document, retrieve_passages
from .knowledge_engine import answer_local
from .prompt import SYSTEM_INSTRUCTION
from .retry_policy import is_retryable_error


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


def is_retryable(exc: Exception) -> bool:
    return is_retryable_error(exc)

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


def call_model(question: str, context: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não foi configurada.")
    client = genai.Client(api_key=api_key)
    last_error = None
    for attempt in range(AI_RETRY_ATTEMPTS):
        try:
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
            return normalize_result(parse_response(response))
        except Exception as exc:
            last_error = exc
            if not is_retryable(exc) or attempt + 1 >= AI_RETRY_ATTEMPTS:
                break
            delay = AI_RETRY_BASE_SECONDS * (2 ** attempt) + random.uniform(0, 0.5)
            time.sleep(delay)
    if last_error and is_retryable(last_error):
        raise ApiBusyError(API_BUSY_MESSAGE) from last_error
    raise RuntimeError(TECHNICAL_MESSAGE) from last_error


def _generate_sync(question: str) -> dict:
    question = question.strip()
    local = answer_local(question)
    if local:
        return local
    cached = get_cached(question)
    if cached:
        return cached
    passages = retrieve_passages(question)
    context = "\n\n".join(passages) if passages else load_document()
    result = call_model(question, context)
    set_cached(question, result)
    return result


async def generate_answer(question: str) -> dict:
    return await asyncio.to_thread(_generate_sync, question)

QuotaExceededError = ApiBusyError
