# Research: GitHub Actions PR Checks

**Feature**: GitHub Actions PR Checks | **Date**: 2025-01-14

## Overview

Research findings for implementing GitHub Actions workflow to run Python test suite on pull requests. This document consolidates decisions on workflow configuration, caching strategies, Python version matrix, and best practices.

---

## Decision 1: Workflow Trigger Strategy

**Decision**: Use `pull_request` event with explicit branch targets

**Rationale**:
- `pull_request` triggers on opened, synchronized (new commits), and reopened events
- Prevents unnecessary runs on draft PRs if `types` filter is added later
- Explicit branch list (`main`, `master`) provides clarity and prevents surprises
- More efficient than `push` (only runs when PR is updated, not every commit to feature branch)

**Implementation**:
```yaml
on:
  pull_request:
    branches: [main, master]
```

**Alternatives Considered**:
- `push` event: Rejected because it runs on every commit, even before PR creation
- `pull_request_target`: Rejected due to security concerns (runs in context of base branch)
- Workflow dispatch: Not suitable for automated PR checks

**References**:
- https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request

---

## Decision 2: Python Version Matrix Strategy

**Decision**: Test on Python 3.11, 3.12, and 3.13 with `fail-fast: false`

**Rationale**:
- Familiar requires Python 3.11+ (per pyproject.toml)
- Testing on 3.12 and 3.13 ensures forward compatibility
- `fail-fast: false` allows all versions to run even if one fails (better visibility)
- Parallel execution reduces total CI time
- 3.13 is the latest stable Python version

**Implementation**:
```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
  fail-fast: false
```

**Alternatives Considered**:
- Only test on 3.11: Rejected because compatibility issues with newer versions would go undetected
- Include 3.10: Rejected because project minimum is 3.11
- `fail-fast: true`: Rejected because we want to see all failures, not just first one

**Performance Impact**: 3 jobs run in parallel, so total time ≈ single job time (not 3x)

---

## Decision 3: Dependency Management with `uv`

**Decision**: Use official `astral-sh/setup-uv` action with `uv sync`

**Rationale**:
- Familiar uses `uv` as standard package manager (not pip)
- Official action from Astral (uv maintainers) ensures best practices
- `uv sync` respects `uv.lock` for reproducible builds
- Much faster than pip (10-100x speedup for install)
- Handles virtual environment creation automatically

**Implementation**:
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4

- name: Install dependencies
  run: uv sync
```

**Alternatives Considered**:
- Manual curl install: Rejected in favor of official action (better caching, version management)
- Using pip: Rejected because project standard is uv, and uv.lock wouldn't be respected
- `uv pip install -r requirements.txt`: Rejected because we have pyproject.toml + uv.lock, not requirements.txt

**References**:
- https://github.com/astral-sh/setup-uv
- https://docs.astral.sh/uv/

---

## Decision 4: Dependency Caching Strategy

**Decision**: Cache `~/.cache/uv` keyed by OS + Python version + `uv.lock` hash

**Rationale**:
- `uv` stores downloaded packages in `~/.cache/uv`
- Keying on `uv.lock` hash ensures cache invalidates when dependencies change
- Including Python version prevents cross-version contamination
- GitHub Actions cache is free for public repos, limited to 10GB per repo
- Reduces dependency install time from ~30s to ~5s

**Implementation**:
```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('uv.lock') }}
    restore-keys: |
      uv-${{ runner.os }}-${{ matrix.python-version }}-
```

**Alternatives Considered**:
- Cache `.venv/`: Rejected because virtual envs are Python version-specific and harder to manage
- No caching: Rejected because it would waste CI minutes and slow down feedback
- Cache `uv` binary: Not needed because `setup-uv` action already handles this

**Performance Impact**: 
- First run (cold cache): ~30-40s for dependency install
- Subsequent runs (warm cache): ~5-10s for dependency install
- 75-85% time savings on cached runs

**References**:
- https://github.com/actions/cache
- https://docs.astral.sh/uv/concepts/cache/

---

## Decision 5: Test Execution Command

**Decision**: Use `uv run pytest tests/ -v --strict-markers`

**Rationale**:
- `uv run` ensures pytest runs in uv-managed environment (handles activation automatically)
- `tests/` targets all tests (unit, integration, contract)
- `-v` provides verbose output for debugging failures in CI
- `--strict-markers` catches typos in test markers (e.g., `@pytest.mark.slwo` instead of `slow`)
- No need for coverage in initial implementation (can add later)

**Implementation**:
```yaml
- name: Run tests
  run: uv run pytest tests/ -v --strict-markers
