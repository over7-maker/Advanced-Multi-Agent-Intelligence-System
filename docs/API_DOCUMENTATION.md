# 📚 **API Documentation - Phase 2 Enhanced**

## 🌐 **Overview**

This document provides comprehensive API documentation for all the Phase 2 enhanced endpoints and services in the Advanced Multi-Agent Intelligence System.

---

## 🏥 **Health Check Endpoints**

### **GET /health**
Basic health status endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600,
  "version": "2.0.0"
}
```

**Status Codes:**
- `200` - Healthy
- `503` - Unhealthy

---

### **GET /health/ready**
Kubernetes readiness probe endpoint.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": "healthy",
    "cache": "healthy",
    "external_api": "healthy"
  }
}
```

**Status Codes:**
- `200` - Ready
- `503` - Not Ready

---

### **GET /health/live**
Kubernetes liveness probe endpoint.

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600
}
```

**Status Codes:**
- `200` - Alive
- `503` - Not Alive

---

### **GET /health/detailed**
Comprehensive health information endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600,
  "version": "2.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 15.5,
      "message": "Connection successful"
    },
    "cache": {
      "status": "healthy",
      "response_time_ms": 2.1,
      "message": "Redis connection active"
    },
    "external_api": {
      "status": "healthy",
      "response_time_ms": 45.2,
      "message": "API endpoint responding"
    }
  },
  "system": {
    "cpu_usage_percent": 25.5,
    "memory_usage_percent": 60.2,
    "disk_usage_percent": 45.8
  }
}
```

**Status Codes:**
- `200` - All checks healthy
- `503` - One or more checks unhealthy

---

## 📊 **Metrics Endpoints**

### **GET /metrics**
Prometheus metrics endpoint.

**Response:**
```
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/users",status="200"} 150

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/api/users",le="0.1"} 100
http_request_duration_seconds_bucket{method="GET",endpoint="/api/users",le="0.5"} 140
http_request_duration_seconds_bucket{method="GET",endpoint="/api/users",le="1.0"} 150
http_request_duration_seconds_sum{method="GET",endpoint="/api/users"} 45.2
http_request_duration_seconds_count{method="GET",endpoint="/api/users"} 150

# HELP system_cpu_usage_percent CPU usage percentage
# TYPE system_cpu_usage_percent gauge
system_cpu_usage_percent 25.5

# HELP system_memory_usage_percent Memory usage percentage
# TYPE system_memory_usage_percent gauge
system_memory_usage_percent 60.2

# HELP circuit_breaker_state Circuit breaker state
# TYPE circuit_breaker_state gauge
circuit_breaker_state{name="external_api",state="closed"} 1
```

**Content-Type:** `text/plain; version=0.0.4; charset=utf-8`

---

## 🔧 **Service APIs**

### **Enhanced Logging Service**

#### **LoggingContext**
Context manager for structured logging with correlation IDs.

```python
from src.amas.services.enhanced_logging_service import LoggingContext

# Basic usage
with LoggingContext(correlation_id="req-123"):
    logger.info("Processing request")

# Advanced usage with multiple context variables
with LoggingContext(
    correlation_id="req-123",
    user_id="user-456",
    session_id="session-789",
    request_id="req-123",
    trace_id="trace-abc"
):
    logger.info("User action performed", action="login")
```

#### **Enhanced Logger Methods**

```python
from src.amas.services.enhanced_logging_service import get_logger

logger = get_logger("my_service", "authentication")

# Basic logging
logger.info("User logged in", user_id="user-123", ip_address="192.168.1.1")

# HTTP request logging
logger.log_http_request(
    method="POST",
    url="/api/login",
    status_code=200,
    duration_ms=150.5,
    request_size=1024,
    response_size=2048
)

# Authentication logging
logger.log_authentication(
    username="john.doe",
    success=True,
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0..."
)

# Authorization logging
logger.log_authorization(
    user_id="user-123",
    resource="admin_panel",
    action="read",
    granted=True
)

# Security event logging
logger.log_security_event(
    event="suspicious_login_attempt",
    severity="high",
    user_id="user-123",
    ip_address="192.168.1.1"
)

# Performance logging
logger.log_performance(
    operation="database_query",
    duration_ms=25.5,
    memory_usage_mb=128.0,
    cpu_usage_percent=15.2
)

# Business event logging
logger.log_business_event(
    event="order_created",
    value=99.99,
    impact="high",
    order_id="order-123"
)

# Error logging
logger.log_error(
    error=ValueError("Invalid input"),
    context="user_validation",
    user_id="user-123"
)
```

