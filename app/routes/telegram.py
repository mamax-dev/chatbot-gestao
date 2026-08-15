import os
from fastapi import APIRouter,BackgroundTasks,Header,HTTPException,Request
from ..telegram_service import answer_message
router=APIRouter()
@router.post('/telegram/webhook')
async def webhook(request:Request,background_tasks:BackgroundTasks,x_telegram_bot_api_secret_token:str|None=Header(default=None)):
    secret=os.getenv('TELEGRAM_WEBHOOK_SECRET')
    if not secret or x_telegram_bot_api_secret_token!=secret:raise HTTPException(status_code=403,detail='Webhook não autorizado.')
    update=await request.json();m=update.get('message') or {};text=m.get('text');chat=(m.get('chat') or {}).get('id')
    if text and chat is not None:background_tasks.add_task(answer_message,chat,text.strip())
    return {'ok':True}
