# Test Step Format Specification

**Version**: 1.0.0  
**Format**: Markdown with YAML frontmatter (optional)  
**File Extension**: `.md`  
**Naming Convention**: `NN-descriptive-name.md` where NN is 00-99

## Purpose

Test steps are natural language instructions written in Markdown that describe user actions and expected outcomes. The AI agent interprets these instructions to interact with web applications.

## File Naming Convention

### Required Format

```
NN-descriptive-name.md
```

**Rules**:
- `NN` MUST be two digits (00-99)
- Hyphen separator MUST be present
- Name MUST be lowercase with hyphens for spaces
- Files are executed in lexicographic order (00 first, 99 last)

**Valid Examples**:
- `00-load-dashboard.md`
- `01-create-project.md`
- `10-verify-notifications.md`
- `99-cleanup.md`

**Invalid Examples**:
- `1-login.md` (single digit)
- `00_login.md` (underscore instead of hyphen)
- `00-Login.md` (capital letter)
- `login.md` (no number prefix)

## Markdown Structure

### Basic Step Format

```markdown
# Step: Descriptive Step Name

Natural language instructions describing the user workflow.

## Expected Outcome

Natural language description of what should happen.
```

### Full Step Format with All Features

```markdown
---
timeout: 45
tags: [auth, critical]
---

# Step: Login to Application

Navigate to ${BASE_URL}/login page.

Enter the following credentials:
- Email: ${TEST_USER}
- Password: ${TEST_PASSWORD}

Click the "Sign In" button and wait for the dashboard to load.

## Expected Outcome

- Dashboard page is visible
- URL contains "/dashboard"
- User's name appears in the top-right corner
- No error messages are displayed

## Notes

This step requires valid test credentials to be set in environment variables.
```

## Markdown Components

### 1. YAML Frontmatter (Optional)

Place at the very beginning of the file between `---` delimiters.

**Supported Fields**:
```yaml
---
timeout: 45           # Step-specific timeout override (seconds)
tags: [auth, smoke]   # Custom tags for categorization
retry_override:       # Override suite retry policy for this step
  type: fixed
  max_retries: 5
  delay: 2.0
---
```

**Rules**:
- If present, MUST be at the very start of file
- Timeout overrides suite step_timeout
- Timeout MUST NOT exceed suite timeout
- Tags are informational (not used for execution logic)

### 2. Step Name (Required)

```markdown
# Step: Descriptive Name
```

**Rules**:
- MUST be the first heading (H1) in the file (after optional frontmatter)
- Prefix "Step:" is optional but recommended
- Used in logs and reports to identify the step
- If missing, filename is used as step name

### 3. Instructions (Required)

Natural language prose describing what the AI agent should do.

**Guidelines**:
- Write as if instructing a human user
- Be specific about elements to interact with (button text, field labels)
- Describe the sequence of actions clearly
- Include any data to enter or select

**Example**:
```markdown
Navigate to the Products page by clicking the "Products" link in the main navigation.

Find the product named "Widget Pro" in the product list.

Click the "Add to Cart" button for Widget Pro.

Verify that the cart icon in the header now shows "1 item".
```

### 4. Expected Outcome (Recommended)

Use H2 heading `## Expected Outcome` to describe success criteria.

**Example**:
```markdown
## Expected Outcome

- Product is added to cart
- Cart count increases by 1
- Success notification appears
- Product page remains visible
```

**Rules**:
- Written in natural language (not code assertions)
- Describes observable results
- Can be bullet points or prose
- AI agent uses this to verify success

### 5. Additional Sections (Optional)

Other H2 sections for documentation:

```markdown
## Notes

Additional context or warnings for the step.

## Prerequisites

What must be true before this step runs.

## Troubleshooting

Common issues and how to interpret failures.
```

These sections are informational and not interpreted as instructions.

## Variable Interpolation

### Syntax

```markdown
${VARIABLE_NAME}
${VARIABLE_NAME:-default_value}
```

**Rules**:
- Variable names MUST be uppercase with underscores
- Variables are replaced at runtime before passing to AI agent
- Undefined variables without defaults cause validation error
- Defaults are used if variable not in environment

**Examples**:
```markdown
Navigate to ${BASE_URL}/login

Email: ${TEST_USER}
Password: ${TEST_PASSWORD:-password123}

Product ID: ${PRODUCT_ID}  <!-- Must be defined, no default -->
```

**Resolution Order**:
1. Suite `env` section in suite.yaml
2. Process environment variables
3. Default value (if specified with `:-` syntax)
4. Error if not found

## Shared Step Inclusion

### Syntax

```markdown
!include shared/steps/login.md
```

**Rules**:
- `!include` directive MUST be on its own line
- Path is relative to test suite root directory
- Included file MUST be valid step format
- Includes are resolved recursively
- Circular includes (A includes B, B includes A) are detected and rejected

**Example Usage**:

**File: `familiar/auth-flow/00-setup.md`**
```markdown
# Step: Setup Test Environment

!include shared/steps/clear-cookies.md

!include shared/steps/navigate-to-home.md

Verify that the homepage loads successfully.
```

**Execution**:
1. Clear cookies step is executed
2. Navigate to home step is executed
3. Verify homepage instruction is executed

**Include Paths**:
- Relative to suite root: `shared/steps/login.md`
- Sibling directory: `../common/setup.md`
- Absolute paths NOT supported

