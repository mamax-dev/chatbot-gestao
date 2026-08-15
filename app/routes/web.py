from fastapi import APIRouter,Request
from pydantic import BaseModel,Field
from ..gemini_service import generate_answer
router=APIRouter()
class Question(BaseModel):question:str=Field(min_length=2,max_length=500)
@router.get('/health')
async def health():return {'status':'ok'}
@router.post('/api/perguntar')
async def ask(payload:Question,request:Request):return await generate_answer(payload.question)
