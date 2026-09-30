from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.cache import clear


@pytest.fixture(autouse=True)
def isolated_cache():
    clear()
    yield
    clear()


@pytest.fixture
def fake_gemini(monkeypatch):
    """Simula apenas a API externa; roteamento e validação são reais."""
    from app import gemini

    state = SimpleNamespace(
        text='Resposta completa.', reason='STOP', error=None,
        calls=[], clients=[],
    )

    class Client:
        def __init__(self, **kwargs):
            self.closed = False
            self.models = self
            state.clients.append(self)

        def generate_content(self, **kwargs):
            state.calls.append(kwargs)
            if state.error:
                raise state.error
            return SimpleNamespace(
                text=state.text,
                candidates=[SimpleNamespace(finish_reason=state.reason)],
            )

        def close(self):
            self.closed = True

    monkeypatch.setenv('GEMINI_API_KEY', 'test-only-not-a-real-key')
    monkeypatch.setattr(gemini.genai, 'Client', Client)
    return state


@pytest.fixture
def web_client(monkeypatch):
    # Não registrar webhook nem enviar mensagens reais durante os testes.
    monkeypatch.delenv('TELEGRAM_BOT_TOKEN', raising=False)
    from app.main import app
    from app.routes.telegram import recent
    recent.clear()
    with TestClient(app) as client:
        yield client
    recent.clear()
