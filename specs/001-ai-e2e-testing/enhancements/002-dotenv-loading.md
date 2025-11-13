# Enhancement Plan: Automatic .env File Loading

**Feature**: `001-ai-e2e-testing` | **Enhancement**: `002-dotenv-loading` | **Date**: 2025-11-13  
**Parent Spec**: [../spec.md](../spec.md) | **Parent Plan**: [../plan.md](../plan.md)

## Summary

Add automatic `.env` file loading to Familiar CLI so that environment variables defined in a `.env` file in the current working directory are automatically loaded when Familiar commands are executed. This enhances developer experience by eliminating the need to manually export variables or use shell scripts before running tests.

**Technical Approach**: Use `python-dotenv` library to load `.env` files from the current working directory before CLI command execution. Load order: system env vars (lowest priority) → `.env` file (medium) → command-line overrides (highest).

## Technical Context

**Language/Version**: Python 3.11  
**New Dependencies**: `python-dotenv` (industry standard, 4M+ downloads/month)  
**Integration Point**: CLI entry point (`src/familiar/cli/main.py` or `src/familiar/__main__.py`)  
**Configuration**: None required - automatically searches for `.env` in CWD  
**Behavior**: Silent if no `.env` found, logs warning if `.env` exists but has parse errors  
**Security**: Does NOT override existing environment variables (secure by default)  
**Performance**: <10ms overhead for .env loading

## Constitution Check

*GATE: Must pass before implementation.*

### ✅ I. Easy to Change

- **Pass**: `.env` loading isolated to single utility function
- **Pass**: Can swap `python-dotenv` for alternative if needed (interface-based)
- **Pass**: No changes to existing environment variable access patterns
- **Pass**: Existing code continues to use `os.getenv()` - zero coupling

### ✅ II. Small, Single Purpose Classes

- **Pass**: `DotenvLoader` class with single responsibility: load .env files
- **Pass**: Integration in CLI entry point is 2-3 lines
- **Pass**: No new classes needed - utility function sufficient
- **Design**: Keep loading logic under 50 lines

### ✅ III. Stable, Minimal Public Interfaces

- **Pass**: Public API unchanged - transparent to users
- **Pass**: No new CLI flags or options required
- **Pass**: Environment variable access patterns unchanged
- **Pass**: Backward compatible - existing setups continue working

### ✅ IV. Polymorphism Over Conditionals

- **Pass**: No conditionals for loading - strategy pattern not needed for simple case
- **Pass**: Could use strategy pattern if supporting multiple config formats later
- **Note**: Single format (.env) doesn't warrant polymorphism yet

### ✅ V. Behavior-Based Testing

- **Pass**: Test "loads variables from .env when present"
- **Pass**: Test "preserves existing env vars (no override)"
- **Pass**: Test "works when .env absent"
- **Pass**: Test "logs warning on parse error"
- **Implementation**: Mock filesystem, verify `os.environ` state

### ✅ VI. Code as User Interface

- **Pass**: Feature is invisible to users - perfect UX
- **Pass**: Documentation clear: "place .env file in project root"
- **Pass**: Error messages guide users if .env malformed
- **Pass**: No complex configuration needed

### ✅ VII. Humane Code

- **Pass**: Explicit: load happens at CLI entry point (visible in code)
- **Pass**: Standard: uses widely-known `.env` convention
- **Pass**: Simple: no custom parsing, use battle-tested library
- **Pass**: Clear: comments explain load order and precedence

### ✅ VIII. Test-Driven Development

- **Implementation Order**:
  1. Write tests for .env loading with various scenarios
  2. Implement `load_dotenv_file()` utility function
  3. Integrate into CLI entry point
  4. Verify tests pass
  5. Update documentation

**Gate Status**: ✅ PASS - All constitutional principles satisfied

---

## Phase 0: Research

### R1: python-dotenv Library

