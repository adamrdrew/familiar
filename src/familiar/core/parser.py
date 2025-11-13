"""Parse suite configurations and test steps."""
import re
from pathlib import Path
from typing import List, Tuple

import yaml

from familiar.models.step import TestStep
from familiar.models.suite import SuiteConfig, TestSuite

# Pattern for numbered step files: 00-name.md, 01-name.md, etc.
STEP_PATTERN = re.compile(r'^\d\d-.+\.md$')


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
        """Find and parse all numbered step files in suite directory.
        
        Steps must follow pattern: NN-description.md (e.g., 00-login.md, 01-navigate.md)
        Files without numeric prefixes are skipped (e.g., README.md, notes.md)
        """
        # Find all markdown files
        all_md_files = list(suite_path.glob("*.md"))
        
        # Separate numbered steps from other files
        numbered_steps, skipped_files = self._categorize_step_files(all_md_files)
        
        if not numbered_steps:
            if skipped_files:
                skipped_names = [f.name for f in skipped_files]
                raise ValueError(
                    f"No numbered step files found in {suite_path}. "
                    f"Found {len(skipped_files)} non-numbered file(s): {skipped_names}. "
                    f"Step files must follow pattern: 00-description.md"
                )
            else:
                raise ValueError(f"No step files found in {suite_path}")
        
        # Validate no duplicate prefixes
        self._validate_step_prefixes(numbered_steps)
        
        # Sort by filename (numeric prefix ensures correct order)
        sorted_steps = sorted(numbered_steps, key=lambda p: p.name)
        
        # Parse each step file
        steps = []
        for step_file in sorted_steps:
            step = self._parse_step(step_file)
            steps.append(step)
        
        return steps
    
    def _categorize_step_files(self, files: List[Path]) -> Tuple[List[Path], List[Path]]:
        """Separate files into numbered steps and skipped files.
        
        Returns:
            Tuple of (numbered_steps, skipped_files)
        """
        numbered = []
        skipped = []
        
        for filepath in files:
            if STEP_PATTERN.match(filepath.name):
                numbered.append(filepath)
            else:
                skipped.append(filepath)
        
        return numbered, skipped
    
    def _validate_step_prefixes(self, step_files: List[Path]) -> None:
        """Ensure no duplicate numeric prefixes in step files.
        
        Raises:
            ValueError: If duplicate prefixes are found.
        """
        prefixes = [f.name[:2] for f in step_files]
        duplicates = {p for p in prefixes if prefixes.count(p) > 1}
        
        if duplicates:
            dup_files = [f.name for f in step_files if f.name[:2] in duplicates]
            raise ValueError(
                f"Duplicate step prefixes found: {sorted(duplicates)}. "
                f"Affected files: {dup_files}. "
                f"Each step must have a unique numeric prefix (00-99)."
            )

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

