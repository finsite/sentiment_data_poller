"""Polls recent sentiment messages from Stocktwits public API."""

import datetime
import time
from typing import Any

import requests

from app.config import get_symbols
from app.config_shared import get_config_value, get_polling_interval
from app.message_queue.queue_sender import publish_to_queue
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

API_URL = "https://api.stocktwits.com/api/2/streams/symbol/{}.json"


def fetch_stocktwits_messages(symbol: str) -> list[dict[str, Any]]:
    """Fetch messages for a symbol from Stocktwits.

    Args:
        symbol (str): Stock symbol.

    Returns:
        list[dict[str, Any]]: Parsed Stocktwits messages.
    """
    try:
        url = API_URL.format(symbol)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        messages = response.json().get("messages", [])
        logger.debug(f"Fetched {len(messages)} messages for {symbol}")
        return messages
    except Exception as e:
        logger.warning(f"Failed to fetch Stocktwits for {symbol}: {e}")
        return []


def build_payload(symbol: str, msg: dict[str, Any]) -> dict[str, Any]:
    """Constructs a standardized message from a Stocktwits post.

    Args:
        symbol (str): Stock symbol.
        msg (dict[str, Any]): Message object.

    Returns:
        dict[str, Any]: Queue-ready payload.
    """
    return {
        "symbol": symbol,
        "timestamp": msg.get("created_at", datetime.datetime.utcnow().isoformat()),
        "source": "Stocktwits",
        "data": {
            "username": msg.get("user", {}).get("username", ""),
            "content": msg.get("body", ""),
            "platform": "stocktwits",
        },
    }


def run_stocktwits_poller() -> None:
    """Main polling loop for Stocktwits."""
    logger.info("📡 Stocktwits poller started")
    interval = get_polling_interval()

    while True:
        all_payloads: list[dict[str, Any]] = []
        symbols = get_symbols()

        for symbol in symbols:
            messages = fetch_stocktwits_messages(symbol)
            for msg in messages:
                payload = build_payload(symbol, msg)
                all_payloads.append(payload)

        if all_payloads:
            publish_to_queue(all_payloads)
            logger.info(f"✅ Published {len(all_payloads)} Stocktwits messages")
        else:
            logger.info("No new messages this round")

        logger.info(f"⏱️ Sleeping for {interval} seconds")
        time.sleep(interval)
