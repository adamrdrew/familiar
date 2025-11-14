# CLI Contract: --fast Flag

**Feature**: Fast Mode Performance Optimization  
**Command**: `familiar run`  
**Flag**: `--fast`  
**Type**: Boolean flag (no parameters)

---

## Purpose

Enable speed optimizations for test execution:
- LLM flash mode (skip verbose thinking output)
- Speed optimization system prompt (encourage concise responses)
- Works with any browser timing configuration

---

## Signature

```bash
familiar run SUITE_PATH [OPTIONS]
```

### Options

```
--fast              Enable speed optimizations
                    (flash mode, speed-optimized prompts)
```

---

## Behavior

### When --fast is Present

**LLM Configuration**:
- `flash_mode=True` on Agent (disables verbose LLM thinking)
- `extend_system_message` includes speed optimization prompt
- Temperature from suite.yaml used unchanged

**Browser Configuration**:
- Uses browser_profile from suite.yaml (if present)
- Uses default timing if browser_profile omitted
- Respects --no-headless flag

**Expected Impact**:
- 40-60% faster LLM inference
- No change to browser timing (controlled by suite.yaml)
- May reduce reliability for complex reasoning tasks

### When --fast is Absent (Default)

**LLM Configuration**:
- `flash_mode=False` (normal LLM output with thinking)
- No speed optimization prompt injected
- Standard agent behavior

**Browser Configuration**:
- Uses browser_profile from suite.yaml (if present)
- Uses default timing if browser_profile omitted

**Expected Impact**:
- Standard execution speed
- Full LLM reasoning output
- Maximum reliability

---

## Usage Examples

### Example 1: Basic Fast Mode

```bash
familiar run tests/login-flow --fast
```

**Effect**:
- Enables flash mode
- Injects speed optimization prompt
- Uses suite.yaml browser timing (or defaults)

### Example 2: Fast Mode + Verbose

```bash
familiar run tests/login-flow --fast --verbose
```

**Effect**:
- Enables fast mode
- Shows detailed logs including speed optimization prompt
- Useful for debugging fast mode behavior

### Example 3: Fast Mode + Headed Browser

```bash
familiar run tests/login-flow --fast --no-headless
```

**Effect**:
- Enables fast mode
- Shows browser window (overrides suite.yaml headless setting)
- Useful for development with speed optimization

### Example 4: Fast Mode + All Suites

```bash
familiar run tests/ --all --fast
```

**Effect**:
- Discovers all suites under tests/
- Runs each suite with fast mode enabled
- Applies speed optimization to entire test run

### Example 5: Standard Mode (No Flag)

```bash
familiar run tests/login-flow
```

**Effect**:
- Standard LLM behavior (no flash mode)
- Standard agent prompts (no speed optimization)
- Uses suite.yaml timing (or defaults)

---

## Flag Combinations

| Flags | Fast Mode | Verbose | Headless | Valid |
|-------|-----------|---------|----------|-------|
| (none) | No | No | Yes | ✅ |
| `--fast` | Yes | No | Yes | ✅ |
| `--verbose` | No | Yes | Yes | ✅ |
| `--fast --verbose` | Yes | Yes | Yes | ✅ |
| `--no-headless` | No | No | No | ✅ |
| `--fast --no-headless` | Yes | No | No | ✅ |
| `--all` | No | No | Yes | ✅ |
| `--all --fast` | Yes | No | Yes | ✅ |
| `--all --fast --verbose` | Yes | Yes | Yes | ✅ |

**All combinations are valid**. Flags are independent and composable.

---

## Implementation Details

### CLI Layer (src/familiar/cli/main.py)

```python
@click.command()
@click.argument("suite_path", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show detailed execution logs")
@click.option("--no-headless", is_flag=True, help="Run browser in headed mode")
@click.option("--all", "run_all", is_flag=True, help="Run all discovered suites")
@click.option("--fast", is_flag=True, help="Enable speed optimizations (flash mode, fast timing)")
def run(suite_path: str, verbose: bool, no_headless: bool, run_all: bool, fast: bool):
    """Run test suite(s) at the specified path."""
    runner = SuiteRunner(
        headless=not no_headless,
        fast_mode=fast,  # Pass to runner
    )
    # ... rest of implementation
```

