"""Retry policy implementations for handling non-deterministic test failures."""
from abc import ABC, abstractmethod
from typing import Protocol


class RetryPolicy(Protocol):
    """Protocol for retry policies.
    
    Defines the interface all retry strategies must implement.
    """
    
    max_retries: int
    
    def should_retry(self, attempt: int) -> bool:
        """Determine if another retry should be attempted.
        
        Args:
            attempt: Current attempt number (0-indexed).
        
        Returns:
            True if should retry, False otherwise.
        """
        ...
    
    def get_delay(self, attempt: int) -> float:
        """Get delay in seconds before next retry attempt.
        
        Args:
            attempt: Current attempt number (0-indexed).
        
        Returns:
            Delay in seconds.
        """
        ...


class FixedRetry:
    """Fixed retry policy with constant delay between attempts.
    
    Retries a fixed number of times with the same delay between each attempt.
    Suitable for transient errors with predictable recovery times.
    
    Example:
        >>> policy = FixedRetry(max_retries=3, delay=2.0)
        >>> policy.should_retry(0)  # True - will retry
        >>> policy.get_delay(0)     # 2.0 seconds
    """
    
    def __init__(self, max_retries: int, delay: float):
        """Initialize fixed retry policy.
        
        Args:
            max_retries: Maximum number of retry attempts.
            delay: Fixed delay in seconds between attempts.
        """
        self.max_retries = max_retries
        self.delay = delay
    
    def should_retry(self, attempt: int) -> bool:
        """Determine if another retry should be attempted.
        
        Args:
            attempt: Current attempt number (0-indexed).
        
        Returns:
            True if attempt < max_retries, False otherwise.
        """
        return attempt < self.max_retries
    
    def get_delay(self, attempt: int) -> float:
        """Get fixed delay before next retry.
        
        Args:
            attempt: Current attempt number (0-indexed).
        
        Returns:
            Fixed delay in seconds.
        """
        return self.delay


class ExponentialBackoff:
    """Exponential backoff retry policy.
    
    Delays grow exponentially with each retry: base * 2^attempt.
    Useful for API rate limiting and overload scenarios.
    
    Example:
        >>> policy = ExponentialBackoff(max_retries=4, base_delay=1.0, max_delay=10.0)
        >>> policy.get_delay(0)  # 1.0 second
        >>> policy.get_delay(1)  # 2.0 seconds
        >>> policy.get_delay(2)  # 4.0 seconds
        >>> policy.get_delay(3)  # 8.0 seconds
    """
    
    def __init__(self, max_retries: int, base_delay: float = 1.0, max_delay: float = 60.0):
        """Initialize exponential backoff policy.
        
        Args:
            max_retries: Maximum number of retry attempts.
            base_delay: Base delay in seconds (multiplied by 2^attempt).
            max_delay: Maximum delay cap in seconds.
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def should_retry(self, attempt: int) -> bool:
        """Determine if another retry should be attempted.
        
        Args:
            attempt: Current attempt number (0-indexed).
        
        Returns:
            True if attempt < max_retries, False otherwise.
        """
        return attempt < self.max_retries
    
    def get_delay(self, attempt: int) -> float:
        """Get exponentially increasing delay.
        
        Args:
            attempt: Current attempt number (0-indexed).
        
        Returns:
            Delay in seconds, capped at max_delay.
        """
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)


class BestOfN:
    """Best-of-N retry policy.
    
    Runs the test N times and takes the best result (first success).
    No delay between runs. Useful for highly non-deterministic AI tests.
    
    Example:
        >>> policy = BestOfN(n_runs=5)
        >>> # Will run test 5 times, succeed if any pass
    """
    
    def __init__(self, n_runs: int):
        """Initialize best-of-N policy.
        
        Args:
            n_runs: Number of times to run the test.
        
        Raises:
            ValueError: If n_runs < 1.
        """
        if n_runs < 1:
            raise ValueError("n_runs must be at least 1")
        
        self.n_runs = n_runs
        self.max_retries = n_runs - 1  # n runs = n-1 retries
    
    def should_retry(self, attempt: int) -> bool:
        """Determine if another run should be attempted.
        
        Args:
            attempt: Current attempt number (0-indexed).
        
        Returns:
            True if attempt < n_runs - 1, False otherwise.
        """
        return attempt < self.max_retries
    
    def get_delay(self, attempt: int) -> float:
        """Get delay before next run (always 0 for best-of-n).
        
        Args:
            attempt: Current attempt number (0-indexed).
        
        Returns:
            0.0 (no delay between runs).
        """
        return 0.0


def create_retry_policy(policy_type: str, **kwargs) -> RetryPolicy:
    """Factory function to create retry policies from configuration.
    
    Args:
        policy_type: Type of policy ("fixed", "exponential", "best_of_n").
        **kwargs: Policy-specific configuration parameters.
    
    Returns:
        Configured retry policy instance.
    
    Raises:
        ValueError: If policy_type is unknown.
    
    Example:
        >>> policy = create_retry_policy("fixed", max_retries=3, delay=1.0)
        >>> policy = create_retry_policy("exponential", max_retries=5, base_delay=1.0)
        >>> policy = create_retry_policy("best_of_n", n_runs=5)
    """
    policy_type = policy_type.lower()
    
    if policy_type == "fixed":
        return FixedRetry(
            max_retries=kwargs.get("max_retries", 3),
            delay=kwargs.get("delay", 1.0),
        )
    elif policy_type == "exponential":
        return ExponentialBackoff(
            max_retries=kwargs.get("max_retries", 3),
            base_delay=kwargs.get("base_delay", 1.0),
            max_delay=kwargs.get("max_delay", 60.0),
        )
    elif policy_type == "best_of_n":
        return BestOfN(n_runs=kwargs.get("n_runs", 3))
    else:
        raise ValueError(
            f"Unknown retry policy type: {policy_type}. "
            f"Supported types: fixed, exponential, best_of_n"
        )

