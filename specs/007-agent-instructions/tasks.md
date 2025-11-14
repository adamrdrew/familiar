# Tasks: Agent Instructions

**Input**: Design documents from `/specs/007-agent-instructions/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are explicitly requested in the feature specification. All test tasks are included per Testing Strategy in spec.md (Unit Tests, Integration Tests, Contract Tests).

**Organization**: Tasks are organized by technical layer/component for this single feature (Model → Utils → Parser → Runner → CLI → Tests → Docs).

## Current Progress

**Status**: ⏳ **Ready to Start**

- ✅ **Phase 1 (Baseline Verification)**: 1/1 complete
- ✅ **Phase 2 (Model Updates)**: 2/2 complete
- ✅ **Phase 3 (File Reading Utility)**: 2/2 complete
- ✅ **Phase 4 (Prompt Building)**: 2/2 complete
- ✅ **Phase 5 (Parser Updates)**: 2/2 complete
- ✅ **Phase 6 (Runner Updates)**: 3/3 complete
- ✅ **Phase 7 (CLI Updates)**: 3/3 complete
- ⏳ **Phase 8 (Unit Tests)**: 0/15 complete
- ⏳ **Phase 9 (Integration Tests)**: 0/6 complete
- ⏳ **Phase 10 (Contract Tests)**: 0/2 complete
- ⏳ **Phase 11 (Documentation & Examples)**: 0/5 complete
- ⏳ **Phase 12 (Finalization)**: 0/5 complete

**Total**: 20/48 tasks complete (42%)

---

## Format: `- [ ] [TaskID] [P?] Description with file path`

- **Checkbox**: ALWAYS start with `- [ ]`
- **Task ID**: Sequential number (T001, T002, T003...)
- **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)
- **Description**: Clear action with exact file path

---

## Phases

### Phase 1: Baseline Verification (Estimated: 5 minutes)

**Goal**: Ensure current test suite is passing before starting implementation.

**Independent Test Criteria**: All 103 existing tests pass without modification.

- [X] T001 Run existing test suite to establish baseline (pytest tests/ -v)

---

### Phase 2: Model Updates (Estimated: 15 minutes)

**Goal**: Add agent_instructions field to TestSuite model and update SuiteRunner initialization.

**Independent Test Criteria**: Existing tests still pass with backward compatible changes.

- [X] T002 Add agent_instructions field to TestSuite dataclass in src/familiar/models/suite.py
- [X] T003 [P] Add scenario_agent_override and global_agent_instructions parameters to SuiteRunner.__init__ in src/familiar/core/runner.py

**Validation**:
```bash
pytest tests/unit/test_models.py -v
pytest tests/integration/test_runner.py -v
```

---

### Phase 3: File Reading Utility (Estimated: 30 minutes)

**Goal**: Implement robust file reading function with encoding fallback and error handling.

**Independent Test Criteria**: File reading handles all error cases gracefully (missing, encoding, permissions, size).

- [X] T004 Add read_agent_instructions() function in src/familiar/core/parser.py with UTF-8/latin-1 fallback
- [X] T005 Add file size check and warning for files >100KB in read_agent_instructions()

**Validation**:
```python
from pathlib import Path
from familiar.core/parser import read_agent_instructions
# Test with non-existent file
result = read_agent_instructions(Path('nonexistent.md'))
assert result is None
```

---

### Phase 4: Prompt Building (Estimated: 30 minutes)

**Goal**: Implement pure function to combine fast mode prompt with agent instructions.

**Independent Test Criteria**: Prompt building correctly combines components in all 11 specified scenarios.

- [X] T006 Add build_system_message() function at module level in src/familiar/core/runner.py
- [X] T007 Implement prompt combination logic following Fast Mode → Global → Scenario order

**Validation**:
```python
from familiar.core.runner import build_system_message, SPEED_OPTIMIZATION_PROMPT
result = build_system_message(True, "Global", "Scenario", False)
assert SPEED_OPTIMIZATION_PROMPT in result
assert "Global" in result
assert "Scenario" in result
```

---

### Phase 5: Parser Updates (Estimated: 30 minutes)

**Goal**: Read scenario-level agent.md during suite parsing and store in TestSuite.

**Independent Test Criteria**: Parser reads agent.md from suite directory and stores in TestSuite.agent_instructions.

- [X] T008 Update SuiteParser.parse_suite() to read scenario agent.md file in src/familiar/core/parser.py
- [X] T009 Add agent_instructions to TestSuite construction in parse_suite() method

**Validation**:
```bash
pytest tests/unit/test_parser.py -v
```

---

### Phase 6: Runner Updates (Estimated: 45 minutes)

**Goal**: Use build_system_message to combine all prompt components and pass to executor.

**Independent Test Criteria**: Runner builds correct system message for all combinations of fast mode, global, scenario, and override flag.

- [X] T010 Update SuiteRunner.__init__ to store new parameters (scenario_agent_override, global_agent_instructions)
- [X] T011 Replace fast mode prompt logic with build_system_message() call in run_suite() method (~line 108)
- [X] T012 Pass combined system message to executor via extend_system_message parameter

**Validation**:
```bash
pytest tests/integration/test_runner.py -v
```

---

### Phase 7: CLI Updates (Estimated: 30 minutes)

**Goal**: Add --scenario-agent-override flag and discover global agent.md file.

**Independent Test Criteria**: CLI accepts new flag and passes parameters correctly to runner.

- [X] T013 Add --scenario-agent-override flag to run command in src/familiar/cli/main.py
- [X] T014 Update run() function signature to accept scenario_agent_override parameter
- [X] T015 Add global agent.md discovery in run_suite_command() in src/familiar/cli/run.py before creating runner

**Validation**:
```bash
familiar run --help | grep scenario-agent-override
```

---

### Phase 8: Unit Tests (Estimated: 2 hours)

**Goal**: Test all new functions with comprehensive coverage (11 prompt building tests + 10 file reading tests).

**Independent Test Criteria**: 100% coverage of build_system_message() and read_agent_instructions() functions.

- [ ] T016 [P] Create tests/unit/test_agent_instructions.py with TestBuildSystemMessage class
- [ ] T017 [P] Add test_no_components to verify None returned when no inputs
- [ ] T018 [P] Add test_fast_mode_only to verify fast mode prompt only
- [ ] T019 [P] Add test_global_only to verify global agent.md only
- [ ] T020 [P] Add test_scenario_only to verify scenario agent.md only
- [ ] T021 [P] Add test_fast_mode_plus_global to verify combination
- [ ] T022 [P] Add test_fast_mode_plus_scenario to verify combination
- [ ] T023 [P] Add test_global_plus_scenario_no_override to verify both combined
- [ ] T024 [P] Add test_global_plus_scenario_with_override to verify scenario only
- [ ] T025 [P] Add test_all_components_no_override to verify all three combined
- [ ] T026 [P] Add test_all_components_with_override to verify fast+scenario only
- [ ] T027 [P] Add test_override_with_no_scenario to verify global still used
- [ ] T028 [P] Add TestReadAgentInstructions class with test_file_not_found
- [ ] T029 [P] Add test_file_exists, test_empty_file, test_whitespace_only to test_agent_instructions.py
- [ ] T030 [P] Add test_utf8_file, test_latin1_fallback, test_large_file_warning to test_agent_instructions.py

**Validation**:
```bash
pytest tests/unit/test_agent_instructions.py -v --cov=src/familiar/core/runner --cov=src/familiar/core/parser
```

---

### Phase 9: Integration Tests (Estimated: 1 hour)

**Goal**: Test complete workflows with real agent.md files and suite execution.

**Independent Test Criteria**: All prompt combination scenarios work end-to-end with actual file reading and suite execution.

- [ ] T031 [P] Create tests/integration/test_agent_instructions_integration.py
- [ ] T032 [P] Add test_suite_with_global_agent_md_only to integration tests
- [ ] T033 [P] Add test_suite_with_scenario_agent_md_only to integration tests
- [ ] T034 [P] Add test_suite_with_both_agent_md_combined to integration tests
- [ ] T035 [P] Add test_suite_with_both_agent_md_override to integration tests
- [ ] T036 [P] Add test_suite_with_fast_mode_and_agent_md to integration tests

**Validation**:
```bash
pytest tests/integration/test_agent_instructions_integration.py -v
```

---

### Phase 10: Contract Tests (Estimated: 30 minutes)

**Goal**: Verify public API contracts (CLI flag acceptance, model field existence).

**Independent Test Criteria**: CLI accepts --scenario-agent-override flag and TestSuite has agent_instructions field.

- [ ] T037 [P] Add test_cli_accepts_scenario_agent_override_flag to tests/contract/test_cli_interface.py
- [ ] T038 [P] Add test_test_suite_has_agent_instructions_field to tests/contract/test_cli_interface.py

**Validation**:
```bash
pytest tests/contract/test_cli_interface.py -v
```

---

### Phase 11: Documentation & Examples (Estimated: 30 minutes)

**Goal**: Update documentation and add example agent.md files.

**Independent Test Criteria**: Documentation is accurate and examples are runnable.

- [ ] T039 [P] Add --scenario-agent-override flag documentation to README.md CLI reference section
- [ ] T040 [P] Add agent instructions section to docs/configuration.md with examples
- [ ] T041 [P] Create examples/basic-login/agent.md with example instructions
- [ ] T042 [P] Create examples/e-commerce/agent.md with example instructions
- [ ] T043 [P] Update README.md with agent instructions overview and usage examples

**Validation**:
```bash
grep "scenario-agent-override" README.md
grep "agent.md" docs/configuration.md
ls examples/basic-login/agent.md
ls examples/e-commerce/agent.md
```

---

### Phase 12: Finalization (Estimated: 30 minutes)

**Goal**: Ensure code quality, test coverage, and readiness for deployment.

**Independent Test Criteria**: All tests pass, code is formatted, coverage meets target, no linter errors.

- [ ] T044 Run complete test suite and verify all 103 + ~23 new tests pass
- [ ] T045 Run pytest coverage report and verify 100% coverage for new code
- [ ] T046 Run ruff check and ruff format on src/ and tests/
- [ ] T047 Verify backward compatibility by running existing examples without agent.md
- [ ] T048 Create IMPLEMENTATION_SUMMARY.md documenting all changes

**Validation**:
```bash
pytest tests/ -v
pytest --cov=src/familiar --cov-report=term-missing
ruff check src/ tests/
ruff format src/ tests/
familiar run examples/basic-login/
```

---

## Dependencies & Execution Order

**Linear Flow**:
```
Phase 1 (Baseline) - MUST do first
  ↓
