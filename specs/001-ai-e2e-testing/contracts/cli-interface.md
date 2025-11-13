# CLI Interface Contract

**Version**: 1.0.0  
**Binary Name**: `familiar`  
**Entry Point**: `familiar.cli.main:cli` (Python package)

## Purpose

This document defines the contract for the Familiar command-line interface, including commands, options, arguments, exit codes, and output formats.

## Global Options

Available for all commands:

```bash
familiar [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--help` | `-h` | flag | - | Show help message and exit |
| `--version` | `-v` | flag | - | Show version and exit |
| `--test-dir` | - | path | `./familiar` | Root directory for test suites |
| `--log-level` | - | choice | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |
| `--log-file` | - | path | - | Write logs to file (default: console only) |
| `--no-color` | - | flag | false | Disable colored output |

### Environment Variables

Global options can be set via environment variables:

| Variable | Equivalent Option | Example |
|----------|-------------------|---------|
| `FAMILIAR_TEST_DIR` | `--test-dir` | `/path/to/tests` |
| `FAMILIAR_LOG_LEVEL` | `--log-level` | `DEBUG` |
| `FAMILIAR_LOG_FILE` | `--log-file` | `/var/log/familiar.log` |
| `NO_COLOR` | `--no-color` | `1` (any truthy value) |

**Priority**: CLI options > Environment variables > Defaults

## Commands

### 1. `familiar run`

Execute test suites.

#### Syntax

```bash
familiar run [OPTIONS] [SUITE_PATH_OR_NAME]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `SUITE_PATH_OR_NAME` | No | Suite directory path or name. If omitted, runs all suites. |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--all` | `-a` | flag | false | Run all discovered suites |
| `--suite` | `-s` | text | - | Run specific suite by name (can specify multiple) |
| `--format` | `-f` | choice | `text` | Output format: text, json, junit |
| `--output` | `-o` | path | stdout | Write output to file instead of stdout |
| `--headless` | - | flag | true | Run browser in headless mode |
| `--headed` | - | flag | false | Run browser with visible UI (opposite of headless) |
| `--fail-fast` | - | flag | false | Stop on first suite failure |
| `--continue` | - | flag | true | Continue running suites after failure (default) |
| `--parallel` | `-p` | int | 1 | Number of suites to run in parallel (future feature) |
| `--dry-run` | - | flag | false | Validate and show what would run, but don't execute |
| `--debug` | `-d` | flag | false | Enable interactive debug mode |

#### Examples

```bash
# Run all suites
familiar run --all

# Run specific suite by path
familiar run familiar/auth-flow

# Run specific suite by name
familiar run --suite "User Authentication Flow"

# Run multiple suites
familiar run --suite auth-flow --suite checkout-flow

# Run with JUnit XML output for CI
familiar run --all --format junit --output results.xml

# Run in headed mode for debugging
familiar run auth-flow --headed

# Dry run to validate tests
familiar run --all --dry-run

# Interactive debug mode
familiar run auth-flow --debug

# Fail fast for quick feedback
familiar run --all --fail-fast
```

#### Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `0` | Success | All executed suites passed |
| `1` | Failure | One or more suites failed |
| `2` | Configuration Error | Invalid config, missing files, unresolved variables |
| `3` | Infrastructure Error | Browser crash, network failure, API key invalid |
| `130` | Interrupted | User interrupted (Ctrl+C) |

#### Output Formats

**Text (default)** - Human-readable console output:
```
Running Familiar v1.0.0
Test directory: ./familiar

Discovering suites...
Found 3 suites

═══════════════════════════════════════════════════════
Suite: User Authentication Flow
Path: familiar/auth-flow
═══════════════════════════════════════════════════════

✓ 00-load-login.md       (5.2s)
✓ 01-enter-credentials.md (3.1s)
✓ 02-verify-dashboard.md  (2.8s)

Suite Result: PASSED (11.1s)
  Steps: 3 passed, 0 failed, 3 total

═══════════════════════════════════════════════════════
Summary
═══════════════════════════════════════════════════════
Suites: 3 passed, 0 failed, 3 total
Steps:  15 passed, 0 failed, 15 total
Duration: 45.3s

Status: ✓ ALL TESTS PASSED
```

**JSON** - Machine-readable structured output:
```json
{
  "version": "1.0.0",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "started_at": "2025-11-13T10:00:00Z",
  "completed_at": "2025-11-13T10:02:00Z",
  "duration": 120.5,
  "success": true,
  "exit_code": 0,
  "suites": [
    {
      "name": "User Authentication Flow",
      "path": "familiar/auth-flow",
      "success": true,
      "duration": 11.1,
      "steps": [
        {
          "name": "Load Login Page",
          "path": "00-load-login.md",
          "success": true,
          "duration": 5.2,
          "attempt": 1,
          "logs": [...]
        }
      ]
    }
  ],
  "summary": {
    "total_suites": 3,
    "passed_suites": 3,
    "failed_suites": 0,
    "total_steps": 15,
    "passed_steps": 15,
    "failed_steps": 0
  }
}
```

