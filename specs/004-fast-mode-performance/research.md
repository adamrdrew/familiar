# Research: Fast Mode & Browser Performance Configuration

**Feature**: 004-fast-mode-performance  
**Date**: 2025-11-13  
**Status**: Phase 0 Complete

---

## Research Areas

### 1. browser-use BrowserProfile API

**Question**: What parameters does `BrowserProfile` accept? What are the defaults?

**Findings**:

From browser-use documentation and examples, `BrowserProfile` supports:

```python
from browser_use import BrowserProfile

profile = BrowserProfile(
    minimum_wait_page_load_time=0.1,  # Default: 1.0 (seconds)
    wait_between_actions=0.1,         # Default: 1.0 (seconds)
    headless=True,                    # Default: True
    # Additional parameters may exist, but these are documented
)
```

**Usage with Browser**:
```python
from browser_use import Browser, BrowserProfile

browser = Browser(
    headless=True,
    browser_profile=profile,  # Optional parameter
    keep_alive=True,         # Our current usage
)
```

**Decision**: Use these three parameters in our `BrowserProfileConfig`:
- `minimum_wait_page_load_time: float = 1.0`
- `wait_between_actions: float = 1.0`
- `headless: bool = True`

**Note**: `headless` will be overridden by CLI flag (`--no-headless`) for consistency with existing behavior.

---

### 2. Agent flash_mode and extend_system_message

**Question**: How do `flash_mode` and `extend_system_message` work on Agent?

**Findings**:

From browser-use documentation:

```python
from browser_use import Agent

agent = Agent(
    task="Your task here",
    llm=llm,
    browser=browser,
    flash_mode=True,                    # Disables LLM thinking output (faster)
    extend_system_message="Additional prompt",  # Appends to system message
)
```

**`flash_mode`**:
- When `True`, disables verbose "thinking" output from LLM
- Reduces token generation → faster inference
- May reduce quality for complex reasoning tasks
- **Default**: `False`

**`extend_system_message`**:
- String appended to the base system prompt
- Does NOT replace the core agent instructions
- Used for context-specific modifications (like speed optimization)
- **Default**: `None` or empty string

**Speed Optimization Prompt** (from browser-use examples):
```python
SPEED_OPTIMIZATION_PROMPT = """
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
"""
```

**Decision**:
- Store `SPEED_OPTIMIZATION_PROMPT` as module constant in `runner.py`
- Pass `flash_mode=True` and `extend_system_message=SPEED_OPTIMIZATION_PROMPT` when `--fast` flag is present
- Both parameters are optional, so no changes needed when fast mode is off

---

### 3. Pydantic Optional Nested Models

**Question**: How do we handle optional nested Pydantic models with defaults?

**Findings**:

Pydantic v2 supports optional nested models with field defaults:

```python
from pydantic import BaseModel, Field
from typing import Optional

class BrowserProfileConfig(BaseModel):
    minimum_wait_page_load_time: float = 1.0
    wait_between_actions: float = 1.0
    headless: bool = True

class SuiteConfig(BaseModel):
    name: str
    temperature: float = 0.5
    # ... existing fields ...
    browser_profile: Optional[BrowserProfileConfig] = None
    # OR with default instance:
    # browser_profile: BrowserProfileConfig = Field(default_factory=BrowserProfileConfig)
```

**YAML Parsing**:
```yaml
# Option 1: Omit browser_profile entirely (uses None)
name: "Test Suite"
temperature: 0.5

# Option 2: Provide browser_profile (uses custom values)
name: "Fast Suite"
browser_profile:
  minimum_wait_page_load_time: 0.1
  wait_between_actions: 0.1
  headless: true
```

**Accessing in Code**:
```python
config = SuiteConfig(**yaml_data)

# Option 1: Check if present
if config.browser_profile:
    profile = config.browser_profile
else:
    profile = BrowserProfileConfig()  # Use defaults

# Option 2: Use OR operator
profile = config.browser_profile or BrowserProfileConfig()
```

**Decision**:
- Use `Optional[BrowserProfileConfig] = None` (cleaner for optional config)
- In runner, use: `profile_config = suite.config.browser_profile or BrowserProfileConfig()`
- This allows backward compatibility (missing field → None → defaults)

**Validation**:
- Pydantic automatically validates nested models
- Invalid values (negative numbers, wrong types) raise ValidationError
- No custom validation needed for basic types

---

### 4. Click CLI Flag Patterns

**Question**: What's the best pattern for adding `--fast` flag to existing `run` command?

**Findings**:

Current `run` command structure in Familiar:
```python
@click.command()
@click.argument("suite_path", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True)
@click.option("--no-headless", is_flag=True)
@click.option("--all", "run_all", is_flag=True)
def run(suite_path: str, verbose: bool, no_headless: bool, run_all: bool):
    # ...
```

**Adding --fast flag**:
```python
@click.option("--fast", is_flag=True, help="Enable speed optimizations (flash mode, fast timing)")
def run(suite_path: str, verbose: bool, no_headless: bool, run_all: bool, fast: bool):
    # Pass to runner
    runner = SuiteRunner(
        headless=not no_headless,
        fast_mode=fast,  # New parameter
    )
```

**Flag Combinations**:
- `--fast` alone: Enable fast mode with defaults
- `--fast --verbose`: Fast mode + detailed output (useful for debugging)
- `--fast --no-headless`: Fast mode + visible browser (for development)
- `--all --fast`: Fast mode for all discovered suites

**Help Text**:
```bash
$ familiar run --help

Options:
  --fast              Enable speed optimizations (flash mode, reduced wait times)
  -v, --verbose       Show detailed execution logs
  --no-headless       Run browser in headed mode
  --all               Run all discovered suites
```

