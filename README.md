# Familiar



<div align="center">

<img src="docs/images/fammy.png" alt="Fammy the Mascot" width="250">

**AI-Driven End-to-End Testing for Complex Web Applications**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Write tests in natural language. Let AI execute them like a human would.

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🌟 Features

### Natural Language Testing
Write test steps in plain English using Markdown. No brittle CSS selectors, no fragile XPath expressions.

```markdown
# Login to Dashboard

Navigate to the login page at ${BASE_URL}
Enter email "test@example.com" and password from environment
Click the "Sign In" button
Wait for the dashboard to load
Verify that the welcome message is displayed
```

### Intelligent AI Agent
Powered by [browser-use](https://github.com/browser-use/browser-use), Familiar uses AI to:
- **Understand Intent**: Interprets natural language instructions
- **Find Elements**: Locates UI elements without selectors
- **Adapt to Changes**: Handles UI changes gracefully
- **Self-Heal**: Retries and adapts when things go wrong

### Robust Non-Determinism Handling
AI-driven tests are inherently non-deterministic. Familiar handles this with:
- **Fixed Retry**: Constant delay between retries
- **Exponential Backoff**: Progressive delays for overload scenarios
- **Best-of-N**: Run multiple times, succeed if any pass
- **Fuzziness**: Tolerate a percentage of step failures

### Multi-Provider LLM Support
Configure your preferred LLM provider via environment variables (powered by [browser-use](https://browser-use.com)):
- **Browser Use** (Optimized browser automation model - 3-5x faster)
- **Anthropic Claude** (Claude 4 Sonnet, Opus, Haiku)
- **OpenAI** (GPT-4, GPT-4o, O3)
- **Google Gemini** (Gemini 2.0 Flash, Pro)
- **Groq** (Fast inference with Llama models)
- **Azure OpenAI** (Enterprise OpenAI deployment)
- **Ollama** (Local open-source models)

### CI/CD Integration
- **Structured Output**: JSON, text, or JUnit XML formats
- **Exit Codes**: Proper success/failure exit codes
- **Environment-Based Config**: All configuration via environment variables
- **Headless Mode**: Run tests without GUI
- **Parallel Execution**: Run multiple suites concurrently

### Developer-Friendly
- **Rich Terminal Output**: Beautiful, colorful test results
- **Test Discovery**: Automatic suite detection
- **Validation**: Lint suite configurations before running
- **Logging**: Detailed execution logs with retry tracking

### Agent Instructions
Provide custom context to the AI agent to improve test execution:
- **Global Instructions** (`agent.md` in familiar root): Shared context for all tests
- **Scenario Instructions** (`agent.md` in scenario dir): Test-specific context
- **Automatic Combination**: Global and scenario instructions combine intelligently
- **Override Control** (`--scenario-agent-override` flag): Use only scenario-level instructions

### Performance Optimization
Speed up test execution with performance controls:
- **Fast Mode** (`--fast` flag): Enable LLM flash mode and speed-optimized prompts (2-3x faster)
- **Browser Timing**: Configure page load and action delays per suite
- **Cumulative Sessions**: Single browser session persists across all steps in a scenario
- **Flexible Tradeoffs**: Balance speed vs. reliability for different environments

| Mode | Simple 3-Step Test | Speedup |
|------|-------------------|---------|
| Standard | ~25-30 seconds | Baseline |
| Fast Mode | ~15-18 seconds | 40-50% |
| Custom Timing | ~18-22 seconds | 30-40% |
| Fast + Custom | ~10-15 seconds | 50-70% |

---

## 📦 Installation

### Using uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Familiar
uv pip install familiar

# Or add to your project
uv add familiar
```

### Using pip

```bash
pip install familiar
```

### From Source

```bash
git clone https://github.com/adamrdrew/familiar.git
cd familiar
uv sync  # or: pip install -e .
```

---

## 🚀 Quick Start

### 1. Set Up Your LLM Provider

Choose and configure your LLM provider using environment variables or a `.env` file:

**Option A: Using a .env file (recommended)**

Create a `.env` file in your project root:

```bash
# .env
FAMILIAR_MODEL_PROVIDER=anthropic
FAMILIAR_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your-api-key
```

Familiar automatically loads `.env` files from your current directory!

**Option B: Using environment variables**

```bash
# For Browser Use (recommended - fastest, optimized for browser automation)
export FAMILIAR_MODEL_PROVIDER="browser-use"
export BROWSER_USE_API_KEY="your-api-key"  # Get from https://cloud.browser-use.com

# For Anthropic Claude
export FAMILIAR_MODEL_PROVIDER="anthropic"
export FAMILIAR_MODEL="claude-sonnet-4-0"
export ANTHROPIC_API_KEY="your-api-key"

# For OpenAI
export FAMILIAR_MODEL_PROVIDER="openai"
export FAMILIAR_MODEL="gpt-4o"
export OPENAI_API_KEY="your-api-key"

# For Groq (fast inference)
export FAMILIAR_MODEL_PROVIDER="groq"
export FAMILIAR_MODEL="llama-4-maverick-17b-128e-instruct"
export GROQ_API_KEY="your-api-key"

# For Azure OpenAI
export FAMILIAR_MODEL_PROVIDER="azure"
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key"

# For Ollama (local)
export FAMILIAR_MODEL_PROVIDER="ollama"
export FAMILIAR_MODEL="llama3.1:8b"
# No API key needed
```

### 2. Create a Test Suite

Create a test suite directory with configuration and steps:

```bash
mkdir -p familiar/login-test
```

**familiar/login-test/suite.yaml**:
```yaml
name: "User Login Test"
description: "Test user authentication flow"
timeout: 120
step_timeout: 30
retry_policy:
  type: "fixed"
  max_retries: 2
  delay: 1.0
fuzziness: 0.0
temperature: 0.7
headless: true
screenshot_on_failure: true
```

**familiar/login-test/00-navigate.md**:
```markdown
# Navigate to Login Page

Navigate to ${BASE_URL}/login

Wait for the page to load completely
Verify that the login form is visible
```

**familiar/login-test/01-login.md**:
```markdown
# Perform Login

Enter the following credentials:
- Email: ${TEST_USER}
- Password: ${TEST_PASSWORD}

Click the "Sign In" or "Login" button

Wait for navigation to complete
```

**familiar/login-test/02-verify.md**:
```markdown
# Verify Successful Login

Verify that we are now on the dashboard page
Check that the user's name or email appears in the header
Confirm that the main navigation menu is visible
```

> **Note:** Steps are executed sequentially (00 → 01 → 02) using the SAME browser session. This means the login state from step 01 persists into step 02, enabling cumulative testing workflows.

### 3. Set Test Environment Variables

**Using .env file (recommended)**:

```bash
# Add to your .env file
BASE_URL=https://your-app.com
TEST_USER=test@example.com
TEST_PASSWORD=securepassword123
```

**Or using environment variables**:

```bash
export BASE_URL="https://your-app.com"
export TEST_USER="test@example.com"
export TEST_PASSWORD="securepassword123"
```

### 4. Run Your Tests

```bash
# Run a specific suite
familiar run familiar/login-test

# Run with verbose output
familiar run familiar/login-test --verbose

# Run in headed mode (see the browser)
familiar run familiar/login-test --no-headless

# Discover all available suites
familiar discover familiar/

# Discover with JSON output
familiar discover familiar/ --format json

# Run all suites
familiar run familiar/ --all
```

### 5. View Results

```
╭──────────────────────────────────────────────────╮
│ ✓ User Login Test                     PASSED    │
╰──────────────────────────────────────────────────╯

┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ Status ┃ Step                   ┃ Duration ┃ Retries┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ ✓ PASS │ Navigate to Login Page │   3.24s  │   -    │
│ ✓ PASS │ Perform Login          │   5.81s  │   1    │
│ ✓ PASS │ Verify Successful Login│   2.15s  │   -    │
└────────┴────────────────────────┴──────────┴────────┘

┏━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric      ┃ Value ┃
┡━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Tests │ 3     │
│ Passed      │ 3     │
│ Failed      │ 0     │
│ Duration    │11.20s │
│ Success Rate│100.0% │
└─────────────┴───────┘
```

---

## 📖 Documentation

### Core Concepts

#### Test Suites
A **test suite** is a directory containing:
- `suite.yaml`: Configuration file
- `NN-name.md`: Test step files with numeric prefixes (00-99) defining execution order
- Optional non-numbered `.md` files (e.g., `README.md`, `notes.md`) - automatically skipped
- Optional `shared/` directory for reusable steps

**Step Naming Requirements:**
- Steps MUST use format: `00-description.md`, `01-next-step.md`, etc.
- Prefixes must be exactly 2 digits (00-99)
- Steps execute in numeric order (00 → 01 → 02...)
- Files without numeric prefixes are skipped
- No duplicate prefixes allowed

**Cumulative Execution:**
- All steps in a scenario share the SAME browser session
- Browser state (cookies, local storage, navigation) persists across steps
- This enables cumulative testing: login → navigate → perform action
- Each scenario has its own isolated browser session

#### Test Steps
Test steps are Markdown files with natural language instructions:

```markdown
# Step Name (optional)

Instructions for the AI agent to execute.
Can use ${VARIABLE} interpolation from environment.

## Expected Outcome (optional)
What should happen after this step.
```

#### Directory Structure

```
your-project/
├── familiar/                    # Test root directory
│   ├── login-flow/             # Test suite
│   │   ├── suite.yaml          # Suite configuration
│   │   ├── 00-navigate.md      # First step
│   │   ├── 01-login.md         # Second step
│   │   └── 02-verify.md        # Third step
│   ├── checkout-flow/          # Another suite
│   │   ├── suite.yaml
│   │   ├── 00-add-to-cart.md
│   │   └── 01-complete-purchase.md
│   └── shared/                 # Shared steps (optional)
│       └── steps/
│           └── common-login.md
└── .env                        # Environment variables
```

### Configuration

#### Suite Configuration (`suite.yaml`)

```yaml
name: "Test Suite Name"
description: "Optional description"

# Timeouts (in seconds)
timeout: 300              # Total suite timeout
step_timeout: 60          # Individual step timeout

# Retry policy
retry_policy:
  type: "fixed"           # fixed, exponential, or best_of_n
  max_retries: 3          # Number of retries
  delay: 1.0             # Delay between retries (fixed/exponential)
  base_delay: 1.0        # Base delay for exponential
  max_delay: 60.0        # Max delay cap for exponential
  n_runs: 5              # Number of runs for best_of_n

# Failure tolerance
fuzziness: 0.1            # Allow 10% of steps to fail (0.0-1.0)

# AI behavior
temperature: 0.7          # LLM temperature (0.0-1.0)
                         # Lower = more deterministic
                         # Higher = more creative

# Browser settings
headless: true            # Run browser in headless mode
screenshot_on_failure: true  # Capture screenshots on errors

# Browser performance tuning (optional)
browser_profile:
  minimum_wait_page_load_time: 1.0  # Seconds to wait after page loads (0-30)
  wait_between_actions: 1.0         # Seconds to wait between actions (0-30)
  headless: true                    # Override global headless setting
  
# Performance optimization examples:
# Fast mode (use with --fast CLI flag): reduces LLM thinking time
# Speed testing (development): minimum_wait_page_load_time: 0.1, wait_between_actions: 0.1
# Slow applications: minimum_wait_page_load_time: 3.0, wait_between_actions: 2.0
# Default/balanced: minimum_wait_page_load_time: 1.0, wait_between_actions: 1.0

# Custom environment variables for this suite
env:
  CUSTOM_VAR: "value"

# Metadata (optional)
metadata:
  owner: "team@example.com"
  priority: "high"
```

#### Environment Variables

**LLM Configuration:**
```bash
FAMILIAR_MODEL_PROVIDER   # browser-use, openai, anthropic, google, gemini, groq, azure, ollama
FAMILIAR_MODEL            # Model name (e.g., gpt-4o, claude-sonnet-4-0, gemini-flash-latest)

# Provider-specific API keys
BROWSER_USE_API_KEY      # For Browser Use (recommended)
OPENAI_API_KEY           # For OpenAI
ANTHROPIC_API_KEY        # For Anthropic
GOOGLE_API_KEY           # For Google/Gemini
GROQ_API_KEY             # For Groq
AZURE_OPENAI_ENDPOINT    # For Azure OpenAI
AZURE_OPENAI_API_KEY     # For Azure OpenAI
OLLAMA_HOST              # For Ollama (optional, defaults to localhost)
```

**Test Variables:**
```bash
BASE_URL                 # Application base URL
TEST_USER                # Test username/email
TEST_PASSWORD            # Test password
# ... any custom variables you need
```

### CLI Reference

#### `familiar run`

Run one or more test suites.

```bash
familiar run <suite_path> [options]

Options:
  --format TEXT                    Output format: text, json (default: text)
  --headless / --no-headless       Run browser in headless mode (default: headless)
  --verbose / --no-verbose         Show detailed logs (default: no-verbose)
  --fast                           Enable fast mode (flash_mode + speed prompt, ~2-3x faster)
  --scenario-agent-override        Use only scenario-level agent.md (ignore global agent.md)
  --all                            Run all suites in directory
  --help                           Show this message and exit
```

**Examples:**
```bash
# Run single suite
familiar run familiar/login-test

# Run with browser visible
familiar run familiar/login-test --no-headless

# Run with verbose output
familiar run familiar/login-test --verbose

# Run in fast mode (2-3x faster)
familiar run familiar/login-test --fast

# Combine fast mode with visible browser
familiar run familiar/login-test --fast --no-headless

# Run all suites in directory
familiar run familiar/ --all

# Output as JSON
familiar run familiar/login-test --format json
```

#### `familiar discover`

Discover available test suites in a directory.

```bash
familiar discover <directory> [options]

Options:
  --format TEXT        Output format: text, json (default: text)
  --validate           Validate suite configurations
  --help              Show this message and exit
```

**Examples:**
```bash
# Discover suites
familiar discover familiar/

# Get JSON output
familiar discover familiar/ --format json

# Discover and validate configurations
familiar discover familiar/ --validate
```

#### `familiar --version`

Show version information.

```bash
familiar --version
```

---

## 📄 Using .env Files

Familiar automatically loads environment variables from a `.env` file in your current directory. This makes configuration easier and more secure:

### Creating a .env File

```bash
# Create .env file in your project root
cat > .env << EOF
# LLM Configuration (choose one provider)
FAMILIAR_MODEL_PROVIDER=browser-use  # or: anthropic, openai, google, groq, azure, ollama
BROWSER_USE_API_KEY=your-api-key-here  # Get from https://cloud.browser-use.com

# Alternative provider example (uncomment to use):
# FAMILIAR_MODEL_PROVIDER=anthropic
# FAMILIAR_MODEL=claude-sonnet-4-0
# ANTHROPIC_API_KEY=your-api-key-here

# Application URLs
BASE_URL=https://staging.example.com
API_URL=https://api.staging.example.com

# Test Credentials  
TEST_USER=test@example.com
TEST_PASSWORD=securepassword123
ADMIN_USER=admin@example.com
ADMIN_PASSWORD=adminpass456

# Custom Variables
PROJECT_NAME=Test Project
TIMEOUT=30
EOF
```

### Important Notes

- ✅ `.env` files are loaded automatically - no setup needed
- ✅ Existing environment variables take precedence over `.env` values (secure)
- ✅ Missing `.env` file is fine - not required
- ⚠️ **Always add `.env` to your `.gitignore`!**

### Example `.gitignore`

```
# Environment files with secrets
.env
.env.local
.env.*.local

# Keep example file
!.env.example
```

### Using with Different Environments

```bash
# Local development
.env                  # Local credentials

# CI/CD
# Use system environment variables instead

# Multiple environments
.env.development      # Development config
.env.staging          # Staging config
.env.production       # Production config

# Load specific file:
cp .env.staging .env
familiar run tests/
```

---

## 🧠 Agent Instructions

Provide custom context and guidance to the AI agent to improve test execution. Agent instructions are written in Markdown and automatically loaded.

### How It Works

Agent instructions allow you to give the AI agent important context about your application, testing environment, or specific scenarios. The agent combines these instructions with your test steps to make better decisions.

**Three types of instructions:**

1. **Fast Mode Prompt** (`--fast` flag): Built-in behavioral instructions for speed
2. **Global Instructions** (`agent.md` in familiar root): Application-wide context
3. **Scenario Instructions** (`agent.md` in scenario directory): Test-specific context

**Combination order:** Fast Mode → Global → Scenario (most general to most specific)

### Global Agent Instructions

Create `agent.md` in your `familiar/` directory to provide context shared across all tests:

```markdown
<!-- familiar/agent.md -->

# Application Context

This is a SaaS project management application with the following key features:

## Authentication
- Uses SSO with Microsoft Azure AD
- Session timeout is 30 minutes
- Login page redirects to /dashboard after authentication

## Navigation
- Main navigation is a sidebar on the left
- Mobile view collapses sidebar into hamburger menu
- Search bar is always visible in top-right

## Known Issues
- Dashboard loads slowly (3-5 seconds typical)
- Notifications dropdown sometimes needs a second click
- Modal dialogs fade in over 500ms

## Test Data
- Test users are in format: test+{name}@company.com
- Default test workspace is "QA Workspace"
- Test projects are prefixed with "TEST-"
```

### Scenario Agent Instructions

Create `agent.md` in a scenario directory for test-specific context:

```markdown
<!-- familiar/checkout-flow/agent.md -->

# Checkout Flow Specifics

This test validates the e-commerce checkout process.

## Important Notes
- Cart must have at least 1 item before checkout
- Payment form uses Stripe test mode (card: 4242 4242 4242 4242)
- Shipping address validation is strict (use real US ZIP codes)
- Order confirmation can take 5-10 seconds to appear

## Test Data
- Test credit card: 4242 4242 4242 4242
- Expiry: Any future date
- CVV: Any 3 digits
- ZIP: Use 94105 (valid San Francisco ZIP)

## Common Issues
- Sometimes the "Place Order" button needs a brief wait before clicking
- If payment fails, refresh the page and try again
```

### Using Agent Instructions

**Basic usage** (both global and scenario instructions combined):
```bash
familiar run familiar/checkout-flow
# Agent receives: Global context + Scenario context + Test steps
```

**With fast mode** (adds speed instructions):
```bash
familiar run familiar/checkout-flow --fast
# Agent receives: Fast prompt + Global context + Scenario context + Test steps
```

**Scenario override** (ignore global, use only scenario):
```bash
familiar run familiar/checkout-flow --scenario-agent-override
# Agent receives: Scenario context only + Test steps
# Useful when scenario instructions conflict with global instructions
```

### Best Practices

**DO:**
- ✅ Keep instructions concise and relevant
- ✅ Focus on behavior-specific details the AI can't see
- ✅ Mention timing quirks, delays, or flaky UI elements
- ✅ Provide test data formats and requirements
- ✅ Note authentication flows and session handling
- ✅ Document known issues or workarounds

**DON'T:**
- ❌ Include step-by-step instructions (those go in your .md test files)
- ❌ Repeat information visible in the UI
- ❌ Make files too large (keep under 100KB, preferably much smaller)
- ❌ Include sensitive data (use environment variables instead)

### Example: Complete Setup

**Directory structure:**
```
project/
├── familiar/
│   ├── agent.md                    # Global instructions
│   ├── login-test/
│   │   ├── agent.md               # Scenario-specific instructions
│   │   ├── suite.yaml
│   │   ├── 00-navigate.md
│   │   └── 01-login.md
│   └── checkout-flow/
│       ├── agent.md               # Different scenario instructions
│       ├── suite.yaml
│       └── *.md steps
└── .env                           # Secrets and variables
```

**Global agent.md:**
```markdown
# MyApp Testing Context

## Authentication
- Uses OAuth2 with Google
- Test account: ${TEST_USER} (from .env)
- Session persists for 1 hour

## UI Behavior
- All pages lazy-load content (wait for spinners to disappear)
- Modals have 300ms fade-in animation
- Auto-save triggers 2 seconds after typing stops
```

**Scenario agent.md:**
```markdown
# Checkout Flow Notes

## Payment Processing
- Test mode uses Stripe test cards
- Processing takes 3-5 seconds
- Success redirect goes to /orders/{id}

## Known Quirks
- Cart totals update with 500ms debounce
- Shipping form validates on blur, not on submit
```

**Result:** The AI agent receives layered context that helps it handle timing, find elements correctly, and adapt to your application's specific behavior.

---

## ⚡ Performance Optimization

Familiar provides multiple ways to optimize test execution speed based on your needs.

### Fast Mode

Enable fast mode with the `--fast` CLI flag to reduce LLM inference time by 40-70%:

```bash
# Standard mode
familiar run tests/login-flow  # ~25-30s for 3-step test

# Fast mode  
familiar run tests/login-flow --fast  # ~10-15s for same test (2-3x faster)
```

**How it works:**
- Enables `flash_mode=True` on the browser-use Agent (skips LLM "thinking" phase)
- Adds speed optimization prompt to encourage concise responses
- Best for: Development, fast feedback loops, simple tests

**Trade-offs:**
- ✅ 2-3x faster execution
- ✅ Lower API costs (fewer tokens)
- ⚠️ May reduce reliability on complex/ambiguous steps
- ⚠️ Less detailed reasoning in logs

### Browser Timing Configuration

Fine-tune browser behavior in `suite.yaml` for optimal performance vs. reliability:

```yaml
name: "Login Test"

# Optional browser performance tuning
browser_profile:
  minimum_wait_page_load_time: 0.1  # Seconds to wait after page loads (0-30)
  wait_between_actions: 0.1         # Seconds to wait between actions (0-30)
  headless: true                    # Override global headless setting
```

**Configuration recipes:**

| Use Case | `minimum_wait_page_load_time` | `wait_between_actions` | When to Use |
|----------|------------------------------|------------------------|-------------|
| **Speed (Dev)** | 0.1 | 0.1 | Fast-loading apps, development testing |
| **Balanced** | 1.0 (default) | 1.0 (default) | General use, production testing |
| **Slow Apps** | 3.0 | 2.0 | Heavy apps, slow networks, SPAs |
| **Very Slow** | 5.0 | 3.0 | Legacy systems, unstable environments |

**Example configurations:**

```yaml
# Fast Mode (Development)
browser_profile:
  minimum_wait_page_load_time: 0.1
  wait_between_actions: 0.1
  # 50-70% faster, good for quick iteration

# Slow Application (Production)
browser_profile:
  minimum_wait_page_load_time: 3.0
  wait_between_actions: 2.0
  # More reliable, better for heavy/slow apps

# Mobile Simulation (Slower)
browser_profile:
  minimum_wait_page_load_time: 2.0
  wait_between_actions: 1.5
  # Simulates slower mobile devices
```

### Combining Optimizations

Stack multiple optimizations for maximum speed:

```bash
# Fast CLI flag + fast browser timing
familiar run tests/checkout-flow --fast

# With custom suite.yaml:
browser_profile:
  minimum_wait_page_load_time: 0.1
  wait_between_actions: 0.1
  
# Result: 50-70% faster execution
```

### Performance Metrics

Approximate speedups for a typical 3-step test (navigate → login → verify):

| Configuration | Time | Speedup | Best For |
|--------------|------|---------|----------|
| Standard (defaults) | 25-30s | Baseline | Production, complex tests |
| `--fast` only | 15-18s | 40-50% | Simple tests, dev iteration |
| Custom timing only | 18-22s | 30-40% | Fast apps, known stable |
| `--fast` + custom | 10-15s | 50-70% | Dev speed testing |

**Real-world example:**

```bash
# Before optimization (default settings)
$ time familiar run examples/e-commerce/
✓ e-commerce: 7/7 passed
real    3m 42s  # 222 seconds for 7 steps

# After optimization (--fast + browser_profile)
$ time familiar run examples/e-commerce/ --fast
# suite.yaml has: minimum_wait_page_load_time: 0.2, wait_between_actions: 0.2
✓ e-commerce: 7/7 passed  
real    1m 28s  # 88 seconds for 7 steps (2.5x faster!)
```

### When NOT to Optimize

Keep standard settings for:
- ❌ Production CI/CD pipelines (reliability > speed)
- ❌ Complex multi-step flows with timing dependencies
- ❌ Tests that verify loading states or animations
- ❌ First-time test development (need detailed logs)
- ❌ Flaky tests (optimizing makes them worse)

### Troubleshooting Performance Issues

If tests fail after optimization:

1. **Disable fast mode first**: Run without `--fast` to isolate timing vs. LLM issues
2. **Increase wait times gradually**: Try 0.5 → 1.0 → 2.0 for each setting
3. **Check logs with verbose**: `familiar run tests/ --verbose` shows timing details
4. **Test one step at a time**: Isolate which step fails with fast settings
5. **Verify app performance**: Slow apps need slower settings

---

## 💡 Examples

### Example: Multi-Step User Journey

```
familiar/user-journey/
├── suite.yaml
├── 00-signup.md
├── 01-onboarding.md
├── 02-create-project.md
├── 03-invite-team.md
└── 04-verify-email.md
```

**suite.yaml**:
```yaml
name: "Complete User Journey"
timeout: 600
step_timeout: 90
retry_policy:
  type: "exponential"
  max_retries: 3
  base_delay: 2.0
  max_delay: 30.0
fuzziness: 0.0
temperature: 0.5
```

### Example: Using Variables

**00-login.md**:
```markdown
# Login with Dynamic Credentials

Navigate to ${BASE_URL}/login

Enter email: ${USER_EMAIL}
Enter password: ${USER_PASSWORD}

Click the login button

Verify we're redirected to ${EXPECTED_LANDING_PAGE}
```

Run with:
```bash
export BASE_URL="https://staging.example.com"
export USER_EMAIL="testuser@example.com"
export USER_PASSWORD="Test123!"
export EXPECTED_LANDING_PAGE="/dashboard"

familiar run familiar/login-test
```

### Example: Best-of-N for Flaky Tests

For tests with inherent non-determinism (e.g., timing-sensitive operations):

```yaml
retry_policy:
  type: "best_of_n"
  n_runs: 5  # Run 5 times, succeed if any pass
```

### Example: Fuzziness for Long Suites

For long test suites where some failures are acceptable:

```yaml
fuzziness: 0.2  # Allow up to 20% of steps to fail
```

---

## 🔧 Advanced Usage

### Retry Policies

**Fixed Retry** (constant delay):
```yaml
retry_policy:
  type: "fixed"
  max_retries: 3
  delay: 2.0  # 2 seconds between retries
```

**Exponential Backoff** (increasing delays):
```yaml
retry_policy:
  type: "exponential"
  max_retries: 5
  base_delay: 1.0   # Start at 1s
  max_delay: 60.0   # Cap at 60s
  # Delays: 1s, 2s, 4s, 8s, 16s (capped at 60s)
```

**Best-of-N** (multiple attempts):
```yaml
retry_policy:
  type: "best_of_n"
  n_runs: 5  # Run 5 times total
  # Returns success if ANY run succeeds
```

### LLM Temperature Tuning

Temperature controls AI creativity vs. determinism:

```yaml
# More deterministic (recommended for critical paths)
temperature: 0.3

# Balanced (default)
temperature: 0.7

# More creative (may help with unusual UIs)
temperature: 0.9
```

### CI/CD Integration

**GitHub Actions:**
```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install Familiar
        run: uv pip install familiar
      
      - name: Run Tests
        env:
          FAMILIAR_MODEL_PROVIDER: anthropic
          FAMILIAR_MODEL: claude-3-5-sonnet-20241022
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          BASE_URL: https://staging.example.com
          TEST_USER: ${{ secrets.TEST_USER }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
        run: |
          familiar run familiar/ --all --headless --format json
```

**GitLab CI:**
```yaml
test:
  image: python:3.11
  before_script:
    - pip install familiar
  script:
    - familiar run familiar/ --all --headless
  variables:
    FAMILIAR_MODEL_PROVIDER: "anthropic"
    ANTHROPIC_API_KEY: $ANTHROPIC_API_KEY
```

---

## 🛠️ Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development setup and guidelines.

### Quick Start for Contributors

```bash
# Clone the repository
git clone https://github.com/adamrdrew/familiar.git
cd familiar

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linter
uv run ruff check src/

# Format code
uv run ruff format src/
```

---

## 🤝 Contributing

We welcome contributions! Whether it's:
- 🐛 Bug reports
- 💡 Feature requests
- 📝 Documentation improvements
- 🔧 Code contributions

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [browser-use](https://github.com/browser-use/browser-use) - AI-powered browser automation
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output
- [Pydantic](https://pydantic.dev/) - Data validation

---

## 📬 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/adamrdrew/familiar/issues)
- 💬 [Discussions](https://github.com/adamrdrew/familiar/discussions)

---

<div align="center">

**Made with ❤️ by developers who are tired of brittle E2E tests**

</div>
