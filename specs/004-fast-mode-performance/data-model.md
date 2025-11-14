# Data Model: Fast Mode & Browser Performance Configuration

**Feature**: 004-fast-mode-performance  
**Date**: 2025-11-13  
**Status**: Phase 1 Design

---

## Overview

This feature introduces one new data model (`BrowserProfileConfig`) and modifies one existing model (`SuiteConfig`) to support browser performance configuration.

---

## New Models

### BrowserProfileConfig

**Purpose**: Encapsulate browser timing and behavior configuration

**Location**: `src/familiar/models/suite.py`

**Type**: Pydantic BaseModel (or Python dataclass with validation)

```python
from pydantic import BaseModel, Field, field_validator

class BrowserProfileConfig(BaseModel):
    """Browser timing and behavior configuration.
    
    Controls how long the browser waits for pages to load and between actions.
    Shorter times = faster tests but may be less reliable for slow pages.
    """
    
    minimum_wait_page_load_time: float = Field(
        default=1.0,
        ge=0.0,
        le=30.0,
        description="Minimum seconds to wait for page loads (0.0-30.0)",
    )
    
    wait_between_actions: float = Field(
        default=1.0,
        ge=0.0,
        le=30.0,
        description="Seconds to wait between browser actions (0.0-30.0)",
    )
    
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode (no GUI)",
    )
    
    @field_validator('minimum_wait_page_load_time', 'wait_between_actions')
    @classmethod
    def validate_timing(cls, v: float) -> float:
        """Ensure timing values are reasonable."""
        if v < 0.0:
            raise ValueError("Wait times cannot be negative")
        if v > 30.0:
            raise ValueError("Wait times above 30s are not recommended")
        return v
    
    def to_browser_profile(self):
        """Convert to browser-use BrowserProfile instance.
        
        Returns:
            BrowserProfile configured with these settings
        """
        from browser_use import BrowserProfile
        
        return BrowserProfile(
            minimum_wait_page_load_time=self.minimum_wait_page_load_time,
            wait_between_actions=self.wait_between_actions,
            headless=self.headless,
        )
```

**Field Descriptions**:

| Field | Type | Default | Valid Range | Description |
|-------|------|---------|-------------|-------------|
| `minimum_wait_page_load_time` | float | 1.0 | 0.0-30.0 | Minimum seconds to wait after page navigation |
| `wait_between_actions` | float | 1.0 | 0.0-30.0 | Seconds to wait between consecutive actions |
| `headless` | bool | True | true/false | Whether to run browser without GUI |

**Validation Rules**:
- Timing values must be ≥ 0.0 (cannot be negative)
- Timing values must be ≤ 30.0 (unreasonably long waits discouraged)
- Invalid values raise `ValidationError` with clear message

**Usage Example**:
```python
# Default configuration
config = BrowserProfileConfig()
# minimum_wait_page_load_time=1.0, wait_between_actions=1.0, headless=True

# Fast configuration
fast_config = BrowserProfileConfig(
    minimum_wait_page_load_time=0.1,
    wait_between_actions=0.1,
    headless=True,
)

# Convert to browser-use BrowserProfile
profile = fast_config.to_browser_profile()
```

---

## Modified Models

### SuiteConfig

**Purpose**: Add optional browser profile configuration

**Location**: `src/familiar/models/suite.py`

**Changes**:

```python
from typing import Optional
from pydantic import BaseModel

class SuiteConfig(BaseModel):
    """Test suite configuration."""
    
    name: str
    temperature: float = 0.5
    step_timeout: int = 60
    timeout: int = 300
    fuzziness: float = 0.0
    retry_policy: RetryPolicyConfig = RetryPolicyConfig()
    
    # NEW FIELD
    browser_profile: Optional[BrowserProfileConfig] = Field(
        default=None,
        description="Browser timing and behavior configuration (optional)",
    )
    
    def get_browser_profile(self) -> BrowserProfileConfig:
        """Get browser profile config, using defaults if not specified.
        
        Returns:
            BrowserProfileConfig with custom or default values
        """
        return self.browser_profile or BrowserProfileConfig()
```

