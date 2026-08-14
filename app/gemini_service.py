import asyncio
import os

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .cache import get_cached, set_cached
from .config import AMBIGUOUS, GEMINI_MODEL, QUOTA_MESSAGE, REFUSAL, TECHNICAL_MESSAGE
from .document import retrieve_passages


class GroundedAnswer(BaseModel):
    status: str = Field(description="answered, absent ou ambiguous")
    answer: str
    evidence: str = ""


class QuotaExceededError(RuntimeError):
    pass


SYSTEM_INSTRUCTION = f"""
Você é um assistente de consulta documental.
Use exclusivamente os TRECHOS fornecidos.
Não use conhecimento externo nem complete lacunas.
Se a informação estiver ausente, use status absent e responda exatamente: {REFUSAL}
Se a pergunta for ambígua, use status ambiguous e responda: {AMBIGUOUS}
Em evidence, copie uma passagem curta dos TRECHOS que sustente a resposta. Para absent ou ambiguous, deixe evidence vazio.
Responda em português, com clareza e concisão.
"""


def _generate_sync(question: str) -> dict:
    cached = get_cached(question)
    if cached:
        return cached

    passages = retrieve_passages(question)
    if not passages:
        result = {"answer": REFUSAL, "evidence": "", "status": "absent", "cached": False}
        set_cached(question, result)
        return result

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não foi configurada.")

    context = "\n\n".join(f"TRECHO {i + 1}: {text}" for i, text in enumerate(passages))
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"{context}\n\nPERGUNTA: {question}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=300,
                response_mime_type="application/json",
                response_schema=GroundedAnswer,
            ),
        )
        parsed = response.parsed
        if parsed is None:
            parsed = GroundedAnswer.model_validate_json(response.text)
        result = {
            "answer": parsed.answer.strip(),
            "evidence": parsed.evidence.strip(),
            "status": parsed.status.strip().lower(),
            "cached": False,
        }
        set_cached(question, result)
        return result
    except Exception as exc:
        message = str(exc)
        if "429" in message or "RESOURCE_EXHAUSTED" in message:
            raise QuotaExceededError(QUOTA_MESSAGE) from exc
        raise RuntimeError(TECHNICAL_MESSAGE) from exc


async def generate_answer(question: str) -> dict:
    return await asyncio.to_thread(_generate_sync, question)
