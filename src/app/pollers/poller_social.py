import datetime

from app.config import get_symbols
from app.message_queue.queue_sender import publish_to_queue
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


def run_social_poller() -> None:
    """"""
    logger.info("Running social sentiment poller...")

    symbols = get_symbols()
    payloads = []

    for symbol in symbols:
        sample_post = {
            "symbol": symbol,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "source": "Reddit",
            "data": {
                "username": "wallstreetbets_user123",
                "content": f"{symbol} is going to the moon 🚀🚀🚀",
                "platform": "reddit",
            },
        }
        payloads.append(sample_post)

    publish_to_queue(payloads)
    logger.info(f"Published {len(payloads)} fake social sentiment posts.")
