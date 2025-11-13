# Familiar

**AI-driven end-to-end testing for web applications**

Familiar enables you to write tests in natural language and have an autonomous AI agent execute them, mimicking real user interactions without brittle CSS selectors.

## Features

- 🤖 **Natural Language Tests**: Write test steps in plain English using Markdown
- 🎯 **AI-Powered Execution**: Uses browser-use to interpret and execute test workflows
- 📊 **Structured Results**: Outputs in text, JSON, or JUnit XML formats
- 🔄 **Smart Retries**: Configurable retry policies to handle AI non-determinism
- 🐛 **Interactive Debugging**: Step-through execution with browser inspection
- 🚀 **CI/CD Ready**: Seamless integration with GitHub Actions, GitLab CI, and more

## Installation

```bash
# Using uv (recommended)
uv pip install familiar

# Using pip
pip install familiar
```

## Quick Start

### 1. Create a test suite

```bash
mkdir -p familiar/login-flow
```

Create `familiar/login-flow/suite.yaml`:

```yaml
name: "Login Flow Test"
timeout: 120
step_timeout: 30
retry_policy:
  type: "fixed"
  max_retries: 3
```

Create `familiar/login-flow/00-login.md`:

```markdown
# Step: Login to Application

Navigate to ${BASE_URL}/login

Enter the following credentials:
- Email: ${TEST_USER}
- Password: ${TEST_PASSWORD}

Click the "Sign In" button

## Expected Outcome
- Dashboard page loads
- User name appears in header
```

### 2. Run your test

```bash
# Set environment variables
export BASE_URL="https://your-app.com"
export TEST_USER="test@example.com"
export TEST_PASSWORD="password123"
export OPENAI_API_KEY="your-openai-key"

# Run the test
familiar run familiar/login-flow
```

### 3. View results

```
Running Familiar v0.1.0

═══════════════════════════════════════════════════════
Suite: Login Flow Test
═══════════════════════════════════════════════════════

✓ 00-login.md (8.2s)

Suite Result: PASSED (8.2s)
  Steps: 1 passed, 0 failed, 1 total
```

## CLI Commands

- `familiar run [suite]` - Run test suites
- `familiar discover` - Discover available test suites
- `familiar validate` - Validate suite configurations
- `familiar init [name]` - Create a new test suite
- `familiar --help` - Show all commands

## Documentation

- [Getting Started](docs/getting-started.md)
- [Test Suite Format](docs/test-suite-format.md)
- [Configuration](docs/configuration.md)
- [CI/CD Integration](docs/ci-integration.md)

## Requirements

- Python 3.11+
- Chrome/Chromium browser
- OpenAI API key (or other supported LLM provider)

## License

MIT

## Contributing

Contributions welcome! Please see our [contributing guidelines](CONTRIBUTING.md).

