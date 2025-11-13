"""Test data models."""
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from familiar.models.result import SuiteResult, TestResult
from familiar.models.step import TestStep
from familiar.models.suite import RetryPolicyConfig, SuiteConfig, TestSuite


def test_suite_config_validates_timeout() -> None:
    """Test that step_timeout cannot exceed timeout."""
    with pytest.raises(ValidationError, match="cannot exceed timeout"):
        SuiteConfig(
            name="Test Suite",
            timeout=30,
            step_timeout=60,  # Invalid: exceeds timeout
        )


def test_suite_config_defaults() -> None:
    """Test default values are applied."""
    config = SuiteConfig(name="Test Suite")
    assert config.timeout == 300
    assert config.step_timeout == 30
    assert config.fuzziness == 0.0
    assert config.temperature == 0.7
    assert config.retry_policy.type == "fixed"
    assert config.retry_policy.max_retries == 3


def test_retry_policy_config_validates_type() -> None:
    """Test retry policy type validation."""
    # Valid types
    RetryPolicyConfig(type="fixed")
    RetryPolicyConfig(type="exponential")
    RetryPolicyConfig(type="best_of_n")

    # Invalid type
    with pytest.raises(ValidationError):
        RetryPolicyConfig(type="invalid")


def test_test_step_extracts_name_from_heading() -> None:
    """Test step name extraction from markdown."""
    step = TestStep(
        path=Path("00-login.md"),
        content="# Step: Login to Dashboard\n\nNavigate to login page",
        order=0,
    )
    assert step.name == "Login to Dashboard"


def test_test_step_extracts_name_without_step_prefix() -> None:
    """Test step name extraction without 'Step:' prefix."""
    step = TestStep(
        path=Path("00-login.md"),
        content="# Login to Dashboard\n\nNavigate to login page",
        order=0,
    )
    assert step.name == "Login to Dashboard"


def test_test_step_uses_filename_if_no_heading() -> None:
    """Test fallback to filename when no heading."""
    step = TestStep(
        path=Path("00-login.md"),
        content="Navigate to login page",
        order=0,
    )
    assert step.name == "00-login"


def test_test_step_extracts_variables() -> None:
    """Test variable extraction from content."""
    step = TestStep(
        path=Path("00-test.md"),
        content="Navigate to ${BASE_URL}/login\nUser: ${TEST_USER}\nDefault: ${VAR:-default}",
        order=0,
    )
    assert step.variables == {"BASE_URL", "TEST_USER", "VAR"}


def test_test_result_properties() -> None:
    """Test TestResult computed properties."""
    result = TestResult(
        step_name="Login",
        step_path=Path("00-login.md"),
        success=True,
        duration=5.2,
        attempt=2,
    )
    assert result.passed is True
    assert result.failed is False
    assert result.retry_count == 1


def test_suite_result_success_with_zero_fuzziness() -> None:
    """Test suite success with no fuzziness."""
    result1 = TestResult(
        step_name="Step 1",
        step_path=Path("00-step.md"),
        success=True,
        duration=1.0,
        attempt=1,
    )
    result2 = TestResult(
        step_name="Step 2",
        step_path=Path("01-step.md"),
        success=False,
        duration=1.0,
        attempt=1,
    )

    suite_result = SuiteResult(
        suite_name="Test",
        suite_path=Path("test"),
        step_results=[result1, result2],
        duration=2.0,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        config_fuzziness=0.0,
    )

    assert suite_result.total_count == 2
    assert suite_result.passed_count == 1
    assert suite_result.failed_count == 1
    assert suite_result.pass_rate == 0.5
    assert not suite_result.success  # 50% < 100% required


def test_suite_result_success_with_fuzziness() -> None:
    """Test suite success calculation with fuzziness."""
    result1 = TestResult(
        step_name="Step 1",
        step_path=Path("00-step.md"),
        success=True,
        duration=1.0,
        attempt=1,
    )
    result2 = TestResult(
        step_name="Step 2",
        step_path=Path("01-step.md"),
        success=False,
        duration=1.0,
        attempt=1,
    )

    # 50% pass rate, 10% fuzziness (90% required) = FAIL
    suite_result = SuiteResult(
        suite_name="Test",
        suite_path=Path("test"),
        step_results=[result1, result2],
        duration=2.0,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        config_fuzziness=0.1,
    )
    assert not suite_result.success

    # 50% pass rate, 50% fuzziness (50% required) = PASS
    suite_result.config_fuzziness = 0.5
    assert suite_result.success

