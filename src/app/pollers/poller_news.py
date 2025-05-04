"""Polls financial news from NewsAPI and publishes structured sentiment-ready data to a
queue."""

import datetime
import os
import time

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_symbols  # ✅ fetch symbols from Vault/env
from app.config import get_newsapi_rate_limit, get_newsapi_timeout
from app.message_queue.queue_sender import publish_to_queue
from app.utils.rate_limit import RateLimiter
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

# NewsAPI configuration
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSAPI_URL = "https://newsapi.org/v2/everything"
QUERY = os.getenv("NEWSAPI_QUERY", "stocks OR earnings OR finance")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))  # 5 minutes

# Set up rate limiter per API
FILL_RATE, CAPACITY = get_newsapi_rate_limit()
rate_limiter = RateLimiter(max_requests=FILL_RATE, time_window=CAPACITY)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.RequestException),
)
def fetch_news(symbol: str) -> list[dict]:
    """
    Fetch news articles for a given stock symbol from NewsAPI.

    Args:
      symbol: str:

    Returns:
    """
    rate_limiter.acquire("NewsPoller")

    try:
        logger.info(f"Fetching news for: {symbol}")
        params = {
            "q": f"{symbol} {QUERY}",
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 10,
            "apiKey": NEWSAPI_KEY,
        }
        response = requests.get(NEWSAPI_URL, params=params, timeout=get_newsapi_timeout())
        response.raise_for_status()
        return response.json().get("articles", [])
    except Exception as e:
        logger.error(f"Failed to fetch news for {symbol}: {e}")
        return []


def build_payload(symbol: str, article: dict) -> dict:
    """
    Construct output payload from article data.

    Args:
      symbol: str:
      article: dict:

    Returns:
    """
    return {
        "symbol": symbol,
        "timestamp": article.get("publishedAt", datetime.datetime.utcnow().isoformat()),
        "source": "NewsAPI",
        "data": {
            "headline": article.get("title", ""),
            "summary": article.get("description", ""),
            "raw": article.get("content", ""),
            "url": article.get("url", ""),
            "source_name": article.get("source", {}).get("name", ""),
        },
    }


def run_news_poller() -> None:
    """Main polling loop for NewsAPI."""
    logger.info("📡 NewsAPI poller started")

    while True:
        all_payloads = []
        symbols = get_symbols()  # ✅ Fetch dynamically each run

        for symbol in symbols:
            articles = fetch_news(symbol)
            for article in articles:
                payload = build_payload(symbol, article)
                all_payloads.append(payload)

        if all_payloads:
            publish_to_queue(all_payloads)
            logger.info(f"✅ Published {len(all_payloads)} news articles to queue")
        else:
            logger.info("No articles found this round")

        logger.info(f"⏱️ Sleeping for {POLL_INTERVAL} seconds")
        time.sleep(POLL_INTERVAL)
