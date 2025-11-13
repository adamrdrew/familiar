"""Discover test suites in directory."""
from pathlib import Path
from typing import List, Optional

from familiar.core.parser import SuiteParser
from familiar.models.suite import TestSuite


class TestSuiteDiscovery:
    """Discover test suites in a directory tree."""

    def __init__(self, parser: Optional[SuiteParser] = None):
        """Initialize with optional parser (dependency injection)."""
        self.parser = parser or SuiteParser()

    def discover_suites(self, root_dir: Path) -> List[TestSuite]:
        """Discover all test suites under root directory."""
        if not root_dir.is_dir():
            raise ValueError(f"Root directory does not exist: {root_dir}")

        suites = []

        # Find all suite.yaml files
        for yaml_file in root_dir.rglob("suite.yaml"):
            # Skip shared directory
            if "shared" in yaml_file.parts:
                continue

            suite_dir = yaml_file.parent
            try:
                suite = self.parser.parse_suite(suite_dir)
                suites.append(suite)
            except Exception as e:
                # Log error but continue discovering
                print(f"Warning: Failed to parse suite {suite_dir}: {e}")

        return sorted(suites, key=lambda s: s.path)

