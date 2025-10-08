# 🚀 AMAS Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying AMAS (Advanced Multi-Agent Intelligence System) to production environments.

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: Minimum 4GB, Recommended 8GB+
- **CPU**: Minimum 2 cores, Recommended 4+ cores
- **Storage**: Minimum 20GB free space
- **Network**: Internet connection for AI API calls

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl/wget

## Quick Start (One-Command Deployment)

### 1. Clone and Deploy
```bash
# Clone the repository
git clone <repository-url>
cd amas

# Make deployment script executable
chmod +x deploy.sh

# Run one-command deployment
./deploy.sh
```

### 2. Verify Deployment
```bash
# Check service status
docker-compose ps

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Access web dashboard
open http://localhost:3000
```

## Manual Deployment

### 1. Environment Setup

#### Create Environment File
```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env
```

#### Required Environment Variables
```bash
# Application
ENVIRONMENT=production
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Database
DATABASE_URL=postgresql://postgres:amas_password@postgres:5432/amas

# Redis
REDIS_URL=redis://:amas_redis_password@redis:6379/0

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=amas_password

# AI API Keys (at least one required)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 2. Database Setup

#### PostgreSQL
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Wait for database to be ready
docker-compose logs postgres

# Run database migrations (if applicable)
docker-compose exec amas python -m alembic upgrade head
```

#### Redis
```bash
# Start Redis
docker-compose up -d redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

#### Neo4j
```bash
# Start Neo4j
docker-compose up -d neo4j

# Wait for Neo4j to be ready
docker-compose logs neo4j

# Access Neo4j browser
open http://localhost:7474
```

### 3. Application Deployment

#### Build and Start Services
```bash
# Build application image
docker-compose build amas

# Start all services
docker-compose up -d

# Check service health
docker-compose ps
```

#### Verify Application
```bash
# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/agents

# Check logs
docker-compose logs amas
```

### 4. Monitoring Setup

#### Prometheus
```bash
# Access Prometheus
open http://localhost:9090

# Check metrics
curl http://localhost:8000/metrics
```

#### Grafana
```bash
# Access Grafana
open http://localhost:3001

# Default credentials
Username: admin
Password: amas_grafana_password
```

## Production Configuration

### 1. Security Hardening

#### SSL/TLS Setup
```bash
# Generate SSL certificates
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/amas.key \
  -out nginx/ssl/amas.crt

# Update nginx configuration for HTTPS
# Edit nginx/nginx.conf
```

#### Environment Security
```bash
# Use strong passwords
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Enable SSL
SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/amas.crt
SSL_KEY_PATH=/etc/ssl/private/amas.key
```

### 2. Performance Optimization

#### Resource Limits
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 1G
      cpus: '0.5'
```

#### Database Optimization
```bash
# PostgreSQL tuning
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
POSTGRES_WORK_MEM=4MB
```

### 3. Monitoring Configuration

#### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'amas'
    static_configs:
      - targets: ['amas:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

#### Grafana Dashboards
- Import AMAS dashboard from `monitoring/grafana/dashboards/`
- Configure alerting rules
- Set up notification channels

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
docker-compose logs <service-name>

# Check resource usage
docker stats

# Restart services
docker-compose restart <service-name>
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready -U postgres

# Test connection
docker-compose exec amas python -c "
import asyncio
from src.database.connection import is_connected
print(asyncio.run(is_connected()))
"
```

#### 3. Redis Connection Issues
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis
```

#### 4. Neo4j Connection Issues
```bash
# Check Neo4j status
docker-compose exec neo4j cypher-shell -u neo4j -p amas_password "RETURN 1"

# Check Neo4j logs
docker-compose logs neo4j
```

### Health Checks

#### Application Health
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed

# Metrics
curl http://localhost:8000/health/metrics
```

#### Service Dependencies
```bash
# Check all services
docker-compose ps

# Check service health
docker-compose exec amas python -c "
import asyncio
from src.database.connection import is_connected as db_connected
from src.cache.redis import is_connected as redis_connected
from src.graph.neo4j import is_connected as neo4j_connected

async def check_services():
    db = await db_connected()
    redis = await redis_connected()
    neo4j = await neo4j_connected()
    print(f'Database: {db}, Redis: {redis}, Neo4j: {neo4j}')

asyncio.run(check_services())
"
```

## Maintenance

### 1. Updates

#### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build amas
docker-compose up -d amas
```

#### Database Migrations
```bash
# Run migrations
docker-compose exec amas python -m alembic upgrade head

# Check migration status
docker-compose exec amas python -m alembic current
```

### 2. Backups

#### Database Backup
```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U postgres amas > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose exec -T postgres psql -U postgres amas < backup_file.sql
```

#### Application Data Backup
```bash
# Backup application data
tar -czf amas_data_backup_$(date +%Y%m%d_%H%M%S).tar.gz data/ logs/

# Restore application data
tar -xzf amas_data_backup_file.tar.gz
```

### 3. Monitoring

#### Log Management
```bash
# View logs
docker-compose logs -f amas

# Rotate logs
docker-compose exec amas logrotate /etc/logrotate.conf
```

#### Performance Monitoring
```bash
# Check resource usage
docker stats

# Check disk usage
df -h

# Check memory usage
free -h
```

## Scaling

### 1. Horizontal Scaling

#### Load Balancer Setup
```yaml
# nginx/nginx.conf
upstream amas_backend {
    server amas1:8000;
    server amas2:8000;
    server amas3:8000;
}
```

#### Multiple Instances
```bash
# Scale application
docker-compose up -d --scale amas=3

# Check scaled services
docker-compose ps
```

### 2. Database Scaling

#### Read Replicas
```yaml
# Add read replica
services:
  postgres-replica:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=amas
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=amas_password
    volumes:
      - postgres_replica_data:/var/lib/postgresql/data
```

## Security Considerations

### 1. Network Security
- Use firewalls to restrict access
- Enable SSL/TLS encryption
- Use VPN for remote access

### 2. Data Security
- Encrypt sensitive data at rest
- Use secure communication protocols
- Regular security audits

### 3. Access Control
- Implement RBAC (Role-Based Access Control)
- Use strong authentication
- Regular access reviews

## Support

### Documentation
- API Documentation: http://localhost:8000/docs
- Health Dashboard: http://localhost:8000/health
- Monitoring: http://localhost:3001

### Logs
- Application logs: `logs/amas.log`
- Docker logs: `docker-compose logs`
- System logs: `/var/log/syslog`

### Contact
- Technical Support: [support@amas.ai]
- Documentation: [docs.amas.ai]
- GitHub Issues: [github.com/amas/issues]

---

**Note**: This deployment guide assumes a production environment. For development environments, some security measures may be relaxed.