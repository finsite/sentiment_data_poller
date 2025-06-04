"""Polls Yahoo Finance news headlines for each stock symbol."""

import datetime
import time
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag

from app.config import get_poll_interval, get_symbols
from app.message_queue.queue_sender import publish_to_queue
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

YAHOO_FINANCE_NEWS_URL = "https://finance.yahoo.com/quote/{symbol}?p={symbol}"


def fetch_yahoo_news(symbol: str) -> list[dict[str, Any]]:
    """Scrapes Yahoo Finance for news articles related to the stock symbol.

    :param symbol: str:
    :param symbol: str:
    :param symbol: str:
    :param symbol: type symbol: str :
    :param symbol: type symbol: str :
    :param symbol: str:
    :param symbol: str: 

    """
    try:
        url = YAHOO_FINANCE_NEWS_URL.format(symbol=symbol)
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        news_items: list[dict[str, Any]] = []

        # Yahoo Finance uses this tag structure for headlines
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

        logger.debug(f"Fetched {len(news_items)} headlines from Yahoo Finance for {symbol}")
        return news_items

    except Exception as e:
        logger.warning(f"Failed to fetch Yahoo Finance news for {symbol}: {e}")
        return []


def build_payload(symbol: str, article: dict[str, Any]) -> dict[str, Any]:
    """

    :param symbol: str:
    :param article: dict[str:
    :param Any: param symbol: str:
    :param article: dict[str:
    :param Any: param symbol: str:
    :param article: dict[str:
    :param Any: param symbol:
    :param article: type article: dict[str :
    :param Any: param symbol:
    :param article: type article: dict[str :
    :param symbol: str:
    :param article: dict[str:
    :param symbol: str: 
    :param article: dict[str: 
    :param Any]: 

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
    interval = get_poll_interval()

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
