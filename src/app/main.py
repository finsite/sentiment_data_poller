"""Main entry point for the sentiment data poller.

This application polls sentiment-related sources (e.g., NewsAPI, Finviz, Stocktwits)
based on the POLLER_TYPE environment variable and sends structured data to
a message queue for downstream analysis.
"""

import os

from app.pollers.poller_benzinga import run_benzinga_poller
from app.pollers.poller_finviz import run_finviz_poller
from app.pollers.poller_google_news import run_google_news_poller

# Import poller runners
from app.pollers.poller_newsapi import run_newsapi_poller
from app.pollers.poller_seeking_alpha import run_seeking_alpha_poller
from app.pollers.poller_stocktwits import run_stocktwits_poller
from app.pollers.poller_yahoo_finance import run_yahoo_poller
from app.pollers.poller_youtube import run_youtube_poller
from app.utils.setup_logger import setup_logger

# Optional placeholder or testing stub
# from app.pollers.poller_reddit import run_reddit_poller
# from app.pollers.poller_twitter import run_twitter_poller

POLLERS = {
    "newsapi": run_newsapi_poller,
    "finviz": run_finviz_poller,
    "stocktwits": run_stocktwits_poller,
    "yahoo": run_yahoo_poller,
    "google_news": run_google_news_poller,
    "seeking_alpha": run_seeking_alpha_poller,
    "youtube": run_youtube_poller,
    "benzinga": run_benzinga_poller,
    # "reddit": run_reddit_poller,
    # "twitter": run_twitter_poller,
}

logger = setup_logger("main")


def main() -> None:
    poller_type = os.getenv("POLLER_TYPE", "").lower()
    logger.info(f"Sentiment data poller starting: type={poller_type}")

    runner = POLLERS.get(poller_type)
    if runner:
        runner()
    else:
        logger.error(
            f"❌ Unknown POLLER_TYPE: {poller_type}. Available options: {', '.join(POLLERS)}"
        )


if __name__ == "__main__":
    main()
