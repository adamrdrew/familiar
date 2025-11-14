"""Test data models."""

from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from familiar.models.result import SuiteResult, TestResult
from familiar.models.step import TestStep
from familiar.models.suite import BrowserProfileConfig, RetryPolicyConfig, SuiteConfig, TestSuite


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
    from familiar.models.result import ResultStatus

    result = TestResult(
        step_name="Login",
        status=ResultStatus.PASSED,
        duration=5.2,
        attempt=2,
    )
    assert result.passed is True
    assert result.failed is False
    assert result.success is True
    assert result.retry_count == 1


def test_suite_result_success_with_zero_fuzziness() -> None:
    """Test suite success with no fuzziness."""
    from familiar.models.result import ResultStatus

    result1 = TestResult(
        step_name="Step 1",
        status=ResultStatus.PASSED,
        duration=1.0,
    )
    result2 = TestResult(
        step_name="Step 2",
        status=ResultStatus.FAILED,
        duration=1.0,
    )

    suite_result = SuiteResult(
        suite_name="Test",
        test_results=[result1, result2],
        total_duration=2.0,
        fuzziness=0.0,
    )

    assert suite_result.total_tests == 2
    assert suite_result.passed_tests == 1
    assert suite_result.failed_tests == 1
    assert suite_result.success_rate == 50.0
    assert not suite_result.success  # 50% < 100% required


def test_suite_result_success_with_fuzziness() -> None:
    """Test suite success calculation with fuzziness."""
    from familiar.models.result import ResultStatus

    result1 = TestResult(
        step_name="Step 1",
        status=ResultStatus.PASSED,
        duration=1.0,
    )
    result2 = TestResult(
        step_name="Step 2",
        status=ResultStatus.FAILED,
        duration=1.0,
    )

    # 50% failure rate, 10% fuzziness (allow 10% failures) = FAIL
    suite_result = SuiteResult(
        suite_name="Test",
        test_results=[result1, result2],
        total_duration=2.0,
        fuzziness=0.1,
    )
    assert not suite_result.success

    # 50% failure rate, 50% fuzziness (allow 50% failures) = PASS
    suite_result2 = SuiteResult(
        suite_name="Test",
        test_results=[result1, result2],
        total_duration=2.0,
        fuzziness=0.5,
    )
    assert suite_result2.success


# BrowserProfileConfig Tests


def test_browser_profile_config_defaults() -> None:
    """Default values should be 1.0s waits, headless."""
    config = BrowserProfileConfig()
    assert config.minimum_wait_page_load_time == 1.0
    assert config.wait_between_actions == 1.0
    assert config.headless is True


def test_browser_profile_config_custom_values() -> None:
    """Custom values should be preserved."""
    config = BrowserProfileConfig(
        minimum_wait_page_load_time=0.1,
        wait_between_actions=0.2,
        headless=False,
    )
    assert config.minimum_wait_page_load_time == 0.1
    assert config.wait_between_actions == 0.2
    assert config.headless is False


def test_browser_profile_config_validation_negative() -> None:
    """Negative wait times should raise error."""
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        BrowserProfileConfig(minimum_wait_page_load_time=-1.0)


def test_browser_profile_config_validation_too_long() -> None:
    """Wait times above 30s should raise error."""
    with pytest.raises(ValidationError, match="less than or equal to 30"):
        BrowserProfileConfig(wait_between_actions=100.0)


def test_browser_profile_config_to_browser_profile() -> None:
    """Conversion to browser-use BrowserProfile should work."""
    from browser_use import BrowserProfile

    config = BrowserProfileConfig(
        minimum_wait_page_load_time=0.5,
        wait_between_actions=0.3,
        headless=False,
    )

    profile = config.to_browser_profile()

    assert isinstance(profile, BrowserProfile)
    assert profile.minimum_wait_page_load_time == 0.5
    assert profile.wait_between_actions == 0.3
    assert profile.headless is False


def test_suite_config_browser_profile_optional() -> None:
    """Suite config should work without browser_profile field."""
    config = SuiteConfig(name="Test Suite")
    assert config.browser_profile is None

    # get_browser_profile() should return defaults
    profile = config.get_browser_profile()
    assert isinstance(profile, BrowserProfileConfig)
    assert profile.minimum_wait_page_load_time == 1.0
    assert profile.wait_between_actions == 1.0
    assert profile.headless is True


def test_suite_config_browser_profile_custom() -> None:
    """Suite config should parse nested browser_profile."""
    config = SuiteConfig(
        name="Test Suite",
        browser_profile=BrowserProfileConfig(
            minimum_wait_page_load_time=0.1,
            wait_between_actions=0.1,
            headless=False,
        ),
    )

    assert config.browser_profile is not None
    assert config.browser_profile.minimum_wait_page_load_time == 0.1
    assert config.browser_profile.wait_between_actions == 0.1
    assert config.browser_profile.headless is False

    # get_browser_profile() should return the custom config
    profile = config.get_browser_profile()
    assert profile.minimum_wait_page_load_time == 0.1
