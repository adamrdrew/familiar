# Quickstart: GitHub Actions PR Checks

**Feature**: Automated test execution on pull requests | **Estimated time**: 5-10 minutes

## Overview

This guide walks you through setting up GitHub Actions to automatically run Familiar's Python test suite on all pull requests. Once configured, every PR will show test results directly in the GitHub UI, and you can optionally block merging if tests fail.

**What you'll accomplish**:
- ✅ Automatic test execution on PR creation and updates
- ✅ Test results visible on PR page (✅ pass / ❌ fail)
- ✅ Tests run on Python 3.11, 3.12, and 3.13
- ✅ Fast CI runs (<3 min) with dependency caching

---

## Prerequisites

- **Repository access**: Write access to create `.github/workflows/` directory
- **Existing tests**: Familiar test suite already exists in `tests/` directory
- **uv configuration**: `pyproject.toml` and `uv.lock` already configured
- **No secrets needed**: Unit tests don't require LLM API keys

**Verification**:
```bash
# Confirm tests run locally
cd /path/to/familiar
uv run pytest tests/ -v

# Should see: "82 passed" (or similar, depending on test count)
```

---

## Step 1: Create Workflow Directory

Create the GitHub Actions workflow directory structure:

```bash
# From repository root
mkdir -p .github/workflows
```

**Why**: GitHub Actions looks for workflows in `.github/workflows/` directory. This is a standard location required by GitHub.

---

## Step 2: Add Workflow File

Copy the workflow configuration to `.github/workflows/pr-checks.yml`:

```bash
# Option A: Copy from contract (if in specs directory)
cp specs/005-github-actions-pr-checks/contracts/pr-checks.yml .github/workflows/pr-checks.yml

# Option B: Create directly (if implementing from scratch)
# Create the file and paste contents from contracts/pr-checks.yml
```

**Verify file location**:
```bash
ls -la .github/workflows/pr-checks.yml
# Should output: .github/workflows/pr-checks.yml
```

**File contents** (abbreviated, see `contracts/pr-checks.yml` for full version):
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
      fail-fast: false
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - uses: astral-sh/setup-uv@v4
      - uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('uv.lock') }}
      - run: uv sync
      - run: uv run pytest tests/ -v --strict-markers
```

---

## Step 3: Adjust Branch Names (if needed)

Check your repository's default branch name:

```bash
git branch --show-current
# Common values: main, master, develop
```

**If your default branch is NOT `main` or `master`**, update the workflow:

```yaml
# Edit .github/workflows/pr-checks.yml
on:
  pull_request:
    branches:
      - main        # ← Change to your default branch
      - master      # ← Remove if not applicable
```

**Common scenarios**:
- Using `main` only: `branches: [main]`
- Using `master` only: `branches: [master]`
- Using `develop`: `branches: [develop]`

---

## Step 4: Commit and Push Workflow

Add the workflow file to git:

```bash
# Add workflow file
git add .github/workflows/pr-checks.yml

# Commit
git commit -m "Add GitHub Actions workflow for PR checks

- Run tests on Python 3.11, 3.12, 3.13
- Trigger on pull request events
- Cache dependencies for performance"

