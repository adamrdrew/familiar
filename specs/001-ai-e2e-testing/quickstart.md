# Quickstart Guide: Building Familiar

**Feature**: AI-Driven End-to-End Testing Platform  
**Audience**: Developers implementing Familiar  
**Prerequisite**: Review spec.md, plan.md, research.md, data-model.md, and contracts/

## Overview

This guide walks through building Familiar from scratch, following our constitution and design principles. We'll build incrementally, testing each component as we go.

## Project Setup

### 1. Initialize Python Project with uv

```bash
# Create project directory
cd /path/to/familiar
git init

# Initialize with uv
uv init --python 3.11

# Create .python-version for uv
echo "3.11" > .python-version

# Create source layout
mkdir -p src/familiar/{cli,core,models,formatters,logging,utils}
mkdir -p tests/{unit,integration,contract,fixtures}

# Create __init__.py files
touch src/familiar/__init__.py
touch src/familiar/{cli,core,models,formatters,logging,utils}/__init__.py
touch tests/__init__.py
```

### 2. Configure pyproject.toml

**Location**: `/familiar/pyproject.toml`

```toml
[project]
name = "familiar"
version = "0.1.0"
description = "AI-driven end-to-end testing for web applications"
readme = "README.md"
requires-python = ">=3.11"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
license = {text = "MIT"}

dependencies = [
    "browser-use>=0.9.5",
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.5.0",
    "ruff>=0.0.290",
]

[project.scripts]
familiar = "familiar.cli.main:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "ANN", "B", "A", "C4", "PIE", "T20", "SIM"]
ignore = ["ANN101", "ANN102"]  # Don't require type hints for self/cls
```

### 3. Install Dependencies

```bash
# Install project in development mode
uv sync --dev

# Verify installation
uv run python -c "import click; import pydantic; print('Dependencies OK')"
```

### 4. Environment Variables

**Location**: `/familiar/.env.example`

```bash
# Familiar Configuration
FAMILIAR_TEST_DIR=./familiar
FAMILIAR_LOG_LEVEL=INFO
FAMILIAR_DEFAULT_TIMEOUT=300
FAMILIAR_DEFAULT_STEP_TIMEOUT=30
FAMILIAR_DEFAULT_RETRIES=3
FAMILIAR_HEADLESS=true

# LLM Configuration (choose one)
OPENAI_API_KEY=your-api-key-here
# ANTHROPIC_API_KEY=your-api-key-here
# GOOGLE_API_KEY=your-api-key-here

# Optional: browser-use cloud
# BROWSER_USE_API_KEY=your-api-key-here

# Test Environment (customize per project)
BASE_URL=https://example.com
TEST_USER=test@example.com
TEST_PASSWORD=securepassword123
```

**Create actual .env file** (gitignored):
```bash
cp .env.example .env
# Edit .env with real values
```

## Implementation Order

Follow this order to build features incrementally, testing each before moving forward:

### Phase 1: Data Models (Easy to Change, Single Responsibility)

**Why first**: Models are foundation for everything else. Small, focused dataclasses with clear responsibilities.

#### 1.1 Create Models

**File**: `src/familiar/models/suite.py`

```python
"""Test suite models."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class RetryPolicyConfig(BaseModel):
    """Retry policy configuration."""
    type: str = Field(pattern="^(fixed|exponential|best_of_n)$")
    max_retries: int = Field(default=3, ge=0, le=10)
    delay: float = Field(default=1.0, ge=0)
    n_runs: Optional[int] = Field(default=None, ge=1, le=20)


class SuiteConfig(BaseModel):
    """Suite configuration from suite.yaml."""
    name: str = Field(min_length=1, max_length=200)
    timeout: int = Field(default=300, gt=0, le=3600)
    step_timeout: int = Field(default=30, gt=0, le=600)
    retry_policy: RetryPolicyConfig = Field(default_factory=lambda: RetryPolicyConfig(type="fixed"))
    fuzziness: float = Field(default=0.0, ge=0.0, le=1.0)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    headless: Optional[bool] = None
    screenshot_on_failure: bool = True
    env: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, any] = Field(default_factory=dict)

    @field_validator("step_timeout")
    @classmethod
    def step_timeout_must_not_exceed_suite_timeout(cls, v: int, info) -> int:
        """Validate step_timeout <= timeout."""
        if "timeout" in info.data and v > info.data["timeout"]:
            raise ValueError(f"step_timeout ({v}) cannot exceed timeout ({info.data['timeout']})")
        return v


@dataclass
class TestSuite:
    """A test suite with configuration and steps."""
    name: str
    path: Path
    config: SuiteConfig
    steps: List["TestStep"] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)
```

