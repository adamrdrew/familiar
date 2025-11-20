"""JSON formatter for machine-readable test results."""

import json
from typing import Any

from familiar.models.result import SuiteResult, TestResult


class JSONFormatter:
    """Formats test results as JSON for machine consumption.

    Provides structured, parseable output for CI/CD pipelines,
    custom reporting tools, and API integrations.
    """

    def __init__(self, pretty: bool = True):
        """Initialize the JSON formatter.

        Args:
            pretty: Whether to pretty-print JSON (indented).
        """
        self.pretty = pretty

    def format(self, result: SuiteResult) -> str:
        """Format a suite result as JSON string.

        Args:
            result: The suite result to format.

        Returns:
            JSON string representation.
        """
        data = self._suite_to_dict(result)

        if self.pretty:
            return json.dumps(data, indent=2, default=str)
        return json.dumps(data, default=str)

    def format_discovery(self, suites: list[Any]) -> str:
        """Format suite discovery results as JSON.

        Args:
            suites: List of discovered TestSuite objects.

        Returns:
            JSON array of suite metadata.
        """
        data = []
        for suite in suites:
            data.append(
                {
                    "name": suite.name,
                    "path": str(suite.path),
                    "steps": len(suite.steps),
                    "timeout": suite.config.timeout if hasattr(suite, "config") else None,
                }
            )

        if self.pretty:
            return json.dumps(data, indent=2, default=str)
        return json.dumps(data, default=str)

    def _suite_to_dict(self, result: SuiteResult) -> dict[str, Any]:
        """Convert SuiteResult to dictionary.

        Args:
            result: The suite result to convert.

        Returns:
            Dictionary representation.
        """
        return {
            "suite_name": result.suite_name,
            "status": result.status.value,
            "success": result.success,
            "total_tests": result.total_tests,
            "passed_tests": result.passed_tests,
            "failed_tests": result.failed_tests,
            "skipped_tests": result.skipped_tests,
            "total_duration": result.total_duration,
            "success_rate": result.success_rate,
            "fuzziness": result.fuzziness,
            "run_timestamp": result.run_timestamp.isoformat(),
            "tests": [self._test_to_dict(test) for test in result.test_results],
        }

    def _test_to_dict(self, test: TestResult) -> dict[str, Any]:
        """Convert TestResult to dictionary.

        Args:
            test: The test result to convert.

        Returns:
            Dictionary representation.
        """
        return {
            "step_name": test.step_name,
            "status": test.status.value,
            "duration": test.duration,
            "error_message": test.error_message,
            "attempt": test.attempt,
            "retry_count": test.retry_count,
            "logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level.value,
                    "message": log.message,
                }
                for log in test.logs
            ],
            "browser_actions": [
                {
                    "type": action.type.value,
                    "target": action.target,
                    "success": action.success,
                    "timestamp": action.timestamp.isoformat(),
                }
                for action in test.browser_actions
            ],
        }