**Backward Compatibility**:
- `browser_profile` field is `Optional` with default `None`
- Existing suite.yaml files without this field parse successfully
- `get_browser_profile()` helper provides defaults when field missing

**YAML Mapping**:

**Before** (existing suite.yaml - still valid):
```yaml
name: "My Test Suite"
temperature: 0.5
step_timeout: 60
timeout: 300
fuzziness: 0.0
retry_policy:
  type: "fixed"
  max_retries: 0
# No browser_profile field
```

**After** (with browser profile):
```yaml
name: "Fast Test Suite"
temperature: 0.0
step_timeout: 30
timeout: 300
fuzziness: 0.0
retry_policy:
  type: "fixed"
  max_retries: 1
browser_profile:
  minimum_wait_page_load_time: 0.1
  wait_between_actions: 0.1
  headless: true
```

---

## Constants

### SPEED_OPTIMIZATION_PROMPT

**Purpose**: System prompt to encourage fast, concise LLM behavior

**Location**: `src/familiar/core/runner.py`

**Type**: String constant

```python
SPEED_OPTIMIZATION_PROMPT = """
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
"""
```

**Usage**:
- Appended to Agent system message when `--fast` flag is present
- Does NOT replace core agent instructions
- Can be modified without code changes (just a constant)

---

## State Transitions

### Fast Mode State Flow

```
┌─────────────────┐
│ CLI Parsing     │
│ --fast flag?    │
└────────┬────────┘
         │
         ├─ Yes ──┐
         │        │
         ├─ No ──┐│
         │       ││
         v       vv
┌────────────────────────┐
│ SuiteRunner.__init__() │
│ fast_mode: bool        │
└───────────┬────────────┘
            │
            v
┌──────────────────────────┐
│ run_suite()              │
│ - Load browser_profile   │
│ - Create BrowserProfile  │
│ - Create Browser         │
│ - Create Agent           │
│   - flash_mode=fast_mode │
│   - extend_system_msg?   │
└──────────────────────────┘
```

### Configuration Loading Flow

```
┌───────────────┐
│ Parse YAML    │
│ suite.yaml    │
└───────┬───────┘
        │
        v
┌──────────────────────┐
│ SuiteConfig.parse()  │
│ - Validate fields    │
│ - browser_profile?   │
└──────────┬───────────┘
           │
           ├─ Present ─────┐
           │               │
           ├─ Missing ────┐│
           │              ││
           v              vv
    ┌────────────────────────────┐
    │ get_browser_profile()      │
    │ - Custom OR Defaults       │
    └──────────┬─────────────────┘
               │
               v
    ┌────────────────────────────┐
    │ to_browser_profile()       │
    │ - Convert to browser-use   │
    │   BrowserProfile           │
    └────────────────────────────┘
```

---

## Relationships

### Model Relationships

```
SuiteConfig
  ├── name: str
  ├── temperature: float
  ├── retry_policy: RetryPolicyConfig
  └── browser_profile: Optional[BrowserProfileConfig]  ← NEW
                                  │
                                  └── minimum_wait_page_load_time: float
                                      wait_between_actions: float
                                      headless: bool
```

### Component Interactions

```
CLI (--fast flag)
    ↓
SuiteRunner (fast_mode: bool)
    ↓
run_suite()
    ├── Load SuiteConfig (from suite.yaml)
    │       ↓
    │   BrowserProfileConfig (optional)
    │       ↓
    │   to_browser_profile()
    │       ↓
    └── Create Browser(browser_profile=...)
            ↓
        Create Agent(
            flash_mode=fast_mode,
            extend_system_message=PROMPT if fast_mode,
            browser=browser,
        )
```

---

## Validation Rules

### BrowserProfileConfig Validation

```python
# Valid configurations
BrowserProfileConfig(minimum_wait_page_load_time=0.1)  # ✓ Fast
BrowserProfileConfig(wait_between_actions=2.0)         # ✓ Slow
BrowserProfileConfig(headless=False)                   # ✓ Visible browser

# Invalid configurations
BrowserProfileConfig(minimum_wait_page_load_time=-1.0) # ✗ Negative wait time
BrowserProfileConfig(wait_between_actions=100.0)       # ✗ Unreasonably long wait
BrowserProfileConfig(headless="yes")                   # ✗ Wrong type (not bool)
```