```

**Alternatives Considered**:
- `pytest tests/`: Rejected because we need `uv run` to activate environment
- Add `--cov`: Deferred to future enhancement (adds complexity, requires coverage reporting setup)
- Separate unit/integration jobs: Rejected for initial version (over-engineering), all tests run in <10s
- Add `--maxfail=3`: Rejected because we want to see all failures for diagnosis

**Test Suite Characteristics**:
- Current: 82 tests (66 unit, 16 integration)
- Runtime: ~4 seconds locally
- All tests are deterministic (no LLM calls, no network)
- Expected CI runtime: ~10-15 seconds (slightly slower than local due to I/O)

---

## Decision 6: GitHub Actions Runner Choice

**Decision**: Use `ubuntu-latest` (currently Ubuntu 22.04)

**Rationale**:
- Linux is the primary deployment target for Familiar
- `ubuntu-latest` is free for public repos (2,000 minutes/month on free tier)
- Fastest startup time among GitHub runners (~10s)
- Most Python packages have pre-built wheels for Linux
- Familiar doesn't have OS-specific code

**Implementation**:
```yaml
runs-on: ubuntu-latest
```

**Alternatives Considered**:
- Matrix with multiple OSes (ubuntu, macos, windows): Rejected because:
  - Familiar is primarily used on Linux/Mac
  - Would triple CI time and cost
  - Python code is OS-agnostic (no platform-specific functionality)
  - Can add OS matrix later if needed
- Self-hosted runner: Rejected due to maintenance overhead and security concerns

**Cost Analysis** (for future reference):
- Public repos: Free (2,000 minutes/month)
- Private repos: $0.008/minute for Linux runners
- Estimated usage: ~3 min/PR × ~10 PRs/week = 120 min/month (well within free tier)

---

## Decision 7: Workflow Naming and Job Structure

**Decision**: Single workflow named "PR Checks" with single job named "Test"

**Rationale**:
- Single workflow keeps configuration simple and maintainable
- Single job reduces complexity (no inter-job dependencies)
- Matrix strategy provides parallelism without multiple jobs
- Clear naming: "PR Checks" appears in GitHub UI, "Test (Python X.Y)" for each matrix job

**Implementation**:
```yaml
name: PR Checks

jobs:
  test:
    name: Test (Python ${{ matrix.python-version }})
