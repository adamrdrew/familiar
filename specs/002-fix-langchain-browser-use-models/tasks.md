# Tasks: Fix LangChain Model Provider Bug

**Input**: Design documents from `/specs/002-fix-langchain-browser-use-models/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/browser-py-interface.md

**Type**: Bug Fix (Critical Priority)  
**Scope**: Replace incorrect LangChain model providers with browser-use native model classes

**Organization**: Tasks are organized by implementation phase. Since this is a bug fix (not a feature with user stories), tasks focus on the specific functional requirements and acceptance criteria.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Single project structure**: `src/familiar/`, `tests/` at repository root
- Primary modification: `src/familiar/utils/browser.py`
- Dependency cleanup: `pyproject.toml`
- Test verification: `tests/unit/test_utils.py`, `tests/integration/test_runner.py`

---

## Phase 1: Pre-Implementation Validation

**Purpose**: Verify current state and prepare for bug fix

- [ ] T001 Run existing test suite to establish baseline in tests/
- [ ] T002 Document current LangChain imports in src/familiar/utils/browser.py for comparison
- [ ] T003 [P] Check for any test mocks of langchain classes in tests/unit/test_utils.py

**Checkpoint**: Baseline established - ready for implementation

---

## Phase 2: Core Implementation (Bug Fix)

**Purpose**: Replace LangChain with browser-use native model providers

**Critical**: All changes maintain backward compatibility (FR4, NFR2)

### Import Replacements (FR1)

- [ ] T004 Replace `from langchain_openai import ChatOpenAI` with `from browser_use import ChatOpenAI` in src/familiar/utils/browser.py
- [ ] T005 Replace `from langchain_anthropic import ChatAnthropic` with `from browser_use import ChatAnthropic` in src/familiar/utils/browser.py
- [ ] T006 Replace `from langchain_google_genai import ChatGoogleGenerativeAI` with `from browser_use import ChatGoogle` in src/familiar/utils/browser.py
- [ ] T007 Replace `from langchain_ollama import ChatOllama` with `from browser_use import ChatOllama` in src/familiar/utils/browser.py

### Provider Implementation Updates (FR1, FR3)

- [ ] T008 Update OpenAI provider block in `create_llm()` to use `browser_use.ChatOpenAI` in src/familiar/utils/browser.py
- [ ] T009 Update Anthropic provider block in `create_llm()` to use `browser_use.ChatAnthropic` in src/familiar/utils/browser.py
- [ ] T010 Update Google/Gemini provider blocks to use `browser_use.ChatGoogle` (note: class name change from ChatGoogleGenerativeAI) in src/familiar/utils/browser.py
- [ ] T011 Update Ollama provider block in `create_llm()` to use `browser_use.ChatOllama` in src/familiar/utils/browser.py

### New Provider Support (FR5)

- [ ] T012 Add ChatBrowserUse provider support with `browser-use` provider name in `create_llm()` in src/familiar/utils/browser.py
- [ ] T013 Add BROWSER_USE_API_KEY validation for ChatBrowserUse provider in src/familiar/utils/browser.py
- [ ] T014 [P] Add ChatGroq provider support (optional enhancement) in src/familiar/utils/browser.py
- [ ] T015 [P] Add ChatAzureOpenAI provider support (optional enhancement) in src/familiar/utils/browser.py

### Error Message Updates

- [ ] T016 Update ImportError messages to reference browser-use instead of langchain packages in src/familiar/utils/browser.py
- [ ] T017 Update ValueError messages for unsupported providers to include new providers (browser-use, groq, azure) in src/familiar/utils/browser.py
- [ ] T018 Verify all API key validation messages remain clear and actionable in src/familiar/utils/browser.py

### Configuration Preservation (FR2, FR6)

- [ ] T019 Verify `FAMILIAR_MODEL_PROVIDER` environment variable handling unchanged in src/familiar/utils/browser.py
- [ ] T020 Verify `FAMILIAR_MODEL` override logic unchanged in src/familiar/utils/browser.py
- [ ] T021 Verify temperature parameter passing unchanged in src/familiar/utils/browser.py
- [ ] T022 Verify `create_browser_use_agent()` function signature unchanged in src/familiar/utils/browser.py

**Checkpoint**: Core implementation complete - ready for dependency cleanup

---

## Phase 3: Dependency Cleanup (NFR1)

**Purpose**: Remove unnecessary LangChain dependencies from project

- [ ] T023 Remove `langchain-openai` dependency from pyproject.toml
- [ ] T024 Remove `langchain-anthropic` dependency from pyproject.toml
- [ ] T025 Remove `langchain-google-genai` dependency from pyproject.toml
- [ ] T026 Remove `langchain-ollama` dependency from pyproject.toml
- [ ] T027 Run `uv sync` to update lock file with removed dependencies
- [ ] T028 Verify `browser-use` dependency is present in pyproject.toml

**Checkpoint**: Dependencies cleaned - ready for testing

---

## Phase 4: Test Verification (NFR3)

**Purpose**: Verify existing tests pass and update mocks if needed

### Unit Test Updates

- [ ] T029 Check if tests/unit/test_utils.py mocks langchain classes and update to browser_use if needed
- [ ] T030 Run unit tests with pytest tests/unit/test_utils.py -v to verify `create_llm()` tests pass
- [ ] T031 Run unit tests with pytest tests/unit/ -v to verify all unit tests pass

### Integration Test Verification

- [ ] T032 Run integration tests with pytest tests/integration/test_runner.py -v to verify end-to-end execution works
- [ ] T033 Run integration tests with pytest tests/integration/ -v to verify all integration tests pass

### Contract Test Verification

- [ ] T034 Run contract tests with pytest tests/contract/ -v to verify CLI interface contracts maintained

### Full Test Suite

- [ ] T035 Run complete test suite with pytest tests/ -v to verify all tests pass (NFR3)
- [ ] T036 Verify no new test failures introduced by bug fix

**Checkpoint**: All tests passing - implementation validated

---

## Phase 5: Manual Provider Testing

**Purpose**: Manually verify each provider works correctly (if API keys available)

### Core Provider Testing (FR3)

- [ ] T037 [P] Test OpenAI provider with `FAMILIAR_MODEL_PROVIDER=openai` and `OPENAI_API_KEY` set
- [ ] T038 [P] Test Anthropic provider with `FAMILIAR_MODEL_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` set (default)
- [ ] T039 [P] Test Google provider with `FAMILIAR_MODEL_PROVIDER=google` and `GOOGLE_API_KEY` set
- [ ] T040 [P] Test Ollama provider with `FAMILIAR_MODEL_PROVIDER=ollama` and local Ollama running

### New Provider Testing (FR5)

- [ ] T041 [P] Test ChatBrowserUse provider with `FAMILIAR_MODEL_PROVIDER=browser-use` and `BROWSER_USE_API_KEY` set
- [ ] T042 [P] Test Groq provider if implemented with `FAMILIAR_MODEL_PROVIDER=groq` and `GROQ_API_KEY` set
- [ ] T043 [P] Test Azure provider if implemented with `FAMILIAR_MODEL_PROVIDER=azure` and Azure credentials set

### Error Handling Testing

- [ ] T044 Test error message for missing API key (e.g., OPENAI_API_KEY not set for openai provider)
- [ ] T045 Test error message for unsupported provider (e.g., FAMILIAR_MODEL_PROVIDER=invalid)
- [ ] T046 Test that browser-use ImportError doesn't occur with package installed

**Checkpoint**: Manual testing complete - all providers work correctly

---

## Phase 6: Documentation & Polish (NFR4)

**Purpose**: Update documentation to reflect browser-use native providers

### Documentation Updates

- [ ] T047 [P] Update README.md to reference browser-use native model providers instead of LangChain
- [ ] T048 [P] Update model provider documentation with ChatBrowserUse option in README.md
- [ ] T049 [P] Add provider selection examples showing new providers in README.md or docs/
- [ ] T050 [P] Update environment variable documentation with new vars (BROWSER_USE_API_KEY, GROQ_API_KEY, etc.)

### Code Documentation

- [ ] T051 Update docstring for `create_llm()` to reflect browser-use classes in src/familiar/utils/browser.py
- [ ] T052 Update module-level documentation in src/familiar/utils/browser.py
- [ ] T053 Add inline comments explaining provider selection logic if needed in src/familiar/utils/browser.py

### Quickstart Validation

- [ ] T054 Follow quickstart.md verification steps to ensure guide is accurate
- [ ] T055 Test quickstart examples with at least one provider (Anthropic or OpenAI)
- [ ] T056 Verify troubleshooting section in quickstart.md addresses common issues

**Checkpoint**: Documentation complete - bug fix ready for review

---

## Phase 7: Final Validation & Acceptance Criteria

**Purpose**: Verify all acceptance criteria from spec.md are met

### Acceptance Criteria Verification

- [ ] T057 ✅ Verify `src/familiar/utils/browser.py` imports model classes from `browser_use` instead of langchain packages
- [ ] T058 ✅ Verify `create_llm()` function uses browser-use native model classes
- [ ] T059 ✅ Verify all model providers (openai, anthropic, google, ollama) work correctly
- [ ] T060 ✅ Verify environment variable handling remains unchanged (backward compatibility)
- [ ] T061 ✅ Verify existing tests pass without modification
- [ ] T062 ✅ Verify pyproject.toml removes langchain dependencies
- [ ] T063 ✅ Verify documentation updated to reference browser-use model providers

### Code Review Checklist

- [ ] T064 Verify no breaking changes to public APIs (NFR2)
- [ ] T065 Verify constitutional alignment (reduces abstraction, improves clarity)
- [ ] T066 Review error messages for clarity and actionability
- [ ] T067 Verify all imports are correct and no unused imports remain

### Performance & Behavior

- [ ] T068 Verify test execution time similar or improved (no regression)
- [ ] T069 Verify agent behavior identical to pre-fix behavior
- [ ] T070 Verify verbose logging works correctly with new implementation

**Checkpoint**: All acceptance criteria met - ready for merge

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Pre-Implementation)**: No dependencies - can start immediately
- **Phase 2 (Core Implementation)**: Depends on Phase 1 completion - All T004-T022 must complete before moving to Phase 3
- **Phase 3 (Dependency Cleanup)**: Depends on Phase 2 completion - Must not remove dependencies until code updated
- **Phase 4 (Test Verification)**: Depends on Phase 3 completion - Tests must run with new dependencies
- **Phase 5 (Manual Testing)**: Depends on Phase 4 completion - Manual testing after automated tests pass
- **Phase 6 (Documentation)**: Can start after Phase 4 (parallel with Phase 5 manual testing)
- **Phase 7 (Final Validation)**: Depends on all previous phases - Final checklist

### Task Dependencies Within Phases

**Phase 2 Import Replacements** (T004-T007):
- Can run sequentially or in parallel (same file, but different sections)
- Must complete before provider implementation updates

**Phase 2 Provider Updates** (T008-T011):
- Depend on corresponding import replacements (T004-T007)
- T008 depends on T004 (OpenAI)
- T009 depends on T005 (Anthropic)
- T010 depends on T006 (Google)
- T011 depends on T007 (Ollama)

**Phase 2 New Providers** (T012-T015):
- T012-T013 (ChatBrowserUse) can start after imports done
- T014-T015 (Groq, Azure) marked [P] - optional enhancements, can be done in parallel

**Phase 3 Dependency Cleanup** (T023-T028):
- Must complete sequentially to avoid dependency conflicts
- T027 (uv sync) must run after T023-T026

**Phase 4 Test Updates** (T029-T036):
- T029 (check mocks) must complete before T030 (run tests)
- T030-T034 can run after T029 in any order
- T035-T036 (full suite) should run after individual test groups pass

**Phase 5 Manual Testing** (T037-T046):
- All provider tests marked [P] - can run in parallel if multiple testers
- Error handling tests (T044-T046) can run anytime after core implementation

**Phase 6 Documentation** (T047-T056):
- All documentation tasks marked [P] - can run in parallel
- All depend on Phase 4 completion (know what to document)

**Phase 7 Validation** (T057-T070):
- Must run sequentially as checklist
- Each verifies a specific acceptance criterion or requirement

### Parallel Opportunities

**Phase 1**: T003 can run in parallel with T001-T002

**Phase 2**:
- T014-T015 (optional providers) can run in parallel
- Error message updates (T016-T018) can run in parallel
- Configuration verification (T019-T022) can run in parallel

**Phase 3**: Must run sequentially (dependency management)

**Phase 4**:
- After T029, tests T030-T034 can run in parallel
- Final suite (T035-T036) must wait for all

**Phase 5**: All manual testing (T037-T043) can run in parallel with multiple testers

**Phase 6**: All documentation (T047-T053) can run in parallel, quickstart (T054-T056) can run in parallel

**Phase 7**: Should run sequentially as final checklist

---

## Parallel Example: Core Implementation

```bash
# Sequential: Import replacements first
Task T004: "Replace langchain_openai with browser_use.ChatOpenAI"
Task T005: "Replace langchain_anthropic with browser_use.ChatAnthropic"
Task T006: "Replace langchain_google_genai with browser_use.ChatGoogle"
Task T007: "Replace langchain_ollama with browser_use.ChatOllama"

