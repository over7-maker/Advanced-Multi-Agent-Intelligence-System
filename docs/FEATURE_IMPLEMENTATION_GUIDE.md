# 🚀 **Feature Implementation Guide - Phase 2 Enhanced**

## 📋 **Overview**

This guide provides comprehensive documentation for all the Phase 2 enhancements implemented in the Advanced Multi-Agent Intelligence System. It covers implementation details, usage examples, configuration options, and best practices.

---

## 🔧 **Core Enhancements**

### **1. Enhanced Project Root Finding**

#### **Implementation**
- **File**: `src/amas/utils/project_root.py`
- **Purpose**: Robust project root detection with security hardening
- **Features**: Multiple detection strategies, security restrictions, validation

#### **Key Features**
```python
# Basic usage
from src.amas.utils.project_root import find_project_root, get_project_root

# Find project root with security validation
project_root = find_project_root("/path/to/project")

# Get cached project root (recommended for performance)
project_root = get_project_root()

# Validate project structure
from src.amas.utils.project_root import validate_project_structure
is_valid = validate_project_structure(project_root)
```

#### **Security Features**
- **Restricted Directory Protection**: Prevents traversal of system directories
- **File Pattern Validation**: Avoids sensitive files during detection
- **Path Security Validation**: Ensures safe path operations
- **Depth Limiting**: Prevents infinite traversal loops

#### **Detection Strategies**
1. **Primary**: Look for `.git` directory
2. **Secondary**: Check for `pyproject.toml`
3. **Tertiary**: Look for `setup.py`, `requirements.txt`, etc.
4. **Fallback**: Use current directory if safe

#### **Configuration**
```python
# Environment variables
PROJECT_ROOT_CACHE_ENABLED=true
PROJECT_ROOT_MAX_DEPTH=20
PROJECT_ROOT_SECURITY_LEVEL=medium
```

---

### **2. Enhanced Logging Service**

#### **Implementation**
- **File**: `src/amas/services/enhanced_logging_service.py`
- **Purpose**: Structured logging with security and observability
- **Features**: JSON logging, security redaction, correlation IDs, performance metrics

#### **Key Features**
```python
from src.amas.services.enhanced_logging_service import (
    configure_logging, get_logger, LoggingConfig, 
    LogLevel, LogFormat, SecurityLevel, LoggingContext
)

# Configure enhanced logging
config = LoggingConfig(
    level=LogLevel.INFO,
    format=LogFormat.JSON,
    security_level=SecurityLevel.MEDIUM,
    enable_correlation=True,
    enable_metrics=True,
    enable_audit=True
)
configure_logging(config)

# Get logger with context
logger = get_logger("my_service", "authentication")

# Use logging context
with LoggingContext(correlation_id="req-123", user_id="user-456"):
    logger.info("User action performed", action="login", status="success")
```

#### **Security Features**
- **PII Redaction**: Automatic redaction of sensitive data
- **Pattern-based Redaction**: Configurable redaction patterns
- **Security Levels**: Multiple security levels (low, medium, high, maximum)
- **Audit Logging**: Specialized logging for security events

#### **Observability Features**
- **Correlation IDs**: Request tracing across services
- **Structured Logging**: JSON format for easy parsing
- **Performance Metrics**: Built-in performance logging
- **Context Management**: Automatic context propagation

#### **Configuration**
```python
# Environment variables
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_SECURITY_LEVEL=medium
LOG_ENABLE_CORRELATION=true
LOG_ENABLE_METRICS=true
LOG_ENABLE_AUDIT=true
LOG_REDACT_PATTERNS=password,api_key,token
```

---

### **3. Health Check Service**

#### **Implementation**
- **File**: `src/amas/services/health_check_service.py`
- **Purpose**: Comprehensive health monitoring with dependency checks
- **Features**: Multiple health check types, dependency monitoring, system metrics

