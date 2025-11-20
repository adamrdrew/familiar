# System Prompt Implementation Summary

**Date**: 2025-11-19  
**Branch**: `007-agent-instructions`  
**Feature**: Base System Prompt Support

## Overview

Added support for a base system prompt that is always loaded and combined with fast mode instructions and agent.md files. The system prompt provides foundational instructions to the AI agent and is stored in `system_prompt.md` in the repository root.

## Changes Made

### 1. Created System Prompt File

**File**: `/Users/adam/Development/familiar/system_prompt.md`

- Created stub file with placeholder content
- Located in repository root (not in familiar/ directory)
- User can update with actual prompt text later

### 2. Added System Prompt Reader Function

**File**: `src/familiar/core/parser.py`

Added `read_system_prompt()` function:
- Reads `system_prompt.md` file with encoding fallback (UTF-8 → latin-1)
- Returns `None` if file doesn't exist or can't be read
- Logs INFO messages if file missing or empty
- Logs WARNING for encoding issues or read errors
- Similar to `read_agent_instructions()` but with different logging behavior

### 3. Updated System Message Builder

**File**: `src/familiar/core/runner.py`

Updated `build_system_message()` function:
- Added `base_system_prompt` as first parameter
- Reordered component priority:
  1. **Base system prompt** (foundational instructions) - NEW
  2. Fast mode prompt (behavioral instructions)
  3. Global agent instructions (app-wide context)
  4. Scenario agent instructions (test-specific context)
- Updated docstring to reflect new parameter and order

### 4. Updated SuiteRunner

**File**: `src/familiar/core/runner.py`

Modified `SuiteRunner.__init__()`:
- Added `base_system_prompt: str | None = None` parameter
- Stored as instance variable `self.base_system_prompt`
- Updated docstring

Modified `SuiteRunner.run_suite()`:
- Passes `base_system_prompt` to `build_system_message()`
- Updated comment to mention base prompt

### 5. Updated CLI Command Handler

**File**: `src/familiar/cli/run.py`

Updated `run_suite_command()`:
- Added import for `read_system_prompt`
- Reads system prompt from repo root: `Path.cwd() / "system_prompt.md"`
- Passes `base_system_prompt` to both async run functions

Updated `run_suite_async()`:
- Added `base_system_prompt` parameter
- Passes to `SuiteRunner` constructor
- Updated docstring

Updated `run_all_suites_async()`:
- Added `base_system_prompt` parameter
- Passes to `SuiteRunner` constructor
- Updated docstring

## Prompt Combination Order

The system now combines prompts in the following order:

```python
# If all components are present:
combined_message = f"""
{base_system_prompt}

{SPEED_OPTIMIZATION_PROMPT}

{global_agent_instructions}

{scenario_agent_instructions}
"""
```

**Rationale**:
1. **Base system prompt** - Foundational instructions (always present if file exists)
2. **Fast mode prompt** - Behavioral modifications (when --fast flag used)
3. **Global agent.md** - Application-wide context (when agent.md in familiar root)
4. **Scenario agent.md** - Test-specific context (when agent.md in suite directory)

## File Locations

- **Base system prompt**: `{repo_root}/system_prompt.md`
- **Global agent instructions**: `{familiar_root}/agent.md`
- **Scenario agent instructions**: `{suite_dir}/agent.md`

## Backward Compatibility

✅ **Fully backward compatible**

- All new parameters have default values (`None`)
- System prompt is optional (returns `None` if file doesn't exist)
- Existing code runs unchanged without `system_prompt.md`
- No breaking changes to any public APIs

## Testing

Verified:
- ✅ Imports successful
- ✅ System prompt file can be read (591 chars loaded)
- ✅ `build_system_message()` combines components correctly
- ✅ Component order is correct: base → fast → global → scenario
- ✅ No linter errors in modified files

## Usage

1. **Create/update system_prompt.md** in repo root with desired instructions
2. **Run tests normally** - system prompt is automatically loaded:
   ```bash
   familiar run familiar/my-suite
   ```
3. **With fast mode** - system prompt + fast mode instructions:
   ```bash
   familiar run familiar/my-suite --fast
   ```
4. **With agent.md files** - all prompts combined:
   ```bash
   # System prompt + global agent.md + scenario agent.md
   familiar run familiar/my-suite
   ```

## Next Steps

1. User to update `system_prompt.md` with actual prompt content
2. Consider adding tests for system prompt reading
3. Update documentation with system prompt usage examples
4. Consider adding CLI flag to override system prompt location (if needed)

## Files Modified

1. `/Users/adam/Development/familiar/system_prompt.md` (created)
2. `/Users/adam/Development/familiar/src/familiar/core/parser.py`
3. `/Users/adam/Development/familiar/src/familiar/core/runner.py`
4. `/Users/adam/Development/familiar/src/familiar/cli/run.py`

## Implementation Complete ✓

All TODOs completed:
- ✅ Create stub system_prompt.md file in repo root
- ✅ Add function to read system_prompt.md at startup
- ✅ Update build_system_message to include base prompt first
- ✅ Update runner to pass system prompt to build_system_message
- ✅ Update CLI to read and pass system prompt to runner

