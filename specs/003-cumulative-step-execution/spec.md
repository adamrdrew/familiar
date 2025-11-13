# Cumulative Step Execution & Session Persistence

**Type**: Enhancement | **Priority**: Critical | **Date**: 2025-11-13

## Problem Statement

Currently, Familiar has two architectural issues that prevent effective end-to-end testing:

### Problem 1: Implicit Step Ordering & No Skipping Logic

Steps are discovered without explicit ordering rules. The system doesn't formally specify that files with numeric prefixes (00-, 01-, 02-, etc.) should run in sequence, and files without numeric prefixes should be skipped. There's no verbose logging to indicate which files are being skipped.

**Current Behavior:**
- Step files are discovered but ordering is implicit
- No clear rules about which files to run vs. skip
- No logging for skipped files

**Desired Behavior:**
- Files with numeric prefixes (00-*, 01-*, 02-*, etc.) run in sequence
- Files without numeric prefixes are explicitly skipped
- Verbose mode logs all skipped files with clear messaging

**Example Scenario Directory:**
```
login-scenario/
├── 00-navigate.md      ← Run first
├── 01-enter-creds.md   ← Run second
├── 02-submit.md        ← Run third
├── README.md           ← SKIP (no numeric prefix)
└── update.md           ← SKIP (no numeric prefix)
```

**Expected Verbose Output:**
```
[INFO] Running step 1/3: 00-navigate.md
[INFO] Running step 2/3: 01-enter-creds.md  
[INFO] Running step 3/3: 02-submit.md
[INFO] Skipped file (no numeric prefix): README.md
[INFO] Skipped file (no numeric prefix): update.md
```

### Problem 2: Browser Session Dies Between Steps

Currently, a new browser-use Agent instance is created for each step. This causes the browser window (or headless browser) to close and restart between steps, breaking the cumulative nature of end-to-end tests.

**Current Behavior:**
```python
# Each step creates a new session
for step in suite.steps:
    agent = await create_browser_use_agent(...)  # New browser!
    result = await agent.run()
    # Browser closes here
```

**Impact:**
- Cannot perform sequences like: login → navigate → fill form → submit
- Each step starts with a fresh browser, losing all state (cookies, local storage, navigation history)
- Makes true end-to-end workflows impossible

**Desired Behavior:**
- Each **scenario** (test suite) has ONE browser session
- All steps in a scenario use the same session
- Browser persists across all steps in the scenario
- Browser closes only when scenario completes
- Scenarios run independently with their own sessions

## Architecture Requirements

### Requirement 1: Explicit Step Ordering & Skipping

**Rule**: Steps are markdown files (*.md) with optional numeric prefixes.

**Processing Logic:**
1. Discover all *.md files in scenario directory
2. Separate into two groups:
   - **Runnable steps**: Files matching pattern `^\d\d-.+\.md$` (e.g., 00-login.md, 01-auth.md)
   - **Skipped files**: All other *.md files (e.g., README.md, update.md, notes.md)
3. Sort runnable steps numerically by prefix (00 → 01 → 02 → ...)
4. Execute in sorted order
5. Log skipped files in verbose mode

**Edge Cases:**
- Gaps in numbering (00, 02, 05) → OK, run in order
- Duplicate numbers (00-login.md, 00-setup.md) → ERROR, fail fast
- No numbered files → ERROR, no steps to run
- Only non-numbered files → ERROR, no steps to run

### Requirement 2: Session Persistence Across Steps

**Architecture Change:**

**Before (Current):**
```
Scenario
├── Step 1: Create Agent → Run → Destroy
├── Step 2: Create Agent → Run → Destroy
└── Step 3: Create Agent → Run → Destroy
```

**After (Desired):**
```
Scenario
├── Create Agent (with Browser)
├── Step 1: Use existing Agent
├── Step 2: Use existing Agent
├── Step 3: Use existing Agent
└── Destroy Agent
```

**Key Changes:**
- Browser/Agent created **once per scenario** at suite level
- Executor receives pre-existing browser/agent instance
- Steps execute sequentially using the same agent
- Browser closes when scenario completes or fails

**Independence Guarantees:**
- Each scenario gets its own isolated browser session
- Scenarios can run in parallel (different browser instances)
- Scenarios cannot depend on each other
- Step order matters within a scenario, but scenario order doesn't matter

