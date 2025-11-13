"""Parse suite configurations and test steps."""
from pathlib import Path
from typing import List

import yaml

from familiar.models.step import TestStep
from familiar.models.suite import SuiteConfig, TestSuite


class SuiteParser:
    """Parse test suite from directory."""

    def parse_suite(self, suite_path: Path) -> TestSuite:
        """Parse suite from directory containing suite.yaml."""
        if not suite_path.is_dir():
            raise ValueError(f"Suite path is not a directory: {suite_path}")

        config_file = suite_path / "suite.yaml"
        if not config_file.exists():
            raise FileNotFoundError(f"suite.yaml not found in {suite_path}")

        # Parse configuration
        config = self._parse_config(config_file)

        # Find and parse step files
        steps = self._parse_steps(suite_path)

        return TestSuite(
            name=config.name,
            path=suite_path,
            config=config,
            steps=steps,
        )

    def _parse_config(self, config_file: Path) -> SuiteConfig:
        """Parse suite.yaml configuration file."""
        with open(config_file) as f:
            data = yaml.safe_load(f)
        return SuiteConfig(**data)

    def _parse_steps(self, suite_path: Path) -> List[TestStep]:
        """Find and parse all step files in suite directory."""
        step_files = sorted(suite_path.glob("[0-9][0-9]-*.md"))

        if not step_files:
            raise ValueError(f"No step files found in {suite_path}")

        steps = []
        for step_file in step_files:
            step = self._parse_step(step_file)
            steps.append(step)

        return steps

    def _parse_step(self, step_file: Path) -> TestStep:
        """Parse single step file."""
        content = step_file.read_text()

        # Extract order from filename (first two digits)
        order = int(step_file.stem[:2])

        # TODO: Parse frontmatter if present

        return TestStep(
            path=step_file,
            content=content,
            order=order,
        )

