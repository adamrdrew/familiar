# Implementation Plan: Agent Instructions

**Branch**: `007-agent-instructions` | **Date**: 2025-11-14 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/007-agent-instructions/spec.md`  
**Status**: ✅ **PLANNING COMPLETE** - Ready for `/speckit.tasks`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add optional agent instructions feature that allows users to provide custom prompts via `agent.md` files at global and scenario levels. Instructions are combined with existing fast mode prompts and injected into the system message when creating the LLM. Supports hierarchical configuration with override capability.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: browser-use>=0.9.5, click>=8.1.0, pydantic>=2.0.0, pyyaml>=6.0, rich>=13.0.0, python-dotenv>=1.0.0  
**Storage**: File system (markdown agent instruction files, read alongside suite files)  
**Testing**: pytest>=7.4.0, pytest-asyncio>=0.21.0, pytest-cov>=4.1.0  
**Target Platform**: macOS, Linux, Windows (Python 3.11+ environments)  
**Project Type**: Single Python CLI application with library components  
**Performance Goals**: Minimal overhead (<10ms for file reading and prompt construction)  
**Constraints**: Zero breaking changes to public API, must work with existing fast mode, backward compatible  
**Scale/Scope**: ~300 lines of new code (parser updates, model updates, CLI updates, tests)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Easy to Change
- **Pass**: Agent instructions will be read by parser (single responsibility)
- **Pass**: Passed as data to runner (dependency injection)
- **Pass**: Prompt building isolated in separate function
- **Action Required**: Ensure prompt building is testable independently

### ✅ II. Small, Single Purpose Classes
- **Pass**: No new classes required
- **Pass**: Existing classes maintain single responsibility:
  - Parser: reads agent.md files
  - TestSuite: stores agent instructions as data
  - SuiteRunner: builds system message and passes to executor
- **Pass**: New functions will be small (<20 lines each)

### ✅ III. Stable, Minimal Public Interfaces
- **Pass**: Only adds optional field to TestSuite (backward compatible)
- **Pass**: CLI adds one optional flag `--scenario-agent-override`
- **Pass**: No changes to existing public APIs
- **Action Required**: Ensure TestSuite.agent_instructions has sensible default (None)

### ✅ IV. Polymorphism Over Conditionals
- **Pass**: Prompt building uses simple conditional logic (appropriate for data combination)
- **Pass**: No type-based branching needed
- **Note**: Fast mode + agent instructions is data combination, not behavior polymorphism

### ✅ V. Behavior-Based Testing
- **Pass**: Tests will validate outcomes (system message content) not internals
- **Pass**: Tests will verify file reading behavior
- **Action Required**: Write integration tests for all prompt combination scenarios

### ✅ VI. Code as User Interface
- **Pass**: Clear names: `agent_instructions`, `build_system_message`, `agent.md`
- **Pass**: Simple file-based configuration (markdown, no special format)
- **Pass**: Familiar pattern (similar to .env files)

### ✅ VII. Humane Code
- **Pass**: Feature is completely optional (no complexity for non-users)
- **Pass**: Clear flag name: `--scenario-agent-override`
- **Pass**: Simple file location rules (global vs scenario)

### ✅ VIII. Test-Driven Development
- **Pass**: Will write tests for prompt building logic first
- **Pass**: Will write tests for file discovery/reading
- **Action Required**: Ensure 100% coverage of new prompt building function

### Summary
**Overall**: ✅ PASS - No violations  
**Gate Status**: Proceed to Phase 0  
**Required Actions**: Standard TDD workflow, ensure testability

## Project Structure

### Documentation (this feature)

```text
specs/007-agent-instructions/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Current Structure** (Single Python CLI Project):

