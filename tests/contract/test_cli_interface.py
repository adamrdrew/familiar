"""Contract tests for CLI interface.

These tests validate that the CLI follows the interface specification
defined in contracts/cli-interface.md.
"""
import subprocess
import sys


def test_cli_version():
    """Test that --version option displays version."""
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_cli_help():
    """Test that --help displays available commands."""
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "run" in result.stdout
    assert "discover" in result.stdout
    assert "AI-driven end-to-end testing tool" in result.stdout


def test_run_command_interface():
    """Test that run command has expected options and arguments."""
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "run", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--format" in result.stdout
    assert "--headless" in result.stdout
    assert "--all" in result.stdout
    assert "Run test suites" in result.stdout

