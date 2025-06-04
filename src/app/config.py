"""Configuration module for the sentiment poller.

Provides typed getter functions to retrieve configuration values from
HashiCorp Vault, environment variables, or defaults — in that order.
"""

import os

from app.utils.vault_client import VaultClient

# Initialize and cache Vault client
_vault = VaultClient()


def get_config_value(key: str, default: str | None = None) -> str:
    """Retrieve a configuration value from Vault, environment variable, or
    default.

    Args:
    ----
      key(str): The configuration key to retrieve.
      default(Optional[str]): Fallback value if key is missing.
      key: str:
      default: str | None:  (Default value = None)
      key: str:
      default: str | None:  (Default value = None)

    Returns:
    -------
      str: The resolved configuration value.

    Raises:
    ------
      ValueError: If the key is missing and no default is provided.

    Parameters
    ----------
    key :
        str:
    default :
        str | None:  (Default value = None)
    key :
        str:
    default :
        str | None:  (Default value = None)
    key :
        str:
    default :
        str | None:  (Default value = None)
    key: str :

    default: str | None :
         (Default value = None)

    Returns
    -------

    """
    val = _vault.get(key, os.getenv(key))
    if val is None:
        if default is not None:
            return str(default)
        raise ValueError(f"❌ Missing required config for key: {key}")
    return str(val)


# --------------------------------------------------------------------------
# 🔧 General Configuration
# --------------------------------------------------------------------------


def get_log_level() -> str:
    """ """
    return get_config_value("LOG_LEVEL", "info")


def get_log_dir() -> str:
    """ """
    return get_config_value("LOG_DIR", "/app/logs")


def get_data_source() -> str:
    """ """
    return get_config_value("DATA_SOURCE", "newsapi")


def get_symbols() -> list[str]:
    """ """
    raw = get_config_value("SYMBOLS", "")
    if not raw:
        raise ValueError("❌ SYMBOLS configuration is not set.")
    return [s.strip().upper() for s in raw.split(",") if s.strip()]


def get_poll_interval() -> int:
    """ """
    return int(get_config_value("POLL_INTERVAL", "300"))


def get_poll_timeout() -> int:
    """ """
    return int(get_config_value("POLL_TIMEOUT", "30"))


def get_request_timeout() -> int:
    """ """
    return int(get_config_value("REQUEST_TIMEOUT", "10"))


# --------------------------------------------------------------------------
# 🔁 Retry & Backfill
# --------------------------------------------------------------------------


def get_max_retries() -> int:
    """ """
    return int(get_config_value("MAX_RETRIES", "3"))


def get_retry_delay() -> int:
    """ """
    return int(get_config_value("RETRY_DELAY", "5"))


def is_retry_enabled() -> bool:
    """ """
    return get_config_value("ENABLE_RETRY", "true") == "true"


def is_backfill_enabled() -> bool:
    """ """
    return get_config_value("ENABLE_BACKFILL", "false") == "true"


# --------------------------------------------------------------------------
# 🧪 Logging Flags
# --------------------------------------------------------------------------


def is_logging_enabled() -> bool:
    """ """
    return get_config_value("ENABLE_LOGGING", "true") == "true"


def is_cloud_logging_enabled() -> bool:
    """ """
    return get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"


# --------------------------------------------------------------------------
# 📊 Poller Configuration
# --------------------------------------------------------------------------


def get_poller_type() -> str:
    """ """
    return get_config_value("POLLER_TYPE", "newsapi")


def get_poller_fill_rate_limit() -> int:
    """ """
    return int(get_config_value("POLLER_FILL_RATE_LIMIT", get_config_value("RATE_LIMIT", "0")))


# NEWSAPI specific fill rate and capacity
def get_newsapi_rate_limit() -> tuple[int, int]:
    """ """
    return (
        int(get_config_value("NEWSAPI_FILL_RATE", "5")),
        int(get_config_value("NEWSAPI_CAPACITY", "5")),
    )


def get_newsapi_timeout() -> int:
    """ """
    return int(get_config_value("NEWSAPI_TIMEOUT", "10"))


# --------------------------------------------------------------------------
# 🔐 API Keys
# --------------------------------------------------------------------------


def get_newsapi_key() -> str:
    """ """
    return get_config_value("NEWSAPI_KEY", "")


# --------------------------------------------------------------------------
# 📬 Queue Configuration
# --------------------------------------------------------------------------


def get_queue_type() -> str:
    """ """
    return get_config_value("QUEUE_TYPE", "rabbitmq")


def get_rabbitmq_host() -> str:
    """ """
    return get_config_value("RABBITMQ_HOST", "localhost")


def get_rabbitmq_port() -> int:
    """ """
    return int(get_config_value("RABBITMQ_PORT", "5672"))


def get_rabbitmq_exchange() -> str:
    """ """
    return get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")


def get_rabbitmq_routing_key() -> str:
    """ """
    return get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")


def get_rabbitmq_vhost() -> str:
    """ """
    vhost = get_config_value("RABBITMQ_VHOST")
    if not vhost:
        raise ValueError("❌ Missing required config: RABBITMQ_VHOST must be set.")
    return vhost


def get_rabbitmq_user() -> str:
    """ """
    return get_config_value("RABBITMQ_USER", "")


def get_rabbitmq_password() -> str:
    """ """
    return get_config_value("RABBITMQ_PASS", "")


def get_sqs_queue_url() -> str:
    """ """
    return get_config_value("SQS_QUEUE_URL", "")


def get_rate_limit() -> int:
    """ """
    return int(get_config_value("RATE_LIMIT", "0"))