**JUnit XML** - Standard CI/CD format:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Familiar Test Run" tests="15" failures="0" errors="0" time="120.5">
  <testsuite name="User Authentication Flow" tests="3" failures="0" errors="0" time="11.1">
    <testcase name="Load Login Page" classname="auth-flow.00-load-login" time="5.2"/>
    <testcase name="Enter Credentials" classname="auth-flow.01-enter-credentials" time="3.1"/>
    <testcase name="Verify Dashboard" classname="auth-flow.02-verify-dashboard" time="2.8"/>
  </testsuite>
</testsuites>
```

---

### 2. `familiar discover`

Discover and list available test suites without executing them.

#### Syntax

```bash
familiar discover [OPTIONS] [DIRECTORY]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `DIRECTORY` | No | Directory to search for suites (default: `--test-dir` value) |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--format` | `-f` | choice | `text` | Output format: text, json |
| `--validate` | - | flag | false | Also validate suite configurations |
| `--show-steps` | - | flag | false | Show steps for each suite |

#### Examples

```bash
# Discover suites in default directory
familiar discover

# Discover in specific directory
familiar discover ./custom-tests

# Discover with validation
familiar discover --validate

# Show detailed information including steps
familiar discover --show-steps

# JSON output for parsing
familiar discover --format json
```

#### Output (Text Format)

```
Discovering test suites in: ./familiar

Found 3 suites:

1. User Authentication Flow
   Path: familiar/auth-flow
   Steps: 3
   Timeout: 120s

2. E-commerce Checkout
   Path: familiar/checkout-flow
   Steps: 8
   Timeout: 300s

3. Dashboard Navigation
   Path: familiar/dashboard-nav
   Steps: 5
   Timeout: 90s

Total: 3 suites, 16 steps
```

#### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success (suites found and valid if `--validate`) |
| `1` | Validation failures (if `--validate`) |
| `2` | No suites found or discovery error |

---

### 3. `familiar validate`

Validate test suite configurations and steps without executing them.

#### Syntax

```bash
familiar validate [OPTIONS] [SUITE_PATH_OR_NAME]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `SUITE_PATH_OR_NAME` | No | Suite to validate. If omitted, validates all suites. |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--all` | `-a` | flag | false | Validate all discovered suites |
| `--strict` | - | flag | false | Treat warnings as errors |
| `--format` | `-f` | choice | `text` | Output format: text, json |

#### Validation Checks

1. **Suite Configuration**:
   - Valid YAML syntax
   - Required fields present
   - Values within valid ranges
   - Cross-field constraints (step_timeout <= timeout)

2. **Step Files**:
   - Files exist and readable
   - Valid markdown syntax
   - Naming convention followed
   - Variables resolvable

3. **Includes**:
   - Included files exist
   - No circular includes

4. **Overall Structure**:
   - At least one step file
   - Timeout estimates reasonable

#### Examples

```bash
# Validate all suites
familiar validate --all

# Validate specific suite
familiar validate auth-flow

# Strict mode (warnings become errors)
familiar validate --all --strict

# JSON output for CI integration
familiar validate --all --format json
```

#### Output (Text Format)

```
Validating: User Authentication Flow (familiar/auth-flow)

✓ Suite configuration valid
✓ 3 step files found
✓ All variables resolvable
⚠ Warning: Estimated time (90s) near timeout (120s)

Result: VALID (1 warning)

═══════════════════════════════════════════════════════
Summary: 3 suites validated
  Valid: 3
  Invalid: 0
  Warnings: 1
```

#### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All validations passed |
| `1` | One or more validation errors |
| `2` | Validation failed to run (missing files, etc.) |

---

### 4. `familiar init`

Initialize a new test suite structure.

#### Syntax

```bash
familiar init [OPTIONS] SUITE_NAME
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `SUITE_NAME` | Yes | Name for the new test suite (e.g., "auth-flow") |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--template` | `-t` | choice | `basic` | Template: basic, advanced, example |
| `--path` | `-p` | path | `./familiar` | Where to create suite directory |
| `--steps` | - | int | 3 | Number of starter step files to create |

#### Examples

```bash
# Create basic suite
familiar init auth-flow

# Create advanced suite with 5 starter steps
familiar init checkout-flow --template advanced --steps 5

# Create in custom location
familiar init api-tests --path ./tests/e2e
```

#### Output

```
Creating test suite: auth-flow

Created:
  familiar/auth-flow/suite.yaml
  familiar/auth-flow/00-setup.md
  familiar/auth-flow/01-main-flow.md
  familiar/auth-flow/02-teardown.md

Next steps:
  1. Edit suite.yaml to configure timeouts and retry policy
  2. Write test steps in the .md files
  3. Run: familiar validate auth-flow
  4. Run: familiar run auth-flow
```

#### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Suite created successfully |
| `1` | Suite already exists |
| `2` | Error creating files |

---

### 5. `familiar version`

Show version information.

#### Syntax

```bash
familiar version [OPTIONS]
```

#### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--full` | - | Show detailed version information |

#### Output

