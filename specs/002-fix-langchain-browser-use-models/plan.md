# Implementation Plan: Fix LangChain Model Provider Bug

**Branch**: `002-fix-langchain-browser-use-models` | **Date**: 2025-11-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fix-langchain-browser-use-models/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Replace incorrect LangChain model provider usage with browser-use's native model classes in `src/familiar/utils/browser.py`. The current implementation uses `langchain-openai`, `langchain-anthropic`, etc., which adds unnecessary dependencies. Browser-use provides its own model provider classes (`ChatOpenAI`, `ChatAnthropic`, etc.) that should be used directly.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: browser-use (with native model providers), playwright
**Storage**: N/A (bug fix only)
**Testing**: pytest (existing test suite)
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single project (CLI tool)
**Performance Goals**: N/A (bug fix maintains existing performance)
**Constraints**: Must maintain backward compatibility with existing environment variables
**Scale/Scope**: Single file modification (`src/familiar/utils/browser.py`), dependency cleanup in `pyproject.toml`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitutional Alignment

✅ **Easy to Change**: Bug fix removes unnecessary dependency layer (LangChain), making the codebase easier to maintain and evolve with browser-use updates.

✅ **Small, Single Purpose Classes**: No new classes introduced. Existing `create_llm()` function maintains single responsibility of creating appropriate LLM client.

✅ **Stable, Minimal Public Interfaces**: Public API of `create_browser_use_agent()` remains unchanged. Internal implementation detail only.

✅ **Polymorphism Over Conditionals**: Maintains existing provider selection pattern via environment variables. No new conditionals introduced.

✅ **Behavior-Based Testing**: Existing tests validate behavior (agent creation, task execution), not implementation. Tests should pass without modification.

✅ **Code as User Interface**: Simplifies code by using browser-use's native classes directly instead of wrapping LangChain.

✅ **Humane Code**: Reduces abstraction layers, making it clearer that we use browser-use's model system directly.

✅ **Test-Driven Development**: Existing test suite validates behavior. Bug fix maintains existing behavior with simpler implementation.

**Gate Result**: ✅ PASS - This bug fix aligns with all constitutional principles and actively improves code quality by reducing unnecessary abstraction.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── familiar/
    ├── utils/
    │   └── browser.py          # PRIMARY FILE TO MODIFY
    ├── core/
    │   └── executor.py         # Uses browser.py (no changes needed)
    └── ...

tests/
├── unit/
│   └── test_utils.py           # May need assertion updates
└── integration/
    └── test_runner.py          # Integration tests should pass as-is

pyproject.toml                   # Remove langchain dependencies
```

**Structure Decision**: Single project structure. This is a focused bug fix affecting one primary file (`src/familiar/utils/browser.py`) and dependency declaration (`pyproject.toml`). No new files or modules required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations. This bug fix simplifies the codebase by removing unnecessary abstraction.

## Phase Completion Status

### Phase 0: Research ✅ COMPLETE

**Outputs**:
- ✅ `research.md` - Comprehensive research on browser-use native model providers
  - Decision: Use browser-use classes directly instead of LangChain
  - Rationale: Simplifies codebase, reduces dependencies, ensures compatibility
  - Model provider mapping documented
  - Environment variable strategy defined
  - Error handling approach defined

**Key Findings**:
- Browser-use includes all model providers natively
- Drop-in replacement for LangChain classes
- Google class name changes from `ChatGoogleGenerativeAI` to `ChatGoogle`
- All existing environment variables remain compatible
- Can add ChatBrowserUse as optimized provider option

### Phase 1: Design & Contracts ✅ COMPLETE

**Outputs**:
- ✅ `data-model.md` - Documents affected types and data structures
  - Function signatures remain unchanged
  - Environment variable configuration model documented
  - Error types and validation rules defined
  - Backward compatibility confirmed
  
- ✅ `contracts/browser-py-interface.md` - Function contract specifications
  - `create_llm()` contract documented
  - `create_browser_use_agent()` contract documented
  - Error handling contracts defined
  - Testing contracts specified
  
- ✅ `quickstart.md` - User-facing guide for bug fix
  - Verification steps provided
  - Provider-specific examples included
  - ChatBrowserUse option documented
  - Troubleshooting guide included
  
- ✅ Agent context updated - Cursor IDE rules updated with new tech stack info

### Phase 2: Tasks ⏸️ PENDING

Phase 2 (`tasks.md` generation via `/speckit.tasks` command) is NOT part of the `/speckit.plan` workflow. The planning phase stops here per the command specification.

## Final Constitution Check (Post-Design)

*Re-evaluation after Phase 1 design artifacts complete*

### Constitutional Alignment Review

✅ **Easy to Change**: The design maintains loose coupling. Browser-use model classes are used through their public interfaces only. No internal implementation details are coupled.

✅ **Small, Single Purpose Classes**: No new classes introduced. Existing `create_llm()` function maintains its single purpose: create appropriate LLM client based on configuration.

✅ **Stable, Minimal Public Interfaces**: 
- Public interface of `create_browser_use_agent()` completely unchanged
- `create_llm()` signature unchanged
- Internal implementation changes only
- Contract documentation confirms interface stability

✅ **Polymorphism Over Conditionals**: 
- Provider selection uses conditional (acceptable for factory pattern)
- All browser-use model classes implement common interface
- Polymorphism at the LLM provider level (each provider class handles its own initialization)

✅ **Behavior-Based Testing**: 
- Contracts specify behavior, not implementation
- Tests verify outcomes (agent creation, task execution) not internals
- Existing tests should pass without modification (validates behavior preservation)

✅ **Code as User Interface**: 
- Simplifies code by removing LangChain wrapper layer
- Direct usage of browser-use classes is clearer
- Fewer abstractions = easier to understand

✅ **Humane Code**: 
- Code becomes more explicit (direct imports from browser_use)
- Reduces dependency chain
- Easier to understand what's happening (less indirection)

✅ **Test-Driven Development**: 
- Design preserves existing test suite
- Contracts define testable behavior
- Bug fix can be verified through existing tests

**Final Gate Result**: ✅ PASS - Design maintains constitutional compliance and actively improves code quality.

## Summary

This implementation plan has completed Phases 0 and 1:

1. **Research Phase**: Investigated browser-use's native model system, documented decisions and rationale
2. **Design Phase**: Created data model, contracts, and quickstart guide
3. **Constitution**: Verified full alignment with project principles

**Next Steps** (outside this command):
1. Run `/speckit.tasks` to generate implementation tasks from this plan
2. Implement the bug fix per the tasks
3. Run tests to verify behavior preservation
4. Update documentation if needed
