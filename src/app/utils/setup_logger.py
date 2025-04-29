# """
# Configure and return a logger for the application.

# The module provides a function to configure and return a logger instance with a
# specified name and logging level.
# """

# import logging

# from src.utils.setup_logger import setup_logger

# # Set up logger for this module
# logger = setup_logger(__name__)


# def setup_logger(name: str | None = None, level: int = logging.INFO) -> logging.Logger:
#     """
#     Configure and return a logger for the application.

#     The logger logs messages to the console using a StreamHandler and a
#     specified format. If the logger already exists, it simply returns the existing instance.

#     Args:
#     ----
#         name (Optional[str]): The name of the logger to create. If not specified, a default
#             logger named "poller" is created.
#         level (int): The logging level to set. Defaults to INFO.

#     Returns:
#     -------
#         logging.Logger: Configured logger instance.
#     """
#     # Determine the logger name
#     logger_name = name or "poller"

#     # Check if the logger already exists to avoid duplicate handlers
#     logger = logging.getLogger(logger_name)
#     if not logger.hasHandlers():
#         # Set the logging level
#         logger.setLevel(level)

#         # Create a StreamHandler to log messages to the console
#         handler = logging.StreamHandler()

#         # Define a format for the log messages
#         formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

#         # Set the format for the StreamHandler
#         handler.setFormatter(formatter)

#         # Add the StreamHandler to the logger
#         logger.addHandler(handler)

#     return logger


# # Create the logger instance
# logger = setup_logger(level=logging.DEBUG)
"""Configure and return a logger for the application.

This module provides a function to configure and return a logger instance with a
specified name and logging level.
"""

import logging


def setup_logger(name: str | None = None, level: int = logging.INFO) -> logging.Logger:
    """Configure and return a logger for the application.

    Logs messages to the console using a StreamHandler and a specified format.
    If the logger already exists, it reuses the existing instance.

    Args:
    ----
        name (Optional[str]): Name of the logger. Defaults to "poller" if not specified.
        level (int): Logging level to use. Defaults to logging.INFO.

    Returns:
    -------
        logging.Logger: Configured logger instance.

    """
    logger_name = name or "poller"
    logger = logging.getLogger(logger_name)

    if not logger.hasHandlers():
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Module-level logger
logger = setup_logger(level=logging.DEBUG)
