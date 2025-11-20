# Contract: Agent Instructions File Reading

**Function**: `read_agent_instructions()`  
**Module**: `src/familiar/core/parser.py` or `src/familiar/utils/`  
**Purpose**: Read agent instructions from file with robust error handling  
**Version**: 1.0

## Function Signature

```python
def read_agent_instructions(path: Path) -> Optional[str]:
    """Read agent instructions from file with robust error handling.
    
    Args:
        path: Path to agent.md file
        
    Returns:
        File content as string, or None if file doesn't exist or can't be read
        
    Error Handling:
        - File not found: Returns None (no warning)
        - Encoding error: Returns None with WARNING log
        - Permission error: Returns None with WARNING log
        - Empty file: Returns None (no warning)
        - Large file (>100KB): Returns content with WARNING log
    """
```

## Input Contract

| Parameter | Type | Required | Valid Values | Notes |
|-----------|------|----------|--------------|-------|
| `path` | `pathlib.Path` | Yes | Any valid Path object | Can be relative or absolute |

**Preconditions**: None (function handles all error cases)

## Output Contract

| Return Type | Conditions | Value |
|-------------|------------|-------|
| `str` | File exists and readable | File content (whitespace preserved) |
| `None` | File doesn't exist | `None` (no log) |
| `None` | File empty (0 bytes) | `None` (no log) |
| `None` | Encoding error | `None` + WARNING log |
| `None` | Permission error | `None` + WARNING log |
| `str` | File >100KB | Content + WARNING log |

**Post-processing**:
- No automatic stripping of whitespace
- No line ending normalization
- Content returned as-is from file

## Behavior Specifications

### Test Case 1: File Doesn't Exist
```python
path = Path("/nonexistent/agent.md")
result = read_agent_instructions(path)
assert result is None
# No log output expected
```

### Test Case 2: File Exists and Valid
```python
# Given: agent.md contains "Test instructions"
path = Path("agent.md")
result = read_agent_instructions(path)
assert result == "Test instructions"
```

### Test Case 3: Empty File
```python
# Given: agent.md is empty (0 bytes)
path = Path("agent.md")
result = read_agent_instructions(path)
assert result is None
# No log output expected
```

### Test Case 4: File with Only Whitespace
```python
# Given: agent.md contains only spaces/newlines
path = Path("agent.md")
result = read_agent_instructions(path)
assert result is not None  # Whitespace IS returned
assert result.strip() == ""  # But is only whitespace
# Caller responsible for handling whitespace-only content
```

### Test Case 5: UTF-8 File
```python
# Given: agent.md contains UTF-8 text with emoji
path = Path("agent.md")
result = read_agent_instructions(path)
assert "🚀" in result  # UTF-8 properly decoded
```

### Test Case 6: Non-UTF-8 File (Latin-1)
```python
# Given: agent.md is encoded as Latin-1
path = Path("agent.md")
result = read_agent_instructions(path)
assert result is not None  # Fallback succeeded
# WARNING log expected: "agent.md at ... is not UTF-8, used latin-1 fallback"
```

### Test Case 7: Corrupted File (Unreadable)
```python
# Given: agent.md has encoding issues beyond latin-1
path = Path("agent.md")
result = read_agent_instructions(path)
assert result is None
# WARNING log expected: "Could not read agent.md at ..."
```

### Test Case 8: Permission Denied
```python
# Given: agent.md exists but no read permission
path = Path("agent.md")
result = read_agent_instructions(path)
assert result is None
# WARNING log expected: "Could not read agent.md at ... Permission denied"
```

### Test Case 9: Large File (>100KB)
```python
# Given: agent.md is 150KB
path = Path("agent.md")
result = read_agent_instructions(path)
assert result is not None  # Content still returned
assert len(result) > 100 * 1024  # Verify size
# WARNING log expected: "agent.md at ... is large (150.0KB)..."
```

### Test Case 10: Multiline File
```python
# Given: agent.md contains multiple lines
path = Path("agent.md")
result = read_agent_instructions(path)
assert "\n" in result  # Line endings preserved
assert result.count("\n") > 0
```

## Error Handling

**This function MUST NOT raise exceptions** (all errors result in `None` + optional warning).

| Error Type | Behavior | Log Level | Return |
|------------|----------|-----------|--------|
| `FileNotFoundError` | Silent | None | `None` |
| `UnicodeDecodeError` | Fallback to latin-1 | WARNING (if fallback fails) | Content or `None` |
| `PermissionError` | Log warning | WARNING | `None` |
| `OSError` | Log warning | WARNING | `None` |
| `IOError` | Log warning | WARNING | `None` |
| File >100KB | Log warning | WARNING | Content |
| Empty file | Silent | None | `None` |

## Logging Contract

**Warning Messages**:

1. **Latin-1 Fallback**:
   ```
   agent.md at {path} is not UTF-8, used latin-1 fallback
   ```

2. **Large File**:
   ```
   agent.md at {path} is large ({size}KB). Consider keeping instructions concise for better results.
   ```

3. **Read Error**:
   ```
   Could not read agent.md at {path}: {error_message}
   ```

## Performance Requirements

| Metric | Requirement |
|--------|-------------|
| File read time | <5ms for files <100KB |
| File stat time | <1ms |
| Memory | O(n) where n is file size |
| Thread safety | Safe (no shared state) |

## Dependencies

- `pathlib.Path` (standard library)
- `logging` (for warnings)
- No external dependencies

## Implementation Notes

**Encoding Strategy**:
1. Try UTF-8 first (explicit encoding)
2. If `UnicodeDecodeError`, try latin-1
3. If still fails, return `None` with warning

**Size Check**:
- Check file size with `path.stat().st_size` before reading
- Warn if >100KB but still read the file
- No hard size limit enforced

**Line Endings**:
- Do NOT normalize line endings
- Preserve original content exactly as in file
- Python's `read_text()` handles platform differences

## Versioning

- **Version 1.0**: Initial implementation
- **Breaking Changes**: Changes to return type, error handling behavior
- **Non-Breaking**: Changes to log messages, size threshold, encoding fallback order

