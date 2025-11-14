# Tasks: Fast Mode & Browser Performance Configuration

**Input**: Design documents from `/specs/004-fast-mode-performance/`  
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, contracts/

**Type**: Performance Enhancement  
**Scope**: Add --fast CLI flag and browser_profile configuration for speed optimization

**Organization**: Tasks are organized by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project structure**: `src/familiar/`, `tests/` at repository root
- Primary modifications: `src/familiar/cli/`, `src/familiar/models/`, `src/familiar/core/`
- Test updates: `tests/unit/`, `tests/integration/`
- Documentation: `README.md`, `examples/`

---

## Phase 1: Setup & Pre-Implementation Analysis

**Purpose**: Understand current implementation and establish baseline

- [X] T001 Read current SuiteRunner implementation in src/familiar/core/runner.py
- [X] T002 Read current CLI interface in src/familiar/cli/main.py and src/familiar/cli/run.py
- [X] T003 Read current SuiteConfig model in src/familiar/models/suite.py
- [X] T004 Document current Agent creation flow (browser, llm, parameters)
- [X] T005 Run existing test suite to establish baseline: pytest tests/ -v
- [X] T006 Measure baseline execution time for sample test (3-step login flow)
- [X] T007 Document current browser-use Browser and Agent instantiation patterns

**Checkpoint**: Current implementation documented - ready for model layer ✅

**Findings**:
- SuiteRunner: headless parameter, Browser created with keep_alive=True
- CLI: --headless/--headed flag, no --fast flag yet
- SuiteConfig: Pydantic model, no browser_profile field yet
- Agent creation: Browser and LLM passed to executor.execute_step()

---

## Phase 2: Model Layer (Foundational)

**Purpose**: Implement BrowserProfileConfig model - required by all user stories

**Blocking**: All user stories depend on this model

- [X] T008 Create BrowserProfileConfig class in src/familiar/models/suite.py
- [X] T009 Add minimum_wait_page_load_time field with validation (ge=0.0, le=30.0)
- [X] T010 Add wait_between_actions field with validation (ge=0.0, le=30.0)
- [X] T011 Add headless boolean field with default=True
- [X] T012 Implement validate_timing() field validator for timing fields
- [X] T013 Implement to_browser_profile() method to convert to browser-use BrowserProfile
- [X] T014 Add browser_profile: Optional[BrowserProfileConfig] field to SuiteConfig
- [X] T015 Add get_browser_profile() helper method to SuiteConfig
- [X] T016 [P] Write unit test for BrowserProfileConfig defaults in tests/unit/test_models.py
- [X] T017 [P] Write unit test for BrowserProfileConfig custom values in tests/unit/test_models.py
- [X] T018 [P] Write unit test for negative timing validation in tests/unit/test_models.py
- [X] T019 [P] Write unit test for excessive timing validation in tests/unit/test_models.py
- [X] T020 [P] Write unit test for to_browser_profile() conversion in tests/unit/test_models.py
- [X] T021 [P] Write unit test for SuiteConfig with missing browser_profile in tests/unit/test_models.py
- [X] T022 [P] Write unit test for SuiteConfig with browser_profile in tests/unit/test_models.py
- [X] T023 Run unit tests for models: pytest tests/unit/test_models.py -v -k browser_profile

**Checkpoint**: BrowserProfileConfig model complete and tested - ready for user stories ✅

**Test Results**: 66 unit tests passing (7 new browser_profile tests)

---

## Phase 3: User Story 1 - Development Testing

**User Story**: As a developer iterating on test scenarios, I want to run tests quickly with --fast flag

**Goal**: Enable --fast CLI flag that activates LLM flash mode and speed optimization prompt

**Independent Test Criteria**:
- [ ] Can run `familiar run suite --fast` without errors
- [ ] Fast mode enables flash_mode=True on Agent
- [ ] Fast mode injects SPEED_OPTIMIZATION_PROMPT
- [ ] Fast mode execution is faster than standard mode