### Runner Layer (src/familiar/core/runner.py)

```python
class SuiteRunner:
    def __init__(self, headless: bool = True, fast_mode: bool = False):
        self.headless = headless
        self.fast_mode = fast_mode
    
    async def run_suite(self, suite: TestSuite):
        # ... browser creation ...
        
        agent_kwargs = {
            "task": task,
            "llm": llm,
            "browser": browser,
        }
        
        if self.fast_mode:
            agent_kwargs["flash_mode"] = True
            agent_kwargs["extend_system_message"] = SPEED_OPTIMIZATION_PROMPT
        
        agent = Agent(**agent_kwargs)
        # ... execution ...
```

---

## Speed Optimization Prompt

When `--fast` is present, this prompt is injected:

```text
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
```

**Injection Method**: Appended to system message via `extend_system_message` parameter  
**Impact**: Encourages LLM to be faster and more direct  
**Location**: `src/familiar/core/runner.py` (module constant)

---

## Help Text

```bash
$ familiar run --help

Usage: familiar run [OPTIONS] SUITE_PATH

  Run test suite(s) at the specified path.

Options:
  -v, --verbose       Show detailed execution logs
  --no-headless       Run browser in headed mode
  --all               Run all discovered suites
  --fast              Enable speed optimizations (flash mode, reduced wait times)
                      Note: May reduce reliability for complex scenarios
  --help              Show this message and exit
```

---

## Exit Codes

| Code | Condition | Description |
|------|-----------|-------------|
| 0 | Success | All tests passed |
| 1 | Failure | One or more tests failed |
| 2 | Error | Invalid arguments or runtime error |

**Fast mode does NOT change exit codes**. Test failures still return exit code 1.

---

## Performance Expectations

### With --fast Flag

**Typical 3-Step Test**:
- Standard mode: ~25-30 seconds
- Fast mode: ~10-15 seconds
- **Speedup**: 40-50% (2-3x faster)

**Factors Affecting Speedup**:
- LLM provider (Groq/Gemini Flash = maximum speedup)
- Browser timing in suite.yaml
- Page complexity (simple pages = higher speedup)
- Network latency (local/fast sites = higher speedup)

### Without --fast Flag (Default)

**Typical 3-Step Test**:
- Baseline: ~25-30 seconds (with default 1.0s waits)
- With custom browser_profile: Varies by configuration

---

## Error Handling

### Invalid Flag Combinations

**All combinations are valid**. No exclusive flags.

### Runtime Errors

```bash
$ familiar run nonexistent-suite --fast
Error: Suite not found: nonexistent-suite
```

**Fast mode does NOT affect error messages or handling**.

---

## Backward Compatibility

### Existing Commands

```bash
# These continue to work unchanged
familiar run tests/login-flow
familiar run tests/login-flow --verbose
familiar run tests/login-flow --no-headless
familiar run tests/ --all
```

### New Commands

```bash
# New commands with --fast flag
familiar run tests/login-flow --fast
familiar run tests/ --all --fast
familiar run tests/login-flow --fast --verbose --no-headless
```

---

## Testing Requirements

### Unit Tests

```python
# tests/unit/test_cli.py

def test_run_command_accepts_fast_flag():
    """CLI should accept --fast flag without error."""
    result = runner.invoke(cli, ["run", "path/to/suite", "--fast"])
    assert result.exit_code == 0

def test_fast_flag_passed_to_runner():
    """--fast flag should be passed to SuiteRunner."""
    with patch("SuiteRunner") as mock_runner:
        runner.invoke(cli, ["run", "path/to/suite", "--fast"])
        mock_runner.assert_called_with(headless=True, fast_mode=True)
```

### Integration Tests

```python
# tests/integration/test_cli.py

async def test_fast_mode_execution():
    """Fast mode should reduce execution time."""
    # Run same suite with and without --fast
    # Verify fast mode is faster (with some tolerance)
    standard_time = measure_run("suite", fast=False)
    fast_time = measure_run("suite", fast=True)
    assert fast_time < standard_time * 0.7  # At least 30% faster
```

---

## Related Contracts

- `specs/004-fast-mode-performance/contracts/browser-profile-config.yaml` - Suite configuration
- `specs/001-ai-e2e-testing/contracts/cli-interface.md` - Base CLI contract

