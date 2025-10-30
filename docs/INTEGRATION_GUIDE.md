# 🔗 **Integration Guide - Phase 2 Enhanced**

## 📋 **Overview**

This guide provides step-by-step instructions for integrating the Phase 2 enhanced features into your existing projects and workflows. It covers installation, configuration, and usage examples.

---

## 🚀 **Quick Start**

### **1. Prerequisites**

- Python 3.8+
- FastAPI (for API endpoints)
- GitHub Actions (for workflows)
- Docker (optional, for containerized deployment)

### **2. Installation**

```bash
# Clone the repository
git clone https://github.com/your-org/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Install dependencies
pip install -r requirements.txt

# Install enhanced features
pip install -e .
```

### **3. Basic Configuration**

```bash
# Set environment variables
export LOG_LEVEL=INFO
export LOG_FORMAT=json
export HEALTH_CHECK_ENABLED=true
export PROMETHEUS_ENABLED=true
```

---

## 🔧 **Service Integration**

### **1. Enhanced Logging Service**

#### **Basic Integration**

```python
# main.py
from src.amas.services.enhanced_logging_service import (
    configure_logging, get_logger, LoggingConfig, LogLevel, LogFormat
)

# Configure logging
config = LoggingConfig(
    level=LogLevel.INFO,
    format=LogFormat.JSON,
    enable_correlation=True,
    enable_metrics=True
)
configure_logging(config)

# Get logger
logger = get_logger("my_app", "main")

# Use logger
logger.info("Application started", version="2.0.0")
```

#### **FastAPI Integration**

```python
# main.py
from fastapi import FastAPI, Request
from src.amas.services.enhanced_logging_service import get_logger, LoggingContext

app = FastAPI()
logger = get_logger("api", "main")

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # Generate correlation ID
    correlation_id = str(uuid.uuid4())
    
    with LoggingContext(correlation_id=correlation_id):
        logger.info("Request started", 
                   method=request.method, 
                   url=str(request.url))
        
        response = await call_next(request)
        
        logger.info("Request completed", 
                   status_code=response.status_code)
        
        return response

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello World"}
```

#### **Django Integration**

```python
# settings.py
import os
from src.amas.services.enhanced_logging_service import configure_logging, LoggingConfig, LogLevel, LogFormat

# Configure logging
config = LoggingConfig(
    level=LogLevel.INFO,
    format=LogFormat.JSON,
    enable_correlation=True
)
configure_logging(config)

# middleware.py
from src.amas.services.enhanced_logging_service import get_logger, LoggingContext
import uuid

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = get_logger("django", "middleware")

    def __call__(self, request):
        correlation_id = str(uuid.uuid4())
        
        with LoggingContext(correlation_id=correlation_id):
            self.logger.info("Request started", 
                           method=request.method, 
                           path=request.path)
            
            response = self.get_response(request)
            
            self.logger.info("Request completed", 
                           status_code=response.status_code)
            
            return response
```

---

### **2. Health Check Service**

#### **Basic Integration**

```python
# main.py
from src.amas.services.health_check_service import (
    add_health_check, check_health, add_memory_health_check, 
    add_disk_health_check, add_database_health_check
)

# Add health checks
add_memory_health_check("memory", max_usage_percent=90.0)
add_disk_health_check("disk", max_usage_percent=85.0)

# Check health
health_result = await check_health()
print(f"Health status: {health_result['status']}")
```

#### **FastAPI Integration**

```python
# main.py
from fastapi import FastAPI
from src.amas.services.health_check_service import check_health

app = FastAPI()

@app.get("/health")
async def health():
    return await check_health()

@app.get("/health/ready")
async def readiness():
    health_result = await check_health()
    if health_result["status"] == "healthy":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Not ready")

@app.get("/health/live")
async def liveness():
    return {"status": "alive"}
```

#### **Custom Health Checks**

```python
# health_checks.py
from src.amas.services.health_check_service import ServiceHealthCheck
import asyncio

class DatabaseHealthCheck(ServiceHealthCheck):
    def __init__(self, name: str, db_connection):
        super().__init__(name, "database", timeout=5.0, critical=True)
        self.db = db_connection
    
    async def _check_impl(self):
        try:
            # Test database connection
            await self.db.execute("SELECT 1")
            return {
                "status": "healthy",
                "message": "Database connection successful",
                "response_time_ms": 15.5
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "response_time_ms": 0.0
            }

# Add custom health check
db_check = DatabaseHealthCheck("main_db", database_connection)
add_health_check(db_check)
```

