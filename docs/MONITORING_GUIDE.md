# AMAS Monitoring Guide

## Overview

This guide provides comprehensive information about monitoring the AMAS (Advanced Multi-Agent Intelligence System) in production environments. The monitoring system includes metrics collection, logging, alerting, and dashboards.

## Table of Contents

1. [Architecture](#architecture)
2. [Metrics Collection](#metrics-collection)
3. [Logging](#logging)
4. [Health Checks](#health-checks)
5. [Dashboards](#dashboards)
6. [Alerting](#alerting)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Architecture

The AMAS monitoring system is built on:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: Kubernetes-ready health and readiness endpoints
- **Circuit Breakers**: Fault tolerance for external services
- **Audit Logging**: Security and compliance tracking

## Metrics Collection

### Prometheus Metrics

AMAS exposes comprehensive metrics in Prometheus format:

#### HTTP Metrics
- `http_requests_total`: Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds`: Request duration histogram
- `http_request_size_bytes`: Request size histogram
- `http_response_size_bytes`: Response size histogram

#### Authentication Metrics
- `auth_attempts_total`: Authentication attempts by result and method
- `auth_failures_total`: Authentication failures by reason and IP
- `active_sessions`: Current active user sessions

#### Agent Metrics
- `agents_total`: Total agents by status
- `agent_executions_total`: Agent executions by agent ID and status
- `agent_execution_duration_seconds`: Agent execution duration

#### Task Metrics
- `tasks_total`: Total tasks by status and priority
- `task_duration_seconds`: Task execution duration
- `tasks_in_progress`: Current tasks in progress

#### System Metrics
- `system_uptime_seconds`: System uptime
- `system_memory_usage_bytes`: Memory usage by type
- `system_cpu_usage_percent`: CPU usage percentage

#### Database Metrics
- `database_connections_active`: Active database connections
- `database_queries_total`: Database queries by operation and status
- `database_query_duration_seconds`: Query duration

#### Cache Metrics
- `cache_operations_total`: Cache operations by type and status
- `cache_hit_ratio`: Cache hit ratio

#### Error Metrics
- `errors_total`: Total errors by type and component
- `rate_limit_exceeded_total`: Rate limit violations

### Metrics Endpoint

Metrics are available at: `http://localhost:8000/metrics`

## Logging

### Structured Logging

AMAS uses structured JSON logging with correlation IDs for better observability:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "User authentication successful",
  "correlation_id": "abc123-def456",
  "user_id": "user123",
  "session_id": "sess789",
  "service": "amas",
  "component": "authentication",
  "action": "login",
  "metadata": {
    "username": "john.doe",
    "ip_address": "192.168.1.100"
  },
  "tags": ["authentication", "security"]
}
```

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about system operation
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors requiring immediate attention

### Log Files

- Main application logs: `/app/logs/amas.log`
- Audit logs: `/app/logs/amas_audit.log`
- Error logs: `/app/logs/amas_error.log`

## Health Checks

### Health Endpoint

**URL**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": 1642248600.123,
  "version": "1.0.0",
  "uptime": 3600.5,
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "neo4j": "healthy",
    "authentication": "healthy"
  },
  "metrics": {
    "memory_usage_percent": 45.2,
    "cpu_usage_percent": 12.8,
    "memory_available_gb": 2.1
  },
  "checks": [
    {
      "name": "database",
      "status": "pass",
      "message": "Database connection successful"
    }
  ]
}
```

### Readiness Endpoint

**URL**: `GET /ready`

**Response**:
```json
{
  "status": "ready",
  "timestamp": 1642248600.123,
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "neo4j": "healthy"
  }
}
```

## Dashboards

### Grafana Dashboard

The AMAS Grafana dashboard provides comprehensive system monitoring:

#### Panels

1. **System Overview**: Overall system health status
2. **HTTP Request Rate**: Requests per second by endpoint
3. **HTTP Response Time**: 95th and 50th percentile response times
4. **Error Rate**: Error rate by type and component
5. **Active Sessions**: Current active user sessions
6. **Tasks in Progress**: Current tasks being processed
7. **Agent Executions**: Agent execution metrics
8. **System Resources**: Memory and CPU usage
9. **Database Connections**: Active database connections
10. **Cache Hit Ratio**: Cache performance metrics
11. **Authentication Events**: Login attempts and failures
12. **Rate Limiting**: Rate limit violations

#### Access

- **URL**: `http://localhost:3001`
- **Username**: `admin`
- **Password**: `amas_grafana_password`

## Alerting

### Alert Rules

#### Critical Alerts

1. **System Down**: `up{job="amas"} == 0`
2. **High Error Rate**: `rate(errors_total[5m]) > 0.1`
3. **High Memory Usage**: `system_memory_usage_bytes{type="used"} / system_memory_usage_bytes{type="total"} > 0.9`
4. **High CPU Usage**: `system_cpu_usage_percent > 90`
5. **Database Down**: `database_connections_active == 0`

#### Warning Alerts

1. **High Response Time**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5`
2. **Low Cache Hit Ratio**: `cache_hit_ratio < 0.8`
3. **High Authentication Failures**: `rate(auth_failures_total[5m]) > 0.05`
4. **Rate Limit Violations**: `rate(rate_limit_exceeded_total[5m]) > 0.1`

### Notification Channels

- **Email**: Critical alerts sent to admin team
- **Slack**: Warning alerts sent to operations channel
- **PagerDuty**: Critical alerts for on-call rotation

## Troubleshooting

### Common Issues

#### 1. High Memory Usage

**Symptoms**: System slow, memory metrics high
**Investigation**:
```bash
# Check memory usage
curl http://localhost:8000/health | jq '.metrics.memory_usage_percent'

# Check for memory leaks
curl http://localhost:8000/metrics | grep system_memory_usage_bytes
```

**Solutions**:
- Restart application
- Check for memory leaks in code
- Increase memory limits
- Optimize data structures

#### 2. Database Connection Issues

**Symptoms**: Health check fails, database errors
**Investigation**:
```bash
# Check database health
curl http://localhost:8000/health | jq '.services.database'

# Check connection pool
curl http://localhost:8000/metrics | grep database_connections_active
```

**Solutions**:
- Check database server status
- Verify connection string
- Check network connectivity
- Restart database service

#### 3. High Error Rate

**Symptoms**: Many 5xx errors, error metrics high
**Investigation**:
```bash
# Check error rate
curl http://localhost:8000/metrics | grep errors_total

# Check logs
tail -f /app/logs/amas.log | grep ERROR
```

**Solutions**:
- Check application logs
- Verify external service dependencies
- Check system resources
- Review recent deployments

#### 4. Authentication Issues

**Symptoms**: Login failures, auth errors
**Investigation**:
```bash
# Check auth metrics
curl http://localhost:8000/metrics | grep auth_

# Check audit logs
tail -f /app/logs/amas_audit.log | grep authentication
```

**Solutions**:
- Verify authentication service
- Check user credentials
- Review security policies
- Check rate limiting

### Log Analysis

#### Search Logs

```bash
# Search for specific correlation ID
grep "abc123-def456" /app/logs/amas.log

# Search for errors
grep "ERROR" /app/logs/amas.log | tail -20

# Search for specific user
grep "user_id.*user123" /app/logs/amas.log
```

#### Log Aggregation

For production environments, consider using:
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Fluentd**: Log collection and forwarding
- **Splunk**: Enterprise log management

## Best Practices

### Monitoring Setup

1. **Set up proper alerting thresholds** based on baseline metrics
2. **Configure multiple notification channels** for redundancy
3. **Regular dashboard reviews** to identify trends
4. **Log retention policies** for compliance and storage management

### Performance Monitoring

1. **Monitor key business metrics** alongside technical metrics
2. **Set up capacity planning** based on growth trends
3. **Regular performance testing** to validate thresholds
4. **Monitor external dependencies** for SLA compliance

### Security Monitoring

1. **Monitor authentication events** for suspicious activity
2. **Track rate limiting violations** for potential attacks
3. **Audit log analysis** for compliance requirements
4. **Regular security scans** using automated tools

### Incident Response

1. **Document runbooks** for common issues
2. **Practice incident response** with regular drills
3. **Post-incident reviews** to improve monitoring
4. **Escalation procedures** for different severity levels

## Configuration

### Environment Variables

```bash
# Prometheus
MONITORING_PROMETHEUS_ENABLED=true
MONITORING_PROMETHEUS_PORT=9090

# Grafana
MONITORING_GRAFANA_ENABLED=true
MONITORING_GRAFANA_PORT=3001
MONITORING_GRAFANA_ADMIN_PASSWORD=amas_grafana_password

# Logging
MONITORING_LOG_LEVEL=INFO
MONITORING_LOG_FORMAT=json
MONITORING_LOG_FILE_PATH=/app/logs/amas.log

# Health checks
FEATURE_ENABLE_HEALTH_CHECKS=true
```

### Docker Compose

```yaml
version: '3.8'
services:
  amas:
    build: .
    ports:
      - "8000:8000"
      - "9090:9090"  # Prometheus metrics
    environment:
      - MONITORING_PROMETHEUS_ENABLED=true
      - MONITORING_GRAFANA_ENABLED=true
    volumes:
      - ./logs:/app/logs

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=amas_grafana_password
    volumes:
      - ./monitoring/grafana:/var/lib/grafana
```

## Conclusion

This monitoring guide provides the foundation for comprehensive observability of the AMAS system. Regular review and updates of monitoring configurations ensure optimal system performance and reliability.

For additional support or questions, refer to the main AMAS documentation or contact the development team.