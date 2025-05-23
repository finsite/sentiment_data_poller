"""Polls latest news headlines from Finviz.com for each symbol."""

import datetime
import time

import requests
from bs4 import BeautifulSoup, Tag

from app.config import get_poll_interval, get_symbols
from app.message_queue.queue_sender import publish_to_queue
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

BASE_URL = "https://finviz.com/quote.ashx?t={}"


def fetch_finviz_news(symbol: str) -> list[dict]:
    """Scrapes the Finviz news table for a given symbol."""
    news: list[dict] = []

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = BASE_URL.format(symbol)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        news_table = soup.find("table", class_="fullview-news-outer")
        if not isinstance(news_table, Tag):
            logger.debug(f"No news table found for {symbol}")
            return []

        rows = news_table.find_all("tr")

        for row in rows:
            if not isinstance(row, Tag):
                continue

            tds = row.find_all("td")
            if len(tds) != 2:
                continue

            timestamp_text = tds[0].get_text(strip=True)

            td_element = tds[1]
            if not isinstance(td_element, Tag):
                continue

            headline_text = td_element.get_text(strip=True)

            a_tag = td_element.find("a")
            if not isinstance(a_tag, Tag) or not a_tag.has_attr("href"):
                continue
            link = a_tag["href"]

            now = datetime.datetime.utcnow()
            try:
                if " " in timestamp_text:
                    date_str, time_str = timestamp_text.split(" ")
                    dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%b-%d-%y %I:%M%p")
                else:
                    dt = datetime.datetime.strptime(timestamp_text, "%I:%M%p")
                    dt = dt.replace(year=now.year, month=now.month, day=now.day)
            except ValueError as ve:
                logger.warning(f"Failed to parse timestamp for {symbol}: {timestamp_text} ({ve})")
                continue

            news.append(
                {
                    "timestamp": dt.isoformat(),
                    "headline": headline_text,
                    "url": link,
                }
            )

    except Exception as e:
        logger.warning(f"Failed to fetch Finviz news for {symbol}: {e}")

    return news


def build_payload(symbol: str, article: dict) -> dict:
    return {
        "symbol": symbol,
        "timestamp": article["timestamp"],
        "source": "Finviz",
        "data": {
            "headline": article["headline"],
            "url": article["url"],
            "platform": "finviz",
        },
    }


def run_finviz_poller() -> None:
    """Main polling loop for Finviz."""
    logger.info("📡 Finviz poller started")
    interval = get_poll_interval()

    while True:
        all_payloads = []
        symbols = get_symbols()

        for symbol in symbols:
            articles = fetch_finviz_news(symbol)
            for article in articles:
                payload = build_payload(symbol, article)
                all_payloads.append(payload)

        if all_payloads:
            publish_to_queue(all_payloads)
            logger.info(f"✅ Published {len(all_payloads)} Finviz headlines")
        else:
            logger.info("No headlines this round")

        logger.info(f"⏱️ Sleeping for {interval} seconds")
        time.sleep(interval)