---

### **Health Check Service**

#### **Health Check Management**

```python
from src.amas.services.health_check_service import (
    HealthCheckService, add_health_check, remove_health_check,
    check_health, check_dependency_health
)

# Add health checks
add_memory_health_check("memory", max_usage_percent=90.0)
add_disk_health_check("disk", max_usage_percent=85.0)
add_database_health_check("database", get_database_connection)
add_cache_health_check("redis", get_redis_client)
add_external_api_health_check("payment_api", "https://api.payment.com")

# Check overall health
health_result = await check_health()
print(f"Status: {health_result['status']}")

# Check specific dependency
db_health = await check_dependency_health("database")
print(f"Database: {db_health.status} - {db_health.message}")

# Remove health check
remove_health_check("old_service")
```

#### **Custom Health Check**

```python
from src.amas.services.health_check_service import ServiceHealthCheck

class CustomHealthCheck(ServiceHealthCheck):
    def __init__(self, name: str, service_instance):
        super().__init__(name, "service", timeout=5.0, critical=True)
        self.service = service_instance
    
    async def _check_impl(self) -> Dict[str, Any]:
        try:
            # Check service health
            result = await self.service.health_check()
            return {
                "status": "healthy",
                "details": result,
                "response_time_ms": 25.5
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": 0.0
            }

# Add custom health check
custom_check = CustomHealthCheck("my_service", my_service_instance)
add_health_check(custom_check)
```

---

### **Circuit Breaker Service**

#### **Circuit Breaker Management**

```python
from src.amas.services.circuit_breaker_service import (
    get_circuit_breaker_service, CircuitBreakerConfig,
    CircuitBreakerOpenException, CircuitBreakerTimeoutException
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
try:
    result = await breaker.call(external_api_function, arg1, arg2)
    print(f"Result: {result}")
except CircuitBreakerOpenException:
    print("Circuit breaker is open - service unavailable")
except CircuitBreakerTimeoutException:
    print("Request timed out")
except Exception as e:
    print(f"Other error: {e}")

# Check circuit breaker status
print(f"State: {breaker.state}")
print(f"Statistics: {breaker.get_stats()}")
```

#### **Circuit Breaker Decorator**

```python
from src.amas.services.circuit_breaker_service import circuit_breaker

# Use decorator
@circuit_breaker("external_api", failure_threshold=5, recovery_timeout=60.0)
async def call_external_api(data):
    # External API call implementation
    response = await external_api_client.post("/api/process", json=data)
    return response.json()

# Call the function
try:
    result = await call_external_api({"key": "value"})
except CircuitBreakerOpenException:
    print("Service temporarily unavailable")
```

---

### **Error Recovery Service**

#### **Error Recovery Management**

```python
from src.amas.services.error_recovery_service import (
    get_error_recovery_service, ErrorContext, ErrorSeverity,
    auto_recover
)

# Get error recovery service
service = get_error_recovery_service()

# Create error context
context = ErrorContext(
    error_type="database_error",
    error_message="Connection failed",
    severity=ErrorSeverity.HIGH,
    component="database_service",
    operation="connect",
    user_id="user-123",
    correlation_id="req-123"
)

# Handle error with recovery
success = await service.handle_error(context)
if success:
    print("Error recovered successfully")
else:
    print("Error recovery failed")

# Use decorator for automatic recovery
@auto_recover("api_error", ErrorSeverity.MEDIUM)
async def api_call():
    # API call implementation
    response = await external_api.get("/data")
    return response.json()

# Call the function
try:
    result = await api_call()
except Exception as e:
    print(f"Error after recovery attempts: {e}")
```

#### **Recovery Strategies**

