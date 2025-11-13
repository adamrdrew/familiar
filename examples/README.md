# Familiar Examples

This directory contains example test suites demonstrating different use cases and patterns with Familiar.

## Available Examples

### 1. Basic Login (`basic-login/`)

**Complexity**: Beginner  
**Duration**: ~10-15 seconds  
**Purpose**: Simple authentication flow

A straightforward example showing:
- Navigation to a login page
- Form input (email and password)
- Form submission
- Verification of successful login

**Best for**: Getting started, understanding basic test structure

[View Example →](basic-login/)

### 2. E-Commerce Flow (`e-commerce/`)

**Complexity**: Intermediate  
**Duration**: ~25-35 seconds  
**Purpose**: Complete shopping journey

A comprehensive user journey covering:
- Homepage navigation
- Product search
- Product selection
- Add to cart
- Cart review
- Checkout process (stops before payment)

**Best for**: Understanding multi-step flows, real-world scenarios

[View Example →](e-commerce/)

## Quick Start

### 1. Choose an Example

```bash
cd familiar
ls examples/
```

### 2. Set Up Environment

Each example has a `README.md` with specific setup instructions. Generally:

```bash
# LLM Configuration
export FAMILIAR_MODEL_PROVIDER="anthropic"
export FAMILIAR_MODEL="claude-3-5-sonnet-20241022"
export ANTHROPIC_API_KEY="your-api-key"

# Application URL
export BASE_URL="https://your-app.com"

# Test Credentials (if needed)
export TEST_USER="test@example.com"
export TEST_PASSWORD="testpassword123"
```

### 3. Run the Example

```bash
# From project root
familiar run examples/basic-login

# Or with options
familiar run examples/basic-login --verbose --no-headless
```

## Example Structure

Each example follows this structure:

```
example-name/
├── README.md              # Setup and usage instructions
├── suite.yaml            # Suite configuration
├── 00-first-step.md      # First test step
├── 01-second-step.md     # Second test step
└── 0N-final-step.md      # Final test step
```

### File Naming Convention

Steps are executed in alphanumeric order:
- `00-` prefix for first step
- `01-` prefix for second step
- etc.

Use descriptive names:
- ✅ `00-navigate-to-login.md`
- ✅ `01-enter-credentials.md`
- ❌ `step1.md`
- ❌ `test.md`

## Configuration Patterns

### Conservative (Critical Paths)

```yaml
retry_policy:
  type: "fixed"
  max_retries: 1
fuzziness: 0.0
temperature: 0.3
```

**Use for**: Payment processing, data deletion, critical operations

### Balanced (Most Tests)

```yaml
retry_policy:
  type: "fixed"
  max_retries: 2
  delay: 1.0
fuzziness: 0.0
temperature: 0.6
```

**Use for**: Standard user flows, feature testing

### Tolerant (Exploratory)

```yaml
retry_policy:
  type: "exponential"
  max_retries: 3
  base_delay: 2.0
fuzziness: 0.2
temperature: 0.8
```

**Use for**: New features, flaky environments, exploratory testing

### Aggressive Retry (Non-deterministic)

```yaml
retry_policy:
  type: "best_of_n"
  n_runs: 5
fuzziness: 0.0
temperature: 0.5
```

**Use for**: Highly variable UIs, timing-sensitive operations

## Creating Your Own Example

### 1. Create Directory Structure

```bash
mkdir -p examples/my-test
cd examples/my-test
```

### 2. Create `suite.yaml`

```yaml
name: "My Test Suite"
timeout: 120
step_timeout: 30
retry_policy:
  type: "fixed"
  max_retries: 2
  delay: 1.0
fuzziness: 0.0
temperature: 0.6
headless: true
```

### 3. Create Test Steps

```bash
# Create step files
touch 00-first-step.md
touch 01-second-step.md
```

**Example Step (`00-first-step.md`):**

```markdown
# Step Name

Instructions for what the AI should do.

Use ${VARIABLES} for dynamic values.

## Expected Outcome

What should happen after this step completes.
```

### 4. Create README

Document:
- What the test does
- Prerequisites
- Required environment variables
- How to run it
- Expected output

### 5. Test It

```bash
familiar run examples/my-test --verbose
```

## Tips for Writing Examples

### Be Specific but Flexible

❌ **Too specific**:
```markdown
Click the button with id "submit-btn" at coordinates (100, 200)
```

✅ **Good**:
```markdown
Click the "Submit" or "Continue" button
```

### Use Variables

❌ **Hardcoded**:
```markdown
Navigate to https://example.com/login
```

✅ **With variables**:
```markdown
Navigate to ${BASE_URL}/login
```

### Describe Expected State

```markdown
# Login

Enter email: ${TEST_USER}
Enter password: ${TEST_PASSWORD}
Click login

## Expected Outcome

User should be redirected to /dashboard
User name should appear in header
No error messages should be visible
```

### Break Down Complex Actions

Instead of one big step:

❌ **Too complex**:
```markdown
# Complete Purchase
Navigate to cart, click checkout, enter shipping, enter payment, submit
```

✅ **Broken down**:
```markdown
# File: 01-open-cart.md
Navigate to cart, verify items

# File: 02-begin-checkout.md
Click checkout button

# File: 03-enter-shipping.md
Fill in shipping address

# File: 04-enter-payment.md
Fill in payment details
```

## Environment-Specific Examples

### Development Environment

```bash
export BASE_URL="http://localhost:3000"
export FAMILIAR_MODEL_PROVIDER="ollama"  # Use local model
export FAMILIAR_MODEL="llama3.2"
```

### Staging Environment

```bash
export BASE_URL="https://staging.example.com"
export FAMILIAR_MODEL_PROVIDER="anthropic"
export TEST_USER="staging-test@example.com"
```

### Production Monitoring

```bash
export BASE_URL="https://app.example.com"
export TEST_USER="prod-monitor@example.com"
# Use read-only test account
```

## Common Patterns

### Login Flow

```markdown
1. Navigate to login page
2. Enter credentials
3. Submit form
4. Verify logged in
```

### Form Submission

```markdown
1. Navigate to form
2. Fill in fields
3. Validate input
4. Submit
5. Verify success
```

### Search and Select

```markdown
1. Enter search term
2. Wait for results
3. Select item from results
4. Verify selection
```

### Multi-Page Wizard

```markdown
1. Complete page 1
2. Click "Next"
3. Complete page 2
4. Click "Next"
5. Review summary
6. Submit
```

## Troubleshooting Examples

### Example Fails Immediately

1. Check environment variables are set
2. Verify BASE_URL is accessible
3. Try with `--verbose` flag
4. Try with `--no-headless` to watch

### Example Passes Locally, Fails in CI

1. Increase timeouts in `suite.yaml`
2. Use exponential backoff retry
3. Check for environment-specific URLs
4. Verify headless mode works

### Example is Flaky

1. Increase `temperature` for more flexibility
2. Add retry policy
3. Use `best_of_n` retry type
4. Add explicit wait statements in steps

## Contributing Examples

Have a useful example? We'd love to include it!

1. Create the example in `examples/your-example/`
2. Include comprehensive `README.md`
3. Test it thoroughly
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Resources

- [Configuration Guide](../docs/configuration.md)
- [Test Suite Format](../docs/test-suite-format.md)
- [Getting Started Guide](../docs/getting-started.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

## Support

Questions about examples?
- 📖 Check the documentation
- 💬 Open a discussion
- 🐛 Report issues

Happy testing! 🚀

