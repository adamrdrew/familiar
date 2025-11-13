"""Test suite execution orchestration."""
from datetime import datetime
from typing import Optional, Dict

from familiar.models.suite import TestSuite
from familiar.models.result import SuiteResult, TestResult
from familiar.core.executor import StepExecutor
from familiar.core.retry import create_retry_policy
from familiar.utils.env import get_env_vars


class SuiteRunner:
    """Orchestrates execution of test suites.
    
    Responsibilities:
    - Coordinate execution of multiple test steps
    - Handle suite-level configuration (retries, timeouts)
    - Aggregate results from individual steps
    - Apply suite-level rules (fuzziness, best-of-N)
    """
    
    def __init__(
        self,
        variables: Optional[Dict[str, str]] = None,
        headless: bool = True,
    ):
        """Initialize the suite runner.
        
        Args:
            variables: Environment variables for step interpolation.
                      If None, will load from os.environ.
            headless: Whether to run browser in headless mode.
        """
        self.variables = variables if variables is not None else get_env_vars()
        self.headless = headless
    
    async def run_suite(self, suite: TestSuite) -> SuiteResult:
        """Execute all steps in a test suite with retry support.
        
        Args:
            suite: The test suite to execute.
        
        Returns:
            SuiteResult with aggregated results from all steps.
        """
        start_time = datetime.now()
        test_results: list[TestResult] = []
        
        # Create retry policy from suite configuration
        retry_config = suite.config.retry_policy
        retry_policy = create_retry_policy(
            policy_type=retry_config.type,
            max_retries=retry_config.max_retries,
            delay=retry_config.delay,
            base_delay=retry_config.base_delay or 1.0,
            max_delay=retry_config.max_delay or 60.0,
            n_runs=retry_config.n_runs or 1,
        )
        
        # Create executor with suite configuration
        executor = StepExecutor(
            headless=self.headless,
            temperature=suite.config.temperature,
            variables=self.variables,
            retry_policy=retry_policy,
        )
        
        # Execute each step in sequence
        for step in suite.steps:
            result = await executor.execute_step(
                step=step,
                timeout=suite.config.step_timeout,
            )
            test_results.append(result)
            
            # Stop on failure if fuzziness is 0.0 (no tolerance for failures)
            if result.status.value == "failed" and suite.config.fuzziness == 0.0:
                break
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return SuiteResult(
            suite_name=suite.name,
            test_results=test_results,
            total_duration=duration,
            fuzziness=suite.config.fuzziness,
            suite_path=suite.path,
            config={
                "retry_policy": retry_config.model_dump(),
                "temperature": suite.config.temperature,
                "step_timeout": suite.config.step_timeout,
                "timeout": suite.config.timeout,
            },
        )

