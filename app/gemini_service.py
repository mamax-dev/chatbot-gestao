import asyncio
import os
import random
import time
from enum import Enum

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .cache import get_cached, set_cached
from .config import (
    AI_RETRY_ATTEMPTS,
    AI_RETRY_BASE_SECONDS,
    AMBIGUOUS,
    API_BUSY_MESSAGE,
    GEMINI_MODEL,
    REFUSAL,
    TECHNICAL_MESSAGE,
)
from .document import load_document, retrieve_passages
from .knowledge_engine import answer_local
from .prompt import SYSTEM_INSTRUCTION
from .retry_policy import is_retryable_error
from .synthesis_policy import is_synthesis_question, synthesis_retry_prompt


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

    if status == AnswerStatus.ABSENT.value:
        answer, evidence = REFUSAL, ""
    elif status == AnswerStatus.AMBIGUOUS.value:
        answer, evidence = AMBIGUOUS, ""
    elif not evidence:
        raise RuntimeError("Resposta sem evidência documental.")

    return {
        "answer": answer,
        "evidence": evidence,
        "status": status,
        "cached": False,
        "source": "gemini",
    }


def _generate_once(client, contents: str) -> GroundedAnswer:
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=1200,
            thinking_config=types.ThinkingConfig(thinking_level="low"),
            response_mime_type="application/json",
            response_schema=GroundedAnswer,
        ),
    )
    return parse_response(response)


def _call_with_transient_retry(client, contents: str) -> GroundedAnswer:
    last_error = None
    attempts = max(1, AI_RETRY_ATTEMPTS)
    for attempt in range(attempts):
        try:
            return _generate_once(client, contents)
        except Exception as exc:
            last_error = exc
            if not is_retryable_error(exc) or attempt + 1 >= attempts:
                break
            delay = AI_RETRY_BASE_SECONDS * (2 ** attempt) + random.uniform(0, 0.5)
            time.sleep(delay)
    if last_error and is_retryable_error(last_error):
        raise ApiBusyError(API_BUSY_MESSAGE) from last_error
    raise RuntimeError(TECHNICAL_MESSAGE) from last_error


def call_model(question: str, context: str, full_document: str, synthesis: bool) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não foi configurada.")

    client = genai.Client(api_key=api_key)
    contents = f"DOCUMENTO:\n---\n{context}\n---\nPERGUNTA:\n{question}"
    parsed = _call_with_transient_retry(client, contents)

    # A recusa em uma pergunta de síntese é revisada uma única vez com o documento completo.
    if synthesis and parsed.status == AnswerStatus.ABSENT:
        parsed = _call_with_transient_retry(
            client,
            synthesis_retry_prompt(question, full_document),
        )

    return normalize_result(parsed)


def _generate_sync(question: str) -> dict:
    question = question.strip()

    local = answer_local(question)
    if local:
        return local

    synthesis = is_synthesis_question(question)

    # Respostas antigas marcadas como "absent" não podem bloquear uma nova síntese.
    cached = get_cached(question)
    if cached and not (synthesis and cached.get("status") == "absent"):
        return cached

    full_document = load_document()
    if synthesis:
        context = full_document
    else:
        passages = retrieve_passages(question)
        context = "\n\n".join(passages) if passages else full_document

    result = call_model(question, context, full_document, synthesis)
    set_cached(question, result)
    return result


async def generate_answer(question: str) -> dict:
    return await asyncio.to_thread(_generate_sync, question)


QuotaExceededError = ApiBusyError