#### **Key Features**
```python
from src.amas.services.health_check_service import (
    HealthCheckService, DatabaseHealthCheck, MemoryHealthCheck,
    DiskHealthCheck, add_health_check, check_health
)

# Create health check service
health_service = HealthCheckService()

# Add health checks
add_memory_health_check("memory", max_usage_percent=90.0)
add_disk_health_check("disk", max_usage_percent=85.0)

# Check all health
health_result = await check_health()
print(f"Overall status: {health_result['status']}")
```

#### **Health Check Types**
1. **Database Health Check**: Connection and query testing
2. **Cache Health Check**: Redis/cache system testing
3. **External API Health Check**: Third-party service testing
4. **File System Health Check**: Disk space and permissions
5. **Memory Health Check**: Memory usage monitoring
6. **Disk Health Check**: Disk space monitoring
7. **Network Health Check**: Connectivity testing
8. **Service Health Check**: Internal service testing

#### **API Endpoints**
- **`/health`**: Basic health status
- **`/health/ready`**: Kubernetes readiness probe
- **`/health/live`**: Kubernetes liveness probe
- **`/health/detailed`**: Comprehensive health information

#### **Configuration**
```python
# Environment variables
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=5
HEALTH_CHECK_RETRIES=3
```

---

### **4. Circuit Breaker Service**

#### **Implementation**
- **File**: `src/amas/services/circuit_breaker_service.py`
- **Purpose**: Circuit breaker pattern for external service calls
- **Features**: Configurable thresholds, automatic recovery, statistics tracking

#### **Key Features**
```python
from src.amas.services.circuit_breaker_service import (
    get_circuit_breaker_service, CircuitBreakerConfig,
    circuit_breaker
)

# Create circuit breaker
config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60.0,
    success_threshold=3,
    timeout=30.0
)
service = get_circuit_breaker_service()
breaker = service.create_breaker("external_api", config)

# Use circuit breaker
try:
    result = await breaker.call(external_api_function)
except CircuitBreakerOpenException:
    # Handle circuit breaker open
    pass
```

#### **Circuit States**
1. **CLOSED**: Normal operation, calls allowed
2. **OPEN**: Circuit open, calls fail fast
3. **HALF_OPEN**: Testing if service is back

#### **Configuration**
```python
# Environment variables
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
CIRCUIT_BREAKER_SUCCESS_THRESHOLD=3
CIRCUIT_BREAKER_TIMEOUT=30
```

---

### **5. Error Recovery Service**

#### **Implementation**
- **File**: `src/amas/services/error_recovery_service.py`
- **Purpose**: Automated error recovery and self-healing
- **Features**: Multiple recovery strategies, error context tracking, statistics

#### **Key Features**
```python
from src.amas.services.error_recovery_service import (
    get_error_recovery_service, ErrorContext, ErrorSeverity,
    auto_recover
)

# Create error context
context = ErrorContext(
    error_type="database_error",
    error_message="Connection failed",
    severity=ErrorSeverity.HIGH,
    component="database_service",
    operation="connect"
)

# Handle error with recovery
service = get_error_recovery_service()
success = await service.handle_error(context)

# Use decorator for automatic recovery
@auto_recover("api_error", ErrorSeverity.MEDIUM)
async def api_call():
    # API call implementation
    pass
```

#### **Recovery Strategies**
1. **Retry**: Exponential backoff retry
2. **Fallback**: Alternative operation
3. **Circuit Breaker**: Open circuit breaker
4. **Graceful Degradation**: Reduced functionality
5. **Service Restart**: Restart service component
6. **Manual Intervention**: Alert for manual handling

#### **Configuration**
```python
# Environment variables
ERROR_RECOVERY_ENABLED=true
ERROR_RECOVERY_MAX_RETRIES=3
ERROR_RECOVERY_RETRY_DELAY=1.0
ERROR_RECOVERY_EXPONENTIAL_BACKOFF=true
ERROR_RECOVERY_MAX_RETRY_DELAY=60.0
```

---

### **6. Prometheus Metrics Service**

#### **Implementation**
- **File**: `src/amas/services/prometheus_metrics_service.py`
- **Purpose**: Comprehensive metrics collection for monitoring
- **Features**: HTTP metrics, system metrics, business metrics, custom metrics

