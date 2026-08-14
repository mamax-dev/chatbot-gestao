import os

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from ..rate_limit import can_use_ai
from ..telegram_service import answer_message

router = APIRouter()


@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if not secret or x_telegram_bot_api_secret_token != secret:
        raise HTTPException(status_code=403, detail="Webhook não autorizado.")
    update = await request.json()
    message = update.get("message") or {}
    text = message.get("text")
    chat_id = (message.get("chat") or {}).get("id")
    if text and chat_id is not None:
        # O serviço decide local/Gemini; falhas transitórias não bloqueiam o webhook.
        background_tasks.add_task(answer_message, chat_id, text.strip())
    return {"ok": True}
