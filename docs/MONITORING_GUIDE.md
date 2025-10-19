# 📊 Monitoring & Observability Guide

> **Production-ready monitoring stack with Prometheus, Grafana, and enterprise alerting**

## 🎆 **Overview**

This guide covers the complete observability stack for AMAS, including metrics collection, visualization, alerting, and production monitoring best practices.

---

## 📊 **Metrics Collection**

### **Core Metrics**

```prometheus
# AI Provider Metrics
amas_ai_requests_total{provider, status}
amas_ai_response_time_seconds{provider}
amas_bulletproof_validation_results{provider, validated}
amas_fake_ai_detection_total{provider, detected}

# Security Metrics
amas_auth_failures_total{reason, ip}
amas_rate_limit_exceeded_total{endpoint, ip}
amas_jwt_validation_results{status}
amas_security_events_total{event_type, severity}

# Performance Metrics
amas_http_requests_total{method, endpoint, status}
amas_http_request_duration_seconds{method, endpoint}
amas_active_sessions_total
amas_tasks_total{status, type}

# Business Metrics
amas_analyses_completed_total{type}
amas_issues_detected_total{severity}
amas_fixes_applied_total{type}
amas_user_satisfaction_score
```

### **Implementation**

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Initialize metrics
request_count = Counter('amas_requests_total', 'Total requests', ['method', 'endpoint'])
response_time = Histogram('amas_response_duration_seconds', 'Response time')
active_users = Gauge('amas_active_users', 'Currently active users')

# Start metrics server
start_http_server(8000)
```

---

## 📈 **Grafana Dashboards**

### **AMAS Overview Dashboard**

```json
{
  "dashboard": {
    "title": "AMAS System Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [{
          "expr": "rate(amas_requests_total[5m])"
        }]
      },
      {
        "title": "Response Time", 
        "type": "graph",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(amas_response_duration_seconds_bucket[5m]))"
        }]
      },
      {
        "title": "AI Provider Health",
        "type": "stat",
        "targets": [{
          "expr": "up{job='amas-ai-providers'}"
        }]
      }
    ]
  }
}
```

---

## 🚨 **Alerting**

### **Alert Rules**

```yaml
groups:
  - name: amas.rules
    rules:
      - alert: AMASHighErrorRate
        expr: rate(amas_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "{{ $value }}% of requests are failing"
          
      - alert: AMASSlowResponse
        expr: histogram_quantile(0.95, rate(amas_response_duration_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response times detected"
          description: "95th percentile response time is {{ $value }}s"
```

---

## 🚀 **Production Setup**

### **Docker Compose**

```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./config/alert.rules.yml:/etc/prometheus/alert.rules.yml
      
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./config/grafana/dashboards:/var/lib/grafana/dashboards
      
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./config/alertmanager.yml:/etc/alertmanager/alertmanager.yml
```

### **Quick Start**

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access dashboards
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
open http://localhost:9093  # Alertmanager

# Import AMAS dashboards
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @config/grafana/amas-dashboard.json
```

---

## 🎯 **Best Practices**

### **Monitoring Strategy**

1. **🔴 Critical Alerts** - Immediate response required
2. **🟡 Warning Alerts** - Investigation needed
3. **🟢 Info Alerts** - Awareness notifications
4. **📊 Trending Analysis** - Long-term pattern recognition

### **SLO/SLI Definitions**

| Service Level Objective | Target | Measurement |
|-------------------------|--------|--------------|
| **Availability** | 99.9% | HTTP 200 responses |
| **Response Time** | <3s 95th percentile | Request duration |
| **Error Rate** | <0.1% | HTTP 5xx responses |
| **AI Provider Success** | >99% | Successful API calls |

This monitoring guide ensures your AMAS deployment has enterprise-grade observability and alerting capabilities.

**Ready for production monitoring!** 🚀