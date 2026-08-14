from app.cache import get_cached, set_cached


def test_cache_stores_success_only():
    set_cached("pergunta", {"answer": "ok", "status": "answered", "evidence": "x"})
    assert get_cached("pergunta")["cached"] is True
    set_cached("erro", {"answer": "erro", "status": "technical_error"})
    assert get_cached("erro") is None