#### **Key Features**
```python
from src.amas.services.prometheus_metrics_service import (
    get_metrics_service, record_http_request, record_error
)

# Get metrics service
metrics_service = get_metrics_service()

# Record HTTP request
metrics_service.record_http_request(
    method="GET",
    endpoint="/api/users",
    status_code=200,
    duration=0.150,
    request_size=1024,
    response_size=2048
)

# Record error
metrics_service.record_error("validation_error", "user_service")
```

#### **Metric Types**
1. **HTTP Metrics**: Request count, duration, size
2. **Authentication Metrics**: Login attempts, failures
3. **Agent Metrics**: Agent executions, performance
4. **Task Metrics**: Task processing, duration
5. **System Metrics**: CPU, memory, disk usage
6. **Database Metrics**: Query count, duration
7. **Cache Metrics**: Hit ratio, operations
8. **Error Metrics**: Error count by type

#### **API Endpoint**
- **`/metrics`**: Prometheus metrics endpoint

#### **Configuration**
```python
# Environment variables
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
PROMETHEUS_METRICS_PATH=/metrics
```

---

### **7. Graceful Shutdown Service**

#### **Implementation**
- **File**: `src/amas/services/graceful_shutdown_service.py`
- **Purpose**: Production-ready graceful shutdown handling
- **Features**: Phased shutdown, connection draining, service priority, signal handling

#### **Key Features**
```python
from src.amas.services.graceful_shutdown_service import (
    GracefulShutdownService, ShutdownConfig, ServicePriority, ShutdownPhase
)

# Create shutdown service
shutdown_service = GracefulShutdownService(
    config=ShutdownConfig(
        shutdown_timeout=30.0,
        drain_timeout=10.0,
        service_timeout=5.0,
        force_shutdown_timeout=5.0,
        enable_health_checks=True,
        enable_metrics_collection=True,
        enable_audit_logging=True
    )
)

# Register services with priorities
shutdown_service.register_service(
    "database",
    shutdown_func=close_database_connections,
    priority=ServicePriority.CRITICAL
)

shutdown_service.register_service(
    "cache",
    shutdown_func=close_cache_connections,
    priority=ServicePriority.HIGH
)

# Register cleanup tasks
shutdown_service.register_cleanup_task(
    "cleanup_temp_files",
    cleanup_func=cleanup_temporary_files
)

# Initialize graceful shutdown handlers
shutdown_service.initialize()
```

#### **Shutdown Phases**
1. **INITIATED**: Shutdown signal received
2. **STOPPING_ACCEPTORS**: Stop accepting new requests
3. **DRAINING_CONNECTIONS**: Drain existing connections
4. **STOPPING_SERVICES**: Stop services in priority order
5. **CLEANING_UP**: Execute cleanup tasks
6. **COMPLETED**: Shutdown complete

#### **Configuration**
```python
# Environment variables
GRACEFUL_SHUTDOWN_ENABLED=true
GRACEFUL_SHUTDOWN_TIMEOUT=30.0
GRACEFUL_SHUTDOWN_DRAIN_TIMEOUT=10.0
GRACEFUL_SHUTDOWN_SERVICE_TIMEOUT=5.0
GRACEFUL_SHUTDOWN_FORCE_TIMEOUT=5.0
```

---

### **8. Timeout Service**

#### **Implementation**
- **File**: `src/amas/services/timeout_service.py`
- **Purpose**: Comprehensive timeout handling for all operations
- **Features**: Multiple timeout types, configurable timeouts, context managers

#### **Key Features**
```python
from src.amas.services.timeout_service import (
    TimeoutService, TimeoutConfig, TimeoutType, TimeoutException
)

# Create timeout service
timeout_service = TimeoutService(
    config=TimeoutConfig(
        default_timeout=30.0,
        timeouts={
            TimeoutType.HTTP_REQUEST: 30.0,
            TimeoutType.DATABASE_QUERY: 10.0,
            TimeoutType.CACHE_OPERATION: 5.0,
            TimeoutType.EXTERNAL_API: 60.0,
            TimeoutType.AGENT_EXECUTION: 300.0
        },
        enable_graceful_shutdown=True,
        max_timeout=300.0,
        min_timeout=0.1
    )
)

# Use timeout context manager
try:
    async with timeout_service.timeout(TimeoutType.HTTP_REQUEST, timeout=30.0):
        response = await make_http_request(url)
except TimeoutException:
    logger.warning("HTTP request timed out")
    # Handle timeout
```

