# Testing Setup & Configuration

## Overview

This document explains the testing infrastructure configuration for AMAS, particularly focusing on Python path setup and import resolution.

## Project Structure

The AMAS project uses the `src/` layout pattern:

```
Advanced-Multi-Agent-Intelligence-System/
├── src/
│   └── amas/
│       ├── __init__.py
│       ├── config/
│       ├── core/
│       ├── services/
│       └── ...
├── tests/
│   ├── conftest.py (test-level configuration)
│   ├── unit/
│   ├── integration/
│   ├── performance/
│   └── ...
├── conftest.py (root-level configuration)
├── pytest.ini
├── pyproject.toml
└── ...
```

## Configuration Files

### 1. Root-level `conftest.py`

The root `conftest.py` file handles:

- **Python Path Setup**: Adds `src/` to `sys.path` so modules can be imported as `from amas...`
- **Environment Variables**: Configures testing environment defaults
- **Test Fixtures**: Provides shared fixtures for all tests
- **Warning Filters**: Suppresses expected warnings during testing

```python
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
src_path = PROJECT_ROOT / "src"

# Critical: Add src to path BEFORE imports
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
```

### 2. `pytest.ini` Configuration

Key settings:

```ini
# Configure Python path for src layout
pythonpath = src

# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# AsyncIO support
asyncio_mode = auto
```

**Why `pythonpath = src`?**
- Tells pytest to add the `src/` directory to the Python path
- Allows all tests to use `from amas...` imports directly
- Works in conjunction with `conftest.py` for redundancy

## Import Styles

Both import styles work correctly:

```python
# Preferred: Direct from module name
from amas.config.settings import AMASConfig
from amas.services.circuit_breaker_service import CircuitBreaker

# Supported but not recommended
from src.amas.config.settings import AMASConfig
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/performance/test_resilience_patterns.py
```

### Run with markers
```bash
pytest -m "not slow"  # Skip slow tests
pytest -m "performance"  # Run only performance tests
pytest -m "integration"  # Run only integration tests
```

### Run with verbose output
```bash
pytest -v
pytest -vv  # Extra verbose
```

### Run with coverage
```bash
pytest --cov=src/amas --cov-report=html
```

## Common Issues & Solutions

### ImportError: No module named 'amas'

**Cause**: Python path not configured correctly

**Solutions**:
1. Ensure `conftest.py` exists in project root
2. Verify `pytest.ini` has `pythonpath = src`
3. Run pytest from project root, not from `tests/` directory

### ModuleNotFoundError in test imports

**Cause**: Using incorrect import path

**Solution**:
```python
# ✅ Correct
from amas.services.circuit_breaker_service import CircuitBreaker

# ❌ Incorrect
from src.amas.services.circuit_breaker_service import CircuitBreaker
```

### asyncio warnings during tests

**Cause**: Missing AsyncIO configuration

**Solution**: `pytest.ini` includes `asyncio_mode = auto` to handle async fixtures properly

## Test Markers

Available markers defined in `pytest.ini`:

| Marker | Purpose |
|--------|----------|
| `slow` | Slow-running tests |
| `integration` | Integration tests requiring external services |
| `unit` | Unit tests |
| `api` | API endpoint tests |
| `agents` | Agent behavior tests |
| `services` | Service layer tests |
| `security` | Security and authentication tests |
| `performance` | Performance and load tests |
| `e2e` | End-to-end tests |
| `load` | Load testing |
| `functional` | Functional tests |

## Environment Variables for Testing

Automatic configuration via `conftest.py`:

```python
os.environ["AMAS_ENVIRONMENT"] = "testing"
os.environ["AMAS_DEBUG"] = "false"
os.environ["AMAS_LOG_LEVEL"] = "ERROR"
os.environ["AMAS_OFFLINE_MODE"] = "true"
os.environ["TESTING"] = "true"
```

Override as needed:
```bash
AMAS_LOG_LEVEL=DEBUG pytest -v
```

## Test Fixtures

Provided by root `conftest.py`:

### `mock_config`

Provides a testing-configured AMASConfig instance:

```python
def test_something(mock_config):
    assert mock_config.environment == "testing"
    assert mock_config.debug is False
    assert mock_config.offline_mode is True
```

### `test_data_dir`

Provides path to test data directory (auto-created):

```python
def test_with_data(test_data_dir):
    test_file = test_data_dir / "sample.json"
    # ... use test data
```

## Continuous Integration

GitHub Actions workflow automatically:

1. Sets `AMAS_ENVIRONMENT=testing`
2. Runs `pytest` with proper configuration
3. Reports coverage and test results
4. Caches dependencies for faster runs

## Best Practices

1. **Always import from `amas`, not `src.amas`**
   ```python
   from amas.services import MyService  # ✅
   from src.amas.services import MyService  # ❌
   ```

2. **Use markers for test categorization**
   ```python
   @pytest.mark.performance
   async def test_throughput():
       ...
   ```

3. **Avoid side effects in tests**
   - Use `conftest.py` fixtures instead
   - Reset state between tests
   - Mock external services

4. **Keep tests isolated**
   ```python
   # Use unique identifiers for test data
   test_id = uuid.uuid4()
   user_key = f"test_user_{test_id}"
   ```

5. **Document complex test logic**
   ```python
   @pytest.mark.asyncio
   async def test_circuit_breaker_recovery():
       """Test that circuit breaker recovers through half-open state
       
       This test verifies the state machine: CLOSED -> OPEN -> HALF_OPEN -> CLOSED
       """
       # ...
   ```

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Python Packaging Guide - src Layout](https://packaging.python.org/guides/packaging-your-project/#packaging-your-project)
