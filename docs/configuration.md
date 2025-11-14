# Configuration Guide

This guide covers all configuration options for Familiar, including environment variables, suite configuration, and CLI options.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Suite Configuration](#suite-configuration)
- [CLI Options](#cli-options)
- [Configuration Precedence](#configuration-precedence)

---

## Environment Variables

Familiar uses environment variables for all runtime configuration. This makes it perfect for CI/CD environments.

### LLM Configuration

#### Provider Selection

```bash
FAMILIAR_MODEL_PROVIDER="anthropic"  # Required
```

**Supported Providers:**
- `anthropic` - Anthropic Claude (recommended)
- `openai` - OpenAI GPT models
- `google` or `gemini` - Google Gemini
- `browser-use` - Browser Use optimized model (3-5x faster)
- `groq` - Groq (fast inference with Llama models)
- `azure` - Azure OpenAI
- `ollama` - Local Ollama models

#### Model Selection

```bash
FAMILIAR_MODEL="claude-3-5-sonnet-20241022"  # Optional, uses provider default if not set
```

**Common Models:**

**Anthropic:**
- `claude-3-5-sonnet-20241022` (recommended, balanced)
- `claude-3-opus-20240229` (most capable, slower)
- `claude-3-haiku-20240307` (fast, economical)

**OpenAI:**
- `gpt-4o` (recommended, multimodal)
- `gpt-4` (capable, slower)
- `gpt-3.5-turbo` (fast, economical)

**Google:**
- `gemini-2.0-flash-exp` (fast, capable)
- `gemini-pro` (balanced)

**Ollama (local):**
- `llama3.2` (general purpose)
- `llama3.1:8b` (faster, smaller)
- `mistral` (alternative option)

#### API Keys

Each provider requires its own API key:

```bash
# Anthropic
ANTHROPIC_API_KEY="sk-ant-api03-..."

# OpenAI
OPENAI_API_KEY="sk-..."

# Google/Gemini
GOOGLE_API_KEY="..."

# Browser Use
BROWSER_USE_API_KEY="..."  # Get from https://cloud.browser-use.com

# Groq
GROQ_API_KEY="..."

# Azure OpenAI
AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
AZURE_OPENAI_API_KEY="..."

# Ollama (no key needed, but can set host)
OLLAMA_HOST="http://localhost:11434"  # optional
```

### Test Environment Variables

Define variables that will be interpolated in your test steps:

```bash
# Application URLs
BASE_URL="https://app.example.com"
API_URL="https://api.example.com"

# Test Credentials
TEST_USER="test@example.com"
TEST_PASSWORD="securepassword123"
ADMIN_USER="admin@example.com"
ADMIN_PASSWORD="adminpassword456"

# Test Data
TEST_PROJECT_NAME="E2E Test Project"
TEST_ORG_ID="org_12345"

# Custom Variables
CUSTOM_TIMEOUT="30"
EXPECTED_TITLE="Welcome to Dashboard"
```

**Usage in Test Steps:**

```markdown
# Login Test

Navigate to ${BASE_URL}/login
Enter email: ${TEST_USER}
Enter password: ${TEST_PASSWORD}
```

### Browser Configuration

```bash
# Headless mode (can be overridden by --headless/--no-headless CLI flag)
FAMILIAR_HEADLESS="true"  # true or false, default: true
```

---

## Suite Configuration

Each test suite has a `suite.yaml` file that configures its behavior.

### Complete Example

```yaml
name: "Complete User Journey"
description: "Tests the full user onboarding and project creation flow"

# Timeouts (in seconds)
timeout: 300              # Maximum time for entire suite
step_timeout: 60          # Maximum time for each step

# Retry configuration
retry_policy:
  type: "exponential"     # fixed, exponential, or best_of_n
  max_retries: 3          # Number of retry attempts
  delay: 1.0             # Fixed delay OR base delay for exponential
  base_delay: 1.0        # Base delay for exponential backoff
  max_delay: 60.0        # Maximum delay cap for exponential
  n_runs: 5              # Number of runs for best_of_n

# Failure tolerance
fuzziness: 0.1            # Allow 10% of steps to fail (0.0 = strict)

# AI behavior
temperature: 0.7          # LLM temperature (0.0-1.0)
                         # Lower = more deterministic
                         # Higher = more creative

# Browser settings
headless: true            # Run in headless mode
screenshot_on_failure: true  # Capture screenshot when steps fail

# Suite-specific environment variables
env:
  SUITE_SPECIFIC_VAR: "value"
  FEATURE_FLAG: "enabled"

# Metadata (optional, for organization)
metadata:
  owner: "qa-team@example.com"
  priority: "high"
  tags: ["critical-path", "user-flow"]
  jira_ticket: "QA-123"
```

### Configuration Fields

#### Basic Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Suite name (1-200 characters) |
| `description` | string | No | Human-readable description |
| `timeout` | integer | No | Total suite timeout in seconds (1-3600, default: 300) |
| `step_timeout` | integer | No | Individual step timeout in seconds (1-600, default: 30) |

**Validation:**
- `step_timeout` must be ≤ `timeout`
- Names must be unique across your test directory

#### Retry Policy

**Type: `fixed`** - Constant delay between retries

```yaml
retry_policy:
  type: "fixed"
  max_retries: 3     # Number of retries (0-10, default: 3)
  delay: 2.0        # Seconds between retries (≥0, default: 1.0)
```

**Example:** With `max_retries: 3` and `delay: 2.0`, a failing step will be retried up to 3 times with 2 seconds between each attempt.

**Type: `exponential`** - Exponentially increasing delays

```yaml
retry_policy:
  type: "exponential"
  max_retries: 5      # Number of retries (0-10, default: 3)
  base_delay: 1.0    # Starting delay in seconds (≥0, default: 1.0)
  max_delay: 60.0    # Maximum delay cap in seconds (≥0, default: 60.0)
```

**Example:** With `base_delay: 1.0`, delays will be: 1s, 2s, 4s, 8s, 16s (capped at `max_delay`)

**Type: `best_of_n`** - Run multiple times, succeed if any pass

```yaml
retry_policy:
  type: "best_of_n"
  n_runs: 5          # Total runs (1-20, default: 3)
```

**Example:** Step will run 5 times. If ANY attempt succeeds, the step passes. No delay between runs.

#### Fuzziness

Controls failure tolerance for the entire suite:

```yaml
fuzziness: 0.2  # Allow 20% of steps to fail
```

| Value | Behavior |
|-------|----------|
| `0.0` | Strict - All steps must pass (default) |
| `0.1` | Allow 10% failure rate |
| `0.2` | Allow 20% failure rate |
| `1.0` | Allow all steps to fail (not recommended) |

**Example:** Suite with 10 steps and `fuzziness: 0.2` can have up to 2 failures and still pass.

**Use Cases:**
- Long test suites where some steps are non-critical
- Exploratory testing where partial success is valuable
- Gradual rollout of new tests

#### Temperature

Controls LLM creativity vs. determinism:

```yaml
temperature: 0.5  # Range: 0.0-1.0, default: 0.7
```

| Value | Behavior | Use Case |
|-------|----------|----------|
| `0.0-0.3` | Very deterministic | Critical paths, regression tests |
| `0.4-0.7` | Balanced (recommended) | General testing |
| `0.8-1.0` | Creative/exploratory | Unusual UIs, edge cases |

**Lower temperature** = More consistent, repeatable results
**Higher temperature** = More adaptable to UI variations

#### Headless Mode

```yaml
headless: true  # or false
```

- `true`: Run browser without GUI (default, for CI/CD)
- `false`: Show browser window (useful for debugging)

Can be overridden by CLI flag: `--headless` / `--no-headless`

#### Screenshot on Failure

```yaml
screenshot_on_failure: true  # or false, default: true
```

When `true`, automatically captures a screenshot when a step fails for debugging.

#### Environment Variables

Suite-specific environment variables that override global ones:

```yaml
env:
  API_ENDPOINT: "https://api.staging.example.com"
  FEATURE_FLAG_NEW_UI: "true"
  DEBUG_MODE: "false"
```

These are merged with system environment variables, with suite values taking precedence.

#### Metadata

Arbitrary metadata for organization and tracking:

```yaml
metadata:
  owner: "qa-team@example.com"
  priority: "high"
  tags: ["smoke", "critical-path"]
  jira_ticket: "QA-456"
  run_frequency: "every_commit"
  estimated_duration: "2m"
```

Metadata is preserved in test results but doesn't affect execution.

---

## CLI Options

### `familiar run`

Run test suites with various options:

```bash
familiar run <suite_path> [OPTIONS]
```

#### Options

**`--format TEXT`**
- **Values**: `text` (default), `json`
- **Description**: Output format
- **Example**:
  ```bash
  familiar run tests/login --format json
  ```

**`--headless / --no-headless`**
- **Default**: `--headless`
- **Description**: Run browser in headless mode
- **Example**:
  ```bash
  # See the browser (useful for debugging)
  familiar run tests/login --no-headless
  ```

**`--verbose / --no-verbose`**
- **Default**: `--no-verbose`
- **Description**: Show detailed logs
- **Example**:
  ```bash
  familiar run tests/login --verbose
  ```

**`--all`**
- **Description**: Run all suites in directory
- **Example**:
  ```bash
  familiar run tests/ --all
  ```

**`--fast`**
- **Description**: Enable speed optimizations (flash mode, reduced wait times). May reduce reliability for complex scenarios.
- **Example**:
  ```bash
  familiar run tests/login --fast
  ```

### `familiar discover`

Discover available test suites:

```bash
familiar discover <directory> [OPTIONS]
```

#### Options

**`--format TEXT`**
- **Values**: `text` (default), `json`
- **Description**: Output format
- **Example**:
  ```bash
  familiar discover tests/ --format json
  ```

### Global Options

**`--version`**
- **Description**: Show version and exit
- **Example**:
  ```bash
  familiar --version
  ```

**`--help`**
- **Description**: Show help message
- **Example**:
  ```bash
  familiar --help
  familiar run --help
  ```

---

## Configuration Precedence

When the same setting is defined in multiple places, Familiar uses this precedence order (highest to lowest):

1. **CLI flags** (e.g., `--headless`)
2. **Suite `env` section** (in `suite.yaml`)
3. **Environment variables** (system or `.env` file)
4. **Suite configuration** (in `suite.yaml`)
5. **Default values**

### Example

```yaml
# suite.yaml
headless: true
temperature: 0.5
env:
  BASE_URL: "https://suite-specific.com"
```

```bash
# Environment
export BASE_URL="https://global.com"
export TEST_USER="user@example.com"

# Command
familiar run tests/my-suite --no-headless --verbose
```

**Effective Configuration:**
- `headless`: `false` (from CLI flag `--no-headless`)
- `verbose`: `true` (from CLI flag)
- `temperature`: `0.5` (from suite.yaml)
- `BASE_URL`: `"https://suite-specific.com"` (from suite env section)
- `TEST_USER`: `"user@example.com"` (from environment)

---

## Configuration Examples

### Example 1: Strict Critical Path Test

```yaml
name: "Payment Processing - Critical Path"
timeout: 180
step_timeout: 45
retry_policy:
  type: "fixed"
  max_retries: 1    # Minimal retries
  delay: 2.0
fuzziness: 0.0      # All steps must pass
temperature: 0.3    # Very deterministic
headless: true
```

### Example 2: Exploratory Test with High Tolerance

```yaml
name: "UI Exploration - New Feature"
timeout: 600
step_timeout: 90
retry_policy:
  type: "best_of_n"
  n_runs: 5         # Run 5 times
fuzziness: 0.3      # Allow 30% failure
temperature: 0.9    # More creative
headless: false     # Watch it run
```

### Example 3: Load Testing Scenario

```yaml
name: "Load Test - User Creation"
timeout: 1800
step_timeout: 120
retry_policy:
  type: "exponential"
  max_retries: 5
  base_delay: 2.0
  max_delay: 60.0   # Back off on overload
fuzziness: 0.1
temperature: 0.5
env:
  CONCURRENT_USERS: "10"
  TEST_DATA_SIZE: "large"
```

### Example 4: Development/Debug Mode

```yaml
name: "Debug - Login Flow"
timeout: 300
step_timeout: 120   # More time for manual inspection
retry_policy:
  type: "fixed"
  max_retries: 0    # No retries, fail fast
fuzziness: 0.0
temperature: 0.5
headless: false     # Watch browser
screenshot_on_failure: true
```

---

## Best Practices

### 1. Use Environment Variables for Secrets

❌ **Don't** put secrets in `suite.yaml`:
```yaml
env:
  API_KEY: "sk-1234567890"  # BAD!
```

✅ **Do** use environment variables:
```bash
export API_KEY="sk-1234567890"
```

### 2. Start with Conservative Settings

Begin with strict settings and relax as needed:
```yaml
retry_policy:
  type: "fixed"
  max_retries: 1
fuzziness: 0.0
temperature: 0.5
```

### 3. Document Custom Variables

Add comments to your suite.yaml:
```yaml
env:
  # Feature flag for new checkout flow
  ENABLE_NEW_CHECKOUT: "true"
  
  # Test data identifier
  TEST_DATASET: "sample_users_v2"
```

### 4. Use Meaningful Suite Names

```yaml
# Good
name: "User Registration - Happy Path"
name: "API Integration - Error Handling"

# Bad
name: "Test 1"
name: "Suite"
```

### 5. Set Realistic Timeouts

```yaml
# Too short - will fail on slow networks
step_timeout: 5

# Too long - slow feedback
step_timeout: 300

# Just right - reasonable for most operations
step_timeout: 30-60
```

### 6. Temperature Guidelines

- **Critical paths**: `0.3-0.5` (deterministic)
- **Standard tests**: `0.5-0.7` (balanced)
- **Exploratory tests**: `0.7-0.9` (adaptable)
- **Never use**: `0.0` (too rigid) or `1.0` (too random)

---

## Troubleshooting

### Tests are flaky / non-deterministic

**Solution**: Reduce temperature and add retries
```yaml
temperature: 0.4
retry_policy:
  type: "fixed"
  max_retries: 2
```

### Tests timeout frequently

**Solution**: Increase timeouts or improve step specificity
```yaml
step_timeout: 90
# And make steps more specific in markdown
```

### Tests fail on CI but pass locally

**Solution**: Ensure headless mode works
```yaml
headless: true
retry_policy:
  type: "exponential"  # Handle CI slowness
  max_retries: 3
```

### Too many retries consuming API credits

**Solution**: Reduce retry attempts
```yaml
retry_policy:
  type: "fixed"
  max_retries: 1
  delay: 1.0
```

---

## Next Steps

- [Test Suite Format Guide](test-suite-format.md)
- [CI/CD Integration Guide](ci-integration.md)
- [Getting Started Guide](getting-started.md)

