# Contributing to Familiar

Thank you for your interest in contributing to Familiar! This guide will help you get started with development, testing, and submitting changes.

## 🌟 Ways to Contribute

- **🐛 Bug Reports**: Found a bug? Open an issue with reproduction steps
- **💡 Feature Requests**: Have an idea? Start a discussion or open an issue
- **📝 Documentation**: Improve docs, add examples, fix typos
- **🔧 Code**: Fix bugs, implement features, improve performance
- **🧪 Testing**: Add tests, improve coverage, report flaky tests

## 🚀 Development Setup

### Prerequisites

- **Python 3.11+** (managed via uv)
- **uv** - Fast Python package installer and version manager
- **Git** - Version control
- **An LLM API Key** - For testing (Anthropic Claude, OpenAI, etc.)

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/familiar.git
cd familiar

# uv will automatically:
# - Install Python 3.11 if needed (via .python-version)
# - Create a virtual environment
# - Install all dependencies (via pyproject.toml)
uv sync

# Verify installation
uv run familiar --version
```

### 3. Configure Development Environment

Create a `.env` file for development:

```bash
# .env
FAMILIAR_MODEL_PROVIDER=anthropic
FAMILIAR_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your-api-key-here

# Test environment
BASE_URL=https://example.com
TEST_USER=test@example.com
TEST_PASSWORD=testpassword
```

**Note**: Never commit `.env` files! They're already in `.gitignore`.

### 4. Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/familiar --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run tests with verbose output
uv run pytest -v

# Run tests in parallel
uv run pytest -n auto
```

### 5. Code Quality

```bash
# Run linter
uv run ruff check src/

# Auto-fix linting issues
uv run ruff check src/ --fix

# Format code
uv run ruff format src/

# Type checking
uv run mypy src/
```

---

## 🏗️ Development with Speckit

Familiar is developed using **Speckit**, a specification-first development workflow that ensures quality and maintainability.

### What is Speckit?

Speckit is a development methodology that uses:
- **Constitution**: Core design principles (in `.specify/memory/constitution.md`)
- **Specifications**: Feature specs with user stories and requirements
- **Plans**: Implementation plans with technical details
- **Tasks**: Granular, trackable work items
- **Tests**: Test-driven development approach

### Using Speckit Commands

Speckit integrates with Cursor AI to provide structured development commands:

#### `/speckit.constitution`

Define or update the project's constitutional principles.

```
/speckit.constitution this project follows clean architecture principles...
```

#### `/speckit.specify`

Create a feature specification with user stories, requirements, and success criteria.

```
/speckit.specify I need to add support for parallel test execution
```

This creates a spec in `specs/NNN-feature-name/spec.md` with:
- User stories
- Functional requirements
- Success criteria
- Edge cases

#### `/speckit.plan`

Create an implementation plan for a specification.

```
/speckit.plan
```

Creates `specs/NNN-feature-name/plan.md` with:
- Technical approach
- Architecture decisions
- File structure
- Constitutional checks

#### `/speckit.tasks`

Generate granular tasks from the plan.

```
/speckit.tasks
```

Creates `specs/NNN-feature-name/tasks.md` with:
- Ordered, trackable tasks
- Dependencies
- Phase organization
- Checkpoints

#### `/speckit.implement`

Begin implementation following the tasks.

```
/speckit.implement
```

Cursor AI will:
1. Follow tasks in order
2. Write tests first (TDD)
3. Implement features
4. Run tests and fix issues
5. Mark tasks as complete

### Speckit Workflow Example

Let's say you want to add JUnit XML output support:

```bash
# 1. Specify the feature
/speckit.specify Add JUnit XML output format for CI/CD integration

# AI generates spec with:
# - User Story: As a CI/CD engineer, I want JUnit XML output...
# - Functional Requirements: FR01: Must output valid JUnit XML...
# - Success Criteria: Can parse output in Jenkins/GitHub Actions...

# 2. Create implementation plan
/speckit.plan

# AI creates plan with:
# - Technical approach (use junit-xml library)
# - File structure (src/familiar/formatters/junit.py)
# - Constitutional checks (single responsibility, testability)

# 3. Generate tasks
/speckit.tasks

# AI creates tasks like:
# - [ ] T001 [P] Add junit-xml dependency to pyproject.toml
# - [ ] T002 [P] Create JunitFormatter class
# - [ ] T003 [P] Implement TestCase conversion
# ...

# 4. Implement
/speckit.implement

# AI implements features following tasks, writing tests first
```

### Speckit Directory Structure

```
familiar/
├── .specify/
│   └── memory/
│       └── constitution.md          # Project principles
├── specs/
│   └── 001-ai-e2e-testing/         # Feature spec
│       ├── spec.md                  # Feature specification
│       ├── plan.md                  # Implementation plan
│       ├── tasks.md                 # Granular tasks
│       ├── research.md              # Technical research
│       ├── data-model.md            # Data structures
│       ├── contracts/               # Interface contracts
│       │   ├── cli-interface.md
│       │   ├── suite-schema.yaml
│       │   └── step-format.md
│       └── checklists/              # Quality checklists
│           └── requirements.md
└── [rest of project...]
```

---

## 📋 Development Guidelines

### Code Style

We follow the principles defined in `.specify/memory/constitution.md`:

#### 1. Easy to Change
- Small, focused classes and functions
- Low coupling between components
- Explicit dependencies

#### 2. Single Responsibility
- Each class has one reason to change
- Methods do one thing well
- Clear, descriptive names

#### 3. Stable Public Interfaces
- Minimal public APIs
- Backward compatibility
- Clear contracts

#### 4. Polymorphism Over Conditionals
- Use protocols and abstract base classes
- Strategy pattern for behavior variation
- Dependency injection

#### 5. Behavior-Based Testing
- Test what code does, not how
- Mock dependencies, not implementation details
- Fast, isolated unit tests

#### 6. Code as User Interface
- Readable by 80% of developers
- Clear over clever
- Self-documenting when possible

#### 7. Humane Code
- Explicit over implicit
- Reduce abstraction layers
- Straightforward implementations

#### 8. Test-Driven Development
- Write tests first
- Red → Green → Refactor
- High coverage

### Python Conventions

```python
# Use type hints
def execute_step(self, step: TestStep, timeout: int = 60) -> TestResult:
    """Execute a single test step.
    
    Args:
        step: The test step to execute.
        timeout: Maximum execution time in seconds.
    
    Returns:
        TestResult with execution outcome.
    """
    ...

# Use dataclasses for data structures
@dataclass
class TestResult:
    """Result of executing a test step."""
    step_name: str
    status: ResultStatus
    duration: float
    logs: List[LogEntry] = field(default_factory=list)

# Use protocols for polymorphism
class RetryPolicy(Protocol):
    """Protocol for retry policies."""
    max_retries: int
    
    def should_retry(self, attempt: int) -> bool:
        ...
    
    def get_delay(self, attempt: int) -> float:
        ...

# Explicit is better than implicit
# Good:
user_email = os.getenv("USER_EMAIL")
if not user_email:
    raise ValueError("USER_EMAIL environment variable is required")

# Avoid magic:
# Bad: Silently default or complex fallback chains
```

### Project Structure