### CLI Layer

- [X] T024 [US1] Add --fast boolean flag to run command in src/familiar/cli/main.py
- [X] T025 [US1] Update run() function signature to accept fast parameter in src/familiar/cli/main.py
- [X] T026 [US1] Pass fast_mode=fast to SuiteRunner constructor in src/familiar/cli/run.py
- [X] T027 [US1] Update help text for --fast flag with clear description

### Runner Layer

- [X] T028 [US1] Add fast_mode parameter to SuiteRunner.__init__() in src/familiar/core/runner.py
- [X] T029 [US1] Define SPEED_OPTIMIZATION_PROMPT constant at module level in src/familiar/core/runner.py
- [X] T030 [US1] Update run_suite() to conditionally add flash_mode to agent_kwargs when fast_mode=True
- [X] T031 [US1] Update run_suite() to conditionally add extend_system_message when fast_mode=True
- [X] T032 [US1] Ensure agent_kwargs defaults work for non-fast mode (flash_mode not set)

**Phase 3 also includes Browser Profile integration** (from US2):
- [X] T043 [US2] Get browser_profile from suite.config in src/familiar/core/runner.py
- [X] T044 [US2] Create BrowserProfile instance using to_browser_profile()
- [X] T045 [US2] Pass BrowserProfile to Browser constructor
- [X] T046 [US2] CLI headless flag overrides suite browser_profile.headless
- [X] T047 [US2] Handle missing browser_profile gracefully (use defaults)

### Testing

- [ ] T033 [P] [US1] Write unit test for CLI --fast flag acceptance in tests/unit/test_cli.py
- [ ] T034 [P] [US1] Write unit test for fast_mode passed to SuiteRunner in tests/unit/test_cli.py
- [ ] T035 [P] [US1] Write integration test for fast mode execution in tests/integration/test_runner.py
- [ ] T036 [P] [US1] Write integration test for flash_mode enabled in tests/integration/test_runner.py
- [ ] T037 [P] [US1] Write integration test for speed prompt injection in tests/integration/test_runner.py
- [ ] T038 [US1] Run tests for US1: pytest tests/ -v -k "fast"

### Validation

- [ ] T039 [US1] Run sample 3-step test with --fast flag and measure execution time
- [ ] T040 [US1] Verify fast mode is 30%+ faster than baseline
- [ ] T041 [US1] Test --fast combined with --verbose to verify logging
- [ ] T042 [US1] Test --fast combined with --no-headless to verify compatibility

**Checkpoint**: User Story 1 complete - --fast flag functional and tested

---

## Phase 4: User Story 2 - CI/CD for Stable Apps

**User Story**: As a DevOps engineer with a fast, reliable application, I want to configure shorter browser wait times in suite.yaml

**Goal**: Support browser_profile configuration in suite.yaml for persistent timing optimization

**Independent Test Criteria**:
- [ ] Can define browser_profile in suite.yaml
- [ ] Suite uses custom timing values from config
- [ ] Missing browser_profile uses defaults
- [ ] CLI --no-headless overrides suite headless setting

### Runner Integration

- [ ] T043 [US2] Update run_suite() to extract browser_profile from suite.config in src/familiar/core/runner.py
- [ ] T044 [US2] Create BrowserProfile instance from browser_profile config using to_browser_profile()
- [ ] T045 [US2] Pass BrowserProfile to Browser constructor via browser_profile parameter
- [ ] T046 [US2] Ensure CLI headless flag overrides suite browser_profile.headless setting
- [ ] T047 [US2] Handle missing browser_profile gracefully (use defaults)

### YAML Examples

- [ ] T048 [P] [US2] Create fast-mode test fixture in tests/fixtures/fast-mode-suite/
- [ ] T049 [P] [US2] Create suite.yaml with browser_profile configuration in tests/fixtures/fast-mode-suite/
- [ ] T050 [P] [US2] Create simple test step file in tests/fixtures/fast-mode-suite/00-test.md
- [ ] T051 [P] [US2] Create example fast suite in examples/fast-login/suite.yaml
- [ ] T052 [P] [US2] Copy login steps to examples/fast-login/ directory