---

### **3. Circuit Breaker Service**

#### **Basic Integration**

```python
# external_api.py
from src.amas.services.circuit_breaker_service import (
    get_circuit_breaker_service, CircuitBreakerConfig,
    CircuitBreakerOpenException
)

# Get circuit breaker service
service = get_circuit_breaker_service()

# Create circuit breaker
config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60.0,
    success_threshold=3,
    timeout=30.0
)
breaker = service.create_breaker("external_api", config)

# Use circuit breaker
async def call_external_api(data):
    try:
        result = await breaker.call(external_api_function, data)
        return result
    except CircuitBreakerOpenException:
        # Use fallback or cached data
        return get_cached_data()
```

#### **Decorator Usage**

```python
# api_client.py
from src.amas.services.circuit_breaker_service import circuit_breaker

@circuit_breaker("payment_api", failure_threshold=3, recovery_timeout=30.0)
async def process_payment(payment_data):
    response = await payment_api_client.post("/process", json=payment_data)
    return response.json()

@circuit_breaker("notification_api", failure_threshold=5, recovery_timeout=60.0)
async def send_notification(notification_data):
    response = await notification_api_client.post("/send", json=notification_data)
    return response.json()
```

---

### **4. Error Recovery Service**

#### **Basic Integration**

```python
# error_handling.py
from src.amas.services.error_recovery_service import (
    get_error_recovery_service, ErrorContext, ErrorSeverity,
    auto_recover
)

# Get error recovery service
recovery_service = get_error_recovery_service()

# Configure recovery strategies
recovery_service.configure_strategy(
    error_type="database_error",
    strategy=RecoveryStrategy.RETRY,
    max_retries=3,
    retry_delay=1.0
)

# Use decorator for automatic recovery
@auto_recover("api_error", ErrorSeverity.MEDIUM)
async def api_call():
    response = await external_api.get("/data")
    return response.json()
```

#### **Manual Error Handling**

```python
# service.py
from src.amas.services.error_recovery_service import ErrorContext, ErrorSeverity

async def process_data(data):
    try:
        result = await database.save(data)
        return result
    except Exception as e:
        # Create error context
        context = ErrorContext(
            error_type="database_error",
            error_message=str(e),
            severity=ErrorSeverity.HIGH,
            component="data_service",
            operation="save",
            user_id=data.get("user_id"),
            correlation_id=data.get("correlation_id")
        )
        
        # Handle error with recovery
        success = await recovery_service.handle_error(context)
        if success:
            logger.info("Error recovered successfully")
        else:
            logger.error("Error recovery failed")
            raise
```

---

### **5. Prometheus Metrics Service**

#### **Basic Integration**

```python
# metrics.py
from src.amas.services.prometheus_metrics_service import get_metrics_service

# Get metrics service
metrics = get_metrics_service()

# Record metrics
metrics.record_http_request(
    method="GET",
    endpoint="/api/users",
    status_code=200,
    duration=0.150
)

metrics.record_business_event("user_registration", value=1.0)
```

#### **FastAPI Integration**

```python
# main.py
from fastapi import FastAPI, Request
from src.amas.services.prometheus_metrics_service import get_metrics_service
import time

app = FastAPI()
metrics = get_metrics_service()

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    metrics.record_http_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration=duration
    )
    
    return response

@app.get("/metrics")
async def metrics_endpoint():
    return Response(
        content=metrics.get_metrics_text(),
        media_type="text/plain"
    )
```

---

## 🔧 **Workflow Integration**

### **1. GitHub Actions Integration**

#### **Basic Workflow**

```yaml
# .github/workflows/enhanced-workflow.yml
name: Enhanced AI Workflow

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  enhanced-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Configure enhanced features
        run: |
          echo "LOG_LEVEL=INFO" >> $GITHUB_ENV
          echo "HEALTH_CHECK_ENABLED=true" >> $GITHUB_ENV
          echo "PROMETHEUS_ENABLED=true" >> $GITHUB_ENV
      
      - name: Run enhanced analysis
        run: |
          python .github/scripts/bulletproof_ai_pr_analyzer.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
          # ... other API keys
```

#### **Advanced Workflow with Health Checks**

