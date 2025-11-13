# Phase 0: Research & Technical Decisions

**Feature**: AI-Driven End-to-End Testing Platform  
**Date**: 2025-11-13  
**Status**: Complete

## Overview

This document consolidates research findings and technical decisions for building Familiar, a CLI-based AI testing tool using browser-use. All "NEEDS CLARIFICATION" items from the Technical Context have been resolved.

## Technology Stack Decisions

### 1. Python 3.11 + uv for Dependency Management

**Decision**: Use Python 3.11 as the minimum version with uv for all project management.

**Rationale**:
- Python 3.11 provides improved async performance (critical for browser-use integration)
- Modern type hints and error messages improve developer experience
- uv provides fast dependency resolution, virtual environment management, and project scaffolding
- uv is becoming the standard for modern Python projects (backed by Astral)
- Easy integration with CI/CD (uv available via single binary)

**Alternatives Considered**:
- **Poetry**: Slower dependency resolution, requires separate tool for Python version management
- **pip + venv**: Manual dependency management, no lockfile standard, slower
- **Python 3.12+**: Would limit compatibility; 3.11 is widely available in CI systems

**Implementation Notes**:
- Use `pyproject.toml` with PEP 621 metadata
- Pin Python 3.11 in `.python-version` for uv auto-detection
- Use uv's built-in script runner for development tasks

### 2. browser-use for Browser Automation

**Decision**: Use browser-use as the core browser automation library.

