import pytest

from app.gemini import ask


def test_normal_text(fake_gemini):
    assert ask('q', 'c') == 'Resposta completa.'


def test_empty_rejected(fake_gemini):
    fake_gemini.text = ''
    with pytest.raises(RuntimeError, match='vazia'):
        ask('q', 'c')


def test_truncated_rejected(fake_gemini):
    fake_gemini.reason = 'MAX_TOKENS'
    with pytest.raises(RuntimeError, match='limite de tokens'):
        ask('q', 'c')


def test_insufficient_returns_none(fake_gemini):
    fake_gemini.text = 'INFORMAÇÃO INSUFICIENTE.'
    assert ask('q', 'c') is None
