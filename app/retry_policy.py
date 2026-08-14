def is_retryable_error(exc: Exception) -> bool:
    message = str(exc).upper()
    return any(token in message for token in [
        "429", "RESOURCE_EXHAUSTED", "RATE LIMIT",
        "503", "UNAVAILABLE", "504", "DEADLINE_EXCEEDED",
    ])
