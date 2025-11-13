# Quickstart: Browser-Use Native Model Providers

**Purpose**: Quick guide to verify the bug fix and use browser-use native model providers  
**Date**: 2025-11-13  
**Estimated Time**: 5-10 minutes

## What Changed?

Familiar now uses **browser-use's native model provider classes** instead of LangChain wrappers. This:
- ✅ Removes unnecessary dependencies
- ✅ Ensures compatibility with browser-use
- ✅ Simplifies the codebase
- ✅ Maintains 100% backward compatibility

**Your existing configuration still works!** No changes needed to environment variables or usage.

## Quick Verification

### 1. Check Dependencies (Optional)

If you want to verify the fix, check that langchain packages are removed:

```bash
# View project dependencies
cat pyproject.toml | grep -E "(langchain|browser-use)"

# Should see:
# browser-use = "^0.1.0"
# 
# Should NOT see:
# langchain-openai = ...
# langchain-anthropic = ...
# langchain-google-genai = ...
```

### 2. Run Existing Tests

```bash
# Ensure all tests pass with new implementation
pytest tests/ -v

# Specifically check utils tests
pytest tests/unit/test_utils.py -v
```

**Expected Result**: All tests pass ✅

### 3. Test with Your Provider

Choose your LLM provider and test:

#### Option A: Anthropic (Default)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
familiar run --headed --all
```

#### Option B: OpenAI

```bash
export FAMILIAR_MODEL_PROVIDER="openai"
export OPENAI_API_KEY="sk-..."
familiar run --headed --all
```

#### Option C: Google Gemini

```bash
export FAMILIAR_MODEL_PROVIDER="google"
export GOOGLE_API_KEY="..."
familiar run --headed --all
```

#### Option D: Local Ollama

```bash
# Start Ollama server first: ollama serve
# Pull a model: ollama pull llama3.1:8b

export FAMILIAR_MODEL_PROVIDER="ollama"
export FAMILIAR_MODEL="llama3.1:8b"
familiar run --headed --all
```

**Expected Result**: Tests run successfully with your chosen provider ✅

## New Provider: ChatBrowserUse (Recommended)

Browser-use offers their own optimized model that's **3-5x faster** than alternatives:

### Setup

1. Get an API key from [Browser Use Cloud](https://cloud.browser-use.com/new-api-key)
   - New signups get $10 free credit via OAuth
   - Or $1 via email

2. Configure environment:

```bash
export FAMILIAR_MODEL_PROVIDER="browser-use"
export BROWSER_USE_API_KEY="your-key-here"
```

3. Run tests:

```bash
familiar run --headed --all
```

### Pricing

ChatBrowserUse is cost-effective:
- Input tokens: $0.20 per 1M tokens
- Cached tokens: $0.02 per 1M tokens
- Output tokens: $2.00 per 1M tokens

### When to Use

- ✅ Faster test execution (3-5x speedup)
- ✅ Cost-effective for high-volume testing
- ✅ Optimized specifically for browser automation

## Troubleshooting

### Error: "ANTHROPIC_API_KEY environment variable required"

**Cause**: API key not set for selected provider

**Solution**:
```bash
# Set the API key for your provider
export ANTHROPIC_API_KEY="sk-ant-..."
# or
export OPENAI_API_KEY="sk-..."
# or
export GOOGLE_API_KEY="..."
```

### Error: "Unsupported model provider: xyz"

**Cause**: Invalid value for `FAMILIAR_MODEL_PROVIDER`

**Solution**: Use one of the supported providers:
```bash
export FAMILIAR_MODEL_PROVIDER="anthropic"  # or openai, google, ollama, browser-use, groq
```

### Error: ImportError related to browser-use

**Cause**: browser-use package not installed or outdated

**Solution**:
```bash
# Reinstall dependencies
uv sync
# or
pip install -e .
```

### Tests failing after update

**Cause**: May need to update test mocks

**Solution**:
```bash
# Check if tests mock langchain classes
grep -r "langchain" tests/

# Update any mocks to use browser_use instead
# Example:
# OLD: @patch('langchain_openai.ChatOpenAI')
# NEW: @patch('browser_use.ChatOpenAI')
```

## Code Examples

### Basic Usage (Unchanged)

The public API remains identical:

```python
from familiar.utils.browser import create_browser_use_agent
import os

os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

async def main():
    agent = await create_browser_use_agent(
        task="Navigate to example.com",
        headless=True,
        temperature=0.5
    )
    result = await agent.run()
    return result
```

### Switching Providers

```python
import os

# Use OpenAI instead of Anthropic
os.environ["FAMILIAR_MODEL_PROVIDER"] = "openai"
os.environ["OPENAI_API_KEY"] = "sk-..."

# Use a specific model
os.environ["FAMILIAR_MODEL"] = "gpt-4o"

# Now all agents will use OpenAI
```

### Custom Temperature

```python
# More deterministic (less random)
agent = await create_browser_use_agent(
    task="...",
    temperature=0.1
)

# More creative (more random)
agent = await create_browser_use_agent(
    task="...",
    temperature=0.9
)
```

## What's Different Internally?

### Before (LangChain)

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Wrapped LangChain classes
```

### After (browser-use native)

```python
from browser_use import ChatOpenAI, ChatAnthropic

# Direct browser-use classes
```

### For End Users

**Nothing changes!** The fix is internal only. Your:
- Test suites work identically
- Environment variables work identically
- CLI commands work identically
- Agent behavior is identical

## Next Steps

1. ✅ Verify tests pass
2. ✅ Test with your provider
3. ✅ Optional: Try ChatBrowserUse for faster execution
4. ✅ Continue using Familiar as before

## Support

If you encounter issues:

1. Check this quickstart for solutions
2. Verify your API keys are set correctly
3. Ensure browser-use is installed: `pip show browser-use`
4. Check verbose output: `familiar run -v --headed --all`
5. Review error messages for specific guidance

## Additional Resources

- **Browser-use model docs**: https://docs.browser-use.com/models
- **Browser-use examples**: https://github.com/browser-use/browser-use/tree/main/examples/models
- **Familiar README**: `/README.md`
- **Bug fix spec**: `./spec.md`
- **Implementation plan**: `./plan.md`