**Normal**:
```
Familiar 1.0.0
```

**Full**:
```
Familiar 1.0.0
  Python: 3.11.5
  browser-use: 0.9.5
  Playwright: 1.40.0
  Platform: macOS-14.1-arm64
```

---

## Interactive Debug Mode

When running with `--debug` flag, Familiar enters interactive mode at each step.

### Debug Commands

| Command | Description |
|---------|-------------|
| `step` / `s` | Execute next step |
| `continue` / `c` | Resume normal execution (no more pauses) |
| `skip` | Skip current step |
| `inspect` / `i` | Show browser state (DOM, console) |
| `screenshot` / `ss` | Capture screenshot |
| `vars` / `v` | Show current variables |
| `logs` / `l` | Show execution logs |
| `reasoning` / `r` | Show AI reasoning for current step |
| `help` / `h` | Show debug commands |
| `quit` / `q` | Stop execution and exit |

### Debug Session Example

```
═══════════════════════════════════════════════════════
Debug Mode: auth-flow
═══════════════════════════════════════════════════════

Step 1/3: Load Login Page
File: 00-load-login.md

Content:
  Navigate to ${BASE_URL}/login
  Verify page loads correctly

[Press Enter to execute step, or type 'help' for commands]
> step

Executing step...
✓ Step completed (5.2s)

[Next: 01-enter-credentials.md]
> inspect

Browser State:
  URL: https://staging.example.com/login
  Title: Login - Example App
  Visible elements: 12
  Console errors: 0

> continue

Resuming normal execution...
✓ 01-enter-credentials.md (3.1s)
✓ 02-verify-dashboard.md (2.8s)

Debug session complete.
```

---

## Error Handling

### Error Output Format

All errors written to stderr in consistent format:

```
Error: [ERROR_TYPE] - [ERROR_MESSAGE]
  Location: [SUITE_NAME / STEP_FILE]
  Details: [ADDITIONAL_CONTEXT]
  
Suggestion: [HOW_TO_FIX]
```

### Example Error Messages

**Unresolved Variable**:
```
Error: Configuration Error - Unresolved variable
  Location: auth-flow / 00-login.md
  Variable: TEST_PASSWORD
  
Suggestion: Set environment variable TEST_PASSWORD or add to suite.yaml env section
```

**Suite Timeout**:
```
Error: Timeout - Suite exceeded timeout limit
  Location: checkout-flow
  Duration: 305.2s
  Timeout: 300s
  Step: 05-payment-confirmation.md
  
Suggestion: Increase suite timeout in suite.yaml or optimize slow steps
```

**Browser Crash**:
```
Error: Infrastructure Error - Browser crashed during execution
  Location: dashboard-nav / 03-load-widgets.md
  Browser: Chrome 120.0.6099.109
  
Suggestion: Check application for JavaScript errors or infinite loops
```

---

## Environment Variables Reference

### Familiar Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `FAMILIAR_TEST_DIR` | path | `./familiar` | Root test suite directory |
| `FAMILIAR_LOG_LEVEL` | choice | `INFO` | DEBUG, INFO, WARNING, ERROR |
| `FAMILIAR_LOG_FILE` | path | - | Log file path (console only if unset) |
| `FAMILIAR_HEADLESS` | bool | `true` | Run browser in headless mode |
| `FAMILIAR_DEFAULT_TIMEOUT` | int | `300` | Default suite timeout (seconds) |
| `FAMILIAR_DEFAULT_STEP_TIMEOUT` | int | `30` | Default step timeout (seconds) |
| `FAMILIAR_DEFAULT_RETRIES` | int | `3` | Default retry count |
| `FAMILIAR_SCREENSHOT_DIR` | path | `./screenshots` | Where to save failure screenshots |
| `NO_COLOR` | bool | `false` | Disable colored output (any truthy value) |

### browser-use Pass-Through Variables

These are passed directly to browser-use library:

| Variable | Description |
|----------|-------------|
| `BROWSER_USE_API_KEY` | browser-use cloud API key |
| `OPENAI_API_KEY` | OpenAI API key for GPT models |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude models |
| `GOOGLE_API_KEY` | Google API key for Gemini models |

See [browser-use documentation](https://github.com/browser-use/browser-use) for complete list.

---

## CI/CD Integration Examples

### GitHub Actions

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Familiar
        run: |
          pip install familiar
          familiar version
      
      - name: Run Tests
        env:
          FAMILIAR_HEADLESS: true
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          BASE_URL: https://staging.example.com
        run: |
          familiar run --all --format junit --output results.xml
      
      - name: Publish Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: results.xml
```

### GitLab CI

```yaml
e2e_tests:
  image: python:3.11
  script:
    - pip install familiar
    - familiar run --all --format junit --output results.xml
  artifacts:
    reports:
      junit: results.xml
    paths:
      - screenshots/
    when: always
  variables:
    FAMILIAR_HEADLESS: "true"
    BASE_URL: "https://staging.example.com"
```

---

## Version History

- **1.0.0** (2025-11-13): Initial CLI specification

