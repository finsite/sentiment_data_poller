# # """
# # The module provides a function to track metrics for individual API requests.

# # Metrics tracked include the status of the request (success or failure), the API endpoint
# # that was accessed, and the response time in seconds.

# # The function logs the tracked metrics to the logger at the INFO level.

# # The function raises a ValueError if the status is not either 'success' or 'failure'.
# # """

# # from typing import Literal

# # from src.utils.setup_logger import setup_logger

# # # Set up logger for this module
# # logger = setup_logger(__name__)


# # def track_request_metrics(
# #     status: Literal["success", "failure"], endpoint: str, response_time: float
# # ) -> None:
# #     """
# #     Tracks metrics for individual API requests.

# #     Args:
# #     ----
# #         status (Literal["success", "failure"]): The status of the request ('success' or 'failure').
# #         endpoint (str): The API endpoint that was accessed.
# #         response_time (float): The time taken for the API request in seconds.

# #     Raises:
# #     ------
# #         ValueError: If the status is not 'success' or 'failure'.
# #     """
# #     # Validate status to ensure it is either 'success' or 'failure'
# #     if status not in {"success", "failure"}:
# #         raise ValueError("Invalid status. Must be 'success' or 'failure'.")

# #     # Construct log message based on the status
# #     message = (
# #         f"Request to {endpoint} completed successfully in {response_time:.2f} seconds."
# #         if status == "success"
# #         else f"Request to {endpoint} failed after {response_time:.2f} seconds."
# #     )

# #     # Log the message with appropriate log level
# #     if status == "success":
# #         logger.info(message)  # Log info for successful requests
# #     else:
# #         logger.error(message)  # Log error for failed requests
# from src.utils.setup_logger import setup_logger

# logger = setup_logger(__name__)

# def track_request_metrics(
#     symbol: str,
#     rate_limit: int,
#     time_window: float,
#     success: bool = True,
# ) -> None:
#     """
#     Tracks metrics for individual API requests.

#     Args:
#         symbol (str): The stock symbol for the request.
#         rate_limit (int): The number of allowed requests.
#         time_window (float): The rate limit window in seconds.
#         success (bool): Whether the request was successful.
#     """
#     status = "success" if success else "failure"
#     message = (
#         f"Request for symbol '{symbol}' succeeded. "
#         f"Rate limit: {rate_limit} req/{time_window}s."
#         if success else
#         f"Request for symbol '{symbol}' failed. "
#         f"Rate limit: {rate_limit} req/{time_window}s."
#     )

#     if success:
#         logger.info(message)
#     else:
#         logger.error(message)
"""Tracks metrics for individual API requests.

This function logs the result of API request operations, including the symbol,
rate limit, and whether the request was successful or not.
"""

from src.utils.setup_logger import setup_logger

# Initialize logger for this module
logger = setup_logger(__name__)


def track_request_metrics(
    symbol: str,
    rate_limit: int,
    time_window: float,
    success: bool = True,
) -> None:
    """Tracks metrics for individual API requests.

    Args:
    ----
        symbol (str): The stock symbol for the request.
        rate_limit (int): The number of allowed requests.
        time_window (float): The rate limit window in seconds.
        success (bool): Whether the request was successful.

    """
    status = "success" if success else "failure"
    message = (
        f"Request for symbol '{symbol}' {status}. " f"Rate limit: {rate_limit} req/{time_window}s."
    )

    if success:
        logger.info(message)
    else:
        logger.error(message)
