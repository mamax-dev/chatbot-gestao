import pytest

from app.config import GEMINI_MODEL
from app.gemini import ask


def test_context_model_and_client_lifecycle(fake_gemini):
    assert ask('Pergunta de teste', 'Contexto de teste') == fake_gemini.text
    call = fake_gemini.calls[0]
    assert call['model'] == GEMINI_MODEL
    assert 'CONTEXTO DELIMITADO:\nContexto de teste' in call['contents']
    assert 'PERGUNTA DO USUÁRIO:\nPergunta de teste' in call['contents']
    assert 'Use somente o CONTEXTO.' in call['config'].system_instruction
    assert call['config'].max_output_tokens == 2048
    assert fake_gemini.clients[0].closed


def test_client_closes_after_api_failure(fake_gemini):
    fake_gemini.error = RuntimeError('API indisponível')
    with pytest.raises(RuntimeError, match='API indisponível'):
        ask('q', 'c')
    assert fake_gemini.clients[0].closed
