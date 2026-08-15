def is_retryable_error(exc:Exception)->bool:
    m=str(exc).upper()
    return any(x in m for x in ['408','429','RESOURCE_EXHAUSTED','RATE LIMIT','503','UNAVAILABLE','504','DEADLINE_EXCEEDED','TIMEOUT'])
