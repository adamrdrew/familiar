"""Custom log handlers with rich formatting."""

import logging

from rich.console import Console
from rich.logging import RichHandler


def create_rich_handler(
    level: str = "INFO",
    show_time: bool = True,
    show_path: bool = False,
) -> RichHandler:
    """Create a Rich console log handler with formatting.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        show_time: Whether to show timestamps.
        show_path: Whether to show file paths.

    Returns:
        Configured RichHandler instance.
    """
    console = Console(stderr=False)

    handler = RichHandler(
        console=console,
        show_time=show_time,
        show_path=show_path,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
    )

    handler.setLevel(getattr(logging, level.upper()))

    return handler


def setup_rich_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging with Rich formatting.

    This provides beautiful console output with colors and formatting.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Configured logger with Rich handler.
    """
    logger = logging.getLogger("familiar")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Add Rich handler
    handler = create_rich_handler(level=level)
    logger.addHandler(handler)

    return logger
