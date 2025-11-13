"""Step execution with browser-use integration."""
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any
import traceback

from browser_use import Browser, Agent

from familiar.models.step import TestStep
from familiar.models.result import TestResult, ResultStatus, LogEntry, LogLevel, BrowserAction, ActionType
from familiar.utils.interpolation import interpolate_variables
from familiar.core.retry import RetryPolicy, FixedRetry


class StepExecutor:
    """Executes individual test steps using browser-use agents.
    
    Now accepts browser and LLM instances from runner for session persistence.
    
    Responsibilities:
    - Execute steps using provided browser session
    - Handle errors and retries
    - Capture logs and browser actions
    - Return structured test results
    """
    
    def __init__(
        self,
        variables: Optional[Dict[str, str]] = None,
        retry_policy: Optional[RetryPolicy] = None,
    ):
        """Initialize the step executor.
        
        Browser and LLM are now passed per-step for session reuse.
        
        Args:
            variables: Environment variables for step interpolation.
            retry_policy: Retry policy for failed steps.
        """
        self.variables = variables or {}
        self.retry_policy = retry_policy or FixedRetry(max_retries=0, delay=0.0)
    
    async def execute_step(
        self,
        step: TestStep,
        browser: Browser,
        llm: Any,
        timeout: int = 60,
    ) -> TestResult:
        """Execute a single test step with retry support.
        
        Uses the provided browser session, enabling cumulative testing
        where browser state persists across steps.
        
        Args:
            step: The test step to execute.
            browser: Browser instance to use for this step.
            llm: LLM client instance to use for this step.
            timeout: Maximum execution time in seconds.
        
        Returns:
            TestResult with execution outcome, logs, and timing.
            For retries, returns the first successful result or the last failure.
        """
        attempt = 0
        all_logs: List[LogEntry] = []
        
        while True:
            if attempt > 0:
                all_logs.append(LogEntry(
                    level=LogLevel.INFO,
                    message=f"Retry attempt {attempt + 1} for step: {step.name}",
                    timestamp=datetime.now(),
                ))
            
            result = await self._execute_step_once(step, browser, llm, timeout, attempt + 1)
            
            # Merge logs from this attempt
            all_logs.extend(result.logs)
            
            # If successful or no more retries, return
            if result.status == ResultStatus.PASSED or not self.retry_policy.should_retry(attempt):
                result.logs = all_logs
                return result
            
            # Get delay for next retry
            delay = self.retry_policy.get_delay(attempt)
            if delay > 0:
                all_logs.append(LogEntry(
                    level=LogLevel.INFO,
                    message=f"Waiting {delay}s before retry",
                    timestamp=datetime.now(),
                ))
                await asyncio.sleep(delay)
            
            attempt += 1
    
    async def _execute_step_once(
        self,
        step: TestStep,
        browser: Browser,
        llm: Any,
        timeout: int,
        attempt: int,
    ) -> TestResult:
        """Execute a single attempt of a test step.
        
        Uses provided browser and LLM instances for session persistence.
        
        Args:
            step: The test step to execute.
            browser: Browser instance to use.
            llm: LLM client instance to use.
            timeout: Maximum execution time in seconds.
            attempt: Current attempt number (1-indexed).
        
        Returns:
            TestResult with execution outcome for this attempt.
        """
        start_time = datetime.now()
        logs: list[LogEntry] = []
        browser_actions: list[BrowserAction] = []
        
        try:
            # Log step start
            logs.append(LogEntry(
                level=LogLevel.INFO,
                message=f"Starting step: {step.name}",
                timestamp=datetime.now(),
            ))
            
            # Interpolate variables in step content
            interpolated_content = interpolate_variables(step.content, self.variables)
            
            logs.append(LogEntry(
                level=LogLevel.DEBUG,
                message=f"Interpolated content ({len(step.variables)} variables)",
                timestamp=datetime.now(),
            ))
            
            # Create agent with existing browser and LLM
            logs.append(LogEntry(
                level=LogLevel.INFO,
                message="Creating agent with persistent browser session",
                timestamp=datetime.now(),
            ))
            
            agent = Agent(
                task=interpolated_content,
                llm=llm,
                browser=browser,
            )
            
            # Execute the step with timeout
            logs.append(LogEntry(
                level=LogLevel.INFO,
                message=f"Executing task (timeout: {timeout}s)",
                timestamp=datetime.now(),
            ))
            
            try:
                result = await asyncio.wait_for(
                    agent.run(),
                    timeout=timeout,
                )
                
                logs.append(LogEntry(
                    level=LogLevel.INFO,
                    message="Task completed successfully",
                    timestamp=datetime.now(),
                ))
                
                # Record browser actions from agent history
                if hasattr(agent, 'history') and agent.history:
                    for i, action in enumerate(agent.history):
                        browser_actions.append(BrowserAction(
                            type=ActionType.NAVIGATE,
                            target=str(action) if action else "unknown",
                            success=True,
                            timestamp=datetime.now(),
                        ))
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return TestResult(
                    step_name=step.name,
                    status=ResultStatus.PASSED,
                    duration=duration,
                    logs=logs,
                    browser_actions=browser_actions,
                    error_message=None,
                    attempt=attempt,
                )
                
            except asyncio.TimeoutError:
                logs.append(LogEntry(
                    level=LogLevel.ERROR,
                    message=f"Step timed out after {timeout}s",
                    timestamp=datetime.now(),
                ))
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return TestResult(
                    step_name=step.name,
                    status=ResultStatus.FAILED,
                    duration=duration,
                    logs=logs,
                    browser_actions=browser_actions,
                    error_message=f"Timeout after {timeout} seconds",
                    attempt=attempt,
                )
        
        except Exception as e:
            # Handle any unexpected errors
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            logs.append(LogEntry(
                level=LogLevel.ERROR,
                message=f"Step failed with error: {error_msg}",
                timestamp=datetime.now(),
            ))
            
            logs.append(LogEntry(
                level=LogLevel.DEBUG,
                message=f"Error traceback:\n{error_trace}",
                timestamp=datetime.now(),
            ))
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                step_name=step.name,
                status=ResultStatus.FAILED,
                duration=duration,
                logs=logs,
                browser_actions=browser_actions,
                error_message=error_msg,
                attempt=attempt,
            )

