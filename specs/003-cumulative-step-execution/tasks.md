# Tasks: Cumulative Step Execution & Session Persistence

**Input**: Design documents from `/specs/003-cumulative-step-execution/`  
**Prerequisites**: plan.md, spec.md, research.md

**Type**: Enhancement (Critical Priority)  
**Scope**: Implement explicit step ordering with numeric prefixes and browser session persistence across steps

**Organization**: Tasks are organized by implementation phase. This is an architectural enhancement affecting core execution logic.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Single project structure**: `src/familiar/`, `tests/` at repository root
- Primary modifications: `src/familiar/core/discovery.py`, `parser.py`, `executor.py`, `runner.py`
- Test updates: `tests/unit/`, `tests/integration/`
- Example updates: `examples/`, `tests/fixtures/`

---

## Phase 1: Pre-Implementation Analysis

**Purpose**: Understand current implementation and establish baseline

- [X] T001 Read and understand current discovery.py implementation in src/familiar/core/discovery.py
- [X] T002 Read and understand current parser.py implementation in src/familiar/core/parser.py
- [X] T003 Read and understand current executor.py browser creation in src/familiar/core/executor.py
- [X] T004 Read and understand current runner.py suite execution in src/familiar/core/runner.py
- [X] T005 Document current step discovery and ordering behavior
- [X] T006 Document current browser session lifecycle
- [X] T007 Run existing test suite to establish baseline in tests/

**Checkpoint**: Current behavior documented - ready for implementation ✅

**Findings:**
- parser.py already uses `[0-9][0-9]-*.md` glob pattern (partially correct)
- No skipped file detection or logging
- executor.py creates new browser agent per step (needs fix)
- runner.py doesn't manage browser session lifecycle

---

## Phase 2: Step Ordering & Filtering (FR1, FR2, FR3)

**Purpose**: Implement explicit step file ordering based on numeric prefixes with automatic skipping

### Step Pattern Detection (FR1)

- [X] T008 Add STEP_PATTERN regex constant `^\d\d-.+\.md$` in src/familiar/core/parser.py (implemented in parser not discovery)
- [X] T009 Implement is_numbered_step() predicate function via _categorize_step_files() in src/familiar/core/parser.py
- [X] T010 Update discover_suites() to filter numbered vs non-numbered files in src/familiar/core/parser.py
- [X] T011 Implement step sorting by numeric prefix in src/familiar/core/parser.py
- [X] T012 Return both runnable steps and skipped files from discovery in src/familiar/core/parser.py

### Prefix Validation (FR3)

- [X] T013 Implement validate_step_prefixes() function in src/familiar/core/parser.py
- [X] T014 Add duplicate prefix detection logic in src/familiar/core/parser.py
- [X] T015 Create clear error messages for duplicate prefixes in src/familiar/core/parser.py
- [X] T016 Add validation for no numbered steps found in src/familiar/core/parser.py
- [X] T017 Integrate prefix validation into parse_suite() in src/familiar/core/parser.py

### Skip File Logging (FR2)

- [ ] T018 Add log_skipped_files() function in src/familiar/logging/setup.py or handlers.py
- [ ] T019 Implement verbose mode check for skip logging
- [ ] T020 Format skip log messages: "[INFO] Skipped file (no numeric prefix): {filename}"
- [ ] T021 Sort skipped files alphabetically before logging
- [ ] T022 Integrate skip logging into runner after step execution

**Checkpoint**: Step ordering and filtering complete - ready for session persistence

---

## Phase 3: Browser Session Persistence (FR4, FR5, FR6)

**Purpose**: Change browser session management so each scenario uses one persistent session across all steps

### Runner Refactoring (FR4, FR6)

- [X] T023 Modify run_suite() to create Browser instance before step loop in src/familiar/core/runner.py
- [X] T024 Move LLM creation to suite level (before steps) in src/familiar/core/runner.py
- [X] T025 Add try/finally block for browser cleanup in src/familiar/core/runner.py
- [X] T026 Pass browser and llm to executor.execute_step() in src/familiar/core/runner.py
- [X] T027 Ensure browser.close() is called in finally block in src/familiar/core/runner.py
- [X] T028 Add error handling for browser initialization failures (implicit via try/finally) in src/familiar/core/runner.py

