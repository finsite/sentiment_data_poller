import os


def get_newsapi_rate_limit() -> tuple[int, int]:
    """Returns the rate limit and burst capacity for NewsAPI requests."""
    return (
        int(os.getenv("NEWSAPI_FILL_RATE", "5")),
        int(os.getenv("NEWSAPI_CAPACITY", "5")),
    )


def get_newsapi_timeout() -> int:
    """Returns the timeout (in seconds) for NewsAPI HTTP requests."""
    return int(os.getenv("NEWSAPI_TIMEOUT", "10"))


def get_symbols() -> list[str]:
    """
    Retrieve a list of stock symbols from the SYMBOLS env var or Vault (if integrated
    later).

    Returns:
        list[str]: List of uppercase stock symbols.
    """
    symbols = os.getenv("SYMBOLS", "")
    if not symbols:
        raise ValueError("SYMBOLS environment variable is not set")

    return [s.strip().upper() for s in symbols.split(",") if s.strip()]
