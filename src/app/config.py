import os


def get_newsapi_rate_limit() -> tuple[int, int]:
    """Returns the rate limit and burst capacity for NewsAPI requests.
    """
    return (
        int(os.getenv("NEWSAPI_FILL_RATE", "5")),
        int(os.getenv("NEWSAPI_CAPACITY", "5")),
    )


def get_newsapi_timeout() -> int:
    """Returns the timeout (in seconds) for NewsAPI HTTP requests.
    """
    return int(os.getenv("NEWSAPI_TIMEOUT", "10"))
