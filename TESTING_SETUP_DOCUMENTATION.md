# Testing Setup Documentation

## Overview

This document explains the testing configuration for the Advanced Multi-Agent Intelligence System (AMAS) and how to properly configure Python import paths for test execution.

## Import Path Configuration Issue & Resolution

### Problem

The test suite was failing because of incorrect import path configuration in `tests/conftest.py`. Specifically:

1. **Root Cause**: The import statement at line 125 of `conftest.py` was using an absolute import:
   ```python
   from tests.fixtures.production_fixtures import (...)
   ```

2. **Why It Failed**: When pytest discovers and runs tests, the root working directory is the project root, not the `tests/` directory. This creates a Python path mismatch where:
   - The `sys.path` doesn't correctly resolve `tests.fixtures` module
   - Python can't find the module because it's looking in the wrong location
   - Pytest's path setup differs from standard Python import behavior

### Solution

Use **relative imports** with pytest's proper path handling.

#### Recommended Fix: Relative Imports

Change line 125-131 in `tests/conftest.py` from:
```python
from tests.fixtures.production_fixtures import (
    alembic_env_path,
    ...
)
```

To:
```python
from .fixtures.production_fixtures import (
    alembic_env_path,
    ...
)
```

**Why This Works**:
- Relative imports work correctly with pytest's module discovery
- They don't depend on sys.path manipulation
- They resolve from the current package (`tests`) to the subpackage (`fixtures`)
- This is the standard Python approach for intra-package imports

## Project Structure for Testing

```
project_root/
├── src/
│   ├── amas/
│   │   ├── api/
│   │   ├── config/
│   │   ├── services/
│   │   └── ...
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 ← Main pytest configuration
│   ├── fixtures/
│   │   ├── __init__.py
│   │   └── production_fixtures.py  ← Fixture definitions
│   ├── unit/
│   ├── integration/
│   ├── functional/
│   └── test_*.py files
├── requirements.txt
├── pytest.ini                       ← Pytest configuration
└── ...
```

## Pytest Configuration

### pytest.ini

Create a `pytest.ini` file to configure pytest paths:

```ini
[pytest]
# Python path configuration
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Add tests directory to Python path
pythonpath = .

# Test discovery
testpaths = tests

# Output options
addopts = -v --tb=short --strict-markers

# Markers
markers =
    unit: Unit tests
    integration: Integration tests
    functional: Functional tests
    slow: Slow running tests
```

## Running Tests

### From Project Root

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestAPIEndpoints

# Run specific test function
pytest tests/test_api.py::TestAPIEndpoints::test_health_check

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run only unit tests
pytest -m unit

# Run excluding slow tests
pytest -m "not slow"
```

## GitHub Actions CI/CD Configuration

The `.github/workflows/deploy.yml` file includes proper test execution:

```yaml
- name: Run tests
  env:
    DATABASE_URL: postgresql://amas:test_password@localhost:5432/amas_test
    REDIS_URL: redis://localhost:6379/0
    SECRET_KEY: test-secret-key
    ENVIRONMENT: test
  run: |
    pytest tests/ -v --cov=src --cov-report=xml --cov-report=html
```

**Key Points**:
- Tests run from project root with `pytest tests/`
- Environment variables are set for test isolation
- Coverage reports are generated for CI/CD pipelines
- Test database uses PostgreSQL for parity with production

## Environment Setup for Testing

### Required Environment Variables

The test suite requires these environment variables (set in `conftest.py`):

```python
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///test.db"  # or postgres for CI
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key"
```

### Local Development Setup

1. **Install test dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   # OR manually:
   pip install pytest pytest-asyncio pytest-cov
   ```

2. **Start services** (PostgreSQL, Redis, Neo4j):
   ```bash
   # Using Docker
   docker-compose -f docker-compose.test.yml up -d
   ```

3. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

## Common Import Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'src'"

**Cause**: The `src/` directory is not in Python path

**Solution**:
```python
# In conftest.py, after os/sys imports
import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))
```

### Issue 2: "ImportError: cannot import name 'X' from 'tests.fixtures'"

**Cause**: Wrong import path or missing fixtures file

**Solution**:
- Use relative imports: `from .fixtures.production_fixtures import X`
- Verify the fixture is exported in `tests/fixtures/__init__.py`
- Check the fixture file exists at `tests/fixtures/production_fixtures.py`

### Issue 3: "conftest.py not found" during test discovery

**Cause**: Pytest not configured to find conftest.py

**Solution**:
- Ensure `tests/` directory has `__init__.py`
- Run pytest from project root: `pytest tests/`
- Add `testpaths = tests` to `pytest.ini`

## Best Practices

1. **Use Relative Imports in Tests**
   - Write tests in `tests/` directory
   - Use relative imports for fixtures: `from .fixtures.module import X`
   - Use absolute imports for `src/` modules: `from src.amas.api import X`

2. **Organize Fixtures Logically**
   - Group related fixtures in separate modules
   - Use `pytest` fixture scopes properly: `scope="function"`, `"class"`, `"module"`, `"session"`
   - Document fixture purposes and dependencies

3. **Environment Isolation**
   - Use test-specific databases and services
   - Clean up resources with fixture teardown
   - Don't modify global state in tests

4. **CI/CD Integration**
   - Run tests from project root
   - Set all required environment variables
   - Generate coverage reports
   - Use same Python path setup as development

## Testing Workflow

```
Developer writes code
        ↓
Run local tests: pytest tests/ -v
        ↓
Push to GitHub
        ↓
GitHub Actions runs tests with CI/CD workflow
        ↓
Tests pass → Code merged
Tests fail → Developer fixes → Repeat
```

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Import System](https://docs.python.org/3/reference/import_system.html)
- [GitHub Actions Python Testing](https://github.com/actions/setup-python)

## Troubleshooting

For additional troubleshooting:

1. Check Python path: `python -c "import sys; print('\\n'.join(sys.path))"`
2. Verify imports manually: `python -c "from tests.fixtures.production_fixtures import X"`
3. Run pytest in verbose mode: `pytest tests/ -vv --tb=long`
4. Check test discovery: `pytest tests/ --collect-only`
