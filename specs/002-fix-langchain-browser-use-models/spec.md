# Fix LangChain Model Provider Bug

**Type**: Bug Fix | **Priority**: Critical | **Date**: 2025-11-13

## Problem Statement

The current implementation in `src/familiar/utils/browser.py` uses LangChain model providers (`langchain-openai`, `langchain-anthropic`, etc.) to interface with LLMs. This is incorrect and violates our architecture specification.

**Browser-use** provides its own built-in model provider classes (`ChatOpenAI`, `ChatAnthropic`, `ChatGoogle`, etc.) that should be used instead. Using LangChain adds an unnecessary dependency layer and may cause compatibility issues.

## Current Implementation (Incorrect)

```python
# src/familiar/utils/browser.py
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

# Custom create_llm() function that wraps langchain
```

## Desired Implementation

Use browser-use's native model providers:

```python
from browser_use import ChatOpenAI, ChatAnthropic, ChatGoogle, ChatOllama, ChatBrowserUse

# Direct usage of browser-use model classes
```

## Supported Providers (browser-use native)

1. **ChatBrowserUse** - Browser Use's optimized in-house model (requires `BROWSER_USE_API_KEY`)
2. **ChatOpenAI** - OpenAI models (requires `OPENAI_API_KEY`)
3. **ChatAnthropic** - Anthropic Claude models (requires `ANTHROPIC_API_KEY`)
4. **ChatGoogle** - Google Gemini models (requires `GOOGLE_API_KEY`)
5. **ChatGroq** - Groq models (requires `GROQ_API_KEY`)
6. **ChatOllama** - Local Ollama models
7. **ChatAzureOpenAI** - Azure OpenAI (requires `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`)
8. **ChatAWSBedrock** - AWS Bedrock models
9. **ChatAnthropicBedrock** - Anthropic via AWS Bedrock
10. **ChatOCIRaw** - Oracle Cloud Infrastructure models

## Requirements

### Functional Requirements

1. **FR1**: Replace LangChain model imports with browser-use native model classes
2. **FR2**: Maintain existing model provider selection logic via `FAMILIAR_MODEL_PROVIDER` environment variable
3. **FR3**: Support all model providers previously supported (openai, anthropic, google, ollama)
4. **FR4**: Maintain backward compatibility with existing environment variables
5. **FR5**: Add support for ChatBrowserUse as the default/recommended provider
6. **FR6**: Preserve temperature and other LLM configuration parameters

### Non-Functional Requirements

1. **NFR1**: Remove dependency on `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`, `langchain-ollama`
2. **NFR2**: No changes to public API of `create_browser_use_agent()` function
3. **NFR3**: All existing tests must pass with updated implementation
4. **NFR4**: Update documentation to reflect browser-use native providers

## Acceptance Criteria

- [ ] `src/familiar/utils/browser.py` imports model classes from `browser_use` instead of langchain packages
- [ ] `create_llm()` function uses browser-use native model classes
- [ ] All model providers (openai, anthropic, google, ollama) work correctly
- [ ] Environment variable handling remains unchanged
- [ ] Existing tests pass without modification
- [ ] pyproject.toml removes langchain dependencies
- [ ] Documentation updated to reference browser-use model providers

## Impact

- **Files Modified**: `src/familiar/utils/browser.py`, `pyproject.toml`, documentation files
- **Dependencies Removed**: `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`, `langchain-ollama`
- **Tests Affected**: May need to update test fixtures if they mock langchain classes
- **Breaking Changes**: None (internal implementation only)

## References

- Browser-use model documentation: https://docs.browser-use.com/models
- Browser-use GitHub examples: https://github.com/browser-use/browser-use/tree/main/examples/models

