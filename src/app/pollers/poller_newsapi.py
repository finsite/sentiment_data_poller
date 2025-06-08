"""Polls financial news from NewsAPI and publishes structured sentiment-ready data."""

import datetime
import time
from typing import Any

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config_shared import (
    get_config_value,
    get_polling_interval,
)

from app.config import get_symbols
from app.config_shared import get_config_value, get_polling_interval
from app.message_queue.queue_sender import publish_to_queue
from app.utils.rate_limit import RateLimiter
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

NEWSAPI_URL = "https://newsapi.org/v2/everything"
QUERY = "stocks OR earnings OR finance"

# These config keys must exist in Vault or environment
NEWSAPI_KEY = get_config_value("NEWSAPI_KEY", "")
NEWSAPI_RATE_LIMIT = int(get_config_value("NEWSAPI_RATE_LIMIT", "60"))  # requests
NEWSAPI_WINDOW_SECONDS = int(
    get_config_value("NEWSAPI_WINDOW_SECONDS", "60")
)  # seconds
NEWSAPI_TIMEOUT = int(get_config_value("NEWSAPI_TIMEOUT", "10"))

rate_limiter = RateLimiter(
    max_requests=NEWSAPI_RATE_LIMIT, time_window=NEWSAPI_WINDOW_SECONDS
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.RequestException),
)
def fetch_newsapi_articles(symbol: str) -> list[dict[str, Any]]:
    """Fetches NewsAPI articles for a given stock symbol.

    Args:
        symbol (str): Stock symbol.

    Returns:
        list[dict[str, Any]]: List of article entries.
    """
    rate_limiter.acquire("NewsAPIPoller")
    try:
        logger.debug(f"Querying NewsAPI for: {symbol}")
        params = {
            "q": f"{symbol} {QUERY}",
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 10,
            "apiKey": NEWSAPI_KEY,
        }
        response = requests.get(NEWSAPI_URL, params=params, timeout=NEWSAPI_TIMEOUT)
        response.raise_for_status()
        return response.json().get("articles", [])
    except Exception as e:
        logger.warning(f"NewsAPI fetch failed for {symbol}: {e}")
        return []


def build_payload(symbol: str, article: dict[str, Any]) -> dict[str, Any]:
    """Constructs a queue-ready payload from a NewsAPI article.

    Args:
        symbol (str): Stock symbol.
        article (dict[str, Any]): Raw article entry.

    Returns:
        dict[str, Any]: Payload for publishing.
    """
    return {
        "symbol": symbol,
        "timestamp": article.get("publishedAt", datetime.datetime.utcnow().isoformat()),
        "source": "NewsAPI",
        "data": {
            "headline": article.get("title", ""),
            "summary": article.get("description", ""),
            "url": article.get("url", ""),
            "source_name": article.get("source", {}).get("name", ""),
            "platform": "newsapi",
        },
    }


def run_newsapi_poller() -> None:
    """Main polling loop for NewsAPI."""
    logger.info("📡 NewsAPI poller started")
    interval = get_polling_interval()

    while True:
        all_payloads: list[dict[str, Any]] = []
        symbols = get_symbols()

        for symbol in symbols:
            articles = fetch_newsapi_articles(symbol)
            for article in articles:
                payload = build_payload(symbol, article)
                all_payloads.append(payload)

        if all_payloads:
            publish_to_queue(all_payloads)
            logger.info(f"✅ Published {len(all_payloads)} NewsAPI articles")
        else:
            logger.info("No new articles this round")

        logger.info(f"⏱️ Sleeping for {interval} seconds")
        time.sleep(interval)
