# 🔄 AMAS CI/CD Pipeline Documentation

## Overview

The AMAS CI/CD pipeline provides automated testing, building, and deployment capabilities for the Advanced Multi-Agent System. This pipeline ensures code quality, security, and reliable deployments across staging and production environments.

## Table of Contents

- [Pipeline Architecture](#pipeline-architecture)
- [Workflow Configuration](#workflow-configuration)
- [Jobs and Stages](#jobs-and-stages)
- [Environment Management](#environment-management)
- [Security and Compliance](#security-and-compliance)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Troubleshooting](#troubleshooting)

## Pipeline Architecture

### High-Level Overview

```mermaid
graph TD
    A[Code Push/PR] --> B[Quality Gate]
    B --> C[Test Suite]
    C --> D[Docker Build]
    D --> E[Security Scan]
    E --> F[Deploy Staging]
    F --> G[E2E Tests]
    G --> H[Deploy Production]
    H --> I[Post-Deployment Validation]
    I --> J[Monitoring & Alerting]
```

### Pipeline Stages

1. **Pre-deployment Checks**
   - Dependency scanning
   - Code quality validation
   - Security analysis

2. **Testing**
   - Unit tests
   - Integration tests
   - End-to-end tests
   - Performance tests

3. **Build & Security**
   - Docker image building
   - Security scanning
   - Vulnerability assessment

4. **Deployment**
   - Staging deployment
   - Production deployment (blue-green)
   - Service validation

5. **Post-deployment**
   - Health checks
   - Performance validation
   - Monitoring setup

## Workflow Configuration

### Main Workflow File

**Location**: `.github/workflows/production-cicd.yml`

**Triggers**:
- Push to `main`, `develop`, `production` branches
- Pull requests to `main`, `develop`, `production` branches
- Release events
- Manual workflow dispatch

### Environment Variables

```yaml
env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '20'
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: amas
  REGISTRY_USERNAME: ${{ github.actor }}
  REGISTRY_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
```

### Secrets Configuration

Required secrets in GitHub repository:

- `GITHUB_TOKEN` - Automatically provided
- `DOCKER_REGISTRY_TOKEN` - Container registry access
- `SLACK_WEBHOOK_URL` - Slack notifications
- `NOTIFICATION_EMAIL` - Email notifications
- `SNYK_TOKEN` - Security scanning
- `MONITORING_WEBHOOK_URL` - Monitoring alerts

## Jobs and Stages

### 1. Pre-deployment Checks

#### Dependency Scan Job

```yaml
dependency-scan:
  name: 🔍 Dependency Security Scan
  runs-on: ubuntu-latest
  outputs:
    vulnerabilities-found: ${{ steps.scan-results.outputs.vulnerabilities }}
```

**Tools Used**:
- Safety - Python dependency vulnerability scanner
- pip-audit - Additional Python security audit
- Semgrep - Static analysis security scanner

**Outputs**:
- Security reports in JSON format
- Vulnerability count for decision making

#### Code Quality Job

```yaml
code-quality:
  name: 🎨 Code Quality & Standards
  runs-on: ubuntu-latest
  outputs:
    quality-score: ${{ steps.quality-check.outputs.score }}
```

**Tools Used**:
- Black - Code formatting
- isort - Import sorting
- Flake8 - Linting
- Pylint - Code analysis
- MyPy - Type checking

**Quality Gates**:
- Code formatting compliance
- Linting errors < 10
- Type checking warnings < 5
- Quality score > 80

### 2. Testing Suite

#### Unit Tests

```yaml
unit-tests:
  name: 🧪 Unit Tests
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python-version: ['3.9', '3.10', '3.11']
      os: [ubuntu-latest, windows-latest, macos-latest]
```

**Coverage Requirements**:
- Minimum 80% code coverage
- All critical paths tested
- Edge cases covered

#### Integration Tests

```yaml
integration-tests:
  name: 🔗 Integration Tests
  runs-on: ubuntu-latest
  needs: [dependency-scan, code-quality]
```

**Services**:
- PostgreSQL 15
- Redis 7
- Neo4j 5

**Test Categories**:
- Database connectivity
- API endpoint integration
- Service communication
- Data persistence

#### End-to-End Tests

```yaml
e2e-tests:
  name: 🎭 End-to-End Tests
  runs-on: ubuntu-latest
  needs: [unit-tests, integration-tests]
```

**Test Scenarios**:
- Complete user workflows
- API functionality
- Database operations
- Error handling

#### Performance Tests

```yaml
performance-tests:
  name: ⚡ Performance Tests
  runs-on: ubuntu-latest
  needs: [unit-tests]
```

**Performance Metrics**:
- Response time < 2 seconds
- Throughput > 100 requests/second
- Memory usage < 2GB
- CPU usage < 80%

### 3. Build & Security

#### Docker Build

```yaml
docker-build:
  name: 🐳 Docker Build & Security Scan
  runs-on: ubuntu-latest
  needs: [unit-tests, integration-tests]
  outputs:
    image-digest: ${{ steps.build.outputs.digest }}
```

**Build Process**:
- Multi-platform builds (linux/amd64, linux/arm64)
- Layer caching for efficiency
- Security scanning with Trivy
- Vulnerability assessment with Snyk

**Security Scanning**:
- Container image vulnerabilities
- Base image security
- Dependency vulnerabilities
- Configuration security

### 4. Deployment

#### Staging Deployment

```yaml
deploy-staging:
  name: 🚀 Deploy to Staging
  runs-on: ubuntu-latest
  needs: [docker-build, e2e-tests, performance-tests]
  if: github.ref == 'refs/heads/develop' || github.event_name == 'workflow_dispatch'
  environment: staging
```

**Deployment Process**:
- Automated staging deployment
- Smoke tests execution
- Environment validation
- Notification sending

#### Production Deployment

```yaml
deploy-production:
  name: 🌟 Deploy to Production
  runs-on: ubuntu-latest
  needs: [docker-build, e2e-tests, performance-tests]
  if: github.ref == 'refs/heads/main' || (github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'production')
  environment: production
```

**Progressive Delivery with Argo Rollouts**:
- **Canary Deployments**: Progressive traffic shifting (10%→25%→50%→75%→100%)
- **Automatic Rollback**: SLO violations trigger immediate rollback within 2 minutes
- **Zero-downtime**: No service interruption during deployments
- **SLO-based Gates**: Health checks and metrics validation prevent bad deployments
- **Analysis Integration**: Success rate, latency P95, and error budget validation
- **Blue-Green Capability**: Instant traffic switching for emergency scenarios

**Deployment Workflow**:
1. Build and scan container image
2. Deploy to staging with smoke tests
3. Trigger canary deployment in production
4. Monitor metrics at each traffic level (10%, 25%, 50%, 75%)
5. Automatic promotion or rollback based on SLO validation
6. Post-deployment validation and monitoring

**Workflow File**: `.github/workflows/progressive-delivery.yml`

For detailed Progressive Delivery documentation, see:
- [Progressive Delivery Quick Start](../PROGRESSIVE_DELIVERY_QUICK_START.md)
- [Progressive Delivery Implementation](../PROGRESSIVE_DELIVERY_IMPLEMENTATION.md)

### 5. Post-deployment Validation

#### Validation Job

```yaml
post-deployment-validation:
  name: ✅ Post-Deployment Validation
  runs-on: ubuntu-latest
  needs: [deploy-staging, deploy-production]
  if: always() && (needs.deploy-staging.result == 'success' || needs.deploy-production.result == 'success')
```

**Validation Checks**:
- Service health verification
- API endpoint testing
- Database connectivity
- Performance baseline validation

## Environment Management

### Staging Environment

**Purpose**: Pre-production testing and validation

**Configuration**:
- Environment: `staging`
- Database: `amas_staging`
- Log Level: `DEBUG`
- Monitoring: Full monitoring enabled

**Access**:
- URL: `https://staging.amas.yourcompany.com`
- Admin: `admin@yourcompany.com`
- Credentials: Managed via environment variables

### Production Environment

**Purpose**: Live production system

**Configuration**:
- Environment: `production`
- Database: `amas`
- Log Level: `INFO`
- Monitoring: Full monitoring + alerting

**Access**:
- URL: `https://api.amas.yourcompany.com`
- Admin: `admin@yourcompany.com`
- Credentials: Managed via secure secrets

### Environment Variables

#### Staging Environment

```env
AMAS_ENVIRONMENT=staging
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://postgres:staging_password@postgres:5432/amas_staging
REDIS_URL=redis://:staging_redis_password@redis:6379/0
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=staging_neo4j_password
```

#### Production Environment

```env
AMAS_ENVIRONMENT=production
LOG_LEVEL=INFO
DATABASE_URL=postgresql://postgres:production_password@postgres:5432/amas
REDIS_URL=redis://:production_redis_password@redis:6379/0
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=production_neo4j_password
```

## Security and Compliance

### Security Scanning

#### Dependency Scanning

- **Safety**: Python package vulnerability scanning
- **pip-audit**: Additional Python security audit
- **npm audit**: Node.js package vulnerability scanning

#### Container Security

- **Trivy**: Container image vulnerability scanning
- **Snyk**: Additional container security analysis
- **Docker Scout**: Docker security scanning

#### Code Security

- **Semgrep**: Static analysis security scanning
- **Bandit**: Python security linting
- **ESLint Security**: JavaScript security linting

### Compliance

#### Security Standards

- OWASP Top 10 compliance
- CVE vulnerability scanning
- Security header validation
- SSL/TLS configuration validation

#### Data Protection

- GDPR compliance checks
- Data encryption validation
- Access control verification
- Audit logging validation

### Secret Management

#### GitHub Secrets

- Repository-level secrets
- Environment-specific secrets
- Encrypted secret storage
- Secret rotation policies

#### Environment Secrets

- Database credentials
- API keys
- SSL certificates
- Monitoring tokens

## Monitoring and Alerting

### Pipeline Monitoring

#### Success Metrics

- Deployment success rate
- Test pass rate
- Build time
- Deployment time

#### Failure Metrics

- Failed deployments
- Test failures
- Security vulnerabilities
- Performance regressions

### Application Monitoring

#### Health Checks

- API health endpoints
- Database connectivity
- Service availability
- Performance metrics

#### Alerting

- Slack notifications
- Email alerts
- PagerDuty integration
- Custom webhook notifications

### Monitoring Tools

#### Prometheus

- Metrics collection
- Time-series data
- Query language (PromQL)
- Alerting rules

#### Grafana

- Dashboard visualization
- Real-time monitoring
- Custom dashboards
- Alert management

## Troubleshooting

### Common Issues

#### Pipeline Failures

**Dependency Scan Failures**:
```bash
# Check dependency vulnerabilities
pip install safety
safety check

# Update vulnerable packages
pip install --upgrade package-name
```

**Test Failures**:
```bash
# Run tests locally
pytest tests/ -v

# Check test coverage
pytest --cov=src tests/

# Debug specific test
pytest tests/unit/test_specific.py -v -s
```

**Build Failures**:
```bash
# Build Docker image locally
docker build -t amas:test .

# Check Docker logs
docker logs container-name

# Clean up Docker
docker system prune -f
```

#### Deployment Issues

**Service Health Issues**:
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs service-name

# Restart services
docker-compose restart service-name
```

**Database Issues**:
```bash
# Check database connectivity
docker-compose exec postgres pg_isready

# Check database logs
docker-compose logs postgres

# Test database queries
docker-compose exec postgres psql -U postgres -d amas -c "SELECT 1;"
```

### Debugging Commands

#### Pipeline Debugging

```bash
# Enable debug logging
export ACTIONS_STEP_DEBUG=true
export ACTIONS_RUNNER_DEBUG=true

# Check workflow status
gh run list
gh run view run-id

# Download workflow logs
gh run download run-id
```

#### Application Debugging

```bash
# Check application logs
docker-compose logs -f amas

# Debug container
docker-compose exec amas bash

# Check environment variables
docker-compose exec amas env
```

### Performance Issues

#### Build Performance

- Use Docker layer caching
- Optimize Dockerfile
- Parallel job execution
- Resource allocation

#### Test Performance

- Parallel test execution
- Test data optimization
- Mock external services
- Test selection strategies

#### Deployment Performance

- Blue-green deployment
- Health check optimization
- Load balancer configuration
- Resource monitoring

## Best Practices

### Development

1. **Code Quality**
   - Write comprehensive tests
   - Follow coding standards
   - Use type hints
   - Document code

2. **Security**
   - Regular dependency updates
   - Security scanning
   - Secret management
   - Access control

3. **Performance**
   - Optimize Docker images
   - Use caching strategies
   - Monitor resource usage
   - Load testing

### Deployment

1. **Reliability**
   - Blue-green deployment
   - Health checks
   - Rollback procedures
   - Monitoring

2. **Security**
   - Environment isolation
   - Secret management
   - Access control
   - Audit logging

3. **Monitoring**
   - Comprehensive logging
   - Performance metrics
   - Alerting
   - Dashboard visualization

---

**Last Updated**: January 2024  
**Version**: 1.0  
**Maintainer**: DevOps Team