### Testing

- [ ] T053 [P] [US2] Write test for suite with browser_profile parsing in tests/integration/test_runner.py
- [ ] T054 [P] [US2] Write test for suite without browser_profile (defaults) in tests/integration/test_runner.py
- [ ] T055 [P] [US2] Write test for CLI --no-headless override in tests/integration/test_cli.py
- [ ] T056 [P] [US2] Write test for BrowserProfile creation in tests/unit/test_runner.py
- [ ] T057 [US2] Run tests for US2: pytest tests/ -v -k "browser_profile"

### Validation

- [ ] T058 [US2] Run test with custom browser_profile (0.2s waits) and measure execution time
- [ ] T059 [US2] Verify custom timing is faster than default timing
- [ ] T060 [US2] Test suite with browser_profile headless:false, then run with --no-headless
- [ ] T061 [US2] Verify existing suites without browser_profile still work

**Checkpoint**: User Story 2 complete - browser_profile configuration functional

---

## Phase 5: User Story 3 - Fast LLM Providers Integration

**User Story**: As a user with access to fast LLM providers (Groq, Gemini Flash), I want fast mode to optimize for speed

**Goal**: Validate that fast mode + browser_profile work together for maximum performance

**Independent Test Criteria**:
- [ ] Can combine --fast flag with browser_profile configuration
- [ ] Combined optimization achieves 2-3x speedup
- [ ] Works with different LLM providers
- [ ] Maintains reliability for simple scenarios

### Integration Testing

- [ ] T062 [P] [US3] Write test for combined --fast + browser_profile in tests/integration/test_runner.py
- [ ] T063 [P] [US3] Write test for fast mode with default browser timing
- [ ] T064 [P] [US3] Write test for standard mode with custom browser timing
- [ ] T065 [US3] Run integration tests: pytest tests/integration/ -v

### Performance Validation

- [ ] T066 [US3] Create performance benchmark test scenario (3-5 steps)
- [ ] T067 [US3] Measure baseline (no --fast, no browser_profile): ~25-30s expected
- [ ] T068 [US3] Measure --fast only: ~15-18s expected (40% speedup)
- [ ] T069 [US3] Measure browser_profile only (0.2s): ~18-22s expected (30% speedup)
- [ ] T070 [US3] Measure --fast + browser_profile (0.1s): ~10-15s expected (50-60% speedup)
- [ ] T071 [US3] Document performance results in PERFORMANCE_RESULTS.md

### Cross-Provider Testing

- [ ] T072 [P] [US3] Test fast mode with Anthropic provider (if available)
- [ ] T073 [P] [US3] Test fast mode with OpenAI provider (if available)
- [ ] T074 [P] [US3] Test fast mode with Groq provider for maximum speed (if available)
- [ ] T075 [US3] Document provider-specific performance characteristics

**Checkpoint**: User Story 3 complete - Full fast mode validated across providers

---

## Phase 6: Documentation & Polish

**Purpose**: Update documentation and ensure user-facing clarity

### README.md Updates

- [X] T076 [P] Add "Performance Optimization" section to README.md
- [X] T077 [P] Document --fast flag usage with examples in README.md
- [X] T078 [P] Document browser_profile configuration with examples in README.md
- [X] T079 [P] Add performance comparison table (standard vs fast modes) in README.md
- [X] T080 [P] Document recommended LLM providers for fast mode in README.md
- [X] T081 [P] Add warning about speed/reliability tradeoff in README.md
- [X] T082 [P] Add troubleshooting section for fast mode issues in README.md

### Example Updates

- [X] T083 [P] Update examples/basic-login/README.md with fast mode instructions (added commented browser_profile)
- [X] T084 [P] Update examples/e-commerce/README.md with performance tips (added active browser_profile)
- [ ] T085 [P] Create examples/fast-login/ directory with optimized suite (skipped - examples updated instead)
- [ ] T086 [P] Add README.md to examples/fast-login/ explaining optimizations (skipped - examples updated instead)