**File**: `src/familiar/models/step.py`

```python
"""Test step models."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Set
import re


@dataclass
class TestStep:
    """A single test step from markdown file."""
    path: Path
    content: str
    order: int
    timeout: Optional[int] = None
    metadata: Dict[str, any] = field(default_factory=dict)
    
    @property
    def name(self) -> str:
        """Extract step name from first heading."""
        for line in self.content.split("\n"):
            if line.startswith("# "):
                # Remove "Step:" prefix if present
                name = line[2:].strip()
                if name.lower().startswith("step:"):
                    name = name[5:].strip()
                return name
        return self.path.stem
    
    @property
    def variables(self) -> Set[str]:
        """Extract all ${VAR} references from content."""
        pattern = r"\$\{([A-Z_][A-Z0-9_]*)(:-[^}]*)?\}"
        matches = re.findall(pattern, self.content)
        return {var for var, _ in matches}
```

**File**: `src/familiar/models/result.py`

```python
"""Test result models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ActionType(Enum):
    """Browser action types."""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    EVALUATE = "evaluate"


@dataclass
class LogEntry:
    """Single log entry."""
    timestamp: datetime
    level: LogLevel
    message: str
    context: Dict[str, any] = field(default_factory=dict)
    source: str = "familiar"


@dataclass
class BrowserAction:
    """Record of browser action."""
    type: ActionType
    timestamp: datetime
    success: bool
    target: Optional[str] = None
    value: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TestResult:
    """Result of executing a test step."""
    step_name: str
    step_path: Path
    success: bool
    duration: float
    attempt: int
    logs: List[LogEntry] = field(default_factory=list)
    error: Optional[str] = None
    browser_actions: List[BrowserAction] = field(default_factory=list)
    screenshot_path: Optional[Path] = None
    
    @property
    def passed(self) -> bool:
        """Alias for success."""
        return self.success
    
    @property
    def failed(self) -> bool:
        """Inverse of success."""
        return not self.success
    
    @property
    def retry_count(self) -> int:
        """Number of retries (attempt - 1)."""
        return self.attempt - 1


@dataclass
class SuiteResult:
    """Result of executing a test suite."""
    suite_name: str
    suite_path: Path
    step_results: List[TestResult]
    duration: float
    started_at: datetime
    completed_at: datetime
    config_fuzziness: float = 0.0
    
    @property
    def success(self) -> bool:
        """Check if suite passed based on fuzziness."""
        if not self.step_results:
            return False
        pass_rate = self.passed_count / self.total_count
        required_pass_rate = 1.0 - self.config_fuzziness
        return pass_rate >= required_pass_rate
    
    @property
    def total_count(self) -> int:
        """Total number of steps."""
        return len(self.step_results)
    
    @property
    def passed_count(self) -> int:
        """Number of passed steps."""
        return sum(1 for r in self.step_results if r.success)
    
    @property
    def failed_count(self) -> int:
        """Number of failed steps."""
        return sum(1 for r in self.step_results if not r.success)
    
    @property
    def pass_rate(self) -> float:
        """Pass rate as percentage (0.0 - 1.0)."""
        if self.total_count == 0:
            return 0.0
        return self.passed_count / self.total_count
```

#### 1.2 Test Models

**File**: `tests/unit/test_models.py`

