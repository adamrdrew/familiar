"""Pytest configuration and fixtures."""
from pathlib import Path

import pytest


@pytest.fixture
def temp_test_dir(tmp_path: Path) -> Path:
    """Create a temporary test directory."""
    return tmp_path