```

**Alternatives Considered**:
- Separate jobs for unit/integration: Rejected because test suite is small and fast
- Separate workflows for lint/test/build: Deferred to future (start simple)
- Name "CI": Rejected because "PR Checks" is more descriptive

**Future Expansion Path**:
- Add `lint` job when adding ruff/mypy checks
- Add `docs` job when adding documentation builds
- Keep as single workflow or split based on run frequency

---

## Decision 8: Branch Protection Rules (Recommended, Not Required)

**Decision**: Document branch protection setup in quickstart, but don't enforce in code

**Rationale**:
- Branch protection is a repository setting, not code
- Requires admin permissions to configure
- Workflow will run automatically, but protection rules must be enabled manually
- Best practice for production repos, but not strictly necessary for initial setup

**Recommended Settings**:
```
Settings → Branches → Branch protection rules for `main`:
- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - ✅ Status checks required: "Test (Python 3.11)", "Test (Python 3.12)", "Test (Python 3.13)"
- ✅ Require conversation resolution before merging (optional)
```

**Implementation Scope**: Document in quickstart.md, not enforced by this PR

---

## Decision 9: Error Handling and Failure Modes

**Decision**: Let pytest handle test failures naturally, no custom error handling

**Rationale**:
- pytest already provides excellent failure reporting
- GitHub Actions automatically captures exit codes (0 = success, non-zero = failure)
- Verbose mode (`-v`) provides sufficient detail for debugging
- No need for custom retry logic (unit tests are deterministic)

**Failure Scenarios**:
1. **Test failures**: pytest fails → workflow fails → PR shows red X
2. **Dependency install failures**: uv sync fails → workflow fails → clear error in logs
3. **Python version not available**: setup-python fails → workflow fails (unlikely with official action)
4. **Workflow syntax errors**: GitHub validates YAML → warns before commit

**No Custom Handling Needed**: GitHub Actions and pytest provide sufficient error reporting out of the box.

---

## Decision 10: Performance Optimization Strategy

**Decision**: Implement caching from day 1, defer other optimizations

**Rationale**:
- Caching provides 75-85% speedup with minimal complexity
- Other optimizations have diminishing returns:
  - Pytest-xdist (parallel tests): Only useful for large test suites (we have 82 tests @ 4s)
  - Conditional test runs (only changed files): Complex to implement correctly, low value
  - Custom Docker images: Maintenance overhead not justified

**Performance Targets**:
- Cold cache (first run): <3 minutes total
- Warm cache (typical run): <2 minutes total
- Acceptable: <5 minutes (PR reviewers wait for feedback)

**Optimization Roadmap** (future):
1. ✅ Dependency caching (implemented)
2. ⏸️ Pytest-xdist: When test suite exceeds 100 tests or >30s runtime
3. ⏸️ Changed-file detection: When test suite exceeds 500 tests
4. ⏸️ Custom Docker image: When dependency install exceeds 2 minutes with cache

---

## Best Practices Summary

### GitHub Actions Best Practices

1. **Use official actions**: Prefer marketplace actions from trusted publishers (actions/, astral-sh/)
2. **Pin action versions**: Use `@v4` instead of `@main` for stability
3. **Minimize secrets**: Unit tests don't need LLM API keys (by design)
4. **Cache aggressively**: GitHub provides 10GB cache for free
5. **Fail fast when appropriate**: We use `fail-fast: false` to see all Python version failures
6. **Use descriptive names**: Job names appear in PR UI, make them clear

### Python Testing Best Practices in CI

1. **Test multiple versions**: Familiar supports 3.11+, so test 3.11, 3.12, 3.13
2. **Use lock files**: `uv.lock` ensures reproducible dependency versions
3. **Keep tests fast**: 82 tests in 4 seconds is excellent, maintain this speed
4. **Avoid network calls**: Unit tests should be deterministic and offline-capable
5. **Use pytest markers**: `--strict-markers` catches typos early

### Maintenance Considerations

1. **Review action updates**: GitHub dependabot can automatically update action versions
2. **Monitor CI minutes**: Track usage in GitHub settings (free tier = 2,000 min/month)
3. **Update Python versions**: When Python 3.14 releases, add to matrix
4. **Cache hit rate**: Monitor cache effectiveness in workflow logs
5. **Test duration trends**: Watch for test suite slowdown over time

---

## Open Questions & Future Work

### Resolved (No Action Needed)
- ✅ Which Python versions to test? → 3.11, 3.12, 3.13
- ✅ How to cache dependencies? → Cache `~/.cache/uv` with lock file hash
- ✅ Should we test on multiple OSes? → No, start with Linux only
- ✅ Need code coverage? → No, deferred to future enhancement

### Future Enhancements (Out of Scope)
- Code coverage reporting (codecov.io or coveralls)
- Linting checks (ruff, mypy)
- Security scanning (bandit, safety)
- Documentation build validation
- Performance regression testing
- Benchmark tracking
- Artifact uploads (test reports, logs)

### Implementation Notes
- Workflow can be tested locally with `act` (GitHub Actions local simulator)
- Consider adding workflow_dispatch trigger for manual runs during testing
- GitHub UI shows workflow status on PR page automatically (no extra config needed)

---

## References

### Official Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [uv Documentation](https://docs.astral.sh/uv/)
- [pytest Documentation](https://docs.pytest.org/)

### GitHub Actions Marketplace
- [actions/checkout](https://github.com/actions/checkout)
- [actions/setup-python](https://github.com/actions/setup-python)
- [actions/cache](https://github.com/actions/cache)
- [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv)

### Best Practices & Guides
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Python in GitHub Actions](https://docs.github.com/en/actions/guides/building-and-testing-python)
- [Caching Dependencies](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)

---

## Conclusion

All technical decisions have been made with clear rationale. The implementation is straightforward:
1. Single YAML workflow file
2. Matrix strategy for Python 3.11-3.13
3. Official actions for setup and caching
4. Standard pytest execution

No NEEDS CLARIFICATION items remain. Ready to proceed to Phase 1: Design & Contracts.

