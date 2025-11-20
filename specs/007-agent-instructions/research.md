# Research: Agent Instructions

**Branch**: `007-agent-instructions` | **Date**: 2025-11-14 | **Spec**: [spec.md](spec.md)  
**Input**: Technical unknowns from implementation plan

## 1. File Encoding Handling Strategy

**Question**: How should we handle different file encodings for agent.md files?

### Research Findings

**Python's Default Behavior**:
- `open(file, encoding='utf-8')` is explicit and recommended
- Files without encoding parameter use platform default (varies by OS)
- UTF-8 is the de facto standard for text files in modern development

**Best Practices**:
- Python standard library `pathlib.Path.read_text()` accepts encoding parameter
- Graceful degradation: UTF-8 → latin-1 (covers most cases)
- Log warnings for encoding issues

### Decision

**Use explicit UTF-8 encoding with error handling**:

```python
def read_agent_instructions(path: Path) -> Optional[str]:
    """Read agent instructions from file with encoding fallback."""
    if not path.exists():
        return None
    
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback to latin-1 (covers most non-UTF-8 cases)
        try:
            content = path.read_text(encoding='latin-1')
            logger.warning(f"agent.md at {path} is not UTF-8, used latin-1 fallback")
            return content
        except Exception as e:
            logger.warning(f"Could not read agent.md at {path}: {e}")
            return None
    except Exception as e:
        logger.warning(f"Could not read agent.md at {path}: {e}")
        return None
```

**Rationale**: UTF-8 is standard, fallback ensures robustness, warnings alert users to issues.

---

## 2. Error Handling Patterns for Missing/Malformed Files

**Question**: How should we handle various file error scenarios?

### Research Findings

**Error Scenarios**:
1. **File doesn't exist** → Expected (optional feature), no warning
2. **Encoding issues** → Log warning, skip file
3. **Permission denied** → Log warning, skip file
4. **File is empty** → Treat as "no instructions" (skip)
5. **File is very large (>100KB)** → Log warning, but still use (edge case)

**Existing Patterns in Familiar**:
- `.env` file loading: Optional, silent if missing
- `suite.yaml` parsing: Required, error if missing/malformed
- Test step files: Required, error if issues

### Decision

**Adopt .env file pattern (optional + graceful degradation)**:

| Scenario | Behavior | Log Level | User Impact |
|----------|----------|-----------|-------------|
| File missing | Skip silently | None | No impact (optional feature) |
| Encoding error | Skip with warning | WARNING | Feature disabled for that file |
| Permission error | Skip with warning | WARNING | Feature disabled for that file |
| Empty file | Skip silently | None | Treated as "no instructions" |
| Large file (>100KB) | Use with warning | WARNING | Works but alerts user |

**Rationale**: Matches user expectations for optional configuration files. Errors don't break tests, just disable the feature gracefully.

---

## 3. System Message Combination Order

**Question**: When combining fast mode prompt and agent instructions, what should the order be?

### Research Findings

**LLM Prompt Engineering Best Practices**:
- System messages establish context and behavioral guidelines
- Earlier content in system message has higher "authority"
- General context should come before specific instructions
- Recency bias: Recent context is more influential for immediate actions

**Familiar's Fast Mode Prompt**:
```text
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
```
This is **behavioral** (how to act).

**Agent Instructions** (expected content):
- Domain-specific context (what the app does)
- UI quirks and patterns (what to expect)
- Test-specific guidance (what to focus on)
This is **contextual** (what to know).

### Decision

**Order: Fast Mode Prompt → Global Agent.md → Scenario Agent.md**

```python
def build_system_message(
    fast_mode: bool,
    global_agent_md: Optional[str],
    scenario_agent_md: Optional[str],
    override_flag: bool
) -> Optional[str]:
    """Build combined system message from components.
    
    Order of components:
    1. Fast mode prompt (behavioral - how to act)
    2. Global agent instructions (app context - what to know)
    3. Scenario agent instructions (test context - specific details)
    """
    components = []
    
    # 1. Behavioral instructions (fast mode)
    if fast_mode:
        components.append(SPEED_OPTIMIZATION_PROMPT)
    
    # 2. General context (global agent.md)
    if not override_flag and global_agent_md:
        components.append(global_agent_md)
    
    # 3. Specific context (scenario agent.md)
    if scenario_agent_md:
        components.append(scenario_agent_md)
    
    return "\n\n".join(components) if components else None
```

**Rationale**: 
- Fast mode is behavioral (how to work) → comes first to set working style
- Global context is general (app-wide knowledge) → comes second
- Scenario context is specific (test-specific details) → comes last for recency

**Separator**: Use `\n\n` (double newline) to clearly separate sections.

---

## 4. Global Agent.md Discovery Strategy

**Question**: How do we find the "familiar root" directory for global agent.md?

### Research Findings

**Current Familiar Behavior**:
- Test suites are discovered in a specified directory (e.g., `familiar/`)
- Each suite is a subdirectory with `suite.yaml`
- The discovery directory can be specified via CLI or defaults to `./familiar`

**Discovery Options**:
1. **Use discovery directory as familiar root** (where suites are discovered)
2. **Use current working directory** (where command is run)
3. **Search upward for marker file** (like git does with .git)

