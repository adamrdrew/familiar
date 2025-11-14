# Implementation Tasks: GitHub Actions PR Checks

**Branch**: `005-github-actions-pr-checks` | **Date**: 2025-01-14
**Feature**: Automated PR testing with GitHub Actions

## Overview

This document provides an actionable, dependency-ordered task list for implementing automated PR checks using GitHub Actions. The feature enables automatic test execution on all pull requests across Python 3.11, 3.12, and 3.13.

**Complexity**: LOW ⭐ (Single YAML configuration file)
**Estimated Time**: 1-2 hours total
**Primary Deliverable**: `.github/workflows/pr-checks.yml`

---

## User Stories Mapping

This feature serves all four user stories simultaneously through a single workflow implementation:

- **US1**: Contributor gets immediate test feedback → Workflow runs automatically on PR events
- **US2**: Maintainer gets automated validation → Tests run without manual intervention
- **US3**: Maintainer prevents bad merges → Workflow status blocks merge (with branch protection)
- **US4**: Contributor gets fast feedback → Caching reduces runtime to <3 minutes

**Implementation Strategy**: All user stories are satisfied by the core workflow file, with optional enhancements for documentation and branch protection.

---

## Phase 1: Setup & Preparation

**Purpose**: Create directory structure and verify prerequisites

**Prerequisites**: None (start of implementation)

- [X] T001 Verify current branch is `005-github-actions-pr-checks`
- [X] T002 Verify local test suite runs successfully: `uv run pytest tests/ -v`
- [X] T003 Check repository default branch name: `git branch --show-current` or verify on GitHub
- [X] T004 Create GitHub Actions workflow directory: `.github/workflows/`
- [X] T005 Verify `pyproject.toml` and `uv.lock` exist in repository root

**Checkpoint**: Directory structure created, prerequisites verified ✅

---

## Phase 2: Core Workflow Implementation

**Purpose**: Create and configure the GitHub Actions workflow file

**Serves**: US1 (immediate feedback), US2 (automated validation), US3 (prevent bad merges), US4 (fast CI)

**Prerequisites**: Phase 1 complete

### Workflow File Creation

- [X] T006 [US1-4] Copy workflow template from `specs/005-github-actions-pr-checks/contracts/pr-checks.yml` to `.github/workflows/pr-checks.yml`
- [X] T007 [US1-4] Verify workflow name is set to "PR Checks" in `.github/workflows/pr-checks.yml`
- [X] T008 [US1-4] Verify trigger configuration uses `pull_request` event in `.github/workflows/pr-checks.yml`
- [X] T009 [US1-4] Adjust branch targets if needed (main/master/develop) in `.github/workflows/pr-checks.yml`
- [X] T010 [US1-4] Verify job name includes matrix variable in `.github/workflows/pr-checks.yml`

### Matrix Strategy Configuration

- [X] T011 [US1-4] Verify Python version matrix includes ["3.11", "3.12", "3.13"] in `.github/workflows/pr-checks.yml`
- [X] T012 [US1-4] Verify `fail-fast: false` is set in strategy in `.github/workflows/pr-checks.yml`
- [X] T013 [US1-4] Verify `runs-on: ubuntu-latest` is configured in `.github/workflows/pr-checks.yml`

### Workflow Steps Configuration

- [X] T014 [US1-4] Verify Step 1: Checkout code using `actions/checkout@v4` in `.github/workflows/pr-checks.yml`
- [X] T015 [US1-4] Verify Step 2: Setup Python using `actions/setup-python@v5` with matrix variable in `.github/workflows/pr-checks.yml`
- [X] T016 [US1-4] Verify Step 3: Install uv using `astral-sh/setup-uv@v4` in `.github/workflows/pr-checks.yml`
- [X] T017 [US4] Verify Step 4: Cache configuration with correct path and key in `.github/workflows/pr-checks.yml`
- [X] T018 [US4] Verify cache key includes OS, Python version, and uv.lock hash in `.github/workflows/pr-checks.yml`
- [X] T019 [US4] Verify cache restore-keys are configured for partial matches in `.github/workflows/pr-checks.yml`
- [X] T020 [US1-4] Verify Step 5: Install dependencies using `uv sync` in `.github/workflows/pr-checks.yml`
- [X] T021 [US1-4] Verify Step 6: Run tests using `uv run pytest tests/ -v --strict-markers` in `.github/workflows/pr-checks.yml`