**Error Messages**:
```
ValidationError: Wait times cannot be negative
ValidationError: Wait times above 30s are not recommended
ValidationError: Input should be a valid boolean
```

---

## Migration & Backward Compatibility

### Existing Data

**Impact**: ✅ **NO MIGRATION NEEDED**

- Existing `suite.yaml` files without `browser_profile` field parse successfully
- Missing field defaults to `None`, which uses default values (1.0s, 1.0s, True)
- No data migration scripts required

### Code Compatibility

**Breaking Changes**: ✅ **NONE**

**Additions**:
- `SuiteConfig.browser_profile: Optional[BrowserProfileConfig]` (new optional field)
- `SuiteConfig.get_browser_profile() -> BrowserProfileConfig` (new helper method)
- `BrowserProfileConfig` class (new model)

**Deprecations**: None

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_models.py

def test_browser_profile_config_defaults():
    """Default values should be 1.0s waits, headless."""
    config = BrowserProfileConfig()
    assert config.minimum_wait_page_load_time == 1.0
    assert config.wait_between_actions == 1.0
    assert config.headless is True

def test_browser_profile_config_custom():
    """Custom values should be preserved."""
    config = BrowserProfileConfig(
        minimum_wait_page_load_time=0.1,
        wait_between_actions=0.2,
        headless=False,
    )
    assert config.minimum_wait_page_load_time == 0.1
    assert config.wait_between_actions == 0.2
    assert config.headless is False

def test_browser_profile_config_validation_negative():
    """Negative wait times should raise error."""
    with pytest.raises(ValidationError, match="cannot be negative"):
        BrowserProfileConfig(minimum_wait_page_load_time=-1.0)

def test_browser_profile_config_validation_too_long():
    """Wait times above 30s should raise error."""
    with pytest.raises(ValidationError, match="above 30s"):
        BrowserProfileConfig(wait_between_actions=100.0)

def test_suite_config_browser_profile_optional():
    """Suite config should work without browser_profile field."""
    data = {"name": "Test", "temperature": 0.5}
    config = SuiteConfig(**data)
    assert config.browser_profile is None
    assert config.get_browser_profile() == BrowserProfileConfig()

def test_suite_config_browser_profile_custom():
    """Suite config should parse nested browser_profile."""
    data = {
        "name": "Test",
        "browser_profile": {
            "minimum_wait_page_load_time": 0.1,
            "wait_between_actions": 0.1,
        }
    }
    config = SuiteConfig(**data)
    assert config.browser_profile is not None
    assert config.browser_profile.minimum_wait_page_load_time == 0.1
```

### Integration Tests

```python
# tests/integration/test_runner.py

async def test_fast_mode_creates_browser_profile():
    """Fast mode should create browser with custom profile."""
    # Create suite with browser_profile config
    # Run with fast_mode=True
    # Verify Browser created with correct timing values
    pass

async def test_browser_profile_from_suite_config():
    """Suite browser_profile should be used when present."""
    # Create suite.yaml with browser_profile
    # Run suite
    # Verify browser uses config values
    pass
```

---

## Performance Considerations

### Memory Impact

- `BrowserProfileConfig` adds ~100 bytes per suite config
- Negligible impact (3 float/bool fields)

### Computation Impact

- Validation on config parse (one-time cost)
- `to_browser_profile()` conversion (one-time per suite)
- No runtime overhead during test execution

### Expected Performance Improvement

With fast mode enabled:
- **LLM inference**: 40-60% faster (flash_mode + speed prompt)
- **Page load waits**: 90% reduction (1.0s → 0.1s per page)
- **Action waits**: 90% reduction (1.0s → 0.1s per action)
- **Overall**: 2-3x speedup for simple scenarios

---

## Summary

**New Models**: 1 (`BrowserProfileConfig`)  
**Modified Models**: 1 (`SuiteConfig` gains optional field)  
**Breaking Changes**: None  
**Migration Required**: None  
**Backward Compatible**: ✅ Yes

