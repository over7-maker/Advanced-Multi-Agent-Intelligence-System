# Data Governance CI/CD Workflow Guide

## Overview

The Data Governance & Compliance CI/CD workflow (`.github/workflows/governance-ci.yml`) performs comprehensive quality checks for the governance module. This document explains the workflow configuration, jobs, and how checks map to specific steps.

## Workflow Configuration

### Triggers

The workflow runs automatically on:
- **Push** to `main` or `feature/data-governance-compliance` branches
- **Pull requests** to `main` branch
- **File changes** in:
  - `src/amas/governance/**/*.py` (module files)
  - `tests/test_data_classifier*.py` (test files)
  - `verify_data_classifier.py` (verification script)
  - `requirements-ci.txt` (dependencies)
  - `mypy.ini` (type checking config)
  - `.github/workflows/governance-ci.yml` (workflow itself)
  - `**/governance*.md` (governance documentation)

### Concurrency

- **Strategy**: Cancel in-progress runs when a new commit is pushed
- **Group**: `${{ github.workflow }}-${{ github.ref }}`
- **Purpose**: Prevents multiple workflow runs from consuming resources unnecessarily

### Environment Variables

- **PYTHON_VERSION**: `3.12.12` (pinned for reproducibility and security)
- **TIMEOUT_MINUTES**: `20` (maximum time per job)
- **MIN_PYTHON_VERSION**: `3.12` (minimum required for type checking features)

---

## Jobs and Checks Mapping

### Job 1: `type-check` - Static Type Checking

**Purpose**: Validates type annotations and catches type-related bugs before runtime

**Tools**:
- **mypy** (v1.18.2): Strict type checking with `mypy.ini` configuration
- **pyright** (v1.1.407): Additional type validation

**Configuration**:
- **Config File**: `mypy.ini`
- **Strict Mode**: Enabled (`--check-untyped-defs`, `--disallow-untyped-defs`, `--disallow-incomplete-defs`)
- **Target**: `src/amas/governance/data_classifier.py`

**Steps**:
1. Checkout code
2. Set up Python (3.12.12)
3. Cache pip packages
4. Install dependencies from `requirements-ci.txt`
5. Run mypy with strict flags
6. Run pyright
7. Upload type check results (if any)

**Timeout**: 20 minutes

---

### Job 2: `lint` - Code Style and Quality

**Purpose**: Enforces code style and quality standards

**Tools**:
- **flake8** (v7.3.0): PEP 8 style checking
- **pylint** (v4.0.2): Code quality and complexity analysis

**Configuration**:
- **flake8**: 
  - Max line length: 120
  - Ignore: E203, W503 (conflicts with Black formatter)
  - Target: `src/amas/governance/data_classifier.py`
- **pylint**:
  - Target: `src/amas/governance/data_classifier.py`
  - Uses default configuration

**Steps**:
1. Checkout code
2. Set up Python (3.12.12)
3. Cache pip packages
4. Install dependencies from `requirements-ci.txt`
5. Run flake8
6. Run pylint

**Timeout**: 20 minutes

---

### Job 3: `test` - Unit Testing and Coverage

**Purpose**: Validates functionality and measures code coverage

**Tools**:
- **pytest** (v9.0.0): Test runner
- **pytest-cov** (v7.0.0): Coverage reporting
- **pytest-rerunfailures** (v14.0): Flaky test handling

**Configuration**:
- **Test Files**: `tests/test_data_classifier.py`
- **Coverage Target**: `src/amas/governance`
- **Coverage Reports**: XML (for CI) and terminal output
- **Retry Strategy**: 2 retries with 1 second delay

**Steps**:
1. Checkout code
2. Set up Python (3.12.12)
3. Cache pip packages
4. Install dependencies from `requirements-ci.txt`
5. Run tests with coverage and retries
6. Upload coverage reports (30 day retention)

**Timeout**: 20 minutes

**Coverage Threshold**: No explicit threshold set (monitored via reports)

---

### Job 4: `performance` - Performance Testing

**Purpose**: Validates performance characteristics and prevents regressions

**Tools**:
- **pytest** (v9.0.0): Test runner
- **pytest-benchmark** (v4.0.0): Performance benchmarking

**Configuration**:
- **Test Files**: `tests/test_data_classifier_performance.py`
- **Benchmarks**: 
  - Large payload handling (< 1s for 1MB)
  - ReDoS prevention
  - DoS protection validation

**Steps**:
1. Checkout code
2. Set up Python (3.12.12)
3. Cache pip packages
4. Install dependencies from `requirements-ci.txt`
5. Run performance tests with benchmarks

**Timeout**: 20 minutes

**Performance Requirements**:
- 1MB payload: < 1.0s
- ReDoS prevention: < 500ms with malicious input
- Credit card detection: < 100ms

---

### Job 5: `security` - Security Scanning

**Purpose**: Identifies security vulnerabilities in code and dependencies

