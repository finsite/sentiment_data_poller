# pyright: reportPrivateImportUsage=false

"""Polls YouTube for recent financial videos and transcripts per stock symbol."""

import time
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi

try:
    from youtube_transcript_api._errors import TranscriptsDisabled
except ImportError:
    TranscriptsDisabled = Exception  # fallback if API changes

from app.config import get_config_value, get_poll_interval, get_symbols
from app.message_queue.queue_sender import publish_to_queue
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

# Constants
YOUTUBE_API_KEY = get_config_value("YOUTUBE_API_KEY")
YOUTUBE_SEARCH_QUERY = "finance|stock|market|earnings"
MAX_RESULTS = 5


def fetch_youtube_transcripts(symbol: str) -> list[dict[str, Any]]:
    """Fetches recent YouTube videos for the symbol and attempts to get transcripts.

    :param symbol: str:
    :param symbol: str:
    :param symbol: str: 

    """
    videos: list[dict[str, Any]] = []

    try:
        service = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        search_response = (
            service.search()
            .list(
                q=f"{symbol} {YOUTUBE_SEARCH_QUERY}",
                part="snippet",
                type="video",
                maxResults=MAX_RESULTS,
                order="date",
            )
            .execute()
        )

        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            published_at = item["snippet"]["publishedAt"]

            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([seg["text"] for seg in transcript])
            except TranscriptsDisabled:
                logger.info(f"Transcript disabled for video {video_id}")
                continue
            except Exception as e:
                logger.warning(f"Failed to fetch transcript for video {video_id}: {e}")
                continue

            videos.append(
                {
                    "timestamp": published_at,
                    "headline": title,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "transcript": transcript_text,
                }
            )

    except HttpError as e:
        logger.error(f"YouTube API error: {e}")
    except Exception as e:
        logger.error(f"Unhandled error in YouTube fetch: {e}")

    return videos


def build_payload(symbol: str, video: dict[str, Any]) -> dict[str, Any]:
    """

    :param symbol: str:
    :param video: dict[str:
    :param Any: param symbol: str:
    :param video: dict[str:
    :param Any: 
    :param symbol: str: 
    :param video: dict[str: 
    :param Any]: 

    """
    return {
        "symbol": symbol,
        "timestamp": video["timestamp"],
        "source": "YouTube",
        "data": {
            "headline": video["headline"],
            "url": video["url"],
            "transcript": video["transcript"],
            "platform": "youtube",
        },
    }


def run_youtube_poller() -> None:
    """Main polling loop for YouTube videos."""
    logger.info("📡 YouTube poller started")
    interval = get_poll_interval()

    while True:
        all_payloads: list[dict[str, Any]] = []
        symbols = get_symbols()

        for symbol in symbols:
            videos = fetch_youtube_transcripts(symbol)
            for video in videos:
                payload = build_payload(symbol, video)
                all_payloads.append(payload)

        if all_payloads:
            publish_to_queue(all_payloads)
            logger.info(f"✅ Published {len(all_payloads)} YouTube video transcripts")
        else:
            logger.info("No video transcripts this round")

        logger.info(f"⏱️ Sleeping for {interval} seconds")
        time.sleep(interval)
