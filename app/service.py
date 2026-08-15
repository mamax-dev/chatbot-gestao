import asyncio
from .cache import get,put
from .faq import lookup
from .policy import local_reply
NOT_FOUND='Não encontrei essa informação nas orientações disponíveis. Posso ajudar com serviços, preços, prazos ou pagamentos. 🙂'
def sync_answer(question):
    direct=local_reply(question)
    if direct:return {'answer':direct,'evidence':'','status':'answered','cached':False,'source':'local'}
    faq=lookup(question)
    if faq:return {'answer':faq.answer,'evidence':faq.evidence,'status':'answered','cached':False,'source':'faq'}
    cached=get(question)
    if cached:return cached
    try:
        from .gemini import ask
        result=ask(question)
    except Exception as exc:
        print(f'GeminiError {type(exc).__name__}: {str(exc)[:200]}');result=None
    if result:put(question,result);return result
    return {'answer':NOT_FOUND,'evidence':'','status':'absent','cached':False,'source':'fallback'}
async def answer(question):return await asyncio.to_thread(sync_answer,question.strip())
