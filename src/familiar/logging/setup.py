"""Logging setup and configuration."""
import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_style: str = "simple",
) -> logging.Logger:
    """Configure logging for Familiar.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format_style: Format style ("simple" or "detailed").
    
    Returns:
        Configured logger instance.
    """
    # Create logger
    logger = logging.getLogger("familiar")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Set format based on style
    if format_style == "detailed":
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter("%(levelname)s: %(message)s")
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name. If None, returns the root familiar logger.
    
    Returns:
        Logger instance.
    """
    if name:
        return logging.getLogger(f"familiar.{name}")
    return logging.getLogger("familiar")

