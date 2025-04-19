"""
Polls social media content (e.g., Reddit, Twitter) and sends it to a message queue.
"""

import datetime

from app.logger import setup_logger
from app.queue_sender import publish_to_queue

logger = setup_logger(__name__)


def run_social_poller() -> None:
    logger.info("Running social sentiment poller...")

    # Placeholder
    sample_post = {
        "symbol": "TSLA",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "source": "Reddit",
        "data": {
            "username": "wallstreetbets_user123",
            "content": "TSLA is going to the moon 🚀🚀🚀",
            "platform": "reddit",
        },
    }

    publish_to_queue([sample_post])
    logger.info("Sample Reddit post published to queue.")
