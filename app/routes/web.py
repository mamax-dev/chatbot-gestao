from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ..config import MAX_QUESTION_LENGTH, QUOTA_MESSAGE
from ..gemini_service import QuotaExceededError, generate_answer
from ..rate_limit import allow

router = APIRouter()


class Question(BaseModel):
    question: str = Field(min_length=2, max_length=MAX_QUESTION_LENGTH)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/api/perguntar")
async def ask(payload: Question, request: Request):
    identifier = request.client.host if request.client else "unknown"
    if not allow(f"web:{identifier}"):
        raise HTTPException(status_code=429, detail="Muitas perguntas em pouco tempo. Aguarde um minuto.")
    try:
        return await generate_answer(payload.question.strip())
    except QuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=QUOTA_MESSAGE) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
