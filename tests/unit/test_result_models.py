"""Unit tests for result model properties and calculations."""

from familiar.models.result import ResultStatus, SuiteResult, TestResult


class TestTestResult:
    """Tests for TestResult properties."""

    def test_success_property(self):
        """Test success property returns True for passed tests."""
        result = TestResult(
            step_name="Test Step",
            status=ResultStatus.PASSED,
            duration=1.0,
        )
        assert result.success is True
        assert result.passed is True  # Alias
        assert result.failed is False

    def test_failed_property(self):
        """Test failed property returns True for failed tests."""
        result = TestResult(
            step_name="Test Step",
            status=ResultStatus.FAILED,
            duration=1.0,
        )
        assert result.success is False
        assert result.passed is False
        assert result.failed is True

    def test_retry_count_calculation(self):
        """Test retry count calculation from attempt."""
        # First attempt (no retries)
        result1 = TestResult(
            step_name="Test",
            status=ResultStatus.PASSED,
            duration=1.0,
            attempt=1,
        )
        assert result1.retry_count == 0

        # Second attempt (1 retry)
        result2 = TestResult(
            step_name="Test",
            status=ResultStatus.PASSED,
            duration=1.0,
            attempt=2,
        )
        assert result2.retry_count == 1

        # Fourth attempt (3 retries)
        result3 = TestResult(
            step_name="Test",
            status=ResultStatus.PASSED,
            duration=1.0,
            attempt=4,
        )
        assert result3.retry_count == 3


class TestSuiteResult:
    """Tests for SuiteResult properties."""

    def test_suite_success_no_fuzziness(self):
        """Test suite success requires all tests pass when fuzziness=0."""
        # All passed
        result_all_pass = SuiteResult(
            suite_name="Test",
            test_results=[
                TestResult("Step 1", ResultStatus.PASSED, 1.0),
                TestResult("Step 2", ResultStatus.PASSED, 1.0),
            ],
            total_duration=2.0,
            fuzziness=0.0,
        )
        assert result_all_pass.success is True

        # One failed with no fuzziness
        result_one_fail = SuiteResult(
            suite_name="Test",
            test_results=[
                TestResult("Step 1", ResultStatus.PASSED, 1.0),
                TestResult("Step 2", ResultStatus.FAILED, 1.0),
            ],
            total_duration=2.0,
            fuzziness=0.0,
        )
        assert result_one_fail.success is False

    def test_suite_success_with_fuzziness(self):
        """Test suite success allows failures with fuzziness>0."""
        # 1 failure out of 5 = 20% failure rate
        # With 20% fuzziness, should still pass
        result = SuiteResult(
            suite_name="Test",
            test_results=[
                TestResult("Step 1", ResultStatus.PASSED, 1.0),
                TestResult("Step 2", ResultStatus.PASSED, 1.0),
                TestResult("Step 3", ResultStatus.PASSED, 1.0),
                TestResult("Step 4", ResultStatus.PASSED, 1.0),
                TestResult("Step 5", ResultStatus.FAILED, 1.0),
            ],
            total_duration=5.0,
            fuzziness=0.2,  # 20% tolerance
        )
        assert result.success is True

        # 2 failures out of 5 = 40% failure rate
        # With 20% fuzziness, should fail
        result2 = SuiteResult(
            suite_name="Test",
            test_results=[
                TestResult("Step 1", ResultStatus.PASSED, 1.0),
                TestResult("Step 2", ResultStatus.PASSED, 1.0),
                TestResult("Step 3", ResultStatus.PASSED, 1.0),
                TestResult("Step 4", ResultStatus.FAILED, 1.0),
                TestResult("Step 5", ResultStatus.FAILED, 1.0),
            ],
            total_duration=5.0,
            fuzziness=0.2,  # 20% tolerance
        )
        assert result2.success is False

    def test_suite_success_rate_calculation(self):
        """Test success rate percentage calculation."""
        # 100% success
        result1 = SuiteResult(
            suite_name="Test",
            test_results=[
                TestResult("Step 1", ResultStatus.PASSED, 1.0),
                TestResult("Step 2", ResultStatus.PASSED, 1.0),
            ],
            total_duration=2.0,
        )
        assert result1.success_rate == 100.0

        # 50% success
        result2 = SuiteResult(
            suite_name="Test",
            test_results=[
                TestResult("Step 1", ResultStatus.PASSED, 1.0),
                TestResult("Step 2", ResultStatus.FAILED, 1.0),
            ],
            total_duration=2.0,
        )
        assert result2.success_rate == 50.0

        # 0% success
        result3 = SuiteResult(
            suite_name="Test",
            test_results=[
                TestResult("Step 1", ResultStatus.FAILED, 1.0),
                TestResult("Step 2", ResultStatus.FAILED, 1.0),
            ],
            total_duration=2.0,
        )
        assert result3.success_rate == 0.0

        # Empty results
        result4 = SuiteResult(
            suite_name="Test",
            test_results=[],
            total_duration=0.0,
        )
        assert result4.success_rate == 0.0
