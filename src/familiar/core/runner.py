"""Test suite execution orchestration."""

from datetime import datetime
from typing import Optional, Dict

from browser_use import Browser, Agent

from familiar.models.suite import TestSuite
from familiar.models.result import SuiteResult, TestResult
from familiar.core.executor import StepExecutor
from familiar.core.retry import create_retry_policy
from familiar.utils.env import get_env_vars
from familiar.utils.browser import create_llm


# Speed optimization prompt for fast mode
SPEED_OPTIMIZATION_PROMPT = """
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
"""


class SuiteRunner:
    """Orchestrates execution of test suites.

    Responsibilities:
    - Coordinate execution of multiple test steps
    - Handle suite-level configuration (retries, timeouts)
    - Aggregate results from individual steps
    - Apply suite-level rules (fuzziness, best-of-N)
    - Apply performance optimizations (fast mode)
    """

    def __init__(
        self,
        variables: Optional[Dict[str, str]] = None,
        headless: bool = True,
        fast_mode: bool = False,
    ):
        """Initialize the suite runner.

        Args:
            variables: Environment variables for step interpolation.
                      If None, will load from os.environ.
            headless: Whether to run browser in headless mode.
            fast_mode: Whether to enable speed optimizations (flash mode, speed prompts).
        """
        self.variables = variables if variables is not None else get_env_vars()
        self.headless = headless
        self.fast_mode = fast_mode

    async def run_suite(self, suite: TestSuite) -> SuiteResult:
        """Execute all steps in a test suite with retry support.

        Creates a single browser session for the entire suite, enabling
        cumulative testing where browser state persists across steps.

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

        # Get browser profile configuration from suite (or use defaults)
        browser_profile_config = suite.config.get_browser_profile()

        # CLI headless flag overrides suite browser_profile.headless setting
        browser_profile_config.headless = self.headless

        # Convert to browser-use BrowserProfile
        browser_profile = browser_profile_config.to_browser_profile()

        # Create browser and LLM ONCE for entire scenario
        # This enables cumulative testing (login → navigate → action)
        browser = Browser(
            headless=self.headless,
            keep_alive=True,
            browser_profile=browser_profile,
        )
        llm = create_llm(temperature=suite.config.temperature)

        # Create executor with suite configuration
        executor = StepExecutor(
            variables=self.variables,
            retry_policy=retry_policy,
        )

        # Execute each step in sequence using the SAME browser
        for step in suite.steps:
            # Prepare fast mode parameters
            flash_mode = self.fast_mode
            extend_system_message = SPEED_OPTIMIZATION_PROMPT if self.fast_mode else None

            result = await executor.execute_step(
                step=step,
                browser=browser,
                llm=llm,
                timeout=suite.config.step_timeout,
                flash_mode=flash_mode,
                extend_system_message=extend_system_message,
            )
            test_results.append(result)

            # Stop on failure if fuzziness is 0.0 (no tolerance for failures)
            if result.status.value == "failed" and suite.config.fuzziness == 0.0:
                break

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        await browser.kill()

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
