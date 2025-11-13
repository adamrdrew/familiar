"""Browser-use integration utilities."""
import os
from typing import Optional, Any
from browser_use import (
    Agent,
    Browser,
    BrowserConfig,
    ChatOpenAI,
    ChatAnthropic,
    ChatGoogle,
    ChatBrowserUse,
    ChatAzureOpenAI,
    ChatGroq,
    ChatOllama,
)


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
    provider: Optional[str] = None,
) -> Any:
    """Create LLM client for browser-use agent using browser-use's native model classes.
    
    Supports all providers that browser-use supports natively.
    Uses browser-use's environment variable conventions for each provider.
    
    Environment variables:
    - FAMILIAR_MODEL_PROVIDER: Provider to use (browseruse, openai, anthropic, gemini, azure, groq, ollama, etc.)
    - FAMILIAR_MODEL: Model name (provider-specific)
    - Provider-specific API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
    
    Args:
        temperature: LLM temperature (0.0-1.0).
        model: Model name override. If None, uses FAMILIAR_MODEL env var.
        provider: Provider override. If None, uses FAMILIAR_MODEL_PROVIDER env var.
    
    Returns:
        Configured LLM instance from browser-use (ChatOpenAI, ChatAnthropic, etc.).
    
    Raises:
        ValueError: If provider is unknown or required API keys are missing.
        
    References:
        - Supported providers: https://github.com/browser-use/browser-use/blob/main/docs/supported-models.mdx
    """
    provider = provider or os.environ.get("FAMILIAR_MODEL_PROVIDER", "openai")
    model = model or os.environ.get("FAMILIAR_MODEL")
    
    provider = provider.lower()
    
    # Browser Use Cloud - optimized in-house model (3-5x faster)
    if provider == "browseruse":
        return ChatBrowserUse()  # Uses BROWSER_USE_API_KEY env var
    
    # OpenAI - GPT models (GPT-4, GPT-3.5, O1, O3)
    elif provider == "openai":
        model = model or "gpt-4"
        return ChatOpenAI(
            model=model,
            temperature=temperature,
        )  # Uses OPENAI_API_KEY env var
    
    # Anthropic - Claude models (Sonnet, Opus, Haiku)
    elif provider == "anthropic":
        model = model or "claude-sonnet-4-0"
        return ChatAnthropic(
            model=model,
            temperature=temperature,
        )  # Uses ANTHROPIC_API_KEY env var
    
    # Google Gemini
    elif provider == "gemini" or provider == "google":
        model = model or "gemini-flash-latest"
        return ChatGoogle(
            model=model,
            temperature=temperature,
        )  # Uses GOOGLE_API_KEY env var
    
    # Azure OpenAI
    elif provider == "azure":
        model = model or "gpt-4"
        return ChatAzureOpenAI(
            model=model,
            temperature=temperature,
        )  # Uses AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT env vars
    
    # Groq - fast inference for open models
    elif provider == "groq":
        model = model or "meta-llama/llama-4-maverick-17b-128e-instruct"
        return ChatGroq(
            model=model,
            temperature=temperature,
        )  # Uses GROQ_API_KEY env var
    
    # Ollama - local models
    elif provider == "ollama":
        model = model or "llama3.1:8b"
        return ChatOllama(
            model=model,
            temperature=temperature,
        )  # Uses localhost, no API key needed
    
    # Unknown provider
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. Supported providers: "
            f"browseruse, openai, anthropic, gemini, azure, groq, ollama. "
            f"See https://github.com/browser-use/browser-use/blob/main/docs/supported-models.mdx"
        )


async def create_browser_use_agent(
    task: str,
    headless: bool = True,
    temperature: float = 0.5,
    model: Optional[str] = None,
    provider: Optional[str] = None,
) -> Agent:
    """Create a browser-use Agent for executing a test step.
    
    This is the main factory function for creating agents to execute test steps.
    browser-use handles all browser control automatically via Playwright.
    LLM provider is selected via FAMILIAR_MODEL_PROVIDER environment variable.
    
    Args:
        task: The natural language task description for the agent.
        headless: Whether to run browser in headless mode.
        temperature: LLM temperature for agent decision making.
        model: Optional model name override (uses FAMILIAR_MODEL if not provided).
        provider: Optional provider override (uses FAMILIAR_MODEL_PROVIDER if not provided).
    
    Returns:
        Configured Agent instance ready to execute the task.
    
    Raises:
        ValueError: If required environment variables are not set or provider is unknown.
    """
    # Create LLM client using browser-use's native model classes
    llm = create_llm(temperature=temperature, model=model, provider=provider)
    
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

