# Feature Specification: Fast Mode & Browser Performance Configuration

**Feature ID**: 004  
**Priority**: High  
**Type**: Performance Enhancement  
**Status**: Planning

---

## Problem Statement

Familiar tests can be slow due to:
1. LLM inference time with verbose outputs
2. Default browser wait times that may be unnecessarily long
3. Lack of user control over performance/reliability tradeoffs

Users need the ability to optimize test execution speed when working in development environments or with fast, reliable web applications.

---

## Goals

### Primary Goals
1. **Fast Mode CLI Option**: Add `--fast` flag to enable speed-optimized LLM behavior
2. **Browser Configuration**: Expose browser timing controls in `suite.yaml` configuration
3. **LLM Flash Mode**: Support `flash_mode` parameter to skip LLM "thinking" output
4. **Speed Optimization Prompt**: Inject system-level prompt to encourage concise, fast LLM responses

### Non-Goals
- Automatic performance tuning (users must explicitly enable fast mode)
- Default behavior changes (existing tests remain unchanged)
- Provider-specific optimizations beyond prompt engineering

---

## Requirements

### Functional Requirements

#### FR1: Fast Mode CLI Flag
**As a developer**, I want to run tests with `--fast` flag to enable all speed optimizations

```bash
familiar run my-suite --fast
familiar run my-suite --all --fast
```

**Behavior**:
- Enables `flash_mode=True` on Agent
- Injects speed optimization system prompt via `extend_system_message`
- Can be combined with other flags (`--verbose`, `--no-headless`, etc.)

#### FR2: Browser Profile Configuration in suite.yaml
**As a test author**, I want to configure browser timing in my suite configuration

```yaml
name: "Fast Login Test"
browser_profile:
  minimum_wait_page_load_time: 0.1  # seconds (default: 1.0)
  wait_between_actions: 0.1          # seconds (default: 1.0)
  headless: true                     # boolean (default: true)
```

**Behavior**:
- Suite-level configuration overrides defaults
- CLI `--no-headless` flag overrides suite `headless` setting
- Missing `browser_profile` section uses current defaults

#### FR3: Speed Optimization System Prompt
**As a developer**, fast mode should inject this system prompt:

```
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
```

**Behavior**:
- Only injected when `--fast` flag is present
- Appended to existing system messages
- Does not replace core agent instructions

#### FR4: Flash Mode Support
**As a developer**, fast mode should enable flash mode to skip LLM thinking process

**Behavior**:
- Sets `flash_mode=True` on Agent when `--fast` is used
- Reduces LLM output tokens (faster inference)
- May reduce reliability for complex tasks (acceptable tradeoff)

### Non-Functional Requirements

#### NFR1: Backward Compatibility
- Existing tests run unchanged without `--fast` flag
- Existing `suite.yaml` files without `browser_profile` continue to work
- Default behavior remains stable

#### NFR2: Performance Impact
- Fast mode should reduce execution time by 30-60% on simple scenarios
- Fast mode may reduce reliability on complex, multi-step scenarios
- Users understand this is a speed/reliability tradeoff

#### NFR3: Documentation
- README.md documents `--fast` flag and use cases
- suite.yaml schema updated with `browser_profile` options
- Examples show when to use fast mode vs. standard mode

---

## User Stories

### Story 1: Development Testing
```
As a developer iterating on test scenarios,
I want to run tests quickly with --fast flag
So that I can rapidly validate my test logic without waiting for conservative timeouts
```

### Story 2: CI/CD for Stable Apps
```
As a DevOps engineer with a fast, reliable application,
I want to configure shorter browser wait times in suite.yaml
So that our CI/CD pipeline completes faster without unnecessary delays
```

### Story 3: Slow vs. Fast LLM Providers
```
As a user with access to fast LLM providers (Groq, Gemini Flash),
I want fast mode to optimize for speed
So that I can take advantage of ultra-fast inference times
```

---

## Technical Approach

### Architecture Changes

#### 1. CLI Layer (`src/familiar/cli/main.py`)
- Add `--fast` flag to `run` command
- Pass `fast_mode` boolean to `SuiteRunner`

#### 2. Suite Configuration (`src/familiar/models/suite.py`)
- Add `BrowserProfileConfig` Pydantic model
- Add optional `browser_profile` field to `SuiteConfig`
- Provide sensible defaults when field is missing

```python
@dataclass
class BrowserProfileConfig:
    minimum_wait_page_load_time: float = 1.0
    wait_between_actions: float = 1.0
    headless: bool = True

@dataclass
class SuiteConfig:
    # ... existing fields ...
    browser_profile: Optional[BrowserProfileConfig] = None
```

#### 3. Runner Layer (`src/familiar/core/runner.py`)
- Accept `fast_mode` parameter in constructor
- Create `BrowserProfile` from suite config
- Pass `flash_mode` and `extend_system_message` to Agent when fast mode enabled

