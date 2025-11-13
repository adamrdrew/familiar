# Implementation Plan: AI-Driven End-to-End Testing Platform

**Branch**: `001-ai-e2e-testing` | **Date**: 2025-11-13 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-ai-e2e-testing/spec.md`

**Note**: This plan is filled in by the `/speckit.plan` command. See `.cursor/commands/speckit.plan.md` for the execution workflow.

## Summary

Familiar is a CLI tool that enables natural language-based end-to-end testing for web applications. Built on top of the browser-use library, it provides an opinionated test suite structure, robust retry mechanisms, comprehensive logging, and CI/CD integration. Users write test steps in Markdown with natural language instructions, organize them into YAML-configured suites, and execute them via a Python CLI that orchestrates browser-use agents.

**Technical Approach**: Python 3.11 CLI application using browser-use for browser automation, Click for CLI framework, PyYAML for configuration parsing, and structured logging. Package distribution via PyPI/uv with optional Homebrew support.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: browser-use (Playwright-based browser automation), Click (CLI framework), PyYAML (config parsing), rich (terminal UI), pydantic (config validation)  
**Storage**: File-based (Markdown test steps, YAML suite configs, JSON/JUnit XML results output)  
**Testing**: pytest (unit/integration tests), pytest-asyncio (async test support)  
**Target Platform**: macOS, Linux, Windows (anywhere Python 3.11+ and Chromium run)  
**Project Type**: Single Python CLI application with library components  
**Performance Goals**: Test execution within 2x manual workflow speed, sub-second test discovery, minimal CLI startup overhead (<500ms)  
**Constraints**: Async/await throughout (browser-use is async), environment variable-driven config (no config files required), graceful handling of browser crashes and network issues  
**Scale/Scope**: Support test suites with 100+ steps, parallel suite execution (future), handle tests running for 30+ minutes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Easy to Change

- **Pass**: Configuration via dependency injection (browser-use clients, loggers, file loaders injected into runners)
- **Pass**: Single responsibility classes (TestSuiteDiscovery, StepExecutor, ResultFormatter are separate)
- **Pass**: Stable public APIs (CLI commands stable, internal step execution can evolve)
- **Pass**: Loose coupling (suite runner depends on abstract StepExecutor interface, not concrete browser-use details)

### ✅ II. Small, Single Purpose Classes

- **Pass**: TestSuiteDiscovery - only discovers suites
- **Pass**: StepParser - only parses markdown steps
- **Pass**: StepExecutor - only executes single steps via browser-use
- **Pass**: SuiteRunner - only orchestrates step execution with retries
- **Pass**: ResultFormatter - only formats results to different output formats
- **Design Checkpoint**: Verify classes stay under 7 public methods during Phase 1

### ✅ III. Stable, Minimal Public Interfaces

- **Pass**: CLI interface is the public API (commands: `run`, `discover`, `validate`)
- **Pass**: Internal Python API minimal (SuiteRunner.run(), StepExecutor.execute())
- **Pass**: Dependencies explicit (SuiteConfig passed to SuiteRunner constructor)
- **Design Checkpoint**: Document public API contracts in Phase 1

### ✅ IV. Polymorphism Over Conditionals

- **Pass**: Different output formats via OutputFormatter strategy pattern (JUnitFormatter, JSONFormatter, TextFormatter)
- **Pass**: Retry strategies via RetryPolicy interface (FixedRetry, BestOfN, ExponentialBackoff)
- **Pass**: Step inclusion via StepResolver interface (LocalStepResolver, SharedStepResolver)
- **Design Checkpoint**: Ensure no format/type conditionals in core logic during Phase 1

### ✅ V. Behavior-Based Testing

- **Pass**: Tests validate CLI output and exit codes, not internal state
- **Pass**: Integration tests execute real test suites and verify results
- **Pass**: Contract tests ensure suite YAML schema is honored
- **Design Checkpoint**: Write behavior tests first in Phase 2 (before implementation)

### ✅ VI. Code as User Interface

- **Pass**: Clear naming (TestSuiteDiscovery, not TSDiscover)
- **Pass**: Native string operations for markdown parsing (no complex regex unless needed)
- **Pass**: Standard Python idioms (pathlib for paths, dataclasses for configs)
- **Design Checkpoint**: Code review for readability before each PR

### ✅ VII. Humane Code

- **Pass**: Descriptive names (discover_suites(), execute_step_with_retry())
- **Pass**: Explicit behavior (retry count in method signature, not hidden in config)
- **Pass**: Minimal abstractions (direct browser-use API usage, no unnecessary wrappers)
- **Design Checkpoint**: Prefer explicit parameters over magic config during implementation

### ✅ VIII. Test-Driven Development

- **Pass**: CLI behavior tests written first (test command parsing, exit codes)
- **Pass**: Suite discovery tests before implementation (test file finding logic)
- **Pass**: Step execution tests with mocked browser-use (test retry logic)
- **Design Checkpoint**: Red-Green-Refactor cycle enforced in Phase 2

### Constitution Compliance: ✅ ALL GATES PASS

No complexity justifications needed. Design aligns with all 8 core principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-e2e-testing/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── suite-schema.yaml    # YAML schema for suite configuration
│   ├── step-format.md       # Markdown step format specification
│   └── cli-interface.md     # CLI command contracts
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code (repository root)

```text
familiar/
├── pyproject.toml           # uv project config, dependencies, entry points
├── README.md                # Project overview, installation, quickstart
├── .python-version          # Python 3.11 pin for uv
├── uv.lock                  # Locked dependencies
├── .env.example             # Example environment variables
├── src/
│   └── familiar/
│       ├── __init__.py
│       ├── __main__.py      # Entry point for python -m familiar
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py      # Click CLI app with commands
│       │   ├── run.py       # 'familiar run' command
│       │   ├── discover.py  # 'familiar discover' command
│       │   └── validate.py  # 'familiar validate' command
│       ├── core/
│       │   ├── __init__.py
│       │   ├── discovery.py    # TestSuiteDiscovery class
│       │   ├── parser.py       # StepParser, SuiteConfigParser
│       │   ├── executor.py     # StepExecutor (browser-use wrapper)
│       │   ├── runner.py       # SuiteRunner (orchestrates execution)
│       │   └── retry.py        # RetryPolicy interfaces and implementations
│       ├── models/
│       │   ├── __init__.py
│       │   ├── suite.py        # TestSuite, SuiteConfig dataclasses
│       │   ├── step.py         # TestStep, StepResult dataclasses
│       │   └── result.py       # TestResult, SuiteResult dataclasses
│       ├── formatters/
│       │   ├── __init__.py
│       │   ├── base.py         # OutputFormatter interface
│       │   ├── junit.py        # JUnitFormatter
│       │   ├── json.py         # JSONFormatter
│       │   └── text.py         # TextFormatter
│       ├── logging/
│       │   ├── __init__.py
│       │   ├── setup.py        # Logging configuration
│       │   └── handlers.py     # Custom log handlers (file, console)
│       └── utils/
│           ├── __init__.py
│           ├── env.py          # Environment variable parsing
│           ├── interpolation.py # Variable interpolation for steps
│           └── browser.py      # Browser-use client setup helpers
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/
│   │   ├── test_discovery.py   # TestSuiteDiscovery tests
│   │   ├── test_parser.py      # Parser tests
│   │   ├── test_retry.py       # Retry policy tests
│   │   └── test_formatters.py  # Output formatter tests
│   ├── integration/
│   │   ├── test_runner.py      # End-to-end suite execution
│   │   ├── test_cli.py         # CLI command integration
│   │   └── test_browser_use.py # Browser-use integration
│   ├── contract/
│   │   ├── test_suite_schema.py # YAML schema validation
│   │   └── test_cli_interface.py # CLI contract tests
│   └── fixtures/
│       ├── sample-suite/       # Example test suite for testing
│       │   ├── suite.yaml
│       │   ├── 00-login.md
│       │   └── 01-dashboard.md
│       └── shared/
│           └── steps/
│               └── common-login.md
└── docs/
    ├── getting-started.md
    ├── test-suite-format.md
    ├── configuration.md
    └── ci-integration.md
```

**Structure Decision**: Single Python project (Option 1) with standard src-layout for proper packaging. This structure enables:
- Clean separation of concerns (CLI, core logic, models, formatters)
- Easy unit testing (each module tested independently)
- pip/uv distribution (src-layout prevents import issues)
- Future extensibility (plugins can extend formatters, retry policies)

The src-layout ensures `familiar` is importable as a library while also working as a CLI tool via entry points defined in `pyproject.toml`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations - all gates passed. No complexity justification required.*
