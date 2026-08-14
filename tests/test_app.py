import os

os.environ.setdefault("TELEGRAM_WEBHOOK_SECRET", "test_secret")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Solução Prática" in response.text


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_short_question_rejected():
    assert client.post("/api/perguntar", json={"question": "x"}).status_code == 422


def test_webhook_rejects_invalid_secret():
    response = client.post("/telegram/webhook", json={}, headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"})
    assert response.status_code == 403


def test_docs_disabled():
    assert client.get("/docs").status_code == 404
