from app.cache import get_cached, set_cached
from app.rate_limit import can_use_ai, record_ai_success
from app.retry_policy import is_retryable_error


def test_errors_are_not_cached():
    set_cached("erro", {"status": "technical_error", "answer": "erro", "evidence": ""})
    assert get_cached("erro") is None


def test_only_successes_count_for_local_rate_limit():
    key = "test-user"
    assert can_use_ai(key)
    for _ in range(6):
        record_ai_success(key)
    assert not can_use_ai(key)


def test_retry_policy():
    assert is_retryable_error(RuntimeError("429 RESOURCE_EXHAUSTED"))
    assert is_retryable_error(RuntimeError("503 UNAVAILABLE"))
    assert not is_retryable_error(RuntimeError("403 PERMISSION_DENIED"))
