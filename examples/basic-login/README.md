# Basic Login Flow Example

This example demonstrates a simple login test flow with Familiar.

## Overview

This test suite verifies that a user can successfully log into an application by:
1. Navigating to the login page (`00-navigate.md`)
2. Entering credentials (`01-enter-credentials.md`)
3. Submitting the form (`02-submit-login.md`)
4. Verifying successful authentication (`03-verify-logged-in.md`)

### Step Naming Convention

Steps use numeric prefixes (00-99) to define execution order:
- `00-navigate.md` → `01-enter-credentials.md` → `02-submit-login.md` → `03-verify-logged-in.md`
- Files without numeric prefixes (like this `README.md`) are automatically skipped
- All steps in this scenario share the SAME browser session (cumulative execution)
- Login state from step 02 persists into step 03 for verification

## Prerequisites

- A web application with a login page
- Test user credentials

## Setup

### 1. Set Environment Variables

```bash
export BASE_URL="https://your-app.com"
export TEST_USER="test@example.com"
export TEST_PASSWORD="testpassword123"

# Configure LLM
export FAMILIAR_MODEL_PROVIDER="anthropic"
export FAMILIAR_MODEL="claude-3-5-sonnet-20241022"
export ANTHROPIC_API_KEY="your-api-key"
```

### 2. Run the Test

```bash
# From the project root
familiar run examples/basic-login

# With verbose output
familiar run examples/basic-login --verbose

# Watch the browser (non-headless)
familiar run examples/basic-login --no-headless
```

## Expected Output

```
╭──────────────────────────────────────────────╮
│ ✓ Basic Login Flow                  PASSED  │
╰──────────────────────────────────────────────╯

┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Status ┃ Step                        ┃ Duration ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ ✓ PASS │ Navigate to Login Page      │   2.3s   │
│ ✓ PASS │ Enter Login Credentials     │   3.1s   │
│ ✓ PASS │ Submit Login Form           │   4.2s   │
│ ✓ PASS │ Verify Successful Login     │   1.8s   │
└────────┴─────────────────────────────┴──────────┘

Suite completed in 11.4s - All tests passed!
```

## Customization

### Adjust Retry Behavior

Edit `suite.yaml` to change retry settings:

```yaml
retry_policy:
  type: "exponential"  # Try exponential backoff
  max_retries: 3
  base_delay: 1.0
  max_delay: 10.0
```

### Add More Steps

Create additional markdown files with numeric prefixes:
- `04-change-password.md`
- `05-logout.md`
- `06-verify-logout.md`

Steps are executed in numeric order (00 → 01 → 02 ...) using the same browser session.

### Make It More Tolerant

Allow some steps to fail:

```yaml
fuzziness: 0.25  # Allow 25% of steps to fail
```

## Troubleshooting

**Test fails at credential entry:**
- Verify TEST_USER and TEST_PASSWORD are set correctly
- Check that field selectors in your app match expectations

**Test fails at verification:**
- Add more specific indicators in `03-verify-logged-in.md`
- Increase step_timeout if page loads slowly

**Too many retries:**
- Reduce max_retries in suite.yaml
- Check if your LLM API key is valid

## Related Examples

- [E-Commerce Flow](../e-commerce/) - More complex multi-step flow
- [API Testing](../api-testing/) - Testing with API interactions