**Decision**:
- Add `--fast` as boolean flag (no parameters needed)
- Help text explains it's a speed/reliability tradeoff
- Pass as `fast_mode` parameter to `SuiteRunner`

---

### 5. Performance Baseline Testing

**Question**: What performance improvement can we expect from fast mode?

**Theoretical Analysis**:

**Time Components of a 3-Step Test**:

| Component | Standard Mode | Fast Mode | Savings |
|-----------|---------------|-----------|---------|
| LLM inference (3 steps) | 3-5s per step | 1-2s per step | 40-60% |
| Page load waits (3 pages) | 3.0s (3×1.0s) | 0.3s (3×0.1s) | 90% |
| Action waits (5 actions) | 5.0s (5×1.0s) | 0.5s (5×0.1s) | 90% |
| Actual work (navigation, clicks) | ~5s | ~5s | 0% |
| **Total Estimated** | **23-28s** | **9-12s** | **55-65%** |

**Expected Speedup**: 2-3x faster

**Factors Affecting Speedup**:
- **High speedup scenarios**: Simple tests, fast LLM provider (Groq), stable pages
- **Low speedup scenarios**: Complex reasoning, slow LLM provider, unstable pages
- **No speedup**: Network-bound operations, video loading, animations

**Measurement Strategy**:
```python
# Baseline test: Simple 3-step login flow
# - Navigate to page
# - Enter credentials
# - Verify login

# Standard mode: ~25-30 seconds
# Fast mode: ~10-15 seconds
# Expected: 40-50% improvement
```

**Decision**:
- Target: 30-60% speedup (conservative estimate)
- Document that speedup varies by scenario
- Recommend fast mode for development, standard for production

---

## Research Summary

### Decisions Made

1. **BrowserProfile Configuration**
   - Use `minimum_wait_page_load_time`, `wait_between_actions`, `headless`
   - Default values: 1.0s, 1.0s, True
   - CLI `--no-headless` overrides suite `headless` setting

2. **Agent Speed Optimization**
   - Use `flash_mode=True` for fast mode
   - Use `extend_system_message` with speed optimization prompt
   - Both parameters optional (only used when `--fast` flag present)

3. **Configuration Model**
   - Use `Optional[BrowserProfileConfig] = None` pattern
   - Backward compatible (missing field uses defaults)
   - Pydantic handles validation automatically

4. **CLI Flag Implementation**
   - Add `--fast` boolean flag to `run` command
   - Pass as `fast_mode` parameter to `SuiteRunner`
   - Compatible with all existing flags

5. **Performance Expectations**
   - Target: 30-60% speedup for simple scenarios
   - May vary based on LLM provider, page complexity, network
   - Document speed/reliability tradeoff clearly

### Alternatives Considered

1. **Separate CLI flags for each optimization**
   - Example: `--flash-mode`, `--fast-waits`, `--speed-prompt`
   - Rejected: Too granular, users want simple "go fast" option
   - Chosen: Single `--fast` flag enables all optimizations

2. **Speed presets in suite.yaml**
   - Example: `browser_profile: "fast"` shorthand
   - Rejected: Adds complexity, explicit is better
   - Chosen: Explicit numeric values in config

3. **Automatic fast mode detection**
   - Example: Auto-enable for Groq/Gemini Flash providers
   - Rejected: Implicit behavior violates humane code principle
   - Chosen: Explicit opt-in via flag

### Best Practices Applied

1. **Backward Compatibility**
   - Optional fields with sensible defaults
   - Existing tests work unchanged
   - No breaking changes to public APIs

2. **Dependency Injection**
   - BrowserProfile injected into Browser
   - Fast mode flag injected into SuiteRunner
   - No global state or singletons

3. **Explicit Over Implicit**
   - `--fast` flag is explicit user choice
   - Config values are explicit numbers
   - No magic behavior

4. **Single Responsibility**
   - `BrowserProfileConfig` only handles browser timing
   - Fast mode flag only controls Agent parameters
   - Each class has one reason to change

---

## Open Questions (Resolved)

~~1. Should fast mode be per-suite or per-run?~~
- **Decision**: Per-run via CLI flag (more flexible)

~~2. What default values for fast mode timing?~~
- **Decision**: 0.1s (from browser-use documentation)

~~3. Should headless be in browser_profile?~~
- **Decision**: Yes, but CLI flag overrides (consistency)

~~4. How to handle missing browser_profile in YAML?~~
- **Decision**: Use `Optional[Config] = None`, provide defaults in code

---

## Risk Mitigation

### Risk: Users Over-Rely on Fast Mode

**Mitigation**:
- Clear documentation of speed/reliability tradeoff
- Examples showing when to use standard vs. fast mode
- Warning in help text: "May reduce reliability for complex tasks"

### Risk: Fast Mode Breaks Complex Tests

**Mitigation**:
- Fast mode is opt-in (default behavior unchanged)
- Users can test both modes easily
- Integration tests verify fast mode behavior

### Risk: Browser-Use API Changes

**Mitigation**:
- Use only documented parameters
- Version pin browser-use dependency
- Graceful degradation if parameters unsupported

---

## Next Steps (Phase 1: Design)

1. Create `data-model.md` - Document BrowserProfileConfig model
2. Create `contracts/browser-profile-config.yaml` - YAML schema
3. Create `contracts/cli-interface.md` - --fast flag contract
4. Create `quickstart.md` - Fast mode usage examples
5. Update agent context with new technical knowledge

**Phase 0 Research**: ✅ **COMPLETE**