```python
from src.amas.services.error_recovery_service import RecoveryStrategy

# Configure recovery strategies
service.configure_strategy(
    error_type="database_error",
    strategy=RecoveryStrategy.RETRY,
    max_retries=3,
    retry_delay=1.0
)

service.configure_strategy(
    error_type="external_api_error",
    strategy=RecoveryStrategy.CIRCUIT_BREAKER,
    circuit_breaker_name="external_api"
)

service.configure_strategy(
    error_type="validation_error",
    strategy=RecoveryStrategy.FALLBACK,
    fallback_function=default_validation
)
```

---

### **Prometheus Metrics Service**

#### **Metrics Collection**

```python
from src.amas.services.prometheus_metrics_service import get_metrics_service

# Get metrics service
metrics = get_metrics_service()

# Record HTTP request metrics
metrics.record_http_request(
    method="GET",
    endpoint="/api/users",
    status_code=200,
    duration=0.150,
    request_size=1024,
    response_size=2048
)

# Record authentication metrics
metrics.record_authentication(
    username="john.doe",
    success=True,
    ip_address="192.168.1.1"
)

# Record agent metrics
metrics.record_agent_execution(
    agent_name="code_analyzer",
    task_id="task-123",
    success=True,
    duration=45.2,
    tokens_used=1500
)

# Record task metrics
metrics.record_task_processing(
    task_type="pr_analysis",
    task_id="task-123",
    success=True,
    duration=120.5,
    files_processed=25
)

# Record system metrics
metrics.record_system_metrics(
    cpu_usage_percent=25.5,
    memory_usage_percent=60.2,
    disk_usage_percent=45.8,
    uptime_seconds=3600
)

# Record database metrics
metrics.record_database_query(
    database="main_db",
    operation="SELECT",
    success=True,
    duration=15.5,
    rows_affected=100
)

# Record cache metrics
metrics.record_cache_operation(
    cache_name="redis",
    operation="GET",
    success=True,
    duration=2.1,
    hit=True
)

# Record error metrics
metrics.record_error(
    error_type="validation_error",
    component="user_service",
    severity="medium"
)

# Record business metrics
metrics.record_business_event(
    event="user_registration",
    value=1.0,
    user_id="user-123"
)

# Record performance metrics
metrics.record_performance(
    operation="data_processing",
    duration_ms=150.0,
    memory_usage_mb=128.0,
    cpu_usage_percent=15.2
)

# Get metrics data
metrics_data = metrics.get_metrics()
print(metrics_data)
```

---

## 🔒 **Security APIs**

### **Input Validation**

```python
from src.amas.errors.error_handling import (
    ValidationError, validate_required_fields, validate_email,
    validate_password_strength, validate_url
)

# Validate required fields
try:
    validate_required_fields(data, ["email", "name", "password"])
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))

# Validate email format
try:
    validate_email(data["email"])
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))

# Validate password strength
try:
    validate_password_strength(data["password"], min_length=8)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))

# Validate URL
try:
    validate_url(data["website"])
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### **Security Logging**

```python
from src.amas.services.enhanced_logging_service import security_logger

# Log authentication events
security_logger.log_authentication(
    username="john.doe",
    success=True,
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0...",
    session_id="session-123"
)

# Log authorization events
security_logger.log_authorization(
    user_id="user-123",
    resource="admin_panel",
    action="read",
    granted=True,
    ip_address="192.168.1.1"
)

# Log security events
security_logger.log_security_event(
    event="suspicious_activity",
    severity="high",
    user_id="user-123",
    ip_address="192.168.1.1",
    details={"attempts": 5, "time_window": "5m"}
)
```

---

## 📊 **Monitoring and Observability**

### **Health Monitoring**

```python
# Check overall health
health_result = await check_health()
print(f"Overall status: {health_result['status']}")
print(f"Uptime: {health_result['uptime_seconds']}s")

# Check specific dependencies
dependencies = ["database", "cache", "external_api"]
for dep in dependencies:
    result = await check_dependency_health(dep)
    print(f"{dep}: {result.status} - {result.message}")
```

### **Metrics Collection**

```python
# Get metrics service
metrics = get_metrics_service()

# Record custom metrics
metrics.record_custom_metric(
    name="custom_operation_duration",
    value=150.5,
    labels={"operation": "data_processing", "type": "batch"}
)

# Get metrics data
metrics_data = metrics.get_metrics()
print(f"Total metrics: {len(metrics_data)}")
```

### **Logging and Tracing**

```python
# Use correlation IDs for tracing
with LoggingContext(correlation_id="req-123"):
    logger.info("Starting request processing")
    
    # Nested operations inherit context
    await process_data()
    await send_notification()
    
    logger.info("Request processing completed")
