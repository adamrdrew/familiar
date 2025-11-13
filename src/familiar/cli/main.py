"""Main CLI entry point."""
import json
from pathlib import Path
from typing import Optional

import click

from familiar.core.discovery import TestSuiteDiscovery


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Familiar: AI-driven end-to-end testing tool."""
    pass


@cli.command()
@click.argument("suite_path_or_name", required=False)
@click.option("--all", "-a", "run_all", is_flag=True, help="Run all discovered suites")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json", "junit"]),
    default="text",
    help="Output format",
)
@click.option("--headless/--headed", default=True, help="Browser display mode")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed logs")
def run(
    suite_path_or_name: Optional[str],
    run_all: bool,
    format: str,
    headless: bool,
    verbose: bool,
) -> None:
    """Run test suites."""
    from familiar.cli.run import run_suite_command
    
    run_suite_command(
        suite_path_or_name=suite_path_or_name,
        run_all=run_all,
        format=format,
        headless=headless,
        verbose=verbose,
    )


@cli.command()
@click.argument(
    "directory", required=False, type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text", help="Output format"
)
def discover(directory: Optional[Path], format: str) -> None:
    """Discover test suites."""
    root_dir = directory or Path("./familiar")
    discovery = TestSuiteDiscovery()
    suites = discovery.discover_suites(root_dir)

    if format == "text":
        click.echo(f"\nDiscovered {len(suites)} suites in: {root_dir}\n")
        for i, suite in enumerate(suites, 1):
            click.echo(f"{i}. {suite.name}")
            click.echo(f"   Path: {suite.path}")
            click.echo(f"   Steps: {len(suite.steps)}")
            click.echo()
    else:
        data = [
            {"name": s.name, "path": str(s.path), "steps": len(s.steps)} for s in suites
        ]
        click.echo(json.dumps(data, indent=2))


if __name__ == "__main__":
    cli()

