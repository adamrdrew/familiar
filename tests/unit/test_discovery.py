"""Test suite discovery."""
from pathlib import Path

import pytest

from familiar.core.discovery import TestSuiteDiscovery


@pytest.fixture
def multi_suite_dir(tmp_path: Path) -> Path:
    """Create multiple test suites."""
    # Suite 1
    suite1 = tmp_path / "suite1"
    suite1.mkdir()
    (suite1 / "suite.yaml").write_text('name: "Suite 1"\n')
    (suite1 / "00-test.md").write_text("# Test")

    # Suite 2
    suite2 = tmp_path / "suite2"
    suite2.mkdir()
    (suite2 / "suite.yaml").write_text('name: "Suite 2"\n')
    (suite2 / "00-test.md").write_text("# Test")

    # Shared directory (should be skipped)
    shared = tmp_path / "shared"
    shared.mkdir()
    (shared / "suite.yaml").write_text('name: "Shared"\n')
    (shared / "00-test.md").write_text("# Test")

    return tmp_path


def test_discover_suites(multi_suite_dir: Path) -> None:
    """Test suite discovery."""
    discovery = TestSuiteDiscovery()
    suites = discovery.discover_suites(multi_suite_dir)

    assert len(suites) == 2
    assert [s.name for s in suites] == ["Suite 1", "Suite 2"]


def test_discover_skips_shared_directory(multi_suite_dir: Path) -> None:
    """Test that shared directory is skipped."""
    discovery = TestSuiteDiscovery()
    suites = discovery.discover_suites(multi_suite_dir)

    # Should not include shared suite
    suite_names = [s.name for s in suites]
    assert "Shared" not in suite_names


def test_discover_invalid_directory() -> None:
    """Test error when root directory doesn't exist."""
    discovery = TestSuiteDiscovery()
    with pytest.raises(ValueError, match="does not exist"):
        discovery.discover_suites(Path("/nonexistent"))


def test_discover_no_suites(tmp_path: Path) -> None:
    """Test discovery when no suites found."""
    discovery = TestSuiteDiscovery()
    suites = discovery.discover_suites(tmp_path)
    assert len(suites) == 0