#### **Timeout Types**
- **HTTP_REQUEST**: HTTP API calls
- **DATABASE_QUERY**: Database operations
- **CACHE_OPERATION**: Cache operations
- **EXTERNAL_API**: External API calls
- **FILE_OPERATION**: File I/O operations
- **AGENT_EXECUTION**: Agent execution tasks
- **TASK_EXECUTION**: Long-running tasks
- **GENERAL**: General operations

#### **Configuration**
```python
# Environment variables
TIMEOUT_ENABLED=true
TIMEOUT_DEFAULT=30.0
TIMEOUT_HTTP_REQUEST=30.0
TIMEOUT_DATABASE_QUERY=10.0
TIMEOUT_CACHE_OPERATION=5.0
TIMEOUT_EXTERNAL_API=60.0
TIMEOUT_AGENT_EXECUTION=300.0
TIMEOUT_TASK_EXECUTION=600.0
TIMEOUT_MAX=300.0
TIMEOUT_MIN=0.1
```

---

### **9. Retry Utilities**

#### **Implementation**
- **File**: `src/amas/utils/retry_utils.py`
- **Purpose**: Robust retry mechanisms with exponential backoff
- **Features**: Multiple retry strategies, configurable conditions, jitter support

#### **Key Features**
```python
from src.amas.utils.retry_utils import (
    retry_with_backoff, RetryConfig, RetryStrategy, RetryCondition
)

# Configure retry behavior
retry_config = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=60.0,
    strategy=RetryStrategy.EXPONENTIAL,
    jitter=True,
    backoff_multiplier=2.0,
    condition=RetryCondition.HTTP_ERRORS,
    exceptions=[ConnectionError, TimeoutError]
)

# Use retry decorator
@retry_with_backoff(config=retry_config)
async def call_external_api(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

# Use retry context manager
from src.amas.utils.retry_utils import RetryContext

async def process_with_retry():
    async with RetryContext(config=retry_config) as retry:
        while retry.should_retry():
            try:
                result = await call_external_api("https://api.example.com")
                retry.mark_success()
                return result
            except Exception as e:
                if retry.should_retry_exception(e):
                    await retry.wait_before_retry()
                else:
                    raise
```

#### **Retry Strategies**
- **FIXED**: Fixed delay between retries
- **EXPONENTIAL**: Exponential backoff (default)
- **LINEAR**: Linear increase in delay
- **CUSTOM**: Custom delay function

#### **Retry Conditions**
- **ANY_EXCEPTION**: Retry on any exception
- **HTTP_ERRORS**: Retry on HTTP errors (4xx, 5xx)
- **TIMEOUT_ERRORS**: Retry on timeout errors
- **CONNECTION_ERRORS**: Retry on connection errors
- **CUSTOM**: Custom condition function

#### **Configuration**
```python
# Environment variables
RETRY_MAX_ATTEMPTS=3
RETRY_BASE_DELAY=1.0
RETRY_MAX_DELAY=60.0
RETRY_STRATEGY=exponential
RETRY_JITTER=true
RETRY_BACKOFF_MULTIPLIER=2.0
```

---

### **10. Enhanced Authentication & Authorization**

#### **Implementation**
- **File**: `src/amas/security/enhanced_auth.py`
- **Purpose**: JWT/OIDC authentication with RBAC
- **Features**: Token management, role-based access, permission checks

#### **Key Features**
```python
from src.amas.security.enhanced_auth import (
    EnhancedAuthManager, User, UserRole, Permission,
    LoginRequest, TokenResponse, get_auth_manager,
    get_current_user, require_role, require_permission
)

# Initialize auth manager
auth_manager = get_auth_manager()

# Login
login_request = LoginRequest(username="user", password="pass")
token_response = await auth_manager.login(login_request, client_ip="127.0.0.1")

# Use in endpoints
from fastapi import APIRouter
router = APIRouter()

@router.get("/protected")
@require_role(UserRole.USER)
@require_permission(Permission.AGENT_READ)
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user.username}
```