### Inline Documentation

- [X] T022 [US1-4] Verify workflow file has inline comments explaining trigger strategy in `.github/workflows/pr-checks.yml`
- [X] T023 [US1-4] Verify workflow file has inline comments explaining matrix strategy in `.github/workflows/pr-checks.yml`
- [X] T024 [US4] Verify workflow file has inline comments explaining cache configuration in `.github/workflows/pr-checks.yml`
- [X] T025 [US1-4] Verify workflow file has inline comments explaining test execution in `.github/workflows/pr-checks.yml`

**Checkpoint**: Workflow file complete with all 6 steps configured and documented ✅

---

## Phase 3: Testing & Verification

**Purpose**: Test workflow execution and verify all acceptance criteria

**Prerequisites**: Phase 2 complete (workflow file created)

### Commit & Push Workflow

- [ ] T026 Add workflow file to git: `git add .github/workflows/pr-checks.yml`
- [ ] T027 Commit with descriptive message explaining the feature in `.github/workflows/pr-checks.yml`
- [ ] T028 Push to feature branch: `git push origin 005-github-actions-pr-checks`

### Create Test PR

- [ ] T029 Create pull request from `005-github-actions-pr-checks` to `main`/`master`
- [ ] T030 Navigate to PR page and verify "Checks" tab appears
- [ ] T031 Verify workflow triggers automatically (should see "PR Checks" workflow running)

### Monitor Workflow Execution

- [ ] T032 Watch workflow progress in "Checks" tab or Actions page
- [ ] T033 Verify 3 parallel jobs appear: "Test (Python 3.11)", "Test (Python 3.12)", "Test (Python 3.13)"
- [ ] T034 Wait for workflow completion (should be <5 minutes on first run)
- [ ] T035 Verify all 3 Python versions show green checkmarks (✅) if tests pass

### Verify Acceptance Criteria

- [ ] T036 ✅ AC1: Verify workflow file exists at `.github/workflows/pr-checks.yml`
- [ ] T037 ✅ AC2: Verify workflow ran automatically when PR was opened
- [ ] T038 ✅ AC3: Verify tests executed on Python 3.11, 3.12, and 3.13 (check workflow logs)
- [ ] T039 ✅ AC4: Verify PR page shows check status (✅ or ❌) for each Python version
- [ ] T040 ✅ AC5: Verify workflow completed in <5 minutes (check run duration)
- [ ] T041 ✅ AC6: Verify test failures would cause workflow to fail (check exit codes)
- [ ] T042 ✅ AC7: Verify workflow logs show pytest output with test results

### Performance Verification

- [ ] T043 Check "Cache dependencies" step for cache hit/miss status in workflow logs
- [ ] T044 Note first run time (cold cache) from workflow summary
- [ ] T045 Make a trivial commit and push to trigger second run
- [ ] T046 Note second run time (warm cache) - should be 30-50% faster
- [ ] T047 Verify cache speedup meets performance targets (<3 min with cache)

**Checkpoint**: Workflow tested and all acceptance criteria verified

---

## Phase 4: Documentation Updates

**Purpose**: Document the CI/CD process for contributors and maintainers

**Prerequisites**: Phase 3 complete (workflow tested successfully)

### CONTRIBUTING.md Updates

- [ ] T048 Read existing `CONTRIBUTING.md` to understand current structure
- [ ] T049 Add "Pull Request Process" or "CI/CD Checks" section in `CONTRIBUTING.md`
- [ ] T050 Document that tests run automatically on PRs in `CONTRIBUTING.md`
- [ ] T051 Explain that tests run on Python 3.11, 3.12, 3.13 in `CONTRIBUTING.md`
- [ ] T052 Document that contributors should wait for green checks before requesting review in `CONTRIBUTING.md`
- [ ] T053 Explain how to view test failures in workflow logs in `CONTRIBUTING.md`
- [ ] T054 Add note about fixing test failures before merging in `CONTRIBUTING.md`

### README.md Updates (Optional)

