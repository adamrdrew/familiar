# Contract: Tech Debt Sprint Refactoring Checklist

**Purpose**: Track all refactoring tasks and ensure nothing is missed  
**Version**: 1.0  
**Date**: 2025-11-14

## Overview

This checklist ensures systematic completion of all tech debt remediation tasks. Each item must be completed and verified before marking the sprint as done.

---

## Phase 1: Dead Code Removal

### A. Remove Unused Functions

- [ ] **browser.py**: Remove `create_browser_use_agent()` (lines 137-177)
  - [ ] Verify no usages: `grep -r "create_browser_use_agent" src/ tests/`
  - [ ] Remove function
  - [ ] Remove any imports if now unused
  - [ ] Run tests

- [ ] **env.py**: Remove `get_required_env()` (lines 36-51)
  - [ ] Verify no usages: `grep -r "get_required_env" src/ tests/`
  - [ ] Remove function
  - [ ] Run tests

- [ ] **env.py**: Remove `get_optional_env()` (lines 54-64)
  - [ ] Verify no usages: `grep -r "get_optional_env" src/ tests/`
  - [ ] Remove function
  - [ ] Run tests

- [ ] **env.py**: Remove `get_bool_env()` (lines 67-82)
  - [ ] Verify no usages: `grep -r "get_bool_env" src/ tests/`
  - [ ] Remove function
  - [ ] Run tests

- [ ] **logging/setup.py**: Remove `setup_logging()` (lines 7-43)
  - [ ] Verify no usages: `grep -r "setup_logging" src/ tests/` (ignore imports from handlers)
  - [ ] Remove function
  - [ ] Run tests

- [ ] **logging/setup.py**: Remove `get_logger()` (lines 46-57)
  - [ ] Verify no usages: `grep -r "get_logger" src/ tests/`
  - [ ] Remove function
  - [ ] Run tests

- [ ] **logging/setup.py**: Decision - remove entire file or keep as import alias?
  - [ ] If removing: verify no imports of this file
  - [ ] If keeping: add imports from handlers.py for backward compat
  - [ ] Run tests

### B. Remove Unused Classes

- [ ] **result.py**: Remove `TestRun` class (lines 154-190)
  - [ ] Verify no usages: `grep -r "TestRun" src/ tests/`
  - [ ] Remove class
  - [ ] Remove from exports if in `__init__.py`
  - [ ] Run tests

### C. Remove Unused Model Fields/Properties

- [ ] **suite.py**: Remove `multiplier` field from `RetryPolicyConfig` (line 17)
  - [ ] Verify not used in create_retry_policy
  - [ ] Verify not used in any retry policy implementations
  - [ ] Remove field
  - [ ] Run tests

- [ ] **step.py**: Remove `resolved_content` property (lines 37-40)
  - [ ] Verify no usages: `grep -r "resolved_content" src/ tests/`
  - [ ] Remove property
  - [ ] Run tests

- [ ] **step.py**: Decision on `variables` property (lines 31-35)
  - [ ] Check if used beyond logging
  - [ ] If only logging: Consider removal
  - [ ] If useful: Keep and document purpose
  - [ ] Run tests

### D. Decision on Questionable Code

- [ ] **interpolation.py**: Evaluate `extract_variables()` (lines 39-68)
  - [ ] Check if TestStep.variables uses similar logic
  - [ ] Check if only used in tests
  - [ ] Decision: KEEP (used by TestStep.variables via similar regex pattern)
  - [ ] Add documentation if keeping

---

## Phase 2: Test Coverage

### A. High Priority - Add Missing Tests

- [ ] **test_browser.py** (NEW FILE)
  - [ ] Test `create_llm()` with provider="anthropic"
  - [ ] Test `create_llm()` with provider="openai"
  - [ ] Test `create_llm()` with provider="google"
  - [ ] Test `create_llm()` with provider="browser-use"
  - [ ] Test `create_llm()` with provider="groq"
  - [ ] Test `create_llm()` with provider="azure"
  - [ ] Test `create_llm()` with provider="ollama"
  - [ ] Test `create_llm()` with invalid provider (should raise ValueError)
  - [ ] Test `create_llm()` with missing API key (should raise ValueError)
  - [ ] Run: `pytest tests/unit/test_browser.py -v`