**Tools**:
- **bandit** (v1.7.10): Static security analysis for Python code
- **safety** (v3.2.7): Dependency vulnerability scanning

**Configuration**:
- **bandit**:
  - Target: `src/amas/governance/data_classifier.py`
  - Severity levels: Low, Medium, High, Critical
  - Confidence levels: Low, Medium, High
- **safety**:
  - Checks: `requirements-ci.txt` for known CVEs
  - Database: Safety DB (updated automatically)

**Steps**:
1. Checkout code
2. Set up Python (3.12.12)
3. Cache pip packages
4. Install dependencies from `requirements-ci.txt`
5. Run bandit security scan
6. Run safety dependency check
7. Upload security reports (90 day retention)

**Timeout**: 20 minutes

**Security Checks**:
- Code vulnerabilities (SQL injection, XSS, etc.)
- Hardcoded secrets detection
- Dependency CVEs
- PII leakage in code

---

## Dependency Management

### Installation Strategy

1. **Primary**: Install from `requirements-ci.txt` (pinned versions)
2. **Validation**: Run `pip check` to detect conflicts
3. **Fallback**: If primary fails, install core tools directly
4. **Verification**: Check tool versions after installation

### Pinned Versions

All tools are pinned to exact versions in `requirements-ci.txt`:
- mypy==1.18.2
- pyright==1.1.407
- flake8==7.3.0
- pylint==4.0.2
- pytest==9.0.0
- pytest-cov==7.0.0
- pytest-benchmark==4.0.0
- pytest-rerunfailures==14.0
- bandit==1.7.10
- safety==3.2.7

**Security Note**: Update versions when security patches are released.

---

## Caching Strategy

### Pip Package Cache

- **Path**: `~/.cache/pip`
- **Key**: `${{ runner.os }}-pip-${{ hashFiles('requirements-ci.txt') }}`
- **Restore Keys**: `${{ runner.os }}-pip-`
- **Purpose**: Reduces build time by caching installed packages

---

## Artifact Management

### Test Coverage Reports

- **Retention**: 30 days
- **Format**: XML (for CI integration) and terminal output
- **Location**: `coverage.xml` and terminal output

### Security Reports

- **Retention**: 90 days
- **Format**: JSON (bandit) and text (safety)
- **Location**: GitHub Actions artifacts

---

## Error Handling

### Dependency Installation

- **Primary**: Try `requirements-ci.txt` with validation
- **Fallback**: Install core tools directly if primary fails
- **Verification**: Check tool versions after installation

### Test Failures

- **Retry Strategy**: 2 retries with 1 second delay (for flaky tests)
- **Error Messages**: Clear and actionable
- **Logging**: All errors logged with context

---

## Performance Optimization

### Parallel Execution

- **Strategy**: All 5 jobs run in parallel
- **Resource Usage**: Maximizes GitHub Actions runner utilization
- **Total Time**: ~20 minutes (longest job duration)

### Caching

- **Pip Cache**: Reduces dependency installation time
- **Cache Key**: Based on `requirements-ci.txt` hash
- **Cache Hit**: Saves ~30-60 seconds per job

---

## Security Considerations

### Version Pinning

- **Python**: 3.12.12 (pinned for reproducibility)
- **Tools**: All pinned in `requirements-ci.txt`
- **Updates**: Check regularly for security patches

### Secrets Management

- **No Hardcoded Secrets**: All secrets stored in GitHub Secrets
- **Artifact Security**: Reports stored securely in GitHub Actions
- **Log Security**: Sensitive data redacted before logging

---

## Troubleshooting

### Common Issues

**Issue**: `mypy: command not found`
- **Solution**: Check dependency installation step, verify `requirements-ci.txt` exists

**Issue**: Tests fail intermittently
- **Solution**: Retry strategy handles flaky tests (2 retries with 1s delay)

**Issue**: Dependency conflicts
- **Solution**: `pip check` detects conflicts, fallback installation available

**Issue**: Timeout errors
- **Solution**: Increase `TIMEOUT_MINUTES` if needed (default: 20 minutes)

---

## Best Practices

1. **Version Pinning**: Always pin tool versions for reproducibility
2. **Error Handling**: Comprehensive error handling with clear messages
3. **Caching**: Use caching to reduce build times
4. **Parallel Execution**: Run independent jobs in parallel
5. **Artifact Retention**: Set appropriate retention periods for artifacts
6. **Security**: Never hardcode secrets, use GitHub Secrets
7. **Documentation**: Keep workflow documentation up to date

---

## Related Documentation

- [Data Governance Guide](DATA_GOVERNANCE_GUIDE.md) - Complete module guide
- [API Reference](API_REFERENCE.md) - API documentation
- [Workflow File](../.github/workflows/governance-ci.yml) - Actual workflow definition

---

## Version History

- **v1.0.0** (PR #242): Initial workflow implementation
  - 5 jobs: type-check, lint, test, performance, security
  - Comprehensive error handling
  - Caching and parallel execution
