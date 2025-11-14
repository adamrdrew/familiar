# Data Model: GitHub Actions PR Checks Workflow

**Feature**: GitHub Actions PR Checks | **Date**: 2025-01-14

## Overview

This document defines the structure and schema of the GitHub Actions workflow configuration for running Python tests on pull requests. Unlike traditional code data models, this describes the YAML workflow structure, its components, and their relationships.

---

## Workflow Structure

### Top-Level Workflow Schema

```yaml
name: string                    # Workflow display name
on: EventTriggerConfig          # Events that trigger workflow
jobs: Map<string, JobConfig>    # Named jobs to execute
```

**Entity**: `Workflow`
- **Purpose**: Root configuration defining when and how tests run
- **Location**: `.github/workflows/pr-checks.yml`
- **Lifecycle**: Static configuration, executed by GitHub Actions runtime

---

## Event Trigger Configuration

### EventTriggerConfig Schema

```yaml
pull_request:
  branches: string[]            # Target branches (e.g., ["main", "master"])
  types: string[]               # Event types (optional, defaults to [opened, synchronize, reopened])
```

**Entity**: `EventTriggerConfig`
- **Type**: Workflow trigger specification
- **Cardinality**: 1 per workflow
- **Validation**:
  - `branches` must be non-empty array
  - Branch names must match repository branches
  - `types` (if specified) must be valid PR event types

**Default Behavior** (when `types` omitted):
- `opened`: New PR created
- `synchronize`: New commits pushed to PR
- `reopened`: Closed PR reopened

---

## Job Configuration

### JobConfig Schema

```yaml
test:                           # Job identifier
  name: string                  # Display name with matrix interpolation
  runs-on: string               # Runner type (e.g., "ubuntu-latest")
  strategy: StrategyConfig      # Matrix and failure handling
  steps: Step[]                 # Ordered list of actions/commands
```

**Entity**: `JobConfig`
- **Type**: Job definition
- **Cardinality**: 1 job ("test") in this workflow
- **Relationships**:
  - Has-one `StrategyConfig`
  - Has-many `Step` (ordered sequence)

---

## Strategy Configuration

### StrategyConfig Schema

```yaml
matrix:
  python-version: string[]      # Python versions to test
fail-fast: boolean              # Stop all jobs on first failure
```

**Entity**: `StrategyConfig`
- **Type**: Matrix build configuration
- **Purpose**: Define parallel job execution
- **Fields**:
  - `python-version`: Array of Python version strings (e.g., ["3.11", "3.12", "3.13"])
  - `fail-fast`: Boolean, `false` = run all matrix jobs even if one fails

**Matrix Behavior**:
- Creates N parallel jobs where N = length of `python-version` array
- Each job runs with a different Python version
- Matrix variables accessible via `${{ matrix.python-version }}`

**Example Expansion**:
```yaml
# This configuration:
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
  fail-fast: false

# Expands to 3 parallel jobs:
# - Test (Python 3.11)
# - Test (Python 3.12)
# - Test (Python 3.13)
```

---

## Step Configuration

### Step Schema

```yaml
- name: string                  # Step display name
  uses: string                  # Action to use (for marketplace actions)
  with: Map<string, any>        # Input parameters for action
  run: string                   # Shell command (mutually exclusive with 'uses')
```

**Entity**: `Step`
- **Type**: Individual workflow action or command
- **Cardinality**: 6 steps in this workflow
- **Execution**: Sequential (one after another)
- **Failure Handling**: Step failure fails entire job by default

### Step Types

#### 1. Checkout Step (uses action)
```yaml
- uses: actions/checkout@v4
```
- **Purpose**: Clone repository code
- **Version**: v4 (latest stable)
- **Inputs**: None (defaults sufficient)

#### 2. Setup Python Step (uses action)
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
```
- **Purpose**: Install specified Python version
- **Inputs**:
  - `python-version`: Matrix variable (3.11, 3.12, or 3.13)
- **Adds to PATH**: `python`, `pip`, `python3`

#### 3. Install uv Step (uses action)
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
```
- **Purpose**: Install uv package manager
- **Version**: v4 (official Astral action)
- **Adds to PATH**: `uv` command