# Then: Provider updates (depend on imports)
Task T008: "Update OpenAI provider block"
Task T009: "Update Anthropic provider block"
Task T010: "Update Google/Gemini provider blocks"
Task T011: "Update Ollama provider block"

# Parallel: New providers (optional enhancements)
Task T014: "Add ChatGroq provider support" [P]
Task T015: "Add ChatAzureOpenAI provider support" [P]

# Parallel: Configuration verification
Task T019: "Verify FAMILIAR_MODEL_PROVIDER handling" [P]
Task T020: "Verify FAMILIAR_MODEL override logic" [P]
Task T021: "Verify temperature parameter passing" [P]
```

---

## Implementation Strategy

### Critical Path (Minimum Viable Fix)

1. **Phase 1**: Establish baseline (T001-T003) - ~15 minutes
2. **Phase 2**: Core implementation (T004-T022) - ~2-3 hours
   - Focus on FR1-FR4 (existing providers)
   - Skip optional T014-T015 for MVP
3. **Phase 3**: Dependency cleanup (T023-T028) - ~15 minutes
4. **Phase 4**: Test verification (T029-T036) - ~30 minutes
5. **Phase 5**: Manual testing (T037-T040 only) - ~30 minutes
6. **Phase 6**: Documentation (T047-T056) - ~1 hour
7. **Phase 7**: Final validation (T057-T070) - ~30 minutes

**Total MVP Time**: ~5-6 hours

### Enhanced Implementation (Include Optional Features)

Add to MVP:
- T012-T013: ChatBrowserUse support (+30 minutes)
- T014-T015: Groq/Azure support (+1 hour)
- T041-T043: Test new providers (+30 minutes)

**Total Enhanced Time**: ~7-8 hours

### Sequential Workflow (Single Developer)

1. Complete Phase 1 → Baseline established
2. Complete Phase 2 → Core fix done
3. Complete Phase 3 → Dependencies cleaned
4. Complete Phase 4 → Tests passing
5. Complete Phase 5 → Manual validation
6. Complete Phase 6 → Documentation updated
7. Complete Phase 7 → Final checklist
8. **STOP and REVIEW**: Bug fix complete, ready for PR

### Parallel Team Strategy

With 2-3 developers:

**After Phase 2-3 complete**:
- Developer A: Phase 4 (Test verification)
- Developer B: Phase 5 (Manual testing)
- Developer C: Phase 6 (Documentation)

Then all join for Phase 7 (Final validation)

---

## Success Criteria

### Must Have (Acceptance Criteria from spec.md)
- ✅ All imports use `browser_use` not `langchain_*`
- ✅ All existing providers work (openai, anthropic, google, ollama)
- ✅ All tests pass without modification
- ✅ No breaking changes to public API
- ✅ Dependencies cleaned from pyproject.toml
- ✅ Documentation updated

### Nice to Have (Enhancements)
- ✅ ChatBrowserUse provider support added
- ✅ Groq provider support added
- ✅ Azure OpenAI provider support added
- ✅ Comprehensive manual testing of all providers
- ✅ Enhanced documentation with examples

### Quality Gates
- ✅ Constitutional alignment maintained
- ✅ No performance regression
- ✅ Error messages clear and actionable
- ✅ Backward compatibility 100%
- ✅ Code simpler than before (reduced abstraction)

---

## Notes

- This is a **bug fix**, not a feature, so no user story organization
- Focus on acceptance criteria from spec.md
- Maintain 100% backward compatibility (critical)
- Only internal implementation changes, no public API changes
- Tests should pass without modification (validates behavior preservation)
- Google class name changes: `ChatGoogleGenerativeAI` → `ChatGoogle`
- Optional enhancements (T014-T015, T042-T043) can be deferred
- Commit after each logical group of tasks
- Run tests frequently during Phase 2 to catch issues early
- Document any deviations or issues encountered during implementation

