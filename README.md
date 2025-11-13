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
- `*.md`: Test step files (executed in alphanumeric order)
- Optional `shared/` directory for reusable steps

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
  --format TEXT        Output format: text, json (default: text)
  --headless / --no-headless  Run browser in headless mode (default: headless)
  --verbose / --no-verbose    Show detailed logs (default: no-verbose)
  --all                Run all suites in directory
  --help               Show this message and exit
```

**Examples:**
```bash
# Run single suite
familiar run familiar/login-test

# Run with browser visible
familiar run familiar/login-test --no-headless

# Run with verbose output
familiar run familiar/login-test --verbose

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
  --help              Show this message and exit
```

**Examples:**
```bash
# Discover suites
familiar discover familiar/

# Get JSON output
familiar discover familiar/ --format json
```

#### `familiar validate`

Validate suite configurations.

```bash
familiar validate <suite_path>

Options:
  --help              Show this message and exit
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
