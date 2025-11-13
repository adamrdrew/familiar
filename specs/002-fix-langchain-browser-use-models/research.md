# Research: Browser-Use Native Model Providers

**Date**: 2025-11-13  
**Purpose**: Research browser-use's native model provider system to replace incorrect LangChain usage

## Overview

Browser-use provides native model provider classes that are optimized for browser automation tasks. These classes are importable directly from the `browser_use` package and should be used instead of LangChain wrappers.

## Decisions

### 1. Model Provider Import Strategy

**Decision**: Import model classes directly from `browser_use` package

**Rationale**: 
- Browser-use bundles its own model provider implementations
- These are tested and optimized specifically for browser automation
- Reduces dependency chain (no need for separate langchain packages)
- Ensures compatibility with browser-use's internal systems

**Implementation**:
```python
from browser_use import (
    ChatOpenAI,
    ChatAnthropic, 
    ChatGoogle,
    ChatOllama,
    ChatBrowserUse,  # NEW: browser-use's optimized model
    ChatGroq,
    ChatAzureOpenAI,
    ChatAWSBedrock,
)
```

**Alternatives Considered**:
- Keep LangChain wrappers: Rejected due to unnecessary complexity and potential version conflicts
- Mix LangChain and browser-use: Rejected due to inconsistency and confusion

### 2. Model Provider Classes Mapping

**Decision**: Direct 1:1 replacement of LangChain classes with browser-use equivalents

**Mapping**:
| Current (LangChain) | New (browser-use) | Constructor Changes |
|---------------------|-------------------|---------------------|
| `langchain_openai.ChatOpenAI` | `browser_use.ChatOpenAI` | Same parameters |
| `langchain_anthropic.ChatAnthropic` | `browser_use.ChatAnthropic` | Same parameters |
| `langchain_google_genai.ChatGoogleGenerativeAI` | `browser_use.ChatGoogle` | **Class name changes** |
| `langchain_ollama.ChatOllama` | `browser_use.ChatOllama` | Same parameters |

**Key Changes**:
- **Google/Gemini**: Class renamed from `ChatGoogleGenerativeAI` to `ChatGoogle`
- Default models may differ (verify in testing)
- All environment variables remain the same

**Rationale**: Browser-use's classes are designed to be drop-in replacements with similar APIs, minimizing code changes.

### 3. Default Model Provider Strategy

**Decision**: Keep Anthropic as default, add ChatBrowserUse as recommended alternative

**Rationale**:
- Maintains backward compatibility (existing users expect Anthropic default)
- ChatBrowserUse offers better performance (3-5x faster) but requires separate API key
- Users can opt-in to ChatBrowserUse by setting `FAMILIAR_MODEL_PROVIDER=browser-use`

**Implementation**:
```python
provider = os.getenv("FAMILIAR_MODEL_PROVIDER", "anthropic").lower()

if provider == "browser-use":
    llm = ChatBrowserUse()
elif provider == "anthropic":
    llm = ChatAnthropic(model=model or "claude-sonnet-4-0", temperature=temperature)
# ... etc
```

**Alternatives Considered**:
- Make ChatBrowserUse the default: Rejected to avoid breaking changes for existing users
- Remove Anthropic default: Rejected for backward compatibility

### 4. Environment Variable Strategy

**Decision**: Maintain all existing environment variables, add new ones for additional providers

**Existing Variables** (keep as-is):
- `FAMILIAR_MODEL_PROVIDER`: Selects provider (openai, anthropic, google, ollama)
- `FAMILIAR_MODEL`: Overrides default model name
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`: Provider-specific auth

**New Variables** (add support):
- `BROWSER_USE_API_KEY`: For ChatBrowserUse provider
- `GROQ_API_KEY`: For Groq provider
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`: For Azure OpenAI

**Rationale**: Backward compatibility is critical. Users shouldn't need to change their configuration.

### 5. Error Handling Strategy

**Decision**: Maintain existing error messages, update import error messages only

**Changes**:
- Update ImportError messages to reference browser-use instead of langchain
- Keep ValueError messages for missing API keys (same behavior)
- Keep provider validation logic (same behavior)

**Example**:
```python
# OLD
raise ImportError("langchain-openai package required...")

# NEW  
raise ImportError("browser-use package includes ChatOpenAI. Ensure browser-use is installed.")
```

**Rationale**: Error messages should guide users to correct solution. Browser-use includes all model providers by default.

## Best Practices Research

### Browser-Use Model Usage Patterns

**Research Finding**: Browser-use models are designed to work seamlessly with the Agent class:

```python
# Standard pattern from browser-use examples
from browser_use import Agent, ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-0", temperature=0.7)
agent = Agent(task="...", llm=llm, browser=browser)
result = await agent.run()
```

**Application to Familiar**:
- Our `create_browser_use_agent()` function already follows this pattern
- No changes needed to agent creation logic
- Only the LLM creation changes

### Model Configuration Parameters

**Research Finding**: Browser-use model classes support standard parameters:

