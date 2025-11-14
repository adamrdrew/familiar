# Quick Start: Tech Debt Sprint Implementation

**Date**: 2025-11-14  
**Estimated Time**: 7-11 hours  
**Prerequisites**: All tests currently passing, code is working

## Overview

This guide provides a step-by-step implementation path for the tech debt sprint. Follow these phases in order for systematic, safe refactoring.

---

## Phase 1: Dead Code Removal (2-3 hours)

### Step 1: Verify Current State
```bash
# Ensure clean starting point
cd /Users/adam/Development/familiar
git status  # Should be clean
pytest tests/ -v  # Should all pass
```

### Step 2: Remove Unused Functions

**Priority Order**: Remove smallest/safest first

```bash
# 1. Remove get_bool_env() from env.py
grep -r "get_bool_env" src/ tests/  # Verify no usages
# Edit src/familiar/utils/env.py - remove lines 67-82
pytest tests/ -v

# 2. Remove get_optional_env() from env.py  
grep -r "get_optional_env" src/ tests/
# Edit src/familiar/utils/env.py - remove lines 54-64
pytest tests/ -v

# 3. Remove get_required_env() from env.py
grep -r "get_required_env" src/ tests/
# Edit src/familiar/utils/env.py - remove lines 36-51
pytest tests/ -v

# 4. Remove multiplier field from RetryPolicyConfig
# Edit src/familiar/models/suite.py - remove line 17
pytest tests/ -v

# 5. Remove resolved_content property from TestStep
grep -r "resolved_content" src/ tests/
# Edit src/familiar/models/step.py - remove lines 37-40
pytest tests/ -v

# 6. Remove TestRun class from result.py
grep -r "TestRun" src/ tests/
# Edit src/familiar/models/result.py - remove lines 154-190
pytest tests/ -v

# 7. Remove create_browser_use_agent() from browser.py
grep -r "create_browser_use_agent" src/ tests/
# Edit src/familiar/utils/browser.py - remove lines 137-177
pytest tests/ -v
```

### Step 3: Remove Unused Logging Module

```bash
# Check if logging/setup.py is imported anywhere
grep -r "from familiar.logging.setup" src/ tests/
grep -r "import familiar.logging.setup" src/ tests/

# If no imports found:
rm src/familiar/logging/setup.py
pytest tests/ -v
```

### Step 4: Commit Dead Code Removal

```bash
git add -A
git commit -m "refactor: remove dead code

- Remove unused env utility functions (get_required_env, get_optional_env, get_bool_env)
- Remove unused TestRun class (never used for multi-suite runs)
- Remove unused create_browser_use_agent function (replaced by separate browser/LLM in spec 003)
- Remove unused multiplier field from RetryPolicyConfig
- Remove unused resolved_content property from TestStep
- Remove unused logging/setup.py module

All removed code was verified as unused via grep searches.
Test suite still passes: 43 tests."
```

**Checkpoint**: All tests should still pass. Code is cleaner but functionally identical.

---

## Phase 2: Add Missing Tests (4-6 hours)

### Step 1: Test Browser LLM Creation

**File**: `tests/unit/test_browser.py` (NEW)

```python
"""Tests for browser-use integration utilities."""
import os
import pytest
from unittest.mock import patch
from familiar.utils.browser import create_llm


class TestCreateLLM:
    """Test LLM client creation."""
    
    def test_create_llm_anthropic(self):
        """Test creating Anthropic LLM client."""
        with patch.dict(os.environ, {
            "FAMILIAR_MODEL_PROVIDER": "anthropic",
            "ANTHROPIC_API_KEY": "test-key",
        }):
            llm = create_llm(temperature=0.5)
            assert llm is not None
            # Verify it's a ChatAnthropic instance (check type or attributes)
    
    def test_create_llm_openai(self):
        """Test creating OpenAI LLM client."""
        # Similar to above
    
    def test_create_llm_invalid_provider(self):
        """Test error handling for invalid provider."""
        with patch.dict(os.environ, {"FAMILIAR_MODEL_PROVIDER": "invalid"}):
            with pytest.raises(ValueError, match="Unsupported model provider"):
                create_llm()
    
    def test_create_llm_missing_api_key(self):
        """Test error handling for missing API key."""
        with patch.dict(os.environ, {"FAMILIAR_MODEL_PROVIDER": "anthropic"}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                create_llm()
```

**Run**: `pytest tests/unit/test_browser.py -v`

### Step 2: Test Formatters

**File**: `tests/unit/test_formatters.py` (NEW)

