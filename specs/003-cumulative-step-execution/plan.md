# Implementation Plan: Cumulative Step Execution & Session Persistence

**Branch**: `003-cumulative-step-execution` | **Date**: 2025-11-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-cumulative-step-execution/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement explicit step file ordering based on numeric prefixes (00-, 01-, etc.) with automatic skipping of non-prefixed files, and change browser session management so each scenario uses a single persistent browser session across all steps instead of creating/destroying sessions per step. This enables true cumulative end-to-end testing workflows like login → navigate → interact.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: browser-use (Agent, Browser), pydantic, asyncio  
**Storage**: N/A (test execution, no persistence)  
**Testing**: pytest with pytest-asyncio  
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)  
**Project Type**: Single project (CLI tool)  
**Performance Goals**: No regression in test execution time; session reuse should improve performance  
**Constraints**: Must maintain browser state across steps; each scenario must be isolated  
**Scale/Scope**: 5 core files modified (discovery, parser, executor, runner, logging)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitutional Alignment

✅ **Easy to Change**: Changes are localized to specific classes (discovery, parser, executor, runner). Each has clear responsibilities that don't bleed into others.

✅ **Small, Single Purpose Classes**: 
- Discovery: Responsible for finding and ordering step files
- Parser: Validates step file format and prefixes  
- Executor: Executes steps using provided browser
- Runner: Manages scenario lifecycle and browser session

✅ **Stable, Minimal Public Interfaces**: 
- Public APIs remain stable (familiar run, familiar discover commands unchanged)
- Internal refactoring only (executor receives browser instead of creating it)
- No breaking changes to CLI interface

✅ **Polymorphism Over Conditionals**: 
- Step filtering uses clear predicate functions (is_numbered_step, is_skipped_file)
- No complex conditional trees; each concern handled separately

✅ **Behavior-Based Testing**: 
- Tests will verify ordering behavior (steps run in sequence)
- Tests will verify session persistence (browser state carries forward)
- Tests won't care how internally the browser is passed around

✅ **Code as User Interface**: 
- Step file naming convention is explicit and human-friendly (00-, 01-, 02-)
- Verbose logging makes behavior transparent
- Error messages guide users to fix issues

✅ **Humane Code**: 
- Numeric prefixes are intuitive and widely used (like migration files)
- Skipping logic is explicit and predictable
- Session persistence matches user mental model (one test = one browser)

✅ **Test-Driven Development**: 
- Can write tests first for ordering logic
- Can write tests for session persistence
- Existing tests will validate no regression

**Gate Result**: ✅ PASS - Enhancement aligns with all constitutional principles and improves code clarity.

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
src/familiar/
├── core/
│   ├── discovery.py        # MODIFY: Add step ordering & filtering
│   ├── parser.py           # MODIFY: Validate numeric prefixes
│   ├── executor.py         # MODIFY: Receive browser instead of creating
│   └── runner.py           # MODIFY: Create browser once per scenario
├── logging/
│   └── setup.py            # MODIFY: Add skipped file logging
├── models/
│   ├── step.py             # READ: Understand step model
│   └── suite.py            # READ: Understand suite model
└── utils/
    └── browser.py          # READ: Browser creation logic

tests/
├── unit/
│   ├── test_discovery.py   # UPDATE: Test step ordering
│   ├── test_parser.py      # UPDATE: Test prefix validation
│   └── test_executor.py    # NEW: Test session persistence
├── integration/
│   └── test_runner.py      # UPDATE: Test cumulative execution
└── fixtures/
    └── sample-suite/       # UPDATE: Add numeric prefixes to steps
        ├── 00-step-one.md  # RENAME from step files
        ├── 01-step-two.md
        └── suite.yaml

examples/
├── basic-login/            # UPDATE: Add numeric prefixes
│   ├── 00-navigate.md
│   ├── 01-enter-credentials.md
│   ├── 02-submit-login.md
│   └── 03-verify-logged-in.md
└── e-commerce/             # UPDATE: Add numeric prefixes
    ├── 00-homepage.md
    ├── 01-search-product.md
    ├── 02-select-product.md
    └── ...
```

**Structure Decision**: Single project structure. Core changes localized to 5 files in `src/familiar/core/` and `src/familiar/logging/`. Tests updated to verify new behavior. Example scenarios updated with numeric prefixes.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations. Changes enhance existing architecture without adding unnecessary complexity.
