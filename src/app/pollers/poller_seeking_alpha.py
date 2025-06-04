"""Polls Seeking Alpha RSS feeds for articles related to each stock symbol."""

import datetime
import time
import urllib.parse

import feedparser

from app.config import get_poll_interval, get_symbols
from app.message_queue.queue_sender import publish_to_queue
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

BASE_RSS_URL = "https://seekingalpha.com/api/sa/combined/{symbol}.xml"


def fetch_seeking_alpha_feed(symbol: str) -> list[dict]:
    """Fetch and parse Seeking Alpha RSS feed for the given symbol.

    :param symbol: str:
    :param symbol: str:
    :param symbol: str: 

    """
    try:
        encoded_symbol = urllib.parse.quote_plus(symbol)
        url = BASE_RSS_URL.format(symbol=encoded_symbol)
        feed = feedparser.parse(url)

        results = []
        for entry in feed.entries:
            results.append(
                {
                    "timestamp": entry.get("published", datetime.datetime.utcnow().isoformat()),
                    "headline": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "source_name": "Seeking Alpha",
                }
            )

        logger.debug(f"Fetched {len(results)} Seeking Alpha items for {symbol}")
        return results

    except Exception as e:
        logger.warning(f"Failed to fetch Seeking Alpha feed for {symbol}: {e}")
        return []


def build_payload(symbol: str, article: dict) -> dict:
    """

    :param symbol: str:
    :param article: dict:
    :param symbol: str:
    :param article: dict:
    :param symbol: str: 
    :param article: dict: 

    """
    return {
        "symbol": symbol,
        "timestamp": article["timestamp"],
        "source": "SeekingAlpha",
        "data": {
            "headline": article["headline"],
            "summary": article["summary"],
            "url": article["url"],
            "source_name": article["source_name"],
            "platform": "seeking_alpha",
        },
    }


def run_seeking_alpha_poller() -> None:
    """Main polling loop for Seeking Alpha."""
    logger.info("📡 Seeking Alpha poller started")
    interval = get_poll_interval()

    while True:
        all_payloads = []
        symbols = get_symbols()

        for symbol in symbols:
            articles = fetch_seeking_alpha_feed(symbol)
            for article in articles:
                payload = build_payload(symbol, article)
                all_payloads.append(payload)

        if all_payloads:
            publish_to_queue(all_payloads)
            logger.info(f"✅ Published {len(all_payloads)} Seeking Alpha articles")
        else:
            logger.info("No articles found this round")

        logger.info(f"⏱️ Sleeping for {interval} seconds")
        time.sleep(interval)
