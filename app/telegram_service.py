import os
import httpx

from .config import PUBLIC_BASE_URL
from .service import answer

START_MESSAGE = (
    "Olá! Que bom falar com você. Posso ajudar com serviços, preços, "
    "prazos ou atendimento."
)


async def telegram_request(method, payload):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN não configurado.")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"https://api.telegram.org/bot{token}/{method}", json=payload
        )
        response.raise_for_status()
        return response.json()


async def configure_webhook():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if token and secret and PUBLIC_BASE_URL:
        await telegram_request(
            "setWebhook",
            {
                "url": f"{PUBLIC_BASE_URL}/telegram/webhook",
                "secret_token": secret,
                "allowed_updates": ["message"],
                "drop_pending_updates": True,
            },
        )


async def answer_message(chat, text):
    # Telegram commands are control messages, not business questions.
    reply = START_MESSAGE if text.strip().lower().split("@")[0] == "/start" else (await answer(text))["answer"]
    try:
        await telegram_request("sendMessage", {"chat_id": chat, "text": reply})
    except Exception as exc:
        print(type(exc).__name__)