```

---

## 🚀 **Best Practices**

### **1. Error Handling**

```python
from src.amas.errors.error_handling import (
    ValidationError, AuthenticationError, AuthorizationError,
    InternalError, ExternalServiceError
)

try:
    # Your business logic
    result = await process_request(data)
    return result
except ValidationError as e:
    logger.warning("Validation failed", error=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except AuthenticationError as e:
    logger.warning("Authentication failed", error=str(e))
    raise HTTPException(status_code=401, detail=str(e))
except AuthorizationError as e:
    logger.warning("Authorization failed", error=str(e))
    raise HTTPException(status_code=403, detail=str(e))
except ExternalServiceError as e:
    logger.error("External service error", error=str(e))
    raise HTTPException(status_code=502, detail="External service unavailable")
except Exception as e:
    logger.error("Unexpected error", error=str(e))
    raise HTTPException(status_code=500, detail="Internal server error")
```

### **2. Health Checks**

```python
# Add health checks for all dependencies
add_database_health_check("main_db", get_database_connection)
add_cache_health_check("redis", get_redis_client)
add_external_api_health_check("payment_api", "https://api.payment.com")

# Implement custom health checks
async def custom_health_check():
    try:
        # Check your service health
        result = await my_service.check_health()
        return {"status": "healthy", "details": result}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

add_service_health_check("my_service", custom_health_check)
```

### **3. Circuit Breakers**

```python
# Use circuit breakers for external service calls
@circuit_breaker("external_api", failure_threshold=5, recovery_timeout=60.0)
async def call_external_api(data):
    response = await external_api_client.post("/api/process", json=data)
    return response.json()

# Handle circuit breaker states
try:
    result = await call_external_api(data)
except CircuitBreakerOpenException:
    # Use fallback or return cached data
    result = get_cached_data()
except CircuitBreakerTimeoutException:
    # Handle timeout
    raise HTTPException(status_code=504, detail="Request timeout")
```

### **4. Metrics Collection**

```python
# Record metrics for all important operations
@app.middleware("http")
async def metrics_middleware(request, call_next):
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
```

---

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_SECURITY_LEVEL=medium
LOG_ENABLE_CORRELATION=true
LOG_ENABLE_METRICS=true
LOG_ENABLE_AUDIT=true

# Health Checks
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=5
HEALTH_CHECK_RETRIES=3

# Metrics
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
PROMETHEUS_METRICS_PATH=/metrics

# Circuit Breakers
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
CIRCUIT_BREAKER_SUCCESS_THRESHOLD=3
CIRCUIT_BREAKER_TIMEOUT=30

# Error Recovery
ERROR_RECOVERY_ENABLED=true
ERROR_RECOVERY_MAX_RETRIES=3
ERROR_RECOVERY_RETRY_DELAY=1.0
ERROR_RECOVERY_EXPONENTIAL_BACKOFF=true
ERROR_RECOVERY_MAX_RETRY_DELAY=60.0
```

---

## 📚 **Troubleshooting**

### **Common Issues**

#### **Health Check Failures**
```python
# Check specific health check
result = await check_dependency_health("database")
print(f"Database health: {result.status} - {result.message}")

# Check all health checks
health_result = await check_health()
for check_name, check_result in health_result["checks"].items():
    print(f"{check_name}: {check_result['status']}")
```

#### **Circuit Breaker Issues**
```python
# Check circuit breaker status
service = get_circuit_breaker_service()
breaker = service.get_breaker("external_api")
print(f"Circuit breaker state: {breaker.state}")
print(f"Statistics: {breaker.get_stats()}")
```

#### **Metrics Issues**
```python
# Check metrics service
metrics = get_metrics_service()
metrics_data = metrics.get_metrics()
print(f"Metrics available: {len(metrics_data)}")
```

---

## 🎯 **Conclusion**

This API documentation provides comprehensive information about all Phase 2 enhanced endpoints and services. The system now includes enterprise-grade reliability, security, and observability features that make it production-ready for any organization.

For additional support or questions, refer to the troubleshooting section or create an issue in the repository.