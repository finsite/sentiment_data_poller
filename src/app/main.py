"""
Main entry point for the sentiment data poller.

This application polls sentiment-related sources (e.g., news, social media)
based on the POLLER_TYPE environment variable and sends structured data
to a message queue for downstream analysis.
"""

import os
from app.logger import setup_logger
from pollers.poller_news import run_news_poller
from pollers.poller_social import run_social_poller

logger = setup_logger("main")


def main() -> None:
    poller_type = os.getenv("POLLER_TYPE", "news").lower()
    logger.info(f"Sentiment data poller starting: type={poller_type}")

    if poller_type == "news":
        run_news_poller()
    elif poller_type == "social":
        run_social_poller()
    else:
        logger.error(f"Unknown POLLER_TYPE: {poller_type}")


if __name__ == "__main__":
    main()
