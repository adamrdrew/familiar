# Contract: CLI Interface - Agent Instructions

**Command**: `familiar run`  
**New Flag**: `--scenario-agent-override`  
**Purpose**: Control agent instruction merging behavior  
**Version**: 1.0

## Command Signature

### Before (Current)
```bash
familiar run [SUITE_PATH_OR_NAME] [OPTIONS]

Options:
  -a, --all                       Run all discovered suites
  -f, --format [text|json|junit]  Output format
  --headless / --headed           Browser display mode
  -v, --verbose                   Show detailed logs
  --fast                          Enable speed optimizations
  --help                          Show this message and exit
```

### After (With Agent Instructions)
```bash
familiar run [SUITE_PATH_OR_NAME] [OPTIONS]

Options:
  -a, --all                       Run all discovered suites
  -f, --format [text|json|junit]  Output format
  --headless / --headed           Browser display mode
  -v, --verbose                   Show detailed logs
  --fast                          Enable speed optimizations
  --scenario-agent-override       Use only scenario agent.md (ignore global)
  --help                          Show this message and exit
```

## Flag Specification

### `--scenario-agent-override`

**Type**: Boolean flag (no argument)  
**Default**: `False` (not set)  
**Aliases**: None  
**Position**: Can appear anywhere in options

**Behavior**:
- When **NOT set** (default): Combine global and scenario agent.md (if both exist)
- When **set**: Use only scenario agent.md (ignore global agent.md)

**Effect Scope**: Applies to all suites in the run (when using `--all`)

## Usage Examples

### Example 1: Default Behavior (Combine Global + Scenario)
```bash
familiar run familiar/checkout-flow
```
- Reads `familiar/agent.md` (if exists) → global instructions
- Reads `familiar/checkout-flow/agent.md` (if exists) → scenario instructions
- Combines both in system message

### Example 2: Scenario Override
```bash
familiar run familiar/checkout-flow --scenario-agent-override
```
- Reads `familiar/agent.md` but **ignores it**
- Reads `familiar/checkout-flow/agent.md` → scenario instructions only
- Uses only scenario instructions in system message

### Example 3: Scenario Override with Fast Mode
```bash
familiar run familiar/checkout-flow --fast --scenario-agent-override
```
- Uses fast mode prompt
- **Ignores** global agent.md
- Uses scenario agent.md
- Combines: fast mode prompt + scenario instructions

### Example 4: Override with --all Flag
```bash
familiar run familiar/ --all --scenario-agent-override
```
- Runs all suites in `familiar/` directory
- For each suite: ignores global agent.md, uses only scenario agent.md
- Override applies to **all** suites in the run

### Example 5: Only Global Agent.md Exists
```bash
familiar run familiar/checkout-flow --scenario-agent-override
```
- `familiar/checkout-flow/agent.md` doesn't exist
- Override flag has no effect (no scenario to override with)
- **Still uses global agent.md** (fallback behavior)

### Example 6: No Agent.md Files Exist
```bash
familiar run familiar/checkout-flow --scenario-agent-override
```
- No agent.md files found
- Override flag has no effect
- Runs normally without agent instructions

## Implementation Contract

### CLI Layer (`cli/main.py`)

**Add Flag to run command**:
```python
@click.command()
@click.argument(...)
@click.option("--all", "-a", is_flag=True, help="Run all discovered suites")
@click.option("--format", ...)
@click.option("--headless", ...)
@click.option("--verbose", ...)
@click.option("--fast", is_flag=True, help="Enable speed optimizations")
@click.option(
    "--scenario-agent-override",
    is_flag=True,
    default=False,
    help="Use only scenario agent.md (ignore global)"
)
def run(..., scenario_agent_override: bool):
    """Run test suites."""
    ...
```

### Runner Layer (`cli/run.py`)

**Pass flag to runner**:
```python
def run_suite_command(
    ...,
    fast_mode: bool,
    scenario_agent_override: bool  # NEW parameter
):
    # Discover global agent instructions
    root_dir = Path("./familiar")  # Or from discovery
    global_agent_md = find_global_agent_instructions(root_dir)
    
    # Create runner with new parameters
    runner = SuiteRunner(
        headless=headless,
        fast_mode=fast_mode,
        scenario_agent_override=scenario_agent_override,  # Pass flag
        global_agent_instructions=global_agent_md,
    )
```

## Behavior Matrix

| Global agent.md | Scenario agent.md | Override Flag | Result |
|----------------|------------------|---------------|---------|
| ❌ No | ❌ No | `False` | No agent instructions |
| ❌ No | ❌ No | `True` | No agent instructions |
| ✅ Yes | ❌ No | `False` | Global only |
| ✅ Yes | ❌ No | `True` | Global only (fallback) |
| ❌ No | ✅ Yes | `False` | Scenario only |
| ❌ No | ✅ Yes | `True` | Scenario only |
| ✅ Yes | ✅ Yes | `False` | **Combined** (Global + Scenario) |
| ✅ Yes | ✅ Yes | `True` | **Scenario only** (Global ignored) |

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Flag used with invalid suite | Standard error (unrelated to flag) |
| Flag used without arguments | CLI shows help (standard click behavior) |
| Flag misspelled | Click error: "no such option" |
| Flag used multiple times | Last occurrence wins (standard click behavior) |

## Help Text

**Short Help** (in command list):
```
--scenario-agent-override  Use only scenario agent.md (ignore global)
```

**Long Help** (`familiar run --help`):
```
  --scenario-agent-override   Use only scenario-level agent.md instructions,
                             ignoring global agent.md. Has no effect if
                             scenario-level agent.md doesn't exist.
```

## Backward Compatibility

✅ **Fully Backward Compatible**

- Existing commands work unchanged (flag defaults to `False`)
- No breaking changes to command syntax
- Optional flag (not required)

### Before (Still Works)
```bash
familiar run familiar/checkout-flow
familiar run familiar/checkout-flow --fast
familiar run familiar/ --all
```

### After (New Capability)
```bash
familiar run familiar/checkout-flow --scenario-agent-override
familiar run familiar/checkout-flow --fast --scenario-agent-override
familiar run familiar/ --all --scenario-agent-override
```

## Testing Requirements

### Contract Tests

1. **Test flag is accepted** (doesn't error)
2. **Test flag default is False** (when not provided)
3. **Test flag can be set to True** (when provided)
4. **Test flag works with other flags** (--fast, --all, --verbose)
5. **Test help text includes flag** (--help output)

### Integration Tests

1. **Test override behavior with both files present**
2. **Test fallback when scenario missing**
3. **Test no effect when no files**
4. **Test with --all flag**

## Documentation Requirements

**Files to Update**:
1. `README.md` - CLI reference section
2. `docs/configuration.md` - CLI options section
3. `examples/` - Add example with agent.md + override usage

## Versioning

- **Version 1.0**: Initial implementation
- **Breaking Changes**: Renaming flag, changing default, removing flag
- **Non-Breaking**: Changing help text, adding aliases

