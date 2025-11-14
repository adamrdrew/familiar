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


class ResultStatus(Enum):
    """Test result status enumeration."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


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
    status: ResultStatus
    duration: float
    logs: List[LogEntry] = field(default_factory=list)
    browser_actions: List[BrowserAction] = field(default_factory=list)
    error_message: Optional[str] = None
    step_path: Optional[Path] = None
    attempt: int = 1
    screenshot_path: Optional[Path] = None

    @property
    def success(self) -> bool:
        """Check if test passed."""
        return self.status == ResultStatus.PASSED

    @property
    def passed(self) -> bool:
        """Alias for success."""
        return self.success

    @property
    def failed(self) -> bool:
        """Check if test failed."""
        return self.status == ResultStatus.FAILED

    @property
    def retry_count(self) -> int:
        """Number of retries (attempt - 1)."""
        return self.attempt - 1


@dataclass
class SuiteResult:
    """Result of executing a test suite."""

    suite_name: str
    test_results: List[TestResult]
    total_duration: float
    fuzziness: float = 0.0
    suite_path: Optional[Path] = None
    run_timestamp: datetime = field(default_factory=datetime.now)
    config: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if suite passed based on fuzziness."""
        if not self.test_results:
            return False
        if self.fuzziness == 0.0:
            return self.failed_tests == 0
        # Allow some failures based on fuzziness
        failure_rate = self.failed_tests / self.total_tests
        return failure_rate <= self.fuzziness

    @property
    def status(self) -> ResultStatus:
        """Get overall status of the suite."""
        if self.success:
            return ResultStatus.PASSED
        return ResultStatus.FAILED

    @property
    def total_tests(self) -> int:
        """Total number of tests."""
        return len(self.test_results)

    @property
    def passed_tests(self) -> int:
        """Number of passed tests."""
        return sum(1 for r in self.test_results if r.status == ResultStatus.PASSED)

    @property
    def failed_tests(self) -> int:
        """Number of failed tests."""
        return sum(1 for r in self.test_results if r.status == ResultStatus.FAILED)

    @property
    def skipped_tests(self) -> int:
        """Number of skipped tests."""
        return sum(1 for r in self.test_results if r.status == ResultStatus.SKIPPED)

    @property
    def success_rate(self) -> float:
        """Success rate as percentage (0.0 - 100.0)."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100.0