#### **Authentication Features**
- **JWT Tokens**: Access and refresh token support
- **OIDC Integration**: OpenID Connect provider support
- **Password Hashing**: Secure password storage
- **Token Refresh**: Automatic token refresh
- **Session Management**: Session tracking and invalidation

#### **Authorization Features**
- **Role-Based Access**: User roles (Admin, User, Viewer, Analyst, Manager)
- **Permission-Based Access**: Fine-grained permissions
- **Resource Authorization**: Resource-level access control
- **Policy Enforcement**: Automatic policy checking

---

### **11. Rate Limiting Middleware**

#### **Implementation**
- **File**: `src/middleware/rate_limiting.py`
- **Purpose**: API rate limiting with token bucket algorithm
- **Features**: Per-IP, per-user, per-token rate limiting

#### **Key Features**
```python
from src.middleware.rate_limiting import (
    RateLimiter, RateLimitConfig, TokenBucket
)

# Create rate limiter
rate_limiter = RateLimiter(
    config=RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        burst_limit=10,
        window_size=60
    )
)

# Use in FastAPI
from fastapi import FastAPI, Request
app = FastAPI()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    if not await rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    response = await call_next(request)
    await rate_limiter.record_request(client_ip)
    return response
```

#### **Rate Limiting Types**
- **Per-IP**: Rate limit by client IP address
- **Per-User**: Rate limit by authenticated user
- **Per-Token**: Rate limit by API token
- **Global**: Global rate limiting

#### **Configuration**
```python
# Environment variables
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000
RATE_LIMIT_BURST_LIMIT=10
RATE_LIMIT_WINDOW_SIZE=60
```

---

## 🔧 **Integration Examples**

### **1. Complete Service Integration**

```python
from src.amas.services.enhanced_logging_service import get_logger, LoggingContext
from src.amas.services.health_check_service import add_health_check, check_health
from src.amas.services.circuit_breaker_service import get_circuit_breaker_service
from src.amas.services.prometheus_metrics_service import get_metrics_service

class MyService:
    def __init__(self):
        self.logger = get_logger("my_service")
        self.circuit_breaker = get_circuit_breaker_service().get_breaker("external_api")
        self.metrics = get_metrics_service()
        
        # Add health checks
        add_health_check("my_service", self._health_check)
    
    async def _health_check(self):
        """Health check implementation"""
        return {"status": "healthy", "uptime": self.get_uptime()}
    
    async def process_request(self, request_data):
        """Process request with full observability"""
        with LoggingContext(correlation_id=request_data.get("correlation_id")):
            try:
                # Log request
                self.logger.info("Processing request", 
                               action="process_request",
                               request_id=request_data.get("id"))
                
                # Process with circuit breaker
                result = await self.circuit_breaker.call(self._process_data, request_data)
                
                # Record metrics
                self.metrics.record_http_request(
                    method="POST",
                    endpoint="/process",
                    status_code=200,
                    duration=0.150
                )
                
                self.logger.info("Request processed successfully",
                               action="process_request",
                               status="success")
                
                return result
                
            except Exception as e:
                # Log error
                self.logger.error("Request processing failed",
                                action="process_request",
                                error=str(e))
                
                # Record error metrics
                self.metrics.record_error("processing_error", "my_service")
                
                raise
```

### **2. API Endpoint with Full Features**

```python
from fastapi import FastAPI, Depends
from src.amas.services.enhanced_logging_service import get_logger, LoggingContext
from src.amas.services.health_check_service import check_health
from src.amas.services.prometheus_metrics_service import get_metrics_service

app = FastAPI()
logger = get_logger("api")
metrics = get_metrics_service()

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

@app.get("/api/data")
async def get_data(correlation_id: str = None):
    with LoggingContext(correlation_id=correlation_id):
        logger.info("Fetching data", action="get_data")
        
        # Your business logic here
        data = {"message": "Hello World"}
        
        logger.info("Data fetched successfully", action="get_data", status="success")
        return data

@app.get("/health")
async def health():
    health_result = await check_health()
    return health_result
```