```python
"""Test data models."""
from pathlib import Path
from datetime import datetime
import pytest
from pydantic import ValidationError

from familiar.models.suite import SuiteConfig, RetryPolicyConfig, TestSuite
from familiar.models.step import TestStep
from familiar.models.result import TestResult, SuiteResult, LogLevel


def test_suite_config_validates_timeout():
    """Test that step_timeout cannot exceed timeout."""
    with pytest.raises(ValidationError, match="cannot exceed timeout"):
        SuiteConfig(
            name="Test Suite",
            timeout=30,
            step_timeout=60,  # Invalid: exceeds timeout
        )


def test_suite_config_defaults():
    """Test default values are applied."""
    config = SuiteConfig(name="Test Suite")
    assert config.timeout == 300
    assert config.step_timeout == 30
    assert config.fuzziness == 0.0
    assert config.temperature == 0.7


def test_test_step_extracts_name_from_heading():
    """Test step name extraction from markdown."""
    step = TestStep(
        path=Path("00-login.md"),
        content="# Step: Login to Dashboard\n\nNavigate to login page",
        order=0,
    )
    assert step.name == "Login to Dashboard"


def test_test_step_extracts_variables():
    """Test variable extraction from content."""
    step = TestStep(
        path=Path("00-test.md"),
        content="Navigate to ${BASE_URL}/login\nUser: ${TEST_USER}\nDefault: ${VAR:-default}",
        order=0,
    )
    assert step.variables == {"BASE_URL", "TEST_USER", "VAR"}


def test_suite_result_success_with_fuzziness():
    """Test suite success calculation with fuzziness."""
    result1 = TestResult(
        step_name="Step 1",
        step_path=Path("00-step.md"),
        success=True,
        duration=1.0,
        attempt=1,
    )
    result2 = TestResult(
        step_name="Step 2",
        step_path=Path("01-step.md"),
        success=False,
        duration=1.0,
        attempt=1,
    )
    
    # 50% pass rate, 10% fuzziness (90% required) = FAIL
    suite_result = SuiteResult(
        suite_name="Test",
        suite_path=Path("test"),
        step_results=[result1, result2],
        duration=2.0,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        config_fuzziness=0.1,
    )
    assert not suite_result.success
    
    # 50% pass rate, 50% fuzziness (50% required) = PASS
    suite_result.config_fuzziness = 0.5
    assert suite_result.success


# Run tests
# uv run pytest tests/unit/test_models.py -v
```

**Run tests**:
```bash
uv run pytest tests/unit/test_models.py -v
```

✅ **Checkpoint**: Models tested and working. Proceed to parsing.

---

### Phase 2: Parsing (Single Responsibility, Clear Interfaces)

**Why next**: Need to load suite configs and step files before execution.

#### 2.1 Create Parser

**File**: `src/familiar/core/parser.py`

```python
"""Parse suite configurations and test steps."""
from pathlib import Path
from typing import List, Optional
import yaml

from familiar.models.suite import SuiteConfig, TestSuite
from familiar.models.step import TestStep


class SuiteParser:
    """Parse test suite from directory."""
    
    def parse_suite(self, suite_path: Path) -> TestSuite:
        """Parse suite from directory containing suite.yaml."""
        if not suite_path.is_dir():
            raise ValueError(f"Suite path is not a directory: {suite_path}")
        
        config_file = suite_path / "suite.yaml"
        if not config_file.exists():
            raise FileNotFoundError(f"suite.yaml not found in {suite_path}")
        
        # Parse configuration
        config = self._parse_config(config_file)
        
        # Find and parse step files
        steps = self._parse_steps(suite_path)
        
        return TestSuite(
            name=config.name,
            path=suite_path,
            config=config,
            steps=steps,
        )
    
    def _parse_config(self, config_file: Path) -> SuiteConfig:
        """Parse suite.yaml configuration file."""
        with open(config_file) as f:
            data = yaml.safe_load(f)
        return SuiteConfig(**data)
    
    def _parse_steps(self, suite_path: Path) -> List[TestStep]:
        """Find and parse all step files in suite directory."""
        step_files = sorted(suite_path.glob("[0-9][0-9]-*.md"))
        
        if not step_files:
            raise ValueError(f"No step files found in {suite_path}")
        
        steps = []
        for step_file in step_files:
            step = self._parse_step(step_file)
            steps.append(step)
        
        return steps
    
    def _parse_step(self, step_file: Path) -> TestStep:
        """Parse single step file."""
        content = step_file.read_text()
        
        # Extract order from filename (first two digits)
        order = int(step_file.stem[:2])
        
        # TODO: Parse frontmatter if present
        
        return TestStep(
            path=step_file,
            content=content,
            order=order,
        )
```

