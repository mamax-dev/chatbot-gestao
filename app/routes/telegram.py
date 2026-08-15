import os
from collections import defaultdict,deque
from time import time
from fastapi import APIRouter,BackgroundTasks,Header,HTTPException,Request
from ..telegram_service import answer_message,telegram_request
router=APIRouter();recent=defaultdict(deque)
def allowed(chat):
    now=time();q=recent[str(chat)]
    while q and q[0]<now-60:q.popleft()
    if len(q)>=8:return False
    q.append(now);return True
async def limited(chat):
    try:await telegram_request('sendMessage',{'chat_id':chat,'text':'Recebi várias mensagens seguidas. Aguarde um instante e tente novamente. 🙂'})
    except Exception:pass
@router.post('/telegram/webhook')
async def webhook(request:Request,bg:BackgroundTasks,x_telegram_bot_api_secret_token:str|None=Header(default=None)):
    if x_telegram_bot_api_secret_token!=os.getenv('TELEGRAM_WEBHOOK_SECRET'):raise HTTPException(403,'Webhook não autorizado.')
    m=(await request.json()).get('message') or {};text=m.get('text');chat=(m.get('chat') or {}).get('id')
    if text and chat is not None:bg.add_task(answer_message,chat,text.strip()) if allowed(chat) else bg.add_task(limited,chat)
    return {'ok':True}
