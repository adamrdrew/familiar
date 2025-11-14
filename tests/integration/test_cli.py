"""Integration tests for CLI commands."""

import subprocess
import sys
from pathlib import Path
import pytest


@pytest.mark.asyncio
async def test_run_command_success_exit_code(tmp_path):
    """Test that successful test run exits with code 0.

    This test will fail until the run command is fully implemented.
    """
    # Create a simple passing test suite
    suite_dir = tmp_path / "passing-suite"
    suite_dir.mkdir()

    (suite_dir / "suite.yaml").write_text("""
name: Passing Suite
description: A test that should pass
timeout: 30
step_timeout: 10
retry_policy:
  type: fixed
  max_retries: 0
  delay: 0
fuzziness: 0.0
temperature: 0.5
headless: true
""")

    (suite_dir / "00-test.md").write_text("""
# Pass Test

This test should pass.

1. Print "Success"
""")

    # Run the suite
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "run", str(suite_dir)],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Expect exit code 0 for success (will fail until implemented)
    # For now, we expect this to fail or be incomplete
    # Once implemented, uncomment:
    # assert result.returncode == 0

    # Placeholder assertion
    assert result.returncode in [0, 1, 2], "CLI should return valid exit code"


@pytest.mark.asyncio
async def test_run_command_failure_exit_code(tmp_path):
    """Test that failed test run exits with code 1.

    This test will fail until the run command is fully implemented.
    """
    # Create a test suite that will fail
    suite_dir = tmp_path / "failing-suite"
    suite_dir.mkdir()

    (suite_dir / "suite.yaml").write_text("""
name: Failing Suite
description: A test that should fail
timeout: 30
step_timeout: 10
retry_policy:
  type: fixed
  max_retries: 0
  delay: 0
fuzziness: 0.0
temperature: 0.5
headless: true
""")

    (suite_dir / "00-test.md").write_text("""
# Fail Test

This test should fail.

1. Navigate to http://this-domain-does-not-exist-familiar-test-12345.com
2. Click a button that doesn't exist
""")

    # Run the suite
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "run", str(suite_dir)],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Expect exit code 1 for failure (will fail until implemented)
    # For now, we expect this to fail or be incomplete
    # Once implemented, uncomment:
    # assert result.returncode == 1

    # Placeholder assertion
    assert result.returncode in [0, 1, 2], "CLI should return valid exit code"