**Existing Code** (`cli/run.py`):
```python
def run_all_suites_async(
    directory: Optional[Path] = None,
    ...
):
    """Run all suites in a directory."""
    root_dir = directory or Path("./familiar")
    discovery = TestSuiteDiscovery()
    suites = discovery.discover_suites(root_dir)
```

The `root_dir` is where suites are discovered.

### Decision

**Use the discovery directory (suite root) as the familiar root**

Implementation:
```python
# In cli/run.py or core/discovery.py
def find_global_agent_instructions(root_dir: Path) -> Optional[str]:
    """Find and read global agent.md in the familiar root directory.
    
    Args:
        root_dir: The root directory where test suites are located
        
    Returns:
        Content of agent.md if found, None otherwise
    """
    agent_file = root_dir / "agent.md"
    return read_agent_instructions(agent_file)
```

**Rationale**: 
- Logical location: Global agent.md lives alongside suite directories
- Consistent with suite organization
- No ambiguity about location
- Easy to document: "Put agent.md in the same directory as your test suites"

**Example Structure**:
```
familiar/
├── agent.md                    ← Global instructions
├── login-flow/
│   ├── suite.yaml
│   ├── agent.md                ← Scenario-specific instructions
│   ├── 00-navigate.md
│   └── 01-login.md
└── checkout-flow/
    ├── suite.yaml
    └── 00-select-product.md
```

---

## 5. Implementation Pattern: Where to Read Files

**Question**: Where in the code flow should agent.md files be read?

### Research Findings

**Current File Reading Patterns in Familiar**:

1. **.env files** → Read in `cli/run.py` before execution
2. **suite.yaml** → Read in `core/parser.py::parse_suite()`
3. **Test step files** → Read in `core/parser.py::_parse_step()`

**Options for agent.md**:
- **Option A**: Read in parser (when parsing suite)
- **Option B**: Read in runner (when creating browser/LLM)
- **Option C**: Read in CLI (before running suites)

### Decision

**Read scenario agent.md in parser, global agent.md in discovery**

**For Scenario agent.md** (in `core/parser.py`):
```python
def parse_suite(self, suite_path: Path) -> TestSuite:
    """Parse a test suite from a directory."""
    # ... existing code ...
    
    # Read agent instructions if present
    agent_file = suite_path / "agent.md"
    agent_instructions = read_agent_instructions(agent_file)
    
    return TestSuite(
        name=config.name,
        path=suite_path,
        config=config,
        steps=steps,
        agent_instructions=agent_instructions,  # NEW
    )
```

**For Global agent.md** (in `core/discovery.py` or `cli/run.py`):
```python
# In cli/run.py before running
root_dir = directory or Path("./familiar")
global_agent_instructions = find_global_agent_instructions(root_dir)

# Pass to runner
runner = SuiteRunner(
    headless=headless,
    fast_mode=fast_mode,
    scenario_agent_override=scenario_agent_override,
    global_agent_instructions=global_agent_instructions,  # NEW
)
```

**Rationale**:
- **Scenario agent.md**: Belongs to suite → read with suite (parser responsibility)
- **Global agent.md**: Applies to all suites → read once at discovery/CLI level
- Separation of concerns: Parser handles suite-specific, CLI/discovery handles global
- Efficient: Global read once, scenario read per-suite

---

## 6. Size Limits and Performance

**Question**: Should we enforce size limits on agent.md files?

### Research Findings

**Typical LLM System Message Limits**:
- Anthropic Claude: ~200K tokens (~800KB of text)
- OpenAI GPT-4: ~128K tokens (~512KB of text)
- Browser-use default: No specific limit documented

**Reasonable Agent Instructions**:
- Simple context: 100-500 words (1-3KB)
- Detailed context: 500-2000 words (3-12KB)
- Comprehensive guide: 2000-5000 words (12-30KB)

**Performance Impact**:
- File reading: <1ms for files <100KB
- String concatenation: Negligible (<1ms)
- LLM processing: Depends on content, but system message is processed once

### Decision

**No hard limit, but warn for files >100KB**

```python
def read_agent_instructions(path: Path) -> Optional[str]:
    """Read agent instructions with size warning."""
    if not path.exists():
        return None
    
    # Check size before reading
    file_size = path.stat().st_size
    if file_size > 100 * 1024:  # 100KB
        logger.warning(
            f"agent.md at {path} is large ({file_size / 1024:.1f}KB). "
            "Consider keeping instructions concise for better results."
        )
    
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # ... fallback logic ...
```

**Rationale**:
- No artificial limits (let LLM providers enforce their limits)
- Warning educates users about best practices
- Performance impact is minimal even for large files
- Flexibility for power users who need detailed instructions

---

## Summary of Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| **File Encoding** | UTF-8 with latin-1 fallback | Standard + robust |
| **Error Handling** | Optional pattern (skip with warnings) | Matches user expectations |
| **Combination Order** | Fast mode → Global → Scenario | Behavioral → General → Specific |
| **Global Discovery** | Use discovery/root directory | Logical, consistent |
| **Read Locations** | Parser (scenario), CLI (global) | Separation of concerns |
| **Size Limits** | No limit, warn >100KB | Flexible + educate |

All technical unknowns resolved. Ready for Phase 1 design.

