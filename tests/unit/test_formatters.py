"""Unit tests for result formatters."""
import json
from datetime import datetime
from pathlib import Path
from familiar.formatters.json import JSONFormatter
from familiar.models.result import SuiteResult, TestResult, ResultStatus, LogEntry, LogLevel


class TestJSONFormatter:
    """Tests for JSON formatter."""
    
    def test_json_format_suite_result(self):
        """Test formatting a suite result."""
        result = SuiteResult(
            suite_name="Test Suite",
            test_results=[
                TestResult(
                    step_name="Step 1",
                    status=ResultStatus.PASSED,
                    duration=1.5,
                )
            ],
            total_duration=1.5,
        )
        
        formatter = JSONFormatter(pretty=True)
        output = formatter.format(result)
        
        # Verify valid JSON
        data = json.loads(output)
        assert data["suite_name"] == "Test Suite"
        assert data["total_tests"] == 1
        assert data["passed_tests"] == 1
        assert data["failed_tests"] == 0
        assert data["success"] is True
    
    def test_json_format_pretty_true(self):
        """Test JSON formatting with pretty=True."""
        result = SuiteResult(
            suite_name="Pretty Test",
            test_results=[
                TestResult(
                    step_name="Step",
                    status=ResultStatus.PASSED,
                    duration=1.0,
                )
            ],
            total_duration=1.0,
        )
        
        formatter = JSONFormatter(pretty=True)
        output = formatter.format(result)
        
        # Pretty JSON should have newlines and indentation
        assert "\n" in output
        assert "  " in output  # Indentation
        
        # Should still be valid JSON
        data = json.loads(output)
        assert data["suite_name"] == "Pretty Test"
    
    def test_json_format_pretty_false(self):
        """Test JSON formatting with pretty=False (compact)."""
        result = SuiteResult(
            suite_name="Compact Test",
            test_results=[
                TestResult(
                    step_name="Step",
                    status=ResultStatus.PASSED,
                    duration=1.0,
                )
            ],
            total_duration=1.0,
        )
        
        formatter = JSONFormatter(pretty=False)
        output = formatter.format(result)
        
        # Compact JSON should be single line (minimal whitespace)
        lines = output.strip().split('\n')
        # Should be mostly one line (might have some newlines in nested structures)
        assert len(lines) < 5  # Much less than pretty format
        
        # Should still be valid JSON
        data = json.loads(output)
        assert data["suite_name"] == "Compact Test"
    
    def test_json_format_discovery_with_suites(self):
        """Test formatting discovery results with suite list."""
        # Create mock suite objects
        class MockSuite:
            def __init__(self, name, path, steps_count):
                self.name = name
                self.path = Path(path)
                self.steps = list(range(steps_count))  # Mock steps
                self.config = type('obj', (object,), {'timeout': 300})()
        
        suites = [
            MockSuite("Suite 1", "/path/to/suite1", 3),
            MockSuite("Suite 2", "/path/to/suite2", 5),
        ]
        
        formatter = JSONFormatter(pretty=True)
        output = formatter.format_discovery(suites)
        
        # Verify valid JSON
        data = json.loads(output)
        assert len(data) == 2
        assert data[0]["name"] == "Suite 1"
        assert data[0]["steps"] == 3
        assert data[1]["name"] == "Suite 2"
        assert data[1]["steps"] == 5
    
    def test_json_format_discovery_empty_list(self):
        """Test formatting discovery results with empty list."""
        formatter = JSONFormatter(pretty=True)
        output = formatter.format_discovery([])
        
        # Should return empty JSON array
        data = json.loads(output)
        assert data == []
        assert isinstance(data, list)
    
    def test_json_output_is_valid_json(self):
        """Test that JSON output is always valid and parseable."""
        result = SuiteResult(
            suite_name="Validation Test",
            test_results=[
                TestResult(
                    step_name="Step 1",
                    status=ResultStatus.PASSED,
                    duration=1.0,
                    logs=[
                        LogEntry(
                            timestamp=datetime.now(),
                            level=LogLevel.INFO,
                            message="Test message",
                        )
                    ],
                ),
                TestResult(
                    step_name="Step 2",
                    status=ResultStatus.FAILED,
                    duration=2.0,
                    error_message="Test error",
                ),
            ],
            total_duration=3.0,
        )
        
        formatter = JSONFormatter(pretty=True)
        output = formatter.format(result)
        
        # Should not raise exception
        data = json.loads(output)
        
        # Verify structure
        assert "suite_name" in data
        assert "tests" in data
        assert len(data["tests"]) == 2
        assert data["tests"][0]["logs"]  # Logs should be included
        assert data["tests"][1]["error_message"] == "Test error"
    
    def test_json_format_with_failed_tests(self):
        """Test JSON formatting with failed test results."""
        result = SuiteResult(
            suite_name="Failed Test Suite",
            test_results=[
                TestResult(
                    step_name="Passing Step",
                    status=ResultStatus.PASSED,
                    duration=1.0,
                ),
                TestResult(
                    step_name="Failing Step",
                    status=ResultStatus.FAILED,
                    duration=2.0,
                    error_message="Step failed",
                    attempt=2,  # Had to retry
                ),
            ],
            total_duration=3.0,
        )
        
        formatter = JSONFormatter(pretty=True)
        output = formatter.format(result)
        
        data = json.loads(output)
        assert data["success"] is False  # Suite should be marked as failed
        assert data["passed_tests"] == 1
        assert data["failed_tests"] == 1
        assert data["tests"][1]["status"] == "failed"
        assert data["tests"][1]["error_message"] == "Step failed"
        assert data["tests"][1]["attempt"] == 2
        assert data["tests"][1]["retry_count"] == 1

