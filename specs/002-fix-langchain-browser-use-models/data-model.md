# Data Model: Browser-Use Native Model Providers

**Date**: 2025-11-13  
**Purpose**: Document the data structures and types affected by the model provider bug fix

## Overview

This bug fix does not introduce new data models. It modifies the internal implementation of LLM client creation while maintaining existing interfaces.

## Affected Components

### 1. LLM Client Types

**Module**: `src/familiar/utils/browser.py`

**Type Signature** (unchanged):
```python
def create_llm(temperature: float = 0.5) -> Any
```

**Return Type**: `Any` (browser-use LLM client instance)

**Concrete Types** (after fix):
- `browser_use.ChatOpenAI`
- `browser_use.ChatAnthropic`
- `browser_use.ChatGoogle`
- `browser_use.ChatOllama`
- `browser_use.ChatBrowserUse`
- `browser_use.ChatGroq`
- `browser_use.ChatAzureOpenAI`

**Note**: Return type remains `Any` to support multiple provider types. All browser-use model classes implement a common interface expected by the Agent class.

### 2. Agent Creation Function

**Module**: `src/familiar/utils/browser.py`

**Type Signature** (unchanged):
```python
async def create_browser_use_agent(
    task: str,
    headless: bool = True,
    temperature: float = 0.5,
) -> Agent
```

**Parameters**:
- `task`: Natural language task description (string)
- `headless`: Browser visibility mode (boolean)
- `temperature`: LLM response randomness (float, 0.0-1.0)

**Returns**: `browser_use.Agent` instance configured with the selected LLM provider

**Note**: This function's signature and behavior remain completely unchanged. Only internal implementation changes.

## Configuration Model

### Environment Variables

**Type**: Configuration via environment variables (not Python types)

**Structure**:
```python
# Model Provider Selection
FAMILIAR_MODEL_PROVIDER: Literal[
    "openai", 
    "anthropic", 
    "google", 
    "gemini",  # alias for google
    "ollama",
    "browser-use",
    "groq",
    "azure",
]

# Model Name Override (optional)
FAMILIAR_MODEL: str | None

# Provider-Specific API Keys
OPENAI_API_KEY: str | None
ANTHROPIC_API_KEY: str | None
GOOGLE_API_KEY: str | None
GROQ_API_KEY: str | None
BROWSER_USE_API_KEY: str | None

# Azure-Specific
AZURE_OPENAI_ENDPOINT: str | None
AZURE_OPENAI_API_KEY: str | None

# Ollama-Specific (optional)
OLLAMA_HOST: str | None
```

**Validation Rules**:
1. If provider requires API key and key is missing → `ValueError`
2. If provider is unsupported → `ValueError` with list of supported providers
3. If browser-use package is not installed → `ImportError`

## Provider-Specific Models

### Model Name Defaults

**Mapping** of provider to default model:
```python
DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-0",
    "google": "gemini-flash-latest",
    "ollama": "llama3.1:8b",
    "browser-use": None,  # Uses ChatBrowserUse default
    "groq": "llama-4-maverick-17b-128e-instruct",
    "azure": "gpt-4o",
}
```

**Override**: `FAMILIAR_MODEL` environment variable overrides the default

### Model Configuration Parameters

**Common Parameters** (supported by all providers):
```python
{
    "model": str,           # Model identifier
    "temperature": float,   # 0.0 to 1.0
}
```

**Provider-Specific Parameters** (optional, not currently used):
```python
{
    # OpenAI/Azure
    "max_tokens": int,
    "top_p": float,
    "frequency_penalty": float,
    
    # Anthropic
    "max_tokens": int,  # Default: 4096
    
    # Google
    "top_k": int,
    "top_p": float,
    
    # Ollama
    "base_url": str,  # For remote Ollama
}
```

**Note**: Current implementation only passes `model` and `temperature`. Other parameters can be added in future enhancements.

## Error Types

### ValueError Cases

**Scenario 1**: Missing API Key
```python
ValueError("OPENAI_API_KEY environment variable required for OpenAI provider")
```

**Scenario 2**: Unsupported Provider
```python
ValueError(
    f"Unsupported model provider: {provider}. "
    f"Supported providers: openai, anthropic, google, gemini, ollama, browser-use, groq"
)
```

### ImportError Cases

**Scenario**: browser-use not installed
```python
ImportError("browser-use package required. Install with: pip install browser-use")
```

**Note**: After the fix, langchain ImportErrors should never occur since browser-use includes all model providers.

## State Diagram

### LLM Client Creation Flow

```
┌─────────────────────────────┐
│ create_llm(temperature)     │
└──────────────┬──────────────┘
               │
               ▼
┌──────────────────────────────────┐
│ Read FAMILIAR_MODEL_PROVIDER     │
│ (default: "anthropic")           │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│ Switch on provider:              │
│  - openai → ChatOpenAI           │
│  - anthropic → ChatAnthropic     │
│  - google/gemini → ChatGoogle    │
│  - ollama → ChatOllama           │
│  - browser-use → ChatBrowserUse  │
│  - groq → ChatGroq               │
│  - azure → ChatAzureOpenAI       │
│  - else → ValueError             │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│ Validate required env vars       │
│ (API keys, endpoints, etc.)      │
└──────────────┬───────────────────┘
               │
               ├─── Missing key ──────► ValueError
               │
               ▼
┌──────────────────────────────────┐
│ Import browser_use model class   │
└──────────────┬───────────────────┘
               │
               ├─── Import fails ─────► ImportError
               │
               ▼
┌──────────────────────────────────┐
│ Instantiate model with:          │
│  - model name (default or env)   │
│  - temperature                   │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│ Return LLM client instance       │
└──────────────────────────────────┘
```

## Interface Compatibility

### Browser-Use Agent Interface

**Expected LLM Interface** (defined by browser-use):
```python
# All browser-use model classes implement this interface
class BaseChatModel:
    async def agenerate(self, messages: List[Message]) -> Response:
        """Generate response from messages"""
        pass
    
    async def astream(self, messages: List[Message]) -> AsyncIterator[Token]:
        """Stream response tokens"""
        pass
```

**Compatibility**: All browser-use model classes (ChatOpenAI, ChatAnthropic, etc.) implement this interface, ensuring they work interchangeably with the Agent class.

## Migration Impact

### Data Compatibility

**No data migration required**. This is an implementation change only:
- No database schema changes
- No configuration file format changes
- No serialization format changes
- No API response format changes

### Backward Compatibility

**Environment Variables**: 100% backward compatible
- All existing env vars continue to work
- New providers add new env vars (opt-in)

**Function Signatures**: 100% backward compatible
- `create_llm()` signature unchanged
- `create_browser_use_agent()` signature unchanged

**Behavior**: 100% backward compatible
- Same model providers supported
- Same error conditions
- Same return types
- Same agent behavior

## Summary

This bug fix modifies only the **internal implementation** of LLM client creation. No changes to:
- Public APIs
- Data models
- Configuration schemas
- Client behavior

The fix simplifies the implementation by removing the LangChain dependency layer and using browser-use's native model providers directly.

