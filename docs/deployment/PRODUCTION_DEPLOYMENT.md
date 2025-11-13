# 🚀 AMAS Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying AMAS in a production environment. It covers security hardening, performance optimization, high availability setup, and operational best practices.

## 📋 Table of Contents

1. [Pre-Production Checklist](#pre-production-checklist)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Security Configuration](#security-configuration)
4. [High Availability Setup](#high-availability-setup)
5. [Performance Optimization](#performance-optimization)
6. [Intelligent Autoscaling](#intelligent-autoscaling)
7. [Monitoring & Alerting](#monitoring--alerting)
8. [Backup & Recovery](#backup--recovery)
9. [Operational Procedures](#operational-procedures)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance](#maintenance)

---

## ✅ Pre-Production Checklist

### Infrastructure Readiness
- [ ] **Servers provisioned** with required specifications
- [ ] **Network configured** with proper segmentation
- [ ] **Load balancers** configured and tested
- [ ] **SSL certificates** obtained and installed
- [ ] **DNS records** configured correctly
- [ ] **Firewall rules** implemented and tested
- [ ] **VPN access** configured for management
- [ ] **Backup systems** configured and tested

### Security Preparation
- [ ] **Security audit** completed
- [ ] **Penetration testing** performed
- [ ] **Compliance review** passed
- [ ] **API keys** rotated and secured
- [ ] **MFA enabled** for all admin accounts
- [ ] **Access controls** configured
- [ ] **Audit logging** enabled
- [ ] **Encryption** configured for data at rest and in transit

### Application Readiness
- [ ] **Code review** completed
- [ ] **Performance testing** passed
- [ ] **Load testing** completed
- [ ] **Security scanning** passed
- [ ] **Dependencies** updated and scanned
- [ ] **Configuration** reviewed for production
- [ ] **Database migrations** tested
- [ ] **Rollback procedures** documented

### Operational Readiness
- [ ] **Monitoring** configured and tested
- [ ] **Alerting** rules configured
- [ ] **Runbooks** documented
- [ ] **Incident response** plan ready
- [ ] **Team training** completed
- [ ] **Support rotation** scheduled
- [ ] **Documentation** up to date
- [ ] **SLAs** defined and agreed

---

## 🏗️ Infrastructure Requirements

### Minimum Production Requirements

| Component | Specification | Quantity | Notes |
|-----------|---------------|----------|-------|
| **API Servers** | 8 vCPU, 32GB RAM, 100GB SSD | 3+ | Behind load balancer |
| **Worker Nodes** | 16 vCPU, 64GB RAM, 200GB SSD | 5+ | For agent processing |
| **Database** | 32 vCPU, 128GB RAM, 1TB SSD | 2 (Primary + Replica) | PostgreSQL 14+ |
| **Cache** | 8 vCPU, 32GB RAM | 3 (Cluster) | Redis 7+ |
| **Load Balancer** | 4 vCPU, 8GB RAM | 2 (Active/Passive) | Nginx or HAProxy |
| **Monitoring** | 8 vCPU, 32GB RAM, 500GB SSD | 1 | Prometheus + Grafana |

### Network Architecture

```
Internet
    │
    ├─── CDN (CloudFlare/Akamai)
    │
    ├─── WAF (Web Application Firewall)
    │
    ├─── Load Balancer (Layer 7)
    │         │
    │    ┌────┴────┬────────┬────────┐
    │    │         │        │        │
    │   API-1    API-2    API-3   API-N
    │    │         │        │        │
    │    └────┬────┴────────┴────────┘
    │         │
    ├─── Internal Load Balancer
    │         │
    │    ┌────┴────┬────────┬────────┐
    │    │         │        │        │
    │  Worker-1 Worker-2 Worker-3 Worker-N
    │    │         │        │        │
    │    └────┬────┴────────┴────────┘
    │         │
    ├─── Data Layer
    │    ├─── PostgreSQL (Primary)
    │    ├─── PostgreSQL (Replica)
    │    ├─── Redis Cluster
    │    └─── Object Storage
    │
    └─── Management Network
         ├─── Monitoring Stack
         ├─── Log Aggregation
         └─── Backup Systems
```

---

## 🔒 Security Configuration

### SSL/TLS Configuration

```nginx
# /etc/nginx/conf.d/ssl.conf
ssl_certificate /etc/ssl/certs/amas.crt;
ssl_certificate_key /etc/ssl/private/amas.key;

# Modern configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

# HSTS
add_header Strict-Transport-Security "max-age=63072000" always;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/ssl/certs/chain.pem;
```

### Firewall Rules

```bash
#!/bin/bash
# Production firewall configuration

# Reset rules
iptables -F
iptables -X

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Loopback
iptables -A INPUT -i lo -j ACCEPT

# Established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# SSH (restricted to management network)
iptables -A INPUT -p tcp --dport 22 -s 10.0.100.0/24 -j ACCEPT

# HTTP/HTTPS (public)
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# API ports (internal only)
iptables -A INPUT -p tcp --dport 8000 -s 10.0.0.0/16 -j ACCEPT

# Database (internal only)
iptables -A INPUT -p tcp --dport 5432 -s 10.0.2.0/24 -j ACCEPT

# Redis (internal only)
iptables -A INPUT -p tcp --dport 6379 -s 10.0.2.0/24 -j ACCEPT

# Monitoring
iptables -A INPUT -p tcp --dport 9090 -s 10.0.100.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 3000 -s 10.0.100.0/24 -j ACCEPT

# Save rules
iptables-save > /etc/iptables/rules.v4
```

### Secrets Management

```yaml
# HashiCorp Vault configuration
storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/cert.pem"
  tls_key_file  = "/opt/vault/tls/key.pem"
}

seal "awskms" {
  region = "us-east-1"
  kms_key_id = "alias/vault-unseal"
}

ui = true
```

---

## 🔄 High Availability Setup

### Database HA Configuration

```sql
-- PostgreSQL Primary configuration
-- postgresql.conf
listen_addresses = '*'
max_connections = 500
shared_buffers = 32GB
effective_cache_size = 96GB
work_mem = 128MB
maintenance_work_mem = 2GB

# Replication
wal_level = replica
max_wal_senders = 10
wal_keep_segments = 64
hot_standby = on

# Archive
archive_mode = on
archive_command = 'rsync -a %p backup@backup-server:/backups/postgres/%f'
```

```sql
-- Streaming replication setup
-- On replica
pg_basebackup -h primary-server -D /var/lib/postgresql/14/main -U replicator -v -P -W

-- recovery.conf
standby_mode = 'on'
primary_conninfo = 'host=primary-server port=5432 user=replicator'
trigger_file = '/tmp/postgresql.trigger'
```

### Redis Cluster Configuration

```conf
# redis.conf for cluster nodes
port 7000
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes
maxmemory 16gb
maxmemory-policy allkeys-lru

# Setup cluster
redis-cli --cluster create \
  node1:7000 node2:7000 node3:7000 \
  node4:7000 node5:7000 node6:7000 \
  --cluster-replicas 1
```

### Load Balancer HA

```conf
# keepalived.conf for VRRP
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass SecurePassword123
    }
    virtual_ipaddress {
        192.168.1.100/24
    }
}
```

---

## ⚡ Performance Optimization

### System Tuning

```bash
# /etc/sysctl.conf
# Network optimizations
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200

# Memory optimizations
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# File system
fs.file-max = 2097152
fs.nr_open = 1048576
```

### Application Optimization

```python
# gunicorn_config.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
timeout = 30
graceful_timeout = 30
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### Database Optimization

```sql
-- Performance indexes
CREATE INDEX CONCURRENTLY idx_tasks_user_status 
    ON tasks(user_id, status) 
    WHERE status IN ('pending', 'processing');

CREATE INDEX CONCURRENTLY idx_results_created_at 
    ON results(created_at DESC) 
    INCLUDE (task_id, status);

-- Table partitioning
CREATE TABLE tasks_2025_q1 PARTITION OF tasks
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

-- Connection pooling with PgBouncer
[databases]
amas = host=localhost port=5432 dbname=amas

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5
```

---

## ⚡ Intelligent Autoscaling

AMAS includes comprehensive intelligent autoscaling infrastructure for production workloads. This section covers KEDA-based autoscaling, semantic caching, and resilience patterns.

> **📚 Complete Guide**: See [Performance Scaling Guide](../PERFORMANCE_SCALING_GUIDE.md) for comprehensive documentation.

### KEDA Autoscaling Setup

**Prerequisites:**
- Kubernetes 1.20+
- KEDA 2.0+ operator installed
- Prometheus available for metrics
- Redis cluster (for caching and rate limiting)

**Deployment:**
```bash
# Apply KEDA autoscaling configuration
kubectl apply -f k8s/scaling/keda-scaler.yaml

# Verify installation
kubectl get scaledobjects -n amas-prod
kubectl describe scaledobject amas-orchestrator-scaler -n amas-prod
```

**Scaling Triggers:**
- HTTP Request Rate: >15 RPS per pod (activation at 5 RPS)
- Queue Depth: >25 queued items (activation at 10 items)
- High Latency: P95 latency >1.0 seconds
- Resource Pressure: CPU >70% OR memory >80%

**Scaling Behavior:**
- Min Replicas: 2 (high availability)
- Max Replicas: 50 (safety limit)
- Scale Up: Fast (up to 100% increase per minute, max 5 pods)
- Scale Down: Conservative (max 10% decrease per minute, max 2 pods)

### Semantic Caching

Enable semantic caching for 30%+ speed improvement on repeated queries:

```python
from src.amas.services.semantic_cache_service import get_semantic_cache

# Initialize semantic cache
cache = await get_semantic_cache(
    redis_url="redis://redis-cluster:6379/0",
    similarity_threshold=0.85
)

# Use in agent calls
cached = await cache.get(query, agent_id="research_agent", use_semantic=True)
if cached:
    return cached  # 30%+ faster than API call
```

**Requirements:**
- Redis with TLS 1.3+ encryption
- Authentication enabled
- RedisVL or external vector search for similarity matching
- Network policies restricting access

### Resilience Patterns

**Circuit Breakers:**
```python
from src.amas.services.circuit_breaker_service import get_circuit_breaker_service

breaker_service = get_circuit_breaker_service()
breaker = breaker_service.get_breaker("external_api")

# Protected API call
result = await breaker.call(external_api_function, arg1, arg2)
```

**Rate Limiting:**
```python
from src.amas.services.rate_limiting_service import get_rate_limiting_service

rate_limiter = await get_rate_limiting_service()

# Check before processing
result = await rate_limiter.check_rate_limit(user_id="user123")
if not result.allowed:
    return {"error": "rate_limit_exceeded", "retry_after": result.retry_after}
```

**Request Deduplication:**
```python
from src.amas.services.request_deduplication_service import get_deduplication_service

dedup = get_deduplication_service()

# Eliminate duplicate concurrent requests
result = await dedup.deduplicate(
    {"query": query, "user": user_id},
    expensive_llm_call
)
```

### Cost Optimization

Track and optimize costs automatically:

```python
from src.amas.services.cost_tracking_service import get_cost_tracking_service

cost_tracker = await get_cost_tracking_service(daily_budget_usd=100.0)

# Track request costs
await cost_tracker.record_request(
    request_id="req_123",
    provider="openai",
    model="gpt-4",
    tokens_input=1000,
    tokens_output=500,
    latency_ms=2000,
    success=True
)

# Get optimization recommendations
recommendations = await cost_tracker.get_optimization_recommendations()
```

### Load Testing

Run comprehensive load tests to validate scaling:

```bash
# List available scenarios
python scripts/run_load_test.py list

# Run specific test
python scripts/run_load_test.py run research_agent_baseline

# Run all scenarios
python scripts/run_load_test.py run-all
```

**Test Scenarios:**
- Baseline: 8 concurrent users, 120s duration
- Stress: 15 concurrent users, linear ramp-up
- Spike: Traffic bursts 4x normal load
- Peak: 25 concurrent users, multi-agent workflows

### Monitoring Scaling

Track scaling events and effectiveness:

```python
from src.amas.services.scaling_metrics_service import get_scaling_metrics_service

scaling_metrics = get_scaling_metrics_service()

# Get scaling statistics
stats = scaling_metrics.get_scaling_stats(component="orchestrator", hours=24)
print(f"Scale ups: {stats['scale_ups']}")
print(f"Scale downs: {stats['scale_downs']}")

# Get recent events
events = scaling_metrics.get_recent_events(component="orchestrator", limit=10)
```

**Prometheus Metrics:**
- `amas_scaling_events_total` - Total scaling events
- `amas_current_replicas` - Current replica count
- `amas_scaling_duration_seconds` - Scaling operation duration
- `amas_scaling_effectiveness` - Requests per replica

### Best Practices

1. **Configure Appropriate Thresholds**
   - CPU: 60-70% for most workloads
   - Memory: 70-80% for memory-intensive workloads
   - Queue Depth: Based on average processing time

2. **Enable Semantic Caching**
   - Use for repeated or similar queries
   - Configure appropriate similarity threshold (0.85 recommended)
   - Monitor cache hit rates

3. **Implement Circuit Breakers**
   - Protect all external API calls
   - Configure appropriate failure thresholds
   - Monitor circuit breaker states

4. **Set Up Rate Limiting**
   - Configure per-user quotas
   - Use sliding window algorithm
   - Monitor rate limit violations

5. **Track Costs**
   - Monitor token usage and API costs
   - Set daily budgets
   - Review optimization recommendations

---

## 📊 Monitoring & Alerting

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    environment: 'production'
    region: 'us-east-1'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts/*.yml'

scrape_configs:
  - job_name: 'amas-api'
    static_configs:
      - targets: ['api1:9090', 'api2:9090', 'api3:9090']
    
  - job_name: 'amas-workers'
    static_configs:
      - targets: ['worker1:9090', 'worker2:9090', 'worker3:9090']
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Alert Rules

```yaml
# alerts/amas.yml
groups:
  - name: amas_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(amas_api_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, amas_api_latency_seconds) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High API response time"
          description: "95th percentile response time is {{ $value }} seconds"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: amas_db_connections_active / amas_db_connections_max > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "{{ $value }}% of connections in use"
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "AMAS Production Dashboard",
    "panels": [
      {
        "title": "API Request Rate",
        "targets": [{
          "expr": "rate(amas_api_requests_total[5m])"
        }]
      },
      {
        "title": "Response Time (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, amas_api_latency_seconds)"
        }]
      },
      {
        "title": "Active Tasks",
        "targets": [{
          "expr": "amas_tasks_active"
        }]
      },
      {
        "title": "AI Provider Health",
        "targets": [{
          "expr": "amas_ai_provider_health"
        }]
      }
    ]
  }
}
```

---

## 💾 Backup & Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh - Production backup script

BACKUP_DIR="/backup/amas/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U amas -d amas -F custom -f $BACKUP_DIR/amas_db.dump

# Redis backup
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis.rdb

# Application data
rsync -av /var/lib/amas/ $BACKUP_DIR/app_data/

# Configuration files
tar -czf $BACKUP_DIR/configs.tar.gz /etc/amas/

# Encrypt backups
gpg --encrypt --recipient backup@amas.com $BACKUP_DIR/*

# Upload to S3
aws s3 sync $BACKUP_DIR s3://amas-backups/production/

# Cleanup old backups (keep 30 days)
find /backup/amas -type d -mtime +30 -exec rm -rf {} \;
```

### Recovery Procedures

```bash
#!/bin/bash
# restore.sh - Disaster recovery script

RESTORE_DATE=$1
BACKUP_DIR="/backup/amas/$RESTORE_DATE"

# Stop services
systemctl stop amas-api amas-worker

# Restore database
pg_restore -h localhost -U amas -d amas_restore $BACKUP_DIR/amas_db.dump
psql -c "ALTER DATABASE amas RENAME TO amas_old;"
psql -c "ALTER DATABASE amas_restore RENAME TO amas;"

# Restore Redis
systemctl stop redis
cp $BACKUP_DIR/redis.rdb /var/lib/redis/dump.rdb
chown redis:redis /var/lib/redis/dump.rdb
systemctl start redis

# Restore application data
rsync -av $BACKUP_DIR/app_data/ /var/lib/amas/

# Start services
systemctl start amas-api amas-worker

# Verify
curl http://localhost:8000/health
```

---

## 📋 Operational Procedures

### Deployment Process

```bash
#!/bin/bash
# deploy.sh - Zero-downtime deployment

VERSION=$1
HEALTH_CHECK_URL="http://localhost:8000/health"

# Pre-deployment checks
./run_tests.sh
./security_scan.sh

# Blue-green deployment
echo "Deploying version $VERSION"

# Start new version
docker run -d --name amas-api-$VERSION \
  -p 8001:8000 \
  amas/api:$VERSION

# Health check
for i in {1..30}; do
  if curl -f $HEALTH_CHECK_URL:8001; then
    echo "New version healthy"
    break
  fi
  sleep 2
done

# Switch traffic
nginx -s reload

# Stop old version
docker stop amas-api-old
docker rm amas-api-old

echo "Deployment complete"
```

### Scaling Procedures

```bash
# Scale up workers
kubectl scale deployment amas-worker --replicas=10

# Auto-scaling configuration
kubectl autoscale deployment amas-api \
  --min=3 \
  --max=20 \
  --cpu-percent=70
```

### Maintenance Mode

```nginx
# maintenance.conf
location / {
    if (-f /var/www/maintenance.flag) {
        return 503;
    }
    proxy_pass http://amas_backend;
}

error_page 503 @maintenance;
location @maintenance {
    root /var/www/maintenance;
    rewrite ^(.*)$ /index.html break;
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Check memory usage
ps aux --sort=-%mem | head -20

# Check for memory leaks
valgrind --leak-check=full python -m src.amas.main

# Force garbage collection
echo 3 > /proc/sys/vm/drop_caches
```

#### Database Performance
```sql
-- Check slow queries
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check blocking queries
SELECT pid, usename, query, state
FROM pg_stat_activity
WHERE state != 'idle'
AND query_start < NOW() - INTERVAL '1 minute';

-- Kill blocking query
SELECT pg_terminate_backend(pid);
```

#### API Latency
```bash
# Check connection pool
curl http://localhost:8000/metrics | grep connection

# Check worker queue depth
redis-cli llen celery

# Profile endpoint
python -m cProfile -o profile.out src/amas/api/app.py
```

---

## 🔄 Maintenance

### Regular Maintenance Tasks

#### Daily
- [ ] Check system alerts
- [ ] Review error logs
- [ ] Verify backup completion
- [ ] Check disk usage
- [ ] Monitor performance metrics

#### Weekly
- [ ] Security scan
- [ ] Database maintenance (VACUUM, ANALYZE)
- [ ] Review capacity planning
- [ ] Update documentation
- [ ] Test recovery procedures

#### Monthly
- [ ] Security patches
- [ ] Performance review
- [ ] Capacity planning
- [ ] Disaster recovery drill
- [ ] Team training

### Database Maintenance

```sql
-- Weekly maintenance
VACUUM ANALYZE;

-- Monthly maintenance
REINDEX DATABASE amas;

-- Quarterly maintenance
CLUSTER tasks USING idx_tasks_created_at;
```

### Log Rotation

```conf
# /etc/logrotate.d/amas
/var/log/amas/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 amas amas
    sharedscripts
    postrotate
        systemctl reload amas-api
    endscript
}
```

---

## 📊 Performance Benchmarks

### Expected Performance Metrics

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| **API Response Time (p95)** | < 200ms | < 500ms | > 1s |
| **Throughput** | > 1000 req/s | > 500 req/s | < 100 req/s |
| **Error Rate** | < 0.1% | < 1% | > 5% |
| **Availability** | 99.99% | 99.9% | < 99% |
| **Task Success Rate** | > 99% | > 95% | < 90% |
| **AI Provider Success** | > 99.9% | > 99% | < 95% |

---

## 🚨 Emergency Procedures

### Incident Response

1. **Assess** - Determine severity and impact
2. **Contain** - Prevent further damage
3. **Communicate** - Notify stakeholders
4. **Remediate** - Fix the issue
5. **Document** - Record actions taken
6. **Review** - Post-mortem analysis

### Emergency Contacts

- **On-Call Engineer**: +1-xxx-xxx-xxxx
- **Infrastructure Team**: infra@amas.com
- **Security Team**: security@amas.com
- **Management**: escalation@amas.com

---

**Remember**: Always test changes in staging before applying to production!

**Last Updated**: January 2025  
**Version**: 1.1.0  
**Approved By**: DevOps Team