# Tasks: Tech Debt Sprint - Code Quality & Test Coverage

**Input**: Design documents from `/specs/006-tech-debt-sprint/`  
**Prerequisites**: spec.md (required), plan.md (required), research.md, data-model.md, contracts/, quickstart.md  
**Branch**: `006-tech-debt-sprint`  
**Status**: ✅ Ready for implementation

**Organization**: Tasks are grouped by cleanup phase to enable systematic refactoring with continuous validation.

**Tests**: Tests are EXPLICITLY requested in this spec (100% public API coverage is a requirement).

---

## Current Progress

**Status**: ✅ **Phase 1 Complete - Starting Phase 2**

- ✅ **Phase 1 (Dead Code Removal)**: 9/9 complete
- ⏳ **Phase 2 (Test Coverage - Utilities)**: 0/12 complete
- ⏳ **Phase 3 (Test Coverage - Formatters)**: 0/8 complete
- ⏳ **Phase 4 (Test Coverage - Results)**: 0/6 complete
- ⏳ **Phase 5 (Test Coverage - Logging)**: 0/5 complete
- ⏳ **Phase 6 (Documentation Validation)**: 0/9 complete
- ⏳ **Phase 7 (Code Quality & Finalization)**: 0/7 complete

**Total**: 0/56 tasks complete

**Estimated Effort**: 8-12 hours

---

## Implementation Strategy

### MVP Definition
This is a refactoring sprint - ALL phases must be completed for success. However, phases can be implemented sequentially with validation after each.

### Incremental Delivery
1. **First Increment**: Phase 1 (Dead Code Removal) - ~2-3 hours
   - Deliverable: Cleaner codebase, all tests passing
2. **Second Increment**: Phases 2-5 (Test Coverage) - ~4-6 hours
   - Deliverable: 80%+ test coverage, all tests passing
3. **Final Increment**: Phases 6-7 (Docs + Quality) - ~2-3 hours
   - Deliverable: Production-ready codebase

### Success Criteria
- Zero dead code remaining
- Test coverage >= 80% for public APIs
- All documentation accurate
- Constitution compliance verified
- All tests passing

---

## Format: `- [ ] [ID] [P?] Description with file path`