```text
src/familiar/
├── __init__.py
├── __main__.py
├── cli/
│   ├── main.py      # ✏️ Update: Add --scenario-agent-override flag
│   └── run.py       # ✏️ Update: Pass flag to runner, discover global agent.md
├── core/
│   ├── discovery.py # ✏️ Update: Add find_global_agent_instructions()
│   ├── executor.py  # ✅ No changes needed (already accepts extend_system_message)
│   ├── parser.py    # ✏️ Update: Read scenario-level agent.md
│   ├── retry.py     # ✅ No changes
│   └── runner.py    # ✏️ Update: Build combined system message
├── formatters/      # ✅ No changes
├── logging/         # ✅ No changes
├── models/
│   ├── result.py    # ✅ No changes
│   ├── step.py      # ✅ No changes
│   └── suite.py     # ✏️ Update: Add agent_instructions field to TestSuite
└── utils/
    ├── browser.py   # ✅ No changes (already supports extend_system_message)
    ├── dotenv.py    # ✅ No changes
    ├── env.py       # ✅ No changes
    └── interpolation.py  # ✅ No changes

tests/
├── contract/        # ✏️ Add: Test CLI accepts --scenario-agent-override
├── integration/     # ✏️ Add: Test agent.md combinations
└── unit/            # ✏️ Add: Test prompt building, file reading

examples/
├── basic-login/     # ✏️ Optional: Add example agent.md
└── e-commerce/      # ✏️ Optional: Add example agent.md
```

**Files to Modify**: 5 files
**New Functions/Methods**: ~6 functions
**New Tests**: ~15 tests

**Structure Decision**: This is a feature addition to the existing single Python CLI application. The implementation touches parsing, models, runner, and CLI layers but doesn't require architectural changes. File reading follows existing patterns (similar to .env file loading).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - this section is not applicable.

## Implementation Phases

### Phase 0: Research ✅

**Objective**: Resolve any technical unknowns and establish implementation patterns.

**Research Areas**:
1. File encoding handling strategy (UTF-8 with fallback)
2. Error handling patterns for missing/malformed files
3. System message combination order (fast mode vs agent instructions)
4. Global agent.md discovery strategy (from familiar root)

**Output**: research.md with decisions documented

### Phase 1: Design ✅

**Objective**: Create detailed design artifacts and contracts.

**Artifacts**:
1. **data-model.md**: Document TestSuite model changes
2. **contracts/prompt-building.md**: Document prompt building function contract
3. **contracts/cli-interface.md**: Document new --scenario-agent-override flag
4. **quickstart.md**: Implementation guide with examples

**Output**: Complete design documentation

### Phase 2: Implementation (Generated by /speckit.tasks)

**Will include**:
- Update models (TestSuite)
- Update parser (read agent.md)
- Update runner (build system message)
- Update CLI (add flag)
- Add comprehensive tests
- Update documentation

## Dependencies & Sequencing

**External Dependencies**: None (uses only standard library for file reading)

**Internal Dependencies**:
- Parser must be updated before runner (runner needs parsed data)
- TestSuite model must be updated before parser (parser stores data in model)
- CLI updates can be done independently

**Execution Order**:
1. Model updates (add field)
2. Parser updates (read files, store in model)
3. Runner updates (build system message)
4. CLI updates (add flag, discover global agent.md)
5. Tests (unit → integration → contract)
6. Documentation updates

## Risk Assessment

**Low Risk**:
- ✅ Completely optional feature (backward compatible)
- ✅ No external dependencies
- ✅ Simple file reading operations
- ✅ Existing system message mechanism already in place

**Medium Risk**:
- ⚠️ File encoding issues (mitigated by UTF-8 + fallback strategy)
- ⚠️ Large agent.md files (mitigated by reasonable size limits)

**Mitigation Strategies**:
- Extensive error handling for file operations
- Clear warning messages for issues
- Documentation of best practices for agent.md size
- Integration tests for all file scenarios

## Success Metrics

- ✅ All 8 Constitution principles satisfied
- ✅ Zero breaking changes to existing API
- ✅ 100% test coverage for new code
- ✅ All edge cases handled gracefully
- ✅ Clear documentation with examples
- ✅ Feature working with fast mode
- ✅ Feature working with override flag
