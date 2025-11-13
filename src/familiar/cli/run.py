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
    if format != "text":
        click.echo(f"⚠️  Format '{format}' not yet implemented, using text", err=True)
    
    if run_all:
        click.echo("❌ --all flag not yet implemented", err=True)
        sys.exit(1)
    
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

