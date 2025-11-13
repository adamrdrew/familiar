"""Test suite parser."""
from pathlib import Path

import pytest

from familiar.core.parser import SuiteParser


@pytest.fixture
def sample_suite(tmp_path: Path) -> Path:
    """Create sample suite for testing."""
    suite_dir = tmp_path / "test-suite"
    suite_dir.mkdir()

    # Create suite.yaml
    (suite_dir / "suite.yaml").write_text(
        """
name: "Test Suite"
timeout: 120
step_timeout: 30
"""
    )

    # Create step files
    (suite_dir / "00-first.md").write_text("# Step: First\n\nDo something")
    (suite_dir / "01-second.md").write_text("# Step: Second\n\nDo more")

    return suite_dir


def test_parse_suite(sample_suite: Path) -> None:
    """Test parsing a complete suite."""
    parser = SuiteParser()
    suite = parser.parse_suite(sample_suite)

    assert suite.name == "Test Suite"
    assert suite.config.timeout == 120
    assert suite.config.step_timeout == 30
    assert len(suite.steps) == 2
    assert suite.steps[0].order == 0
    assert suite.steps[0].name == "First"
    assert suite.steps[1].order == 1
    assert suite.steps[1].name == "Second"


def test_parse_suite_missing_yaml(tmp_path: Path) -> None:
    """Test error when suite.yaml missing."""
    suite_dir = tmp_path / "invalid-suite"
    suite_dir.mkdir()

    parser = SuiteParser()
    with pytest.raises(FileNotFoundError, match="suite.yaml not found"):
        parser.parse_suite(suite_dir)


def test_parse_suite_not_directory(tmp_path: Path) -> None:
    """Test error when path is not a directory."""
    not_a_dir = tmp_path / "file.txt"
    not_a_dir.write_text("content")

    parser = SuiteParser()
    with pytest.raises(ValueError, match="not a directory"):
        parser.parse_suite(not_a_dir)


def test_parse_suite_no_steps(tmp_path: Path) -> None:
    """Test error when no step files found."""
    suite_dir = tmp_path / "empty-suite"
    suite_dir.mkdir()
    (suite_dir / "suite.yaml").write_text('name: "Empty"\n')

    parser = SuiteParser()
    with pytest.raises(ValueError, match="No step files found"):
        parser.parse_suite(suite_dir)


def test_parse_steps_ordering(tmp_path: Path) -> None:
    """Test that steps are ordered correctly."""
    suite_dir = tmp_path / "ordered-suite"
    suite_dir.mkdir()
    (suite_dir / "suite.yaml").write_text('name: "Ordered"\n')

    # Create files in non-sequential order
    (suite_dir / "03-third.md").write_text("# Third")
    (suite_dir / "01-first.md").write_text("# First")
    (suite_dir / "02-second.md").write_text("# Second")

    parser = SuiteParser()
    suite = parser.parse_suite(suite_dir)

    assert suite.steps[0].order == 1
    assert suite.steps[1].order == 2
    assert suite.steps[2].order == 3

