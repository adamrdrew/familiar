# Data Model: Tech Debt Sprint Changes

**Date**: 2025-11-14  
**Phase**: 1 (Design)  
**Purpose**: Document changes to data models and API surface

## Overview

This document tracks all changes to data models, classes, and API surface during the tech debt sprint. Since this is a refactoring sprint (not new features), the focus is on **removals** and **cleanups** rather than additions.

---

## Model Changes

### TestStep (`src/familiar/models/step.py`)

**BEFORE**:
```python
@dataclass
class TestStep:
    path: Path
    content: str
    order: int
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str: ...
    
    @property
    def variables(self) -> Set[str]: ...  # ⚠️ Barely used
    
    @property
    def resolved_content(self) -> str: ... # ❌ DEAD CODE
```

**AFTER**:
```python
@dataclass
class TestStep:
    path: Path
    content: str
    order: int
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str: ...
    
    # REMOVED: resolved_content (dead code, just returned content)
    # DECISION: Keep variables property (used in executor logs for diagnostics)
```

**Rationale**: `resolved_content` was a placeholder that never did anything useful. The `variables` property is minimally used but provides diagnostic value in logs.

---

### RetryPolicyConfig (`src/familiar/models/suite.py`)

**BEFORE**:
```python
class RetryPolicyConfig(BaseModel):
    type: str = Field(pattern="^(fixed|exponential|best_of_n)$")
    max_retries: int = Field(default=3, ge=0, le=10)
    delay: float = Field(default=1.0, ge=0)
    base_delay: Optional[float] = Field(default=None, ge=0)
    max_delay: Optional[float] = Field(default=None, ge=0)
    multiplier: Optional[float] = Field(default=None, ge=1)  # ❌ NEVER USED
    n_runs: Optional[int] = Field(default=None, ge=1, le=20)
```

**AFTER**:
```python
class RetryPolicyConfig(BaseModel):
    type: str = Field(pattern="^(fixed|exponential|best_of_n)$")
    max_retries: int = Field(default=3, ge=0, le=10)
    delay: float = Field(default=1.0, ge=0)
    base_delay: Optional[float] = Field(default=None, ge=0)
    max_delay: Optional[float] = Field(default=None, ge=0)
    # REMOVED: multiplier (never used, leftover from early design)
    n_runs: Optional[int] = Field(default=None, ge=1, le=20)
```

**Rationale**: The `multiplier` field was never implemented in any retry policy. Exponential backoff uses fixed `2^n` formula.

---

### TestRun (`src/familiar/models/result.py`)

**BEFORE**:
```python
@dataclass
class TestRun:
    """Result of a complete test run."""
    run_id: str
    command: str
    suite_results: List[SuiteResult]
    duration: float
    started_at: datetime
    completed_at: datetime
    environment: Dict[str, str] = field(default_factory=dict)
    
    # ... 9 properties ...
```

**AFTER**:
```python
# REMOVED ENTIRELY - dead code, never used
```

**Rationale**: This class was designed for tracking multi-suite runs but was never actually used. The CLI `run_all_suites_async()` function handles multi-suite aggregation directly with simple variables. If needed in future, can be redesigned based on actual requirements.

---

## API Surface Changes

### Utils Module (`src/familiar/utils/`)

#### browser.py

**REMOVE**:
```python
async def create_browser_use_agent(
    task: str,
    headless: bool = True,
    temperature: float = 0.5,
) -> Agent:
    """Dead code - never called"""
```

**KEEP**:
```python
def create_llm(temperature: float = 0.5) -> Any:
    """Actually used by runner"""
```

**Rationale**: The agent creation is now handled by executor with separate browser/LLM instances for session persistence (spec 003). The `create_browser_use_agent()` was never migrated to the new architecture.

---

#### env.py

**REMOVE**:
```python
def get_required_env(key: str) -> str: ...
def get_optional_env(key: str, default: str = "") -> str: ...
def get_bool_env(key: str, default: bool = False) -> bool: ...
```

**KEEP**:
```python
def get_env_vars(prefix: str = "") -> Dict[str, str]: ...
```

