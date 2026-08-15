import os

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .config import GEMINI_MODEL
from .document import load_document


class Answer(BaseModel):
    answer: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)


def ask(question: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    prompt = f"""Use somente o documento.
Responda em até 4 frases curtas, com cordialidade, sem omitir partes da pergunta.
Se a resposta puder ser construída combinando regras do documento, faça a síntese.

DOCUMENTO:
{load_document()}

PERGUNTA:
{question}
"""

    # IMPORTANT: keep a strong reference to the client for the entire request.
    # Creating Client(...).models.generate_content(...) inline can allow the
    # temporary client to be finalized/closed before the request completes.
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Answer,
                max_output_tokens=900,
            ),
        )
        value = response.parsed or Answer.model_validate_json(response.text)
        if not value.evidence:
            return None
        return {
            "answer": value.answer.strip(),
            "evidence": " ".join(value.evidence),
            "status": "answered",
            "cached": False,
            "source": "gemini",
        }
    finally:
        client.close()
