# Contract: browser.py Module Interface

**Module**: `src/familiar/utils/browser.py`  
**Purpose**: Provide LLM client creation and browser-use agent initialization  
**Version**: 1.0 (post bug-fix)

## Public Functions

### create_llm()

**Signature**:
```python
def create_llm(temperature: float = 0.5) -> Any
```

**Purpose**: Create an LLM client based on environment configuration

**Parameters**:
- `temperature` (float, optional): LLM temperature for response variability
  - Range: 0.0 to 1.0
  - Default: 0.5
  - Lower values = more deterministic responses
  - Higher values = more creative/random responses

**Returns**:
- `Any`: Browser-use LLM client instance
  - Concrete type depends on `FAMILIAR_MODEL_PROVIDER` environment variable
  - All returned types are compatible with `browser_use.Agent`

**Raises**:
- `ValueError`: When required API key is missing for selected provider
- `ValueError`: When `FAMILIAR_MODEL_PROVIDER` specifies unsupported provider
- `ImportError`: When browser-use package is not installed (should not occur in normal usage)

**Environment Variables** (input):
- `FAMILIAR_MODEL_PROVIDER` (required): Selects LLM provider
  - Supported values: `"openai"`, `"anthropic"`, `"google"`, `"gemini"`, `"ollama"`, `"browser-use"`, `"groq"`, `"azure"`
  - Default: `"anthropic"`
  
- `FAMILIAR_MODEL` (optional): Overrides default model name
  - Format: Provider-specific model identifier
  - Examples: `"gpt-4o"`, `"claude-sonnet-4-0"`, `"gemini-flash-latest"`
  
- Provider-specific API keys (required for most providers):
  - `OPENAI_API_KEY`: For OpenAI provider
  - `ANTHROPIC_API_KEY`: For Anthropic provider
  - `GOOGLE_API_KEY`: For Google/Gemini provider
  - `GROQ_API_KEY`: For Groq provider
  - `BROWSER_USE_API_KEY`: For Browser Use provider
  - `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY`: For Azure OpenAI
  - Note: Ollama does not require an API key

**Contract Guarantees**:
1. Returns a valid LLM client compatible with `browser_use.Agent`
2. Temperature parameter is applied to the returned client
3. Model name is either default for provider or overridden by `FAMILIAR_MODEL`
4. Raises `ValueError` (not silent failure) if configuration is invalid
5. Function is deterministic for same environment configuration

**Example Usage**:
```python
import os
os.environ["FAMILIAR_MODEL_PROVIDER"] = "openai"
os.environ["OPENAI_API_KEY"] = "sk-..."

llm = create_llm(temperature=0.7)
# Returns: ChatOpenAI instance configured with temperature=0.7
```

**Error Examples**:
```python
# Missing API key
os.environ["FAMILIAR_MODEL_PROVIDER"] = "openai"
# os.environ["OPENAI_API_KEY"] not set
create_llm()
# Raises: ValueError("OPENAI_API_KEY environment variable required for OpenAI provider")

# Unsupported provider
os.environ["FAMILIAR_MODEL_PROVIDER"] = "invalid"
create_llm()
# Raises: ValueError("Unsupported model provider: invalid. Supported providers: ...")
```

---

### create_browser_use_agent()

**Signature**:
```python
async def create_browser_use_agent(
    task: str,
    headless: bool = True,
    temperature: float = 0.5,
) -> Agent
```

**Purpose**: Create and configure a browser-use agent for test execution

**Parameters**:
- `task` (str, required): Natural language task description for the agent to execute
  - Example: `"Navigate to google.com and search for 'python'"`
  - Should be clear, actionable instructions
  
- `headless` (bool, optional): Whether to run browser in headless mode
  - Default: `True`
  - `True` = no visible browser window (faster, for CI/CD)
  - `False` = visible browser window (for debugging)
  
- `temperature` (float, optional): LLM temperature for agent decision making
  - Range: 0.0 to 1.0
  - Default: 0.5
  - Passed to `create_llm()` internally

**Returns**:
- `browser_use.Agent`: Configured agent instance ready to execute the task
  - Agent is initialized but not yet started
  - Call `await agent.run()` to execute the task

**Raises**:
- Same exceptions as `create_llm()` (ValueError, ImportError)
- Potentially browser initialization errors (from playwright/browser-use)

**Environment Variables** (indirect, via `create_llm()`):
- All environment variables from `create_llm()` apply
- Agent creation depends on successful LLM creation

**Contract Guarantees**:
1. Returns a fully configured `Agent` instance
2. Agent is configured with:
   - Specified task
   - LLM created via `create_llm(temperature)`
   - Browser instance with specified headless mode
3. Agent is NOT yet running (awaits `agent.run()` call)
4. Browser is initialized but not yet navigated
5. Function is async (must be awaited)

**Example Usage**:
```python
import asyncio
import os

os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

async def main():
    agent = await create_browser_use_agent(
        task="Navigate to example.com and verify the page title",
        headless=True,
        temperature=0.5
    )
    result = await agent.run()
    return result

asyncio.run(main())
```

**Execution Flow**:
```
create_browser_use_agent()
  ↓
  1. Call create_llm(temperature)
  ↓
  2. Create Browser(headless=headless)
  ↓
  3. Create Agent(task=task, llm=llm, browser=browser)
  ↓
  4. Return agent instance
```

## Implementation Changes (Bug Fix)

### Before (Incorrect)

```python
def create_llm(temperature: float = 0.5) -> Any:
    provider = os.getenv("FAMILIAR_MODEL_PROVIDER", "anthropic").lower()
    
    if provider == "openai":
        from langchain_openai import ChatOpenAI  # ❌ Wrong
        # ...
```

### After (Correct)

```python
def create_llm(temperature: float = 0.5) -> Any:
    provider = os.getenv("FAMILIAR_MODEL_PROVIDER", "anthropic").lower()
    
    if provider == "openai":
        from browser_use import ChatOpenAI  # ✅ Correct
        # ...
```

### Contract Preservation

**Critical**: The bug fix changes ONLY the internal implementation:
- Function signatures remain identical
- Parameter types remain identical
- Return types remain identical (semantically)
- Error behavior remains identical
- Environment variable handling remains identical

**No breaking changes** to consumers of this module.

## Testing Contract

### Unit Tests

Tests MUST verify:
1. `create_llm()` returns appropriate model instance for each provider
2. Temperature parameter is applied correctly
3. Missing API keys raise `ValueError` with appropriate message
4. Invalid provider raises `ValueError` with list of supported providers
5. `create_browser_use_agent()` returns `Agent` instance
6. Agent is configured with correct task, headless mode, and LLM

### Integration Tests

Tests MUST verify:
1. Agent created by `create_browser_use_agent()` can execute real tasks
2. All supported providers can successfully run a simple task
3. Headless and headed modes both work
4. Temperature parameter affects agent behavior appropriately

### Contract Tests

Tests MUST verify:
1. Function signatures match contract specification
2. Return types are compatible with expected usage
3. Error messages match contract specification
4. Environment variable handling matches contract specification

## Version History

- **v1.0** (2025-11-13): Initial contract post-bug-fix
  - Replaces LangChain with browser-use native model providers
  - No API changes, internal implementation only

