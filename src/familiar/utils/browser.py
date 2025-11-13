"""Browser-use integration utilities."""
import os
from typing import Optional
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI


def create_browser_config(headless: bool = True) -> BrowserConfig:
    """Create browser configuration from environment and parameters.
    
    Args:
        headless: Whether to run browser in headless mode.
    
    Returns:
        BrowserConfig instance configured for the test environment.
    """
    return BrowserConfig(
        headless=headless,
        disable_security=True,  # For testing, allow insecure contexts
    )


def create_llm(
    temperature: float = 0.5,
    model: Optional[str] = None,
) -> ChatOpenAI:
    """Create LLM client for browser-use agent.
    
    Uses environment variables for API configuration:
    - OPENAI_API_KEY: OpenAI API key (required)
    - OPENAI_MODEL: Model to use (default: gpt-4)
    
    Args:
        temperature: LLM temperature (0.0-1.0).
        model: Optional model override.
    
    Returns:
        Configured ChatOpenAI instance.
    
    Raises:
        ValueError: If OPENAI_API_KEY is not set.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required for AI-driven testing"
        )
    
    model_name = model or os.environ.get("OPENAI_MODEL", "gpt-4")
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
    )


async def create_browser_use_agent(
    task: str,
    headless: bool = True,
    temperature: float = 0.5,
) -> Agent:
    """Create a browser-use Agent for executing a test step.
    
    This is the main factory function for creating agents to execute test steps.
    browser-use handles all browser control automatically via Playwright.
    
    Args:
        task: The natural language task description for the agent.
        headless: Whether to run browser in headless mode.
        temperature: LLM temperature for agent decision making.
    
    Returns:
        Configured Agent instance ready to execute the task.
    
    Raises:
        ValueError: If required environment variables are not set.
    """
    # Create LLM client
    llm = create_llm(temperature=temperature)
    
    # Create browser
    browser_config = create_browser_config(headless=headless)
    browser = Browser(config=browser_config)
    
    # Create and return agent
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )
    
    return agent

