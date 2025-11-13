# Research: Cumulative Step Execution & Session Persistence

**Date**: 2025-11-13  
**Purpose**: Research implementation strategies for step ordering, file filtering, and browser session management

## Overview

This research addresses two architectural improvements:
1. Explicit step file ordering based on numeric prefixes with automatic skipping
2. Browser session persistence across steps within a scenario

## Decisions

### 1. Step File Naming Convention

**Decision**: Use two-digit numeric prefixes (00-99) followed by hyphen and descriptive name

**Pattern**: `^\d\d-.+\.md$`

**Examples**:
- ✅ `00-login.md`
- ✅ `01-navigate.md`
- ✅ `02-submit-form.md`
- ❌ `0-login.md` (single digit)
- ❌ `1-login.md` (single digit)
- ❌ `login.md` (no prefix)

**Rationale**:
- Two digits allow 100 steps (00-99), sufficient for any scenario
- Fixed width enables simple string sorting without custom comparators
- Hyphen separator is conventional (like database migrations)
- Descriptive names after prefix aid readability

**Alternatives Considered**:
- Single digit (0-9): Rejected - only 10 steps, too limiting
- Three digits (000-999): Rejected - overkill, adds visual noise
- No fixed width: Rejected - requires custom sorting logic

### 2. File Filtering Strategy

**Decision**: Separate step files into two categories using regex pattern matching

**Implementation**:
```python
import re
from pathlib import Path

STEP_PATTERN = re.compile(r'^\d\d-.+\.md$')

def is_numbered_step(filepath: Path) -> bool:
    """Check if file matches numbered step pattern."""
    return bool(STEP_PATTERN.match(filepath.name))

def discover_steps(suite_dir: Path) -> tuple[list[Path], list[Path]]:
    """Discover and categorize step files."""
    all_md_files = sorted(suite_dir.glob('*.md'))
    
    steps = [f for f in all_md_files if is_numbered_step(f)]
    skipped = [f for f in all_md_files if not is_numbered_step(f)]
    
    return steps, skipped
```

**Rationale**:
- Regex is explicit and easily testable
- Functional approach (filter predicates) is clean
- Returns both lists for comprehensive logging
- Simple glob + filter is performant

**Alternatives Considered**:
- Manual string parsing: Rejected - error-prone, less maintainable
- Complex glob patterns: Rejected - glob doesn't support numeric ranges well
- Database/index file: Rejected - adds complexity, breaks simplicity

### 3. Step Ordering Strategy

**Decision**: Sort step files lexicographically by filename after filtering

**Implementation**:
```python
def order_steps(steps: list[Path]) -> list[Path]:
    """Sort steps by numeric prefix (lexicographic sort works due to fixed width)."""
    return sorted(steps, key=lambda p: p.name)
```

**Rationale**:
- Two-digit prefix ensures lexicographic sort matches numeric sort
- Simple sorted() call, no custom comparator needed
- Deterministic and predictable ordering

**Edge Cases Handled**:
- Gaps in numbering (00, 02, 05): Works correctly, runs in order
- Out-of-order discovery: sorted() fixes it
- Duplicate prefixes: Detected separately in validation

**Alternatives Considered**:
- Extract and sort by integer: Rejected - unnecessary with fixed-width prefixes
- Configuration file ordering: Rejected - defeats purpose of self-documenting names

### 4. Duplicate Prefix Detection

**Decision**: Validate uniqueness of numeric prefixes before execution

**Implementation**:
```python
def validate_step_prefixes(steps: list[Path]) -> None:
    """Ensure no duplicate numeric prefixes."""
    prefixes = [step.name[:2] for step in steps]
    duplicates = {p for p in prefixes if prefixes.count(p) > 1}
    
    if duplicates:
        dup_files = [s.name for s in steps if s.name[:2] in duplicates]
        raise ValueError(
            f"Duplicate step prefixes found: {duplicates}. "
            f"Affected files: {dup_files}. "
            f"Each step must have a unique numeric prefix."
        )
```

**Rationale**:
- Fail fast with clear error message
- Lists all affected files for easy fixing
- Prevents non-deterministic behavior

**Alternatives Considered**:
- Allow duplicates, run alphabetically: Rejected - ambiguous intent
- Allow duplicates, run in discovery order: Rejected - non-deterministic

### 5. Browser Session Management Architecture

**Decision**: Move browser creation from Executor to Runner level

**Current Architecture** (Problem):
```python
class StepExecutor:
    async def execute_step(self, step: TestStep) -> TestResult:
        # Creates new browser for EACH step
        agent = await create_browser_use_agent(
            task=step.content,
            headless=self.headless,
            temperature=self.temperature
        )
        result = await agent.run()
        # Browser closes here automatically
```

**New Architecture** (Solution):
```python
class SuiteRunner:
    async def run_suite(self, suite: TestSuite) -> SuiteResult:
        # Create browser ONCE for entire scenario
        browser = Browser(headless=self.headless)
        llm = create_llm(temperature=suite.config.temperature)
        
        try:
            for step in suite.steps:
                # Reuse browser across steps
                result = await executor.execute_step(
                    step=step,
                    browser=browser,
                    llm=llm,
                    timeout=suite.config.step_timeout
                )
                test_results.append(result)
        finally:
            await browser.close()  # Clean up

class StepExecutor:
    async def execute_step(
        self,
        step: TestStep,
        browser: Browser,  # Received, not created
        llm: Any,
        timeout: int
    ) -> TestResult:
        # Create agent with existing browser
        agent = Agent(task=step.content, llm=llm, browser=browser)
        result = await agent.run()
        # Browser stays open
```

