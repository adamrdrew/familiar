"""Browser-use integration utilities."""
import os
from typing import Optional, Any
from browser_use import Agent, Browser


def create_llm(temperature: float = 0.5) -> Any:
    """Create LLM client based on FAMILIAR_MODEL_PROVIDER environment variable.
    
    Supports multiple LLM providers through langchain:
    - openai: OpenAI models (requires langchain-openai)
    - anthropic: Anthropic Claude models (requires langchain-anthropic)
    - google/gemini: Google Gemini models (requires langchain-google-genai)
    - ollama: Local Ollama models (requires langchain-ollama)
    
    The model is specified via FAMILIAR_MODEL env var.
    Provider-specific auth is handled via their standard env vars:
    - OpenAI: OPENAI_API_KEY
    - Anthropic: ANTHROPIC_API_KEY
    - Google: GOOGLE_API_KEY
    - Ollama: OLLAMA_HOST (optional)
    
    Args:
        temperature: LLM temperature for response variability (0.0-1.0).
    
    Returns:
        Configured LLM client instance.
    
    Raises:
        ValueError: If model provider is not supported or required env vars are missing.
        ImportError: If required langchain package is not installed.
    
    Example:
        >>> os.environ["FAMILIAR_MODEL_PROVIDER"] = "anthropic"
        >>> os.environ["FAMILIAR_MODEL"] = "claude-3-5-sonnet-20241022"
        >>> os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
        >>> llm = create_llm(temperature=0.7)
    """
    provider = os.getenv("FAMILIAR_MODEL_PROVIDER", "anthropic").lower()
    model = os.getenv("FAMILIAR_MODEL")
    
    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("langchain-openai package required for OpenAI provider. Install with: pip install langchain-openai")
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable required for OpenAI provider")
        return ChatOpenAI(
            model=model or "gpt-4o",
            temperature=temperature,
        )
    
    elif provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("langchain-anthropic package required for Anthropic provider. Install with: pip install langchain-anthropic")
        
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable required for Anthropic provider")
        return ChatAnthropic(
            model=model or "claude-3-5-sonnet-20241022",
            temperature=temperature,
        )
    
    elif provider in ("google", "gemini"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError("langchain-google-genai package required for Google provider. Install with: pip install langchain-google-genai")
        
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable required for Google provider")
        return ChatGoogleGenerativeAI(
            model=model or "gemini-2.0-flash-exp",
            temperature=temperature,
        )
    
    elif provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError("langchain-ollama package required for Ollama provider. Install with: pip install langchain-ollama")
        
        # Ollama doesn't require API key, just OLLAMA_HOST (optional)
        return ChatOllama(
            model=model or "llama3.2",
            temperature=temperature,
        )
    
    else:
        raise ValueError(
            f"Unsupported model provider: {provider}. "
            f"Supported providers: openai, anthropic, google, gemini, ollama"
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