**Rationale**: These helper functions were never used. All env access uses either:
1. `os.getenv()` directly (for LLM provider config in browser.py)
2. `get_env_vars()` (for test variable interpolation)
3. Direct checks in pydantic models

---

#### interpolation.py

**KEEP (with evaluation)**:
```python
def interpolate_variables(text: str, variables: Dict[str, str]) -> str: ...
def extract_variables(text: str) -> list[str]: ...
```

**Decision**: 
- `interpolate_variables()` - ✅ KEEP (used by executor)
- `extract_variables()` - ⚠️ **EVALUATE** during implementation:
  - If only used in tests: Remove
  - If TestStep.variables uses it: Keep (it does use similar logic)
  - Recommendation: **KEEP** (used by TestStep.variables property via regex)

---

### Logging Module (`src/familiar/logging/`)

#### setup.py

**REMOVE (or consolidate)**:
```python
def setup_logging(...): ...  # ❌ Never used
def get_logger(...): ...      # ❌ Never used
```

**DECISION**: **REMOVE entire file** - all logging setup is handled by `handlers.py` with `setup_rich_logging()`.

**Alternative**: Consolidate setup_logging into handlers.py if someone prefers that API (but not currently used anywhere).

---

## Public API Surface Inventory

### Current Public APIs (to be preserved)

**CLI Interface** (stable, no changes):
- `familiar run <suite>` ✅
- `familiar run <dir> --all` ✅
- `familiar discover <dir>` ✅
- `familiar --version` ✅
- All CLI flags (--format, --headless, --verbose, --fast) ✅

**Core Classes** (stable, no changes):
- `TestSuite` ✅
- `TestStep` ✅ (removing 1 dead property)
- `SuiteResult` ✅
- `TestResult` ✅
- `SuiteConfig` ✅ (removing 1 dead field)
- All retry policies ✅

**Core Functions** (stable, no changes):
- `SuiteParser.parse_suite()` ✅
- `TestSuiteDiscovery.discover_suites()` ✅
- `SuiteRunner.run_suite()` ✅
- `StepExecutor.execute_step()` ✅
- `create_retry_policy()` ✅
- `create_llm()` ✅

**Formatters** (stable, no changes):
- `TextFormatter.format()` / `.print()` ✅
- `JSONFormatter.format()` / `.format_discovery()` ✅

**Utilities** (changes noted):
- `interpolate_variables()` ✅ KEEP
- `extract_variables()` ✅ KEEP (used by TestStep.variables)
- `get_env_vars()` ✅ KEEP
- ❌ REMOVE: get_required_env, get_optional_env, get_bool_env
- `load_dotenv_file()` ✅ KEEP

---

## Module Structure Changes

### Before
```
src/familiar/
├── logging/
│   ├── handlers.py     # Used
│   └── setup.py        # Dead code
└── ...
```

### After
```
src/familiar/
├── logging/
│   └── handlers.py     # Consolidate everything here
└── ...
```

**Alternative**: Keep `setup.py` with just imports from handlers.py for backward compatibility (but currently nothing imports it).

**Decision**: **REMOVE** `logging/setup.py` entirely. No code imports from it.

---

## Breaking Changes

**NONE** - All removals are of dead code that is not used by any consumers (internal or external).

---

## Test Changes Required

### Remove Tests
- Any tests for removed functions (check if any exist)

### Add Tests
- `create_llm()` - All provider paths
- `JSONFormatter` - Both format methods
- Result model properties
- Logging handlers

### Update Tests
- None required (removals are dead code)

---

## Documentation Updates Required

### README.md
- ✅ No changes (removed functions were internal)

### API Documentation (if exists)
- Remove references to removed functions (unlikely to exist)

### Examples
- ✅ No changes (examples use CLI, not internal APIs)

---

## Migration Guide

**N/A** - No public API changes, therefore no migration needed.

---

## Validation Checklist

Before completing this sprint:

- [ ] All removed code is verified as unused (grep searches)
- [ ] All public APIs still work (run test suite)
- [ ] All examples still work (manual validation)
- [ ] Documentation is accurate (review pass)
- [ ] No breaking changes introduced
- [ ] Test coverage improved (new tests added)

---

**Status**: Draft | **Phase**: 1 | **Date**: 2025-11-14