### Executor Refactoring (FR5)

- [X] T029 Update execute_step() signature to receive browser parameter in src/familiar/core/executor.py
- [X] T030 Update execute_step() signature to receive llm parameter in src/familiar/core/executor.py
- [X] T031 Remove create_browser_use_agent() call from _execute_step_once() in src/familiar/core/executor.py
- [X] T032 Create Agent with provided browser and llm instances in src/familiar/core/executor.py
- [X] T033 Update StepExecutor.__init__() to remove headless and temperature (now at suite level) in src/familiar/core/executor.py
- [X] T034 Verify browser stays open after agent.run() completes (implicit in new architecture) in src/familiar/core/executor.py
- [X] T035 Update retry logic to reuse same browser across attempts (browser passed to _execute_step_once) in src/familiar/core/executor.py

### Session State Preservation

- [ ] T036 Add logging for browser session lifecycle (create/reuse/close)
- [ ] T037 Verify cookies persist across steps (integration test scenario)
- [ ] T038 Verify navigation history persists across steps (integration test scenario)
- [ ] T039 Verify local/session storage persists across steps (integration test scenario)

**Checkpoint**: Browser session persistence complete - ready for testing

---

## Phase 4: Testing & Validation

**Purpose**: Verify new behavior with comprehensive tests

### Unit Tests - Step Ordering

- [ ] T040 [P] Write test for is_numbered_step() with valid patterns in tests/unit/test_discovery.py
- [ ] T041 [P] Write test for is_numbered_step() with invalid patterns in tests/unit/test_discovery.py
- [ ] T042 [P] Write test for step sorting with gaps in numbering in tests/unit/test_discovery.py
- [ ] T043 [P] Write test for step sorting with out-of-order files in tests/unit/test_discovery.py
- [ ] T044 [P] Write test for skipped file categorization in tests/unit/test_discovery.py

### Unit Tests - Prefix Validation

- [ ] T045 [P] Write test for duplicate prefix detection in tests/unit/test_parser.py
- [ ] T046 [P] Write test for no numbered steps error in tests/unit/test_parser.py
- [ ] T047 [P] Write test for valid prefix validation in tests/unit/test_parser.py
- [ ] T048 [P] Write test for prefix validation error messages in tests/unit/test_parser.py

### Unit Tests - Session Persistence

- [ ] T049 [P] Write test for executor receiving browser parameter in tests/unit/test_executor.py (new file)
- [ ] T050 [P] Write test for browser reuse across execute_step() calls in tests/unit/test_executor.py
- [ ] T051 [P] Write test for Agent creation with provided browser in tests/unit/test_executor.py

### Integration Tests - Cumulative Execution

- [ ] T052 Create test scenario with 3 numbered steps in tests/fixtures/cumulative-test/
- [ ] T053 Write integration test for step execution order in tests/integration/test_runner.py
- [ ] T054 Write integration test for browser state persistence in tests/integration/test_runner.py
- [ ] T055 Write integration test for skipped file logging in tests/integration/test_runner.py
- [ ] T056 Write integration test for scenario isolation (multiple suites) in tests/integration/test_runner.py

### Test Suite Execution

- [ ] T057 Run unit tests to verify step ordering logic: pytest tests/unit/test_discovery.py -v
- [ ] T058 Run unit tests to verify prefix validation: pytest tests/unit/test_parser.py -v
- [ ] T059 Run unit tests to verify session persistence: pytest tests/unit/test_executor.py -v
- [ ] T060 Run integration tests to verify cumulative execution: pytest tests/integration/test_runner.py -v
- [ ] T061 Run full test suite to verify no regressions: pytest tests/ -v

**Checkpoint**: All tests passing - implementation validated

---

## Phase 5: Example Updates & Migration

**Purpose**: Update existing examples and test fixtures with numeric prefixes

### Test Fixtures