Phase 2 (Models) - Blocking for all downstream
  ↓
Phase 3 (File Reading) + Phase 4 (Prompt Building) - Can be parallel
  ↓
Phase 5 (Parser) - Needs Phase 2, 3
  ↓
Phase 6 (Runner) - Needs Phase 2, 4
  ↓
Phase 7 (CLI) - Needs Phase 2, 3, 6
  ↓
Phases 8-10 (Tests) - Can be parallel after Phase 7
  ↓
Phase 11 (Docs) - Can be parallel with tests
  ↓
Phase 12 (Finalize) - MUST do last
```

**Critical Path**: Phase 1 → Phase 2 → Phase 5 → Phase 6 → Phase 7 → Phase 12

**Parallel Opportunities**:
- Phase 3 & 4 can be done simultaneously (different files, different functions)
- Phase 8, 9, 10 tests can be written in parallel (different test files)
- Phase 11 docs can be done in parallel with tests

---

## Parallel Execution Examples

**Batch 1** (After Phase 2 complete):
- T004-T005 (File reading) by Developer A
- T006-T007 (Prompt building) by Developer B

**Batch 2** (After Phase 7 complete):
- T016-T030 (Unit tests) by Developer A
- T031-T036 (Integration tests) by Developer B  
- T037-T038 (Contract tests) by Developer C
- T039-T043 (Documentation) by Developer D

---

## Implementation Strategy

### Test-Driven Development (TDD)

Per Constitution principle VIII and spec.md Section 10, this feature follows TDD:

1. **Unit Tests First**: Write tests for build_system_message() and read_agent_instructions() (Phase 8)
2. **Implement to Pass**: Implement functions to make tests pass (Phases 3-4)
3. **Integration Tests**: Verify end-to-end behavior (Phase 9)
4. **Contract Tests**: Validate public API contracts (Phase 10)

### Incremental Delivery

**MVP (Minimal Viable Product)**: Phases 1-7
- Core functionality working
- Can be tested manually
- No automated tests yet

**Complete Feature**: All Phases
- Full test coverage
- Documentation updated
- Production ready

### Rollback Strategy

If issues arise at any phase:
```bash
# Revert last commit
git revert HEAD --no-edit

