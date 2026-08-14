from .local_answers import find_local_answer
import asyncio
import os

from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError

from .cache import get_cached, set_cached
from .config import AMBIGUOUS, GEMINI_MODEL, QUOTA_MESSAGE, REFUSAL, TECHNICAL_MESSAGE
from .document import normalize, retrieve_passages


class GroundedAnswer(BaseModel):
    status: str = Field(description="answered, absent ou ambiguous")
    answer: str
    evidence: str = ""


class QuotaExceededError(RuntimeError):
    pass


SERVICE_TERMS = {
    "diagnostico", "formatacao", "sistema", "limpeza", "rede",
    "wifi", "roteador", "visita", "tecnica", "computador",
}

ABSENT_TOPICS = {
    "celular", "celulares", "smartphone", "smartphones",
    "venda de computador", "venda de computadores",
    "vender computador", "vender computadores",
    "recuperacao de dados", "desconto promocional",
    "descontos promocionais", "desconto para estudante",
    "desconto para estudantes", "fora de sao paulo",
}

GENERIC_AMBIGUOUS_PHRASES = {
    "quanto custa", "quanto custa o servico", "qual o preco",
    "qual o preco do servico", "quanto tempo demora", "qual o prazo",
    "esta incluido", "tem garantia", "voces fazem esse servico",
    "posso parcelar isso",
}

SYSTEM_INSTRUCTION = f"""
Você é um assistente de consulta documental.
Use exclusivamente os TRECHOS fornecidos.
Não use conhecimento externo nem complete lacunas.
Se a informação estiver ausente, use status absent e responda exatamente: {REFUSAL}
Se a pergunta for ambígua, use status ambiguous e responda: {AMBIGUOUS}
Em evidence, copie uma passagem curta dos TRECHOS que sustente a resposta.
Para absent ou ambiguous, deixe evidence vazio.
Responda em português, com clareza e concisão.
"""


def classify_before_model(question: str) -> dict | None:
    normalized = normalize(question)

    if any(topic in normalized for topic in ABSENT_TOPICS):
        return {"answer": REFUSAL, "evidence": "", "status": "absent", "cached": False}

    words = set(normalized.split())
    has_specific_service = bool(words & SERVICE_TERMS)
    if normalized in GENERIC_AMBIGUOUS_PHRASES and not has_specific_service:
        return {"answer": AMBIGUOUS, "evidence": "", "status": "ambiguous", "cached": False}

    return None


def is_quota_error(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    code = getattr(exc, "code", None)
    message = str(exc).upper()
    return (
        status_code == 429 or code == 429 or "429" in message
        or "RESOURCE_EXHAUSTED" in message or "QUOTA" in message
        or "RATE LIMIT" in message
    )


def parse_response(response) -> GroundedAnswer:
    if response.parsed is not None:
        return response.parsed

    text = (response.text or "").strip()
    if text:
        return GroundedAnswer.model_validate_json(text)

    raise RuntimeError("O modelo retornou uma resposta vazia.")


def _generate_sync(question: str) -> dict:
    local_result = find_local_answer(question)
    
    if local_result:
    return local_result

    cached = get_cached(question)
    
    if cached:
        return cached
        
    direct_result = classify_before_model(question)
    
    if direct_result:
        set_cached(question, direct_result)
        return direct_result

    passages = retrieve_passages(question)
    
    if not passages:
        result = {
            "answer": REFUSAL,
            "evidence": "",
            "status": "absent",
            "cached": False
        }
        set_cached(question, result)
        return result

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não foi configurada.")

    context = "\n\n".join(
        f"TRECHO {index + 1}: {text}" for index, text in enumerate(passages)
    )
    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"{context}\n\nPERGUNTA: {question}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=900,
                thinking_config=types.ThinkingConfig(thinking_level="low"),
                response_mime_type="application/json",
                response_schema=GroundedAnswer,
            ),
        )

        parsed = parse_response(response)
        status = parsed.status.strip().lower()
        answer = parsed.answer.strip()
        evidence = parsed.evidence.strip()

        if status == "absent":
            answer, evidence = REFUSAL, ""
        elif status == "ambiguous":
            answer, evidence = AMBIGUOUS, ""
        elif status != "answered":
            raise ValidationError.from_exception_data("GroundedAnswer", [])

        result = {
            "answer": answer,
            "evidence": evidence,
            "status": status,
            "cached": False,
        }
        set_cached(question, result)
        return result

    except Exception as exc:
        error_type = type(exc).__name__
        error_message = str(exc).replace("\n", " ")[:500]
        print(f"GeminiError type={error_type} detail={error_message}")

        if is_quota_error(exc):
            raise QuotaExceededError(QUOTA_MESSAGE) from exc
        raise RuntimeError(TECHNICAL_MESSAGE) from exc


async def generate_answer(question: str) -> dict:
    return await asyncio.to_thread(_generate_sync, question)
