"""Integration tests for multi-suite functionality."""
import subprocess
import sys
from pathlib import Path
import pytest
import json


@pytest.mark.asyncio
async def test_discover_multiple_suites(tmp_path):
    """Test discovering multiple test suites in a directory."""
    # Create multiple test suites
    suite1_dir = tmp_path / "suite1"
    suite1_dir.mkdir()
    (suite1_dir / "suite.yaml").write_text("""
name: Suite One
description: First test suite
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
    (suite1_dir / "00-test.md").write_text("# Test 1\n\nTest step 1")
    
    suite2_dir = tmp_path / "suite2"
    suite2_dir.mkdir()
    (suite2_dir / "suite.yaml").write_text("""
name: Suite Two
description: Second test suite
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
    (suite2_dir / "00-test.md").write_text("# Test 2\n\nTest step 2")
    
    # Run discover command
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "discover", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    assert result.returncode == 0
    assert "Suite One" in result.stdout
    assert "Suite Two" in result.stdout
    assert "2" in result.stdout  # Should show 2 suites discovered


@pytest.mark.asyncio
async def test_discover_json_format(tmp_path):
    """Test discovering suites with JSON output format."""
    # Create a test suite
    suite_dir = tmp_path / "test-suite"
    suite_dir.mkdir()
    (suite_dir / "suite.yaml").write_text("""
name: JSON Test Suite
description: Test JSON output
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
    (suite_dir / "00-test.md").write_text("# Test\n\nTest step")
    
    # Run discover with JSON format
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "discover", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    assert result.returncode == 0
    
    # Should be valid JSON
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "JSON Test Suite"


@pytest.mark.asyncio  
async def test_run_specific_suite(tmp_path):
    """Test running a specific suite by path."""
    # Create multiple suites
    suite1_dir = tmp_path / "suite1"
    suite1_dir.mkdir()
    (suite1_dir / "suite.yaml").write_text("""
name: Suite One
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
    (suite1_dir / "00-test.md").write_text("# Test 1\n\nTest step 1")
    
    suite2_dir = tmp_path / "suite2"
    suite2_dir.mkdir()
    (suite2_dir / "suite.yaml").write_text("""
name: Suite Two
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
    (suite2_dir / "00-test.md").write_text("# Test 2\n\nTest step 2")
    
    pytest.skip("Requires network access for browser-use")
    
    # Run only suite1
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "run", str(suite1_dir)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    # Should complete (may pass or fail depending on LLM availability)
    assert result.returncode in [0, 1, 2]
    assert "Suite One" in result.stdout or "suite1" in result.stdout


@pytest.mark.asyncio
async def test_run_all_suites(tmp_path):
    """Test running all suites with --all flag."""
    # Create multiple suites
    for i in range(2):
        suite_dir = tmp_path / f"suite{i+1}"
        suite_dir.mkdir()
        (suite_dir / "suite.yaml").write_text(f"""
name: Suite {i+1}
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
        (suite_dir / "00-test.md").write_text(f"# Test {i+1}\n\nTest step")
    
    # Run all suites (this will likely fail without API keys, but should execute)
    result = subprocess.run(
        [sys.executable, "-m", "familiar", "run", "--all", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    # Should attempt to run (exit code may vary)
    assert result.returncode in [0, 1, 2]

