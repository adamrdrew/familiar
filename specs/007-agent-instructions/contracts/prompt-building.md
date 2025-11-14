# Contract: System Message Building

**Function**: `build_system_message()`  
**Module**: `src/familiar/core/runner.py`  
**Purpose**: Combine fast mode prompt and agent instructions into system message  
**Version**: 1.0

## Function Signature

```python
def build_system_message(
    fast_mode: bool,
    global_agent_md: Optional[str],
    scenario_agent_md: Optional[str],
    override_flag: bool
) -> Optional[str]:
    """Build combined system message from fast mode and agent instructions.
    
    Combines components in priority order:
    1. Fast mode prompt (behavioral instructions)
    2. Global agent instructions (app-wide context)
    3. Scenario agent instructions (test-specific context)
    
    Args:
        fast_mode: Whether fast mode is enabled.
        global_agent_md: Global agent instructions content (or None).
        scenario_agent_md: Scenario agent instructions content (or None).
        override_flag: If True, ignore global_agent_md when scenario_agent_md exists.
        
    Returns:
        Combined system message string, or None if no components present.
    """
```

## Input Contract

| Parameter | Type | Required | Valid Values | Notes |
|-----------|------|----------|--------------|-------|
| `fast_mode` | `bool` | Yes | `True`, `False` | Whether fast mode is enabled |
| `global_agent_md` | `Optional[str]` | Yes | Any string or `None` | Global agent instructions |
| `scenario_agent_md` | `Optional[str]` | Yes | Any string or `None` | Scenario agent instructions |
| `override_flag` | `bool` | Yes | `True`, `False` | Whether to ignore global when scenario exists |

**Preconditions**:
- All string inputs (if provided) should be non-empty after stripping
- Empty strings should be treated as `None`

## Output Contract

| Return Type | Conditions | Value |
|-------------|------------|-------|
| `str` | At least one component present | Combined message with components separated by `\n\n` |
| `None` | No components present | `None` |

**Component Order** (when present):
1. Fast mode prompt (from `SPEED_OPTIMIZATION_PROMPT` constant)
2. Global agent instructions (unless `override_flag=True` and `scenario_agent_md` present)
3. Scenario agent instructions

**Separator**: Components are joined with `"\n\n"` (double newline)

## Behavior Specifications

### Test Case 1: No Components
```python
result = build_system_message(
    fast_mode=False,
    global_agent_md=None,
    scenario_agent_md=None,
    override_flag=False
)
assert result is None
```

### Test Case 2: Fast Mode Only
```python
result = build_system_message(
    fast_mode=True,
    global_agent_md=None,
    scenario_agent_md=None,
    override_flag=False
)
assert result == SPEED_OPTIMIZATION_PROMPT
assert "\n\n" not in result  # No double newline (single component)
```

### Test Case 3: Global Agent Only
```python
result = build_system_message(
    fast_mode=False,
    global_agent_md="Global context",
    scenario_agent_md=None,
    override_flag=False
)
assert result == "Global context"
```

### Test Case 4: Scenario Agent Only
```python
result = build_system_message(
    fast_mode=False,
    global_agent_md=None,
    scenario_agent_md="Scenario context",
    override_flag=False
)
assert result == "Scenario context"
```

### Test Case 5: Fast Mode + Global Agent
```python
result = build_system_message(
    fast_mode=True,
    global_agent_md="Global context",
    scenario_agent_md=None,
    override_flag=False
)
expected = f"{SPEED_OPTIMIZATION_PROMPT}\n\nGlobal context"
assert result == expected
```

### Test Case 6: Fast Mode + Scenario Agent
```python
result = build_system_message(
    fast_mode=True,
    global_agent_md=None,
    scenario_agent_md="Scenario context",
    override_flag=False
)
expected = f"{SPEED_OPTIMIZATION_PROMPT}\n\nScenario context"
assert result == expected
```

### Test Case 7: Global + Scenario (No Override)
```python
result = build_system_message(
    fast_mode=False,
    global_agent_md="Global context",
    scenario_agent_md="Scenario context",
    override_flag=False
)
expected = "Global context\n\nScenario context"
assert result == expected
```

### Test Case 8: Global + Scenario (With Override)
```python
result = build_system_message(
    fast_mode=False,
    global_agent_md="Global context",
    scenario_agent_md="Scenario context",
    override_flag=True
)
# Global is ignored due to override flag
assert result == "Scenario context"
```

### Test Case 9: All Components (No Override)
```python
result = build_system_message(
    fast_mode=True,
    global_agent_md="Global context",
    scenario_agent_md="Scenario context",
    override_flag=False
)
expected = f"{SPEED_OPTIMIZATION_PROMPT}\n\nGlobal context\n\nScenario context"
assert result == expected
```

### Test Case 10: All Components (With Override)
```python
result = build_system_message(
    fast_mode=True,
    global_agent_md="Global context",
    scenario_agent_md="Scenario context",
    override_flag=True
)
# Global is ignored, only fast mode + scenario
expected = f"{SPEED_OPTIMIZATION_PROMPT}\n\nScenario context"
assert result == expected
```

### Test Case 11: Override Flag with No Scenario
```python
result = build_system_message(
    fast_mode=False,
    global_agent_md="Global context",
    scenario_agent_md=None,
    override_flag=True
)
# Override flag has no effect when no scenario present
# Global is still used
assert result == "Global context"
```

## Error Handling

**This function MUST NOT raise exceptions.**

| Scenario | Behavior |
|----------|----------|
| Invalid type for `fast_mode` | Type error (caller responsibility) |
| Invalid type for `override_flag` | Type error (caller responsibility) |
| Empty strings in agent instructions | Treat as `None` |
| Very long strings (>1MB) | Accept (no validation) |

## Performance Requirements

| Metric | Requirement |
|--------|-------------|
| Execution time | <1ms for typical inputs (<100KB total) |
| Memory | O(n) where n is total length of inputs |
| Thread safety | Pure function, thread-safe |

## Dependencies

- `SPEED_OPTIMIZATION_PROMPT` constant (defined in same module)
- No external dependencies

## Versioning

- **Version 1.0**: Initial implementation
- **Breaking Changes**: Changes to parameter order, return type, or component order
- **Non-Breaking**: Changes to separator, internal logic (if behavior preserved)