- [ ] T055 [Optional] Read existing `README.md` badges section
- [ ] T056 [Optional] Add GitHub Actions workflow status badge to `README.md`
- [ ] T057 [Optional] Badge format: `[![PR Checks](https://github.com/ORG/familiar/actions/workflows/pr-checks.yml/badge.svg)](https://github.com/ORG/familiar/actions/workflows/pr-checks.yml)`
- [ ] T058 [Optional] Update README CI/CD features section if present

### Commit Documentation Changes

- [ ] T059 Add CONTRIBUTING.md changes: `git add CONTRIBUTING.md`
- [ ] T060 Add README.md changes if modified: `git add README.md`
- [ ] T061 Commit documentation updates with descriptive message
- [ ] T062 Push documentation changes to feature branch

**Checkpoint**: Documentation complete, contributors have clear guidance on CI process

---

## Phase 5: Branch Protection Setup (Optional Enhancement)

**Purpose**: Enforce passing tests before merge (serves US3)

**Prerequisites**: Phase 3 complete, admin access to repository

**Note**: This phase requires repository admin permissions and is optional but recommended.

### Enable Branch Protection

- [ ] T063 [US3] [Optional] Navigate to repository Settings → Branches
- [ ] T064 [US3] [Optional] Click "Add rule" for branch protection
- [ ] T065 [US3] [Optional] Set branch name pattern to `main` (or `master`, `develop`)
- [ ] T066 [US3] [Optional] Enable "Require status checks to pass before merging"
- [ ] T067 [US3] [Optional] Enable "Require branches to be up to date before merging"
- [ ] T068 [US3] [Optional] Search and select required checks: "Test (Python 3.11)"
- [ ] T069 [US3] [Optional] Search and select required checks: "Test (Python 3.12)"
- [ ] T070 [US3] [Optional] Search and select required checks: "Test (Python 3.13)"
- [ ] T071 [US3] [Optional] Enable "Require conversation resolution before merging" (recommended)
- [ ] T072 [US3] [Optional] Save branch protection rule

### Verify Branch Protection

- [ ] T073 [US3] [Optional] Return to test PR page
- [ ] T074 [US3] [Optional] Verify merge button shows protection requirements
- [ ] T075 [US3] [Optional] Verify "All checks have passed" message appears
- [ ] T076 [US3] [Optional] Document branch protection settings in CONTRIBUTING.md

**Checkpoint**: Branch protection active (if completed), merge blocked on test failures

---

## Phase 6: Final Validation & Cleanup

**Purpose**: Comprehensive end-to-end validation and merge preparation

**Prerequisites**: All previous phases complete

### End-to-End Testing

- [ ] T077 Create a test commit that intentionally breaks a test
- [ ] T078 Push breaking commit and verify workflow fails (red X)
- [ ] T079 Verify PR shows "Some checks were not successful" message
- [ ] T080 Click "Details" on failed check and verify pytest output shows failure reason
- [ ] T081 Fix the intentionally broken test
- [ ] T082 Push fix and verify workflow re-runs automatically
- [ ] T083 Verify workflow passes again (green checks return)

### Final Checklist Review

- [ ] T084 Review all workflow configuration for best practices
- [ ] T085 Verify workflow follows GitHub Actions security guidelines (no secrets exposed)
- [ ] T086 Verify workflow is cost-efficient (uses caching, no unnecessary steps)
- [ ] T087 Verify workflow output is clear and actionable for contributors
- [ ] T088 Run workflow one final time to confirm stable performance

### Merge Preparation

- [ ] T089 Squash all commits if needed for clean history
- [ ] T090 Update PR description with summary of changes and testing results
- [ ] T091 Request review from maintainer (if not self-reviewing)
- [ ] T092 Address any review comments
- [ ] T093 Verify all checks pass one final time
- [ ] T094 Merge PR to activate workflow for all future PRs

### Post-Merge Verification

- [ ] T095 Verify workflow file exists on main branch: `git checkout main && ls .github/workflows/pr-checks.yml`
- [ ] T096 Create a new test branch to verify workflow triggers on new PRs
- [ ] T097 Open a test PR and verify workflow runs automatically
- [ ] T098 Close/delete test PR after verification
- [ ] T099 Monitor first few production PRs to ensure workflow operates smoothly
- [ ] T100 Address any issues discovered in production use

