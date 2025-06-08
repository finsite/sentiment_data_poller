"""Repository-specific configuration.

Delegates to shared config for common settings and defines any custom logic needed
by this repository (e.g., symbol lists, indicator types).
"""

import os
from app.config_shared import (
    get_polling_interval,
    get_batch_size,
    get_queue_type,
    get_rabbitmq_queue,
    get_output_mode,
    get_sqs_queue_url,
    get_sqs_region,
    get_config_value,
)


def get_symbols() -> list[str]:
    """Returns a list of symbols to track for this repository."""
    symbols = os.getenv("SYMBOLS", "AAPL,MSFT,GOOG")
    return [s.strip() for s in symbols.split(",") if s.strip()]
