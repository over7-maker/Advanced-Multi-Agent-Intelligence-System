# Production Component Test Suite

Comprehensive test coverage for all production deployment components implemented in PART_8 and PART_9.

## Test Structure

```
tests/
├── validation/          # Syntax & configuration validation tests
├── functional/          # Functional tests for scripts and builds
├── integration/         # Integration tests for full stack
├── performance/         # Performance benchmarks
├── security/            # Security validation tests
├── documentation/       # Documentation validation tests
├── manual/              # Manual validation procedures
├── fixtures/            # Test fixtures
└── utils/               # Test utilities and helpers
```

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### By Category
```bash
# Validation tests
pytest tests/validation/ -v

# Functional tests
pytest tests/functional/ -v

# Integration tests (requires Docker)
pytest tests/integration/ -v -m integration

# Performance tests
pytest tests/performance/ -v -m performance

# Security tests
pytest tests/security/ -v -m security

# Documentation tests
pytest tests/documentation/ -v -m documentation
```

### Excluding Slow Tests
```bash
pytest tests/ -v -m "not slow"
```

### With Coverage
```bash
pytest tests/ --cov=tests --cov-report=html
```

## Test Categories

### 1. Validation Tests (`tests/validation/`)

Validates syntax and configuration of all production files:
- `test_dockerfile.py` - Dockerfile validation
- `test_docker_compose.py` - Docker Compose validation
- `test_nginx_config.py` - Nginx configuration validation
- `test_k8s_manifests.py` - Kubernetes manifest validation
- `test_cicd_workflow.py` - CI/CD workflow validation
- `test_env_template.py` - Environment template validation

### 2. Functional Tests (`tests/functional/`)

Tests functionality of scripts and builds:
- `test_docker_build.py` - Docker build functionality
- `test_backup_script.py` - Backup script functionality
- `test_restore_script.py` - Restore script functionality
- `test_deploy_script.py` - Deployment script functionality
- `test_alembic_migrations.py` - Database migration functionality

### 3. Integration Tests (`tests/integration/`)

Tests full stack integration:
- `test_production_stack.py` - Full Docker Compose stack
- `test_backup_restore.py` - Backup/restore integration
- `test_deployment_pipeline.py` - Deployment pipeline integration

### 4. Performance Tests (`tests/performance/`)

Performance benchmarks:
- `test_build_performance.py` - Build time benchmarks
- `test_script_performance.py` - Script execution time benchmarks

### 5. Security Tests (`tests/security/`)

Security validation:
- `test_config_security.py` - Configuration security
- `test_container_security.py` - Container security
- `test_network_security.py` - Network security

### 6. Documentation Tests (`tests/documentation/`)

Documentation validation:
- `test_docs_validation.py` - Markdown syntax and structure
- `test_docs_completeness.py` - Documentation completeness

## Manual Validation

See `tests/manual/MANUAL_VALIDATION_CHECKLIST.md` for step-by-step manual validation procedures.

## CI/CD Integration

Tests run automatically in GitHub Actions via `.github/workflows/test-production.yml`:
- Validation tests run on every PR
- Functional tests run on every PR
- Integration tests run on every PR (with Docker)
- Performance tests run only on main branch pushes
- Security tests run on every PR
- Documentation tests run on every PR

## Prerequisites

### Required Tools
- Python 3.11+
- pytest
- Docker (for integration tests)
- Docker Compose (for integration tests)

### Optional Tools
- kubectl (for K8s validation)
- nginx (for nginx config validation)
- hadolint (for Dockerfile linting)
- trivy (for container security scanning)

## Test Fixtures

Fixtures are defined in `tests/fixtures/production_fixtures.py`:
- `project_root` - Project root directory
- `dockerfile_path` - Dockerfile path
- `docker_compose_path` - docker-compose.prod.yml path
- `nginx_config_path` - nginx.conf path
- `k8s_manifest_path` - k8s/deployment.yaml path
- And more...

## Test Utilities

Utilities are in `tests/utils/validation_helpers.py`:
- `YAMLValidator` - YAML file validation
- `DockerfileValidator` - Dockerfile validation
- `NginxConfigValidator` - Nginx config validation
- `KubernetesManifestValidator` - K8s manifest validation
- `EnvFileValidator` - Environment file validation
- `MarkdownValidator` - Markdown validation

## Troubleshooting

### Tests Fail with Import Errors
```bash
# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pyyaml requests
```

### Docker Tests Fail
```bash
# Ensure Docker is running
docker ps

# Check Docker Compose is available
docker-compose --version
```

### Integration Tests Timeout
- Increase timeout values in test files
- Ensure sufficient system resources
- Check Docker daemon is responsive

## Success Criteria

All tests should:
- ✅ Pass validation tests
- ✅ Pass functional tests
- ✅ Pass integration tests (when services available)
- ✅ Meet performance thresholds
- ✅ Pass security checks
- ✅ Pass documentation validation

## Contributing

When adding new production components:
1. Add validation tests in `tests/validation/`
2. Add functional tests in `tests/functional/`
3. Add integration tests if needed
4. Update this README
5. Ensure all tests pass