```python
"""Tests for result formatters."""
import json
from datetime import datetime
from familiar.formatters.json import JSONFormatter
from familiar.models.result import SuiteResult, TestResult, ResultStatus


class TestJSONFormatter:
    """Test JSON formatter."""
    
    def test_format_suite_result(self):
        """Test formatting a suite result."""
        result = SuiteResult(
            suite_name="Test Suite",
            test_results=[
                TestResult(
                    step_name="Step 1",
                    status=ResultStatus.PASSED,
                    duration=1.5,
                )
            ],
            total_duration=1.5,
        )
        
        formatter = JSONFormatter(pretty=True)
        output = formatter.format(result)
        
        # Verify valid JSON
        data = json.loads(output)
        assert data["suite_name"] == "Test Suite"
        assert data["total_tests"] == 1
        assert data["passed_tests"] == 1
    
    def test_format_discovery(self):
        """Test formatting discovery results."""
        # Mock suite objects
        # ...
```

**Run**: `pytest tests/unit/test_formatters.py -v`

### Step 3: Test Result Models

**File**: `tests/unit/test_result_models.py` (NEW)

```python
"""Tests for result model properties and calculations."""
from familiar.models.result import TestResult, SuiteResult, ResultStatus


class TestTestResult:
    """Test TestResult properties."""
    
    def test_success_property(self):
        """Test success property returns True for passed tests."""
        result = TestResult(
            step_name="Test",
            status=ResultStatus.PASSED,
            duration=1.0,
        )
        assert result.success is True
        assert result.passed is True
        assert result.failed is False
    
    def test_retry_count_calculation(self):
        """Test retry count calculation from attempt."""
        result = TestResult(
            step_name="Test",
            status=ResultStatus.PASSED,
            duration=1.0,
            attempt=3,
        )
        assert result.retry_count == 2  # attempt - 1


class TestSuiteResult:
    """Test SuiteResult properties."""
    
    def test_success_with_no_fuzziness(self):
        """Test suite success requires all tests pass when fuzziness=0."""
        # ... test cases ...
    
    def test_success_with_fuzziness(self):
        """Test suite success allows failures with fuzziness>0."""
        # ... test cases ...
    
    def test_success_rate_calculation(self):
        """Test success rate percentage calculation."""
        # ... test cases ...
```

**Run**: `pytest tests/unit/test_result_models.py -v`

### Step 4: Test Logging

**File**: `tests/unit/test_logging.py` (NEW)

```python
"""Tests for logging setup and handlers."""
import logging
from familiar.logging.handlers import create_rich_handler, setup_rich_logging


class TestLoggingHandlers:
    """Test logging handler creation."""
    
    def test_create_rich_handler(self):
        """Test creating a Rich handler."""
        handler = create_rich_handler(level="INFO")
        assert handler is not None
        assert handler.level == logging.INFO
    
    def test_setup_rich_logging(self):
        """Test setting up Rich logging."""
        logger = setup_rich_logging(level="DEBUG")
        assert logger.name == "familiar"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) > 0
```

**Run**: `pytest tests/unit/test_logging.py -v`

### Step 5: Verify Coverage

```bash
# Run with coverage
pytest --cov=src/familiar --cov-report=term-missing --cov-report=html

# Review coverage report
open htmlcov/index.html  # macOS
# Or check terminal output

# Goal: >= 80% coverage for all modules
```

### Step 6: Commit New Tests

```bash
git add tests/
git commit -m "test: add missing test coverage

- Add test_browser.py: test LLM creation for all providers
- Add test_formatters.py: test JSON and text formatters
- Add test_result_models.py: test result properties and calculations
- Add test_logging.py: test logging handler creation

Test coverage increased from X% to Y%."
```

**Checkpoint**: Test count should increase by ~15-20 tests. Coverage should improve significantly.

---

## Phase 3: Documentation Validation (1-2 hours)

### Step 1: Validate Examples

```bash
# Test suite discovery on examples
familiar discover examples/

# Validate each example suite
familiar validate examples/basic-login/ || echo "No validate command yet"
familiar validate examples/e-commerce/ || echo "No validate command yet"

# Manually: Try parsing with Python
python -c "
from pathlib import Path
from familiar.core.parser import SuiteParser
parser = SuiteParser()
suite = parser.parse_suite(Path('examples/basic-login'))
print(f'✓ {suite.name}: {len(suite.steps)} steps')
"
```

### Step 2: Review README.md

Open README.md and verify:
- [ ] CLI commands match actual (lines 445-519)
- [ ] Suite.yaml schema matches SuiteConfig model (lines 361-411)
- [ ] Environment variables list is complete (lines 416-429)
- [ ] LLM providers list is accurate (lines 53-61, 144-172)
- [ ] Fast mode details are accurate (lines 75-88, 597-709)

**Update any inaccuracies found**

### Step 3: Review docs/configuration.md

```bash
# Read and compare to actual models
cat docs/configuration.md
# Compare against:
# - src/familiar/models/suite.py (SuiteConfig)
# - src/familiar/models/suite.py (BrowserProfileConfig)
# - src/familiar/models/suite.py (RetryPolicyConfig)
```

**Update any drift found**

### Step 4: Check examples/README.md

```bash
cat examples/README.md
# Verify all examples listed actually exist
# Verify descriptions match example content
```

### Step 5: Commit Documentation Updates