- [X] T062 Rename tests/fixtures/sample-suite/00-login.md (already correctly named)
- [X] T063 Rename tests/fixtures/sample-suite/01-dashboard.md (already correctly named)
- [X] T064 Update tests/fixtures/sample-suite/suite.yaml if needed (no changes needed)
- [X] T065 Add README.md to sample-suite as example of skipped file (optional)

### Example Scenarios - Basic Login

- [X] T066 [P] Rename examples/basic-login/00-navigate.md (already correctly named)
- [X] T067 [P] Rename examples/basic-login/01-enter-credentials.md (already correctly named)
- [X] T068 [P] Rename examples/basic-login/02-submit-login.md (already correctly named)
- [X] T069 [P] Rename examples/basic-login/03-verify-logged-in.md (already correctly named)
- [ ] T070 [P] Update examples/basic-login/README.md to explain new naming convention

### Example Scenarios - E-Commerce

- [X] T071 [P] Rename examples/e-commerce/00-homepage.md (already correctly named)
- [X] T072 [P] Rename examples/e-commerce/01-search-product.md (already correctly named)
- [X] T073 [P] Rename examples/e-commerce/02-select-product.md (already correctly named)
- [X] T074 [P] Rename examples/e-commerce/03-add-to-cart.md (already correctly named)
- [X] T075 [P] Rename examples/e-commerce/04-view-cart.md (already correctly named)
- [X] T076 [P] Rename examples/e-commerce/05-begin-checkout.md (already correctly named)
- [X] T077 [P] Rename examples/e-commerce/06-verify-checkout-form.md (already correctly named)
- [ ] T078 [P] Update examples/e-commerce/README.md to explain new naming convention

**Checkpoint**: All examples already have correct numeric prefixes ✅

---

## Phase 6: Documentation & Polish

**Purpose**: Update documentation and ensure user-facing clarity

### Documentation Updates

- [X] T079 [P] Update README.md section on step file naming conventions
- [X] T080 [P] Add explanation of numeric prefix pattern (00-, 01-, 02-)
- [X] T081 [P] Document file skipping behavior in README.md
- [ ] T082 [P] Add migration guide for existing users to rename files (optional)
- [X] T083 [P] Update quickstart examples with numbered step files
- [ ] T084 [P] Add FAQ entry about why files are skipped (optional)

### Error Message Polish

- [ ] T085 Review duplicate prefix error messages for clarity in src/familiar/core/parser.py
- [ ] T086 Review no numbered steps error messages for clarity in src/familiar/core/parser.py
- [ ] T087 Add helpful suggestions in error messages (e.g., "Rename login.md to 00-login.md")
- [ ] T088 Verify verbose skip logging messages are clear and actionable

### Logging Enhancements

- [ ] T089 Add DEBUG level logs for browser session lifecycle
- [ ] T090 Add INFO level logs for step execution with step numbers (1/3, 2/3, 3/3)
- [ ] T091 Ensure error logs clearly indicate which step failed
- [ ] T092 Add timing logs for session creation vs. reuse performance comparison

**Checkpoint**: Documentation and polish complete

---

## Phase 7: Final Validation & Acceptance Criteria

**Purpose**: Verify all acceptance criteria from spec.md are met

### Acceptance Criteria Verification

- [ ] T093 ✅ Verify step files with numeric prefixes (00-*, 01-*, etc.) execute in sorted order
- [ ] T094 ✅ Verify step files without numeric prefixes are skipped
- [ ] T095 ✅ Verify verbose mode logs all skipped files with clear message
- [ ] T096 ✅ Verify duplicate numeric prefixes cause immediate failure with clear error
- [ ] T097 ✅ Verify browser session created once per scenario, before first step
- [ ] T098 ✅ Verify all steps in a scenario use the same browser instance
- [ ] T099 ✅ Verify browser state (cookies, storage, navigation) persists across steps
- [ ] T100 ✅ Verify browser closes after scenario completes (success or failure)
- [ ] T101 ✅ Verify multiple scenarios get independent browser sessions
- [ ] T102 ✅ Verify existing tests updated to use numeric prefixes
- [ ] T103 ✅ Verify documentation updated with step file naming conventions

