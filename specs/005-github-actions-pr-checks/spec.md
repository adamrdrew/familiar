# Feature Specification: GitHub Actions PR Checks

**Branch**: `005-github-actions-pr-checks` | **Date**: 2025-01-14

## Problem Statement

The Familiar repository currently has no automated continuous integration (CI) checks for pull requests. This means:

1. **No automated test validation**: Unit and integration tests must be run manually by reviewers
2. **Risk of broken code**: PRs can be merged without knowing if tests pass
3. **Slower review process**: Reviewers must manually run tests locally
4. **No consistent test environment**: Different developers may test on different Python versions or dependency versions

This increases the risk of regressions and slows down the development workflow.

## Goals

### Primary Goal
Set up GitHub Actions to automatically run the Python test suite (unit + integration tests) on all pull requests, providing immediate feedback to contributors.

### Secondary Goals
- Run tests on multiple Python versions (3.11, 3.12, 3.13)
- Cache dependencies for faster CI runs
- Provide clear pass/fail status checks on PRs
- Block merging if tests fail (branch protection rules)

## Non-Goals

- **NOT** running Familiar's AI-driven E2E tests in CI (those require LLM API keys and browser automation)
- **NOT** implementing deployment pipelines (out of scope)
- **NOT** adding code coverage reporting (can be added later)
- **NOT** adding linting/formatting checks (can be added separately)

## Requirements

### Functional Requirements

**FR1**: GitHub Actions workflow MUST run on pull request events
- Trigger on: `pull_request` (opened, synchronize, reopened)
- Target branches: `main`, `master` (check current default branch)

**FR2**: Tests MUST run on multiple Python versions
- Minimum: Python 3.11 (project requirement)
- Recommended: 3.11, 3.12, 3.13 (current stable versions)
- Use matrix strategy for parallel execution

**FR3**: Workflow MUST install dependencies using `uv`
- Familiar uses `uv` for dependency management
- Install `uv` from official installer
- Run `uv sync` to install dependencies (respects `uv.lock`)

**FR4**: Workflow MUST run pytest with appropriate options
- Run: `uv run pytest tests/`
- Include verbose output: `-v`
- Optionally: `--strict-markers` to catch typos

**FR5**: Workflow MUST report clear pass/fail status
- GitHub check shows green checkmark on success
- Shows red X on failure with test output
- Status visible on PR page

**FR6**: Workflow MUST be reasonably fast
- Cache `uv` dependencies between runs
- Use GitHub Actions cache for `.venv/`
- Target: <3 minutes for typical run

### Non-Functional Requirements

**NFR1**: **Reliability**: Tests must run in isolated, reproducible environment
- Use clean Ubuntu runner
- No dependency on external services (no LLM APIs required for unit tests)

**NFR2**: **Maintainability**: Workflow configuration must be clear and documented
- Use official actions where possible
- Add comments explaining key steps
- Follow GitHub Actions best practices

**NFR3**: **Cost-efficiency**: Minimize CI minutes usage
- Use GitHub-hosted runners (free for public repos)
- Cache dependencies aggressively
- Skip unnecessary steps

**NFR4**: **Security**: No secrets or API keys exposed
- Unit tests don't require LLM API keys
- No sensitive data in workflow logs

## User Stories

**US1**: As a **contributor**, I want immediate feedback on whether my PR breaks tests, so I can fix issues before requesting review.

**US2**: As a **maintainer**, I want automated test validation on PRs, so I don't have to manually run tests for every contribution.

**US3**: As a **maintainer**, I want to prevent merging PRs with failing tests, so the main branch stays stable.

**US4**: As a **contributor**, I want fast CI runs (<3 min), so I can iterate quickly on my changes.

## Acceptance Criteria

**AC1**: GitHub Actions workflow file exists at `.github/workflows/pr-checks.yml`

**AC2**: Workflow runs automatically when PR is opened/updated

**AC3**: Tests execute successfully on Python 3.11, 3.12, and 3.13

**AC4**: PR page shows check status (✅ or ❌) for each Python version

**AC5**: Workflow completes in <5 minutes for typical PR (with warm cache)

**AC6**: Failing tests cause workflow to fail and block merge (when branch protection enabled)

**AC7**: Workflow logs show clear test output and failure reasons

## Technical Approach

### GitHub Actions Workflow

```yaml
name: PR Checks

on:
  pull_request:
    branches: [main, master]

jobs:
  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
      fail-fast: false  # Run all versions even if one fails
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('uv.lock') }}
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run tests
        run: uv run pytest tests/ -v --strict-markers
```

### Implementation Steps

1. Create `.github/workflows/` directory
2. Add `pr-checks.yml` workflow file
3. Test workflow on a draft PR
4. Document workflow in CONTRIBUTING.md
5. Enable branch protection rules (recommended, not required)

## Dependencies

- **GitHub Actions**: Free for public repositories
- **Python 3.11+**: Already required by project
- **uv**: Already used for dependency management
- **pytest**: Already in dev dependencies

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Slow CI runs (>5 min) | Frustrates contributors | Cache dependencies, use matrix for parallel runs |
| Flaky tests | False negatives block PRs | Ensure unit tests are deterministic (no LLM calls) |
| Python version incompatibility | Tests fail on new Python | Test on multiple versions in matrix |
| Workflow configuration errors | CI doesn't run | Test on draft PR first |

## Future Enhancements

- Add code coverage reporting (codecov.io)
- Add linting checks (ruff, mypy)
- Add security scanning (bandit, safety)
- Add docs build validation
- Add performance regression tests

## References

- GitHub Actions documentation: https://docs.github.com/en/actions
- `setup-python` action: https://github.com/actions/setup-python
- `setup-uv` action: https://github.com/astral-sh/setup-uv
- pytest documentation: https://docs.pytest.org/