#### 4. Cache Step (uses action)
```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('uv.lock') }}
    restore-keys: |
      uv-${{ runner.os }}-${{ matrix.python-version }}-
```
- **Purpose**: Cache downloaded Python packages
- **Cache Key**: Composite of OS + Python version + lock file hash
- **Fallback**: Restore-keys provide partial match fallback
- **Performance**: 75-85% speedup on cache hit

**Cache Key Breakdown**:
- `runner.os`: Operating system (Linux, macOS, Windows)
- `matrix.python-version`: Python version from matrix
- `hashFiles('uv.lock')`: SHA hash of lock file contents

#### 5. Install Dependencies Step (run command)
```yaml
- name: Install dependencies
  run: uv sync
```
- **Purpose**: Install project dependencies
- **Command**: `uv sync`
- **Behavior**:
  - Reads `pyproject.toml` and `uv.lock`
  - Creates virtual environment (`.venv/`)
  - Installs all dependencies including dev group
  - Respects lock file for reproducible builds

#### 6. Run Tests Step (run command)
```yaml
- name: Run tests
  run: uv run pytest tests/ -v --strict-markers
```
- **Purpose**: Execute test suite
- **Command**: `uv run pytest tests/ -v --strict-markers`
- **Flags**:
  - `tests/`: Target directory (all test types)
  - `-v`: Verbose output
  - `--strict-markers`: Fail on unknown pytest markers
- **Exit Code**: 0 = all tests pass, non-zero = failure

---

## Data Flow

### Workflow Execution Flow

```
1. PR Event (opened/synchronized/reopened)
   ↓
2. GitHub Actions triggers workflow
   ↓
3. Matrix expansion (3 parallel jobs)
   ↓
4. For each Python version:
   a. Checkout code
   b. Set up Python
   c. Install uv
   d. Restore cache (if available)
   e. Install dependencies (uv sync)
   f. Run tests (pytest)
   ↓
5. Report status on PR
   - ✅ Green check if all tests pass
   - ❌ Red X if any tests fail
```

### Cache Flow

```
First Run (cold cache):
  1. Cache miss
  2. uv sync downloads packages (~30s)
  3. Cache save

Subsequent Runs (warm cache):
  1. Cache hit (if uv.lock unchanged)
  2. uv sync skips downloads (~5s)
  3. No cache save needed

After Dependency Change:
  1. Cache miss (lock file hash changed)
  2. uv sync downloads new/changed packages
  3. Cache save with new key
```

---

## Validation Rules

### Workflow-Level Validation

1. **Event Trigger**:
   - ✅ MUST trigger on `pull_request` event
   - ✅ MUST target `main` or `master` branches (or both)
   - ❌ MUST NOT trigger on `push` to feature branches (inefficient)

2. **Job Configuration**:
   - ✅ MUST define at least one job
   - ✅ Job name MUST include matrix variable for clarity
   - ✅ MUST use GitHub-hosted runner (ubuntu-latest)

3. **Matrix Strategy**:
   - ✅ MUST test Python 3.11 (project minimum)
   - ✅ SHOULD test Python 3.12 and 3.13 (forward compatibility)
   - ✅ MUST set `fail-fast: false` (see all failures)

4. **Steps Order**:
   - ✅ MUST checkout before any other steps
   - ✅ MUST setup Python before installing uv
   - ✅ SHOULD cache before installing dependencies
   - ✅ MUST install dependencies before running tests

### Action Version Validation

