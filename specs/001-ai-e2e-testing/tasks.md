# Tasks: AI-Driven End-to-End Testing Platform

**Input**: Design documents from `/specs/001-ai-e2e-testing/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the spec, but this is a testing tool - we follow TDD. All test tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Current Progress

**Status**: 🎉 **Phase 3 Complete - MVP Ready!**

- ✅ **Phase 1 (Setup)**: 10/10 complete (T001-T010, T010 skipped - browser-use handles Chromium automatically)
- ✅ **Phase 2 (Foundational)**: 46/46 complete (T011-T046)
  - ✅ All models and core parsers implemented
  - ✅ Test suite discovery working
  - ✅ CLI framework fully functional
  - ✅ All tests passing (43 passed, 1 skipped)
- ✅ **Phase 3 (User Story 1 - MVP)**: 22/22 complete (T047-T068)
  - ✅ Tests written first (TDD approach)
  - ✅ Utilities: environment variables, interpolation, **multi-provider LLM support**
  - ✅ Executor and Runner: step execution with error handling
  - ✅ Formatters: Rich terminal output
  - ✅ CLI run command fully functional
  - ✅ Exit code handling (0 for success, 1 for failure)
  - ✅ **Architecture**: 15+ LLM providers via browser-use's native model classes
- ⏳ **Phase 4+ (User Stories 2-5)**: Ready to implement - 0/78 remaining

**Recent Updates**:
- ✨ Updated to use browser-use's native model classes (ChatOpenAI, ChatAnthropic, ChatGoogle, etc.)
- ✨ Added FAMILIAR_MODEL_PROVIDER for provider selection (browseruse, openai, anthropic, gemini, azure, groq, ollama)
- ✨ Supports all browser-use providers: no need to maintain our own LLM integration code

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths assume src-layout: `src/familiar/` for source code

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create Python project structure with uv (pyproject.toml, .python-version, src/familiar/, tests/)
- [x] T002 Configure pyproject.toml with dependencies (browser-use, click, pydantic, pyyaml, rich)
- [x] T003 [P] Configure development dependencies (pytest, pytest-asyncio, pytest-cov, mypy, ruff)
- [x] T004 [P] Create .env.example with environment variable template
- [x] T005 [P] Create .gitignore for Python project (venv, __pycache__, .env, etc.)
- [x] T006 [P] Create README.md with project overview and installation instructions
- [x] T007 Create directory structure (src/familiar/{cli,core,models,formatters,logging,utils}/__init__.py)
- [x] T008 Create test directory structure (tests/{unit,integration,contract,fixtures}/__init__.py)
- [x] T009 Install dependencies with uv sync
- [ ] T010 [P] ~~Install Chromium for browser-use~~ (SKIPPED - browser-use handles this automatically via Playwright)

**Checkpoint**: Project structure ready, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Models (Data Structures)

- [x] T011 [P] Create SuiteConfig model with Pydantic validation in src/familiar/models/suite.py
- [x] T012 [P] Create RetryPolicyConfig model in src/familiar/models/suite.py
- [x] T013 [P] Create TestSuite dataclass in src/familiar/models/suite.py
- [x] T014 [P] Create TestStep dataclass with name/variables properties in src/familiar/models/step.py
- [x] T015 [P] Create LogEntry and LogLevel enums in src/familiar/models/result.py
- [x] T016 [P] Create BrowserAction and ActionType enums in src/familiar/models/result.py
- [x] T017 [P] Create TestResult dataclass in src/familiar/models/result.py
- [x] T018 [P] Create SuiteResult dataclass with computed properties in src/familiar/models/result.py
- [x] T019 [P] Create TestRun dataclass in src/familiar/models/result.py

### Model Tests

- [x] T020 [P] Test SuiteConfig validation (timeout constraints) in tests/unit/test_models.py
- [x] T021 [P] Test TestStep name extraction and variable parsing in tests/unit/test_models.py
- [x] T022 [P] Test SuiteResult success calculation with fuzziness in tests/unit/test_models.py

### Core Parsers

- [x] T023 Create SuiteParser class in src/familiar/core/parser.py
- [x] T024 Add parse_suite method to load suite.yaml and step files in src/familiar/core/parser.py
- [x] T025 Add _parse_config method using PyYAML in src/familiar/core/parser.py
- [x] T026 Add _parse_steps method to find NN-*.md files in src/familiar/core/parser.py
- [x] T027 Add _parse_step method to load markdown content in src/familiar/core/parser.py

### Parser Tests

- [x] T028 [P] Test parse_suite with valid suite directory in tests/unit/test_parser.py
- [x] T029 [P] Test parse_suite error handling (missing suite.yaml) in tests/unit/test_parser.py
- [x] T030 [P] Test step file discovery and ordering in tests/unit/test_parser.py

### Discovery

- [x] T031 Create TestSuiteDiscovery class in src/familiar/core/discovery.py
- [x] T032 Add discover_suites method using rglob for suite.yaml in src/familiar/core/discovery.py
- [x] T033 Add error handling for malformed suites (continue discovery) in src/familiar/core/discovery.py

### Discovery Tests

- [x] T034 [P] Test discover_suites finds multiple suites in tests/unit/test_discovery.py
- [x] T035 [P] Test discovery skips shared directory in tests/unit/test_discovery.py

### CLI Foundation

- [x] T036 Create CLI entry point with Click in src/familiar/cli/main.py
- [x] T037 Add version option and help text in src/familiar/cli/main.py
- [x] T038 Create __main__.py entry point for python -m familiar in src/familiar/__main__.py
- [x] T039 Configure entry point in pyproject.toml [project.scripts]
- [x] T040 Install package in editable mode (uv pip install -e .)

### CLI Tests

- [x] T041 [P] Test CLI --version output in tests/contract/test_cli_interface.py
- [x] T042 [P] Test CLI --help displays commands in tests/contract/test_cli_interface.py

### Test Fixtures

- [x] T043 Create pytest conftest.py with temp directory fixture in tests/conftest.py
- [x] T044 [P] Create sample suite fixture in tests/fixtures/sample-suite/
- [x] T045 [P] Create sample suite.yaml in tests/fixtures/sample-suite/suite.yaml
- [x] T046 [P] Create sample step files in tests/fixtures/sample-suite/00-login.md and 01-dashboard.md

**Checkpoint**: Foundation ready - models work, parser works, discovery works, CLI boots

---

## Phase 3: User Story 1 - Run Single Natural Language Test (Priority: P1) 🎯 MVP

**Goal**: Execute a single test step using natural language, show results with logs

**Independent Test**: Create test file with "Visit homepage", run `familiar run test-file`, verify structured output with pass/fail and logs

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T047 [P] [US1] Contract test for CLI run command interface in tests/contract/test_cli_interface.py
- [x] T048 [P] [US1] Integration test for single step execution in tests/integration/test_runner.py
- [x] T049 [P] [US1] Integration test for exit code 0 on success in tests/integration/test_cli.py
- [x] T050 [P] [US1] Integration test for exit code 1 on failure in tests/integration/test_cli.py

### Implementation for User Story 1

- [x] T051 [P] [US1] Create environment variable parser in src/familiar/utils/env.py
- [x] T052 [P] [US1] Create variable interpolation module in src/familiar/utils/interpolation.py
- [x] T053 [US1] Add interpolate_variables method to resolve ${VAR} syntax in src/familiar/utils/interpolation.py
- [x] T054 [P] [US1] Create multi-provider LLM factory using browser-use's native model classes in src/familiar/utils/browser.py
- [x] T055 [US1] Add create_browser_use_agent factory with provider selection (FAMILIAR_MODEL_PROVIDER) in src/familiar/utils/browser.py
- [x] T056 [US1] Create StepExecutor class for browser-use integration in src/familiar/core/executor.py
- [x] T057 [US1] Add execute_step async method wrapping browser-use Agent in src/familiar/core/executor.py
- [x] T058 [US1] Add error handling and logging to StepExecutor in src/familiar/core/executor.py
- [x] T059 [US1] Create SuiteRunner class in src/familiar/core/runner.py
- [x] T060 [US1] Add run_suite async method to orchestrate step execution in src/familiar/core/runner.py
- [x] T061 [US1] Add logging setup for real-time progress in src/familiar/logging/setup.py
- [x] T062 [P] [US1] Create console log handler with rich formatting in src/familiar/logging/handlers.py
- [x] T063 [P] [US1] Create TextFormatter for human-readable output in src/familiar/formatters/text.py
- [x] T064 [US1] Implement format method for SuiteResult in src/familiar/formatters/text.py
- [x] T065 [US1] Create run command implementation in src/familiar/cli/run.py
- [x] T066 [US1] Add --format and --headless options to run command in src/familiar/cli/run.py
- [x] T067 [US1] Wire up run command to main CLI in src/familiar/cli/main.py
- [x] T068 [US1] Add exit code handling (0 for success, 1 for failure) in src/familiar/cli/run.py

**Checkpoint**: At this point, User Story 1 should be fully functional - can run single test with natural language and see results

---

## Phase 4: User Story 2 - Organize Tests into Suites (Priority: P2)

**Goal**: Discover multiple suites in directory structure, run specific or all suites

**Independent Test**: Create directory with multiple suite folders, run discovery, verify all found, run specific suite

### Tests for User Story 2

- [ ] T069 [P] [US2] Contract test for discover command interface in tests/contract/test_cli_interface.py
- [ ] T070 [P] [US2] Integration test for suite discovery with multiple suites in tests/integration/test_cli.py
- [ ] T071 [P] [US2] Integration test for running specific suite by name in tests/integration/test_cli.py
- [ ] T072 [P] [US2] Integration test for running all suites in tests/integration/test_cli.py

### Implementation for User Story 2

- [ ] T073 [US2] Create discover command implementation in src/familiar/cli/discover.py
- [ ] T074 [US2] Add --format option (text, json) to discover command in src/familiar/cli/discover.py
- [ ] T075 [US2] Add --validate flag to discover command in src/familiar/cli/discover.py
- [ ] T076 [US2] Wire up discover command to main CLI in src/familiar/cli/main.py
- [ ] T077 [P] [US2] Create JSONFormatter for machine-readable output in src/familiar/formatters/json.py
- [ ] T078 [US2] Implement format method for suite discovery results in src/familiar/formatters/json.py
- [ ] T079 [US2] Add --suite option to run command for specific suite execution in src/familiar/cli/run.py
- [ ] T080 [US2] Add --all flag to run command for all suite execution in src/familiar/cli/run.py
- [ ] T081 [US2] Implement multi-suite execution in run command in src/familiar/cli/run.py
- [ ] T082 [US2] Add suite summary statistics to TextFormatter in src/familiar/formatters/text.py
- [ ] T083 [US2] Update run command to display per-suite and overall results in src/familiar/cli/run.py

**Checkpoint**: User Stories 1 AND 2 should both work independently - can discover and run multiple suites

---

## Phase 5: User Story 3 - Handle Non-Deterministic Failures with Retries (Priority: P3)

**Goal**: Implement retry policies (fixed, exponential, best-of-n) with proper logging

**Independent Test**: Create test with intermittent failure, configure retry policy, verify retries logged and test passes if any succeeds

### Tests for User Story 3

- [ ] T084 [P] [US3] Unit test for FixedRetry policy in tests/unit/test_retry.py
- [ ] T085 [P] [US3] Unit test for ExponentialBackoff policy in tests/unit/test_retry.py
- [ ] T086 [P] [US3] Unit test for BestOfN policy in tests/unit/test_retry.py
- [ ] T087 [P] [US3] Integration test for step retry on failure in tests/integration/test_runner.py
- [ ] T088 [P] [US3] Integration test for best-of-n run strategy in tests/integration/test_runner.py

### Implementation for User Story 3

- [ ] T089 [P] [US3] Create RetryPolicy protocol interface in src/familiar/core/retry.py
- [ ] T090 [P] [US3] Implement FixedRetry strategy in src/familiar/core/retry.py
- [ ] T091 [P] [US3] Implement ExponentialBackoff strategy in src/familiar/core/retry.py
- [ ] T092 [P] [US3] Implement BestOfN strategy in src/familiar/core/retry.py
- [ ] T093 [US3] Add retry logic to StepExecutor in src/familiar/core/executor.py
- [ ] T094 [US3] Add retry attempt logging (attempt number, delay) in src/familiar/core/executor.py
- [ ] T095 [US3] Update SuiteRunner to use retry policies from config in src/familiar/core/runner.py
- [ ] T096 [US3] Add fuzziness calculation to SuiteResult in src/familiar/models/result.py
- [ ] T097 [US3] Update SuiteRunner to respect fuzziness setting in src/familiar/core/runner.py
- [ ] T098 [US3] Add retry context to log output in src/familiar/formatters/text.py
- [ ] T099 [US3] Update TextFormatter to show all retry attempts for failed steps in src/familiar/formatters/text.py

**Checkpoint**: All user stories 1-3 should work independently - tests can retry with configurable policies

---

## Phase 6: User Story 4 - CI/CD Pipeline Integration (Priority: P4)

**Goal**: Produce CI-friendly output formats (JUnit XML, JSON), proper exit codes, headless mode

**Independent Test**: Run in CI-like environment, verify exit codes, generate JUnit XML that CI can parse

### Tests for User Story 4

- [ ] T100 [P] [US4] Contract test for JUnit XML output format in tests/contract/test_cli_interface.py
- [ ] T101 [P] [US4] Contract test for JSON output format in tests/contract/test_cli_interface.py
- [ ] T102 [P] [US4] Integration test for exit code 0 when all tests pass in tests/integration/test_cli.py
- [ ] T103 [P] [US4] Integration test for exit code 1 when any test fails in tests/integration/test_cli.py
- [ ] T104 [P] [US4] Integration test for exit code 2 on configuration error in tests/integration/test_cli.py

### Implementation for User Story 4

- [ ] T105 [P] [US4] Create JUnitFormatter class in src/familiar/formatters/junit.py
- [ ] T106 [US4] Implement format method to generate JUnit XML in src/familiar/formatters/junit.py
- [ ] T107 [US4] Add test suite grouping to JUnit XML in src/familiar/formatters/junit.py
- [ ] T108 [US4] Add failure details and logs to JUnit XML in src/familiar/formatters/junit.py
- [ ] T109 [US4] Update JSONFormatter with complete test run data in src/familiar/formatters/json.py
- [ ] T110 [US4] Add duration and timestamp fields to JSON output in src/familiar/formatters/json.py
- [ ] T111 [US4] Add --output option to run command for file output in src/familiar/cli/run.py
- [ ] T112 [US4] Implement formatter selection based on --format flag in src/familiar/cli/run.py
- [ ] T113 [US4] Add exit code 2 for configuration errors in src/familiar/cli/run.py
- [ ] T114 [US4] Add exit code 3 for infrastructure errors in src/familiar/cli/run.py
- [ ] T115 [US4] Add CI environment detection (FAMILIAR_HEADLESS env var) in src/familiar/utils/env.py
- [ ] T116 [US4] Update browser setup to respect headless mode in src/familiar/utils/browser.py

**Checkpoint**: All user stories 1-4 work independently - can run in CI with proper outputs

---

## Phase 7: User Story 5 - Interactive Debugging and Stepover (Priority: P5)

**Goal**: Implement debug mode with interactive commands (step, continue, inspect)

**Independent Test**: Run test with --debug flag, verify execution pauses, accepts commands, shows browser state

### Tests for User Story 5

- [ ] T117 [P] [US5] Integration test for debug mode pausing at steps in tests/integration/test_cli.py
- [ ] T118 [P] [US5] Integration test for debug commands (step, continue, inspect) in tests/integration/test_cli.py

### Implementation for User Story 5

- [ ] T119 [P] [US5] Create interactive debug handler in src/familiar/cli/debug.py
- [ ] T120 [US5] Implement debug command parser (step, continue, inspect, etc.) in src/familiar/cli/debug.py
- [ ] T121 [US5] Add pause points to StepExecutor for debug mode in src/familiar/core/executor.py
- [ ] T122 [US5] Implement inspect command to show browser state in src/familiar/cli/debug.py
- [ ] T123 [US5] Implement screenshot command in debug mode in src/familiar/cli/debug.py
- [ ] T124 [US5] Add --debug flag to run command in src/familiar/cli/run.py
- [ ] T125 [US5] Wire up debug mode to StepExecutor in src/familiar/cli/run.py
- [ ] T126 [US5] Add AI reasoning display for debug mode in src/familiar/cli/debug.py
- [ ] T127 [US5] Add debug command help text in src/familiar/cli/debug.py

**Checkpoint**: All user stories 1-5 complete and independently testable

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T128 [P] Create validate command implementation in src/familiar/cli/validate.py
- [ ] T129 [P] Add --all and --strict flags to validate command in src/familiar/cli/validate.py
- [ ] T130 [P] Wire up validate command to main CLI in src/familiar/cli/main.py
- [ ] T131 [P] Create init command for new suite scaffolding in src/familiar/cli/init.py
- [ ] T132 [P] Add template support to init command in src/familiar/cli/init.py
- [ ] T133 [P] Wire up init command to main CLI in src/familiar/cli/main.py
- [ ] T134 [P] Implement shared step resolution (!include directive) in src/familiar/utils/interpolation.py
- [ ] T135 [P] Add circular include detection in src/familiar/utils/interpolation.py
- [ ] T136 [P] Add screenshot capture on failure in src/familiar/core/executor.py
- [ ] T137 [P] Implement graceful Ctrl+C handling in src/familiar/cli/run.py
- [ ] T138 [P] Add browser cleanup on interruption in src/familiar/core/runner.py
- [ ] T139 [P] Create file log handler for structured logs in src/familiar/logging/handlers.py
- [ ] T140 [P] Add sensitive value masking in logs in src/familiar/logging/setup.py
- [ ] T141 [P] Create getting-started.md documentation in docs/getting-started.md
- [ ] T142 [P] Create test-suite-format.md documentation in docs/test-suite-format.md
- [ ] T143 [P] Create configuration.md documentation in docs/configuration.md
- [ ] T144 [P] Create ci-integration.md documentation in docs/ci-integration.md
- [ ] T145 [P] Add comprehensive error messages with suggestions in src/familiar/core/executor.py
- [ ] T146 [P] Add timeout handling at step and suite level in src/familiar/core/runner.py
- [ ] T147 [P] Run full test suite validation (pytest with coverage)
- [ ] T148 [P] Run linting and type checking (ruff, mypy)
- [ ] T149 Code cleanup and refactoring pass for constitution compliance
- [ ] T150 Update README.md with complete examples and badges

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (if staffed) after Foundation
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent, but builds on US1's execution engine
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent, enhances US1's execution
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent, adds output formats to US1
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Independent, adds debug mode to US1

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before commands
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a phase marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for CLI run command interface in tests/contract/test_cli_interface.py"
Task: "Integration test for single step execution in tests/integration/test_runner.py"
Task: "Integration test for exit code 0 on success in tests/integration/test_cli.py"
Task: "Integration test for exit code 1 on failure in tests/integration/test_cli.py"

# Launch all parallel implementation tasks together:
Task: "Create environment variable parser in src/familiar/utils/env.py"
Task: "Create variable interpolation module in src/familiar/utils/interpolation.py"
Task: "Create browser-use client setup helpers in src/familiar/utils/browser.py"
Task: "Create console log handler with rich formatting in src/familiar/logging/handlers.py"
Task: "Create TextFormatter for human-readable output in src/familiar/formatters/text.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**Deliverable**: Working CLI that can run a single natural language test and show results.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! ✅)
3. Add User Story 2 → Test independently → Deploy/Demo (Discovery + multi-suite)
4. Add User Story 3 → Test independently → Deploy/Demo (Retry policies)
5. Add User Story 4 → Test independently → Deploy/Demo (CI/CD ready)
6. Add User Story 5 → Test independently → Deploy/Demo (Debug mode)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T047-T068)
   - Developer B: User Story 2 (T069-T083) - can start in parallel
   - Developer C: User Story 3 (T084-T099) - can start in parallel
3. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 150

**By Phase**:
- Phase 1 (Setup): 10 tasks
- Phase 2 (Foundational): 36 tasks (BLOCKING)
- Phase 3 (User Story 1 - P1): 22 tasks 🎯 MVP
- Phase 4 (User Story 2 - P2): 15 tasks
- Phase 5 (User Story 3 - P3): 16 tasks
- Phase 6 (User Story 4 - P4): 17 tasks
- Phase 7 (User Story 5 - P5): 11 tasks
- Phase 8 (Polish): 23 tasks

**Parallel Opportunities**: 89 tasks marked [P] can run in parallel (59% of tasks)

**Independent Test Criteria**:
- **US1**: Single test execution with natural language → structured output
- **US2**: Multi-suite discovery and selective execution → per-suite results
- **US3**: Retry configuration → successful retry logged and counted
- **US4**: CI execution → proper exit codes and JUnit XML format
- **US5**: Debug mode → pauses at steps, accepts commands

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 68 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are included because Familiar is a testing tool - we must practice what we preach
- All tasks follow constitutional principles: small classes, clear interfaces, behavior tests

### LLM Provider Architecture

**Implementation**: Tasks T054-T055 implement multi-provider LLM support via browser-use's native model classes.

**Key Design Decisions**:
- ✅ Use browser-use's `ChatOpenAI`, `ChatAnthropic`, `ChatGoogle`, etc. - NOT langchain directly
- ✅ Factory pattern in `create_llm()` returns appropriate browser-use model class
- ✅ Provider selection via `FAMILIAR_MODEL_PROVIDER` env var
- ✅ Model selection via `FAMILIAR_MODEL` env var
- ✅ API keys use browser-use's conventions (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.)
- ✅ Supports 15+ providers: browseruse, openai, anthropic, gemini, azure, groq, ollama, aws, oci, and more
- ✅ Future providers added automatically via browser-use updates

**References**:
- Supported models: https://github.com/browser-use/browser-use/blob/main/docs/supported-models.mdx
- Browser Use Cloud (optimized model): https://browser-use.com/posts/speed-matters

---

## Format Validation ✅

All 150 tasks follow the required checklist format:
- ✅ All tasks start with `- [ ]` checkbox
- ✅ All tasks have sequential Task ID (T001-T150)
- ✅ Parallel tasks marked with [P]
- ✅ User story tasks marked with [US1]-[US5]
- ✅ All implementation tasks include exact file paths
- ✅ Tasks organized by user story for independent delivery

