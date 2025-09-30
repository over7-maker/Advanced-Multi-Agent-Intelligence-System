# AMAS Testing Documentation

## Overview

This document describes the testing framework for the Advanced Multi-Agent Intelligence System (AMAS). The test suite is designed to ensure system reliability, functionality, and performance across all components.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Test configuration and fixtures
├── test_core.py               # Core system tests
├── test_agents.py             # Agent implementation tests
├── test_services.py           # Service layer tests
├── test_api.py               # API endpoint tests
└── test_integration.py       # Integration tests
```

## Test Categories

### 1. Unit Tests (`test_core.py`, `test_agents.py`, `test_services.py`)

**Purpose**: Test individual components in isolation

**Coverage**:
- AMAS application initialization
- Service manager functionality
- Individual agent implementations
- Database service operations
- Security service operations

**Key Test Cases**:
- Application initialization and shutdown
- Service health checks
- Agent task execution
- Database operations
- JWT token handling
- Password hashing/verification

### 2. API Tests (`test_api.py`)

**Purpose**: Test REST API endpoints

**Coverage**:
- Health check endpoint
- System status endpoint
- Task submission and retrieval
- Agent listing and status
- Workflow execution
- Audit log retrieval
- Authentication and authorization

**Key Test Cases**:
- Endpoint availability and response codes
- Request/response data validation
- Authentication requirements
- Error handling
- Invalid input handling

### 3. Integration Tests (`test_integration.py`)

**Purpose**: Test component interactions and end-to-end workflows

**Coverage**:
- Complete task processing workflows
- Multi-agent coordination
- Service dependencies
- Concurrent operations
- Error handling across components
- Audit trail functionality

**Key Test Cases**:
- End-to-end task processing
- Multi-agent task coordination
- System health monitoring
- Concurrent task processing
- Service integration
- Workflow execution

## Test Configuration

### Fixtures (`conftest.py`)

**Application Fixtures**:
- `amas_app`: Initialized AMAS application
- `test_client`: HTTP client for API testing
- `test_config`: Test configuration
- `sample_task`: Sample task for testing
- `sample_workflow`: Sample workflow for testing

**Service Fixtures**:
- `database_config`: Database configuration
- `security_config`: Security configuration
- `database_service`: Database service instance
- `security_service`: Security service instance

### Test Markers

- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.api`: API tests
- `@pytest.mark.agents`: Agent tests
- `@pytest.mark.services`: Service tests

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Ensure required services are running:
- PostgreSQL (for database tests)
- Redis (for caching tests)
- Ollama (for LLM tests)
- Neo4j (for knowledge graph tests)

### Basic Test Execution

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_core.py
python -m pytest tests/test_agents.py
python -m pytest tests/test_services.py
python -m pytest tests/test_api.py
python -m pytest tests/test_integration.py

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src/amas

# Run specific test markers
python -m pytest tests/ -m "not slow"
python -m pytest tests/ -m "integration"
```

### Using the Test Runner

```bash
# Run the automated test suite
python run_tests.py
```

### Test Environment Setup

For API tests, start the AMAS application:

```bash
# Terminal 1: Start the application
cd /workspace
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Run API tests
python -m pytest tests/test_api.py -v
```

## Test Data and Mocking

### Mock Services

Tests use mock implementations for external services:
- LLM service: Mock responses for text generation
- Vector service: Mock vector operations
- Knowledge graph: Mock graph operations
- Database: In-memory or test database

### Test Data

- **Sample Tasks**: Predefined task structures for testing
- **Sample Workflows**: Predefined workflow configurations
- **Mock Responses**: Expected service responses
- **Test Users**: Mock user accounts for authentication tests

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: AMAS Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: python run_tests.py
```

## Performance Testing

### Load Testing

```bash
# Run performance tests
python -m pytest tests/test_performance.py -v
```

### Benchmark Tests

- Task processing throughput
- Concurrent agent performance
- Memory usage monitoring
- Response time measurements

## Test Coverage

### Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **API Tests**: 95%+ coverage

### Coverage Reports

```bash
# Generate coverage report
python -m pytest tests/ --cov=src/amas --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Ensure PostgreSQL is running
   - Check connection parameters
   - Verify database exists

2. **Service Dependencies**:
   - Start required services (Redis, Neo4j, Ollama)
   - Check service configurations
   - Verify network connectivity

3. **Authentication Errors**:
   - Check JWT secret configuration
   - Verify token generation
   - Test with valid credentials

### Debug Mode

```bash
# Run tests with debug output
python -m pytest tests/ -v -s --tb=long

# Run specific test with debug
python -m pytest tests/test_core.py::TestAMASApplication::test_application_initialization -v -s
```

## Best Practices

### Test Writing

1. **Isolation**: Each test should be independent
2. **Clarity**: Use descriptive test names
3. **Completeness**: Test both success and failure cases
4. **Performance**: Keep tests fast and efficient
5. **Maintainability**: Use fixtures and helper functions

### Test Data Management

1. **Cleanup**: Clean up test data after each test
2. **Isolation**: Use separate test databases
3. **Consistency**: Use consistent test data structures
4. **Security**: Don't use production data in tests

### Continuous Improvement

1. **Regular Updates**: Keep tests current with code changes
2. **Coverage Monitoring**: Track and improve test coverage
3. **Performance**: Monitor test execution time
4. **Documentation**: Keep test documentation updated

## Test Results Interpretation

### Success Criteria

- All unit tests pass
- Integration tests complete successfully
- API tests return expected responses
- Performance tests meet benchmarks
- Coverage targets are met

### Failure Analysis

1. **Unit Test Failures**: Check individual component logic
2. **Integration Failures**: Verify component interactions
3. **API Failures**: Check endpoint implementations
4. **Performance Issues**: Optimize code and tests

## Future Enhancements

### Planned Improvements

1. **Automated Test Generation**: AI-generated test cases
2. **Visual Testing**: UI component testing
3. **Security Testing**: Penetration testing integration
4. **Performance Monitoring**: Real-time performance metrics
5. **Test Analytics**: Advanced test result analysis

### Test Automation

1. **Scheduled Testing**: Automated test execution
2. **Regression Testing**: Automated regression detection
3. **Performance Regression**: Automated performance monitoring
4. **Security Scanning**: Automated security testing

## Conclusion

The AMAS testing framework provides comprehensive coverage of all system components, ensuring reliability and functionality. Regular test execution and maintenance are essential for maintaining system quality and preventing regressions.

For questions or issues with testing, refer to the troubleshooting section or contact the development team.