```yaml
# .github/workflows/advanced-workflow.yml
name: Advanced AI Workflow

on:
  workflow_dispatch:
    inputs:
      enable_health_checks:
        description: 'Enable health checks'
        required: false
        default: 'true'
        type: boolean

jobs:
  health-check:
    if: ${{ inputs.enable_health_checks }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Run health checks
        run: |
          python -c "
          import asyncio
          from src.amas.services.health_check_service import check_health
          
          async def main():
              result = await check_health()
              print(f'Health status: {result[\"status\"]}')
              if result['status'] != 'healthy':
                  exit(1)
          
          asyncio.run(main())
          "
  
  enhanced-analysis:
    needs: health-check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Run enhanced analysis
        run: |
          python .github/scripts/bulletproof_ai_pr_analyzer.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
```

---

### **2. Docker Integration**

#### **Dockerfile**

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV LOG_LEVEL=INFO
ENV LOG_FORMAT=json
ENV HEALTH_CHECK_ENABLED=true
ENV PROMETHEUS_ENABLED=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN pip install -e .

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "src.amas.api.main"]
```

#### **Docker Compose**

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
      - "9090:9090"
    environment:
      - LOG_LEVEL=INFO
      - LOG_FORMAT=json
      - HEALTH_CHECK_ENABLED=true
      - PROMETHEUS_ENABLED=true
      - CIRCUIT_BREAKER_ENABLED=true
      - ERROR_RECOVERY_ENABLED=true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  grafana-storage:
```

---

## 🔧 **Configuration Management**

### **1. Environment Configuration**

```bash
# .env
# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_SECURITY_LEVEL=medium
LOG_ENABLE_CORRELATION=true
LOG_ENABLE_METRICS=true
LOG_ENABLE_AUDIT=true

# Health Check Configuration
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=5
HEALTH_CHECK_RETRIES=3

# Metrics Configuration
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
PROMETHEUS_METRICS_PATH=/metrics

# Circuit Breaker Configuration
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
CIRCUIT_BREAKER_SUCCESS_THRESHOLD=3
CIRCUIT_BREAKER_TIMEOUT=30

# Error Recovery Configuration
ERROR_RECOVERY_ENABLED=true
ERROR_RECOVERY_MAX_RETRIES=3
ERROR_RECOVERY_RETRY_DELAY=1.0
ERROR_RECOVERY_EXPONENTIAL_BACKOFF=true
ERROR_RECOVERY_MAX_RETRY_DELAY=60.0

# Project Root Configuration
PROJECT_ROOT_CACHE_ENABLED=true
PROJECT_ROOT_MAX_DEPTH=20
PROJECT_ROOT_SECURITY_LEVEL=medium
```

### **2. YAML Configuration**

```yaml
# config/application.yaml
logging:
  level: INFO
  format: json
  security_level: medium
  enable_correlation: true
  enable_metrics: true
  enable_audit: true
  redact_patterns:
    - password
    - api_key
    - token
    - secret

health:
  enabled: true
  interval: 30
  timeout: 5
  retries: 3
  checks:
    - name: database
      type: database
      timeout: 5
      critical: true
    - name: cache
      type: cache
      timeout: 3
      critical: false
    - name: external_api
      type: external_api
      timeout: 10
      critical: false

metrics:
  prometheus:
    enabled: true
    port: 9090
    path: /metrics
  custom_metrics:
    enabled: true
    interval: 60

circuit_breaker:
  enabled: true
  default_config:
    failure_threshold: 5
    recovery_timeout: 60.0
    success_threshold: 3
    timeout: 30.0
  breakers:
    external_api:
      failure_threshold: 3
      recovery_timeout: 30.0
    payment_api:
      failure_threshold: 5
      recovery_timeout: 60.0

error_recovery:
  enabled: true
  max_retries: 3
  retry_delay: 1.0
  exponential_backoff: true
  max_retry_delay: 60.0
  strategies:
    database_error:
      strategy: retry
      max_retries: 3
      retry_delay: 1.0
    external_api_error:
      strategy: circuit_breaker
      circuit_breaker_name: external_api
    validation_error:
      strategy: fallback
      fallback_function: default_validation
```

---

## 📊 **Monitoring Setup**

### **1. Prometheus Configuration**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'amas-app'
    static_configs:
      - targets: ['app:9090']
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### **2. Grafana Dashboard**

```json
{
  "dashboard": {
    "title": "AMAS Enhanced Monitoring",
    "panels": [
      {
        "title": "HTTP Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "HTTP Request Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Circuit Breaker Status",
        "type": "stat",
        "targets": [
          {
            "expr": "circuit_breaker_state",
            "legendFormat": "{{name}} - {{state}}"
          }
        ]
      },
      {
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "system_cpu_usage_percent",
            "legendFormat": "CPU Usage %"
          },
          {
            "expr": "system_memory_usage_percent",
            "legendFormat": "Memory Usage %"
          }
        ]
      }
    ]
  }
}
```