## Functional Requirements

### FR1: Explicit Step File Ordering

**Given** a scenario directory with mixed files:
- `00-login.md`, `01-dashboard.md`, `02-logout.md`
- `README.md`, `notes.md`, `update.md`

**When** the scenario is executed

**Then**:
- Steps run in order: 00-login.md → 01-dashboard.md → 02-logout.md
- Non-numbered files are skipped: README.md, notes.md, update.md
- Order is deterministic and repeatable

### FR2: Skip File Logging in Verbose Mode

**Given** verbose mode is enabled (`-v` flag)

**When** a scenario contains files without numeric prefixes

**Then**:
- Log each skipped file with format: `[INFO] Skipped file (no numeric prefix): {filename}`
- Log appears after step execution completes
- Skipped files are listed in alphabetical order

### FR3: Step Prefix Validation

**Given** a scenario directory

**When** step files are discovered

**Then**:
- Validate all numeric prefixes are 2 digits (00-99)
- Detect duplicate prefixes and fail with clear error
- Detect missing steps.md files entirely and fail
- Allow gaps in numbering (00, 02, 05 is OK)

### FR4: Single Browser Session Per Scenario

**Given** a scenario with multiple steps

**When** the scenario executes

**Then**:
- Browser is created once before first step
- Same browser instance is reused for all steps
- Browser maintains state (cookies, storage, navigation) across steps
- Browser closes after last step completes (success or failure)

### FR5: Cumulative Step Execution

**Given** steps that depend on previous state (e.g., login → navigate)

**When** steps execute in sequence

**Then**:
- Each step starts with browser state from previous step
- Cookies and session data persist
- Current page/URL carries forward
- Local/session storage is preserved

### FR6: Scenario Independence

**Given** multiple scenarios in a test run

**When** scenarios execute

**Then**:
- Each scenario has its own isolated browser session
- Scenarios do not share state
- Scenarios can run in any order
- Scenarios can run in parallel (if supported in future)

## Non-Functional Requirements

### NFR1: Backward Compatibility

Existing scenarios without numeric prefixes should fail gracefully with clear error message guiding users to add prefixes.

### NFR2: Performance

Session reuse should improve performance by eliminating browser startup/teardown overhead between steps.

### NFR3: Error Handling

If any step fails, the browser session should close cleanly and error details should be reported.

### NFR4: Logging Clarity

Verbose logs must clearly distinguish between:
- Steps being executed
- Files being skipped
- Browser session lifecycle (create/destroy)

## Acceptance Criteria

- [ ] Step files with numeric prefixes (00-*, 01-*, etc.) execute in sorted order
- [ ] Step files without numeric prefixes are skipped
- [ ] Verbose mode logs all skipped files with clear message
- [ ] Duplicate numeric prefixes cause immediate failure with clear error
- [ ] Browser session created once per scenario, before first step
- [ ] All steps in a scenario use the same browser instance
- [ ] Browser state (cookies, storage, navigation) persists across steps
- [ ] Browser closes after scenario completes (success or failure)
- [ ] Multiple scenarios get independent browser sessions
- [ ] Existing tests updated to use numeric prefixes
- [ ] Documentation updated with step file naming conventions

## Impact

### Files Modified
- `src/familiar/core/discovery.py` - Add step ordering and filtering logic
- `src/familiar/core/parser.py` - Update to validate step prefixes
- `src/familiar/core/executor.py` - Modify to receive browser instance instead of creating it
- `src/familiar/core/runner.py` - Create browser once per scenario, pass to executor
- `src/familiar/logging/setup.py` - Add logging for skipped files

### Breaking Changes
- Scenarios without numeric prefixes on step files will fail (but with clear guidance)
- `StepExecutor` constructor signature changes (receives browser instead of creating it)

### Migration Path
Users must rename step files to include numeric prefixes:
- `login.md` → `00-login.md`
- `dashboard.md` → `01-dashboard.md`
- `logout.md` → `02-logout.md`

Files like `README.md` can stay as-is (they'll be skipped).

## References

- Browser-use Agent documentation: https://docs.browser-use.com/
- Familiar architecture spec: `specs/001-ai-e2e-testing/spec.md`
- Current executor implementation: `src/familiar/core/executor.py`
- Current runner implementation: `src/familiar/core/runner.py`

