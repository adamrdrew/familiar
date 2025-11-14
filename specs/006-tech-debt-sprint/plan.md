# Implementation Plan: Tech Debt Sprint - Code Quality & Test Coverage

**Branch**: `006-tech-debt-sprint` | **Date**: 2025-11-14 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/006-tech-debt-sprint/spec.md`  
**Status**: ✅ Phase 0-1 Complete (Planning & Design)

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Comprehensive technical debt remediation sprint to audit and clean the codebase before new feature development. This includes removing all dead/unused code, ensuring 100% test coverage of public APIs, validating documentation accuracy, and confirming Constitution compliance throughout the codebase.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: browser-use>=0.9.5, click>=8.1.0, pydantic>=2.0.0, pyyaml>=6.0, rich>=13.0.0, python-dotenv>=1.0.0  
**Storage**: File system (markdown test files, YAML configs)  
**Testing**: pytest>=7.4.0, pytest-asyncio>=0.21.0, pytest-cov>=4.1.0  
**Target Platform**: macOS, Linux, Windows (Python 3.11+ environments)  
**Project Type**: Single Python CLI application with library components  
**Performance Goals**: N/A (refactoring sprint - maintain current performance)  
**Constraints**: Zero breaking changes to public API, all tests must pass, backward compatibility required  
**Scale/Scope**: ~2,500 lines of source code, 20 modules, 9 test files, 43 tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Easy to Change
- **Pass**: Dependency injection in place (browser/LLM passed to executor)
- **Pass**: Single responsibility maintained across modules
- **Pass**: Public CLI interface stable
- **⚠️ Action Required**: Some unused utility functions need removal for clarity

### ✅ II. Small, Single Purpose Classes
- **Pass**: Most classes under 7 public methods
- **⚠️ Concern**: TextFormatter has 11 methods (but 7 are private helpers for formatting)
- **Pass**: StepExecutor (3 methods), SuiteRunner (1 public), Parser (3 methods)
- **✅ Action Required**: Verify all methods serve single purpose

### ✅ III. Stable, Minimal Public Interfaces
- **Pass**: CLI interface is stable and minimal
- **Pass**: Internal APIs are minimal
- **⚠️ Action Required**: Some unused public functions need removal (create_browser_use_agent, etc.)
- **Pass**: Dependencies explicit in constructors

### ✅ IV. Polymorphism Over Conditionals
- **Pass**: RetryPolicy uses protocol/interface pattern
- **Pass**: Formatters use strategy pattern
- **Pass**: LLM provider selection via factory pattern
- **Pass**: No problematic conditionals found

### ✅ V. Behavior-Based Testing
- **Pass**: Tests validate CLI behavior and outcomes
- **Pass**: Integration tests use real test suites
- **Pass**: Contract tests verify schema compliance
- **⚠️ Action Required**: Verify 100% public API coverage

### ✅ VI. Code as User Interface
- **Pass**: Clear, descriptive naming throughout
- **Pass**: Native string operations used
- **Pass**: Standard Python idioms
- **✅ Action Required**: Review for any clever code vs. clear code

### ✅ VII. Humane Code
- **Pass**: Descriptive function/class names
- **Pass**: Explicit behavior (retry counts in signatures)
- **Pass**: Minimal abstractions
- **⚠️ Action Required**: Some unused code adds cognitive load (needs removal)

### ✅ VIII. Test-Driven Development
- **Pass**: Contract tests written first
- **Pass**: Good test coverage exists
- **⚠️ Action Required**: Verify 100% public API coverage, add missing tests

### Summary
**Overall**: ✅ PASS with minor cleanup required  
**Gate Status**: Proceed to Phase 0  
**Required Actions**: Remove dead code, verify test coverage, validate method purposes

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

**Current Structure** (Single Python CLI Project):

```text
src/familiar/
├── __init__.py
├── __main__.py
├── cli/              # CLI interface
│   ├── main.py      # Entry point, click commands
│   └── run.py       # Run command implementation
├── core/            # Core business logic
│   ├── discovery.py # Suite discovery
│   ├── executor.py  # Step execution (browser-use integration)
│   ├── parser.py    # Suite/step parsing
│   ├── retry.py     # Retry policies
│   └── runner.py    # Suite orchestration
├── formatters/      # Output formatters
│   ├── json.py     # JSON formatter
│   └── text.py     # Rich text formatter
├── logging/         # Logging setup
│   ├── handlers.py # Rich log handlers
│   └── setup.py    # Logging configuration
├── models/          # Data models
│   ├── result.py   # Test results
│   ├── step.py     # Test steps
│   └── suite.py    # Test suites
└── utils/           # Utilities
    ├── browser.py   # Browser-use/LLM creation
    ├── dotenv.py    # .env file loading
    ├── env.py       # Environment utilities
    └── interpolation.py # Variable interpolation

tests/
├── contract/        # Contract/API tests
│   └── test_cli_interface.py
├── integration/     # Integration tests
│   ├── test_cli.py
│   ├── test_cli_dotenv.py
│   ├── test_multi_suite.py
│   ├── test_retry.py
│   └── test_runner.py
├── unit/            # Unit tests
│   ├── test_discovery.py
│   ├── test_dotenv.py
│   ├── test_models.py
│   ├── test_parser.py
│   ├── test_retry.py
│   └── test_utils.py
└── fixtures/        # Test fixtures
    └── sample-suite/

docs/
├── configuration.md
└── images/

examples/
├── basic-login/
├── e-commerce/
└── api-testing/
```

**Structure Decision**: This is a single Python CLI application. The structure follows standard Python package conventions with clear separation of concerns: CLI interface, core logic, models, formatters, utilities, and comprehensive test coverage.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| TextFormatter: 11 methods (7 limit) | Formatting requires multiple private helpers (_format_header, _format_table, etc.) | Splitting into multiple formatters would duplicate console/rich setup and make formatting inconsistent |

**Note**: The TextFormatter has 11 total methods but only 2-3 are public (`format()`, `print()`). The remaining 8 are private helpers for formatting different output sections. This is acceptable under Constitution as these are internal implementation details, not public API surface.
