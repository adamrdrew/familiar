# Implementation Plan: Fast Mode & Browser Performance Configuration

**Branch**: `004-fast-mode-performance` | **Date**: 2025-11-13 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/004-fast-mode-performance/spec.md`

## Summary

Add performance optimization features to Familiar: (1) `--fast` CLI flag that enables LLM flash mode and injects speed optimization prompts, and (2) configurable `browser_profile` in suite.yaml to control browser timing parameters (page load waits, action delays). This allows users to trade reliability for speed in development environments or with fast, stable applications.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: browser-use (BrowserProfile, Agent), click (CLI), pydantic (config validation)  
**Storage**: N/A (configuration only)  
**Testing**: pytest with existing unit/integration test infrastructure  
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)  
**Project Type**: Single project (CLI tool)  
**Performance Goals**: 30-60% faster execution time when fast mode enabled on simple scenarios  
**Constraints**: Must maintain backward compatibility (no breaking changes to existing tests)  
**Scale/Scope**: 4-5 files modified, minimal complexity, ~200-300 LOC total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Easy to Change
- **PASS**: Fast mode is additive (new optional parameters), no coupling introduced
- **PASS**: BrowserProfile config is injected via constructor (dependency injection)
- **PASS**: Changes are isolated to specific layers (CLI, models, runner)

### ✅ II. Small, Single Purpose Classes
- **PASS**: New `BrowserProfileConfig` class has one purpose (browser timing configuration)
- **PASS**: Existing classes gain one new responsibility each (fast mode flag handling)
- **PASS**: No god classes created

### ✅ III. Stable, Minimal Public Interfaces
- **PASS**: CLI adds one flag (`--fast`), no breaking changes
- **PASS**: `suite.yaml` adds optional field (`browser_profile`), backward compatible
- **PASS**: Public APIs remain stable (new parameters are optional)

### ✅ IV. Polymorphism Over Conditionals
- **PASS**: Fast mode uses simple boolean flag (appropriate for binary behavior)
- **PASS**: No complex type-based conditionals introduced

### ✅ V. Behavior-Based Testing
- **PASS**: Tests will validate outcomes (execution time, agent configuration)
- **PASS**: Tests will not mock internal browser-use classes
- **PASS**: Integration tests verify end-to-end fast mode behavior

### ✅ VI. Code as User Interface
- **PASS**: `--fast` flag is clear and discoverable
- **PASS**: `browser_profile` configuration is explicit and readable
- **PASS**: No clever tricks, straightforward parameter passing

### ✅ VII. Humane Code
- **PASS**: Feature is explicit (opt-in via flag or config)
- **PASS**: Sensible defaults preserved for non-fast mode
- **PASS**: Clear documentation of speed/reliability tradeoff

### ✅ VIII. Test-Driven Development
- **PASS**: Existing test infrastructure supports new tests
- **PASS**: Can write tests for CLI flag, config parsing, agent creation
- **PASS**: Behavior is testable through public interfaces

**Constitutional Compliance**: ✅ **PASS** - No violations detected

## Project Structure

### Documentation (this feature)

```text
specs/004-fast-mode-performance/
├── plan.md              # This file
├── spec.md              # Feature specification (created)
├── research.md          # Phase 0 output (next)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── browser-profile-config.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/familiar/
├── cli/
│   ├── main.py          # ✏️ Add --fast flag to run command
│   └── run.py           # ✏️ Pass fast_mode to SuiteRunner
├── models/
│   ├── suite.py         # ✏️ Add BrowserProfileConfig, update SuiteConfig
│   └── ...
├── core/
│   ├── runner.py        # ✏️ Accept fast_mode, create BrowserProfile, pass to Agent
│   ├── executor.py      # ℹ️  No changes needed (already accepts browser)
│   └── ...
└── utils/
    └── ...

tests/
├── unit/
│   ├── test_models.py   # ✏️ Add BrowserProfileConfig validation tests
│   └── test_cli.py      # ✏️ Add --fast flag tests
├── integration/
│   ├── test_runner.py   # ✏️ Add fast mode execution tests
│   └── test_cli.py      # ✏️ Add end-to-end fast mode tests
└── fixtures/
    └── fast-mode-suite/ # 🆕 Create test fixture with browser_profile
        ├── suite.yaml
        └── 00-test.md
```

**Structure Decision**: Single project structure (existing). Changes are localized to CLI, models, and runner layers. No new directories needed. Follows existing pattern of configuration options flowing from CLI → runner → executor.

## Complexity Tracking

> No constitution violations detected. This section intentionally left empty.

---

## Phase 0: Research (to be generated by /speckit.plan)

Research tasks:
1. Verify browser-use BrowserProfile API parameters and defaults
2. Confirm Agent flash_mode and extend_system_message parameters
3. Validate Pydantic field merging for optional nested models
4. Review existing CLI flag patterns in click framework
5. Test performance baseline for fast mode justification

**Output**: `research.md`

---

## Phase 1: Design (to be generated by /speckit.plan)

Design artifacts:
1. `data-model.md` - BrowserProfileConfig model with validation rules
2. `contracts/browser-profile-config.yaml` - suite.yaml schema extension
3. `contracts/cli-interface.md` - --fast flag specification
4. `quickstart.md` - Fast mode usage examples

**Output**: Design documents in `/contracts/`, `data-model.md`, `quickstart.md`

---

## Phase 2: Implementation (to be generated by /speckit.tasks)

Task breakdown for:
- CLI flag implementation
- Configuration model updates
- Runner refactoring
- Test creation
- Documentation updates

**Output**: `tasks.md` (generated by separate `/speckit.tasks` command)

---

## Notes

### Design Decisions

1. **Fast mode as CLI flag (not suite config)**
   - Rationale: Speed optimization is typically a developer preference, not a test requirement
   - Alternative considered: `fast_mode: true` in suite.yaml
   - Decision: Start with CLI-only, add suite config if users request it

2. **Browser profile in suite config (not CLI)**
   - Rationale: Timing parameters are test-specific (stable app vs. slow app)
   - Alternative considered: CLI flags like `--page-load-wait 0.1`
   - Decision: Suite config is more maintainable for test-specific tuning

3. **Speed optimization prompt as constant**
   - Rationale: Prompt engineering is experimental, should be easy to modify
   - Alternative considered: Load from config file
   - Decision: Keep simple with constant, can externalize later if needed

### Risk Assessment

**Low Risk**:
- Additive feature with no breaking changes
- browser-use library already supports all needed parameters
- Existing tests validate no regression

**Medium Risk**:
- Users may over-rely on fast mode and miss reliability issues
- Mitigation: Clear documentation of speed/reliability tradeoff

**Dependencies**:
- browser-use >=0.9.5 (already required)
- No new external dependencies needed