```python
from browser_use import BrowserProfile

SPEED_OPTIMIZATION_PROMPT = """
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
"""

class SuiteRunner:
    def __init__(self, headless: bool = True, fast_mode: bool = False):
        self.headless = headless
        self.fast_mode = fast_mode
    
    async def run_suite(self, suite: TestSuite):
        # Create BrowserProfile from suite config
        profile_config = suite.config.browser_profile or BrowserProfileConfig()
        browser_profile = BrowserProfile(
            minimum_wait_page_load_time=profile_config.minimum_wait_page_load_time,
            wait_between_actions=profile_config.wait_between_actions,
            headless=self.headless,  # CLI override
        )
        
        browser = Browser(
            headless=self.headless,
            browser_profile=browser_profile,
            keep_alive=True,
        )
        
        # ... agent creation ...
        agent_kwargs = {
            "task": task,
            "llm": llm,
            "browser": browser,
        }
        
        if self.fast_mode:
            agent_kwargs["flash_mode"] = True
            agent_kwargs["extend_system_message"] = SPEED_OPTIMIZATION_PROMPT
        
        agent = Agent(**agent_kwargs)
```

#### 4. Executor Layer (`src/familiar/core/executor.py`)
- Accept optional `browser_profile` parameter
- Pass to Agent creation (already refactored for session persistence)

---

## Acceptance Criteria

### AC1: Fast Mode CLI
- [ ] `familiar run suite --fast` executes with flash_mode enabled
- [ ] `familiar run suite --fast --verbose` shows speed optimization prompt in logs
- [ ] `familiar run suite --all --fast` applies fast mode to all suites
- [ ] Fast mode reduces execution time by ≥30% on sample test (3+ steps)

### AC2: Browser Profile Configuration
- [ ] Suite with `browser_profile` section uses configured values
- [ ] Suite without `browser_profile` uses default values (1.0s waits)
- [ ] CLI `--no-headless` overrides suite `headless: true` setting
- [ ] Invalid browser_profile values raise clear validation errors

### AC3: Speed Optimization
- [ ] Fast mode injects speed optimization system prompt
- [ ] Fast mode enables flash_mode on Agent
- [ ] Non-fast mode does NOT inject prompt or enable flash_mode
- [ ] Speed prompt is appended (does not replace core instructions)

### AC4: Backward Compatibility
- [ ] Existing tests without --fast flag run unchanged
- [ ] Existing suite.yaml files without browser_profile work unchanged
- [ ] Test suite execution time matches baseline for non-fast mode

### AC5: Documentation
- [ ] README.md documents --fast flag with examples
- [ ] README.md documents browser_profile configuration
- [ ] Examples include fast-mode-optimized suite
- [ ] Performance tradeoffs clearly explained

---

## Examples

### Example 1: Fast Mode CLI

```bash
# Development: Run quickly with speed optimizations
familiar run tests/login-flow --fast

# Production: Run with reliable defaults
familiar run tests/login-flow
```

### Example 2: Browser Profile Configuration

**tests/fast-suite/suite.yaml**:
```yaml
name: "Fast Login Test"
temperature: 0.0
step_timeout: 30
browser_profile:
  minimum_wait_page_load_time: 0.1
  wait_between_actions: 0.1
  headless: true
retry_policy:
  type: "fixed"
  max_retries: 1
```

### Example 3: Performance Comparison

| Mode | Browser Waits | Flash Mode | System Prompt | Typical 3-Step Test |
|------|---------------|------------|---------------|-------------------|
| Standard | 1.0s | No | Standard | ~25-30 seconds |
| Fast | 0.1s | Yes | Speed-optimized | ~10-15 seconds |

**Speed improvement**: 40-50% faster

---

## Migration Guide

### For Existing Users

**No changes required!** Existing tests continue to work with default behavior.

### To Enable Fast Mode

**Option 1**: Use CLI flag for one-off speed optimization
```bash
familiar run my-suite --fast
```

**Option 2**: Configure suite for permanent speed optimization
```yaml
# my-suite/suite.yaml
browser_profile:
  minimum_wait_page_load_time: 0.2
  wait_between_actions: 0.2
```

**Option 3**: Combine both for maximum speed
```bash
familiar run my-fast-suite --fast  # Uses suite browser_profile + fast mode prompt
```

### Recommended Fast LLM Providers

For best results with `--fast` mode:

```bash
# Groq - Ultra-fast inference
export FAMILIAR_MODEL_PROVIDER="groq"
export FAMILIAR_MODEL="meta-llama/llama-4-maverick-17b-128e-instruct"
export GROQ_API_KEY="your-key"

# OR Google Gemini Flash - Optimized for speed
export FAMILIAR_MODEL_PROVIDER="google"
export FAMILIAR_MODEL="gemini-flash-lite-latest"
export GOOGLE_API_KEY="your-key"
```

---

## Open Questions

1. **Should fast mode be persistent per suite?**
   - Current: CLI flag only
   - Alternative: Add `fast_mode: true` to suite.yaml
   - **Decision**: Start with CLI-only, add suite config if users request it

2. **Should we provide speed presets?**
   - Example: `browser_profile: "fast"` shorthand
   - **Decision**: Not in v1, keep explicit configuration

3. **What are appropriate fast mode default values?**
   - Proposed: 0.1s for both timing values
   - **Decision**: Use 0.1s based on browser-use docs example

---

## Related Documentation

- [browser-use BrowserProfile API](https://github.com/browser-use/browser-use)
- [Fast Agent Example](https://github.com/browser-use/browser-use/tree/main/examples)
- Familiar Suite Schema: `specs/001-ai-e2e-testing/contracts/suite-schema.yaml`

