# 🚀 AMAS Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the AMAS (Advanced Multi-Agent System) to production environments. The deployment process includes automated CI/CD pipelines, blue-green deployment strategies, and comprehensive monitoring.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Process](#deployment-process)
- [Monitoring & Validation](#monitoring--validation)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Memory**: Minimum 8GB RAM (16GB+ recommended)
- **Storage**: Minimum 50GB free disk space
- **CPU**: 4+ cores (8+ cores recommended)
- **Network**: Stable internet connection for container pulls

### Software Requirements

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: Version 2.25+
- **curl**: For health checks
- **jq**: For JSON processing
- **bc**: For mathematical calculations

### Access Requirements

- GitHub repository access
- Container registry access (GitHub Container Registry)
- Production environment access
- Monitoring system access

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/amas.git
cd amas
```

### 2. Create Environment Files

#### Production Environment

```bash
cp .env.example .env.production
```

Edit `.env.production` with production values:

```env
# Environment Configuration
AMAS_ENVIRONMENT=production
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-super-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
POSTGRES_PASSWORD=your-secure-postgres-password
DATABASE_URL=postgresql://postgres:your-secure-postgres-password@postgres:5432/amas

# Redis Configuration
REDIS_PASSWORD=your-secure-redis-password
REDIS_URL=redis://:your-secure-redis-password@redis:6379/0

# Neo4j Configuration
NEO4J_PASSWORD=your-secure-neo4j-password
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j

# Docker Registry
DOCKER_REGISTRY=ghcr.io
IMAGE_NAME=amas
IMAGE_TAG=latest

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
NOTIFICATION_EMAIL=admin@yourcompany.com
```

### 3. Set Up Monitoring

Create monitoring configuration:

```bash
mkdir -p monitoring/grafana/provisioning
mkdir -p nginx/ssl
mkdir -p logs
mkdir -p backups
```

### 4. Configure SSL Certificates

Place your SSL certificates in `nginx/ssl/`:
- `cert.pem` - SSL certificate
- `key.pem` - Private key
- `ca.pem` - Certificate authority (if applicable)

## Deployment Process

### Automated Deployment

#### Staging Deployment

```bash
# Deploy to staging
./scripts/deploy-staging.sh

# Validate deployment
./scripts/validate-deployment.sh --environment staging --type comprehensive
```

#### Production Deployment

```bash
# Deploy to production (blue-green)
./scripts/deploy-production.sh

# Validate deployment
./scripts/validate-deployment.sh --environment production --type comprehensive
```

### Manual Deployment

#### 1. Pre-deployment Checks

```bash
# Check system resources
df -h
free -h
docker system df

# Verify Docker is running
docker info

# Check environment files
ls -la .env*
```

#### 2. Build and Deploy

```bash
# Build production images
docker-compose -f docker-compose.production-blue.yml build

# Start services
docker-compose -f docker-compose.production-blue.yml up -d

# Wait for services to be healthy
sleep 60

# Check service status
docker-compose -f docker-compose.production-blue.yml ps
```

#### 3. Switch Load Balancer

```bash
# Update nginx configuration
sed -i 's/server localhost:8001;/server localhost:8000;/' nginx/production.conf

# Reload nginx
docker-compose exec nginx nginx -s reload
```

### CI/CD Pipeline Deployment

The automated CI/CD pipeline handles deployment through GitHub Actions:

1. **Code Push**: Push to `main` branch triggers production deployment
2. **Quality Gates**: Code quality, security, and test validation
3. **Build**: Docker image build and security scanning
4. **Deploy**: Blue-green deployment to production
5. **Validate**: Post-deployment validation and monitoring

## Monitoring & Validation

### Health Checks

#### API Health

```bash
# Basic health check
curl -f http://localhost:8000/health

# Detailed health check
curl -f http://localhost:8000/api/v1/health

# Metrics endpoint
curl -f http://localhost:8000/metrics
```

#### Service Health

```bash
# Check all services
docker-compose -f docker-compose.production-blue.yml ps

# Check individual services
docker-compose -f docker-compose.production-blue.yml logs amas-blue
docker-compose -f docker-compose.production-blue.yml logs postgres-blue
```

### Monitoring Dashboards

- **Grafana**: http://localhost:3001 (admin/amas_grafana_password)
- **Prometheus**: http://localhost:9090
- **Neo4j Browser**: http://localhost:7474 (neo4j/amas_password)

### Validation Scripts

```bash
# Basic validation
./scripts/validate-deployment.sh --environment production --type basic

# Comprehensive validation
./scripts/validate-deployment.sh --environment production --type comprehensive

# Security validation
./scripts/validate-deployment.sh --environment production --type security

# Performance validation
./scripts/validate-deployment.sh --environment production --type performance
```

## Rollback Procedures

### Automated Rollback

```bash
# Rollback to previous version
./scripts/rollback.sh --environment production

# Rollback to specific version
./scripts/rollback.sh --environment production --target v1.2.3

# Force rollback without confirmation
./scripts/rollback.sh --environment production --force
```

### Manual Rollback

#### 1. Switch Load Balancer

```bash
# Switch back to previous stack
sed -i 's/server localhost:8000;/server localhost:8001;/' nginx/production.conf
docker-compose exec nginx nginx -s reload
```

#### 2. Stop Current Stack

```bash
# Stop current stack
docker-compose -f docker-compose.production-blue.yml down
```

#### 3. Start Previous Stack

```bash
# Start previous stack
docker-compose -f docker-compose.production-green.yml up -d
```

### Database Rollback

```bash
# Restore database from backup
docker-compose -f docker-compose.production-blue.yml exec -T postgres-blue \
  psql -U postgres -d amas < backups/production-20240101-120000/database-backup.sql
```

## Troubleshooting

### Common Issues

#### 1. Services Not Starting

**Symptoms**: Services fail to start or become unhealthy

**Solutions**:
```bash
# Check logs
docker-compose -f docker-compose.production-blue.yml logs

# Check resource usage
docker stats

# Restart services
docker-compose -f docker-compose.production-blue.yml restart
```

#### 2. Database Connection Issues

**Symptoms**: Application cannot connect to database

**Solutions**:
```bash
# Check database status
docker-compose -f docker-compose.production-blue.yml exec postgres-blue pg_isready

# Check database logs
docker-compose -f docker-compose.production-blue.yml logs postgres-blue

# Test database connection
docker-compose -f docker-compose.production-blue.yml exec postgres-blue \
  psql -U postgres -d amas -c "SELECT 1;"
```

#### 3. High Memory Usage

**Symptoms**: System running out of memory

**Solutions**:
```bash
# Check memory usage
free -h
docker stats

# Clean up unused containers
docker system prune -f

# Restart services
docker-compose -f docker-compose.production-blue.yml restart
```

#### 4. SSL Certificate Issues

**Symptoms**: SSL/TLS connection errors

**Solutions**:
```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect your-domain.com:443

# Update certificates
# Place new certificates in nginx/ssl/ and restart nginx
docker-compose -f docker-compose.production-blue.yml restart nginx
```

### Log Analysis

#### Application Logs

```bash
# View application logs
docker-compose -f docker-compose.production-blue.yml logs -f amas-blue

# View specific log levels
docker-compose -f docker-compose.production-blue.yml logs amas-blue | grep ERROR

# Export logs
docker-compose -f docker-compose.production-blue.yml logs amas-blue > amas-logs.txt
```

#### System Logs

```bash
# View system logs
journalctl -u docker

# View nginx logs
docker-compose -f docker-compose.production-blue.yml logs nginx
```

### Performance Issues

#### CPU Usage

```bash
# Check CPU usage
top
htop

# Check container CPU usage
docker stats
```

#### Memory Usage

```bash
# Check memory usage
free -h
docker stats

# Check memory leaks
docker-compose -f docker-compose.production-blue.yml exec amas-blue \
  python -c "import psutil; print(psutil.virtual_memory())"
```

#### Disk Usage

```bash
# Check disk usage
df -h
du -sh /var/lib/docker

# Clean up Docker
docker system prune -f
docker volume prune -f
```

## Maintenance

### Regular Maintenance Tasks

#### Daily Tasks

- [ ] Check service health
- [ ] Review error logs
- [ ] Monitor resource usage
- [ ] Verify backups

#### Weekly Tasks

- [ ] Update dependencies
- [ ] Review security logs
- [ ] Test backup restoration
- [ ] Clean up old logs

#### Monthly Tasks

- [ ] Security updates
- [ ] Performance review
- [ ] Capacity planning
- [ ] Disaster recovery testing

### Backup Procedures

#### Automated Backups

```bash
# Create backup
./scripts/backup.sh --environment production

# List available backups
ls -la backups/

# Restore from backup
./scripts/restore.sh --environment production --backup 20240101-120000
```

#### Manual Backups

```bash
# Database backup
docker-compose -f docker-compose.production-blue.yml exec -T postgres-blue \
  pg_dump -U postgres amas > backup-$(date +%Y%m%d-%H%M%S).sql

# Configuration backup
tar -czf config-backup-$(date +%Y%m%d-%H%M%S).tar.gz nginx/ monitoring/ .env.production
```

### Updates and Upgrades

#### Application Updates

```bash
# Pull latest changes
git pull origin main

# Update images
docker-compose -f docker-compose.production-blue.yml pull

# Deploy updates
./scripts/deploy-production.sh
```

#### System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker
sudo apt install docker.io docker-compose -y

# Restart services
sudo systemctl restart docker
```

### Security Maintenance

#### Security Updates

```bash
# Check for security vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image amas:latest

# Update base images
docker-compose -f docker-compose.production-blue.yml build --no-cache
```

#### Access Management

```bash
# Rotate secrets
# Update .env.production with new secrets
# Restart services
docker-compose -f docker-compose.production-blue.yml restart
```

## Support and Documentation

### Additional Resources

- [API Documentation](API_DOCUMENTATION.md)
- [Configuration Guide](CONFIGURATION_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
- [Security Guide](SECURITY_GUIDE.md)

### Getting Help

- **GitHub Issues**: Create an issue for bugs or feature requests
- **Documentation**: Check the docs/ directory for detailed guides
- **Logs**: Always include relevant logs when reporting issues

### Emergency Contacts

- **On-call Engineer**: +1-555-0123
- **DevOps Team**: devops@yourcompany.com
- **Security Team**: security@yourcompany.com

---

**Last Updated**: January 2024  
**Version**: 1.0  
**Maintainer**: DevOps Team