**Checkpoint**: Feature complete, workflow active for all PRs

---

## Task Summary

### Task Counts by Phase

| Phase | Tasks | Parallel Opportunities | Estimated Time |
|-------|-------|------------------------|----------------|
| Phase 1: Setup | 5 | All sequential | 10 minutes |
| Phase 2: Implementation | 20 | Most parallelizable (file verification) | 20 minutes |
| Phase 3: Testing | 22 | Sequential (workflow execution) | 30-60 minutes |
| Phase 4: Documentation | 15 | 7 docs tasks parallelizable | 20 minutes |
| Phase 5: Branch Protection | 14 | All sequential, optional | 10 minutes |
| Phase 6: Final Validation | 24 | Some parallelizable | 30 minutes |
| **Total** | **100 tasks** | **~20% parallelizable** | **2-3 hours** |

### Tasks by User Story

| User Story | Task IDs | Count | Phase |
|------------|----------|-------|-------|
| US1: Immediate feedback | T006-T025, T029-T035 | 27 | Phase 2-3 |
| US2: Automated validation | T006-T025, T029-T042 | 32 | Phase 2-3 |
| US3: Prevent bad merges | T063-T076 | 14 | Phase 5 (optional) |
| US4: Fast CI (<3 min) | T017-T019, T043-T047 | 8 | Phase 2-3 |
| All stories | T006-T025 | 20 | Phase 2 (core) |

### Parallel Execution Opportunities

**Phase 2 (Verification tasks)**: Tasks T006-T025 can be executed quickly as they're all verification steps on the same file. Can be batched as a single "verify workflow file" task.

**Phase 4 (Documentation)**: Tasks T048-T058 can be split into two parallel tracks:
- Track A: CONTRIBUTING.md updates (T048-T054)
- Track B: README.md updates (T055-T058, optional)

**Phase 6 (Final review)**: Tasks T084-T088 can be reviewed in parallel as they're independent checks.

---

## Dependencies & Execution Order

### Critical Path

```
Phase 1 (Setup)
   ↓
Phase 2 (Implementation) → BLOCKS → Phase 3 (Testing)
   ↓
Phase 3 (Testing) → BLOCKS → Phase 4 (Documentation)
   ↓
Phase 4 (Documentation) → OPTIONAL → Phase 5 (Branch Protection)
   ↓
Phase 6 (Final Validation & Merge)
```

### Independent Paths

- **Phase 5 (Branch Protection)** is optional and can be done after merge
- **README.md updates** (T055-T058) are optional and can be skipped
- **Post-merge verification** (T095-T100) can be deferred to production monitoring

---

## MVP Recommendation

For minimum viable implementation (fastest path to working CI):

**MVP Scope** (30-45 minutes):
- ✅ Phase 1: Setup (T001-T005)
- ✅ Phase 2: Core Implementation (T006-T025)
- ✅ Phase 3: Basic Testing (T026-T042)
- ❌ Phase 4: Documentation (defer to follow-up)
- ❌ Phase 5: Branch Protection (defer to follow-up)
- ❌ Phase 6: Extended validation (defer to production)

**MVP Delivers**:
- Working workflow on PRs
- Tests on 3 Python versions
- All acceptance criteria met
- Ready for production use

**Follow-up** (can be done in separate PRs):
- Documentation updates
- Branch protection setup
- Extended validation

---

## Testing Criteria

### Per-Phase Acceptance

**Phase 1 Complete When**:
- ✅ `.github/workflows/` directory exists
- ✅ Local tests pass (`uv run pytest tests/ -v`)
- ✅ Default branch name identified

**Phase 2 Complete When**:
- ✅ `.github/workflows/pr-checks.yml` exists
- ✅ Workflow file has all 6 steps configured
- ✅ Matrix includes Python 3.11, 3.12, 3.13
- ✅ Cache configuration is correct
- ✅ All inline documentation present

**Phase 3 Complete When**:
- ✅ Workflow runs automatically on PR creation
- ✅ All 3 Python versions execute in parallel
- ✅ All acceptance criteria (AC1-AC7) verified
- ✅ Cache demonstrates speedup on second run
- ✅ Workflow completes in <5 minutes

