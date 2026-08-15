import os,httpx
from .config import PUBLIC_BASE_URL
from .service import answer
async def telegram_request(method,payload):
    token=os.getenv('TELEGRAM_BOT_TOKEN')
    async with httpx.AsyncClient(timeout=30) as c:
        r=await c.post(f'https://api.telegram.org/bot{token}/{method}',json=payload);r.raise_for_status();return r.json()
async def configure_webhook():
    token=os.getenv('TELEGRAM_BOT_TOKEN');secret=os.getenv('TELEGRAM_WEBHOOK_SECRET')
    if token and secret and PUBLIC_BASE_URL:await telegram_request('setWebhook',{'url':f'{PUBLIC_BASE_URL}/telegram/webhook','secret_token':secret,'allowed_updates':['message'],'drop_pending_updates':True})
async def answer_message(chat,text):
    reply=(await answer(text))['answer']
    try:await telegram_request('sendMessage',{'chat_id':chat,'text':reply})
    except Exception as e:print(type(e).__name__)