**Decision**: Use `python-dotenv` (https://github.com/theskumar/python-dotenv)

**Rationale**:
- Industry standard: 4M+ downloads/month on PyPI
- Zero dependencies
- Mature (v1.0.0+, active maintenance)
- Simple API: `load_dotenv()` does everything
- Supports `.env` syntax standards
- Does NOT override existing env vars by default (secure)

**Alternatives Considered**:
- **python-decouple**: Similar but adds config file concepts (overkill)
- **environs**: Adds validation (not needed - pydantic does this)
- **Custom parsing**: Reinventing wheel, risky for edge cases

**Integration Pattern**:
```python
from dotenv import load_dotenv

# At CLI entry point, before any commands
load_dotenv(verbose=False, override=False)
```

### R2: Load Order and Precedence

**Decision**: System env vars → .env file → CLI flags (lowest to highest priority)

**Rationale**:
- **System env vars**: Lowest priority - defaults and machine config
- **.env file**: Medium priority - project-specific settings
- **CLI flags**: Highest priority - user overrides

**Security**: `.env` files cannot override system env vars by default (`override=False`)

**Use Cases**:
- Local dev: Use .env for credentials
- CI/CD: System env vars override .env (if .env committed)
- Manual override: `FAMILIAR_MODEL=gpt-4 familiar run` wins

### R3: File Location Strategy

**Decision**: Load from current working directory only

**Rationale**:
- Simple: No complex search up directory tree
- Predictable: Always in same place as test suites
- Safe: No accidental loading of .env from parent dirs
- Standard: Matches most tools (.env in project root)

**Behavior**:
- Look for `.env` in `os.getcwd()`
- If not found: Silent (no error)
- If found but invalid: Log warning, continue

### R4: Error Handling Strategy

**Decision**: Fail gracefully - log warnings but don't crash

**Rationale**:
- .env file is optional convenience, not required
- Missing .env should not prevent running tests
- Malformed .env should warn but not crash
- Users can still use system env vars

**Error Scenarios**:
- No .env: Silent success
- Malformed .env: Log warning, skip loading
- Permission denied: Log warning, skip loading

---

## Phase 1: Design

### Data Model

No new data models required. Uses existing:
- Environment variables: `str` (via `os.environ`)
- Configuration: Existing Pydantic models unchanged

### API / Interface Contract

#### Utility Function

```python
# src/familiar/utils/dotenv.py

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def load_dotenv_file(
    dotenv_path: Optional[Path] = None,
    verbose: bool = False,
) -> bool:
    """Load environment variables from .env file.
    
    Loads variables from .env file in current directory (or specified path).
    Does NOT override existing environment variables.
    
    Args:
        dotenv_path: Path to .env file. If None, looks in current directory.
        verbose: If True, log info about loaded variables.
    
    Returns:
        True if .env file was found and loaded, False otherwise.
    
    Example:
        >>> load_dotenv_file()  # Loads from ./.env
        True
        >>> load_dotenv_file(Path("/path/to/.env"))
        True
    """
    ...
```

#### CLI Integration

```python
# src/familiar/cli/main.py or src/familiar/__main__.py

from familiar.utils.dotenv import load_dotenv_file

def cli():
    """Main CLI entry point."""
    # Load .env file before any command execution
    load_dotenv_file()
    
    # Continue with normal CLI setup
    ...
```

### File Structure

```
src/familiar/
├── utils/
│   ├── __init__.py
│   ├── env.py              # Existing env helpers
│   └── dotenv.py           # NEW: .env file loading
├── cli/
│   └── main.py             # MODIFIED: Add load_dotenv_file() call
└── __main__.py             # MODIFIED: Add load_dotenv_file() call (if entry point)

tests/
├── unit/
│   └── test_dotenv.py      # NEW: Unit tests for .env loading
└── integration/
    └── test_cli_dotenv.py  # NEW: Integration tests for CLI with .env
```

### Dependencies

Update `pyproject.toml`:

```toml
[project]
dependencies = [
    "browser-use>=0.1.0",
    "click>=8.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
    "rich>=13.0.0",
    "python-dotenv>=1.0.0",  # NEW
]
```

---

## Implementation Tasks

### T201: Testing (TDD)

- [ ] **T201** [P] Write unit test: load .env when file exists in `tests/unit/test_dotenv.py`
- [ ] **T202** [P] Write unit test: skip silently when .env missing in `tests/unit/test_dotenv.py`
- [ ] **T203** [P] Write unit test: existing env vars NOT overridden in `tests/unit/test_dotenv.py`
- [ ] **T204** [P] Write unit test: log warning on malformed .env in `tests/unit/test_dotenv.py`
- [ ] **T205** [P] Write integration test: CLI loads .env before execution in `tests/integration/test_cli_dotenv.py`

### T206-T210: Implementation

- [ ] **T206** [P] Add python-dotenv dependency to `pyproject.toml`
- [ ] **T207** [P] Run `uv sync` to install python-dotenv
- [ ] **T208** [P] Create `src/familiar/utils/dotenv.py` with `load_dotenv_file()` function
- [ ] **T209** [P] Integrate `load_dotenv_file()` into CLI entry point in `src/familiar/cli/main.py`
- [ ] **T210** [P] Add error handling and logging for .env loading

### T211-T213: Documentation

- [ ] **T211** [P] Update README.md with .env file usage example
- [ ] **T212** [P] Update `docs/configuration.md` with .env file documentation
- [ ] **T213** [P] Add .env example to `examples/basic-login/.env.example`

### T214: Validation

- [ ] **T214** [P] Run full test suite and verify all tests pass

---

## Quickstart: Developer Implementation Guide

### 1. Add Dependency

```bash
cd /Users/adam/Development/familiar
echo 'python-dotenv>=1.0.0' >> requirements.txt  # Or update pyproject.toml
uv sync
```

### 2. Create Utility Function

Create `src/familiar/utils/dotenv.py`:

```python
"""Dotenv file loading utilities."""
from pathlib import Path
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)


def load_dotenv_file(
    dotenv_path: Optional[Path] = None,
    verbose: bool = False,
) -> bool:
    """Load environment variables from .env file.
    
    Loads variables from .env file in current directory (or specified path).
    Does NOT override existing environment variables (secure by default).
    
    Args:
        dotenv_path: Path to .env file. If None, looks for .env in CWD.
        verbose: If True, log info about loaded variables.
    
    Returns:
        True if .env file was found and loaded, False otherwise.
    
    Raises:
        No exceptions raised - fails gracefully with logging.
    
    Example:
        >>> load_dotenv_file()
        True  # Loaded from ./.env
    """
    try:
        from dotenv import load_dotenv
        
        # Determine .env path
        if dotenv_path is None:
            dotenv_path = Path.cwd() / ".env"
        
        # Check if file exists
        if not dotenv_path.exists():
            if verbose:
                logger.debug(f"No .env file found at {dotenv_path}")
            return False
        
        # Load .env file (override=False means existing env vars win)
        load_dotenv(dotenv_path=dotenv_path, override=False, verbose=verbose)
        
        if verbose:
            logger.info(f"Loaded environment variables from {dotenv_path}")
        
        return True
        
    except Exception as e:
        logger.warning(f"Failed to load .env file: {e}")
        return False
```

### 3. Integrate into CLI

Update `src/familiar/cli/main.py`:

```python
from familiar.utils.dotenv import load_dotenv_file

@click.group()
@click.version_option(version=__version__)
def cli():
    """Familiar - AI-driven end-to-end testing."""
    # Load .env file at start of CLI execution
    load_dotenv_file()
    pass
```

### 4. Write Tests

Create `tests/unit/test_dotenv.py`:

```python
import os
import pytest
from pathlib import Path
from familiar.utils.dotenv import load_dotenv_file


def test_load_dotenv_when_file_exists(tmp_path):
    """Test loading variables from .env file."""
    # Create .env file
    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("TEST_VAR=hello\nANOTHER_VAR=world\n")
    
    # Load it
    result = load_dotenv_file(dotenv_path=dotenv_file)
    
    assert result is True
    assert os.getenv("TEST_VAR") == "hello"
    assert os.getenv("ANOTHER_VAR") == "world"


def test_skip_silently_when_dotenv_missing(tmp_path):
    """Test that missing .env file doesn't cause errors."""
    dotenv_file = tmp_path / ".env"  # Doesn't exist
    
    result = load_dotenv_file(dotenv_path=dotenv_file)
    
    assert result is False  # Not found, but no error


def test_existing_env_vars_not_overridden(tmp_path):
    """Test that existing environment variables are preserved."""
    # Set existing var
    os.environ["EXISTING_VAR"] = "original"
    
    # Create .env with same var
    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("EXISTING_VAR=from_dotenv\n")
    
    # Load it
    load_dotenv_file(dotenv_path=dotenv_file)
    
    # Original value should be preserved
    assert os.getenv("EXISTING_VAR") == "original"
```

### 5. Update Documentation

Add to README.md:

```markdown
## Using .env Files

Familiar automatically loads environment variables from a `.env` file in your current directory:

```bash
# Create .env file
cat > .env << EOF
FAMILIAR_MODEL_PROVIDER=anthropic
FAMILIAR_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your-api-key
BASE_URL=https://staging.example.com
TEST_USER=test@example.com
TEST_PASSWORD=securepass123
EOF

# Run familiar - .env is automatically loaded
familiar run tests/login-flow
```

**Note**: Existing environment variables take precedence over `.env` values.
```

---

## Success Criteria

- [ ] `.env` file in CWD is automatically loaded when Familiar commands run
- [ ] Existing environment variables are NOT overridden by .env
- [ ] Missing .env file does not cause errors or warnings
- [ ] Malformed .env file logs warning but doesn't crash
- [ ] All existing tests continue to pass
- [ ] New tests cover .env loading scenarios
- [ ] Documentation updated with .env usage examples

---

## Notes

### Security Considerations

1. **No Override**: `.env` cannot override system env vars (secure by default)
2. **.gitignore**: Examples show .env in .gitignore (best practice)
3. **Logging**: Don't log .env contents (may contain secrets)
4. **Permissions**: Rely on filesystem permissions for .env access control

### User Experience

1. **Zero Config**: Works out of box - just create .env file
2. **Familiar Convention**: Matches tools like Node.js, Rails, Flask
3. **Backward Compatible**: Existing env var workflows unchanged
4. **Optional**: .env is convenience, not requirement

### Future Enhancements

- Support `.env.local`, `.env.production` variants (not in this scope)
- Support loading from multiple locations (not in this scope)
- Support .env.example validation (not in this scope)

---

## Execution Order

1. ✅ Phase 0: Research (Complete above)
2. → **Phase 1**: Implement tests (T201-T205)
3. → **Phase 2**: Implement functionality (T206-T210)
4. → **Phase 3**: Update documentation (T211-T213)
5. → **Phase 4**: Validate (T214)

**Estimated Effort**: 2-3 hours
**Risk Level**: Low (simple, well-understood feature)
**Dependencies**: None (independent enhancement)

