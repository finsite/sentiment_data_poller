"""Polls Benzinga Newswire API for real-time sentiment-rich headlines."""

import datetime
import time
import requests

from app.config import get_symbols
from app.config_shared import get_config_value, get_polling_interval
from app.message_queue.queue_sender import publish_to_queue
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

BENZINGA_API_KEY = get_config_value("BENZINGA_API_KEY", "")
BENZINGA_NEWS_URL = "https://api.benzinga.com/api/v2/news"


def fetch_benzinga_news(symbol: str) -> list[dict]:
    """Fetch news articles from Benzinga Newswire API for a given symbol."""
    try:
        params = {
            "token": BENZINGA_API_KEY,
            "symbols": symbol,
            "pagesize": 10,
        }
        response = requests.get(BENZINGA_NEWS_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"❌ Failed to fetch Benzinga news for {symbol}: {e}")
        return []


def build_payload(symbol: str, item: dict) -> dict:
    """Standardize a Benzinga article item for publishing to the queue."""
    return {
        "symbol": symbol,
        "timestamp": item.get("created", datetime.datetime.utcnow().isoformat()),
        "source": "Benzinga",
        "data": {
            "headline": item.get("title", ""),
            "summary": item.get("summary", ""),
            "url": item.get("url", ""),
            "platform": "benzinga",
            "sentiment": item.get("sentiment", ""),
        },
    }


def run_benzinga_poller() -> None:
    """Main polling loop for Benzinga Newswire."""
    logger.info("📡 Benzinga poller started")
    interval = get_polling_interval()

    while True:
        all_payloads = []
        symbols = get_symbols()

        for symbol in symbols:
            news_items = fetch_benzinga_news(symbol)
            for item in news_items:
                payload = build_payload(symbol, item)
                all_payloads.append(payload)

        if all_payloads:
            publish_to_queue(all_payloads)
            logger.info(f"✅ Published {len(all_payloads)} Benzinga news entries")
        else:
            logger.info("No news articles this round")

        logger.info(f"⏱️ Sleeping for {interval} seconds")
        time.sleep(interval)
