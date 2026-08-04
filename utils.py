"""
Utils module - Utility helpers for logging, spinners, and formatting.
"""

import logging
import os
from datetime import datetime
from contextlib import contextmanager
from rich.console import Console


def setup_logger(log_file: str = "ip_tracker.log") -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        log_file (str): Path to log file.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger("ip_tracker")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def build_google_maps_url(latitude: float, longitude: float) -> str:
    """
    Generate a clickable Google Maps URL from coordinates.

    Args:
        latitude (float): Latitude value.
        longitude (float): Longitude value.

    Returns:
        str: Google Maps URL.
    """
    return f"https://www.google.com/maps?q={latitude},{longitude}"


def timestamp() -> str:
    """Return an ISO 8601 timestamp string."""
    return datetime.now().isoformat(timespec="seconds")


@contextmanager
def spinner(console: Console, message: str = "Fetching data..."):
    """
    Context manager showing a Rich spinner during long operations.

    Args:
        console (Console): Rich console instance.
        message (str): Message next to the spinner.
    """
    with console.status(f"[bold green]{message}", spinner="dots"):
        yield


def ensure_directory(path: str) -> None:
    """Create directory if it does not exist."""
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
