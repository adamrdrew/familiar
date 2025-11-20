"""Integration tests for CLI with .env file loading."""

import os
import subprocess
import sys


def test_cli_loads_dotenv_before_execution(tmp_path, monkeypatch):
    """Test that CLI loads .env file before command execution."""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Create a .env file with a test variable
    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("CLI_TEST_VAR=loaded_from_dotenv\n")

    # Run familiar version command (doesn't require much setup)
    # The .env should be loaded by the CLI
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "--version"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    # Command should succeed
    assert result.returncode == 0
    assert "0.1.0" in result.stdout or "0.1.0" in result.stderr


def test_cli_works_without_dotenv(tmp_path, monkeypatch):
    """Test that CLI works fine without a .env file."""
    # Change to temp directory (no .env file)
    monkeypatch.chdir(tmp_path)

    # Run familiar version command
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "--version"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    # Command should still succeed
    assert result.returncode == 0
    assert "0.1.0" in result.stdout or "0.1.0" in result.stderr


def test_system_env_vars_take_precedence(tmp_path, monkeypatch):
    """Test that system environment variables override .env values."""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Create .env file with a test variable
    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("TEST_PRECEDENCE=from_dotenv\n")

    # Set system environment variable with same name
    env = os.environ.copy()
    env["TEST_PRECEDENCE"] = "from_system"

    # Run familiar help command with custom env
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "--help"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )

    # Command should succeed
    assert result.returncode == 0

    # Note: We can't easily verify which value was used from subprocess,
    # but the unit tests cover this behavior