### End-to-End Validation

- [ ] T104 Run discover command to verify step ordering display is correct
- [ ] T105 Run test scenario with numbered steps and verify execution order
- [ ] T106 Run test scenario with mixed files and verify skipping behavior
- [ ] T107 Run verbose mode and verify skip logging appears correctly
- [ ] T108 Run scenario with login → navigate → action sequence to verify state persistence
- [ ] T109 Run multiple scenarios and verify session isolation
- [ ] T110 Test error handling when scenario has only non-numbered files

### Performance & Behavior Validation

- [ ] T111 Compare test execution time before/after (expect improvement from session reuse)
- [ ] T112 Verify no memory leaks from browser session persistence
- [ ] T113 Verify error handling doesn't leave browser processes hanging
- [ ] T114 Test with both --headed and --headless modes
- [ ] T115 Verify browser state cleanup between scenarios

**Checkpoint**: All acceptance criteria met - ready for merge

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Pre-Implementation)**: No dependencies - can start immediately
- **Phase 2 (Step Ordering)**: Depends on Phase 1 completion - Must understand current code first
- **Phase 3 (Session Persistence)**: Can start after Phase 1, parallel with Phase 2
- **Phase 4 (Testing)**: Depends on Phases 2 and 3 completion - Must have implementation to test
- **Phase 5 (Example Updates)**: Depends on Phase 2 completion - Need ordering logic working
- **Phase 6 (Documentation)**: Can start after Phase 4 - Need verified behavior to document
- **Phase 7 (Final Validation)**: Depends on all previous phases - Final checklist

### Task Dependencies Within Phases

**Phase 2 (Step Ordering)**:
- T008-T012 (Pattern Detection): Must complete sequentially in discovery.py
- T013-T017 (Prefix Validation): Must complete sequentially in parser.py
- T018-T022 (Skip Logging): Can start after T012 (need skipped files list)

**Phase 3 (Session Persistence)**:
- T023-T028 (Runner): Must complete before executor changes
- T029-T035 (Executor): Depends on T023-T028 (runner must pass browser)
- T036-T039 (Validation): Depends on all previous in Phase 3

**Phase 4 (Testing)**:
- T040-T048 (Unit Tests): All marked [P], can run in parallel
- T049-T051 (Executor Tests): Can run in parallel after Phase 3
- T052-T056 (Integration Tests): Must run after implementation complete
- T057-T061 (Test Execution): Must run sequentially to verify all tests

**Phase 5 (Example Updates)**:
- All rename tasks marked [P] - can run in parallel
- README updates depend on corresponding renames

**Phase 6 (Documentation)**:
- All documentation tasks marked [P] - can run in parallel
- All depend on Phase 4 completion (need verified behavior)

**Phase 7 (Final Validation)**:
- Must run sequentially as checklist
- Each criterion verified independently

### Parallel Opportunities

**Phase 1**: T001-T004 can read files in parallel

**Phase 2**:
- T013-T017 (validation) can proceed in parallel with T018-T022 (logging)

**Phase 3**:
- T036-T039 (validation tasks) can run in parallel once implementation done

**Phase 4**:
- T040-T051 (all unit tests) can run in parallel
- T066-T070 and T071-T078 (example updates) can run in parallel

**Phase 5**: Almost all tasks marked [P] - highly parallelizable

**Phase 6**: All documentation tasks marked [P] - can run in parallel

---

## Parallel Example: Step Ordering Implementation

```bash
# Sequential: Core logic first
Task T008: "Add STEP_PATTERN regex" in discovery.py
Task T009: "Implement is_numbered_step()" in discovery.py
Task T010: "Update discover_suites()" in discovery.py

# Parallel: Validation and logging
Task T013: "Implement validate_step_prefixes()" in parser.py [parallel with T018]
Task T018: "Add log_skipped_files()" in logging/ [parallel with T013]
```

---

## Parallel Example: Testing Phase

