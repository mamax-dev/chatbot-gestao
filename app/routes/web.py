from fastapi import APIRouter
from pydantic import BaseModel,Field
from ..service import answer
router=APIRouter()
class Question(BaseModel):question:str=Field(min_length=2,max_length=500)
@router.get('/health')
async def health():return {'status':'ok'}
@router.post('/api/perguntar')
async def ask(value:Question):return await answer(value.question)
