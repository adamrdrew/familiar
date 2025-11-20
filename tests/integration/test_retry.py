"""Integration tests for retry functionality."""

import pytest

from familiar.core.retry import BestOfN, ExponentialBackoff, FixedRetry, create_retry_policy
from familiar.models.suite import RetryPolicyConfig


def test_retry_policy_creation_from_config():
    """Test creating retry policies from configuration."""
    # Test fixed retry
    config = RetryPolicyConfig(type="fixed", max_retries=3, delay=1.0)
    policy = create_retry_policy(
        policy_type=config.type,
        max_retries=config.max_retries,
        delay=config.delay,
    )

    assert isinstance(policy, FixedRetry)
    assert policy.max_retries == 3
    assert policy.delay == 1.0


def test_exponential_backoff_from_config():
    """Test creating exponential backoff from configuration."""
    config = RetryPolicyConfig(
        type="exponential",
        max_retries=5,
        base_delay=1.0,
        max_delay=30.0,
    )
    policy = create_retry_policy(
        policy_type=config.type,
        max_retries=config.max_retries,
        base_delay=config.base_delay or 1.0,
        max_delay=config.max_delay or 60.0,
    )

    assert isinstance(policy, ExponentialBackoff)
    assert policy.max_retries == 5
    assert policy.base_delay == 1.0
    assert policy.max_delay == 30.0


def test_best_of_n_from_config():
    """Test creating best-of-N from configuration."""
    config = RetryPolicyConfig(type="best_of_n", n_runs=5)
    policy = create_retry_policy(
        policy_type=config.type,
        n_runs=config.n_runs or 1,
    )

    assert isinstance(policy, BestOfN)
    assert policy.n_runs == 5
    assert policy.max_retries == 4  # n-1


def test_invalid_policy_type_raises_error():
    """Test that invalid policy type raises ValueError."""
    with pytest.raises(ValueError, match="Unknown retry policy type"):
        create_retry_policy(policy_type="invalid")
