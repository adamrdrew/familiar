"""Unit tests for logging setup and handlers."""

import logging
from familiar.logging.handlers import create_rich_handler, setup_rich_logging


class TestLoggingHandlers:
    """Tests for logging handler creation."""

    def test_create_rich_handler_default(self):
        """Test creating a Rich handler with default settings."""
        handler = create_rich_handler(level="INFO")

        assert handler is not None
        assert handler.level == logging.INFO
        assert hasattr(handler, "console")  # Should have console attribute

    def test_create_rich_handler_debug_level(self):
        """Test creating a Rich handler with DEBUG level."""
        handler = create_rich_handler(level="DEBUG")

        assert handler is not None
        assert handler.level == logging.DEBUG

    def test_create_rich_handler_error_level(self):
        """Test creating a Rich handler with ERROR level."""
        handler = create_rich_handler(level="ERROR")

        assert handler is not None
        assert handler.level == logging.ERROR

    def test_setup_rich_logging_returns_logger(self):
        """Test that setup_rich_logging returns a configured logger."""
        logger = setup_rich_logging(level="DEBUG")

        assert logger is not None
        assert logger.name == "familiar"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) > 0  # Should have at least one handler

        # Clean up - remove handlers to avoid affecting other tests
        logger.handlers.clear()
