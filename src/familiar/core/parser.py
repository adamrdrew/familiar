"""Parse suite configurations and test steps."""

import logging
import re
from pathlib import Path

import yaml

from familiar.models.step import TestStep
from familiar.models.suite import SuiteConfig, TestSuite

# Pattern for numbered step files: 00-name.md, 01-name.md, etc.
STEP_PATTERN = re.compile(r"^\d\d-.+\.md$")

logger = logging.getLogger(__name__)


def read_agent_instructions(path: Path) -> str | None:
    """Read agent instructions from file with robust error handling.

    Args:
        path: Path to agent.md file

    Returns:
        File content as string, or None if file doesn't exist or can't be read

    Error Handling:
        - File not found: Returns None (no warning)
        - Encoding error: Returns None with WARNING log
        - Permission error: Returns None with WARNING log
        - Empty file: Returns None (no warning)
        - Large file (>100KB): Returns content with WARNING log
    """
    if not path.exists():
        return None

    # Check file size
    try:
        file_size = path.stat().st_size
        if file_size == 0:
            return None  # Empty file

        if file_size > 100 * 1024:  # 100KB
            logger.warning(
                f"agent.md at {path} is large ({file_size / 1024:.1f}KB). "
                "Consider keeping instructions concise for better results."
            )
    except OSError as e:
        logger.warning(f"Could not stat agent.md at {path}: {e}")
        return None

    # Read file with encoding fallback
    try:
        content = path.read_text(encoding="utf-8")
        # Strip whitespace and return None if empty
        content = content.strip()
        return content if content else None
    except UnicodeDecodeError:
        try:
            content = path.read_text(encoding="latin-1").strip()
            if content:
                logger.warning(f"agent.md at {path} is not UTF-8, used latin-1 fallback")
                return content
            return None
        except Exception as e:
            logger.warning(f"Could not read agent.md at {path}: {e}")
            return None
    except Exception as e:
        logger.warning(f"Could not read agent.md at {path}: {e}")
        return None


def read_system_prompt(path: Path) -> str | None:
    """Read base system prompt from file.

    Args:
        path: Path to system_prompt.md file

    Returns:
        File content as string, or None if file doesn't exist or can't be read

    Error Handling:
        - File not found: Returns None with INFO log
        - Encoding error: Returns None with WARNING log
        - Permission error: Returns None with WARNING log
        - Empty file: Returns None with INFO log
    """
    if not path.exists():
        logger.info(f"System prompt file not found at {path}, using default behavior")
        return None

    # Check file size
    try:
        file_size = path.stat().st_size
        if file_size == 0:
            logger.info(f"System prompt file at {path} is empty")
            return None
    except OSError as e:
        logger.warning(f"Could not stat system_prompt.md at {path}: {e}")
        return None

    # Read file with encoding fallback
    try:
        content = path.read_text(encoding="utf-8")
        # Strip whitespace and return None if empty
        content = content.strip()
        return content if content else None
    except UnicodeDecodeError:
        try:
            content = path.read_text(encoding="latin-1").strip()
            if content:
                logger.warning(f"system_prompt.md at {path} is not UTF-8, used latin-1 fallback")
                return content
            return None
        except Exception as e:
            logger.warning(f"Could not read system_prompt.md at {path}: {e}")
            return None
    except Exception as e:
        logger.warning(f"Could not read system_prompt.md at {path}: {e}")
        return None


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

        # Read agent instructions if present
        agent_file = suite_path / "agent.md"
        agent_instructions = read_agent_instructions(agent_file)

        return TestSuite(
            name=config.name,
            path=suite_path,
            config=config,
            steps=steps,
            agent_instructions=agent_instructions,
        )

    def _parse_config(self, config_file: Path) -> SuiteConfig:
        """Parse suite.yaml configuration file."""
        with open(config_file) as f:
            data = yaml.safe_load(f)
        return SuiteConfig(**data)

    def _parse_steps(self, suite_path: Path) -> list[TestStep]:
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

    def _categorize_step_files(self, files: list[Path]) -> tuple[list[Path], list[Path]]:
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

    def _validate_step_prefixes(self, step_files: list[Path]) -> None:
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
