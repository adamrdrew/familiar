# Implementation Plan: GitHub Actions PR Checks

**Branch**: `005-github-actions-pr-checks` | **Date**: 2025-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-github-actions-pr-checks/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add GitHub Actions CI/CD workflow to automatically run Familiar's Python test suite (unit + integration tests) on all pull requests. Tests will run on Python 3.11, 3.12, and 3.13 using a matrix strategy, with dependency caching for performance. This provides immediate feedback to contributors and prevents merging PRs with failing tests.

**Technical Approach**: Create `.github/workflows/pr-checks.yml` using GitHub Actions with `setup-python`, `setup-uv`, and `cache` actions. Use `uv sync` for dependency installation and `uv run pytest` for test execution.

## Technical Context

**Language/Version**: Python 3.11+ (project supports 3.11, 3.12, 3.13)
**Primary Dependencies**: 
- GitHub Actions (CI/CD platform)
- `uv` (Python package installer and resolver)
- `pytest` (test framework, already in dev dependencies)
- `setup-python` action (GitHub Actions marketplace)
- `setup-uv` action (astral-sh official action)
- `cache` action (GitHub Actions built-in)

**Storage**: N/A (CI workflow configuration only)
**Testing**: pytest with `uv run pytest tests/ -v --strict-markers`
**Target Platform**: GitHub Actions runners (ubuntu-latest, Linux x86_64)
**Project Type**: CI/CD configuration (single YAML file)
**Performance Goals**: 
- Workflow completes in <5 minutes with warm cache
- <3 minutes ideal with cached dependencies
- Parallel execution across Python versions using matrix

**Constraints**: 
- Must use `uv` (not pip) for dependency management (project standard)
- Must respect `uv.lock` for reproducible builds
- Must not require LLM API keys (unit tests only)
- Must work on GitHub-hosted runners (no self-hosted)
- Must be free tier compatible (public repo)

**Scale/Scope**: 
- Single workflow file (`.github/workflows/pr-checks.yml`)
- ~50-70 lines of YAML configuration
- 3 Python versions in matrix (3.11, 3.12, 3.13)
- Current test suite: 82 tests (~4 seconds local runtime)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Status: ✅ PASS

This feature adds CI/CD infrastructure configuration, not application code. Most constitution principles apply to code design rather than configuration files. However, relevant principles are satisfied:

**✅ I. Easy to Change**
- Single YAML file with clear structure
- Standard GitHub Actions syntax (no custom scripts)
- Modular steps that can be added/removed independently

**✅ II. Small, Single Purpose**
- Workflow has one clear purpose: run tests on PRs
- Each step does one thing (checkout, setup Python, install deps, run tests)
- No mixed responsibilities

**✅ VI. Code as User Interface** (Configuration as User Interface)
- Uses descriptive step names
- Follows GitHub Actions best practices and conventions
- Includes comments explaining key decisions

**✅ VII. Humane Configuration**
- Clear, explicit configuration (no hidden behavior)
- Familiar syntax (standard GitHub Actions patterns)
- Well-documented with inline comments

**N/A**: Principles III (Public Interfaces), IV (Polymorphism), V (Behavior Testing), VIII (TDD) do not apply to infrastructure configuration files.

**Complexity Assessment**: No violations. This is a straightforward configuration file with no unconventional patterns or excessive abstraction.

## Project Structure

### Documentation (this feature)

```text
specs/005-github-actions-pr-checks/
├── spec.md              # Feature specification (created)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (workflow structure)
├── quickstart.md        # Phase 1 output (setup guide)
└── contracts/           # Phase 1 output (workflow schema/examples)
    └── pr-checks.yml    # Example workflow contract
```

### Files Modified/Created

**New Files**:
```text
.github/
└── workflows/
    └── pr-checks.yml    # Main CI workflow (NEW - primary deliverable)
```

**Modified Files**:
```text
CONTRIBUTING.md          # Add section on CI/CD checks
README.md                # Update badges section (optional)
```

**Existing Structure (unchanged)**:
```text
src/familiar/            # Application code (no changes)
tests/                   # Test suite (no changes)
├── unit/                # Unit tests (already exist)
├── integration/         # Integration tests (already exist)
└── contract/            # Contract tests (already exist)
```

**Structure Decision**: This feature adds CI/CD infrastructure without modifying the existing Python codebase. The single workflow file `.github/workflows/pr-checks.yml` is the primary deliverable. Documentation updates in CONTRIBUTING.md are secondary.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - Constitution check passed with no complexity concerns.