### Configuration Documentation

- [ ] T087 [P] Update suite.yaml schema documentation with browser_profile
- [ ] T088 [P] Add browser_profile examples to specs/001-ai-e2e-testing/contracts/suite-schema.yaml
- [ ] T089 [P] Document all browser_profile fields with defaults and ranges

### Help & CLI Documentation

- [ ] T090 Review CLI help text for clarity: familiar run --help
- [ ] T091 Ensure --fast flag is properly documented in help output
- [ ] T092 Add examples to CLI help for common use cases

**Checkpoint**: Documentation complete and user-friendly

---

## Phase 7: Final Validation & Acceptance Criteria

**Purpose**: Verify all acceptance criteria from spec.md are met

### Acceptance Criteria Verification

- [ ] T093 ✅ AC1.1: `familiar run suite --fast` executes with flash_mode enabled
- [ ] T094 ✅ AC1.2: `familiar run suite --fast --verbose` shows speed optimization prompt in logs
- [ ] T095 ✅ AC1.3: `familiar run suite --all --fast` applies fast mode to all suites
- [ ] T096 ✅ AC1.4: Fast mode reduces execution time by ≥30% on sample test

- [ ] T097 ✅ AC2.1: Suite with browser_profile section uses configured values
- [ ] T098 ✅ AC2.2: Suite without browser_profile uses default values (1.0s waits)
- [ ] T099 ✅ AC2.3: CLI --no-headless overrides suite headless:true setting
- [ ] T100 ✅ AC2.4: Invalid browser_profile values raise clear validation errors

- [ ] T101 ✅ AC3.1: Fast mode injects speed optimization system prompt
- [ ] T102 ✅ AC3.2: Fast mode enables flash_mode on Agent
- [ ] T103 ✅ AC3.3: Non-fast mode does NOT inject prompt or enable flash_mode
- [ ] T104 ✅ AC3.4: Speed prompt is appended (does not replace core instructions)

- [ ] T105 ✅ AC4.1: Existing tests without --fast flag run unchanged
- [ ] T106 ✅ AC4.2: Existing suite.yaml files without browser_profile work unchanged
- [ ] T107 ✅ AC4.3: Test suite execution time matches baseline for non-fast mode

- [ ] T108 ✅ AC5.1: README.md documents --fast flag with examples
- [ ] T109 ✅ AC5.2: README.md documents browser_profile configuration
- [ ] T110 ✅ AC5.3: Examples include fast-mode-optimized suite
- [ ] T111 ✅ AC5.4: Performance tradeoffs clearly explained

### End-to-End Validation

- [ ] T112 Run full test suite to verify no regressions: pytest tests/ -v
- [ ] T113 Test discover command works with browser_profile suites: familiar discover examples/
- [ ] T114 Run examples/basic-login without --fast (baseline behavior)
- [ ] T115 Run examples/basic-login with --fast (verify speedup)
- [ ] T116 Run examples/fast-login (if created) with optimized timing
- [ ] T117 Test --all --fast on all examples: familiar run examples/ --all --fast

### Performance Benchmarking

- [ ] T118 Measure and document simple 3-step test speedup
- [ ] T119 Measure and document complex 7-step test speedup
- [ ] T120 Compare different LLM providers with fast mode (if available)
- [ ] T121 Document scenarios where fast mode provides maximum benefit
- [ ] T122 Document scenarios where fast mode should be avoided

### Final Checklist

- [ ] T123 All unit tests pass: pytest tests/unit/ -v
- [ ] T124 All integration tests pass: pytest tests/integration/ -v
- [ ] T125 All acceptance criteria verified
- [ ] T126 No linter errors: ruff check src/
- [ ] T127 Documentation is complete and accurate
- [ ] T128 Examples are tested and working
- [ ] T129 Performance targets met (30-60% speedup)
- [ ] T130 Backward compatibility confirmed

