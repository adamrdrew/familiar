"""Run command implementation."""
import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from familiar.core.parser import SuiteParser
from familiar.core.runner import SuiteRunner
from familiar.formatters.text import TextFormatter
from familiar.logging.handlers import setup_rich_logging


async def run_suite_async(
    suite_path: Path,
    headless: bool,
    verbose: bool,
) -> int:
    """Run a single test suite asynchronously.
    
    Args:
        suite_path: Path to the test suite directory.
        headless: Whether to run browser in headless mode.
        verbose: Whether to show detailed logs.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_rich_logging(level=log_level)
    
    try:
        # Parse the suite
        parser = SuiteParser()
        suite = parser.parse_suite(suite_path)
        
        click.echo(f"\n🚀 Running test suite: [bold]{suite.name}[/bold]\n", nl=True)
        
        # Run the suite
        runner = SuiteRunner(headless=headless)
        result = await runner.run_suite(suite)
        
        # Format and display results
        formatter = TextFormatter(verbose=verbose)
        formatter.print(result)
        
        # Return appropriate exit code
        return 0 if result.success else 1
        
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        return 2
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        return 2


async def run_all_suites_async(
    directory: Path,
    headless: bool,
    verbose: bool,
    format: str,
) -> int:
    """Run all test suites in a directory asynchronously.
    
    Args:
        directory: Directory containing test suites.
        headless: Whether to run browser in headless mode.
        verbose: Whether to show detailed logs.
        format: Output format (text, json, junit).
    
    Returns:
        Exit code (0 if all pass, 1 if any fail).
    """
    from familiar.core.discovery import TestSuiteDiscovery
    from familiar.formatters.json import JSONFormatter
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_rich_logging(level=log_level)
    
    # Discover all suites
    discovery = TestSuiteDiscovery()
    suites = discovery.discover_suites(directory)
    
    if not suites:
        click.echo(f"❌ No test suites found in: {directory}", err=True)
        return 2
    
    click.echo(f"\n🚀 Running {len(suites)} test suites from: {directory}\n")
    
    # Run each suite
    runner = SuiteRunner(headless=headless)
    results = []
    
    for i, suite in enumerate(suites, 1):
        click.echo(f"[{i}/{len(suites)}] Running: {suite.name}")
        result = await runner.run_suite(suite)
        results.append(result)
        
        # Show brief result
        status_icon = "✓" if result.success else "✗"
        status_color = "green" if result.success else "red"
        click.echo(f"  {status_icon} {suite.name}: {result.passed_tests}/{result.total_tests} passed")
    
    # Display summary
    click.echo("\n" + "=" * 60)
    click.echo("SUMMARY")
    click.echo("=" * 60 + "\n")
    
    total_suites = len(results)
    passed_suites = sum(1 for r in results if r.success)
    failed_suites = total_suites - passed_suites
    
    total_tests = sum(r.total_tests for r in results)
    total_passed = sum(r.passed_tests for r in results)
    total_failed = sum(r.failed_tests for r in results)
    total_duration = sum(r.total_duration for r in results)
    
    click.echo(f"Suites: {passed_suites}/{total_suites} passed")
    click.echo(f"Tests:  {total_passed}/{total_tests} passed")
    click.echo(f"Duration: {total_duration:.2f}s")
    
    if format == "json":
        json_formatter = JSONFormatter(pretty=True)
        json_results = {
            "summary": {
                "total_suites": total_suites,
                "passed_suites": passed_suites,
                "failed_suites": failed_suites,
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": total_failed,
                "total_duration": total_duration,
            },
            "suites": [json.loads(json_formatter.format(r)) for r in results],
        }
        click.echo("\n" + json.dumps(json_results, indent=2))
    
    return 0 if failed_suites == 0 else 1


def run_suite_command(
    suite_path_or_name: Optional[str],
    run_all: bool,
    format: str,
    headless: bool,
    verbose: bool,
) -> None:
    """Run test suites command handler.
    
    Args:
        suite_path_or_name: Path or name of the suite to run.
        run_all: Whether to run all discovered suites.
        format: Output format (text, json, junit).
        headless: Whether to run browser in headless mode.
        verbose: Whether to show detailed logs.
    """
    import json
    
    if format == "junit":
        click.echo(f"⚠️  Format 'junit' not yet implemented, using text", err=True)
        format = "text"
    
    # Handle --all flag
    if run_all:
        if not suite_path_or_name:
            directory = Path("./familiar")
        else:
            directory = Path(suite_path_or_name)
        
        if not directory.exists():
            click.echo(f"❌ Error: Directory does not exist: {directory}", err=True)
            sys.exit(2)
        
        if not directory.is_dir():
            click.echo(f"❌ Error: Path is not a directory: {directory}", err=True)
            sys.exit(2)
        
        # Run all suites
        exit_code = asyncio.run(run_all_suites_async(
            directory=directory,
            headless=headless,
            verbose=verbose,
            format=format,
        ))
        sys.exit(exit_code)
    
    # Run single suite
    if not suite_path_or_name:
        click.echo("❌ Error: Please specify a suite path or use --all", err=True)
        sys.exit(1)
    
    # Convert to Path
    suite_path = Path(suite_path_or_name)
    
    if not suite_path.exists():
        click.echo(f"❌ Error: Suite path does not exist: {suite_path}", err=True)
        sys.exit(2)
    
    # Run the suite
    exit_code = asyncio.run(run_suite_async(
        suite_path=suite_path,
        headless=headless,
        verbose=verbose,
    ))
    
    sys.exit(exit_code)