- [ ] **test_formatters.py** (NEW FILE)
  - [ ] Test `JSONFormatter.format()` with sample SuiteResult
  - [ ] Test `JSONFormatter.format()` with pretty=True
  - [ ] Test `JSONFormatter.format()` with pretty=False
  - [ ] Test `JSONFormatter.format_discovery()` with sample suites
  - [ ] Test `JSONFormatter.format_discovery()` with empty list
  - [ ] Test JSON is valid (json.loads doesn't raise)
  - [ ] Run: `pytest tests/unit/test_formatters.py -v`

- [ ] **test_result_models.py** (NEW FILE)
  - [ ] Test `TestResult.success` property
  - [ ] Test `TestResult.passed` property (alias)
  - [ ] Test `TestResult.failed` property
  - [ ] Test `TestResult.retry_count` calculation
  - [ ] Test `SuiteResult.success` with fuzziness=0.0
  - [ ] Test `SuiteResult.success` with fuzziness=0.2
  - [ ] Test `SuiteResult.status` property
  - [ ] Test `SuiteResult.success_rate` calculation
  - [ ] Test `SuiteResult` property calculations (total_tests, passed_tests, etc.)
  - [ ] Run: `pytest tests/unit/test_result_models.py -v`

- [ ] **test_logging.py** (NEW FILE)
  - [ ] Test `create_rich_handler()` returns RichHandler
  - [ ] Test `create_rich_handler()` with level="DEBUG"
  - [ ] Test `create_rich_handler()` with level="ERROR"
  - [ ] Test `setup_rich_logging()` returns logger
  - [ ] Test `setup_rich_logging()` sets correct level
  - [ ] Test logger has Rich handler attached
  - [ ] Run: `pytest tests/unit/test_logging.py -v`

### B. Coverage Verification

- [ ] Run coverage report: `pytest --cov=src/familiar --cov-report=term-missing`
- [ ] Verify coverage of all public functions >= 80%
- [ ] Verify coverage of all public classes >= 80%
- [ ] Identify any gaps and add tests

### C. Remove Obsolete Tests

- [ ] Search for tests of removed functions
- [ ] Remove any tests for:
  - [ ] `create_browser_use_agent()` (if any)
  - [ ] `get_required_env()` (if any)
  - [ ] `get_optional_env()` (if any)
  - [ ] `get_bool_env()` (if any)
  - [ ] `setup_logging()` from setup.py (if any)
  - [ ] `TestRun` class (if any)
  - [ ] `resolved_content` property (if any)

---

## Phase 3: Documentation Validation

### A. README.md Review

- [ ] Verify "Features" section is accurate
- [ ] Verify "Installation" instructions work
- [ ] Verify "Quick Start" example is accurate
- [ ] Verify all CLI commands match actual interface
  - [ ] `familiar run` options
  - [ ] `familiar discover` options
  - [ ] `familiar --version`
- [ ] Verify suite.yaml schema in README matches SuiteConfig model
- [ ] Verify retry_policy options match actual implementation
- [ ] Verify browser_profile options match BrowserProfileConfig model
- [ ] Verify environment variables list is complete
- [ ] Verify LLM provider list is accurate
- [ ] Check model names are current (e.g., "claude-sonnet-4-0", "gpt-4o")
- [ ] Verify fast mode performance claims (or add "approximate" disclaimers)
- [ ] Verify browser timing examples match browser_profile fields

### B. docs/ Directory Review

- [ ] Read `docs/configuration.md`
- [ ] Verify configuration docs match SuiteConfig schema
- [ ] Verify examples in docs are valid
- [ ] Check for any hallucinations or drift
- [ ] Update any inaccuracies found

### C. Examples Validation

- [ ] Validate `examples/basic-login/`
  - [ ] Run `familiar validate examples/basic-login` (if command exists)
  - [ ] Or manually: Parse suite.yaml with SuiteParser
  - [ ] Verify README.md in example is accurate
- [ ] Validate `examples/e-commerce/`
  - [ ] Run `familiar validate examples/e-commerce`
  - [ ] Verify README.md in example is accurate
- [ ] Check `examples/api-testing/`
  - [ ] Verify directory contents (may be empty placeholder)
  - [ ] If empty: Remove or add basic example
  - [ ] If has content: Validate suite
- [ ] Verify examples/README.md explains all examples

### D. Spec Documents

- [ ] Review `docs/images/` - ensure fammy.png exists and is used
- [ ] Check CONTRIBUTING.md for accuracy (if exists)
- [ ] specs/ directory: Keep as-is (historical record)

---

## Phase 4: Code Quality

### A. Constitution Compliance Re-check

- [ ] Verify no methods > 20 lines without justification
  - [ ] `_execute_step_once()` in executor.py (145 lines) - JUSTIFY or REFACTOR
  - [ ] `run_all_suites_async()` in run.py (93 lines) - JUSTIFY or REFACTOR
  - [ ] Others: scan for long methods
- [ ] Verify no classes > 7 public methods
  - [ ] TextFormatter (11 total but only 2-3 public) - VERIFY and DOCUMENT
- [ ] Verify dependency injection is used appropriately
- [ ] Verify single responsibility for all classes

### B. Import Cleanup

- [ ] Run `ruff check src/` to identify issues
- [ ] Run `ruff check src/ --select F401` for unused imports
- [ ] Remove any unused imports found
- [ ] Run `ruff format src/` to format code
- [ ] Commit: "style: clean up imports and formatting"

### C. Type Hints Verification

- [ ] Run `mypy src/familiar` (if configured)
- [ ] Fix any type errors found
- [ ] Ensure all public functions have type hints

---

## Phase 5: Final Validation

### A. Test Suite

- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify all tests pass
- [ ] Verify no new warnings introduced
- [ ] Check test count increased (new tests added)
- [ ] Run coverage: `pytest --cov=src/familiar --cov-report=term --cov-report=html`

### B. Integration Testing

- [ ] Run examples manually (if possible with test server)
  - [ ] Or at minimum, verify they parse: `familiar discover examples/`
- [ ] Test CLI commands:
  - [ ] `familiar --version`
  - [ ] `familiar discover examples/`
  - [ ] `familiar run examples/basic-login` (requires test server, or mock)
- [ ] Test .env loading: verify `.env` file is loaded on startup

### C. Linting

- [ ] Run `ruff check src/` - no errors
- [ ] Run `ruff check tests/` - no errors  
- [ ] Run `mypy src/familiar` - no errors (if mypy is configured)

### D. Git Hygiene

- [ ] Ensure no untracked files in src/ or tests/
- [ ] Ensure no debug print statements left in code
- [ ] Ensure no commented-out code blocks
- [ ] Check for any TODOs added - document or remove

---

## Phase 6: Documentation

### A. Update Spec Documents

- [ ] Mark spec.md as "Complete"
- [ ] Update plan.md with "COMPLETED" status
- [ ] Update research.md if any findings changed during implementation
- [ ] Update data-model.md with actual changes made
- [ ] Create IMPLEMENTATION_SUMMARY.md (see template below)

### B. Code Comments

- [ ] Add/update docstrings for any modified public functions
- [ ] Remove outdated comments
- [ ] Add comments explaining any justified Constitution violations (long methods)

---

## Completion Criteria

ALL items above must be checked off before marking sprint as complete.

**Sign-off**:
- [ ] All dead code removed
- [ ] All tests pass
- [ ] Test coverage >= 80% for public APIs
- [ ] Documentation validated and updated
- [ ] Constitution compliance verified
- [ ] Examples validated
- [ ] No breaking changes introduced
- [ ] Ready for next feature development

---

## IMPLEMENTATION_SUMMARY.md Template

```markdown
# Implementation Summary: Tech Debt Sprint

**Branch**: 006-tech-debt-sprint  
**Status**: ✅ COMPLETE  
**Date**: [completion date]

## Summary

Completed comprehensive technical debt remediation. Removed [X] lines of dead code, added [X] tests, achieved [X]% test coverage, validated all documentation.

## Changes Made

### Dead Code Removed
- Removed X unused functions
- Removed X unused classes
- Removed X unused model fields
- Total lines removed: ~X lines

### Test Coverage Added
- Added X new test files
- Added X new tests
- Coverage increased from X% to X%

### Documentation Updates
- Updated README.md: [changes]
- Updated docs/: [changes]
- Validated examples: [results]

## Metrics

- Lines of code removed: X
- Lines of test code added: X
- Test coverage: X% -> X%
- Tests added: X
- Constitution violations: 0 (or X justified)

## Breaking Changes

NONE

## Next Steps

Ready for new feature development. Codebase is clean, well-tested, and documented.
```

---

**Status**: Draft | **Version**: 1.0 | **Date**: 2025-11-14

