import os,httpx
from .config import PUBLIC_BASE_URL,TECHNICAL_MESSAGE
from .gemini_service import generate_answer
from .input_policy import MAX_INPUT_CHARS
async def telegram_request(method,payload):
    token=os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:raise RuntimeError('TELEGRAM_BOT_TOKEN não foi configurado.')
    async with httpx.AsyncClient(timeout=30) as c:
        r=await c.post(f'https://api.telegram.org/bot{token}/{method}',json=payload);r.raise_for_status();return r.json()
async def configure_webhook():
    secret=os.getenv('TELEGRAM_WEBHOOK_SECRET');token=os.getenv('TELEGRAM_BOT_TOKEN')
    if token and secret and PUBLIC_BASE_URL:await telegram_request('setWebhook',{'url':f'{PUBLIC_BASE_URL}/telegram/webhook','secret_token':secret,'allowed_updates':['message'],'drop_pending_updates':True})
async def answer_message(chat_id,text):
    try:reply='Olá! Posso informar preços, prazos, pagamentos e condições dos serviços.' if text=='/start' else (await generate_answer(text, channel='telegram'))['answer']
    except Exception:reply=TECHNICAL_MESSAGE
    try:await telegram_request('sendMessage',{'chat_id':chat_id,'text':reply})
    except Exception as e:print(f'TelegramSendError type={type(e).__name__}')