---

## 📊 **Monitoring and Observability**

### **1. Health Monitoring**

```python
# Check overall health
health_result = await check_health()
print(f"Status: {health_result['status']}")
print(f"Uptime: {health_result['uptime_seconds']}s")
print(f"Checks: {len(health_result['checks'])}")

# Check specific dependency
from src.amas.services.health_check_service import check_dependency_health
db_health = await check_dependency_health("database")
print(f"Database status: {db_health.status}")
```

### **2. Metrics Collection**

```python
# Custom metrics
metrics_service = get_metrics_service()

# Record business metrics
metrics_service.record_business_event("user_registration", value=1.0)

# Record performance metrics
metrics_service.record_performance("data_processing", duration_ms=150.0)

# Get metrics data
metrics_data = metrics_service.get_metrics()
```

### **3. Logging and Tracing**

```python
# Structured logging with context
with LoggingContext(correlation_id="req-123", user_id="user-456"):
    logger.info("User action", 
               action="purchase",
               amount=99.99,
               product_id="prod-123")
    
    # Nested operations inherit context
    await process_payment()
    await send_confirmation_email()
```

---

## 🔒 **Security Implementation**

### **1. Input Validation**

```python
from src.amas.errors.error_handling import (
    ValidationError, validate_required_fields, validate_email
)

def create_user(user_data):
    # Validate required fields
    validate_required_fields(user_data, ["email", "name", "password"])
    
    # Validate email format
    validate_email(user_data["email"])
    
    # Validate password strength
    if len(user_data["password"]) < 8:
        raise ValidationError("Password must be at least 8 characters")
    
    return process_user_creation(user_data)
```

### **2. Security Logging**

```python
from src.amas.services.enhanced_logging_service import security_logger

# Log security events
security_logger.log_authentication("user123", success=True, ip_address="192.168.1.1")
security_logger.log_authorization("user123", "admin_panel", "read", granted=True)
security_logger.log_security_event("suspicious_activity", severity="high")
```

### **3. Rate Limiting**

```python
from src.amas.middleware.rate_limiting import RateLimiter

# Create rate limiter
rate_limiter = RateLimiter(
    requests_per_minute=60,
    burst_size=10
)

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    if not rate_limiter.allow_request(request.client.host):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return await call_next(request)
```

---

## 🚀 **Best Practices**

### **1. Logging Best Practices**

```python
# Use structured logging
logger.info("User action performed",
           action="login",
           user_id=user_id,
           ip_address=ip_address,
           success=True)

# Use appropriate log levels
logger.debug("Detailed debug information")
logger.info("Normal operation information")
logger.warning("Warning condition")
logger.error("Error condition")
logger.critical("Critical error")

# Use correlation IDs for tracing
with LoggingContext(correlation_id=request_id):
    # All logs in this context will include the correlation ID
    pass
```

### **2. Error Handling Best Practices**

```python
# Use specific exception types
from src.amas.errors.error_handling import (
    ValidationError, AuthenticationError, AuthorizationError
)

try:
    validate_user_input(data)
except ValidationError as e:
    logger.warning("Validation failed", error=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except AuthenticationError as e:
    logger.warning("Authentication failed", error=str(e))
    raise HTTPException(status_code=401, detail=str(e))
```

### **3. Health Check Best Practices**

```python
# Add health checks for all dependencies
add_database_health_check("main_db", get_database_connection)
add_cache_health_check("redis", get_redis_client)
add_external_api_health_check("payment_api", "https://api.payment.com", check_payment_api)

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

### **4. Metrics Best Practices**

```python
# Record metrics for all important operations
metrics.record_http_request(method, endpoint, status_code, duration)
metrics.record_database_query(database, operation, status, duration)
metrics.record_business_event("order_created", value=order_amount)

