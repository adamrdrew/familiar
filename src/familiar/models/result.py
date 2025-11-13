"""Test result models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ActionType(Enum):
    """Browser action types."""

    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    EVALUATE = "evaluate"


@dataclass
class LogEntry:
    """Single log entry."""

    timestamp: datetime
    level: LogLevel
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    source: str = "familiar"


@dataclass
class BrowserAction:
    """Record of browser action."""

    type: ActionType
    timestamp: datetime
    success: bool
    target: Optional[str] = None
    value: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TestResult:
    """Result of executing a test step."""

    step_name: str
    step_path: Path
    success: bool
    duration: float
    attempt: int
    logs: List[LogEntry] = field(default_factory=list)
    error: Optional[str] = None
    browser_actions: List[BrowserAction] = field(default_factory=list)
    screenshot_path: Optional[Path] = None

    @property
    def passed(self) -> bool:
        """Alias for success."""
        return self.success

    @property
    def failed(self) -> bool:
        """Inverse of success."""
        return not self.success

    @property
    def retry_count(self) -> int:
        """Number of retries (attempt - 1)."""
        return self.attempt - 1


@dataclass
class SuiteResult:
    """Result of executing a test suite."""

    suite_name: str
    suite_path: Path
    step_results: List[TestResult]
    duration: float
    started_at: datetime
    completed_at: datetime
    config_fuzziness: float = 0.0

    @property
    def success(self) -> bool:
        """Check if suite passed based on fuzziness."""
        if not self.step_results:
            return False
        pass_rate = self.passed_count / self.total_count
        required_pass_rate = 1.0 - self.config_fuzziness
        return pass_rate >= required_pass_rate

    @property
    def total_count(self) -> int:
        """Total number of steps."""
        return len(self.step_results)

    @property
    def passed_count(self) -> int:
        """Number of passed steps."""
        return sum(1 for r in self.step_results if r.success)

    @property
    def failed_count(self) -> int:
        """Number of failed steps."""
        return sum(1 for r in self.step_results if not r.success)

    @property
    def pass_rate(self) -> float:
        """Pass rate as percentage (0.0 - 1.0)."""
        if self.total_count == 0:
            return 0.0
        return self.passed_count / self.total_count


@dataclass
class TestRun:
    """Result of a complete test run."""

    run_id: str
    command: str
    suite_results: List[SuiteResult]
    duration: float
    started_at: datetime
    completed_at: datetime
    environment: Dict[str, str] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """True if all suites passed."""
        return all(sr.success for sr in self.suite_results)

    @property
    def exit_code(self) -> int:
        """CLI exit code."""
        return 0 if self.success else 1

    @property
    def total_suites(self) -> int:
        """Number of suites executed."""
        return len(self.suite_results)

    @property
    def passed_suites(self) -> int:
        """Number of suites that passed."""
        return sum(1 for sr in self.suite_results if sr.success)

    @property
    def failed_suites(self) -> int:
        """Number of suites that failed."""
        return sum(1 for sr in self.suite_results if not sr.success)