**Rationale**:
- Specifically designed for AI agent-driven browser interaction [(source)](https://github.com/browser-use/browser-use)
- Built on Playwright (stable, well-maintained, cross-browser)
- Async-first design matches our async architecture requirements
- Provides high-level abstractions for AI agents while exposing low-level control
- Active community and frequent updates (72.5k stars, 7,718 commits)
- Handles common AI automation challenges (element detection, context extraction, action execution)

**Alternatives Considered**:
- **Selenium**: Older synchronous API, lacks AI-friendly abstractions
- **Playwright directly**: Would require building AI agent layer ourselves
- **Puppeteer**: JavaScript-only, doesn't integrate with Python AI tools

**Key Features Used**:
- `Agent` class for executing natural language tasks
- `Browser` class for browser lifecycle management
- Environment variable configuration for LLM selection
- Support for headless and headed modes
- Built-in logging and debugging capabilities

**Integration Approach**:
- Wrap browser-use `Agent` in our `StepExecutor` class
- Map Familiar's test steps to browser-use tasks
- Leverage browser-use's environment variables for LLM configuration
- Use browser-use's async API throughout Familiar

### 3. Click for CLI Framework

**Decision**: Use Click as the CLI framework.

**Rationale**:
- Industry standard for Python CLIs (used by Flask, pip, AWS CLI)
- Declarative command definition via decorators
- Built-in support for subcommands (`familiar run`, `familiar discover`)
- Automatic help generation and validation
- Easy testing (commands are just functions)
- Rich parameter types and validation

**Alternatives Considered**:
- **argparse**: Standard library but more verbose, harder to test
- **Typer**: Modern but adds FastAPI dependency, overkill for our needs
- **Fire**: Too magical, harder to control exact CLI behavior

**CLI Structure**:
```python
@click.group()
def cli():
    """Familiar: AI-driven end-to-end testing tool"""
    pass

@cli.command()
@click.argument('suite_or_path')
@click.option('--format', type=click.Choice(['text', 'json', 'junit']))
def run(suite_or_path, format):
    """Run test suites"""
    pass
```

### 4. Configuration via Environment Variables

**Decision**: All configuration via environment variables, no required config files.

**Rationale**:
- 12-factor app principles (config in environment)
- CI/CD friendly (no file management required)
- browser-use already uses env vars for LLM configuration
- Consistent with modern CLI tools (Docker, kubectl, etc.)
- Easy secret management (CI secrets inject as env vars)

**Environment Variable Schema**:
```bash
# Familiar Configuration
FAMILIAR_TEST_DIR=./familiar           # Test suite directory
FAMILIAR_LOG_LEVEL=INFO               # Logging level
FAMILIAR_DEFAULT_TIMEOUT=30           # Default step timeout (seconds)
FAMILIAR_DEFAULT_RETRIES=3            # Default retry count
FAMILIAR_HEADLESS=true                # Browser headless mode

# browser-use Configuration (passed through)
BROWSER_USE_API_KEY=xxx               # Browser-use cloud API key
OPENAI_API_KEY=xxx                    # OpenAI for LLM
ANTHROPIC_API_KEY=xxx                 # Claude for LLM
# ... other LLM providers
```

**Override Order**:
1. Suite YAML config (most specific)
2. Environment variables
3. Built-in defaults (least specific)

### 5. Test Suite Format: YAML + Markdown

**Decision**: YAML for suite configuration, Markdown for test steps.

**Rationale**:
- YAML is human-readable and widely understood by QA engineers
- Markdown is familiar to everyone, supports rich formatting
- Clear separation: YAML = configuration, Markdown = test instructions
- Both formats are version control friendly (plain text, clear diffs)
- Easy to validate and parse (PyYAML, markdown-it)

**Suite YAML Schema**:
```yaml
name: "Login Flow Test"
timeout: 60                    # Total suite timeout (seconds)
step_timeout: 30              # Individual step timeout
retry_policy:
  type: "best_of_n"           # fixed | best_of_n | exponential
  max_retries: 3
  n_runs: 5                   # For best_of_n
fuzziness: 0.2                # Allow 20% of steps to fail
temperature: 0.7              # AI improvisation level (0.0-1.0)
env:                          # Suite-specific environment variables
  BASE_URL: "https://app.example.com"
  TEST_USER: "qa@example.com"
```

**Step Markdown Format**:
```markdown
# Step: Login to Dashboard

Navigate to ${BASE_URL}/login and log in using:
- Email: ${TEST_USER}
- Password: ${TEST_PASSWORD}

Verify that the dashboard loads and shows the user's name in the header.

## Expected Outcome
- Dashboard URL contains "/dashboard"
- User greeting visible in top right
```

**Variable Interpolation**:
- `${VAR_NAME}` syntax in Markdown replaced with environment variable values
- Fails fast if required variable missing
- Supports defaults: `${VAR_NAME:-default_value}`

### 6. Logging Strategy

**Decision**: Use Python's standard logging with structured output and rich console formatting.

**Rationale**:
- Standard library logging is familiar and well-understood
- Structured logging (JSON) for machine parsing
- Rich terminal output for human readability during development
- Separate log levels for different audiences (DEBUG for devs, INFO for QA)

**Logging Architecture**:
- **Console Handler**: Rich-formatted for terminal (colors, progress bars)
- **File Handler**: JSON-structured for post-mortem analysis
- **CI Handler**: Plain text with timestamps for CI log aggregation

**Log Levels**:
- **DEBUG**: Internal state, browser-use calls, retry attempts
- **INFO**: Step execution, suite progress, results summary
- **WARNING**: Recoverable errors, retry triggers
- **ERROR**: Test failures, unrecoverable errors

### 7. Output Formats

**Decision**: Support three output formats via strategy pattern.

**Formats**:
1. **Text** (default): Human-readable console output with rich formatting
2. **JSON**: Machine-readable structured output for custom processing
3. **JUnit XML**: Standard format for CI/CD integration (Jenkins, GitHub Actions, GitLab CI)

**Implementation**:
```python
class OutputFormatter(Protocol):
    def format(self, result: SuiteResult) -> str: ...

class JUnitFormatter(OutputFormatter):
    def format(self, result: SuiteResult) -> str:
        # Generate JUnit XML
        pass
```

**CI/CD Integration Pattern**:
```bash
# GitHub Actions
familiar run --all --format junit > test-results.xml

# GitLab CI
familiar run --suite critical --format junit | tee results.xml

# Custom processing
familiar run --all --format json | jq '.failed_count'
```

## Best Practices Research

### 1. Python CLI Tool Distribution

**Findings**:
- **PyPI**: Standard Python package index, `pip install familiar`
- **uv**: Direct install via `uvx familiar` (no pip required)
- **Homebrew**: Requires formula, good for macOS users

**Distribution Strategy**:
1. **Primary**: PyPI via `uv publish`
2. **Secondary**: GitHub Releases with pre-built wheels
3. **Future**: Homebrew tap for macOS users

**Project Structure for Distribution**:
- Use src-layout (`src/familiar/`) to avoid import issues
- Define CLI entry point in `pyproject.toml`:
  ```toml
  [project.scripts]
  familiar = "familiar.cli.main:cli"
  ```
- Include `py.typed` for type hint distribution

### 2. Async/Await Throughout

**Findings**:
- browser-use is fully async (all methods are `async def`)
- Python 3.11 improved asyncio performance significantly
- Proper async context management critical for browser lifecycle

**Implementation Guidelines**:
- All core functions async (`async def execute_step`, `async def run_suite`)
- Use `asyncio.run()` only at CLI entry point
- Context managers for browser lifecycle:
  ```python
  async with Browser() as browser:
      async with Agent(browser=browser, task=task) as agent:
          await agent.run()
  ```
- Parallel execution (future) via `asyncio.gather()`

### 3. Error Handling for Non-Deterministic AI

**Findings**:
- AI agents can fail for transient reasons (model API timeout, ambiguous UI)
- Need to distinguish: permanent failure vs. retry-able failure
- Browser crashes must be handled separately from test failures

**Error Taxonomy**:
1. **Permanent Errors**: Invalid test syntax, missing environment variables
2. **Retry-able Errors**: Browser timeout, AI model timeout, ambiguous element
3. **Infrastructure Errors**: Browser crash, network failure, API key invalid

**Retry Strategy**:
```python
async def execute_with_retry(step, policy):
    for attempt in range(policy.max_retries):
        try:
            result = await execute_step(step)
            if result.success:
                return result
        except RetryableError as e:
            if attempt == policy.max_retries - 1:
                raise
            await asyncio.sleep(policy.backoff(attempt))
        except PermanentError:
            raise  # Don't retry
```

### 4. Test Discovery Patterns

**Findings**:
- pytest uses file naming conventions (`test_*.py`)
- Jest uses directory scanning with glob patterns
- Cargo uses manifest files (`Cargo.toml`)

**Familiar's Approach**:
- **Convention**: Suites are directories containing `suite.yaml`
- **Discovery**: Walk from root directory, find all `suite.yaml` files
- **Ordering**: Steps sorted lexicographically (`00-first.md`, `01-second.md`)
- **Shared Steps**: Special `shared/` directory at root

**Discovery Algorithm**:
```python
def discover_suites(root: Path) -> List[TestSuite]:
    suites = []
    for yaml_file in root.rglob("suite.yaml"):
        if yaml_file.parent.name == "shared":
            continue  # Skip shared directory
        suite = parse_suite(yaml_file)
        suites.append(suite)
    return sorted(suites, key=lambda s: s.path)
```

### 5. CI/CD Integration Patterns

**Findings**:
- Exit codes critical for CI pass/fail detection
- Structured output formats expected (JUnit XML, JSON)
- Parallel test execution reduces CI time
- Headless browser required for most CI environments

**CI Best Practices**:
```yaml
# GitHub Actions Example
- name: Run Familiar Tests
  run: |
    export FAMILIAR_HEADLESS=true
    familiar run --all --format junit > results.xml
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    BASE_URL: https://staging.example.com

- name: Publish Test Results
  uses: EnricoMi/publish-unit-test-result-action@v2
  if: always()
  with:
    files: results.xml
```

**Exit Code Contract**:
- `0`: All tests passed
- `1`: One or more tests failed
- `2`: Configuration error (invalid YAML, missing env vars)
- `3`: Infrastructure error (browser crash, network failure)

## Integration Patterns

### browser-use Integration

**Core Integration Points**:

1. **Agent Initialization**:
```python
from browser_use import Agent, Browser, ChatBrowserUse

async def create_agent(step: TestStep, config: SuiteConfig) -> Agent:
    browser = Browser(
        headless=config.headless,
        # browser-use reads LLM config from env vars
    )
    llm = ChatBrowserUse()  # or other LLM from env
    agent = Agent(
        task=step.content,  # Natural language from markdown
        llm=llm,
        browser=browser,
    )
    return agent
```

2. **Step Execution**:
```python
async def execute_step(step: TestStep) -> StepResult:
    agent = await create_agent(step)
    try:
        history = await agent.run()
        return StepResult(
            success=True,
            logs=extract_logs(history),
            duration=calculate_duration(history),
        )
    except Exception as e:
        return StepResult(
            success=False,
            error=str(e),
            logs=extract_error_context(e),
        )
```

3. **Environment Variable Pass-Through**:
- Familiar sets `FAMILIAR_*` variables
- browser-use reads `BROWSER_USE_*`, `OPENAI_API_KEY`, etc.
- Both coexist without conflict
- Documentation lists all supported env vars

### Shared Step Resolution

**Pattern**: Allow steps to reference shared steps via special syntax.

**Syntax in Markdown**:
```markdown
# Step: Create New Project

!include shared/steps/login.md

Navigate to Projects page and click "New Project" button.

Fill in project details:
- Name: ${PROJECT_NAME}
- Description: ${PROJECT_DESC}
```

**Implementation**:
```python
def resolve_includes(step_content: str, root: Path) -> str:
    include_pattern = r'^!include\s+(.+\.md)$'
    lines = []
    for line in step_content.split('\n'):
        if match := re.match(include_pattern, line):
            include_path = root / match.group(1)
            included = include_path.read_text()
            lines.append(resolve_includes(included, root))
        else:
            lines.append(line)
    return '\n'.join(lines)
```

## Performance Considerations

### Test Execution Speed

**Goal**: Within 2x of manual user workflow speed (SC-003)

**Factors**:
- **AI Model Latency**: 1-5 seconds per action (depends on model)
- **Browser Rendering**: 100-500ms per page load
- **Network**: Variable (target application dependent)
- **Familiar Overhead**: <100ms per step (parsing, logging)

**Optimizations**:
1. **Async Throughout**: No blocking operations
2. **Parallel Execution**: Future feature for independent suites
3. **Browser Reuse**: Keep browser open across steps in same suite
4. **Efficient Logging**: Buffer logs, write in batches

### Test Discovery Performance

**Goal**: Sub-second discovery for 100+ test suites (SC-009)

**Approach**:
- Use `pathlib.rglob()` (efficient C implementation)
- Lazy parsing (parse YAML only when needed)
- Cache discovery results (optional via `--cache` flag)

**Benchmark Target**:
- 100 suites: <500ms
- 1000 suites: <2s

## Security Considerations

### Credential Management

**Approach**:
- Environment variables for secrets (no files)
- Support `.env` file for local development (never committed)
- CI injects secrets as env vars
- Mask secrets in logs (replace with `***`)

**Implementation**:
```python
SENSITIVE_ENV_VARS = ['PASSWORD', 'API_KEY', 'SECRET', 'TOKEN']

def mask_sensitive_values(log_entry: str, env: dict) -> str:
    for key, value in env.items():
        if any(sensitive in key.upper() for sensitive in SENSITIVE_ENV_VARS):
            log_entry = log_entry.replace(value, '***')
    return log_entry
```

### Browser Security

**Considerations**:
- Tests run against potentially untrusted web applications
- Browser-use handles sandboxing via Playwright
- Screenshots may contain sensitive data (mask via config)

## Dependency Versions

**Core Dependencies** (to be added to `pyproject.toml`):
```toml
[project.dependencies]
browser-use = ">=0.9.5"      # Latest stable with sandbox support
click = ">=8.1.0"            # Modern Click with type hints
pydantic = ">=2.0.0"         # V2 for performance
pyyaml = ">=6.0"             # Security fixes
rich = ">=13.0.0"            # Modern terminal formatting
```

**Development Dependencies**:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.5.0",
    "ruff>=0.0.290",         # Fast linter/formatter
]
```

## Open Questions Resolved

All "NEEDS CLARIFICATION" items from Technical Context have been resolved:

1. ✅ **Language/Version**: Python 3.11 (stable, modern, good async)
2. ✅ **Dependencies**: browser-use, Click, PyYAML, pydantic, rich
3. ✅ **Testing**: pytest with async support
4. ✅ **Distribution**: PyPI via uv, with Homebrew as future enhancement
5. ✅ **Configuration**: Environment variables, no required config files
6. ✅ **Output Formats**: Text, JSON, JUnit XML

## Next Steps

Phase 0 research complete. Proceed to Phase 1:
- ✅ Create `data-model.md` with entity definitions
- ✅ Create `contracts/` with YAML schemas and CLI interface
- ✅ Create `quickstart.md` with getting started guide
- ✅ Update agent context file

**Status**: ✅ Ready for Phase 1 Design