```
familiar/
├── src/familiar/              # Source code
│   ├── __init__.py
│   ├── __main__.py           # Entry point
│   ├── cli/                  # CLI commands
│   │   ├── __init__.py
│   │   ├── main.py          # Main CLI group
│   │   └── run.py           # Run command
│   ├── core/                 # Core business logic
│   │   ├── __init__.py
│   │   ├── discovery.py     # Suite discovery
│   │   ├── parser.py        # Suite parsing
│   │   ├── executor.py      # Step execution
│   │   ├── runner.py        # Suite orchestration
│   │   └── retry.py         # Retry policies
│   ├── models/               # Data models
│   │   ├── __init__.py
│   │   ├── suite.py         # Suite models
│   │   ├── step.py          # Step models
│   │   └── result.py        # Result models
│   ├── formatters/           # Output formatters
│   │   ├── __init__.py
│   │   └── text.py          # Text formatter
│   ├── logging/              # Logging setup
│   │   ├── __init__.py
│   │   ├── setup.py
│   │   └── handlers.py
│   └── utils/                # Utilities
│       ├── __init__.py
│       ├── env.py           # Environment helpers
│       ├── interpolation.py # Variable interpolation
│       └── browser.py       # Browser-use integration
├── tests/                    # Tests
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── unit/                # Unit tests
│   │   ├── test_models.py
│   │   ├── test_parser.py
│   │   ├── test_discovery.py
│   │   ├── test_retry.py
│   │   └── test_utils.py
│   ├── integration/         # Integration tests
│   │   ├── test_cli.py
│   │   ├── test_runner.py
│   │   └── test_multi_suite.py
│   ├── contract/            # Contract tests
│   │   └── test_cli_interface.py
│   └── fixtures/            # Test fixtures
│       └── sample-suite/
├── docs/                    # Documentation
├── specs/                   # Speckit specifications
├── pyproject.toml          # Project configuration
├── .python-version         # Python version (3.11)
├── README.md               # Main documentation
└── CONTRIBUTING.md         # This file
```

### Testing Guidelines

#### Test Organization

- **Unit Tests** (`tests/unit/`): Test individual functions/classes in isolation
- **Integration Tests** (`tests/integration/`): Test components working together
- **Contract Tests** (`tests/contract/`): Test external interfaces (CLI, file formats)

#### Writing Tests

```python
# Use descriptive test names
def test_fixed_retry_should_retry_within_max_attempts():
    """Test that fixed retry allows retries up to max_retries."""
    policy = FixedRetry(max_retries=3, delay=1.0)
    
    assert policy.should_retry(attempt=0) is True
    assert policy.should_retry(attempt=2) is True
    assert policy.should_retry(attempt=3) is False

# Test behavior, not implementation
def test_suite_result_success_with_fuzziness():
    """Test that suite passes when failures are within fuzziness tolerance."""
    # Given: A suite with 10 tests, 2 failures, 20% fuzziness
    results = [
        TestResult(step_name=f"Step {i}", status=ResultStatus.PASSED, duration=1.0)
        for i in range(8)
    ] + [
        TestResult(step_name="Failed 1", status=ResultStatus.FAILED, duration=1.0),
        TestResult(step_name="Failed 2", status=ResultStatus.FAILED, duration=1.0),
    ]
    
    suite_result = SuiteResult(
        suite_name="Test",
        test_results=results,
        total_duration=10.0,
        fuzziness=0.2,  # 20% tolerance
    )
    
    # Then: Suite should pass (failure rate = 20%, within tolerance)
    assert suite_result.success is True

# Use fixtures for common setup
@pytest.fixture
def sample_suite(tmp_path):
    """Create a sample test suite directory."""
    suite_dir = tmp_path / "test-suite"
    suite_dir.mkdir()
    
    (suite_dir / "suite.yaml").write_text("""
name: Test Suite
timeout: 60
step_timeout: 30
""")
    
    (suite_dir / "00-test.md").write_text("# Test Step\n\nTest content")
    
    return suite_dir
```

#### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test category
uv run pytest tests/unit/
uv run pytest tests/integration/

# Run specific test file
uv run pytest tests/unit/test_retry.py

# Run specific test
uv run pytest tests/unit/test_retry.py::test_fixed_retry_basic

# Run with coverage
uv run pytest --cov=src/familiar --cov-report=html
open htmlcov/index.html

