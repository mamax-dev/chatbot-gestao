import os
import httpx
from .config import API_BUSY_MESSAGE, PUBLIC_BASE_URL, TECHNICAL_MESSAGE
from .gemini_service import ApiBusyError, generate_answer

async def telegram_request(method: str, payload: dict) -> dict:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN não foi configurado.")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"https://api.telegram.org/bot{token}/{method}", json=payload)
        response.raise_for_status()
        return response.json()

async def configure_webhook() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if not token or not secret or not PUBLIC_BASE_URL:
        return
    await telegram_request("setWebhook", {
        "url": f"{PUBLIC_BASE_URL}/telegram/webhook",
        "secret_token": secret,
        "allowed_updates": ["message"],
        "drop_pending_updates": True,
    })

async def answer_message(chat_id: int, text: str) -> None:
    if text == "/start":
        reply = "Olá! Posso informar preços, prazos, pagamentos e condições dos serviços."
    else:
        try:
            reply = (await generate_answer(text))["answer"]
        except ApiBusyError:
            reply = API_BUSY_MESSAGE
        except Exception:
            reply = TECHNICAL_MESSAGE
    try:
        await telegram_request("sendMessage", {"chat_id": chat_id, "text": reply})
    except Exception as exc:
        print(f"TelegramSendError type={type(exc).__name__}")