All actions MUST use pinned versions (not `@main` or `@latest`):
- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/cache@v4`
- `astral-sh/setup-uv@v4`

**Rationale**: Pinned versions prevent breaking changes from upstream updates.

### Command Validation

1. **Dependency Install**:
   - ✅ MUST use `uv sync` (not `pip install`)
   - ❌ MUST NOT use `uv pip install -r requirements.txt` (no requirements.txt in project)

2. **Test Execution**:
   - ✅ MUST use `uv run pytest` (activates environment automatically)
   - ✅ MUST target `tests/` directory
   - ✅ MUST include `-v` for verbose output
   - ✅ SHOULD include `--strict-markers` for marker validation

---

## Environment Variables

### Implicit Environment Variables (GitHub Actions)

These are automatically available in workflow:

| Variable | Example Value | Usage |
|----------|---------------|-------|
| `GITHUB_WORKSPACE` | `/home/runner/work/familiar/familiar` | Working directory |
| `RUNNER_OS` | `Linux` | Operating system |
| `RUNNER_TEMP` | `/home/runner/work/_temp` | Temporary directory |
| `GITHUB_SHA` | `abc123...` | Commit SHA |
| `GITHUB_REF` | `refs/pull/42/merge` | PR reference |

### Matrix Variables

| Variable | Values | Usage |
|----------|--------|-------|
| `matrix.python-version` | `"3.11"`, `"3.12"`, `"3.13"` | Python version selection |

### No Secrets Required

This workflow intentionally does NOT require secrets:
- ❌ No `ANTHROPIC_API_KEY` (unit tests don't call LLMs)
- ❌ No `OPENAI_API_KEY` (unit tests don't call LLMs)
- ✅ Tests are fully offline and deterministic

---

## State Transitions

### Job State Machine

```
Created (workflow triggered)
   ↓
Queued (waiting for runner)
   ↓
Running (executing steps)
   ↓
   ├─→ Success (all steps exit 0)
   ├─→ Failure (any step exits non-zero)
   └─→ Cancelled (manually cancelled)
```

### PR Check Status

```
PR Created/Updated
   ↓
Check: Pending (⏳)
   ↓
Workflow Executes
   ↓
   ├─→ Check: Success (✅) → Can merge
   ├─→ Check: Failure (❌) → Cannot merge (if branch protection enabled)
   └─→ Check: Cancelled (⚪) → No status
```

---

## Performance Characteristics

### Time Complexity

| Step | Cold Cache | Warm Cache |
|------|------------|------------|
| Checkout | ~2s | ~2s |
| Setup Python | ~10s | ~10s |
| Install uv | ~3s | ~3s |
| Cache restore | ~1s | ~1s |
| Install dependencies | ~30s | ~5s |
| Run tests | ~10s | ~10s |
| **Total** | **~56s** | **~31s** |

*Per-job time. Total workflow time = max(all matrix jobs) ≈ single job time (parallel execution).*

### Space Complexity

| Resource | Size |
|----------|------|
| Repository checkout | ~5 MB |
| uv binary | ~15 MB |
| Python packages (cached) | ~200 MB |
| Virtual environment | ~300 MB |
| **Total per job** | **~520 MB** |

GitHub Actions runners have ~14GB disk space, so no constraints.

---

## Extension Points

### Future Schema Additions

```yaml
# Linting job (future)
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
    - run: uv run ruff check .
    - run: uv run mypy src/

# Coverage reporting (future)
test:
  steps:
    - run: uv run pytest tests/ --cov=familiar --cov-report=xml
    - uses: codecov/codecov-action@v3
```

### Conditional Execution (future)

```yaml
# Only run on specific file changes
on:
  pull_request:
    paths:
      - 'src/**'
      - 'tests/**'
      - 'pyproject.toml'
      - 'uv.lock'
```

---

## Summary

The workflow data model consists of:
1. **1 Workflow**: PR Checks
2. **1 Job**: Test
3. **1 Matrix Strategy**: 3 Python versions
4. **6 Steps per job**: Checkout, Setup, Install, Cache, Sync, Test
5. **3 Parallel Executions**: One per Python version

Total entities created at runtime: 3 jobs × 6 steps = 18 step executions.

All validation rules are enforced by GitHub Actions runtime. No custom validation code required.