```bash
# All unit tests can run in parallel (different test files)
Task T040: "Test is_numbered_step() valid" [P]
Task T041: "Test is_numbered_step() invalid" [P]
Task T045: "Test duplicate prefix detection" [P]
Task T049: "Test executor browser parameter" [P]

# Example updates can run in parallel (different directories)
Task T066: "Rename 00-navigate.md" [P]
Task T071: "Rename e-commerce 00-homepage.md" [P]
```

---

## Implementation Strategy

### MVP Scope (Minimum Viable Implementation)

Focus on **Phases 1-3** for core functionality:

1. **Phase 1**: Understand current implementation (~30 min)
2. **Phase 2**: Step ordering & filtering (~2-3 hours)
   - Regex pattern matching
   - File categorization
   - Skip logging
3. **Phase 3**: Browser session persistence (~3-4 hours)
   - Runner refactoring
   - Executor signature changes
   - Session lifecycle management
4. **Phase 4**: Basic testing (~2-3 hours)
   - Unit tests for ordering
   - Integration test for session persistence

**Total MVP Time**: ~8-10 hours

### Full Implementation (Including Polish)

Add **Phases 5-7** for production readiness:

5. **Phase 5**: Example updates (~1-2 hours)
6. **Phase 6**: Documentation & polish (~2-3 hours)
7. **Phase 7**: Final validation (~1-2 hours)

**Total Full Time**: ~12-17 hours

### Incremental Delivery Strategy

1. **Milestone 1**: Step ordering working (Phase 1-2)
   - Can test that numbered files run in sequence
   - Skip logging works in verbose mode
   
2. **Milestone 2**: Session persistence working (Phase 3)
   - Browser stays open across steps
   - State persists (cookies, storage)
   
3. **Milestone 3**: Fully tested (Phase 4)
   - All unit and integration tests pass
   - Behavior validated
   
4. **Milestone 4**: Production ready (Phases 5-7)
   - Examples updated
   - Documentation complete
   - User migration path clear

### Sequential Workflow (Single Developer)

1. Complete Phase 1 → Understand current implementation
2. Complete Phase 2 → Step ordering working
3. Complete Phase 3 → Session persistence working
4. Complete Phase 4 → Tests passing
5. Complete Phase 5 → Examples updated
6. Complete Phase 6 → Documentation complete
7. Complete Phase 7 → Final validation
8. **STOP and REVIEW**: Enhancement complete, ready for PR

### Parallel Team Strategy

With 2-3 developers:

**After Phase 1 complete**:
- Developer A: Phase 2 (Step Ordering)
- Developer B: Phase 3 (Session Persistence)

**After Phases 2-3 complete**:
- Developer A: Phase 4 (Testing)
- Developer B: Phase 5 (Examples)
- Developer C: Phase 6 (Documentation)

**Finally**: All join for Phase 7 (Validation)

---

## Notes

- [P] tasks = different files or independent concerns, can run in parallel
- Phase 2 and 3 are the core implementation - most complex work
- Phase 4 is critical - must validate behavior thoroughly
- Phase 5 is time-consuming but straightforward (many file renames)
- Phase 6 improves user experience significantly
- Phase 7 is final safety check before merge
- This is an architectural enhancement, not a feature with user stories
- Focus on functional requirements FR1-FR6 from spec.md
- Maintain backward compatibility where possible
- Provide clear migration path for existing scenarios

## Success Criteria

### Must Have
- ✅ Steps with numeric prefixes run in sorted order
- ✅ Non-numbered files are skipped with verbose logging
- ✅ Browser session persists across all steps in scenario
- ✅ Browser state (cookies, storage) carries forward
- ✅ Scenarios are isolated with independent sessions
- ✅ All tests pass
- ✅ No performance regression

### Nice to Have
- ✅ All examples updated with numeric prefixes
- ✅ Comprehensive documentation
- ✅ Clear migration guide for users
- ✅ Helpful error messages
- ✅ Performance improvement from session reuse

### Quality Gates
- ✅ Constitutional alignment maintained
- ✅ No breaking changes to CLI interface
- ✅ Clean error messages guide users
- ✅ Code is well-tested and maintainable
- ✅ Documentation is clear and complete

