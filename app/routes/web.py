from fastapi import APIRouter,HTTPException,Request
from pydantic import BaseModel,Field
from ..config import MAX_QUESTION_LENGTH
from ..gemini_service import generate_answer
from ..rate_limit import can_use_ai,record_ai_success
router=APIRouter()
class Question(BaseModel):question:str=Field(min_length=2,max_length=MAX_QUESTION_LENGTH)
@router.get('/health')
async def health():return {'status':'ok'}
@router.post('/api/perguntar')
async def ask(payload:Question,request:Request):
    identifier=f"web:{request.client.host if request.client else 'unknown'}"
    if not can_use_ai(identifier):raise HTTPException(status_code=429,detail='Muitas consultas à IA em pouco tempo. Aguarde um minuto.')
    result=await generate_answer(payload.question.strip())
    if result.get('source')=='gemini' and not result.get('cached'):record_ai_success(identifier)
    return result