#### 2.2 Test Parser

**File**: `tests/unit/test_parser.py`

```python
"""Test suite parser."""
import pytest
from pathlib import Path
from familiar.core.parser import SuiteParser


@pytest.fixture
def sample_suite(tmp_path):
    """Create sample suite for testing."""
    suite_dir = tmp_path / "test-suite"
    suite_dir.mkdir()
    
    # Create suite.yaml
    (suite_dir / "suite.yaml").write_text("""
name: "Test Suite"
timeout: 120
step_timeout: 30
""")
    
    # Create step files
    (suite_dir / "00-first.md").write_text("# Step: First\n\nDo something")
    (suite_dir / "01-second.md").write_text("# Step: Second\n\nDo more")
    
    return suite_dir


def test_parse_suite(sample_suite):
    """Test parsing a complete suite."""
    parser = SuiteParser()
    suite = parser.parse_suite(sample_suite)
    
    assert suite.name == "Test Suite"
    assert suite.config.timeout == 120
    assert len(suite.steps) == 2
    assert suite.steps[0].order == 0
    assert suite.steps[1].order == 1


def test_parse_suite_missing_yaml(tmp_path):
    """Test error when suite.yaml missing."""
    suite_dir = tmp_path / "invalid-suite"
    suite_dir.mkdir()
    
    parser = SuiteParser()
    with pytest.raises(FileNotFoundError, match="suite.yaml not found"):
        parser.parse_suite(suite_dir)
```

**Run tests**:
```bash
uv run pytest tests/unit/test_parser.py -v
```

✅ **Checkpoint**: Parser working. Proceed to discovery.

---

### Phase 3: Discovery (Small, Single Purpose)

**File**: `src/familiar/core/discovery.py`

```python
"""Discover test suites in directory."""
from pathlib import Path
from typing import List

from familiar.core.parser import SuiteParser
from familiar.models.suite import TestSuite


class TestSuiteDiscovery:
    """Discover test suites in a directory tree."""
    
    def __init__(self, parser: Optional[SuiteParser] = None):
        """Initialize with optional parser (dependency injection)."""
        self.parser = parser or SuiteParser()
    
    def discover_suites(self, root_dir: Path) -> List[TestSuite]:
        """Discover all test suites under root directory."""
        if not root_dir.is_dir():
            raise ValueError(f"Root directory does not exist: {root_dir}")
        
        suites = []
        
        # Find all suite.yaml files
        for yaml_file in root_dir.rglob("suite.yaml"):
            # Skip shared directory
            if "shared" in yaml_file.parts:
                continue
            
            suite_dir = yaml_file.parent
            try:
                suite = self.parser.parse_suite(suite_dir)
                suites.append(suite)
            except Exception as e:
                # Log error but continue discovering
                print(f"Warning: Failed to parse suite {suite_dir}: {e}")
        
        return sorted(suites, key=lambda s: s.path)
```

**Test**:
```python
# tests/unit/test_discovery.py
def test_discover_suites(tmp_path):
    """Test suite discovery."""
    # Create two suites
    suite1 = tmp_path / "suite1"
    suite1.mkdir()
    (suite1 / "suite.yaml").write_text('name: "Suite 1"')
    (suite1 / "00-test.md").write_text("# Test")
    
    suite2 = tmp_path / "suite2"
    suite2.mkdir()
    (suite2 / "suite.yaml").write_text('name: "Suite 2"')
    (suite2 / "00-test.md").write_text("# Test")
    
    discovery = TestSuiteDiscovery()
    suites = discovery.discover_suites(tmp_path)
    
    assert len(suites) == 2
    assert [s.name for s in suites] == ["Suite 1", "Suite 2"]
```

✅ **Checkpoint**: Discovery working.

---

### Phase 4: CLI Foundation (Stable Public Interface)

#### 4.1 Create CLI Entry Point

**File**: `src/familiar/cli/main.py`

