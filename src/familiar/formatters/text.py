"""Text formatter for human-readable test results."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from familiar.models.result import ResultStatus, SuiteResult


class TextFormatter:
    """Formats test results as human-readable text with Rich formatting.

    Provides colorful, structured output for terminal display.
    """

    def __init__(self, verbose: bool = False):
        """Initialize the text formatter.

        Args:
            verbose: Whether to include detailed logs and actions.
        """
        self.verbose = verbose
        self.console = Console()

    def format(self, result: SuiteResult) -> str:
        """Format a suite result as human-readable text.

        Args:
            result: The suite result to format.

        Returns:
            Formatted text output.
        """
        # Build output parts
        parts = []

        # Suite header
        parts.append(self._format_header(result))

        # Test results table
        parts.append(self._format_results_table(result))

        # Summary
        parts.append(self._format_summary(result))

        # Detailed logs if verbose
        if self.verbose:
            parts.append(self._format_detailed_logs(result))

        return "\n\n".join(parts)

    def print(self, result: SuiteResult) -> None:
        """Print formatted result to console.

        Args:
            result: The suite result to print.
        """
        # Print header
        self._print_header(result)

        # Print results table
        self._print_results_table(result)

        # Print summary
        self._print_summary(result)

        # Print detailed logs if verbose
        if self.verbose:
            self._print_detailed_logs(result)

    def _format_header(self, result: SuiteResult) -> str:
        """Format suite header."""
        status_icon = "✓" if result.success else "✗"
        status_color = "green" if result.success else "red"
        return f"[bold]{status_icon} Test Suite: {result.suite_name}[/bold] [{status_color}]{result.status.value.upper()}[/{status_color}]"

    def _print_header(self, result: SuiteResult) -> None:
        """Print suite header."""
        status_icon = "✓" if result.success else "✗"
        status_color = "green" if result.success else "red"

        title = f"{status_icon} {result.suite_name}"
        subtitle = f"[{status_color}]{result.status.value.upper()}[/{status_color}]"

        self.console.print(
            Panel(
                subtitle,
                title=title,
                border_style=status_color,
            )
        )

    def _format_results_table(self, result: SuiteResult) -> str:
        """Format test results as a table."""
        lines = []
        lines.append("Test Results:")
        lines.append("=" * 60)

        for test in result.test_results:
            status_icon = "✓" if test.status == ResultStatus.PASSED else "✗"
            duration = f"{test.duration:.2f}s"
            retry_info = f" (retries: {test.retry_count})" if test.retry_count > 0 else ""
            lines.append(f"  {status_icon} {test.step_name} ({duration}){retry_info}")

            if test.error_message:
                lines.append(f"    Error: {test.error_message}")

        return "\n".join(lines)

    def _print_results_table(self, result: SuiteResult) -> None:
        """Print test results as a table."""
        table = Table(title="Test Results", show_header=True, header_style="bold")

        table.add_column("Status", width=8)
        table.add_column("Step", style="cyan")
        table.add_column("Duration", justify="right", width=10)
        table.add_column("Retries", justify="right", width=8)

        for test in result.test_results:
            status_text = Text()
            if test.status == ResultStatus.PASSED:
                status_text.append("✓ PASS", style="green")
            elif test.status == ResultStatus.FAILED:
                status_text.append("✗ FAIL", style="red")
            else:
                status_text.append("○ SKIP", style="yellow")

            duration = f"{test.duration:.2f}s"

            # Show retry count if there were retries
            retry_text = Text()
            if test.retry_count > 0:
                retry_text.append(str(test.retry_count), style="yellow")
            else:
                retry_text.append("-", style="dim")

            table.add_row(
                status_text,
                test.step_name,
                duration,
                retry_text,
            )

        self.console.print(table)

    def _format_summary(self, result: SuiteResult) -> str:
        """Format result summary."""
        lines = []
        lines.append("Summary:")
        lines.append("=" * 60)
        lines.append(f"  Total Tests: {result.total_tests}")
        lines.append(f"  Passed: {result.passed_tests}")
        lines.append(f"  Failed: {result.failed_tests}")
        lines.append(f"  Skipped: {result.skipped_tests}")
        lines.append(f"  Duration: {result.total_duration:.2f}s")
        lines.append(f"  Success Rate: {result.success_rate:.1f}%")

        return "\n".join(lines)

    def _print_summary(self, result: SuiteResult) -> None:
        """Print result summary."""
        # Create summary table
        table = Table(title="Summary", show_header=False, box=None)
        table.add_column("Metric", style="bold")
        table.add_column("Value")

        table.add_row("Total Tests", str(result.total_tests))
        table.add_row("Passed", f"[green]{result.passed_tests}[/green]")
        table.add_row("Failed", f"[red]{result.failed_tests}[/red]")
        table.add_row("Skipped", f"[yellow]{result.skipped_tests}[/yellow]")
        table.add_row("Duration", f"{result.total_duration:.2f}s")
        table.add_row("Success Rate", f"{result.success_rate:.1f}%")

        self.console.print(table)

    def _format_detailed_logs(self, result: SuiteResult) -> str:
        """Format detailed logs for verbose output."""
        lines = []
        lines.append("Detailed Logs:")
        lines.append("=" * 60)

        for test in result.test_results:
            lines.append(f"\n{test.step_name}:")
            for log in test.logs:
                timestamp = log.timestamp.strftime("%H:%M:%S")
                lines.append(f"  [{timestamp}] {log.level.value}: {log.message}")

        return "\n".join(lines)

    def _print_detailed_logs(self, result: SuiteResult) -> None:
        """Print detailed logs for verbose output."""
        for test in result.test_results:
            self.console.print(f"\n[bold]Logs for: {test.step_name}[/bold]")

            for log in test.logs:
                timestamp = log.timestamp.strftime("%H:%M:%S")

                # Color based on log level
                if log.level.value == "error":
                    color = "red"
                elif log.level.value == "warning":
                    color = "yellow"
                elif log.level.value == "debug":
                    color = "dim"
                else:
                    color = "white"

                self.console.print(
                    f"[{color}][{timestamp}] {log.level.value.upper()}: {log.message}[/{color}]"
                )