**Rationale**:
- Runner orchestrates scenario lifecycle, owns resources
- Executor focuses on step execution, receives dependencies
- Clean separation of concerns (Single Responsibility Principle)
- Browser cleanup in finally block ensures proper teardown

**Alternatives Considered**:
- Context manager for browser: Considered but async context managers add complexity
- Browser pool/reuse across scenarios: Rejected - breaks scenario independence
- Keep in Executor, add "reuse" flag: Rejected - violates dependency injection

### 6. Verbose Logging for Skipped Files

**Decision**: Log skipped files after step execution completes

**Implementation**:
```python
def log_skipped_files(skipped: list[Path], logger: Logger) -> None:
    """Log non-numbered files that were skipped."""
    if not skipped:
        return
    
    logger.info(f"Skipped {len(skipped)} non-numbered files:")
    for filepath in sorted(skipped):
        logger.info(f"  Skipped file (no numeric prefix): {filepath.name}")
```

**Timing**: After all steps complete, before scenario summary

**Rationale**:
- Doesn't clutter step execution logs
- Groups all skipped files together for clarity
- Uses INFO level (informational, not warning)
- Alphabetical order for consistency

**Alternatives Considered**:
- Log during discovery: Rejected - too early, users haven't seen steps yet
- Log each skip inline with steps: Rejected - clutters step output
- Don't log at all: Rejected - users need visibility into what's skipped

### 7. Browser State Persistence

**Decision**: Rely on browser-use's built-in state management

**browser-use Guarantees**:
- Cookies persist across Agent.run() calls with same Browser instance
- Navigation history maintained
- Local storage and session storage preserved
- Page context remains active

**Verification Strategy**:
```python
# Test that demonstrates state persistence
async def test_cumulative_steps():
    browser = Browser(headless=True)
    llm = create_llm()
    
    # Step 1: Login
    agent1 = Agent(task="Login with test credentials", llm=llm, browser=browser)
    await agent1.run()
    
    # Step 2: Navigate (should be logged in)
    agent2 = Agent(task="Navigate to dashboard", llm=llm, browser=browser)
    await agent2.run()
    # Cookies from step 1 are still present
    
    await browser.close()
```

**Rationale**:
- browser-use handles persistence natively, no custom code needed
- Each Agent instance shares the same Browser instance
- State management is browser-use's responsibility

**Alternatives Considered**:
- Manual cookie/storage management: Rejected - reinvents the wheel
- Snapshot/restore between steps: Rejected - unnecessary with proper architecture

## Best Practices Research

### Pattern: Database Migration Naming

**Finding**: Django, Rails, Alembic all use numeric prefixes for ordering

**Examples**:
- Django: `0001_initial.py`, `0002_add_user_email.py`
- Rails: `20231113120000_create_users.rb`
- Alembic: `001_initial.py`, `002_add_column.py`

**Application**: Our `00-`, `01-`, `02-` pattern follows established conventions

### Pattern: Resource Lifecycle Management

**Finding**: Pytest fixtures use setup/teardown with proper cleanup

**Application**: Runner's browser management mirrors fixture pattern:
```python
async def run_suite(self, suite: TestSuite) -> SuiteResult:
    browser = Browser(...)  # Setup
    try:
        # Use resource
        for step in suite.steps:
            await executor.execute_step(..., browser=browser)
    finally:
        await browser.close()  # Teardown
```

### Pattern: Dependency Injection

**Finding**: Clean Architecture advocates passing dependencies explicitly

**Application**: Executor receives browser instead of creating it:
- Testable (can inject mock browser)
- Flexible (different browser configurations)
- Clear dependencies (visible in signature)

## Implementation Checklist

- [ ] Update discovery.py with step filtering and ordering logic
- [ ] Add prefix validation in parser.py
- [ ] Modify executor.py to receive browser parameter
- [ ] Refactor runner.py to create browser once per scenario
- [ ] Add skipped file logging in logging module
- [ ] Update existing tests for new behavior
- [ ] Add tests for step ordering logic
- [ ] Add tests for session persistence
- [ ] Rename example step files to use numeric prefixes
- [ ] Update documentation with naming convention

## Risk Assessment

### Low Risk
- ✅ Step ordering logic (simple, well-tested pattern)
- ✅ File filtering (regex is explicit and testable)
- ✅ Verbose logging (additive, no breaking changes)

### Medium Risk
- ⚠️ Browser session refactoring (signature changes to Executor)
- ⚠️ Existing scenarios without prefixes will break (but with clear error)

### Mitigation Strategies
- Comprehensive unit tests for ordering logic
- Integration tests for session persistence
- Clear error messages guide users to fix unprefixed files
- Migration guide in documentation

## References

- browser-use Browser documentation: https://docs.browser-use.com/browser
- browser-use Agent documentation: https://docs.browser-use.com/agent
- Python regex documentation: https://docs.python.org/3/library/re.html
- Pytest async fixtures: https://pytest-asyncio.readthedocs.io/