**Common Parameters** (across all providers):
- `model`: Model name/identifier (string)
- `temperature`: Response randomness (float, 0.0-1.0)
- `max_tokens`: Maximum response tokens (int, optional)
- `timeout`: Request timeout (float, optional)

**Provider-Specific**:
- **OpenAI**: `api_key`, `base_url` (for compatible APIs)
- **Anthropic**: `api_key`, `max_tokens` defaults to 4096
- **Google**: `api_key`, uses `gemini-flash-latest` or specific version
- **Ollama**: No API key, optional `base_url` for remote Ollama

**Application to Familiar**:
- We currently only pass `model` and `temperature`
- This will continue to work with browser-use classes
- Can expand to support additional parameters in future

### Dependency Management

**Research Finding**: Browser-use bundles model providers as optional dependencies

**browser-use Package Structure**:
```
browser-use/
├── agent.py
├── browser.py
├── models/
│   ├── openai.py       # ChatOpenAI
│   ├── anthropic.py    # ChatAnthropic
│   ├── google.py       # ChatGoogle
│   └── ...
```

**Implications**:
- No need to install separate `langchain-*` packages
- Browser-use has its own abstractions
- Lighter dependency footprint

**Dependencies to Remove** from `pyproject.toml`:
```toml
# REMOVE these:
langchain-openai = "..."
langchain-anthropic = "..."
langchain-google-genai = "..."
langchain-ollama = "..."
```

**Dependencies to Keep**:
```toml
browser-use = "^0.1.0"  # Already present
playwright = "^1.40.0"   # Already present
```

## Integration Patterns

### Current Pattern (Incorrect)

```python
def create_llm(temperature: float = 0.5) -> Any:
    provider = os.getenv("FAMILIAR_MODEL_PROVIDER", "anthropic")
    
    if provider == "openai":
        from langchain_openai import ChatOpenAI  # ❌ Wrong
        return ChatOpenAI(model=..., temperature=temperature)
    # ...
```

### New Pattern (Correct)

```python
def create_llm(temperature: float = 0.5) -> Any:
    provider = os.getenv("FAMILIAR_MODEL_PROVIDER", "anthropic")
    
    if provider == "openai":
        from browser_use import ChatOpenAI  # ✅ Correct
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY required")
        return ChatOpenAI(model=model or "gpt-4o", temperature=temperature)
    # ...
```

### Key Differences

1. **Import source**: `browser_use` instead of `langchain_*`
2. **Class names**: `ChatGoogle` instead of `ChatGoogleGenerativeAI`
3. **No additional abstractions**: Direct usage of browser-use classes
4. **Error messages**: Reference browser-use, not langchain packages

## Testing Strategy

### Unit Tests

**Existing Tests** to verify:
- `tests/unit/test_utils.py`: Tests for `create_llm()` and `create_browser_use_agent()`
- May need to update mocks if they mock langchain classes

**Test Updates Needed**:
```python
# OLD (if using mocks)
@patch('langchain_openai.ChatOpenAI')

# NEW
@patch('browser_use.ChatOpenAI')
```

### Integration Tests

**Existing Tests** should pass without changes:
- `tests/integration/test_runner.py`: End-to-end test execution
- These test behavior, not implementation
- Should work identically with browser-use native classes

### Manual Testing

**Test Matrix**:
| Provider | Model | Environment Variables | Expected Result |
|----------|-------|----------------------|-----------------|
| anthropic | claude-sonnet-4-0 | `ANTHROPIC_API_KEY` | ✅ Agent runs task |
| openai | gpt-4o | `OPENAI_API_KEY` | ✅ Agent runs task |
| google | gemini-flash-latest | `GOOGLE_API_KEY` | ✅ Agent runs task |
| ollama | llama3.1:8b | None (local) | ✅ Agent runs task |

## Risk Assessment

### Low Risk Areas
- ✅ Model provider selection logic (same structure)
- ✅ Environment variable handling (unchanged)
- ✅ Public API surface (no changes to `create_browser_use_agent`)
- ✅ Temperature and configuration parameters (same)

### Medium Risk Areas
- ⚠️ Default model names may differ between LangChain and browser-use versions
- ⚠️ Error message changes may confuse users temporarily
- ⚠️ Unit tests may need mock updates

### Mitigation Strategies
- Explicitly set default model names (don't rely on provider defaults)
- Test with all supported providers before merge
- Update error messages to be clear and actionable
- Verify test suite passes completely

## Implementation Checklist

- [ ] Update imports in `browser.py` to use `browser_use` package
- [ ] Replace LangChain class names with browser-use equivalents
- [ ] Update `ChatGoogleGenerativeAI` → `ChatGoogle`
- [ ] Add support for `ChatBrowserUse` provider
- [ ] Update ImportError messages
- [ ] Remove langchain dependencies from `pyproject.toml`
- [ ] Update any mocks in unit tests
- [ ] Run full test suite
- [ ] Manual test with each provider (if API keys available)
- [ ] Update documentation/README with new provider info

## References

- Browser-use documentation: https://docs.browser-use.com/models
- Browser-use GitHub examples: https://github.com/browser-use/browser-use/tree/main/examples/models
- Browser-use source code: https://github.com/browser-use/browser-use