**Checkpoint**: All acceptance criteria met - ready for merge

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Model Layer)**: Depends on Phase 1 - MUST complete before user stories
- **Phase 3 (US1)**: Depends on Phase 2 - Can start once models complete
- **Phase 4 (US2)**: Depends on Phase 2 - Can run parallel to Phase 3
- **Phase 5 (US3)**: Depends on Phases 3 and 4 - Integration validation
- **Phase 6 (Documentation)**: Can start after Phase 4 - Parallel with Phase 5
- **Phase 7 (Validation)**: Depends on all previous phases - Final checklist

### User Story Independence

```
Phase 2 (Model Layer - Foundation)
    ├── Phase 3 (US1: --fast CLI flag)
    └── Phase 4 (US2: browser_profile config)
            └── Phase 5 (US3: Combined validation)
```

**US1 and US2 are independent** and can be implemented in parallel after Phase 2.

### Parallel Execution Opportunities

**Within Phase 2 (Model Layer)**:
- T016-T022: All model unit tests can run in parallel [P]

**Within Phase 3 (US1)**:
- T033-T037: All US1 tests can run in parallel [P]

**Within Phase 4 (US2)**:
- T048-T052: All example/fixture creation can run in parallel [P]
- T053-T056: All US2 tests can run in parallel [P]

**Within Phase 5 (US3)**:
- T062-T064: Integration tests can run in parallel [P]
- T072-T074: Cross-provider tests can run in parallel [P]

**Within Phase 6 (Documentation)**:
- T076-T089: All documentation tasks can run in parallel [P]

### Critical Path

The minimum sequential path to MVP (US1 only):

```
Phase 1 (Setup) → Phase 2 (Models) → Phase 3 (US1: --fast flag) → Phase 7 (Validation)
```

**Estimated**: 15-20 tasks on critical path, rest can be parallelized

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Deliver First**: User Story 1 only
- Phase 1: Setup (T001-T007)
- Phase 2: Model Layer (T008-T023)
- Phase 3: US1 - --fast CLI flag (T024-T042)
- Phase 6: Minimal docs (T076-T081)
- Phase 7: US1 validation (T093-T096)

**Rationale**: Provides immediate value for developers with minimal code changes

### Incremental Delivery

**Iteration 1**: MVP (US1 - --fast flag)
- Core fast mode functionality
- Immediate 40-60% speedup for development

**Iteration 2**: Add US2 (browser_profile config)
- Persistent timing configuration
- CI/CD pipeline optimization

**Iteration 3**: Polish (US3 + Documentation)
- Combined optimization validation
- Comprehensive documentation
- Cross-provider testing

---

## Task Summary

**Total Tasks**: 130
- Phase 1 (Setup): 7 tasks
- Phase 2 (Model Layer): 16 tasks
- Phase 3 (US1 - Fast CLI): 19 tasks
- Phase 4 (US2 - Browser Profile): 19 tasks
- Phase 5 (US3 - Integration): 14 tasks
- Phase 6 (Documentation): 17 tasks
- Phase 7 (Validation): 38 tasks

**Parallel Opportunities**: 45 tasks marked [P]

**Independent Stories**: 
- US1: 19 tasks (T024-T042)
- US2: 19 tasks (T043-T061)
- US3: 14 tasks (T062-T075)

**MVP Critical Path**: ~25 tasks
**Full Implementation**: ~130 tasks

---

## Testing Strategy

**Unit Tests** (tests/unit/):
- test_models.py: BrowserProfileConfig validation
- test_cli.py: CLI flag acceptance
- test_runner.py: SuiteRunner configuration

**Integration Tests** (tests/integration/):
- test_runner.py: Fast mode execution, browser profile usage
- test_cli.py: End-to-end CLI workflows

**Performance Tests**:
- Baseline measurement
- Fast mode speedup validation
- Combined optimization validation

**No mocking of browser-use classes** - behavior-based testing per constitution

