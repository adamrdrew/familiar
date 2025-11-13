"""Browser-use integration utilities."""
import os
from typing import Optional, Any
from browser_use import Agent, Browser


def create_llm(temperature: float = 0.5) -> Any:
    """Create LLM client based on FAMILIAR_MODEL_PROVIDER environment variable.
    
    Supports multiple LLM providers through browser-use:
    - openai: OpenAI models (requires OPENAI_API_KEY)
    - anthropic: Anthropic Claude models (requires ANTHROPIC_API_KEY)
    - google/gemini: Google Gemini models (requires GOOGLE_API_KEY)
    - ollama: Local Ollama models (optional OLLAMA_HOST)
    - browser-use: Browser Use optimized model (requires BROWSER_USE_API_KEY)
    - groq: Groq models (requires GROQ_API_KEY)
    - azure: Azure OpenAI (requires AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY)
    
    The model is specified via FAMILIAR_MODEL env var.
    Provider-specific auth is handled via their standard env vars.
    
    Args:
        temperature: LLM temperature for response variability (0.0-1.0).
    
    Returns:
        Configured LLM client instance.
    
    Raises:
        ValueError: If model provider is not supported or required env vars are missing.
        ImportError: If browser-use package is not installed.
    
    Example:
        >>> os.environ["FAMILIAR_MODEL_PROVIDER"] = "anthropic"
        >>> os.environ["FAMILIAR_MODEL"] = "claude-sonnet-4-0"
        >>> os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
        >>> llm = create_llm(temperature=0.7)
    """
    provider = os.getenv("FAMILIAR_MODEL_PROVIDER", "anthropic").lower()
    model = os.getenv("FAMILIAR_MODEL")
    
    if provider == "openai":
        try:
            from browser_use import ChatOpenAI
        except ImportError:
            raise ImportError("browser-use package required. Install with: pip install browser-use")
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable required for OpenAI provider")
        return ChatOpenAI(
            model=model or "gpt-4o",
            temperature=temperature,
        )
    
    elif provider == "anthropic":
        try:
            from browser_use import ChatAnthropic
        except ImportError:
            raise ImportError("browser-use package required. Install with: pip install browser-use")
        
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable required for Anthropic provider")
        return ChatAnthropic(
            model=model or "claude-sonnet-4-0",
            temperature=temperature,
        )
    
    elif provider in ("google", "gemini"):
        try:
            from browser_use import ChatGoogle
        except ImportError:
            raise ImportError("browser-use package required. Install with: pip install browser-use")
        
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable required for Google provider")
        return ChatGoogle(
            model=model or "gemini-flash-latest",
            temperature=temperature,
        )
    
    elif provider == "ollama":
        try:
            from browser_use import ChatOllama
        except ImportError:
            raise ImportError("browser-use package required. Install with: pip install browser-use")
        
        # Ollama doesn't require API key, just OLLAMA_HOST (optional)
        return ChatOllama(
            model=model or "llama3.1:8b",
            temperature=temperature,
        )
    
    elif provider == "browser-use":
        try:
            from browser_use import ChatBrowserUse
        except ImportError:
            raise ImportError("browser-use package required. Install with: pip install browser-use")
        
        if not os.getenv("BROWSER_USE_API_KEY"):
            raise ValueError("BROWSER_USE_API_KEY environment variable required for Browser Use provider")
        return ChatBrowserUse(
            temperature=temperature,
        )
    
    elif provider == "groq":
        try:
            from browser_use import ChatGroq
        except ImportError:
            raise ImportError("browser-use package required. Install with: pip install browser-use")
        
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY environment variable required for Groq provider")
        return ChatGroq(
            model=model or "llama-4-maverick-17b-128e-instruct",
            temperature=temperature,
        )
    
    elif provider == "azure":
        try:
            from browser_use import ChatAzureOpenAI
        except ImportError:
            raise ImportError("browser-use package required. Install with: pip install browser-use")
        
        if not os.getenv("AZURE_OPENAI_ENDPOINT") or not os.getenv("AZURE_OPENAI_API_KEY"):
            raise ValueError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables required for Azure OpenAI provider")
        return ChatAzureOpenAI(
            model=model or "gpt-4o",
            temperature=temperature,
        )
    
    else:
        raise ValueError(
            f"Unsupported model provider: {provider}. "
            f"Supported providers: openai, anthropic, google, gemini, ollama, browser-use, groq, azure"
        )


async def create_browser_use_agent(
    task: str,
    headless: bool = True,
    temperature: float = 0.5,
) -> Agent:
    """Create and configure a browser-use agent for test execution.
    
    This is the primary entry point for creating browser-use agents.
    It handles LLM provider selection, browser configuration, and agent setup.
    
    Args:
        task: The natural language task/instruction for the agent to execute.
        headless: Whether to run browser in headless mode.
        temperature: LLM temperature for agent decision making.
    
    Returns:
        Configured Agent instance ready to execute the task.
    
    Example:
        >>> agent = await create_browser_use_agent(
        ...     task="Navigate to google.com and search for 'python'",
        ...     headless=True,
        ...     temperature=0.7,
        ... )
        >>> result = await agent.run()
    """
    # Create LLM based on environment configuration
    llm = create_llm(temperature=temperature)
    
    # Create browser session with configuration
    browser = Browser(headless=headless)
    
    # Create and return agent
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )
    
    return agent