**Phase 4 Complete When**:
- ✅ CONTRIBUTING.md has CI/CD section
- ✅ Contributors understand how to view test results
- ✅ Process for handling test failures documented
- ✅ Optional: README.md has status badge

**Phase 5 Complete When** (optional):
- ✅ Branch protection rule active on main branch
- ✅ Required checks include all 3 Python versions
- ✅ Merge button blocked when tests fail
- ✅ Branch protection documented

**Phase 6 Complete When**:
- ✅ Workflow handles test failures correctly
- ✅ Re-runs work automatically on new commits
- ✅ PR merged to main branch
- ✅ Workflow active for all new PRs
- ✅ Production monitoring established

---

## Troubleshooting Reference

### Common Issues

**Issue 1**: Workflow doesn't trigger on PR
- Check: Branch names in workflow match target branch
- Check: Workflow file exists on target branch (main/master)
- Check: GitHub Actions enabled in repository settings

**Issue 2**: Tests fail in CI but pass locally
- Check: Python version matches (local might be different)
- Check: Running same command: `uv run pytest tests/ -v --strict-markers`
- Check: `uv.lock` is committed and up to date

**Issue 3**: Slow workflow (>5 minutes)
- Check: Cache hit rate in "Cache dependencies" step
- Check: Verify cache key includes `uv.lock` hash
- Check: Dependency install time (should be ~5-10s with cache)

**Issue 4**: Cache not working
- Check: Cache key syntax is correct
- Check: `uv.lock` file exists in repository root
- Check: Cache size within 10GB GitHub limit

**Issue 5**: Python version not found
- Check: Using stable version strings ("3.11", not "3.11.5")
- Check: `setup-python@v5` action is latest version
- Check: Python version available on ubuntu-latest

---

## Success Metrics

### Immediate Success Indicators

- ✅ Workflow file created and committed
- ✅ PR shows 3 green checks (one per Python version)
- ✅ Workflow completes in <5 minutes
- ✅ Second run faster than first (cache working)
- ✅ Test output visible in workflow logs

### Long-term Success Indicators

- ✅ All PRs show automated test results
- ✅ Contributors fix test failures before review
- ✅ No PRs merged with failing tests
- ✅ Workflow remains stable (<5% failure rate from infra issues)
- ✅ CI minutes usage within free tier budget

### Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Workflow duration (cold cache) | <5 min | Check first run duration |
| Workflow duration (warm cache) | <3 min | Check subsequent runs |
| Cache hit rate | >80% | Monitor "Cache dependencies" step |
| Test execution time | <15 sec | Check "Run tests" step duration |
| Parallel execution | 3 jobs | Verify all Python versions run simultaneously |

---

## Future Enhancements

**Not in scope for this feature, but documented for future work**:

### Code Coverage (Follow-up Feature)
- Add `pytest --cov` flag
- Upload coverage to codecov.io or coveralls
- Add coverage badge to README

### Linting & Formatting (Follow-up Feature)
- Add separate `lint` job with ruff and mypy
- Run in parallel with test job
- Add pre-commit hooks for local validation

### Security Scanning (Follow-up Feature)
- Add `bandit` for security vulnerabilities
- Add `safety` for dependency vulnerabilities
- Run on schedule (weekly) in addition to PRs

### Performance Testing (Follow-up Feature)
- Add benchmark tests for key operations
- Track performance trends over time
- Alert on regressions >10%

---

## References

### Design Documents
- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Research & Decisions](./research.md)
- [Data Model](./data-model.md)
- [Workflow Contract](./contracts/pr-checks.yml)
- [Quickstart Guide](./quickstart.md)

### External Resources
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [setup-uv Action](https://github.com/astral-sh/setup-uv)
- [setup-python Action](https://github.com/actions/setup-python)
- [cache Action](https://github.com/actions/cache)

---

**Ready to implement!** Start with Phase 1 (Setup) and work through phases sequentially. Each phase has clear completion criteria and builds on the previous phase.

**Estimated completion time**: 2-3 hours for full implementation, or 30-45 minutes for MVP.

