import os
from collections import defaultdict, deque
from time import time
from fastapi import APIRouter,BackgroundTasks,Header,HTTPException,Request
from ..telegram_service import answer_message, telegram_request
router=APIRouter()
_recent=defaultdict(deque)

def allowed(chat_id):
    now=time();q=_recent[str(chat_id)]
    while q and q[0]<now-60:q.popleft()
    if len(q)>=8:return False
    q.append(now);return True

async def send_limit_message(chat_id):
    try:await telegram_request('sendMessage',{'chat_id':chat_id,'text':'Recebi várias mensagens seguidas. Aguarde um instante e tente novamente. 🙂'})
    except Exception:pass

@router.post('/telegram/webhook')
async def webhook(request:Request,background_tasks:BackgroundTasks,x_telegram_bot_api_secret_token:str|None=Header(default=None)):
    secret=os.getenv('TELEGRAM_WEBHOOK_SECRET')
    if not secret or x_telegram_bot_api_secret_token!=secret:raise HTTPException(status_code=403,detail='Webhook não autorizado.')
    update=await request.json();m=update.get('message') or {};text=m.get('text');chat=(m.get('chat') or {}).get('id')
    if text and chat is not None:
        background_tasks.add_task(answer_message,chat,text.strip()) if allowed(chat) else background_tasks.add_task(send_limit_message,chat)
    return {'ok':True}
