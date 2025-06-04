"""Polls Google News RSS feed headlines for each stock symbol."""

import datetime
import time
import urllib.parse
from typing import Any

import feedparser

from app.config import get_poll_interval, get_symbols
from app.message_queue.queue_sender import publish_to_queue
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en"


def fetch_google_news(symbol: str) -> list[dict[str, Any]]:
    """Fetches news headlines from Google News RSS for a given stock symbol.

    :param symbol: str:
    :param symbol: str: 

    """
    encoded_symbol = urllib.parse.quote_plus(symbol)
    url = GOOGLE_NEWS_RSS.format(symbol=encoded_symbol)

    logger.debug(f"Fetching Google News RSS for {symbol}: {url}")
    feed = feedparser.parse(url)
    entries = getattr(feed, "entries", [])

    news_items: list[dict[str, Any]] = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        title = entry.get("title", "")
        link = entry.get("link", "")
        published = entry.get("published", "")

        try:
            dt = datetime.datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
            timestamp = dt.isoformat()
        except Exception as e:
            logger.warning(f"Failed to parse publish date for {symbol}: {published} ({e})")
            timestamp = datetime.datetime.utcnow().isoformat()

        news_items.append(
            {
                "timestamp": timestamp,
                "headline": title,
                "url": link,
            }
        )

    return news_items


def build_payload(symbol: str, article: dict[str, Any]) -> dict[str, Any]:
    """

    :param symbol: str:
    :param article: dict[str:
    :param Any: 
    :param symbol: str: 
    :param article: dict[str: 
    :param Any]: 

    """
    return {
        "symbol": symbol,
        "timestamp": article["timestamp"],
        "source": "GoogleNews",
        "data": {
            "headline": article["headline"],
            "url": article["url"],
            "platform": "google_news",
        },
    }


def run_google_news_poller() -> None:
    """Main polling loop for Google News."""
    logger.info("📡 Google News poller started")
    interval = get_poll_interval()

    while True:
        all_payloads: list[dict[str, Any]] = []
        symbols = get_symbols()

        for symbol in symbols:
            articles = fetch_google_news(symbol)
            for article in articles:
                payload = build_payload(symbol, article)
                all_payloads.append(payload)

        if all_payloads:
            publish_to_queue(all_payloads)
            logger.info(f"✅ Published {len(all_payloads)} Google News items")
        else:
            logger.info("No new headlines this round")

        logger.info(f"⏱️ Sleeping for {interval} seconds")
        time.sleep(interval)
