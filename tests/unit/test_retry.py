"""Unit tests for retry policies."""

import pytest
import asyncio
from datetime import datetime, timedelta

from familiar.core.retry import RetryPolicy, FixedRetry, ExponentialBackoff, BestOfN


class TestFixedRetry:
    """Tests for FixedRetry policy."""

    def test_fixed_retry_basic(self):
        """Test basic fixed retry configuration."""
        policy = FixedRetry(max_retries=3, delay=1.0)

        assert policy.max_retries == 3
        assert policy.delay == 1.0

    def test_fixed_retry_should_retry(self):
        """Test should_retry logic."""
        policy = FixedRetry(max_retries=2, delay=0.1)

        # Should retry on attempts 0, 1 (not 2)
        assert policy.should_retry(attempt=0) is True
        assert policy.should_retry(attempt=1) is True
        assert policy.should_retry(attempt=2) is False
        assert policy.should_retry(attempt=3) is False

    def test_fixed_retry_get_delay(self):
        """Test fixed delay calculation."""
        policy = FixedRetry(max_retries=3, delay=2.5)

        # Fixed delay should be same for all attempts
        assert policy.get_delay(attempt=0) == 2.5
        assert policy.get_delay(attempt=1) == 2.5
        assert policy.get_delay(attempt=2) == 2.5

    def test_fixed_retry_zero_delay(self):
        """Test immediate retry with zero delay."""
        policy = FixedRetry(max_retries=1, delay=0.0)

        assert policy.get_delay(attempt=0) == 0.0


class TestExponentialBackoff:
    """Tests for ExponentialBackoff policy."""

    def test_exponential_backoff_basic(self):
        """Test basic exponential backoff configuration."""
        policy = ExponentialBackoff(max_retries=3, base_delay=1.0, max_delay=10.0)

        assert policy.max_retries == 3
        assert policy.base_delay == 1.0
        assert policy.max_delay == 10.0

    def test_exponential_backoff_delay_calculation(self):
        """Test exponential delay calculation."""
        policy = ExponentialBackoff(max_retries=5, base_delay=1.0, max_delay=30.0)

        # Delays should grow exponentially: 1, 2, 4, 8, 16
        assert policy.get_delay(attempt=0) == 1.0
        assert policy.get_delay(attempt=1) == 2.0
        assert policy.get_delay(attempt=2) == 4.0
        assert policy.get_delay(attempt=3) == 8.0
        assert policy.get_delay(attempt=4) == 16.0

    def test_exponential_backoff_max_delay(self):
        """Test that delay respects max_delay cap."""
        policy = ExponentialBackoff(max_retries=10, base_delay=1.0, max_delay=5.0)

        # Should cap at max_delay
        assert policy.get_delay(attempt=0) == 1.0  # 2^0 = 1
        assert policy.get_delay(attempt=1) == 2.0  # 2^1 = 2
        assert policy.get_delay(attempt=2) == 4.0  # 2^2 = 4
        assert policy.get_delay(attempt=3) == 5.0  # 2^3 = 8, capped at 5
        assert policy.get_delay(attempt=4) == 5.0  # 2^4 = 16, capped at 5

    def test_exponential_backoff_should_retry(self):
        """Test should_retry logic."""
        policy = ExponentialBackoff(max_retries=2, base_delay=1.0)

        assert policy.should_retry(attempt=0) is True
        assert policy.should_retry(attempt=1) is True
        assert policy.should_retry(attempt=2) is False


class TestBestOfN:
    """Tests for BestOfN policy."""

    def test_best_of_n_basic(self):
        """Test basic best-of-n configuration."""
        policy = BestOfN(n_runs=5)

        assert policy.n_runs == 5
        assert policy.max_retries == 4  # n-1 retries

    def test_best_of_n_should_retry(self):
        """Test should_retry logic."""
        policy = BestOfN(n_runs=3)

        # Should run exactly 3 times (attempts 0, 1, 2)
        assert policy.should_retry(attempt=0) is True
        assert policy.should_retry(attempt=1) is True
        assert policy.should_retry(attempt=2) is False

    def test_best_of_n_no_delay(self):
        """Test that best-of-n has no delay between runs."""
        policy = BestOfN(n_runs=3)

        assert policy.get_delay(attempt=0) == 0.0
        assert policy.get_delay(attempt=1) == 0.0
        assert policy.get_delay(attempt=2) == 0.0

    def test_best_of_n_minimum_runs(self):
        """Test minimum n_runs validation."""
        with pytest.raises(ValueError, match="n_runs must be at least 1"):
            BestOfN(n_runs=0)

        with pytest.raises(ValueError, match="n_runs must be at least 1"):
            BestOfN(n_runs=-1)

    def test_best_of_n_single_run(self):
        """Test best-of-1 (no retries)."""
        policy = BestOfN(n_runs=1)

        assert policy.max_retries == 0
        assert policy.should_retry(attempt=0) is False
