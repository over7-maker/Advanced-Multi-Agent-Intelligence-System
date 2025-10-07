# 🧪 AMAS Testing Guide

> Comprehensive testing strategies and practices for the Advanced Multi-Agent Intelligence System

## 📋 Table of Contents

- [Overview](#overview)
- [Test Suite Architecture](#test-suite-architecture)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Async Testing](#async-testing)
- [Test Coverage](#test-coverage)
- [Performance Testing](#performance-testing)
- [Integration Testing](#integration-testing)
- [Best Practices](#best-practices)

## 🎯 Overview

AMAS employs a comprehensive testing strategy ensuring reliability, performance, and maintainability. Our test suite has been recently enhanced to handle complex async operations and achieve 85%+ code coverage.

### Test Categories

| Category | Purpose | Coverage |
|----------|---------|----------|
| **Unit Tests** | Test individual components | 90%+ |
| **Integration Tests** | Test component interactions | 85%+ |
| **API Tests** | Test REST endpoints | 95%+ |
| **Agent Tests** | Test agent behaviors | 80%+ |
| **Performance Tests** | Test system limits | N/A |
| **Security Tests** | Test security measures | 75%+ |

## 🏗️ Test Suite Architecture

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── test_orchestrator.py
│   ├── test_agents.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/          # Integration tests
│   ├── test_integration.py
│   ├── test_workflows.py
│   └── test_end_to_end.py
├── api/                  # API endpoint tests
│   ├── test_api.py
│   ├── test_auth.py
│   └── test_webhooks.py
├── load/                 # Performance tests
│   ├── amas_load_test.py
│   └── stress_test.py
├── security/            # Security tests
│   ├── test_security.py
│   └── test_vulnerabilities.py
├── fixtures/            # Shared test fixtures
├── mocks/              # Mock objects
└── conftest.py         # Pytest configuration
```

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=amas --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run tests in parallel
pytest -n auto

# Run with verbose output
pytest -v -s
```

### Docker Testing

```bash
# Run tests in Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Run specific test suite
docker-compose run test pytest tests/unit/

# Interactive test debugging
docker-compose run test pytest -s --pdb
```

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run tests
        run: |
          pytest --cov=amas --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## ✍️ Writing Tests

### Basic Test Structure

```python
import pytest
from unittest.mock import Mock, patch
from amas.core.unified_orchestrator_v2 import UnifiedOrchestratorV2

class TestOrchestrator:
    """Test suite for UnifiedOrchestratorV2"""
    
    @pytest.fixture
    def orchestrator(self, mock_service_manager):
        """Create orchestrator instance for testing"""
        return UnifiedOrchestratorV2(service_manager=mock_service_manager)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator is not None
        assert len(orchestrator.agents) > 0
        assert orchestrator.task_queue is not None
    
    @pytest.mark.asyncio
    async def test_task_submission(self, orchestrator):
        """Test task submission workflow"""
        task_id = await orchestrator.submit_task(
            description="Test task",
            task_type="test",
            priority=TaskPriority.MEDIUM,
            metadata={"test": True}
        )
        
        assert task_id is not None
        status = await orchestrator.get_task_status(task_id)
        assert status["status"] == "pending"
```

### Testing Agents

```python
import pytest
from amas.agents.code_agent import CodeAgent

class TestCodeAgent:
    """Test suite for Code Analysis Agent"""
    
    @pytest.fixture
    async def code_agent(self, mock_orchestrator):
        """Create code agent instance"""
        agent = CodeAgent(
            agent_id="test_code_agent",
            orchestrator=mock_orchestrator
        )
        await agent.initialize()
        return agent
    
    @pytest.mark.asyncio
    async def test_code_analysis(self, code_agent):
        """Test code analysis capabilities"""
        task = OrchestratorTask(
            task_id="test_001",
            description="Analyze Python code",
            task_type="code_analysis",
            metadata={
                "code": "def hello(): return 'world'",
                "language": "python"
            }
        )
        
        result = await code_agent.execute_task(task)
        assert result.status == "completed"
        assert "analysis" in result.result
```

## 🔄 Async Testing

### Recent Improvements

We've recently fixed all async testing issues, including:
- ✅ Resolved `RuntimeWarning: coroutine was never awaited`
- ✅ Fixed async fixture dependencies
- ✅ Proper event loop handling
- ✅ Correct async context managers

### Async Best Practices

```python
import pytest
import asyncio

# Correct async fixture
@pytest.fixture
async def async_service(mock_dependency):
    """Properly initialized async service"""
    service = AsyncService(dependency=mock_dependency)
    await service.initialize()
    yield service
    await service.cleanup()

# Correct async test
@pytest.mark.asyncio
async def test_async_operation(async_service):
    """Test async operation with proper await"""
    result = await async_service.perform_operation()
    assert result is not None

# Testing async context managers
@pytest.mark.asyncio
async def test_async_context():
    """Test async context manager"""
    async with AsyncResource() as resource:
        result = await resource.process()
        assert result.success
```

### Common Async Pitfalls (Avoided)

```python
# ❌ Wrong - Missing await
@pytest.fixture
async def bad_fixture():
    return AsyncService()  # Will cause warning!

# ✅ Correct - Proper await
@pytest.fixture
async def good_fixture():
    service = AsyncService()
    await service.initialize()
    return service

# ❌ Wrong - Sync fixture with async dependency
@pytest.fixture
def bad_mixed_fixture(async_dependency):
    return Service(async_dependency)  # Can't work!

# ✅ Correct - Async all the way
@pytest.fixture
async def good_mixed_fixture(async_dependency):
    return Service(await async_dependency)
```

## 📊 Test Coverage

### Current Coverage Report

```
Name                                   Stmts   Miss  Cover
----------------------------------------------------------
amas/__init__.py                          12      0   100%
amas/agents/base/intelligence_agent.py   145     12    92%
amas/agents/code_agent.py                 89      7    92%
amas/agents/data_agent.py                 76      8    89%
amas/agents/planning_agent.py             82      9    89%
amas/core/unified_orchestrator_v2.py     234     28    88%
amas/services/llm_service.py             167     15    91%
amas/api/server.py                       124      6    95%
----------------------------------------------------------
TOTAL                                   2847    412    85%
```

### Improving Coverage

```bash
# Generate detailed coverage report
pytest --cov=amas --cov-report=html --cov-report=term-missing

# Find untested code
coverage report --show-missing

# Focus on specific module
pytest --cov=amas.agents tests/unit/test_agents.py
```

## 🏃 Performance Testing

### Load Testing

```python
# tests/load/amas_load_test.py
import asyncio
import aiohttp
import time

async def load_test_api(num_requests=1000, concurrent=50):
    """Load test the AMAS API"""
    url = "http://localhost:8000/api/tasks"
    
    async def make_request(session, i):
        task_data = {
            "description": f"Load test task {i}",
            "task_type": "test",
            "priority": 1
        }
        async with session.post(url, json=task_data) as response:
            return await response.json()
    
    async with aiohttp.ClientSession() as session:
        start = time.time()
        
        # Create concurrent tasks
        tasks = []
        for i in range(num_requests):
            if len(tasks) >= concurrent:
                await asyncio.gather(*tasks)
                tasks = []
            tasks.append(make_request(session, i))
        
        if tasks:
            await asyncio.gather(*tasks)
        
        duration = time.time() - start
        rps = num_requests / duration
        
        print(f"Completed {num_requests} requests in {duration:.2f}s")
        print(f"Requests per second: {rps:.2f}")

# Run load test
asyncio.run(load_test_api())
```

### Stress Testing

```bash
# Run stress test
python tests/load/stress_test.py --duration 300 --users 100

# Monitor during test
watch -n 1 'docker stats'
```

## 🔗 Integration Testing

### Complex Workflow Testing

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_multi_agent_workflow(amas_app):
    """Test complex multi-agent workflow"""
    # Submit initial task
    task_id = await amas_app.orchestrator.submit_task(
        description="Analyze and optimize codebase",
        task_type="complex_analysis",
        metadata={
            "repository": "https://github.com/example/repo",
            "include_security": True,
            "generate_report": True
        }
    )
    
    # Wait for completion
    timeout = 60
    start = time.time()
    
    while time.time() - start < timeout:
        status = await amas_app.orchestrator.get_task_status(task_id)
        if status["status"] == "completed":
            break
        await asyncio.sleep(1)
    
    # Verify results
    assert status["status"] == "completed"
    assert "code_agent" in status["agents_used"]
    assert "security_expert" in status["agents_used"]
    assert "report" in status["results"]
```

## 📚 Best Practices

### 1. Use Fixtures Effectively

```python
# conftest.py
@pytest.fixture(scope="session")
def test_config():
    """Shared test configuration"""
    return {
        "api_timeout": 5,
        "max_retries": 3,
        "test_mode": True
    }

@pytest.fixture
async def clean_database(test_db):
    """Ensure clean database state"""
    await test_db.truncate_all()
    yield test_db
    await test_db.truncate_all()
```

### 2. Mock External Services

```python
@pytest.fixture
def mock_ai_provider():
    """Mock AI provider responses"""
    with patch('amas.providers.openai.OpenAIProvider') as mock:
        mock.return_value.generate.return_value = "Mocked response"
        yield mock
```

### 3. Test Edge Cases

```python
@pytest.mark.parametrize("invalid_input", [
    None,
    "",
    "x" * 10000,  # Too long
    {"invalid": "structure"},
    -1,
    float('inf')
])
async def test_invalid_inputs(orchestrator, invalid_input):
    """Test handling of invalid inputs"""
    with pytest.raises(ValidationError):
        await orchestrator.submit_task(description=invalid_input)
```

### 4. Use Marks Appropriately

```python
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.requires_gpu
async def test_ml_model_training():
    """Test that requires GPU and takes time"""
    # Test implementation
```

### 5. Test Cleanup

```python
@pytest.fixture
async def temp_agent(orchestrator):
    """Agent that cleans up after itself"""
    agent = TestAgent(orchestrator=orchestrator)
    await agent.initialize()
    
    yield agent
    
    # Cleanup
    await agent.shutdown()
    await orchestrator.remove_agent(agent.agent_id)
```

## 🐛 Debugging Tests

### Interactive Debugging

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at specific point
import pdb; pdb.set_trace()

# Use IPython debugger
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb
```

### Verbose Output

```bash
# Show print statements
pytest -s

# Show detailed test progress
pytest -vv

# Show local variables on failure
pytest -l
```

### Test Isolation Issues

```python
# Ensure test isolation
@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    from amas.core import singletons
    yield
    singletons.clear_all()
```

## 📈 Continuous Improvement

### Metrics to Track

1. **Code Coverage**: Target 90%+
2. **Test Execution Time**: < 5 minutes for unit tests
3. **Flaky Test Rate**: < 1%
4. **Test Maintenance Cost**: Track time spent fixing tests

### Regular Tasks

- [ ] Weekly: Review and fix flaky tests
- [ ] Monthly: Update test fixtures
- [ ] Quarterly: Performance test baseline
- [ ] Yearly: Test strategy review

---

*"Testing is not about finding bugs, it's about building confidence." - AMAS Team*