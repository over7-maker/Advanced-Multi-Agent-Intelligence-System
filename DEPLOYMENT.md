# 🚀 AMAS Deployment Guide

> Comprehensive guide for deploying the Advanced Multi-Agent Intelligence System

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
- [Quick Start](#quick-start)
- [Production Deployment](#production-deployment)
- [Monitoring Setup](#monitoring-setup)
- [Security Configuration](#security-configuration)
- [Scaling Guidelines](#scaling-guidelines)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### System Requirements

| Component | Minimum | Recommended | Production |
|-----------|---------|-------------|------------|
| **CPU** | 4 cores | 8 cores | 16+ cores |
| **RAM** | 8 GB | 16 GB | 32+ GB |
| **Storage** | 20 GB SSD | 50 GB SSD | 100+ GB NVMe |
| **Network** | 100 Mbps | 1 Gbps | 10 Gbps |
| **OS** | Ubuntu 20.04+ | Ubuntu 22.04 | Ubuntu 22.04 LTS |

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)
- Node.js 18+ (for web dashboard)

### API Keys (Optional but Recommended)

```bash
# Create .env file
cp .env.example .env

# Add your API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...
# ... add other provider keys
```

## 🚀 Deployment Options

### 1. Docker Compose (Recommended)

Perfect for single-server deployments and testing.

```bash
# Clone repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Setup environment
cp .env.example .env
nano .env  # Configure your settings

# Launch all services
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs -f
```

### 2. Kubernetes Deployment

For production and multi-node deployments.

```bash
# Apply configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/config/
kubectl apply -f k8s/storage/
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/

# Verify deployment
kubectl get pods -n amas
kubectl get svc -n amas
```

### 3. Cloud Deployment

#### AWS
```bash
# Use provided CloudFormation template
aws cloudformation create-stack \
  --stack-name amas-platform \
  --template-body file://aws/cloudformation/amas-stack.yaml \
  --parameters file://aws/parameters.json \
  --capabilities CAPABILITY_IAM
```

#### Azure
```bash
# Deploy using ARM template
az deployment group create \
  --resource-group amas-rg \
  --template-file azure/template.json \
  --parameters azure/parameters.json
```

#### GCP
```bash
# Deploy using Terraform
cd terraform/gcp
terraform init
terraform plan
terraform apply
```

### 4. Bare Metal Installation

For maximum control and performance.

```bash
# Install system dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip \
  postgresql-15 redis-server nginx \
  prometheus grafana nodejs npm

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-monitoring.txt

# Setup database
sudo -u postgres createdb amas
sudo -u postgres createuser amas_user
python scripts/setup_database.py

# Configure services
sudo cp config/nginx/amas.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/amas.conf /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Start services
python -m amas.api.server &
python monitor-intelligence.py &
cd web && npm install && npm run build && npm start &
```

## 📊 Monitoring Setup

### Prometheus + Grafana Stack

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access dashboards
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090

# Import AMAS dashboards
cd monitoring/grafana/dashboards
./import-dashboards.sh
```

### Configure Alerts

```yaml
# prometheus/alerts.yml
groups:
  - name: amas_alerts
    rules:
      - alert: HighMemoryUsage
        expr: amas_memory_usage_bytes > 10737418240  # 10GB
        for: 5m
        annotations:
          summary: "High memory usage detected"
      
      - alert: AIProviderFailure
        expr: amas_ai_provider_errors_total > 10
        for: 2m
        annotations:
          summary: "AI provider experiencing failures"
      
      - alert: TaskQueueBacklog
        expr: amas_task_queue_size > 1000
        for: 10m
        annotations:
          summary: "Task queue backlog growing"
```

## 🔒 Security Configuration

### 1. Enable HTTPS

```bash
# Generate SSL certificates
certbot certonly --standalone -d your-domain.com

# Update nginx configuration
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

### 2. Configure Firewall

```bash
# UFW configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 3000/tcp  # Dashboard (internal only)
sudo ufw allow 8000/tcp  # API (internal only)
sudo ufw enable
```

### 3. Environment Variables

```bash
# Production .env
NODE_ENV=production
AMAS_ENV=production
DEBUG=false
LOG_LEVEL=warning

# Security settings
JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)
API_RATE_LIMIT=100
ENABLE_AUDIT_LOG=true

# Database
DATABASE_SSL=true
REDIS_PASSWORD=$(openssl rand -base64 16)
```

## 📈 Scaling Guidelines

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  amas-worker:
    image: amas/worker:latest
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '2'
          memory: 4G
    environment:
      - WORKER_ID={{.Task.Slot}}
      - REDIS_URL=redis://redis:6379
```

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created ON tasks(created_at);
CREATE INDEX idx_agents_type ON agents(agent_type);

-- Partition large tables
CREATE TABLE tasks_2025_q1 PARTITION OF tasks
FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
```

### Redis Configuration

```conf
# redis.conf for production
maxmemory 8gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
```

## 🔍 Health Checks

### API Health Endpoint
```bash
curl http://localhost:8000/health
```

### Component Status
```bash
# Check all services
./scripts/health-check.sh

# Individual checks
docker exec amas-api python -m amas.health
docker exec amas-redis redis-cli ping
docker exec amas-postgres pg_isready
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Memory Issues
```bash
# Check memory usage
docker stats
htop

# Increase memory limits
docker-compose down
# Edit docker-compose.yml memory limits
docker-compose up -d
```

#### 2. Database Connection Issues
```bash
# Test connection
psql -h localhost -U amas_user -d amas

# Check logs
docker logs amas-postgres
tail -f /var/log/postgresql/postgresql-15-main.log
```

#### 3. AI Provider Failures
```bash
# Check provider status
curl http://localhost:8000/api/providers/status

# Test specific provider
python scripts/test_provider.py --provider openai
```

### Debug Mode

```bash
# Enable debug logging
export AMAS_DEBUG=true
export LOG_LEVEL=debug

# Run with verbose output
docker-compose up  # without -d for live logs
```

### Performance Tuning

```bash
# Run performance tests
python tests/load/amas_load_test.py

# Analyze bottlenecks
python scripts/analyze_performance.py

# Generate optimization report
python scripts/optimize_config.py > optimization_report.md
```

## 🔄 Backup and Recovery

### Automated Backups

```bash
# Setup backup cron job
crontab -e
# Add: 0 2 * * * /opt/amas/scripts/backup.sh

# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec amas-postgres pg_dump -U amas_user amas > backup_$DATE.sql
aws s3 cp backup_$DATE.sql s3://amas-backups/
```

### Disaster Recovery

```bash
# Restore from backup
docker exec -i amas-postgres psql -U amas_user amas < backup_20251007.sql

# Restore Redis snapshot
docker cp redis_backup.rdb amas-redis:/data/dump.rdb
docker restart amas-redis
```

## 📝 Post-Deployment Checklist

- [ ] All services running (`docker-compose ps`)
- [ ] API accessible (`curl http://localhost:8000/health`)
- [ ] Dashboard loading (`http://localhost:3000`)
- [ ] Monitoring active (`http://localhost:3001`)
- [ ] SSL certificates valid
- [ ] Firewall configured
- [ ] Backups scheduled
- [ ] Alerts configured
- [ ] Performance baseline established
- [ ] Security scan completed

## 🆘 Support

- **Documentation**: [docs.amas.ai](https://docs.amas.ai)
- **Issues**: [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- **Community**: [Discord Server](https://discord.gg/amas)
- **Email**: support@amas.ai

---

*Remember: A well-deployed AMAS is a happy AMAS! 🎉*