# Run in parallel
uv run pytest -n auto
```

---

## 🔄 Contribution Workflow

### 1. Create an Issue

Before starting work:
1. Check existing issues to avoid duplication
2. Create a new issue describing:
   - Problem or feature request
   - Proposed solution
   - Any relevant context

### 2. Fork and Branch

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/familiar.git
cd familiar

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 3. Develop with Speckit (Optional but Recommended)

For larger features, use Speckit workflow:

```bash
# In Cursor AI:
/speckit.specify [your feature description]
/speckit.plan
/speckit.tasks
/speckit.implement
```

### 4. Make Changes

```bash
# Make your changes
# Write tests first (TDD)
# Implement the feature
# Run tests frequently

# Format and lint
uv run ruff format src/ tests/
uv run ruff check src/ tests/ --fix
uv run mypy src/

# Run tests
uv run pytest
```

### 5. Commit

Write clear, descriptive commit messages:

```bash
# Good commit messages:
git commit -m "Add exponential backoff retry policy"
git commit -m "Fix retry count not updating in test results"
git commit -m "Update README with retry policy examples"

# Bad commit messages:
git commit -m "fix stuff"
git commit -m "WIP"
git commit -m "asdf"
```

Follow conventional commits (optional but nice):
```
feat: Add JUnit XML output formatter
fix: Correct retry delay calculation in exponential backoff
docs: Add configuration examples to README
test: Add unit tests for BestOfN retry policy
refactor: Extract retry logic into separate module
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- **Clear title** describing the change
- **Description** explaining what and why
- **Link to issue** it addresses
- **Screenshots** if UI changes
- **Checklist** items completed

### PR Checklist

- [ ] Tests added/updated
- [ ] All tests passing (`uv run pytest`)
- [ ] Code formatted (`uv run ruff format`)
- [ ] Linting passes (`uv run ruff check`)
- [ ] Type checking passes (`uv run mypy src/`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] Follows constitutional principles

---

## 📝 Documentation

### Adding Documentation

- **README.md**: Overview, quick start, main features
- **docs/*.md**: Detailed guides and tutorials
- **Docstrings**: All public functions/classes
- **Type hints**: All function signatures
- **Comments**: Complex logic only (code should be self-documenting)

### Documentation Style

```python
def execute_step(
    self,
    step: TestStep,
    timeout: int = 60,
) -> TestResult:
    """Execute a single test step with retry support.
    
    Attempts to execute the step, retrying on failure according to
    the configured retry policy. Logs all attempts.
    
    Args:
        step: The test step to execute.
        timeout: Maximum execution time in seconds.
    
    Returns:
        TestResult with execution outcome, logs, and timing.
        For retries, returns the first successful result or the last failure.
    
    Raises:
        TimeoutError: If step execution exceeds timeout.
    
    Example:
        >>> executor = StepExecutor(retry_policy=FixedRetry(max_retries=3))
        >>> result = await executor.execute_step(step, timeout=30)
        >>> assert result.status == ResultStatus.PASSED
    """
```

---

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Try the latest version
3. Verify it's not a configuration issue

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Create suite with...
2. Run command...
3. See error...

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 14.0]
- Python version: [e.g., 3.11.5]
- Familiar version: [e.g., 0.1.0]
- LLM provider: [e.g., Anthropic Claude]

**Additional context**
- Error messages
- Log output
- Suite configuration
- Screenshots
```

---

## 💡 Feature Requests

### Feature Request Template

```markdown
**Problem**
Describe the problem this feature would solve.

**Proposed Solution**
How you envision this working.

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
- Use cases
- Examples
- Mock-ups
```

---

## 🎯 Good First Issues

Looking for a place to start? Check issues labeled:
- `good first issue` - Simple, well-defined tasks
- `help wanted` - Need community help
- `documentation` - Improve docs

---

## 🤝 Code of Conduct

Be respectful, inclusive, and professional. We're all here to build something great together.

---

## ❓ Questions?

- 💬 [GitHub Discussions](https://github.com/yourusername/familiar/discussions)
- 🐛 [Issue Tracker](https://github.com/yourusername/familiar/issues)
- 📖 [Documentation](docs/)

---

## 🙏 Thank You!

Every contribution, no matter how small, makes Familiar better. Thank you for being part of this project!

