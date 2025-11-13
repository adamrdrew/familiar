"""Step execution with browser-use integration."""
import asyncio
from datetime import datetime
from typing import Optional, Dict
import traceback

from familiar.models.step import TestStep
from familiar.models.result import TestResult, ResultStatus, LogEntry, LogLevel, BrowserAction, ActionType
from familiar.utils.browser import create_browser_use_agent
from familiar.utils.interpolation import interpolate_variables


class StepExecutor:
    """Executes individual test steps using browser-use agents.
    
    Responsibilities:
    - Create browser-use agents for each step
    - Execute steps with proper error handling
    - Capture logs and browser actions
    - Return structured test results
    """
    
    def __init__(
        self,
        headless: bool = True,
        temperature: float = 0.5,
        variables: Optional[Dict[str, str]] = None,
    ):
        """Initialize the step executor.
        
        Args:
            headless: Whether to run browser in headless mode.
            temperature: LLM temperature for agent decision making.
            variables: Environment variables for step interpolation.
        """
        self.headless = headless
        self.temperature = temperature
        self.variables = variables or {}
    
    async def execute_step(
        self,
        step: TestStep,
        timeout: int = 60,
    ) -> TestResult:
        """Execute a single test step.
        
        Args:
            step: The test step to execute.
            timeout: Maximum execution time in seconds.
        
        Returns:
            TestResult with execution outcome, logs, and timing.
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
            
            # Create browser-use agent
            logs.append(LogEntry(
                level=LogLevel.INFO,
                message="Initializing browser agent",
                timestamp=datetime.now(),
            ))
            
            agent = await create_browser_use_agent(
                task=interpolated_content,
                headless=self.headless,
                temperature=self.temperature,
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
            )

