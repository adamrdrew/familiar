# Implementation Plan: AI-Driven End-to-End Testing Platform

**Branch**: `001-ai-e2e-testing` | **Date**: 2025-11-13 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-ai-e2e-testing/spec.md`

**Note**: This plan reflects the architecture after Phase 3 (MVP) completion with clarifications on LLM provider support.

## Summary

Familiar is a CLI tool that enables natural language-based end-to-end testing for web applications. Built on top of browser-use, it provides an opinionated test suite structure, multi-provider LLM support, robust retry mechanisms, comprehensive logging, and CI/CD integration. Users write test steps in Markdown with natural language instructions, organize them into YAML-configured suites, and execute them via a Python CLI that orchestrates browser-use agents.

**Technical Approach**: Python 3.11 CLI application using browser-use's native model classes for multi-provider LLM support (OpenAI, Anthropic, Gemini, Azure, Groq, Ollama, etc.), Click for CLI framework, PyYAML for configuration parsing, and structured logging. Package distribution via PyPI/uv with optional Homebrew support.

**Important**: browser-use manages Chrome/Chromium installation and browser lifecycle via Playwright - we do NOT implement any browser control ourselves. browser-use also provides native LLM integrations - we do NOT use langchain directly or implement our own LLM connections.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: browser-use (Playwright-based browser automation with multi-provider LLM support), Click (CLI framework), PyYAML (config parsing), rich (terminal UI), pydantic (config validation)  
**Storage**: File-based (Markdown test steps, YAML suite configs, JSON/JUnit XML results output)  
**Testing**: pytest (unit/integration tests), pytest-asyncio (async test support)  
**Target Platform**: macOS, Linux, Windows (anywhere Python 3.11+ and Chromium run)  
**Project Type**: Single Python CLI application with library components  
**Performance Goals**: Test execution within 2x manual workflow speed, sub-second test discovery, minimal CLI startup overhead (<500ms)  
**Constraints**: Async/await throughout (browser-use is async), environment variable-driven config (no config files required), graceful handling of browser crashes and network issues  
**Scale/Scope**: Support test suites with 100+ steps, parallel suite execution (future), handle tests running for 30+ minutes

**LLM Provider Support**: Use browser-use's native model classes (`ChatOpenAI`, `ChatAnthropic`, `ChatGoogle`, `ChatGroq`, `ChatOllama`, `ChatBrowserUse`, etc.) to support 15+ providers. Selection via `FAMILIAR_MODEL_PROVIDER` env var, configuration via browser-use's standard env vars (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.).

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
- **Pass**: LLM providers via factory pattern (returns appropriate ChatXXX class from browser-use)
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
- **Pass**: LLM provider selection is simple factory, not complex abstraction layer
- **Design Checkpoint**: Pair review all new modules for clarity

### ✅ VIII. Test-Driven Development

- **Pass**: Write contract tests first (CLI interface validation)
- **Pass**: Write integration tests before runner implementation
- **Pass**: Unit tests for each model and parser
- **Design Checkpoint**: No code merged without tests

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-e2e-testing/
├── spec.md              # Feature specification
├── plan.md              # This file (implementation plan)
├── research.md          # Technical decisions and research
├── data-model.md        # Entity definitions
├── quickstart.md        # Developer onboarding
├── contracts/           # API contracts and schemas
│   ├── cli-interface.md
│   ├── step-format.md
│   └── suite-schema.yaml
├── checklists/          # Quality validation
│   └── requirements.md
└── tasks.md             # Implementation task breakdown
```

### Source Code (repository root)

```text
src/familiar/
├── __init__.py
├── __main__.py          # Enable python -m familiar
├── cli/                 # Command-line interface
│   ├── __init__.py
│   ├── main.py          # Entry point, command group
│   └── run.py           # Run command implementation
├── core/                # Core business logic
│   ├── __init__.py
│   ├── discovery.py     # Test suite discovery
│   ├── parser.py        # YAML and Markdown parsing
│   ├── executor.py      # Step execution with browser-use
│   └── runner.py        # Suite orchestration
├── models/              # Data models
│   ├── __init__.py
│   ├── suite.py         # SuiteConfig, TestSuite
│   ├── step.py          # TestStep
│   └── result.py        # TestResult, SuiteResult, ResultStatus
├── utils/               # Utilities
│   ├── __init__.py
│   ├── env.py           # Environment variable helpers
│   ├── interpolation.py # Variable interpolation
│   └── browser.py       # LLM provider factory
├── logging/             # Logging configuration
│   ├── __init__.py
│   ├── setup.py         # Logging setup
│   └── handlers.py      # Rich console handlers
└── formatters/          # Output formatters
    ├── __init__.py
    ├── text.py          # Human-readable output
    ├── json.py          # (Future) JSON output
    └── junit.py         # (Future) JUnit XML output

tests/
├── conftest.py          # Pytest fixtures
├── contract/            # CLI contract tests
│   └── test_cli_interface.py
├── integration/         # End-to-end tests
│   ├── test_cli.py
│   └── test_runner.py
├── unit/                # Unit tests
│   ├── test_discovery.py
│   ├── test_models.py
│   ├── test_parser.py
│   └── test_utils.py
└── fixtures/            # Test fixtures
    └── sample-suite/
        ├── suite.yaml
        ├── 00-login.md
        └── 01-dashboard.md
```

**Structure Decision**: Single Python project using src-layout. This is the standard approach for Python CLI tools and ensures proper import behavior when installed. The `src/` directory prevents accidental imports from the repository root, and the structure separates concerns clearly: `cli` for interface, `core` for business logic, `models` for data, `utils` for helpers, and `formatters` for output.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations - all constitutional principles are satisfied by the current design.*