## Natural Language Guidelines

### Writing Effective Instructions

**Good Example**:
```markdown
Click the blue "Submit" button at the bottom of the form to submit your order.
```

**Poor Example**:
```markdown
Click #submit-btn
```

**Why**: The AI agent interprets natural language, not CSS selectors. Describe elements as a human would see them.

### Specificity Levels

**Highly Specific** (use for critical steps):
```markdown
In the login form, find the input field labeled "Email Address" and enter "test@example.com".
Then find the input field labeled "Password" and enter "SecurePass123!".
Finally, click the green button with the text "Sign In" at the bottom of the form.
```

**Moderately Specific** (default):
```markdown
Enter email "test@example.com" and password "SecurePass123!" in the login form.
Click the Sign In button.
```

**Less Specific** (for flexible/adaptive tests):
```markdown
Log in with test credentials.
```

**Trade-off**: More specific = less adaptable to UI changes. Less specific = more AI interpretation, may be less reliable.

### Assertions in Natural Language

**Explicit Assertions**:
```markdown
Verify that:
- The user's name "John Doe" appears in the header
- The page title is "Dashboard"
- At least one project is visible in the project list
- The "Create New Project" button is enabled
```

**Implicit Assertions** (in expected outcome):
```markdown
## Expected Outcome

The shopping cart shows 1 item and the product is visible in the cart summary.
```

Both styles work. Explicit assertions are clearer but more verbose.

## Examples

### Example 1: Simple Login Step

**File: `00-login.md`**
```markdown
# Step: User Login

Navigate to ${BASE_URL}/login

Enter email: ${TEST_USER}
Enter password: ${TEST_PASSWORD}

Click "Sign In" button

## Expected Outcome

Dashboard page loads and shows user's name
```

### Example 2: Multi-Action Step with Validation

**File: `01-create-project.md`**
```markdown
---
timeout: 60
tags: [creation, critical]
---

# Step: Create New Project

Click the "New Project" button in the top right corner.

In the create project modal:
1. Enter project name: "${PROJECT_NAME}"
2. Select category: "Web Application"
3. Enable "Private" checkbox
4. Click "Create" button

Wait for the project to be created.

## Expected Outcome

- Success message: "Project created successfully"
- Redirected to project dashboard page
- Project name appears in the header
- Project listed in projects sidebar

## Notes

This step may take up to 30 seconds in staging environment.
```

### Example 3: Step with Shared Inclusion

**File: `02-invite-user.md`**
```markdown
# Step: Invite Team Member

!include shared/steps/navigate-to-settings.md

Click on "Team" tab.

Click "Invite Member" button.

Fill in invitation form:
- Email: ${INVITE_EMAIL}
- Role: ${INVITE_ROLE:-Member}

Click "Send Invitation".

## Expected Outcome

- Invitation sent confirmation appears
- New member listed in pending invitations
- Email notification sent (check logs)
```

### Example 4: Verification-Only Step

**File: `99-verify-cleanup.md`**
```markdown
# Step: Verify Test Data Cleanup

Navigate to ${BASE_URL}/admin/test-data

Verify that no test projects exist with name containing "TestProject".

Verify that no test users exist with email domain "@test.example.com".

## Expected Outcome

- Test projects list is empty or contains no test data
- Test users list is empty or contains no test data
- System is clean for next test run
```

## Validation Rules

Familiar validates steps before execution:

1. **File Naming**: Must match `NN-name.md` pattern
2. **Markdown Syntax**: Must be valid Markdown
3. **Step Name**: Must have at least one H1 heading (or valid filename)
4. **Variables**: All `${VAR}` references must be resolvable
5. **Includes**: All `!include` paths must exist
6. **Frontmatter**: If present, must be valid YAML
7. **Circular Includes**: Must not exist
8. **Timeout**: Step timeout must not exceed suite timeout

**Validation Errors Stop Execution**:
```
Error: Step validation failed for 01-login.md
  - Unresolved variable: ${ADMIN_PASSWORD}
  - Timeout (90s) exceeds suite timeout (60s)
```

## Best Practices

1. **One Concept Per Step**: Each step should test one user action or flow
2. **Clear Names**: File names and step names should be descriptive
3. **Use Variables**: Avoid hardcoding URLs, credentials, or test data
4. **Expected Outcomes**: Always include to help AI verify success
5. **Specificity**: Be as specific as needed, but no more
6. **Shared Steps**: Extract common flows (login, navigation) to shared steps
7. **Ordering**: Number steps logically (00=setup, 99=cleanup)
8. **Comments**: Use regular Markdown to document complex steps
9. **Timeouts**: Override only when step genuinely needs more/less time
10. **Idempotency**: Steps should be rerunnable without side effects when possible

## Anti-Patterns (Avoid)

❌ **CSS Selectors**: `Click button#submit-btn`  
✅ **Natural Language**: `Click the "Submit" button`

❌ **Code/Scripts**: Including JavaScript or Python code  
✅ **Instructions**: Describe what the user would do

❌ **Ambiguous**: `Do the thing`  
✅ **Specific**: `Click the Save button to save your changes`

❌ **Too Many Actions**: 20 different actions in one step  
✅ **Focused**: Break into 3-5 separate steps

❌ **No Verification**: Just actions, no expected outcome  
✅ **With Verification**: Always include expected outcome

## Version History

- **1.0.0** (2025-11-13): Initial specification

