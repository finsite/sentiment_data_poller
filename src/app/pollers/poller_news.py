"""Polls financial news headlines and sends them to a message queue.
"""

import datetime

from app.logger import setup_logger
from app.queue_sender import publish_to_queue

logger = setup_logger(__name__)


def run_news_poller() -> None:
    logger.info("Running news sentiment poller...")

    # Placeholder: this would pull from a real API
    sample_headline = {
        "symbol": "AAPL",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "source": "MockNewsAPI",
        "data": {
            "headline": "Apple shares rise after earnings beat expectations",
            "summary": "Q2 earnings exceeded expectations with strong iPhone sales.",
            "raw": "Apple Inc (NASDAQ: AAPL)...",
        },
    }

    publish_to_queue([sample_headline])
    logger.info("Sample news headline published to queue.")
