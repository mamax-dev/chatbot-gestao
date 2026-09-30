from app import cache
from app.service import sync_answer
from tests.test_routing import COMPARISON, COMPARISON_REPLY


def test_cache_expiration_causes_new_generation(fake_gemini, monkeypatch):
    fake_gemini.text = COMPARISON_REPLY
    now = [100.0]
    monkeypatch.setattr(cache.time, 'time', lambda: now[0])
    assert sync_answer(COMPARISON)['source'] == 'gemini'
    now[0] += cache.CACHE_TTL_SECONDS + 1
    assert sync_answer(COMPARISON)['source'] == 'gemini'
    assert len(fake_gemini.calls) == 2


def test_model_change_invalidates_cache(fake_gemini, monkeypatch):
    fake_gemini.text = COMPARISON_REPLY
    sync_answer(COMPARISON)
    monkeypatch.setattr(cache, 'GEMINI_MODEL', 'another-test-model')
    assert sync_answer(COMPARISON)['source'] == 'gemini'
    assert len(fake_gemini.calls) == 2


def test_prompt_change_invalidates_cache(fake_gemini, monkeypatch):
    fake_gemini.text = COMPARISON_REPLY
    sync_answer(COMPARISON)
    monkeypatch.setattr(cache, 'PROMPT_VERSION', 'test-new-prompt')
    assert sync_answer(COMPARISON)['source'] == 'gemini'
    assert len(fake_gemini.calls) == 2


def test_business_change_invalidates_cache(fake_gemini, monkeypatch):
    fake_gemini.text = COMPARISON_REPLY
    sync_answer(COMPARISON)
    from app.business_config import load_business
    config = dict(load_business(), schema_version='test-new-version')
    monkeypatch.setattr(cache, 'load_business', lambda: config)
    assert sync_answer(COMPARISON)['source'] == 'gemini'
    assert len(fake_gemini.calls) == 2
