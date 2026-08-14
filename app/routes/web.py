from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ..config import API_BUSY_MESSAGE, MAX_QUESTION_LENGTH
from ..gemini_service import ApiBusyError, generate_answer
from ..knowledge_engine import answer_local
from ..rate_limit import can_use_ai, record_ai_success

router = APIRouter()


class Question(BaseModel):
    question: str = Field(min_length=2, max_length=MAX_QUESTION_LENGTH)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/api/perguntar")
async def ask(payload: Question, request: Request):
    question = payload.question.strip()
    local = answer_local(question)
    if local:
        return local

    identifier = request.client.host if request.client else "unknown"
    if not can_use_ai(f"web:{identifier}"):
        raise HTTPException(status_code=429, detail="Muitas consultas à IA em pouco tempo. Aguarde um minuto.")

    try:
        result = await generate_answer(question)
        if result.get("source") == "gemini" and not result.get("cached"):
            record_ai_success(f"web:{identifier}")
        return result
    except ApiBusyError as exc:
        # Falha transitória não entra no limite local.
        raise HTTPException(status_code=503, detail=API_BUSY_MESSAGE) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
