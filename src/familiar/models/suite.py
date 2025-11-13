"""Test suite models."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class RetryPolicyConfig(BaseModel):
    """Retry policy configuration."""

    type: str = Field(pattern="^(fixed|exponential|best_of_n)$")
    max_retries: int = Field(default=3, ge=0, le=10)
    delay: float = Field(default=1.0, ge=0)
    base_delay: Optional[float] = Field(default=None, ge=0)
    max_delay: Optional[float] = Field(default=None, ge=0)
    multiplier: Optional[float] = Field(default=None, ge=1)
    n_runs: Optional[int] = Field(default=None, ge=1, le=20)


class SuiteConfig(BaseModel):
    """Suite configuration from suite.yaml."""

    name: str = Field(min_length=1, max_length=200)
    timeout: int = Field(default=300, gt=0, le=3600)
    step_timeout: int = Field(default=30, gt=0, le=600)
    retry_policy: RetryPolicyConfig = Field(
        default_factory=lambda: RetryPolicyConfig(type="fixed")
    )
    fuzziness: float = Field(default=0.0, ge=0.0, le=1.0)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    headless: Optional[bool] = None
    screenshot_on_failure: bool = True
    env: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("step_timeout")
    @classmethod
    def step_timeout_must_not_exceed_suite_timeout(cls, v: int, info: Any) -> int:
        """Validate step_timeout <= timeout."""
        if "timeout" in info.data and v > info.data["timeout"]:
            raise ValueError(
                f"step_timeout ({v}) cannot exceed timeout ({info.data['timeout']})"
            )
        return v


@dataclass
class TestSuite:
    """A test suite with configuration and steps."""

    name: str
    path: Path
    config: SuiteConfig
    steps: List[Any] = field(default_factory=list)  # List[TestStep] forward ref
    metadata: Dict[str, Any] = field(default_factory=dict)