```python
"""Main CLI entry point."""
import click
from pathlib import Path


@click.group()
@click.version_option()
def cli():
    """Familiar: AI-driven end-to-end testing tool."""
    pass


@cli.command()
@click.argument("suite_path_or_name", required=False)
@click.option("--all", "-a", is_flag=True, help="Run all discovered suites")
@click.option("--format", "-f", type=click.Choice(["text", "json", "junit"]), default="text")
@click.option("--headless/--headed", default=True, help="Browser display mode")
def run(suite_path_or_name, all, format, headless):
    """Run test suites."""
    click.echo(f"Running tests (format={format}, headless={headless})")
    
    # TODO: Implement execution
    click.echo("Implementation in progress...")


@cli.command()
@click.argument("directory", required=False, type=click.Path(exists=True, path_type=Path))
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
def discover(directory, format):
    """Discover test suites."""
    from familiar.core.discovery import TestSuiteDiscovery
    
    root_dir = directory or Path("./familiar")
    discovery = TestSuiteDiscovery()
    suites = discovery.discover_suites(root_dir)
    
    if format == "text":
        click.echo(f"\nDiscovered {len(suites)} suites in: {root_dir}\n")
        for i, suite in enumerate(suites, 1):
            click.echo(f"{i}. {suite.name}")
            click.echo(f"   Path: {suite.path}")
            click.echo(f"   Steps: {len(suite.steps)}")
            click.echo()
    else:
        import json
        data = [{"name": s.name, "path": str(s.path), "steps": len(s.steps)} for s in suites]
        click.echo(json.dumps(data, indent=2))


if __name__ == "__main__":
    cli()
```

**File**: `src/familiar/__main__.py`

```python
"""Allow running as: python -m familiar"""
from familiar.cli.main import cli

if __name__ == "__main__":
    cli()
```

**Test CLI**:
```bash
# Install in editable mode
uv pip install -e .

# Test commands
familiar --version
familiar --help
familiar discover --help

# Create test suite to discover
mkdir -p familiar/test-suite
echo 'name: "Test"' > familiar/test-suite/suite.yaml
echo '# Test' > familiar/test-suite/00-test.md

# Test discovery
familiar discover
```

✅ **Checkpoint**: CLI foundation working. Can discover suites.

---

## Next Steps

With this foundation in place:

1. ✅ Models defined and tested
2. ✅ Parser working
3. ✅ Discovery working
4. ✅ CLI framework ready

**Continue with**:
- Phase 5: Executor (integrate browser-use)
- Phase 6: Runner (orchestrate execution with retries)
- Phase 7: Formatters (output results)
- Phase 8: Integration tests

See `/speckit.tasks` to generate detailed task breakdown for implementation.

## Development Workflow

### Run Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=familiar --cov-report=html

# Specific test file
uv run pytest tests/unit/test_models.py -v

# Watch mode (requires pytest-watch)
uv run ptw
```

### Linting and Type Checking

```bash
# Lint with ruff
uv run ruff check src/

# Format code
uv run ruff format src/

# Type check
uv run mypy src/
```

### Run Familiar CLI

```bash
# Direct invocation
uv run familiar --help

# As module
uv run python -m familiar --help
```

## Constitution Adherence Checklist

Before each commit, verify:

- ✅ **Easy to Change**: Dependencies injected, clear interfaces
- ✅ **Small Classes**: Each class has one responsibility
- ✅ **Stable APIs**: Public interfaces documented and consistent
- ✅ **Polymorphism**: Strategies for formatters, retry policies
- ✅ **Behavior Tests**: Tests validate outcomes, not implementation
- ✅ **Readable**: Clear names, native Python idioms
- ✅ **Humane**: Explicit behavior, minimal abstraction
- ✅ **TDD**: Write tests before implementation

## Troubleshooting

### Import Errors

If you get import errors, ensure you're using the installed package:
```bash
uv pip install -e .
```

### Browser-use Not Found

Install Chromium for browser-use:
```bash
uv run python -m playwright install chromium
```

### Type Errors

Strict mypy can be noisy. Adjust `pyproject.toml`:
```toml
[tool.mypy]
strict = false  # Temporarily while building
```

---

**Status**: ✅ Quickstart Complete

This guide provides a working foundation. Continue with `/speckit.tasks` for detailed implementation tasks.

