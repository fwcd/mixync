def truncate(s: str, max_len: int, suffix: str='...') -> str:
    actual_max_len = max_len - len(suffix)
    return s if len(s) < actual_max_len else s[:actual_max_len] + suffix