# Re-run tests to confirm
pytest tests/ -v
```

---

## Success Criteria

**Feature Complete When**:
- ✅ All 48 tasks checked off
- ✅ All tests passing (103 existing + ~23 new = ~126 total)
- ✅ Coverage at 100% for new code
- ✅ CLI accepts --scenario-agent-override flag
- ✅ Global and scenario agent.md files supported
- ✅ Override behavior working correctly
- ✅ Fast mode integration working
- ✅ Documentation updated
- ✅ Examples created
- ✅ Backward compatibility verified
- ✅ Code formatted and linted

---

## Validation Commands

After each phase:

```bash
# Run tests
pytest tests/ -v

# Check coverage
pytest --cov=src/familiar --cov-report=term-missing

# Lint code
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Test CLI
familiar run --help

# Manual test with agent.md
echo "Test instructions" > /tmp/agent.md
familiar run examples/basic-login/
```

---

## Estimated Time Breakdown

| Phase | Estimated Time | Cumulative |
|-------|---------------|------------|
| Phase 1: Baseline | 5 min | 5 min |
| Phase 2: Models | 15 min | 20 min |
| Phase 3: File Reading | 30 min | 50 min |
| Phase 4: Prompt Building | 30 min | 80 min |
| Phase 5: Parser | 30 min | 110 min |
| Phase 6: Runner | 45 min | 155 min |
| Phase 7: CLI | 30 min | 185 min |
| Phase 8: Unit Tests | 120 min | 305 min |
| Phase 9: Integration Tests | 60 min | 365 min |
| Phase 10: Contract Tests | 30 min | 395 min |
| Phase 11: Documentation | 30 min | 425 min |
| Phase 12: Finalization | 30 min | 455 min |

**Total Estimated Time**: 455 minutes (~7.5 hours)

**Note**: With parallel execution (2-3 developers), total calendar time can be reduced to ~4-5 hours.

---

## Task Count Summary

- **Total Tasks**: 48
- **Parallelizable**: 31 tasks marked [P]
- **Sequential**: 17 tasks (must complete in order)
- **Test Tasks**: 23 tasks (48% of total)
- **Implementation Tasks**: 20 tasks (42% of total)
- **Documentation Tasks**: 5 tasks (10% of total)

---

## Notes

- All tasks follow strict checkbox format: `- [ ] [TaskID] [P?] Description with file path`
- Tests are explicitly requested per spec.md Section 10 (Testing Strategy)
- Feature is completely optional and backward compatible (zero breaking changes)
- File reading uses UTF-8 with latin-1 fallback per research.md
- Prompt order is: Fast Mode → Global → Scenario per research.md
- Constitution compliance verified (all 8 principles satisfied)

---

**Last Updated**: 2025-11-14  
**Status**: Ready for implementation  
**Branch**: `007-agent-instructions`