# Use consistent metric names
# Good: user_registrations_total
# Bad: userRegistrations, user_registrations, UserRegistrations
```

---

## 🔧 **Configuration Management**

### **1. Environment Variables**

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_SECURITY_LEVEL=medium
LOG_ENABLE_CORRELATION=true

# Health Checks
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=5

# Metrics
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# Circuit Breakers
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5

# Error Recovery
ERROR_RECOVERY_ENABLED=true
ERROR_RECOVERY_MAX_RETRIES=3
```

### **2. Configuration Files**

```yaml
# config/logging.yaml
logging:
  level: INFO
  format: json
  security_level: medium
  enable_correlation: true
  enable_metrics: true
  enable_audit: true

# config/health.yaml
health:
  enabled: true
  interval: 30
  timeout: 5
  checks:
    - name: database
      type: database
      timeout: 5
    - name: redis
      type: cache
      timeout: 3

# config/metrics.yaml
metrics:
  prometheus:
    enabled: true
    port: 9090
    path: /metrics
  custom_metrics:
    enabled: true
    interval: 60
```

---

## 📚 **Troubleshooting**

### **1. Common Issues**

#### **Project Root Not Found**
```python
# Check if you're in a valid project directory
from src.amas.utils.project_root import validate_project_structure
is_valid = validate_project_structure(".")
if not is_valid:
    print("Not in a valid project directory")
```

#### **Health Check Failures**
```python
# Check specific health check
from src.amas.services.health_check_service import check_dependency_health
result = await check_dependency_health("database")
print(f"Database health: {result.status} - {result.message}")
```

#### **Circuit Breaker Open**
```python
# Check circuit breaker status
from src.amas.services.circuit_breaker_service import get_circuit_breaker_service
service = get_circuit_breaker_service()
breaker = service.get_breaker("external_api")
print(f"Circuit breaker state: {breaker.state}")
print(f"Statistics: {breaker.get_stats()}")
```

### **2. Debug Mode**

```python
# Enable debug logging
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Enable detailed health checks
health_result = await check_health()
print(json.dumps(health_result, indent=2))
```

### **3. Performance Monitoring**

```python
# Monitor performance metrics
metrics_service = get_metrics_service()
metrics_data = metrics_service.get_metrics()
print(metrics_data)
```

---

## 🎯 **Conclusion**

This implementation guide provides comprehensive documentation for all Phase 2 enhancements. The system now includes enterprise-grade reliability, security, and observability features that make it production-ready for any organization.

Key benefits:
- **Enhanced Reliability**: Circuit breakers, retry policies, error recovery, graceful shutdown, timeout handling
- **Comprehensive Security**: JWT/OIDC authentication, RBAC authorization, rate limiting, input validation, audit logging, PII redaction
- **Full Observability**: Structured logging, Prometheus metrics, health monitoring, distributed tracing
- **Easy Integration**: Simple APIs and configuration options
- **Production Ready**: Enterprise-grade features and best practices

## 📋 **Phase 2 Complete Feature List**

### **Core Services (11 Total)**
1. ✅ **Enhanced Logging Service** - Structured logging with security
2. ✅ **Health Check Service** - Comprehensive health monitoring
3. ✅ **Circuit Breaker Service** - Fault tolerance for external services
4. ✅ **Error Recovery Service** - Automated error recovery
5. ✅ **Prometheus Metrics Service** - Metrics collection
6. ✅ **Structured Logging Service** - JSON logging with correlation
7. ✅ **Graceful Shutdown Service** - Production shutdown handling
8. ✅ **Timeout Service** - Comprehensive timeout management
9. ✅ **Retry Utilities** - Robust retry mechanisms
10. ✅ **Enhanced Authentication** - JWT/OIDC with RBAC
11. ✅ **Rate Limiting Middleware** - API rate limiting

### **Infrastructure Components**
- ✅ **Universal AI Router** - Multi-provider failover
- ✅ **Project Root Utilities** - Secure project detection
- ✅ **Error Handling** - Comprehensive error management
- ✅ **Security Middleware** - Request security
- ✅ **Auth API Routes** - Authentication endpoints

For additional support or questions, refer to the troubleshooting section or create an issue in the repository.