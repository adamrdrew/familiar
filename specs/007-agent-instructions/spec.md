# Feature Specification: Agent Instructions

**Feature Name**: Agent Instructions  
**Branch**: `007-agent-instructions`  
**Date**: 2025-11-14  
**Status**: Draft

## 1. Overview

This feature adds support for optional agent instructions that users can provide to guide the AI agent's behavior during test execution. Users can specify custom prompts via `agent.md` files that will be injected into the system message when creating the LLM.

## 2. Goals

The feature aims to:

1. Allow users to provide domain-specific context and instructions to the AI agent
2. Support hierarchical instruction configuration (global and scenario-specific)
3. Integrate seamlessly with existing fast mode optimizations
4. Maintain backward compatibility (completely optional)

## 3. Requirements

### 3.1. Functional Requirements

- **FR1**: The system MUST support reading agent instructions from `agent.md` files
- **FR2**: The system MUST support `agent.md` at two levels:
  - Global level: `{familiar_root}/agent.md`
  - Scenario level: `{scenario_dir}/agent.md`
- **FR3**: The system MUST combine global and scenario-level instructions by default
- **FR4**: The system MUST support a `--scenario-agent-override` CLI flag to use only scenario-level instructions
- **FR5**: The system MUST combine agent instructions with fast mode prompts when both are enabled
- **FR6**: The system MUST handle all combinations of fast mode and agent instructions:
  - No fast mode + no agent.md → run normal
  - Fast mode + no agent.md → use fast mode prompt
  - No fast mode + agent.md → use agent.md content
  - Fast mode + agent.md → combine both prompts
- **FR7**: Agent instructions MUST be attached to the system message when creating the LLM
- **FR8**: The feature MUST be completely optional (no breaking changes)

### 3.2. Non-Functional Requirements

- **NFR1**: **Backward Compatibility**: Existing test suites MUST run unchanged without agent.md files
- **NFR2**: **Performance**: Loading agent instructions MUST NOT significantly impact test execution time
- **NFR3**: **Maintainability**: The implementation MUST follow Constitution principles
- **NFR4**: **Usability**: Error messages MUST be clear if agent.md files have issues (encoding, permissions, etc.)

## 4. Technical Design

### 4.1. File Discovery

The system will search for `agent.md` files in the following order:

1. **Global agent.md**: `{familiar_root}/agent.md` (where test suite directories are located)
2. **Scenario agent.md**: `{scenario_dir}/agent.md` (where suite.yaml and test steps are)

### 4.2. Prompt Combination Logic

When creating the system message for the LLM:

```python
def build_system_message(fast_mode: bool, global_agent_md: Optional[str], 
                         scenario_agent_md: Optional[str], override_flag: bool) -> str:
    components = []
    
    # Add fast mode prompt if enabled
    if fast_mode:
        components.append(FAST_MODE_PROMPT)
    
    # Add agent instructions
    if override_flag and scenario_agent_md:
        # Only scenario-level
        components.append(scenario_agent_md)
    elif global_agent_md or scenario_agent_md:
        # Combine both (or just one if only one exists)
        if global_agent_md:
            components.append(global_agent_md)
        if scenario_agent_md:
            components.append(scenario_agent_md)
    
    # Join with double newlines if there are components
    return "\n\n".join(components) if components else None
```

### 4.3. Integration Point

The agent instructions will be read during suite parsing and passed to `SuiteRunner`, which will then pass them to the LLM creation function (`create_llm` or when creating the `Agent`).

Currently, fast mode is handled in `SuiteRunner.run_suite()`:

```python
# Current code (runner.py ~lines 62-73)
if self.flash_mode:
    llm = create_llm(temperature=temperature)
    extend_system_message = f"{SPEED_OPTIMIZATION_PROMPT}\n\n"
else:
    llm = create_llm(temperature=temperature)
    extend_system_message = None
```

This needs to be updated to:

```python
# New code
system_message = build_system_message(
    fast_mode=self.flash_mode,
    global_agent_md=self.global_agent_instructions,
    scenario_agent_md=suite.agent_instructions,
    override_flag=self.scenario_agent_override
)
llm = create_llm(temperature=temperature)
extend_system_message = system_message
```

### 4.4. Data Flow

1. **CLI Layer** (`cli/run.py`):
   - Accept `--scenario-agent-override` flag
   - Pass flag to runner

2. **Discovery Layer** (`core/discovery.py`):
   - Search for global `agent.md` in the familiar root directory
   - Return path if found

3. **Parser Layer** (`core/parser.py`):
   - Read scenario-level `agent.md` if present in suite directory
   - Store content in `TestSuite` model

4. **Runner Layer** (`core/runner.py`):
   - Combine fast mode prompt + agent instructions based on logic above
   - Pass combined prompt to Agent creation

5. **Models Layer** (`models/suite.py`):
   - Add optional `agent_instructions: Optional[str]` field to `TestSuite`

## 5. Examples

### Example 1: Scenario-Specific Instructions

**File**: `familiar/checkout-flow/agent.md`
```markdown
You are testing an e-commerce checkout flow. Important context:

- Payment processing uses Stripe test mode
- The shipping address form has custom validation
- There's a promotional code field that may or may not be visible
- The "Place Order" button is disabled until all required fields are filled
```

### Example 2: Global Instructions

**File**: `familiar/agent.md`
```markdown
You are testing a React application with the following characteristics:

- Uses React Router for navigation
- All forms have client-side validation
- Loading states are indicated by spinner icons
- Error messages appear as red text below form fields
```

### Example 3: Combined Instructions

With both files present:
- Global instructions provide general app context
- Scenario instructions provide specific test context
- Both are combined in the system message

## 6. CLI Changes

### New Flag

```bash
familiar run <suite> --scenario-agent-override
```

**Behavior**: When set, only scenario-level `agent.md` is used (global `agent.md` is ignored).

### Examples

```bash
# Run with default behavior (combine global + scenario agent.md)
familiar run familiar/checkout-flow

# Run with scenario-only agent instructions
familiar run familiar/checkout-flow --scenario-agent-override

# Run with fast mode + agent instructions (both combined)
familiar run familiar/checkout-flow --fast

# Run with fast mode + scenario-only agent instructions
familiar run familiar/checkout-flow --fast --scenario-agent-override
```

## 7. Error Handling

- **Missing agent.md**: No error, feature is optional
- **Malformed agent.md**: Log warning and skip that file
- **Encoding issues**: Try UTF-8, fallback to latin-1, log warning if issues
- **Permission issues**: Log warning and skip that file

## 8. Out of Scope

- Variable interpolation in agent.md files (treat as plain text)
- Conditional agent instructions based on environment variables
- Multiple agent.md files per scenario (only one supported)
- Agent instructions validation or linting

## 9. Success Criteria

The feature will be considered successful when:

- Users can provide agent.md at global and scenario levels
- Instructions are properly combined and passed to the LLM
- Fast mode integration works correctly
- `--scenario-agent-override` flag works as specified
- All existing tests pass without modification
- New tests cover all instruction combination scenarios
- Documentation is updated with examples

## 10. Testing Strategy

### Unit Tests

- Test `build_system_message()` with all combinations of inputs
- Test agent.md file reading (success, missing, malformed)
- Test instruction merging logic

### Integration Tests

- Test suite execution with global agent.md only
- Test suite execution with scenario agent.md only
- Test suite execution with both (combined)
- Test suite execution with override flag
- Test fast mode + agent instructions combinations

### Contract Tests

- Verify CLI accepts `--scenario-agent-override` flag
- Verify TestSuite model has agent_instructions field

