import json
import os
import random
import time
from enum import Enum

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .business_config import load_business
from .config import GEMINI_MODEL


class Status(str, Enum):
    ANSWERED = "answered"
    ABSENT = "absent"


class Answer(BaseModel):
    status: Status = Field(description="answered quando a configuração permite responder; absent somente sem base relacionada")
    answer: str = Field(min_length=1, description="Resposta cordial, objetiva e com no máximo quatro frases")
    evidence: list[str] = Field(min_length=1, description="Trechos literais curtos copiados da configuração")


def _retryable(exc: Exception) -> bool:
    message = str(exc).upper()
    return any(code in message for code in ("408", "429", "500", "503", "504", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "TIMEOUT"))


def _generate(client, question: str, config_text: str) -> Answer:
    prompt = f"""CONFIGURAÇÃO EMPRESARIAL:
{config_text}

PERGUNTA:
{question}

Use somente a configuração empresarial.
Responda com cordialidade e objetividade, em até quatro frases.
Perguntas de síntese devem relacionar informações de partes diferentes da configuração.
Use status answered quando existir base relacionada.
Use status absent somente quando não existir informação relacionada.
Em evidence, copie literalmente trechos curtos da configuração que sustentem a resposta.
"""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Answer,
            max_output_tokens=900,
            temperature=0.2,
        ),
    )
    return response.parsed or Answer.model_validate_json(response.text)


def ask(question: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada")

    config_text = json.dumps(load_business(), ensure_ascii=False, sort_keys=True)
    client = genai.Client(api_key=api_key)
    try:
        for attempt in range(3):
            try:
                value = _generate(client, question, config_text)
                if value.status == Status.ABSENT:
                    return None
                return {
                    "answer": value.answer.strip(),
                    "evidence": " ".join(value.evidence),
                    "status": "answered",
                    "cached": False,
                    "source": "gemini",
                }
            except Exception as exc:
                if not _retryable(exc) or attempt == 2:
                    raise
                time.sleep((2 ** attempt) + random.uniform(0, 0.4))
    finally:
        client.close()
