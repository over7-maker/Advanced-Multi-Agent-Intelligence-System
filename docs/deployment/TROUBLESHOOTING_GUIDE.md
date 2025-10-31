# 🔧 AMAS Troubleshooting Guide

## Overview

This comprehensive troubleshooting guide provides step-by-step solutions for common issues encountered with the AMAS (Advanced Multi-Agent System) in production and staging environments.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Service Issues](#service-issues)
- [Database Problems](#database-problems)
- [Performance Issues](#performance-issues)
- [Network Problems](#network-problems)
- [Security Issues](#security-issues)
- [Monitoring and Logs](#monitoring-and-logs)
- [Emergency Procedures](#emergency-procedures)

## Quick Reference

### Essential Commands

```bash
# Check system status
./scripts/validate-deployment.sh --environment production --type basic

# View service logs
docker-compose -f docker-compose.production-blue.yml logs -f

# Restart services
docker-compose -f docker-compose.production-blue.yml restart

# Check resource usage
docker stats

# Access service shell
docker-compose -f docker-compose.production-blue.yml exec amas-blue bash
```

### Emergency Contacts

- **On-call Engineer**: +1-555-0123
- **DevOps Team**: devops@yourcompany.com
- **Security Team**: security@yourcompany.com
- **Slack Channel**: #amas-incidents

## Service Issues

### Service Won't Start

#### Symptoms
- Service shows "Exited" status
- Error messages in logs
- Health checks failing

#### Diagnosis

```bash
# Check service status
docker-compose -f docker-compose.production-blue.yml ps

# View service logs
docker-compose -f docker-compose.production-blue.yml logs service-name

# Check resource usage
docker stats service-name

# Check disk space
df -h

# Check memory usage
free -h
```

#### Common Causes and Solutions

**1. Insufficient Resources**
```bash
# Check available memory
free -h

# Check available disk space
df -h

# Clean up Docker resources
docker system prune -f
docker volume prune -f
```

**2. Port Conflicts**
```bash
# Check port usage
netstat -tulpn | grep :8000

# Kill process using port
sudo kill -9 $(lsof -t -i:8000)

# Restart service
docker-compose -f docker-compose.production-blue.yml restart service-name
```

**3. Configuration Errors**
```bash
# Validate configuration
docker-compose -f docker-compose.production-blue.yml config

# Check environment variables
docker-compose -f docker-compose.production-blue.yml exec service-name env

# Fix configuration and restart
docker-compose -f docker-compose.production-blue.yml up -d service-name
```

**4. Dependency Issues**
```bash
# Check dependency services
docker-compose -f docker-compose.production-blue.yml ps

# Start dependencies first
docker-compose -f docker-compose.production-blue.yml up -d postgres redis neo4j

# Wait for dependencies to be ready
sleep 30

# Start main service
docker-compose -f docker-compose.production-blue.yml up -d amas-blue
```

### Service Health Check Failures

#### Symptoms
- Service shows "Unhealthy" status
- Health check endpoints returning errors
- Service appears to be running but not responding

#### Diagnosis

```bash
# Check health endpoint directly
curl -f http://localhost:8000/health

# Check service logs
docker-compose -f docker-compose.production-blue.yml logs amas-blue

# Check service processes
docker-compose -f docker-compose.production-blue.yml exec amas-blue ps aux

# Check service configuration
docker-compose -f docker-compose.production-blue.yml exec amas-blue cat /app/config/app.conf
```

#### Solutions

**1. Database Connection Issues**
```bash
# Check database connectivity
docker-compose -f docker-compose.production-blue.yml exec postgres-blue pg_isready -U postgres

# Test database connection
docker-compose -f docker-compose.production-blue.yml exec amas-blue python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:password@postgres-blue:5432/amas')
print('Database connection successful')
"

# Restart database service
docker-compose -f docker-compose.production-blue.yml restart postgres-blue
```

**2. Redis Connection Issues**
```bash
# Check Redis connectivity
docker-compose -f docker-compose.production-blue.yml exec redis-blue redis-cli ping

# Test Redis connection
docker-compose -f docker-compose.production-blue.yml exec amas-blue python -c "
import redis
r = redis.Redis(host='redis-blue', port=6379, password='password')
print(r.ping())
"

# Restart Redis service
docker-compose -f docker-compose.production-blue.yml restart redis-blue
```

**3. Neo4j Connection Issues**
```bash
# Check Neo4j connectivity
docker-compose -f docker-compose.production-blue.yml exec neo4j-blue cypher-shell -u neo4j -p password "RETURN 1;"

# Test Neo4j connection
docker-compose -f docker-compose.production-blue.yml exec amas-blue python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://neo4j-blue:7687', auth=('neo4j', 'password'))
with driver.session() as session:
    result = session.run('RETURN 1')
    print(result.single()[0])
"

# Restart Neo4j service
docker-compose -f docker-compose.production-blue.yml restart neo4j-blue
```

## Database Problems

### Database Connection Errors

#### Symptoms
- "Connection refused" errors
- "Authentication failed" errors
- "Database does not exist" errors

#### Diagnosis

```bash
# Check database service status
docker-compose -f docker-compose.production-blue.yml ps postgres-blue

# Check database logs
docker-compose -f docker-compose.production-blue.yml logs postgres-blue

# Test database connectivity
docker-compose -f docker-compose.production-blue.yml exec postgres-blue pg_isready -U postgres

# Check database configuration
docker-compose -f docker-compose.production-blue.yml exec postgres-blue cat /var/lib/postgresql/data/postgresql.conf
```

#### Solutions

**1. Database Service Not Running**
```bash
# Start database service
docker-compose -f docker-compose.production-blue.yml up -d postgres-blue

# Wait for service to be ready
sleep 30

# Check service status
docker-compose -f docker-compose.production-blue.yml ps postgres-blue
```

**2. Authentication Issues**
```bash
# Check environment variables
docker-compose -f docker-compose.production-blue.yml exec postgres-blue env | grep POSTGRES

# Reset database password
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -c "ALTER USER postgres PASSWORD 'new_password';"

# Update application configuration
# Edit .env.production with new password
```

**3. Database Does Not Exist**
```bash
# Create database
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -c "CREATE DATABASE amas;"

# Run database migrations
docker-compose -f docker-compose.production-blue.yml exec amas-blue python -m alembic upgrade head
```

### Database Performance Issues

#### Symptoms
- Slow query responses
- High CPU usage
- Memory consumption issues
- Connection timeouts

#### Diagnosis

```bash
# Check database performance
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
"

# Check database size
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "
SELECT pg_size_pretty(pg_database_size('amas'));
"

# Check table sizes
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

#### Solutions

**1. Query Optimization**
```bash
# Analyze slow queries
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
"

# Update table statistics
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "ANALYZE;"

# Reindex tables
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "REINDEX DATABASE amas;"
```

**2. Resource Optimization**
```bash
# Check database configuration
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "
SELECT name, setting, unit 
FROM pg_settings 
WHERE name IN ('shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem');
"

# Optimize database configuration
# Edit postgresql.conf with optimized settings
```

## Performance Issues

### High CPU Usage

#### Symptoms
- System load average > 4.0
- CPU usage > 80%
- Slow response times
- Service timeouts

#### Diagnosis

```bash
# Check system load
uptime

# Check CPU usage
top
htop

# Check container CPU usage
docker stats

# Check specific service CPU usage
docker-compose -f docker-compose.production-blue.yml exec amas-blue top
```

#### Solutions

**1. Optimize Application Code**
```bash
# Check for infinite loops or inefficient algorithms
docker-compose -f docker-compose.production-blue.yml exec amas-blue python -c "
import cProfile
import pstats
# Profile application code
"

# Check for memory leaks
docker-compose -f docker-compose.production-blue.yml exec amas-blue python -c "
import psutil
import gc
print('Memory usage:', psutil.virtual_memory().percent)
print('Objects in memory:', len(gc.get_objects()))
"
```

**2. Scale Services**
```bash
# Scale application service
docker-compose -f docker-compose.production-blue.yml up -d --scale amas-blue=3

# Check load balancing
docker-compose -f docker-compose.production-blue.yml ps
```

### High Memory Usage

#### Symptoms
- Memory usage > 80%
- Out of memory errors
- System swapping
- Service crashes

#### Diagnosis

```bash
# Check memory usage
free -h

# Check container memory usage
docker stats

# Check specific service memory usage
docker-compose -f docker-compose.production-blue.yml exec amas-blue python -c "
import psutil
print('Memory usage:', psutil.virtual_memory().percent)
print('Available memory:', psutil.virtual_memory().available)
"
```

#### Solutions

**1. Optimize Memory Usage**
```bash
# Check for memory leaks
docker-compose -f docker-compose.production-blue.yml exec amas-blue python -c "
import gc
import sys
print('Objects before GC:', len(gc.get_objects()))
gc.collect()
print('Objects after GC:', len(gc.get_objects()))
"

# Restart service to clear memory
docker-compose -f docker-compose.production-blue.yml restart amas-blue
```

**2. Increase Memory Limits**
```bash
# Update docker-compose.yml with higher memory limits
# Edit docker-compose.production-blue.yml
# Update memory limits in deploy.resources.limits.memory
```

### Slow Response Times

#### Symptoms
- API response times > 2 seconds
- User complaints about slowness
- Timeout errors
- Queue buildup

#### Diagnosis

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Check database query performance
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "
SELECT 
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Check network latency
ping -c 10 localhost
```

#### Solutions

**1. Database Optimization**
```bash
# Create indexes for slow queries
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
"

# Update table statistics
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "ANALYZE;"
```

**2. Caching Optimization**
```bash
# Check Redis cache usage
docker-compose -f docker-compose.production-blue.yml exec redis-blue redis-cli info memory

# Clear cache if needed
docker-compose -f docker-compose.production-blue.yml exec redis-blue redis-cli flushall
```

## Network Problems

### Connection Refused Errors

#### Symptoms
- "Connection refused" errors
- Service unreachable
- Network timeouts
- DNS resolution failures

#### Diagnosis

```bash
# Check service status
docker-compose -f docker-compose.production-blue.yml ps

# Check port binding
netstat -tulpn | grep :8000

# Test connectivity
telnet localhost 8000

# Check DNS resolution
nslookup postgres-blue
```

#### Solutions

**1. Service Not Running**
```bash
# Start service
docker-compose -f docker-compose.production-blue.yml up -d service-name

# Check service logs
docker-compose -f docker-compose.production-blue.yml logs service-name
```

**2. Port Conflicts**
```bash
# Find process using port
lsof -i :8000

# Kill conflicting process
sudo kill -9 $(lsof -t -i:8000)

# Restart service
docker-compose -f docker-compose.production-blue.yml restart service-name
```

### DNS Resolution Issues

#### Symptoms
- "Name or service not known" errors
- Service discovery failures
- Inter-service communication issues

#### Diagnosis

```bash
# Test DNS resolution
nslookup postgres-blue
nslookup redis-blue
nslookup neo4j-blue

# Check Docker network
docker network ls
docker network inspect amas-production-blue-network
```

#### Solutions

**1. Recreate Network**
```bash
# Stop services
docker-compose -f docker-compose.production-blue.yml down

# Remove network
docker network rm amas-production-blue-network

# Start services
docker-compose -f docker-compose.production-blue.yml up -d
```

**2. Use IP Addresses**
```bash
# Get service IP addresses
docker-compose -f docker-compose.production-blue.yml exec amas-blue nslookup postgres-blue

# Update configuration with IP addresses if needed
```

## Security Issues

### Authentication Failures

#### Symptoms
- "Authentication failed" errors
- "Invalid credentials" errors
- JWT token errors
- Session timeouts

#### Diagnosis

```bash
# Check authentication logs
docker-compose -f docker-compose.production-blue.yml logs amas-blue | grep -i auth

# Check JWT token validity
docker-compose -f docker-compose.production-blue.yml exec amas-blue python -c "
import jwt
import os
token = 'your-jwt-token'
secret = os.getenv('JWT_SECRET_KEY')
try:
    decoded = jwt.decode(token, secret, algorithms=['HS256'])
    print('Token is valid')
except jwt.ExpiredSignatureError:
    print('Token has expired')
except jwt.InvalidTokenError:
    print('Token is invalid')
"
```

#### Solutions

**1. Reset Authentication**
```bash
# Restart authentication service
docker-compose -f docker-compose.production-blue.yml restart amas-blue

# Clear authentication cache
docker-compose -f docker-compose.production-blue.yml exec redis-blue redis-cli flushdb
```

**2. Update Credentials**
```bash
# Update JWT secret
# Edit .env.production with new JWT_SECRET_KEY

# Restart services
docker-compose -f docker-compose.production-blue.yml restart amas-blue
```

### SSL/TLS Issues

#### Symptoms
- SSL handshake failures
- Certificate errors
- HTTPS connection issues

#### Diagnosis

```bash
# Check SSL certificate
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect localhost:443

# Check certificate expiration
openssl x509 -in nginx/ssl/cert.pem -noout -dates
```

#### Solutions

**1. Update Certificate**
```bash
# Place new certificate files
cp new-cert.pem nginx/ssl/cert.pem
cp new-key.pem nginx/ssl/key.pem

# Restart nginx
docker-compose -f docker-compose.production-blue.yml restart nginx
```

**2. Regenerate Self-Signed Certificate**
```bash
# Generate new self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes

# Restart nginx
docker-compose -f docker-compose.production-blue.yml restart nginx
```

## Monitoring and Logs

### Log Analysis

#### Common Log Locations

```bash
# Application logs
docker-compose -f docker-compose.production-blue.yml logs amas-blue

# Database logs
docker-compose -f docker-compose.production-blue.yml logs postgres-blue

# Redis logs
docker-compose -f docker-compose.production-blue.yml logs redis-blue

# Neo4j logs
docker-compose -f docker-compose.production-blue.yml logs neo4j-blue

# Nginx logs
docker-compose -f docker-compose.production-blue.yml logs nginx
```

#### Log Analysis Commands

```bash
# Search for errors
docker-compose -f docker-compose.production-blue.yml logs amas-blue | grep -i error

# Search for specific patterns
docker-compose -f docker-compose.production-blue.yml logs amas-blue | grep "database connection"

# Follow logs in real-time
docker-compose -f docker-compose.production-blue.yml logs -f amas-blue

# Export logs to file
docker-compose -f docker-compose.production-blue.yml logs amas-blue > amas-logs.txt
```

### Monitoring Issues

#### Symptoms
- Missing metrics
- Dashboard not updating
- Alerts not firing
- Performance data unavailable

#### Diagnosis

```bash
# Check Prometheus status
curl http://localhost:9090/api/v1/query?query=up

# Check Grafana status
curl http://localhost:3001/api/health

# Check metrics endpoint
curl http://localhost:8000/metrics
```

#### Solutions

**1. Restart Monitoring Services**
```bash
# Restart Prometheus
docker-compose -f docker-compose.production-blue.yml restart prometheus

# Restart Grafana
docker-compose -f docker-compose.production-blue.yml restart grafana
```

**2. Check Configuration**
```bash
# Validate Prometheus configuration
docker-compose -f docker-compose.production-blue.yml exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Check Grafana configuration
docker-compose -f docker-compose.production-blue.yml exec grafana grafana-cli admin reset-admin-password newpassword
```

## Emergency Procedures

### Complete System Failure

#### Immediate Actions

```bash
# 1. Check system status
./scripts/validate-deployment.sh --environment production --type basic

# 2. Check resource usage
df -h
free -h
docker system df

# 3. Check service status
docker-compose -f docker-compose.production-blue.yml ps

# 4. Check logs
docker-compose -f docker-compose.production-blue.yml logs --tail=100
```

#### Recovery Steps

```bash
# 1. Stop all services
docker-compose -f docker-compose.production-blue.yml down

# 2. Clean up resources
docker system prune -f
docker volume prune -f

# 3. Restart services
docker-compose -f docker-compose.production-blue.yml up -d

# 4. Wait for services to be ready
sleep 60

# 5. Validate system
./scripts/validate-deployment.sh --environment production --type comprehensive
```

### Data Corruption

#### Immediate Actions

```bash
# 1. Stop affected services
docker-compose -f docker-compose.production-blue.yml stop amas-blue

# 2. Check data integrity
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "SELECT 1;"

# 3. Check backup availability
ls -la backups/production-*
```

#### Recovery Steps

```bash
# 1. Restore from backup
./scripts/restore.sh --environment production --backup latest --type database --force

# 2. Validate data integrity
./scripts/validate-data-integrity.sh --environment production

# 3. Restart services
docker-compose -f docker-compose.production-blue.yml up -d

# 4. Validate system
./scripts/validate-deployment.sh --environment production --type comprehensive
```

### Security Breach

#### Immediate Actions

```bash
# 1. Isolate system
docker-compose -f docker-compose.production-blue.yml down

# 2. Preserve evidence
docker-compose -f docker-compose.production-blue.yml logs > security-incident-logs.txt

# 3. Check for unauthorized access
docker-compose -f docker-compose.production-blue.yml exec postgres-blue psql -U postgres -d amas -c "
SELECT * FROM pg_stat_activity WHERE state = 'active';
"
```

#### Recovery Steps

```bash
# 1. Restore from clean backup
./scripts/restore.sh --environment production --backup clean-backup --type full --force

# 2. Update security configurations
./scripts/update-security-config.sh --environment production

# 3. Rotate all secrets
./scripts/rotate-secrets.sh --environment production

# 4. Restart services
docker-compose -f docker-compose.production-blue.yml up -d

# 5. Validate security
./scripts/security-scan.sh --environment production
```

## Prevention and Best Practices

### Regular Maintenance

```bash
# Daily checks
./scripts/daily-health-check.sh --environment production

# Weekly maintenance
./scripts/weekly-maintenance.sh --environment production

# Monthly optimization
./scripts/monthly-optimization.sh --environment production
```

### Monitoring Setup

```bash
# Set up monitoring alerts
./scripts/setup-monitoring-alerts.sh --environment production

# Configure log rotation
./scripts/setup-log-rotation.sh --environment production

# Set up backup verification
./scripts/setup-backup-verification.sh --environment production
```

### Documentation Updates

- Update troubleshooting procedures
- Document new issues and solutions
- Maintain knowledge base
- Conduct regular training

---

**Last Updated**: January 2024  
**Version**: 1.0  
**Maintainer**: DevOps Team  
**Next Review**: February 2024