```bash
git add README.md docs/ examples/
git commit -m "docs: validate and update documentation

- Verify CLI command documentation matches actual interface
- Verify suite.yaml schema documentation matches models
- Verify examples are accurate and parse successfully
- Fix [any specific issues found]"
```

**Checkpoint**: Documentation should be accurate and match code.

---

## Phase 4: Code Quality & Final Validation (1 hour)

### Step 1: Run Linters

```bash
# Check for issues
ruff check src/

# Check specifically for unused imports
ruff check src/ --select F401

# Auto-fix what can be fixed
ruff check src/ --fix

# Format code
ruff format src/ tests/
```

### Step 2: Type Checking

```bash
# If mypy is configured
mypy src/familiar/

# Fix any type errors found
```

### Step 3: Constitution Review

Review long methods:
- `core/executor.py`: `_execute_step_once()` (145 lines)
  - Justification: Error handling and logging dominate. Could extract but would reduce clarity.
- `cli/run.py`: `run_all_suites_async()` (93 lines)
  - Justification: Orchestration code with sequential logic. Extraction would fragment flow.

Document justifications in code if needed.

### Step 4: Final Test Run

```bash
# Full test suite
pytest tests/ -v

# With coverage
pytest --cov=src/familiar --cov-report=term

# Verify:
# - All tests pass
# - Test count increased
# - Coverage improved
```

### Step 5: Manual Smoke Test

```bash
# Test CLI works
familiar --version
familiar discover examples/
familiar discover examples/ --format json

# If possible: run an example suite
# familiar run examples/basic-login --no-headless
```

### Step 6: Commit Code Quality

```bash
git add src/ tests/
git commit -m "style: code quality improvements

- Run ruff to clean up imports and formatting
- Add justifications for long methods (Constitution compliance)
- Verify type hints are present
- All tests passing"
```

---

## Phase 5: Finalize Sprint

### Step 1: Create Implementation Summary

Create `specs/006-tech-debt-sprint/IMPLEMENTATION_SUMMARY.md` using the template in `contracts/refactoring-checklist.md`.

Fill in:
- Lines of code removed
- Tests added
- Coverage metrics
- Changes made

### Step 2: Update Spec Status

```bash
# Mark spec and plan as complete
# Edit specs/006-tech-debt-sprint/spec.md
# Change "Status: Draft" to "Status: Complete"

# Edit specs/006-tech-debt-sprint/plan.md
# Add completion notes
```

### Step 3: Final Commit

```bash
git add specs/006-tech-debt-sprint/
git commit -m "docs: complete tech debt sprint

Created implementation summary with metrics:
- X lines of dead code removed
- X tests added
- Coverage: Y% -> Z%
- Zero breaking changes
- All documentation validated

Sprint complete. Codebase is clean and ready for new features."
```

### Step 4: Push and Review

```bash
# Push branch
git push origin 006-tech-debt-sprint

# Create PR (if using GitHub/GitLab)
# Or merge to master if working alone
```

---

## Success Criteria Checklist

Before merging:

- [ ] All dead code removed (~150 lines)
- [ ] All tests pass (43+ tests, should increase to ~60+)
- [ ] Test coverage >= 80% for public APIs
- [ ] All documentation validated and accurate
- [ ] Examples parse successfully
- [ ] No breaking changes to public API
- [ ] Code formatted with ruff
- [ ] No unused imports
- [ ] Constitution compliance verified
- [ ] IMPLEMENTATION_SUMMARY.md created

---

## Rollback Plan

If issues are discovered:

```bash
# Rollback to master
git checkout master

# Or rollback specific commits
git revert <commit-hash>
```

**Prevention**: Run tests after EACH removal to catch issues early.

---

## Estimated Timeline

- **Phase 1** (Dead Code): 2-3 hours
- **Phase 2** (Tests): 4-6 hours
- **Phase 3** (Docs): 1-2 hours
- **Phase 4** (Quality): 1 hour
- **Phase 5** (Finalize): 0.5 hours

**Total**: 8.5-12.5 hours

Can be done in one long session or split across 2-3 days.

---

## Tips

1. **Run tests frequently**: After each removal, run `pytest -v`
2. **Commit incrementally**: Don't wait until the end
3. **Use grep liberally**: Verify code is unused before removing
4. **Keep master branch stable**: Work on feature branch
5. **Take breaks**: 11 hours is a lot of focused work

---

## Questions to Answer During Implementation

1. Should `logging/setup.py` be removed entirely or kept as compatibility shim?
   - **Recommendation**: Remove (nothing imports it)

2. Should `extract_variables()` be kept or removed?
   - **Recommendation**: Keep (TestStep.variables uses similar logic)

3. Should `variables` property be removed from TestStep?
   - **Recommendation**: Keep (used in logs for diagnostics)

4. Should we add `familiar validate` command for examples?
   - **Recommendation**: Future feature (not part of this sprint)

---

**Status**: Ready for implementation | **Date**: 2025-11-14

