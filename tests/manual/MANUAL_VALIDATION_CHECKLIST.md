# Manual Validation Checklist

This document provides step-by-step manual validation procedures for all production components.

## Pre-Validation Setup

- [ ] Docker and Docker Compose installed and running
- [ ] Kubernetes cluster accessible (for K8s tests)
- [ ] Required environment variables set in `.env.production`
- [ ] All required API keys configured
- [ ] Network access to required services

## 1. Dockerfile Validation

### Visual Inspection
- [ ] Open `Dockerfile` and verify:
  - [ ] Multi-stage build structure (python-builder, frontend-builder, production)
  - [ ] Non-root user creation (`useradd`, `USER` directive)
  - [ ] Health check configuration
  - [ ] Minimal base images used
  - [ ] No hardcoded secrets

### Build Test
```bash
# Build the image
docker build -t amas-test:manual .

# Verify image builds successfully
docker images | grep amas-test

# Check image size (should be reasonable)
docker images amas-test:manual
```

### Security Check
```bash
# Run security scan (if trivy available)
trivy image amas-test:manual
```

## 2. Docker Compose Validation

### Configuration Review
- [ ] Open `docker-compose.prod.yml` and verify:
  - [ ] All 15 services defined
  - [ ] Service dependencies correct
  - [ ] Health checks configured
  - [ ] Resource limits set
  - [ ] Volumes and networks defined

### Stack Startup Test
```bash
# Start the stack
docker-compose -f docker-compose.prod.yml up -d

# Check all services are running
docker-compose -f docker-compose.prod.yml ps

# Check service logs
docker-compose -f docker-compose.prod.yml logs --tail=50

# Stop the stack
docker-compose -f docker-compose.prod.yml down
```

## 3. Nginx Configuration Validation

### Syntax Check
```bash
# Test nginx configuration
docker run --rm -v $(pwd)/nginx:/etc/nginx:ro nginx:alpine nginx -t
```

### Visual Inspection
- [ ] Open `nginx/nginx.conf` and verify:
  - [ ] SSL/TLS configuration
  - [ ] Security headers present
  - [ ] Rate limiting configured
  - [ ] WebSocket support
  - [ ] Upstream backend defined

## 4. Kubernetes Manifest Validation

### Syntax Check
```bash
# Validate manifests
kubectl apply --dry-run=client -f k8s/deployment.yaml
```

### Visual Inspection
- [ ] Open `k8s/deployment.yaml` and verify:
  - [ ] All resource types present
  - [ ] Namespace defined
  - [ ] ConfigMap and Secret configured
  - [ ] Deployment with proper replicas
  - [ ] Service and Ingress configured
  - [ ] HPA configured
  - [ ] PVCs defined

## 5. CI/CD Workflow Validation

### Visual Inspection
- [ ] Open `.github/workflows/deploy.yml` and verify:
  - [ ] All required jobs present
  - [ ] Job dependencies correct
  - [ ] Test job configured
  - [ ] Build job configured
  - [ ] Deploy job configured

### GitHub Actions Test
- [ ] Push to test branch
- [ ] Verify workflow runs
- [ ] Check all jobs pass

## 6. Backup Script Validation

### Manual Execution
```bash
# Test backup script
./scripts/backup.sh --environment test --type full

# Verify backup files created
ls -la backups/

# Check backup manifest
cat backups/*/backup-manifest.json
```

### Functionality Check
- [ ] Database backup created
- [ ] Redis backup created
- [ ] Manifest file created
- [ ] Verification passes

## 7. Restore Script Validation

### Manual Execution
```bash
# Test restore script (with confirmation)
./scripts/restore.sh --environment test --backup <backup-path>

# Verify restore completes
# Check database contents
```

### Functionality Check
- [ ] Confirmation prompt works
- [ ] Backup detection works
- [ ] Database restore works
- [ ] Verification passes

## 8. Deployment Script Validation

### Manual Execution
```bash
# Test deployment script
./scripts/deploy-production.sh --build

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

### Functionality Check
- [ ] Pre-flight checks pass
- [ ] Backup created
- [ ] Build succeeds
- [ ] Deployment succeeds
- [ ] Health checks pass
- [ ] Migrations run

## 9. Alembic Migration Validation

### Manual Execution
```bash
# Test migration
alembic upgrade head

# Verify migration
alembic current

# Test downgrade
alembic downgrade -1
```

### Functionality Check
- [ ] Migration runs successfully
- [ ] Database schema updated
- [ ] Downgrade works

## 10. Documentation Review

### Visual Inspection
- [ ] Review `docs/SECURITY.md`:
  - [ ] All sections complete
  - [ ] Examples work
  - [ ] No placeholder text

- [ ] Review `docs/PERFORMANCE.md`:
  - [ ] All sections complete
  - [ ] Performance targets defined
  - [ ] Examples work

- [ ] Review `docs/SCALING.md`:
  - [ ] Scaling strategies documented
  - [ ] Thresholds defined

- [ ] Review `docs/PRODUCTION_CHECKLIST.md`:
  - [ ] All steps documented
  - [ ] Checklist complete

## Troubleshooting

### Common Issues

1. **Docker build fails**
   - Check Docker daemon is running
   - Verify Dockerfile syntax
   - Check disk space

2. **Services won't start**
   - Check port conflicts
   - Verify environment variables
   - Check service logs

3. **Migrations fail**
   - Verify database connection
   - Check migration file syntax
   - Verify database permissions

4. **Scripts fail**
   - Check script permissions (`chmod +x`)
   - Verify required tools installed
   - Check environment variables

## Success Criteria

All manual validations should:
- [ ] Complete without errors
- [ ] Produce expected outputs
- [ ] Follow documented procedures
- [ ] Match automated test results