---

## 🚀 **Deployment**

### **1. Kubernetes Deployment**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amas-enhanced
spec:
  replicas: 3
  selector:
    matchLabels:
      app: amas-enhanced
  template:
    metadata:
      labels:
        app: amas-enhanced
    spec:
      containers:
      - name: amas-enhanced
        image: amas-enhanced:latest
        ports:
        - containerPort: 8000
        - containerPort: 9090
        env:
        - name: LOG_LEVEL
          value: "INFO"
        - name: HEALTH_CHECK_ENABLED
          value: "true"
        - name: PROMETHEUS_ENABLED
          value: "true"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: amas-enhanced-service
spec:
  selector:
    app: amas-enhanced
  ports:
  - name: http
    port: 8000
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer
```

### **2. Helm Chart**

```yaml
# helm/amas-enhanced/values.yaml
replicaCount: 3

image:
  repository: amas-enhanced
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 8000
  metricsPort: 9090

ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
  hosts:
    - host: amas.example.com
      paths:
        - path: /
          pathType: Prefix

config:
  logging:
    level: INFO
    format: json
    security_level: medium
  health:
    enabled: true
    interval: 30
  metrics:
    prometheus:
      enabled: true
      port: 9090
  circuit_breaker:
    enabled: true
    failure_threshold: 5
    recovery_timeout: 60
  error_recovery:
    enabled: true
    max_retries: 3

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

---

## 🔧 **Testing**

### **1. Unit Tests**

```python
# tests/test_integration.py
import pytest
import asyncio
from src.amas.services.enhanced_logging_service import get_logger, LoggingContext
from src.amas.services.health_check_service import check_health
from src.amas.services.circuit_breaker_service import get_circuit_breaker_service

class TestIntegration:
    def test_logging_integration(self):
        logger = get_logger("test", "integration")
        
        with LoggingContext(correlation_id="test-123"):
            logger.info("Test message", test_data="value")
    
    @pytest.mark.asyncio
    async def test_health_check_integration(self):
        result = await check_health()
        assert result["status"] in ["healthy", "unhealthy"]
    
    def test_circuit_breaker_integration(self):
        service = get_circuit_breaker_service()
        breaker = service.create_breaker("test_api")
        assert breaker.state == "CLOSED"
```

### **2. Integration Tests**

```python
# tests/test_full_integration.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from src.amas.api.main import app

class TestFullIntegration:
    def test_health_endpoints(self):
        client = TestClient(app)
        
        # Test basic health
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] in ["healthy", "unhealthy"]
        
        # Test readiness
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]
        
        # Test liveness
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"
    
    def test_metrics_endpoint(self):
        client = TestClient(app)
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
```

---

## 🎯 **Best Practices**

### **1. Service Integration**

- **Always use correlation IDs** for request tracing
- **Implement health checks** for all dependencies
- **Use circuit breakers** for external service calls
- **Configure error recovery** for critical operations
- **Record metrics** for all important operations

### **2. Configuration Management**

- **Use environment variables** for configuration
- **Provide sensible defaults** for all settings
- **Validate configuration** at startup
- **Use different configs** for different environments

### **3. Monitoring and Observability**

- **Set up comprehensive monitoring** with Prometheus and Grafana
- **Configure alerts** for critical metrics
- **Use structured logging** with correlation IDs
- **Monitor health checks** and circuit breaker states

### **4. Error Handling**

- **Use specific exception types** for different error conditions
- **Implement retry logic** with exponential backoff
- **Provide fallback mechanisms** for critical operations
- **Log all errors** with appropriate context

---

## 🎉 **Conclusion**

This integration guide provides comprehensive instructions for integrating the Phase 2 enhanced features into your projects. The system now includes enterprise-grade reliability, security, and observability features that make it production-ready for any organization.

Key benefits:
- **Easy Integration**: Simple APIs and configuration options
- **Production Ready**: Enterprise-grade features and best practices
- **Comprehensive Monitoring**: Full observability and alerting
- **Flexible Deployment**: Support for various deployment scenarios
- **Extensive Testing**: Comprehensive test coverage and examples

For additional support or questions, refer to the troubleshooting section or create an issue in the repository.