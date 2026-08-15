import asyncio
from .business_config import load_business
from .cache import get,put
from .conversation import local_reply
from .faq import lookup
def sync_answer(question):
    direct=local_reply(question)
    if direct:return {'answer':direct,'evidence':'','status':'answered','cached':False,'source':'local'}
    faq=lookup(question)
    if faq:return faq
    cached=get(question)
    if cached:return cached
    try:
        from .gemini import ask
        result=ask(question)
    except Exception as exc:
        print(f'GeminiError {type(exc).__name__}: {str(exc)[:300]}');result=None
    if result:put(question,result);return result
    return {'answer':load_business()['conversa']['indisponibilidade_ia'],'evidence':'','status':'absent','cached':False,'source':'fallback'}
async def answer(question):return await asyncio.to_thread(sync_answer,question.strip())
