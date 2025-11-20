"""Test step models."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TestStep:
    """A single test step from markdown file."""

    path: Path
    content: str
    order: int
    timeout: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        """Extract step name from first heading."""
        for line in self.content.split("\n"):
            if line.startswith("# "):
                # Remove "Step:" prefix if present
                name = line[2:].strip()
                if name.lower().startswith("step:"):
                    name = name[5:].strip()
                return name
        return self.path.stem

    @property
    def variables(self) -> set[str]:
        """Extract all ${VAR} references from content."""
        pattern = r"\$\{([A-Z_][A-Z0-9_]*)(:-[^}]*)?\}"
        matches = re.findall(pattern, self.content)
        return {var for var, _ in matches}