- `[P]` = Parallelizable (can work on simultaneously with other [P] tasks)
- Task IDs are sequential (T001, T002, etc.)
- Run `pytest tests/ -v` after each removal task
- Commit incrementally (don't wait until end)

---

## Phase 1: Dead Code Removal (Setup & Cleanup)

**Goal**: Remove all unused functions, classes, fields, and modules identified in research.md

**Estimated Time**: 2-3 hours

**Independent Test Criteria**:
- [ ] All tests pass after each removal
- [ ] `grep` searches confirm code is unused
- [ ] No imports of removed code remain
- [ ] Test count unchanged (no tests for dead code)

### Tasks

- [X] T001 Verify clean starting state: git status clean, all tests passing
- [X] T002 [P] Remove unused function `get_bool_env()` from src/familiar/utils/env.py (lines 67-82)
- [X] T003 [P] Remove unused function `get_optional_env()` from src/familiar/utils/env.py (lines 54-64)
- [X] T004 [P] Remove unused function `get_required_env()` from src/familiar/utils/env.py (lines 36-51)
- [X] T005 Remove unused field `multiplier` from RetryPolicyConfig in src/familiar/models/suite.py (line 17)
- [X] T006 Remove unused property `resolved_content` from TestStep in src/familiar/models/step.py (lines 37-40)
- [X] T007 Remove unused class `TestRun` from src/familiar/models/result.py (lines 154-190)
- [X] T008 Remove unused function `create_browser_use_agent()` from src/familiar/utils/browser.py (lines 137-177)
- [X] T009 Remove entire unused module src/familiar/logging/setup.py (verify no imports first)

**Validation**:
```bash
# After each task, verify:
grep -r "function_name" src/ tests/  # Should return no results
pytest tests/ -v                      # Should pass
```

**Commit**: After completing all Phase 1 tasks:
```bash
git add -A
git commit -m "refactor: remove dead code

- Remove unused env utility functions (get_required_env, get_optional_env, get_bool_env)
- Remove unused TestRun class (never used for multi-suite runs)
- Remove unused create_browser_use_agent function (replaced in spec 003)
- Remove unused multiplier field from RetryPolicyConfig
- Remove unused resolved_content property from TestStep
- Remove unused logging/setup.py module

~150 lines of dead code removed. All tests passing."
```

---

## Phase 2: Test Coverage - Browser Utilities

**Goal**: Add comprehensive tests for LLM creation and browser utilities

**Estimated Time**: 1.5-2 hours

**Independent Test Criteria**:
- [ ] All LLM provider paths tested
- [ ] Error cases tested (invalid provider, missing API key)
- [ ] Tests can run independently without browser-use API calls (mocked)
- [ ] Coverage for create_llm() reaches 100%

### Tasks

- [ ] T010 Create new test file tests/unit/test_browser.py with TestCreateLLM class
- [ ] T011 [P] Add test_create_llm_anthropic in tests/unit/test_browser.py
- [ ] T012 [P] Add test_create_llm_openai in tests/unit/test_browser.py
- [ ] T013 [P] Add test_create_llm_google in tests/unit/test_browser.py
- [ ] T014 [P] Add test_create_llm_gemini_alias in tests/unit/test_browser.py
- [ ] T015 [P] Add test_create_llm_ollama in tests/unit/test_browser.py
- [ ] T016 [P] Add test_create_llm_browser_use in tests/unit/test_browser.py
- [ ] T017 [P] Add test_create_llm_groq in tests/unit/test_browser.py
- [ ] T018 [P] Add test_create_llm_azure in tests/unit/test_browser.py
- [ ] T019 [P] Add test_create_llm_invalid_provider in tests/unit/test_browser.py
- [ ] T020 [P] Add test_create_llm_missing_anthropic_api_key in tests/unit/test_browser.py
- [ ] T021 [P] Add test_create_llm_missing_openai_api_key in tests/unit/test_browser.py

**Validation**:
```bash
pytest tests/unit/test_browser.py -v
pytest --cov=src/familiar/utils/browser --cov-report=term-missing
```

**Commit**: After completing Phase 2:
```bash
git add tests/unit/test_browser.py
git commit -m "test: add comprehensive tests for LLM creation

- Test all 8 supported LLM providers (anthropic, openai, google, gemini, ollama, browser-use, groq, azure)
- Test error handling for invalid provider
- Test error handling for missing API keys
- Coverage for create_llm() now 100%

Added 12 tests."
```

---

## Phase 3: Test Coverage - Result Formatters

**Goal**: Add tests for JSON and text formatters

**Estimated Time**: 1.5-2 hours

**Independent Test Criteria**:
- [ ] JSONFormatter.format() tested with valid SuiteResult
- [ ] JSONFormatter.format_discovery() tested with suite list
- [ ] JSON output is valid (parseable)
- [ ] Pretty and compact modes tested
- [ ] Coverage for formatters reaches 80%+

### Tasks

- [ ] T022 Create new test file tests/unit/test_formatters.py with TestJSONFormatter class
- [ ] T023 [P] Add test_json_format_suite_result in tests/unit/test_formatters.py
- [ ] T024 [P] Add test_json_format_pretty_true in tests/unit/test_formatters.py
- [ ] T025 [P] Add test_json_format_pretty_false in tests/unit/test_formatters.py
- [ ] T026 [P] Add test_json_format_discovery_with_suites in tests/unit/test_formatters.py
- [ ] T027 [P] Add test_json_format_discovery_empty_list in tests/unit/test_formatters.py
- [ ] T028 [P] Add test_json_output_is_valid_json in tests/unit/test_formatters.py
- [ ] T029 Add test_json_format_with_failed_tests in tests/unit/test_formatters.py

**Note**: TextFormatter tests are optional since it's well-tested via integration tests and uses Rich library (hard to test output format).

**Validation**:
```bash
pytest tests/unit/test_formatters.py -v
pytest --cov=src/familiar/formatters --cov-report=term-missing
```

**Commit**: After completing Phase 3:
```bash
git add tests/unit/test_formatters.py
git commit -m "test: add tests for JSON formatter

- Test format() with sample SuiteResult
- Test format_discovery() with suite list
- Test pretty and compact output modes
- Verify JSON output is valid and parseable
- Test formatting of failed test results

Added 8 tests. Coverage for formatters: 80%+"
```

---

## Phase 4: Test Coverage - Result Models

**Goal**: Test all properties and calculations in result models

**Estimated Time**: 1-1.5 hours

**Independent Test Criteria**:
- [ ] TestResult properties fully tested (success, failed, retry_count)
- [ ] SuiteResult properties fully tested (success, status, success_rate)
- [ ] Fuzziness logic tested (0.0 and >0.0)
- [ ] Edge cases tested (empty results, all failed, etc.)

### Tasks

- [ ] T030 Create new test file tests/unit/test_result_models.py with TestTestResult class
- [ ] T031 [P] Add test_test_result_success_property in tests/unit/test_result_models.py
- [ ] T032 [P] Add test_test_result_failed_property in tests/unit/test_result_models.py
- [ ] T033 [P] Add test_test_result_retry_count_calculation in tests/unit/test_result_models.py
- [ ] T034 Add TestSuiteResult class and test_suite_success_no_fuzziness in tests/unit/test_result_models.py
- [ ] T035 Add test_suite_success_with_fuzziness in tests/unit/test_result_models.py
- [ ] T036 Add test_suite_success_rate_calculation in tests/unit/test_result_models.py

**Validation**:
```bash
pytest tests/unit/test_result_models.py -v
pytest --cov=src/familiar/models/result --cov-report=term-missing
```

**Commit**: After completing Phase 4:
```bash
git add tests/unit/test_result_models.py
git commit -m "test: add tests for result model properties

- Test TestResult properties (success, failed, retry_count)
- Test SuiteResult success calculation with fuzziness
- Test success_rate percentage calculation
- Test edge cases and status logic

Added 6 tests. Coverage for result models improved."
```

---

## Phase 5: Test Coverage - Logging Handlers

**Goal**: Test logging handler creation and setup

**Estimated Time**: 0.5-1 hour

**Independent Test Criteria**:
- [ ] create_rich_handler() tested for different log levels
- [ ] setup_rich_logging() tested for logger configuration
- [ ] Handler attachment verified
- [ ] Coverage for logging module >= 80%

### Tasks

- [ ] T037 Create new test file tests/unit/test_logging.py with TestLoggingHandlers class
- [ ] T038 [P] Add test_create_rich_handler_default in tests/unit/test_logging.py
- [ ] T039 [P] Add test_create_rich_handler_debug_level in tests/unit/test_logging.py
- [ ] T040 [P] Add test_create_rich_handler_error_level in tests/unit/test_logging.py
- [ ] T041 Add test_setup_rich_logging_returns_logger in tests/unit/test_logging.py

**Validation**:
```bash
pytest tests/unit/test_logging.py -v
pytest --cov=src/familiar/logging --cov-report=term-missing
```

**Commit**: After completing Phase 5:
```bash
git add tests/unit/test_logging.py
git commit -m "test: add tests for logging handlers

- Test create_rich_handler() with different log levels
- Test setup_rich_logging() returns configured logger
- Verify handler attachment and configuration
- Coverage for logging module: 80%+

Added 5 tests."
```

---

## Phase 6: Documentation Validation

**Goal**: Verify all documentation accurately reflects implementation

**Estimated Time**: 1-2 hours

**Independent Test Criteria**:
- [ ] All CLI commands in README match actual interface
- [ ] All configuration options in docs match models
- [ ] All examples parse successfully
- [ ] No hallucinations or drift found

### Tasks

- [ ] T042 Verify examples parse: run familiar discover examples/ and check all suites found
- [ ] T043 Manually validate examples/basic-login/suite.yaml with SuiteParser
- [ ] T044 Manually validate examples/e-commerce/suite.yaml with SuiteParser
- [ ] T045 Check examples/api-testing/ directory (may be empty, decide: remove or populate)
- [ ] T046 Review README.md CLI command docs (lines 445-519) match src/familiar/cli/main.py
- [ ] T047 Review README.md suite.yaml schema (lines 361-411) matches src/familiar/models/suite.py
- [ ] T048 Review README.md environment variables (lines 416-429) are complete and accurate
- [ ] T049 Review docs/configuration.md matches SuiteConfig, BrowserProfileConfig, RetryPolicyConfig models
- [ ] T050 Verify README.md LLM provider list (lines 53-61, 144-172) matches browser.py implementation

**Validation**:
```bash
# Verify examples
familiar discover examples/
python -c "from pathlib import Path; from familiar.core.parser import SuiteParser; \
           parser = SuiteParser(); \
           suite = parser.parse_suite(Path('examples/basic-login')); \
           print(f'✓ {suite.name}: {len(suite.steps)} steps')"
```

**Commit**: After completing Phase 6:
```bash
git add README.md docs/ examples/
git commit -m "docs: validate and update documentation

- Verified CLI command docs match actual interface
- Verified suite.yaml schema docs match SuiteConfig model
- Verified environment variable list is complete
- Validated all examples parse successfully
- Fixed [list any issues found]

All documentation now accurate."
```

---

## Phase 7: Code Quality & Finalization

**Goal**: Run linters, verify Constitution compliance, finalize sprint

**Estimated Time**: 1 hour

**Independent Test Criteria**:
- [ ] All linter checks pass (ruff)
- [ ] No unused imports remain
- [ ] Code properly formatted
- [ ] Full test suite passes
- [ ] Test coverage >= 80% for public APIs

### Tasks

- [ ] T051 Run ruff check src/ and fix any issues found
- [ ] T052 Run ruff check src/ --select F401 to find unused imports and remove them
- [ ] T053 Run ruff format src/ tests/ to format all code
- [ ] T054 Run pytest tests/ -v to verify all tests pass
- [ ] T055 Run pytest --cov=src/familiar --cov-report=term --cov-report=html to verify coverage
- [ ] T056 Create specs/006-tech-debt-sprint/IMPLEMENTATION_SUMMARY.md with final metrics
- [ ] T057 Update specs/006-tech-debt-sprint/spec.md status to "Complete"

**Validation**:
```bash
# Full validation
ruff check src/ tests/
pytest tests/ -v
pytest --cov=src/familiar --cov-report=term-missing

# Verify improvements
git diff master --stat  # Should show removals and test additions
```

**Final Commit**: After completing Phase 7:
```bash
git add -A
git commit -m "docs: complete tech debt sprint

Created implementation summary with metrics:
- 150 lines of dead code removed
- 31 tests added (43 → 74 tests)
- Coverage: X% → Y%
- Zero breaking changes
- All documentation validated

Sprint complete. Codebase is clean and ready for new features."
```

---

## Dependencies Between Phases

### Linear Dependencies (Must complete in order)
```
Phase 1 (Dead Code) 
  ↓
Phase 2-5 (Test Coverage) [Can be done in parallel or any order]
  ↓
Phase 6 (Documentation) [Can be done in parallel with Phases 2-5]
  ↓
Phase 7 (Finalization)
```

### Parallel Opportunities

**Phases 2-5 are fully independent**:
- Phase 2 (Browser tests) - tests src/familiar/utils/browser.py
- Phase 3 (Formatter tests) - tests src/familiar/formatters/
- Phase 4 (Result tests) - tests src/familiar/models/result.py
- Phase 5 (Logging tests) - tests src/familiar/logging/

**Phase 6 can be done anytime after Phase 1**:
- Documentation validation doesn't depend on test coverage

**Within each phase, all [P] tasks are parallelizable**.

---

## Test Execution

### Run Individual Phase Tests
```bash
# Phase 2
pytest tests/unit/test_browser.py -v

# Phase 3
pytest tests/unit/test_formatters.py -v

# Phase 4
pytest tests/unit/test_result_models.py -v

# Phase 5
pytest tests/unit/test_logging.py -v
```

### Run All New Tests
```bash
pytest tests/unit/test_browser.py \
       tests/unit/test_formatters.py \
       tests/unit/test_result_models.py \
       tests/unit/test_logging.py -v
```

### Run Full Test Suite
```bash
pytest tests/ -v
```

### Coverage Report
```bash
pytest --cov=src/familiar \
       --cov-report=term-missing \
       --cov-report=html
```

---

## Rollback Strategy

If any phase introduces issues:

```bash
# Rollback specific commit
git log --oneline  # Find commit hash
git revert <commit-hash>

# Or rollback to before sprint
git checkout master

# Or reset to specific phase
git reset --hard <commit-hash>
```

**Prevention**: Run `pytest tests/ -v` after EVERY task to catch issues immediately.

---

## Success Metrics

### Before Sprint
- Lines of code: ~2,500
- Test count: 43
- Test coverage: ~60-70% (estimated)
- Dead code: ~150 lines identified

### After Sprint (Target)
- Lines of code: ~2,350 (150 removed)
- Test count: 74+ (31 added)
- Test coverage: >= 80%
- Dead code: 0 lines

### Quality Metrics
- Constitution violations: 0 (or justified)
- Unused imports: 0
- Documentation drift: 0
- Breaking changes: 0

---

## Notes

1. **Run tests frequently**: After EVERY removal in Phase 1, after EVERY test file in Phases 2-5
2. **Commit incrementally**: Don't wait until end of phase
3. **Use grep liberally**: Verify code is unused before removing
4. **Keep quickstart.md open**: Reference for code examples and commands
5. **Mark progress**: Update "Current Progress" section as you complete phases

---

## Completion Checklist

Before marking sprint complete:

- [ ] All 56 tasks completed
- [ ] Full test suite passes (pytest tests/ -v)
- [ ] Test coverage >= 80% (pytest --cov)
- [ ] All documentation validated
- [ ] Examples parse successfully
- [ ] No unused imports (ruff)
- [ ] Code formatted (ruff format)
- [ ] Constitution compliance verified
- [ ] IMPLEMENTATION_SUMMARY.md created
- [ ] Zero breaking changes confirmed

---

**Status**: Ready for implementation | **Date**: 2025-11-14  
**Next Step**: Begin Phase 1 - Dead Code Removal

**Estimated Timeline**:
- **Day 1** (4-6 hours): Phases 1-2
- **Day 2** (4-6 hours): Phases 3-6
- **Day 3** (1 hour): Phase 7 finalization

Or complete in one intensive 8-12 hour session.

---

**Good luck! The codebase will be significantly cleaner after this sprint.** 🚀