# Push to your branch
git push origin 005-github-actions-pr-checks
```

**Note**: Pushing the workflow file doesn't trigger it yet. It only runs on pull requests targeting `main`/`master`.

---

## Step 5: Test the Workflow

### Option A: Create a Test PR (Recommended)

1. **Open a pull request** from your feature branch to `main`/`master`:
   ```bash
   # Via GitHub CLI
   gh pr create --title "Add GitHub Actions PR checks" --body "Implements automated testing on PRs"
   
   # Or via GitHub web UI:
   # Go to: https://github.com/YOUR_ORG/familiar/pull/new/005-github-actions-pr-checks
   ```

2. **Watch workflow execute**:
   - GitHub automatically triggers the workflow
   - Visit the PR page
   - Look for "Checks" tab or workflow status at bottom
   - Should see: "Test (Python 3.11)", "Test (Python 3.12)", "Test (Python 3.13)"

3. **Wait for results** (~2-5 minutes):
   - First run (cold cache): ~3-5 minutes
   - Subsequent runs: ~1-3 minutes

4. **Check status**:
   - ✅ **All green**: Tests passed on all Python versions → Ready to merge
   - ❌ **Red X**: Tests failed → Click "Details" to see which tests failed
   - ⏳ **Yellow dot**: Still running → Wait for completion

### Option B: Manual Trigger (During Development)

For testing workflow changes without creating a PR:

1. **Add manual trigger** (temporary, for testing):
   ```yaml
   # Edit .github/workflows/pr-checks.yml
   on:
     pull_request:
       branches: [main, master]
     workflow_dispatch:  # ← Add this for manual runs
   ```

2. **Trigger manually**:
   - Go to: Actions tab → PR Checks → Run workflow
   - Select your branch → Click "Run workflow"

3. **Remove `workflow_dispatch`** once testing is complete.

---

## Step 6: View Workflow Results

### In GitHub UI

**Navigate to workflow run**:
1. Go to PR page
2. Scroll to bottom → "Checks" section
3. Click "Details" next to any Python version

**What you'll see**:
- **Summary**: Overall pass/fail status
- **Jobs**: Each Python version (3.11, 3.12, 3.13)
- **Logs**: Detailed output for each step
  - Checkout code
  - Set up Python
  - Install uv
  - Cache dependencies (HIT or MISS)
  - Install dependencies (uv sync output)
  - Run tests (pytest output with results)

### Interpreting Results

**✅ Success (all tests pass)**:
```
Test (Python 3.11) ✓ 2m 34s
Test (Python 3.12) ✓ 2m 41s
Test (Python 3.13) ✓ 2m 38s
```
→ PR is ready to merge (tests pass on all versions)

**❌ Failure (tests fail)**:
```
Test (Python 3.11) ✓ 2m 34s
Test (Python 3.12) ✗ 2m 41s  ← Failed
Test (Python 3.13) ✓ 2m 38s
```
→ Click "Details" on failed job to see which tests failed and why

**⚠️ Partial failure with `fail-fast: false`**:
- All Python versions run to completion
- You see results for all versions, not just the first failure
- Helps identify if issue is Python version-specific

---

## Step 7: Enable Branch Protection (Optional)

Prevent merging PRs with failing tests:

1. **Go to repository settings**:
   ```
   Settings → Branches → Branch protection rules
   ```

2. **Add rule for `main` (or your default branch)**:
   - Click "Add rule"
   - Branch name pattern: `main` (or `master`)

3. **Configure protection settings**:
   ```
   ✅ Require status checks to pass before merging
      ✅ Require branches to be up to date before merging
      
      Status checks required: (search and select)
      ✅ Test (Python 3.11)
      ✅ Test (Python 3.12)
      ✅ Test (Python 3.13)
   
   ✅ Require conversation resolution before merging (optional)
   ```

4. **Save changes**

**Result**: PRs with failing tests cannot be merged. Merge button will be grayed out until tests pass.

**Note**: Branch protection requires admin permissions. If you don't have admin access, ask a repository admin to configure this.

---

## Step 8: Verify Everything Works

### Checklist

- [ ] Workflow file exists at `.github/workflows/pr-checks.yml`
- [ ] Workflow file committed and pushed
- [ ] PR created (or workflow manually triggered)
- [ ] Workflow appears in "Actions" tab
- [ ] Workflow runs automatically on PR events
- [ ] All 3 Python versions execute in parallel
- [ ] Tests pass on all versions (or failures are visible)
- [ ] PR page shows check status (✅ or ❌)
- [ ] Branch protection enabled (optional)

### Test Scenarios

**Scenario 1: All tests pass**
- Expected: ✅ Green checks on PR
- Action: Merge is allowed (if no other blocking issues)

**Scenario 2: Tests fail**
- Expected: ❌ Red X on PR
- Action: Fix failing tests, push new commit, workflow re-runs automatically

**Scenario 3: Dependency change**
- Edit `pyproject.toml`, run `uv lock`, push
- Expected: Cache misses (new lock file hash), dependencies reinstall, tests run
- Performance: ~30s longer (cold cache), then back to ~5s (warm cache)

---

## Troubleshooting

### Issue: Workflow doesn't trigger on PR

**Symptoms**:
- Created PR but no workflow runs
- "Checks" tab shows no workflows

**Solutions**:
1. **Check branch name**: Workflow only triggers for PRs targeting `main`/`master`
   ```yaml
   # Verify in .github/workflows/pr-checks.yml
   on:
     pull_request:
       branches: [main, master]  # ← Must match your target branch
   ```

2. **Confirm workflow is on target branch**: 
   ```bash
   # Switch to main branch
   git checkout main
   
   # Check if workflow file exists
   ls .github/workflows/pr-checks.yml
   
   # If missing, you need to merge the workflow file to main first
   ```

3. **Check Actions permissions**:
   - Go to: Settings → Actions → General
   - Ensure "Allow all actions and reusable workflows" is enabled
   - For private repos: Check if GitHub Actions is enabled

### Issue: Tests fail in CI but pass locally

**Symptoms**:
- Local: `uv run pytest tests/ -v` passes
- CI: Workflow fails with test errors

**Solutions**:
1. **Check Python version**:
   ```bash
   # Locally
   python --version  # e.g., Python 3.12.1
   
   # CI uses 3.11, 3.12, 3.13
   # If you're on 3.10 locally, that might explain differences
   ```

2. **Run tests with same flags as CI**:
   ```bash
   uv run pytest tests/ -v --strict-markers
   # The --strict-markers flag might catch issues you missed
   ```

3. **Check for environment-specific issues**:
   - CI runs on Linux (ubuntu-latest)
   - Local might be macOS or Windows
   - Check for OS-specific path issues or assumptions

4. **Check dependency versions**:
   ```bash
   # Ensure your lock file is up to date
   uv lock --check  # Verifies lock file matches pyproject.toml
   ```

### Issue: Workflow is slow (>5 minutes)

**Symptoms**:
- Workflow takes >5 minutes to complete
- Much slower than local test execution

**Solutions**:
1. **Check cache effectiveness**:
   - Open workflow run logs
   - Find "Cache dependencies" step
   - Look for "Cache hit" vs "Cache miss"
   - If always missing: Check cache key configuration

2. **Verify cache key**:
   ```yaml
   # In .github/workflows/pr-checks.yml
   key: uv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('uv.lock') }}
   # Ensure uv.lock path is correct (should be in repo root)
   ```

3. **Check dependency install time**:
   - Expand "Install dependencies" step in logs
   - Should be ~5-10s with cache, ~30-40s without
   - If >1 minute: Consider optimizing dependencies

4. **Optimize test execution** (future):
   - Add `pytest-xdist` for parallel test execution
   - Use `pytest -n auto` for multi-core testing

### Issue: Python version X.Y not available

**Symptoms**:
- Error: "Version X.Y with arch x64 not found"
- Specific Python version fails to install

**Solutions**:
1. **Use stable versions**:
   ```yaml
   python-version: ["3.11", "3.12", "3.13"]  # ✅ Stable
   # Not: ["3.11.5", "3.12.1", "3.13.0"]     # ❌ Too specific
   ```

2. **Check Python version availability**:
   - Visit: https://github.com/actions/python-versions/releases
   - Verify version is available for `ubuntu-latest`

3. **Update workflow Python versions** as needed:
   ```yaml
   # When Python 3.14 releases:
   python-version: ["3.11", "3.12", "3.13", "3.14"]
   ```

### Issue: Out of disk space

**Symptoms**:
- Error: "No space left on device"
- Workflow fails during dependency install

**Solutions**:
1. **Check virtual environment size**:
   - GitHub runners have ~14GB free space
   - Familiar dependencies should be <500MB
   - Unlikely to hit this limit unless dependencies changed significantly

2. **Clear cache if corrupted**:
   - Go to: Settings → Actions → Caches
   - Delete all caches (they'll rebuild)

---

## Next Steps

### Immediate Next Steps

1. **Merge the PR** (once tests pass):
   ```bash
   # Via GitHub CLI
   gh pr merge 005-github-actions-pr-checks --squash
   
   # Or via GitHub web UI
   ```

2. **Update CONTRIBUTING.md** (recommended):
   ```markdown
   ## Pull Request Process
   
   All pull requests must pass automated tests:
   - Tests run automatically on PR creation/update
   - Python 3.11, 3.12, and 3.13 are tested
   - Wait for green checks (✅) before requesting review
   - Fix any test failures before merging
   ```

3. **Add status badge to README** (optional):
   ```markdown
   [![PR Checks](https://github.com/YOUR_ORG/familiar/actions/workflows/pr-checks.yml/badge.svg)](https://github.com/YOUR_ORG/familiar/actions/workflows/pr-checks.yml)
   ```

### Future Enhancements

**Add code coverage** (codecov.io):
```yaml
- name: Run tests with coverage
  run: uv run pytest tests/ --cov=familiar --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

**Add linting checks** (ruff, mypy):
```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
    - run: uv run ruff check .
    - run: uv run mypy src/
```

**Add security scanning** (bandit, safety):
```yaml
security:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: uv run bandit -r src/
    - run: uv run safety check
```

---

## Summary

You've successfully set up GitHub Actions for automated PR testing! Here's what you accomplished:

✅ **Automated Testing**: Tests run automatically on every PR
✅ **Multi-Version Support**: Tests execute on Python 3.11, 3.12, 3.13
✅ **Fast Feedback**: ~2-3 minutes per PR (with caching)
✅ **Clear Status**: PR page shows ✅/❌ status for each Python version
✅ **Optional Protection**: Can block merging if tests fail

**Workflow behavior**:
- Triggers: When PR opened, updated, or reopened
- Duration: ~2-5 minutes (first run), ~1-3 minutes (cached)
- Cost: Free for public repos (2,000 minutes/month free tier)
- Maintenance: Minimal (update Python versions yearly)

**Next PR onwards**: All contributors see automated test results immediately after pushing changes. No manual test running required!

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [setup-uv Action](https://github.com/astral-sh/setup-uv)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [Familiar Contributing Guide](../../CONTRIBUTING.md)

