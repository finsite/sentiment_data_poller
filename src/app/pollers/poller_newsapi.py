"""Polls financial news from NewsAPI and publishes structured sentiment-ready data."""

import datetime
import time

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import (
    get_newsapi_key,
    get_newsapi_rate_limit,
    get_newsapi_timeout,
    get_poll_interval,
    get_symbols,
)
from app.message_queue.queue_sender import publish_to_queue
from app.utils.rate_limit import RateLimiter
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

NEWSAPI_URL = "https://newsapi.org/v2/everything"
QUERY = "stocks OR earnings OR finance"

FILL_RATE, CAPACITY = get_newsapi_rate_limit()
rate_limiter = RateLimiter(max_requests=FILL_RATE, time_window=CAPACITY)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.RequestException),
)
def fetch_newsapi_articles(symbol: str, api_key: str) -> list[dict]:
    """Fetches NewsAPI articles for a given stock symbol.

    Parameters
    ----------
    symbol :
        str:
    api_key :
        str:
    symbol :
        str:
    api_key :
        str:
    symbol :
        str:
    api_key :
        str:
    symbol: str :

    api_key: str :


    Returns
    -------

    """
    rate_limiter.acquire("NewsAPIPoller")
    try:
        logger.debug(f"Querying NewsAPI for: {symbol}")
        params = {
            "q": f"{symbol} {QUERY}",
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 10,
            "apiKey": api_key,
        }
        response = requests.get(NEWSAPI_URL, params=params, timeout=get_newsapi_timeout())
        response.raise_for_status()
        return response.json().get("articles", [])
    except Exception as e:
        logger.warning(f"NewsAPI fetch failed for {symbol}: {e}")
        return []


def build_payload(symbol: str, article: dict) -> dict:
    """

    Parameters
    ----------
    symbol :
        str:
    article :
        dict:
    symbol :
        str:
    article :
        dict:
    symbol :
        str:
    article :
        dict:
    symbol: str :

    article: dict :


    Returns
    -------

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
    api_key = get_newsapi_key()
    interval = get_poll_interval()

    while True:
        all_payloads = []
        symbols = get_symbols()

        for symbol in symbols:
            articles = fetch_newsapi_articles(symbol, api_key)
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
