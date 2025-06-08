"""Polls Yahoo Finance news headlines for each stock symbol."""

import datetime
import time
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag

from app.config import get_symbols
from app.config_shared import get_config_value, get_polling_interval
from app.message_queue.queue_sender import publish_to_queue
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

YAHOO_FINANCE_NEWS_URL = "https://finance.yahoo.com/quote/{symbol}?p={symbol}"


def fetch_yahoo_news(symbol: str) -> list[dict[str, Any]]:
    """Scrapes Yahoo Finance for news articles related to the stock symbol.

    Args:
        symbol (str): Stock ticker symbol.

    Returns:
        list[dict[str, Any]]: List of parsed headline items.
    """
    try:
        url = YAHOO_FINANCE_NEWS_URL.format(symbol=symbol)
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        news_items: list[dict[str, Any]] = []

        for tag in soup.find_all("a"):
            if not isinstance(tag, Tag):
                continue

            href = tag.get("href", "")
            if isinstance(href, str) and href.startswith("/news/"):
                headline = tag.get_text(strip=True)
                article_url = f"https://finance.yahoo.com{href}"
                news_items.append(
                    {
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "headline": headline,
                        "url": article_url,
                    }
                )

        logger.debug(f"Fetched {len(news_items)} Yahoo Finance headlines for {symbol}")
        return news_items

    except Exception as e:
        logger.warning(f"Failed to fetch Yahoo Finance news for {symbol}: {e}")
        return []


def build_payload(symbol: str, article: dict[str, Any]) -> dict[str, Any]:
    """Constructs a queue-compatible payload from a Yahoo Finance article.

    Args:
        symbol (str): Stock ticker.
        article (dict[str, Any]): Parsed article information.

    Returns:
        dict[str, Any]: Queue-ready payload.
    """
    return {
        "symbol": symbol,
        "timestamp": article["timestamp"],
        "source": "YahooFinance",
        "data": {
            "headline": article["headline"],
            "url": article["url"],
            "platform": "yahoo_finance",
        },
    }


def run_yahoo_poller() -> None:
    """Main polling loop for Yahoo Finance."""
    logger.info("📡 Yahoo Finance poller started")
    interval = get_polling_interval()

    while True:
        all_payloads: list[dict[str, Any]] = []
        symbols = get_symbols()

        for symbol in symbols:
            articles = fetch_yahoo_news(symbol)
            for article in articles:
                payload = build_payload(symbol, article)
                all_payloads.append(payload)

        if all_payloads:
            publish_to_queue(all_payloads)
            logger.info(f"✅ Published {len(all_payloads)} Yahoo Finance articles")
        else:
            logger.info("No headlines this round")

        logger.info(f"⏱️ Sleeping for {interval} seconds")
        time.sleep(interval)
