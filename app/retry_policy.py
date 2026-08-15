def is_retryable_error(exc):return any(x in str(exc).upper() for x in ['408','429','503','504','UNAVAILABLE','TIMEOUT','RESOURCE_EXHAUSTED'])
