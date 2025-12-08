# **🎯 AMAS PROJECT: PART 6 - MONITORING & OBSERVABILITY**
## **Complete Prometheus, Grafana, OpenTelemetry Integration**

***

## **PHASE 4: MONITORING & OBSERVABILITY LAYER**

### **Step 6.1: Prometheus Metrics Service**

**File**: `src/amas/services/prometheus_metrics_service.py` (ENHANCE EXISTING)

**CURRENT STATE**: Basic Prometheus initialization exists but metrics are not being collected.

**REQUIRED PRODUCTION IMPLEMENTATION**:

```python
# src/amas/services/prometheus_metrics_service.py (PRODUCTION-READY)
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
from typing import Dict, Any, Optional
import logging
import time
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

class PrometheusMetricsService:
    """
    Production-grade Prometheus metrics collection
    
    ✅ Task execution metrics
    ✅ Agent performance metrics
    ✅ AI provider metrics
    ✅ API endpoint metrics
    ✅ Database metrics
    ✅ System resource metrics
    ✅ Custom business metrics
    """
    
    def __init__(self, registry: CollectorRegistry = None):
        self.registry = registry or CollectorRegistry()
        
        # Initialize all metrics
        self._init_task_metrics()
        self._init_agent_metrics()
        self._init_ai_provider_metrics()
        self._init_api_metrics()
        self._init_database_metrics()
        self._init_system_metrics()
        self._init_business_metrics()
        
        logger.info("PrometheusMetricsService initialized")
    
    def _init_task_metrics(self):
        """Initialize task-related metrics"""
        
        # Task execution counter
        self.task_executions_total = Counter(
            'amas_task_executions_total',
            'Total number of task executions',
            ['task_type', 'status'],
            registry=self.registry
        )
        
        # Task duration histogram
        self.task_duration_seconds = Histogram(
            'amas_task_duration_seconds',
            'Task execution duration in seconds',
            ['task_type'],
            buckets=[0.5, 1, 2, 5, 10, 30, 60, 120, 300, 600],
            registry=self.registry
        )
        
        # Task success rate gauge
        self.task_success_rate = Gauge(
            'amas_task_success_rate',
            'Task success rate (0.0-1.0)',
            ['task_type'],
            registry=self.registry
        )
        
        # Task quality score gauge
        self.task_quality_score = Gauge(
            'amas_task_quality_score',
            'Task quality score (0.0-1.0)',
            ['task_type'],
            registry=self.registry
        )
        
        # Active tasks gauge
        self.tasks_active = Gauge(
            'amas_tasks_active',
            'Number of currently executing tasks',
            ['task_type'],
            registry=self.registry
        )
        
        # Task queue depth gauge
        self.task_queue_depth = Gauge(
            'amas_task_queue_depth',
            'Number of tasks waiting in queue',
            ['priority'],
            registry=self.registry
        )
        
        # Task errors counter
        self.task_errors_total = Counter(
            'amas_task_errors_total',
            'Total number of task errors',
            ['task_type', 'error_type'],
            registry=self.registry
        )
    
    def _init_agent_metrics(self):
        """Initialize agent-related metrics"""
        
        # Agent executions counter
        self.agent_executions_total = Counter(
            'amas_agent_executions_total',
            'Total number of agent executions',
            ['agent_id', 'agent_name', 'status'],
            registry=self.registry
        )
        
        # Agent duration histogram
        self.agent_duration_seconds = Histogram(
            'amas_agent_duration_seconds',
            'Agent execution duration in seconds',
            ['agent_id', 'agent_name'],
            buckets=[0.5, 1, 2, 5, 10, 30, 60, 120],
            registry=self.registry
        )
        
        # Agent utilization gauge
        self.agent_utilization = Gauge(
            'amas_agent_utilization',
            'Agent utilization percentage (0.0-1.0)',
            ['agent_id', 'agent_name'],
            registry=self.registry
        )
        
        # Agent success rate gauge
        self.agent_success_rate = Gauge(
            'amas_agent_success_rate',
            'Agent success rate (0.0-1.0)',
            ['agent_id', 'agent_name'],
            registry=self.registry
        )
        
        # Agent tokens used counter
        self.agent_tokens_total = Counter(
            'amas_agent_tokens_total',
            'Total tokens used by agent',
            ['agent_id', 'agent_name'],
            registry=self.registry
        )
        
        # Agent cost counter
        self.agent_cost_usd_total = Counter(
            'amas_agent_cost_usd_total',
            'Total cost in USD for agent',
            ['agent_id', 'agent_name'],
            registry=self.registry
        )
    
    def _init_ai_provider_metrics(self):
        """Initialize AI provider metrics"""
        
        # Provider API calls counter
        self.ai_provider_calls_total = Counter(
            'amas_ai_provider_calls_total',
            'Total AI provider API calls',
            ['provider', 'model', 'status'],
            registry=self.registry
        )
        
        # Provider latency histogram
        self.ai_provider_latency_seconds = Histogram(
            'amas_ai_provider_latency_seconds',
            'AI provider response latency in seconds',
            ['provider', 'model'],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30],
            registry=self.registry
        )
        
        # Provider tokens counter
        self.ai_provider_tokens_total = Counter(
            'amas_ai_provider_tokens_total',
            'Total tokens used per provider',
            ['provider', 'model'],
            registry=self.registry
        )
        
        # Provider cost counter
        self.ai_provider_cost_usd_total = Counter(
            'amas_ai_provider_cost_usd_total',
            'Total cost in USD per provider',
            ['provider', 'model'],
            registry=self.registry
        )
        
        # Provider fallback counter
        self.ai_provider_fallbacks_total = Counter(
            'amas_ai_provider_fallbacks_total',
            'Total provider fallbacks',
            ['from_provider', 'to_provider'],
            registry=self.registry
        )
        
        # Provider circuit breaker state gauge
        self.ai_provider_circuit_breaker_state = Gauge(
            'amas_ai_provider_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half-open)',
            ['provider'],
            registry=self.registry
        )
    
    def _init_api_metrics(self):
        """Initialize API endpoint metrics"""
        
        # HTTP requests counter
        self.http_requests_total = Counter(
            'amas_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        # HTTP request duration histogram
        self.http_request_duration_seconds = Histogram(
            'amas_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
            registry=self.registry
        )
        
        # Active HTTP requests gauge
        self.http_requests_active = Gauge(
            'amas_http_requests_active',
            'Number of active HTTP requests',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # WebSocket connections gauge
        self.websocket_connections_active = Gauge(
            'amas_websocket_connections_active',
            'Number of active WebSocket connections',
            registry=self.registry
        )
    
    def _init_database_metrics(self):
        """Initialize database metrics"""
        
        # Database queries counter
        self.db_queries_total = Counter(
            'amas_db_queries_total',
            'Total database queries',
            ['operation', 'table', 'status'],
            registry=self.registry
        )
        
        # Database query duration histogram
        self.db_query_duration_seconds = Histogram(
            'amas_db_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5],
            registry=self.registry
        )
        
        # Database connection pool gauge
        self.db_pool_connections = Gauge(
            'amas_db_pool_connections',
            'Database connection pool status',
            ['state'],  # active, idle, total
            registry=self.registry
        )
        
        # Cache hit rate gauge
        self.cache_hit_rate = Gauge(
            'amas_cache_hit_rate',
            'Cache hit rate (0.0-1.0)',
            ['cache_type'],  # redis, memory
            registry=self.registry
        )
        
        # Cache operations counter
        self.cache_operations_total = Counter(
            'amas_cache_operations_total',
            'Total cache operations',
            ['operation', 'result'],  # get/set/delete, hit/miss/success/error
            registry=self.registry
        )
    
    def _init_system_metrics(self):
        """Initialize system resource metrics"""
        
        # CPU usage gauge
        self.system_cpu_usage_percent = Gauge(
            'amas_system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        # Memory usage gauge
        self.system_memory_usage_bytes = Gauge(
            'amas_system_memory_usage_bytes',
            'System memory usage in bytes',
            registry=self.registry
        )
        
        # Memory usage percentage gauge
        self.system_memory_usage_percent = Gauge(
            'amas_system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )
        
        # Disk usage gauge
        self.system_disk_usage_bytes = Gauge(
            'amas_system_disk_usage_bytes',
            'System disk usage in bytes',
            ['mount_point'],
            registry=self.registry
        )
        
        # Network I/O counter
        self.system_network_io_bytes_total = Counter(
            'amas_system_network_io_bytes_total',
            'Total network I/O in bytes',
            ['direction'],  # sent, received
            registry=self.registry
        )
    
    def _init_business_metrics(self):
        """Initialize business/custom metrics"""
        
        # ML prediction accuracy gauge
        self.ml_prediction_accuracy = Gauge(
            'amas_ml_prediction_accuracy',
            'ML model prediction accuracy (0.0-1.0)',
            ['model_name'],
            registry=self.registry
        )
        
        # ML model training counter
        self.ml_model_training_total = Counter(
            'amas_ml_model_training_total',
            'Total ML model training runs',
            ['model_name'],
            registry=self.registry
        )
        
        # Integration triggers counter
        self.integration_triggers_total = Counter(
            'amas_integration_triggers_total',
            'Total integration triggers',
            ['platform', 'event_type', 'status'],
            registry=self.registry
        )
        
        # User activity counter
        self.user_logins_total = Counter(
            'amas_user_logins_total',
            'Total user logins',
            ['status'],  # success, failure
            registry=self.registry
        )
        
        # Active users gauge
        self.users_active = Gauge(
            'amas_users_active',
            'Number of active users',
            registry=self.registry
        )
    
    # ========================================================================
    # METRIC RECORDING METHODS
    # ========================================================================
    
    def record_task_execution(
        self,
        task_id: str,
        task_type: str,
        status: str,
        duration: float,
        success_rate: float = None,
        quality_score: float = None,
        error_type: str = None
    ):
        """Record task execution metrics"""
        
        # Increment counter
        self.task_executions_total.labels(
            task_type=task_type,
            status=status
        ).inc()
        
        # Record duration
        self.task_duration_seconds.labels(
            task_type=task_type
        ).observe(duration)
        
        # Update success rate
        if success_rate is not None:
            self.task_success_rate.labels(
                task_type=task_type
            ).set(success_rate)
        
        # Update quality score
        if quality_score is not None:
            self.task_quality_score.labels(
                task_type=task_type
            ).set(quality_score)
        
        # Record error if present
        if error_type:
            self.task_errors_total.labels(
                task_type=task_type,
                error_type=error_type
            ).inc()
        
        logger.debug(f"Recorded task metrics: {task_id} ({task_type}) - {status}")
    
    def record_agent_execution(
        self,
        agent_id: str,
        agent_name: str,
        status: str,
        duration: float,
        tokens_used: int = 0,
        cost_usd: float = 0.0
    ):
        """Record agent execution metrics"""
        
        # Increment counter
        self.agent_executions_total.labels(
            agent_id=agent_id,
            agent_name=agent_name,
            status=status
        ).inc()
        
        # Record duration
        self.agent_duration_seconds.labels(
            agent_id=agent_id,
            agent_name=agent_name
        ).observe(duration)
        
        # Record tokens
        if tokens_used > 0:
            self.agent_tokens_total.labels(
                agent_id=agent_id,
                agent_name=agent_name
            ).inc(tokens_used)
        
        # Record cost
        if cost_usd > 0:
            self.agent_cost_usd_total.labels(
                agent_id=agent_id,
                agent_name=agent_name
            ).inc(cost_usd)
        
        logger.debug(f"Recorded agent metrics: {agent_name} - {status}")
    
    def record_ai_provider_call(
        self,
        provider: str,
        model: str,
        status: str,
        latency: float,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        fallback_from: str = None
    ):
        """Record AI provider API call metrics"""
        
        # Increment call counter
        self.ai_provider_calls_total.labels(
            provider=provider,
            model=model,
            status=status
        ).inc()
        
        # Record latency
        self.ai_provider_latency_seconds.labels(
            provider=provider,
            model=model
        ).observe(latency / 1000)  # Convert ms to seconds
        
        # Record tokens
        if tokens_used > 0:
            self.ai_provider_tokens_total.labels(
                provider=provider,
                model=model
            ).inc(tokens_used)
        
        # Record cost
        if cost_usd > 0:
            self.ai_provider_cost_usd_total.labels(
                provider=provider,
                model=model
            ).inc(cost_usd)
        
        # Record fallback if occurred
        if fallback_from:
            self.ai_provider_fallbacks_total.labels(
                from_provider=fallback_from,
                to_provider=provider
            ).inc()
        
        logger.debug(f"Recorded AI provider metrics: {provider}/{model} - {status}")
    
    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ):
        """Record HTTP request metrics"""
        
        # Increment counter
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        # Record duration
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        logger.debug(f"Recorded HTTP metrics: {method} {endpoint} - {status_code}")
    
    def record_db_query(
        self,
        operation: str,
        table: str,
        status: str,
        duration: float
    ):
        """Record database query metrics"""
        
        # Increment counter
        self.db_queries_total.labels(
            operation=operation,
            table=table,
            status=status
        ).inc()
        
        # Record duration
        self.db_query_duration_seconds.labels(
            operation=operation,
            table=table
        ).observe(duration)
        
        logger.debug(f"Recorded DB metrics: {operation} on {table} - {status}")
    
    def update_system_resources(
        self,
        cpu_percent: float,
        memory_bytes: int,
        memory_percent: float
    ):
        """Update system resource metrics"""
        
        self.system_cpu_usage_percent.set(cpu_percent)
        self.system_memory_usage_bytes.set(memory_bytes)
        self.system_memory_usage_percent.set(memory_percent)
    
    def record_integration_trigger(
        self,
        platform: str,
        event_type: str,
        status: str
    ):
        """Record integration trigger metrics"""
        
        self.integration_triggers_total.labels(
            platform=platform,
            event_type=event_type,
            status=status
        ).inc()
    
    # ========================================================================
    # DECORATOR FOR AUTOMATIC METRIC COLLECTION
    # ========================================================================
    
    def track_execution(self, metric_type: str = "task"):
        """
        Decorator to automatically track execution metrics
        
        Usage:
            @metrics_service.track_execution(metric_type="agent")
            async def my_agent_function():
                ...
        """
        
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"
                error_type = None
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "error"
                    error_type = type(e).__name__
                    raise
                finally:
                    duration = time.time() - start_time
                    
                    # Extract identifiers from function arguments or result
                    # (This is a simplified example - customize based on your needs)
                    if metric_type == "task":
                        task_type = kwargs.get("task_type", "unknown")
                        self.record_task_execution(
                            task_id=kwargs.get("task_id", "unknown"),
                            task_type=task_type,
                            status=status,
                            duration=duration,
                            error_type=error_type
                        )
                    elif metric_type == "agent":
                        agent_id = kwargs.get("agent_id", "unknown")
                        agent_name = kwargs.get("agent_name", "unknown")
                        self.record_agent_execution(
                            agent_id=agent_id,
                            agent_name=agent_name,
                            status=status,
                            duration=duration
                        )
            
            return wrapper
        return decorator
    
    # ========================================================================
    # METRICS EXPORT
    # ========================================================================
    
    def get_metrics(self) -> bytes:
        """
        Get metrics in Prometheus format
        
        Returns:
            Metrics in Prometheus text format
        """
        return generate_latest(self.registry)
    
    def get_content_type(self) -> str:
        """Get Prometheus content type"""
        return CONTENT_TYPE_LATEST


# Global metrics service instance
_metrics_service: Optional[PrometheusMetricsService] = None

def get_metrics_service() -> PrometheusMetricsService:
    """Get global metrics service"""
    
    global _metrics_service
    
    if _metrics_service is None:
        _metrics_service = PrometheusMetricsService()
    
    return _metrics_service
```

***

### **Step 6.2: Prometheus Metrics Endpoint**

**File**: `src/api/routes/metrics.py` (CREATE NEW)

```python
# src/api/routes/metrics.py (PROMETHEUS METRICS ENDPOINT)
from fastapi import APIRouter, Response, Depends
from src.amas.services.prometheus_metrics_service import get_metrics_service

router = APIRouter()

@router.get("/metrics")
async def prometheus_metrics(
    metrics_service = Depends(get_metrics_service)
):
    """
    Prometheus metrics endpoint
    
    This endpoint is scraped by Prometheus server
    Format: Prometheus text exposition format
    """
    
    metrics_data = metrics_service.get_metrics()
    
    return Response(
        content=metrics_data,
        media_type=metrics_service.get_content_type()
    )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    
    Used by Kubernetes liveness/readiness probes
    """
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "amas-backend"
    }
```

**Register in main app**:

```python
# src/api/main.py (ADD)
from src.api.routes import metrics

app.include_router(
    metrics.router,
    tags=["Monitoring"]
)
```

***

### **Step 6.3: FastAPI Middleware for Automatic Metrics**

**File**: `src/api/middleware/metrics_middleware.py` (CREATE NEW)

```python
# src/api/middleware/metrics_middleware.py (AUTO-METRICS MIDDLEWARE)
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from src.amas.services.prometheus_metrics_service import get_metrics_service

logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically collect HTTP request metrics
    
    ✅ Request counter
    ✅ Request duration
    ✅ Active requests
    ✅ Status code distribution
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.metrics_service = get_metrics_service()
    
    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Extract endpoint pattern (remove path parameters)
        endpoint = request.url.path
        method = request.method
        
        # Increment active requests
        self.metrics_service.http_requests_active.labels(
            method=method,
            endpoint=endpoint
        ).inc()
        
        # Record request start time
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            
            self.metrics_service.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
        
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            
            self.metrics_service.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=500,
                duration=duration
            )
            
            raise
        
        finally:
            # Decrement active requests
            self.metrics_service.http_requests_active.labels(
                method=method,
                endpoint=endpoint
            ).dec()
```

**Register middleware in main app**:

```python
# src/api/main.py (ADD)
from src.api.middleware.metrics_middleware import MetricsMiddleware

app.add_middleware(MetricsMiddleware)
```

***

### **Step 6.4: System Resource Monitoring**

**File**: `src/amas/services/system_monitor.py` (CREATE NEW)

```python
# src/amas/services/system_monitor.py (SYSTEM RESOURCE MONITORING)
import asyncio
import psutil
import logging
from typing import Dict, Any
from src.amas.services.prometheus_metrics_service import get_metrics_service

logger = logging.getLogger(__name__)

class SystemMonitor:
    """
    System resource monitoring service
    
    ✅ CPU usage tracking
    ✅ Memory usage tracking
    ✅ Disk usage tracking
    ✅ Network I/O tracking
    ✅ Process monitoring
    """
    
    def __init__(self, update_interval: int = 15):
        self.update_interval = update_interval
        self.metrics_service = get_metrics_service()
        self.running = False
    
    async def start(self):
        """Start system monitoring"""
        
        if self.running:
            logger.warning("System monitor already running")
            return
        
        self.running = True
        logger.info("Starting system monitor")
        
        asyncio.create_task(self._monitor_loop())
    
    async def stop(self):
        """Stop system monitoring"""
        
        self.running = False
        logger.info("Stopping system monitor")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        
        while self.running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"System monitoring error: {e}", exc_info=True)
                await asyncio.sleep(self.update_interval)
    
    async def _collect_metrics(self):
        """Collect all system metrics"""
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics_service.system_cpu_usage_percent.set(cpu_percent)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics_service.system_memory_usage_bytes.set(memory.used)
        self.metrics_service.system_memory_usage_percent.set(memory.percent)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self.metrics_service.system_disk_usage_bytes.labels(
            mount_point='/'
        ).set(disk.used)
        
        # Network I/O metrics
        net_io = psutil.net_io_counters()
        self.metrics_service.system_network_io_bytes_total.labels(
            direction='sent'
        ).inc(net_io.bytes_sent)
        self.metrics_service.system_network_io_bytes_total.labels(
            direction='received'
        ).inc(net_io.bytes_recv)
        
        logger.debug(f"System metrics collected: CPU={cpu_percent}%, Memory={memory.percent}%")
    
    async def get_snapshot(self) -> Dict[str, Any]:
        """
        Get current system metrics snapshot
        
        Returns:
            Dict with current system state
        """
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        }


# Global system monitor instance
_system_monitor: Optional[SystemMonitor] = None

def get_system_monitor() -> SystemMonitor:
    """Get global system monitor"""
    
    global _system_monitor
    
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    
    return _system_monitor
```

**Start system monitor on app startup**:

```python
# src/api/main.py (ADD)
from src.amas.services.system_monitor import get_system_monitor

@app.on_event("startup")
async def start_system_monitor():
    system_monitor = get_system_monitor()
    await system_monitor.start()
    logger.info("System monitor started")

@app.on_event("shutdown")
async def stop_system_monitor():
    system_monitor = get_system_monitor()
    await system_monitor.stop()
    logger.info("System monitor stopped")
```

***

### **Step 6.5: Prometheus Configuration**

**File**: `monitoring/prometheus/prometheus.yml` (CREATE NEW)

```yaml
# monitoring/prometheus/prometheus.yml
# Prometheus configuration for AMAS

global:
  scrape_interval: 15s      # How often to scrape targets
  evaluation_interval: 15s   # How often to evaluate rules
  external_labels:
    cluster: 'amas-production'
    environment: 'production'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Load rules once and periodically evaluate them
rule_files:
  - "/etc/prometheus/rules/*.yml"

# Scrape configurations
scrape_configs:
  # AMAS Backend API
  - job_name: 'amas-backend'
    static_configs:
      - targets:
          - 'amas-backend:8000'
    metrics_path: '/metrics'
    scrape_interval: 10s
    scrape_timeout: 5s

  # AMAS Worker Nodes (if distributed)
  - job_name: 'amas-workers'
    static_configs:
      - targets:
          - 'amas-worker-1:8000'
          - 'amas-worker-2:8000'
          - 'amas-worker-3:8000'
    metrics_path: '/metrics'
    scrape_interval: 15s

  # PostgreSQL Exporter
  - job_name: 'postgres'
    static_configs:
      - targets:
          - 'postgres-exporter:9187'
    scrape_interval: 30s

  # Redis Exporter
  - job_name: 'redis'
    static_configs:
      - targets:
          - 'redis-exporter:9121'
    scrape_interval: 30s

  # Node Exporter (System metrics)
  - job_name: 'node-exporter'
    static_configs:
      - targets:
          - 'node-exporter:9100'
    scrape_interval: 15s

  # cAdvisor (Container metrics)
  - job_name: 'cadvisor'
    static_configs:
      - targets:
          - 'cadvisor:8080'
    scrape_interval: 15s

  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets:
          - 'localhost:9090'
    scrape_interval: 30s
```

***

### **Step 6.6: Alerting Rules**

**File**: `monitoring/prometheus/rules/alerts.yml` (CREATE NEW)

```yaml
# monitoring/prometheus/rules/alerts.yml
# Prometheus alerting rules for AMAS

groups:
  # Task Execution Alerts
  - name: task_alerts
    interval: 30s
    rules:
      - alert: HighTaskFailureRate
        expr: |
          rate(amas_task_executions_total{status="failed"}[5m]) 
          / 
          rate(amas_task_executions_total[5m]) 
          > 0.2
        for: 5m
        labels:
          severity: warning
          component: task-execution
        annotations:
          summary: "High task failure rate detected"
          description: "Task failure rate is {{ $value | humanizePercentage }} over the last 5 minutes"
      
      - alert: TaskQueueBacklog
        expr: amas_task_queue_depth > 100
        for: 10m
        labels:
          severity: warning
          component: task-queue
        annotations:
          summary: "Task queue backlog detected"
          description: "Task queue has {{ $value }} pending tasks"
      
      - alert: SlowTaskExecution
        expr: |
          histogram_quantile(0.95, 
            rate(amas_task_duration_seconds_bucket[5m])
          ) > 300
        for: 5m
        labels:
          severity: warning
          component: task-execution
        annotations:
          summary: "Slow task execution detected"
          description: "95th percentile task duration is {{ $value }} seconds"

  # Agent Performance Alerts
  - name: agent_alerts
    interval: 30s
    rules:
      - alert: AgentHighErrorRate
        expr: |
          rate(amas_agent_executions_total{status="error"}[5m]) 
          / 
          rate(amas_agent_executions_total[5m]) 
          > 0.15
        for: 5m
        labels:
          severity: warning
          component: agent
        annotations:
          summary: "High agent error rate for {{ $labels.agent_name }}"
          description: "Agent {{ $labels.agent_name }} has {{ $value | humanizePercentage }} error rate"
      
      - alert: AgentHighCost
        expr: |
          rate(amas_agent_cost_usd_total[1h]) > 10
        for: 15m
        labels:
          severity: info
          component: agent-cost
        annotations:
          summary: "High agent cost detected"
          description: "Agent {{ $labels.agent_name }} is costing ${{ $value }}/hour"

  # AI Provider Alerts
  - name: ai_provider_alerts
    interval: 30s
    rules:
      - alert: AIProviderDown
        expr: |
          rate(amas_ai_provider_calls_total{status="error"}[5m]) 
          / 
          rate(amas_ai_provider_calls_total[5m]) 
          > 0.5
        for: 3m
        labels:
          severity: critical
          component: ai-provider
        annotations:
          summary: "AI provider {{ $labels.provider }} may be down"
          description: "Provider {{ $labels.provider }} has {{ $value | humanizePercentage }} error rate"
      
      - alert: AIProviderHighLatency
        expr: |
          histogram_quantile(0.95, 
            rate(amas_ai_provider_latency_seconds_bucket[5m])
          ) > 10
        for: 5m
        labels:
          severity: warning
          component: ai-provider
        annotations:
          summary: "High AI provider latency"
          description: "Provider {{ $labels.provider }} has {{ $value }}s latency (95th percentile)"
      
      - alert: AIProviderCircuitBreakerOpen
        expr: amas_ai_provider_circuit_breaker_state == 1
        for: 1m
        labels:
          severity: critical
          component: ai-provider
        annotations:
          summary: "Circuit breaker open for {{ $labels.provider }}"
          description: "Provider {{ $labels.provider }} circuit breaker is OPEN"

  # System Resource Alerts
  - name: system_alerts
    interval: 30s
    rules:
      - alert: HighCPUUsage
        expr: amas_system_cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
          component: system
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}%"
      
      - alert: CriticalCPUUsage
        expr: amas_system_cpu_usage_percent > 95
        for: 2m
        labels:
          severity: critical
          component: system
        annotations:
          summary: "Critical CPU usage"
          description: "CPU usage is {{ $value }}%"
      
      - alert: HighMemoryUsage
        expr: amas_system_memory_usage_percent > 85
        for: 5m
        labels:
          severity: warning
          component: system
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"
      
      - alert: CriticalMemoryUsage
        expr: amas_system_memory_usage_percent > 95
        for: 2m
        labels:
          severity: critical
          component: system
        annotations:
          summary: "Critical memory usage"
          description: "Memory usage is {{ $value }}%"

  # Database Alerts
  - name: database_alerts
    interval: 30s
    rules:
      - alert: SlowDatabaseQueries
        expr: |
          histogram_quantile(0.95, 
            rate(amas_db_query_duration_seconds_bucket[5m])
          ) > 1
        for: 5m
        labels:
          severity: warning
          component: database
        annotations:
          summary: "Slow database queries"
          description: "95th percentile query time is {{ $value }} seconds"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: amas_db_pool_connections{state="idle"} < 2
        for: 2m
        labels:
          severity: critical
          component: database
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Only {{ $value }} idle connections remaining"
      
      - alert: LowCacheHitRate
        expr: amas_cache_hit_rate < 0.7
        for: 10m
        labels:
          severity: info
          component: cache
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value | humanizePercentage }}"

  # API Alerts
  - name: api_alerts
    interval: 30s
    rules:
      - alert: HighAPIErrorRate
        expr: |
          rate(amas_http_requests_total{status_code=~"5.."}[5m]) 
          / 
          rate(amas_http_requests_total[5m]) 
          > 0.05
        for: 3m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "High API error rate"
          description: "API error rate is {{ $value | humanizePercentage }}"
      
      - alert: SlowAPIResponses
        expr: |
          histogram_quantile(0.95, 
            rate(amas_http_request_duration_seconds_bucket[5m])
          ) > 2
        for: 5m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "Slow API responses"
          description: "95th percentile response time is {{ $value }} seconds"
```

***

### **Step 6.7: Grafana Dashboards**

**File**: `monitoring/grafana/dashboards/amas-overview.json` (CREATE NEW)

```json
{
  "dashboard": {
    "title": "AMAS - System Overview",
    "tags": ["amas", "overview"],
    "timezone": "browser",
    "schemaVersion": 16,
    "version": 1,
    "refresh": "30s",
    "panels": [
      {
        "id": 1,
        "title": "Task Execution Rate",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "rate(amas_task_executions_total[5m])",
            "legendFormat": "{{task_type}} - {{status}}"
          }
        ]
      },
      {
        "id": 2,
        "title": "Task Success Rate",
        "type": "gauge",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "targets": [
          {
            "expr": "avg(amas_task_success_rate)"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 1,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 0.7},
                {"color": "green", "value": 0.9}
              ]
            }
          }
        }
      },
      {
        "id": 3,
        "title": "CPU Usage",
        "type": "graph",
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 8},
        "targets": [
          {
            "expr": "amas_system_cpu_usage_percent",
            "legendFormat": "CPU %"
          }
        ]
      },
      {
        "id": 4,
        "title": "Memory Usage",
        "type": "graph",
        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 8},
        "targets": [
          {
            "expr": "amas_system_memory_usage_percent",
            "legendFormat": "Memory %"
          }
        ]
      },
      {
        "id": 5,
        "title": "Active Tasks",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 8},
        "targets": [
          {
            "expr": "sum(amas_tasks_active)"
          }
        ]
      },
      {
        "id": 6,
        "title": "Queue Depth",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 8},
        "targets": [
          {
            "expr": "sum(amas_task_queue_depth)"
          }
        ]
      }
    ]
  }
}
```

***

**This completes Part 6 - Monitoring & Observability (First Section)**

**What's Implemented**:
1. ✅ Complete Prometheus metrics service (50+ metrics)
2. ✅ Automatic HTTP request tracking middleware
3. ✅ System resource monitoring
4. ✅ Prometheus configuration
5. ✅ Alerting rules (15+ alerts)
6. ✅ Grafana dashboard template

**Still Needed**:
- OpenTelemetry tracing integration
- Grafana complete dashboard set
- Docker Compose monitoring stack
- Log aggregation (ELK/Loki)

and this are the Part 6B:
- **Part 6B**: OpenTelemetry Tracing + Complete Monitoring Stack
# **🎯 AMAS PROJECT: PART 6B - OPENTELEMETRY TRACING + COMPLETE MONITORING STACK**
## **Distributed Tracing, Log Aggregation & Complete Observability**

***

## **PART 6B: OPENTELEMETRY & COMPLETE OBSERVABILITY**

### **Step 6B.1: OpenTelemetry Tracing Setup**

**File**: `src/amas/services/tracing_service.py` (CREATE NEW)

```python
# src/amas/services/tracing_service.py (OPENTELEMETRY DISTRIBUTED TRACING)
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.trace import Status, StatusCode
from typing import Optional, Dict, Any, Callable
import logging
from functools import wraps
import os

logger = logging.getLogger(__name__)

class TracingService:
    """
    OpenTelemetry distributed tracing service
    
    ✅ Automatic span creation
    ✅ Context propagation
    ✅ Custom attributes
    ✅ Error tracking
    ✅ Performance monitoring
    ✅ Multi-exporter support (Jaeger, OTLP, Console)
    """
    
    def __init__(
        self,
        service_name: str = "amas-backend",
        service_version: str = "1.0.0",
        environment: str = "production",
        jaeger_endpoint: str = None,
        otlp_endpoint: str = None
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        
        # Create resource
        self.resource = Resource.create({
            ResourceAttributes.SERVICE_NAME: service_name,
            ResourceAttributes.SERVICE_VERSION: service_version,
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: environment,
            ResourceAttributes.SERVICE_NAMESPACE: "amas",
        })
        
        # Initialize tracer provider
        self.tracer_provider = TracerProvider(resource=self.resource)
        
        # Configure exporters
        self._configure_exporters(jaeger_endpoint, otlp_endpoint)
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
        
        logger.info(f"TracingService initialized: {service_name} ({environment})")
    
    def _configure_exporters(
        self,
        jaeger_endpoint: Optional[str],
        otlp_endpoint: Optional[str]
    ):
        """Configure span exporters"""
        
        # Console exporter (development)
        if os.getenv("TRACING_CONSOLE", "false").lower() == "true":
            console_exporter = ConsoleSpanExporter()
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )
            logger.info("Console trace exporter enabled")
        
        # Jaeger exporter
        if jaeger_endpoint or os.getenv("JAEGER_ENDPOINT"):
            endpoint = jaeger_endpoint or os.getenv("JAEGER_ENDPOINT")
            
            jaeger_exporter = JaegerExporter(
                agent_host_name=endpoint.split(":")[0] if ":" in endpoint else endpoint,
                agent_port=int(endpoint.split(":")[1]) if ":" in endpoint else 6831,
            )
            
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
            logger.info(f"Jaeger trace exporter configured: {endpoint}")
        
        # OTLP exporter (for Tempo, Grafana Cloud, etc.)
        if otlp_endpoint or os.getenv("OTLP_ENDPOINT"):
            endpoint = otlp_endpoint or os.getenv("OTLP_ENDPOINT")
            
            otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
            
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
            logger.info(f"OTLP trace exporter configured: {endpoint}")
    
    def instrument_app(self, app):
        """
        Instrument FastAPI application
        
        Automatically creates spans for all HTTP requests
        """
        
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumentation enabled")
    
    def instrument_libraries(self):
        """
        Instrument common libraries
        
        Automatically traces:
        - HTTP requests (requests, httpx)
        - Database queries (asyncpg)
        - Redis operations
        """
        
        # HTTP clients
        RequestsInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
        
        # Database
        AsyncPGInstrumentor().instrument()
        
        # Redis
        RedisInstrumentor().instrument()
        
        logger.info("Library instrumentation enabled")
    
    def start_span(
        self,
        name: str,
        attributes: Dict[str, Any] = None,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL
    ):
        """
        Start a new span
        
        Args:
            name: Span name (e.g., "task_execution", "agent_call")
            attributes: Custom attributes to add to span
            kind: Span kind (INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER)
        
        Returns:
            Span context manager
        """
        
        span = self.tracer.start_span(name, kind=kind)
        
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        
        return span
    
    def trace_function(
        self,
        span_name: str = None,
        attributes: Dict[str, Any] = None
    ):
        """
        Decorator to automatically trace function execution
        
        Usage:
            @tracing_service.trace_function(span_name="my_function")
            async def my_function():
                ...
        """
        
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Use function name if span_name not provided
                name = span_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(name) as span:
                    # Add custom attributes
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, value)
                    
                    # Add function metadata
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    
                    except Exception as e:
                        # Record exception in span
                        span.set_status(
                            Status(StatusCode.ERROR, str(e))
                        )
                        span.record_exception(e)
                        raise
            
            def sync_wrapper(*args, **kwargs):
                name = span_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(name) as span:
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, value)
                    
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    
                    except Exception as e:
                        span.set_status(
                            Status(StatusCode.ERROR, str(e))
                        )
                        span.record_exception(e)
                        raise
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """
        Add event to current span
        
        Args:
            name: Event name
            attributes: Event attributes
        """
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes=attributes or {})
    
    def set_attribute(self, key: str, value: Any):
        """
        Set attribute on current span
        
        Args:
            key: Attribute key
            value: Attribute value
        """
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_attribute(key, value)
    
    def record_exception(self, exception: Exception):
        """
        Record exception in current span
        
        Args:
            exception: Exception to record
        """
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.record_exception(exception)
            current_span.set_status(
                Status(StatusCode.ERROR, str(exception))
            )


# Global tracing service instance
_tracing_service: Optional[TracingService] = None

def init_tracing(
    service_name: str = "amas-backend",
    service_version: str = "1.0.0",
    environment: str = None,
    jaeger_endpoint: str = None,
    otlp_endpoint: str = None
) -> TracingService:
    """Initialize global tracing service"""
    
    global _tracing_service
    
    if _tracing_service is not None:
        logger.warning("Tracing already initialized")
        return _tracing_service
    
    # Get environment from env var if not provided
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "production")
    
    _tracing_service = TracingService(
        service_name=service_name,
        service_version=service_version,
        environment=environment,
        jaeger_endpoint=jaeger_endpoint,
        otlp_endpoint=otlp_endpoint
    )
    
    # Instrument common libraries
    _tracing_service.instrument_libraries()
    
    return _tracing_service

def get_tracing_service() -> TracingService:
    """Get global tracing service"""
    
    if _tracing_service is None:
        raise RuntimeError(
            "Tracing not initialized. Call init_tracing() during startup."
        )
    
    return _tracing_service
```

***

### **Step 6B.2: Integration with Task Execution**

**File**: `src/api/routes/tasks.py` (ENHANCE WITH TRACING)

```python
# src/api/routes/tasks.py (ADD TRACING)
from src.amas.services.tracing_service import get_tracing_service

# Add to task execution endpoint
@router.post("/tasks/{task_id}/execute", response_model=TaskExecutionResponse)
async def execute_task(
    task_id: str,
    execution_options: Optional[TaskExecutionOptions] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute task with full tracing"""
    
    tracing = get_tracing_service()
    
    # Start main execution span
    with tracing.tracer.start_as_current_span("task_execution") as span:
        # Add task metadata to span
        span.set_attribute("task.id", task_id)
        span.set_attribute("task.user_id", current_user.id)
        
        # Fetch task from database (auto-traced by AsyncPG instrumentation)
        try:
            task_row = await db.fetchrow(
                "SELECT * FROM tasks WHERE task_id = $1",
                task_id
            )
            
            if not task_row:
                span.set_attribute("task.found", False)
                raise HTTPException(status_code=404, detail="Task not found")
            
            span.set_attribute("task.found", True)
            span.set_attribute("task.type", task_row["task_type"])
            span.set_attribute("task.status", task_row["status"])
            
            task_data = dict(task_row)
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise
        
        # Update status (auto-traced)
        await db.execute(
            "UPDATE tasks SET status = $1, started_at = $2 WHERE task_id = $3",
            "executing", datetime.now(), task_id
        )
        
        # Background execution with tracing
        async def execute_task_async():
            """Background task execution with distributed tracing"""
            
            # Create child span for async execution
            with tracing.tracer.start_as_current_span("task_async_execution") as exec_span:
                exec_span.set_attribute("task.id", task_id)
                exec_span.set_attribute("task.type", task_data["task_type"])
                
                execution_start = time.time()
                
                try:
                    # Orchestrator execution (will create child spans)
                    result = await orchestrator.execute_task(
                        task_id=task_id,
                        task_type=task_data["task_type"],
                        target=task_data["target"],
                        parameters=json.loads(task_data["parameters"]) if task_data["parameters"] else {},
                        assigned_agents=json.loads(task_data["execution_metadata"]).get("assigned_agents", []),
                        user_context={
                            "user_id": current_user.id,
                            "execution_options": execution_options.dict() if execution_options else {}
                        }
                    )
                    
                    execution_duration = time.time() - execution_start
                    
                    # Add result metadata to span
                    exec_span.set_attribute("task.duration", execution_duration)
                    exec_span.set_attribute("task.success", result.success)
                    exec_span.set_attribute("task.quality_score", result.quality_score)
                    
                    # Persist results (auto-traced)
                    await db.execute(
                        "UPDATE tasks SET "
                        "status = $1, "
                        "result = $2, "
                        "completed_at = $3, "
                        "duration_seconds = $4, "
                        "success_rate = $5, "
                        "quality_score = $6 "
                        "WHERE task_id = $7",
                        "completed",
                        json.dumps(result.output),
                        datetime.now(),
                        execution_duration,
                        result.success_rate,
                        result.quality_score,
                        task_id
                    )
                    
                    exec_span.set_status(Status(StatusCode.OK))
                    
                except Exception as e:
                    # Record exception in span
                    exec_span.record_exception(e)
                    exec_span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    # Update database
                    await db.execute(
                        "UPDATE tasks SET "
                        "status = $1, "
                        "error_details = $2 "
                        "WHERE task_id = $3",
                        "failed",
                        json.dumps({"error": str(e)}),
                        task_id
                    )
                    
                    raise
        
        # Schedule background execution
        background_tasks.add_task(execute_task_async)
        
        span.set_status(Status(StatusCode.OK))
        
        return TaskExecutionResponse(
            task_id=task_id,
            status="executing",
            message="Task execution started"
        )
```

***

### **Step 6B.3: Enhanced Orchestrator with Tracing**

**File**: `src/amas/core/unified_intelligence_orchestrator.py` (ADD TRACING)

```python
# src/amas/core/unified_intelligence_orchestrator.py (ENHANCE WITH TRACING)
from src.amas.services.tracing_service import get_tracing_service
from opentelemetry.trace import Status, StatusCode

class UnifiedIntelligenceOrchestrator:
    """Enhanced orchestrator with distributed tracing"""
    
    def __init__(self):
        # ... existing init code ...
        self.tracing = get_tracing_service()
    
    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        target: str,
        parameters: Dict,
        assigned_agents: List[str],
        user_context: Dict,
        progress_callback: Callable = None
    ) -> TaskExecutionResult:
        """Execute task with full distributed tracing"""
        
        # Create orchestration span
        with self.tracing.tracer.start_as_current_span("orchestrator.execute_task") as span:
            span.set_attribute("orchestrator.task_id", task_id)
            span.set_attribute("orchestrator.task_type", task_type)
            span.set_attribute("orchestrator.target", target)
            span.set_attribute("orchestrator.agent_count", len(assigned_agents))
            
            execution_start = time.time()
            
            try:
                # STEP 1: Validate (create child span)
                with self.tracing.tracer.start_as_current_span("orchestrator.validate") as validate_span:
                    if not assigned_agents:
                        assigned_agents = await self.intelligence_manager.select_optimal_agents(
                            task_type, target, parameters
                        )
                    
                    agents = [self.agent_registry.get(agent_id) for agent_id in assigned_agents]
                    agents = [a for a in agents if a is not None]
                    
                    if not agents:
                        raise ValueError("No valid agents available for task")
                    
                    validate_span.set_attribute("agents.validated_count", len(agents))
                    validate_span.set_status(Status(StatusCode.OK))
                
                # STEP 2: Create execution plan
                with self.tracing.tracer.start_as_current_span("orchestrator.plan") as plan_span:
                    execution_plan = await self._create_execution_plan(
                        task_type, target, parameters, agents
                    )
                    
                    plan_span.set_attribute("plan.mode", execution_plan["mode"])
                    plan_span.set_status(Status(StatusCode.OK))
                
                # STEP 3: Execute agents
                with self.tracing.tracer.start_as_current_span("orchestrator.execute_agents") as exec_span:
                    exec_span.set_attribute("execution.mode", execution_plan["mode"])
                    
                    agent_results = {}
                    
                    if execution_plan["mode"] == "parallel":
                        # Parallel execution with individual spans
                        tasks = []
                        for agent in agents:
                            # Each agent execution will create its own span
                            tasks.append(
                                self._execute_agent(
                                    agent=agent,
                                    task_id=task_id,
                                    target=target,
                                    parameters=parameters,
                                    progress_callback=progress_callback
                                )
                            )
                        
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        for i, agent in enumerate(agents):
                            if isinstance(results[i], Exception):
                                agent_results[agent.id] = {
                                    "success": False,
                                    "error": str(results[i])
                                }
                            else:
                                agent_results[agent.id] = results[i]
                    
                    else:
                        # Sequential execution
                        for agent in agents:
                            result = await self._execute_agent(
                                agent=agent,
                                task_id=task_id,
                                target=target,
                                parameters=parameters,
                                progress_callback=progress_callback
                            )
                            agent_results[agent.id] = result
                    
                    exec_span.set_attribute("execution.completed_agents", len(agent_results))
                    exec_span.set_status(Status(StatusCode.OK))
                
                # STEP 4: Aggregate results
                with self.tracing.tracer.start_as_current_span("orchestrator.aggregate") as agg_span:
                    aggregated_result = await self._aggregate_agent_results(
                        agent_results, task_type
                    )
                    agg_span.set_status(Status(StatusCode.OK))
                
                execution_duration = time.time() - execution_start
                
                # Add final metrics to span
                span.set_attribute("orchestrator.duration", execution_duration)
                span.set_attribute("orchestrator.success", True)
                span.set_status(Status(StatusCode.OK))
                
                return TaskExecutionResult(
                    task_id=task_id,
                    success=True,
                    output=aggregated_result,
                    agents_used=[a.id for a in agents],
                    execution_time=execution_duration,
                    success_rate=self._calculate_success_rate(agent_results),
                    quality_score=self._calculate_quality_score(agent_results)
                )
            
            except Exception as e:
                # Record exception in span
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("orchestrator.success", False)
                
                execution_duration = time.time() - execution_start
                
                return TaskExecutionResult(
                    task_id=task_id,
                    success=False,
                    error=str(e),
                    execution_time=execution_duration
                )
    
    async def _execute_agent(
        self,
        agent: BaseAgent,
        task_id: str,
        target: str,
        parameters: Dict,
        progress_callback: Callable = None
    ) -> Dict:
        """Execute single agent with tracing"""
        
        # Create agent execution span
        with self.tracing.tracer.start_as_current_span(f"agent.{agent.id}.execute") as span:
            span.set_attribute("agent.id", agent.id)
            span.set_attribute("agent.name", agent.name)
            span.set_attribute("agent.type", agent.type)
            span.set_attribute("task.id", task_id)
            
            agent_start = time.time()
            
            try:
                # Prepare prompt
                with self.tracing.tracer.start_as_current_span("agent.prepare_prompt") as prompt_span:
                    prompt = await agent._prepare_prompt(target, parameters)
                    prompt_span.set_attribute("prompt.length", len(prompt))
                    prompt_span.set_status(Status(StatusCode.OK))
                
                # Execute agent (AI call will create child span via httpx instrumentation)
                with self.tracing.tracer.start_as_current_span("agent.ai_call") as ai_span:
                    response = await self.provider_router.generate_with_fallback(
                        prompt=prompt,
                        model_preference=agent.model_preference,
                        max_tokens=4000,
                        temperature=0.3,
                        system_prompt=agent.system_prompt,
                        strategy=agent.strategy
                    )
                    
                    ai_span.set_attribute("ai.provider", response.provider)
                    ai_span.set_attribute("ai.model", response.model)
                    ai_span.set_attribute("ai.tokens", response.tokens_used)
                    ai_span.set_attribute("ai.cost", response.cost_usd)
                    ai_span.set_attribute("ai.latency_ms", response.latency_ms)
                    ai_span.set_status(Status(StatusCode.OK))
                
                # Parse response
                with self.tracing.tracer.start_as_current_span("agent.parse_response") as parse_span:
                    parsed_result = await agent._parse_response(response.content)
                    parse_span.set_status(Status(StatusCode.OK))
                
                agent_duration = time.time() - agent_start
                
                # Add metrics to span
                span.set_attribute("agent.duration", agent_duration)
                span.set_attribute("agent.success", True)
                span.set_status(Status(StatusCode.OK))
                
                return {
                    "success": True,
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "result": parsed_result,
                    "duration": agent_duration,
                    "provider_used": response.provider,
                    "tokens_used": response.tokens_used
                }
            
            except Exception as e:
                # Record exception
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("agent.success", False)
                
                return {
                    "success": False,
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "error": str(e),
                    "duration": time.time() - agent_start
                }
```

***

### **Step 6B.4: Complete Monitoring Stack - Docker Compose**

**File**: `monitoring/docker-compose.yml` (CREATE NEW)

```yaml
# monitoring/docker-compose.yml
# Complete monitoring stack for AMAS

version: '3.8'

services:
  # Prometheus - Metrics collection
  prometheus:
    image: prom/prometheus:latest
    container_name: amas-prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/rules:/etc/prometheus/rules
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - amas-monitoring
    restart: unless-stopped

  # Grafana - Visualization
  grafana:
    image: grafana/grafana:latest
    container_name: amas-grafana
    volumes:
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3001:3000"
    networks:
      - amas-monitoring
    restart: unless-stopped
    depends_on:
      - prometheus

  # Jaeger - Distributed tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: amas-jaeger
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "5775:5775/udp"  # accept zipkin.thrift
      - "6831:6831/udp"  # accept jaeger.thrift
      - "6832:6832/udp"  # accept jaeger.thrift
      - "5778:5778"      # serve configs
      - "16686:16686"    # serve frontend
      - "14250:14250"    # accept model.proto
      - "14268:14268"    # accept jaeger.thrift
      - "14269:14269"    # admin port: health check
      - "9411:9411"      # Zipkin compatible endpoint
      - "4317:4317"      # OTLP gRPC
      - "4318:4318"      # OTLP HTTP
    networks:
      - amas-monitoring
    restart: unless-stopped

  # Alertmanager - Alert routing
  alertmanager:
    image: prom/alertmanager:latest
    container_name: amas-alertmanager
    volumes:
      - ./alertmanager/config.yml:/etc/alertmanager/config.yml
      - alertmanager-data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/config.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    networks:
      - amas-monitoring
    restart: unless-stopped

  # Node Exporter - System metrics
  node-exporter:
    image: prom/node-exporter:latest
    container_name: amas-node-exporter
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    ports:
      - "9100:9100"
    networks:
      - amas-monitoring
    restart: unless-stopped

  # cAdvisor - Container metrics
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: amas-cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:rw
      - /sys:/sys:ro
      - /var/lib/docker:/var/lib/docker:ro
    ports:
      - "8080:8080"
    networks:
      - amas-monitoring
    restart: unless-stopped

  # PostgreSQL Exporter - Database metrics
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: amas-postgres-exporter
    environment:
      - DATA_SOURCE_NAME=postgresql://amas:amas_password@postgres:5432/amas?sslmode=disable
    ports:
      - "9187:9187"
    networks:
      - amas-monitoring
      - amas-backend
    restart: unless-stopped

  # Redis Exporter - Redis metrics
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: amas-redis-exporter
    environment:
      - REDIS_ADDR=redis:6379
    ports:
      - "9121:9121"
    networks:
      - amas-monitoring
      - amas-backend
    restart: unless-stopped

  # Loki - Log aggregation
  loki:
    image: grafana/loki:latest
    container_name: amas-loki
    volumes:
      - ./loki/config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - amas-monitoring
    restart: unless-stopped

  # Promtail - Log shipper
  promtail:
    image: grafana/promtail:latest
    container_name: amas-promtail
    volumes:
      - ./promtail/config.yml:/etc/promtail/config.yml
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/config.yml
    networks:
      - amas-monitoring
    restart: unless-stopped
    depends_on:
      - loki

  # Tempo - Distributed tracing backend (alternative to Jaeger)
  tempo:
    image: grafana/tempo:latest
    container_name: amas-tempo
    volumes:
      - ./tempo/config.yml:/etc/tempo/config.yml
      - tempo-data:/tmp/tempo
    command: -config.file=/etc/tempo/config.yml
    ports:
      - "3200:3200"  # tempo
      - "4319:4317"  # otlp grpc
    networks:
      - amas-monitoring
    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:
  alertmanager-data:
  loki-data:
  tempo-data:

networks:
  amas-monitoring:
    driver: bridge
  amas-backend:
    external: true
```

***

### **Step 6B.5: Alertmanager Configuration**

**File**: `monitoring/alertmanager/config.yml` (CREATE NEW)

```yaml
# monitoring/alertmanager/config.yml
# Alertmanager configuration for AMAS

global:
  resolve_timeout: 5m
  slack_api_url: 'YOUR_SLACK_WEBHOOK_URL'
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@amas.local'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

# Templates for notifications
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Route configuration
route:
  receiver: 'default'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  
  routes:
    # Critical alerts - immediate notification
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 0s
      repeat_interval: 5m
    
    # High priority alerts
    - match:
        severity: warning
      receiver: 'warning-alerts'
      group_wait: 30s
      repeat_interval: 1h
    
    # Info alerts
    - match:
        severity: info
      receiver: 'info-alerts'
      repeat_interval: 24h

# Receivers configuration
receivers:
  # Default receiver
  - name: 'default'
    email_configs:
      - to: 'ops@amas.local'
        subject: '[AMAS] {{ .GroupLabels.alertname }}'
        html: |
          {{ range .Alerts }}
          <b>Alert:</b> {{ .Labels.alertname }}<br>
          <b>Severity:</b> {{ .Labels.severity }}<br>
          <b>Description:</b> {{ .Annotations.description }}<br>
          <b>Started:</b> {{ .StartsAt }}<br>
          {{ end }}
  
  # Critical alerts - Slack + Email + PagerDuty
  - name: 'critical-alerts'
    slack_configs:
      - channel: '#amas-critical-alerts'
        title: '🔴 CRITICAL: {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Labels.alertname }}
          *Severity:* {{ .Labels.severity }}
          *Component:* {{ .Labels.component }}
          *Description:* {{ .Annotations.description }}
          *Started:* {{ .StartsAt }}
          {{ end }}
        send_resolved: true
    
    email_configs:
      - to: 'ops-oncall@amas.local'
        subject: '🔴 CRITICAL ALERT: {{ .GroupLabels.alertname }}'
    
    # pagerduty_configs:
    #   - service_key: 'YOUR_PAGERDUTY_KEY'
  
  # Warning alerts - Slack
  - name: 'warning-alerts'
    slack_configs:
      - channel: '#amas-alerts'
        title: '🟠 WARNING: {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Labels.alertname }}
          *Component:* {{ .Labels.component }}
          *Description:* {{ .Annotations.description }}
          {{ end }}
        send_resolved: true
  
  # Info alerts - Slack (low priority channel)
  - name: 'info-alerts'
    slack_configs:
      - channel: '#amas-info'
        title: 'ℹ️ INFO: {{ .GroupLabels.alertname }}'
        send_resolved: false

# Inhibition rules - prevent duplicate alerts
inhibit_rules:
  # Inhibit warning alerts if critical alert is firing
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'component']
  
  # Inhibit info alerts if warning is firing
  - source_match:
      severity: 'warning'
    target_match:
      severity: 'info'
    equal: ['alertname', 'component']
```

***

### **Step 6B.6: Loki Configuration (Log Aggregation)**

**File**: `monitoring/loki/config.yml` (CREATE NEW)

```yaml
# monitoring/loki/config.yml
# Loki configuration for log aggregation

auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://alertmanager:9093

# Limits configuration
limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20

# Chunk store configuration
chunk_store_config:
  max_look_back_period: 0s

# Table manager configuration
table_manager:
  retention_deletes_enabled: true
  retention_period: 720h  # 30 days

# Query configuration
query_range:
  align_queries_with_step: true
  max_retries: 5
  parallelise_shardable_queries: true
  cache_results: true
```

***

### **Step 6B.7: Promtail Configuration (Log Shipper)**

**File**: `monitoring/promtail/config.yml` (CREATE NEW)

```yaml
# monitoring/promtail/config.yml
# Promtail configuration for shipping logs to Loki

server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Docker container logs
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
    
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'
      
      - source_labels: ['__meta_docker_container_log_stream']
        target_label: 'stream'
      
      - source_labels: ['__meta_docker_container_label_com_docker_compose_service']
        target_label: 'service'
    
    pipeline_stages:
      # Parse JSON logs
      - json:
          expressions:
            timestamp: timestamp
            level: level
            message: message
            logger: logger
      
      # Extract log level
      - labels:
          level:
          service:
      
      # Add timestamp
      - timestamp:
          source: timestamp
          format: RFC3339
      
      # Output
      - output:
          source: message

  # AMAS application logs
  - job_name: amas-backend
    static_configs:
      - targets:
          - localhost
        labels:
          job: amas-backend
          __path__: /var/log/amas/backend/*.log
    
    pipeline_stages:
      # Parse structured JSON logs
      - json:
          expressions:
            timestamp: timestamp
            level: level
            message: message
            logger: logger
            task_id: task_id
            agent_id: agent_id
            user_id: user_id
      
      # Extract labels
      - labels:
          level:
          logger:
          task_id:
          agent_id:
      
      # Add timestamp
      - timestamp:
          source: timestamp
          format: RFC3339
      
      # Output
      - output:
          source: message

  # System logs
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: syslog
          __path__: /var/log/syslog
    
    pipeline_stages:
      - regex:
          expression: '^(?P<timestamp>\S+\s+\d+\s+\S+)\s+(?P<hostname>\S+)\s+(?P<process>\S+)\[(?P<pid>\d+)\]:\s+(?P<message>.*)$'
      
      - labels:
          hostname:
          process:
      
      - timestamp:
          source: timestamp
          format: Jan _2 15:04:05
      
      - output:
          source: message
```

***

### **Step 6B.8: Structured Logging Configuration**

**File**: `src/utils/logging_config.py` (CREATE NEW)

```python
# src/utils/logging_config.py (STRUCTURED LOGGING SETUP)
import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any
import traceback

class JSONFormatter(logging.Formatter):
    """
    JSON log formatter for structured logging
    
    Outputs logs in JSON format for easy parsing by Loki/ELK
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        
        if hasattr(record, "agent_id"):
            log_data["agent_id"] = record.agent_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data)

def configure_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
    log_file: str = None
):
    """
    Configure application logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Use JSON formatting (for production)
        log_file: Optional log file path
    """
    
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if json_logs:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
    
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter() if json_logs else logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        root_logger.addHandler(file_handler)
    
    logging.info(f"Logging configured: level={log_level}, json={json_logs}")
```

**Initialize logging in main app**:

```python
# src/api/main.py (ADD)
from src.utils.logging_config import configure_logging
import os

# Configure logging on startup
configure_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    json_logs=os.getenv("JSON_LOGS", "true").lower() == "true",
    log_file=os.getenv("LOG_FILE")
)
```

***

### **Step 6B.9: Initialize Tracing in Main App**

**File**: `src/api/main.py` (COMPLETE TRACING SETUP)

```python
# src/api/main.py (ADD TRACING INITIALIZATION)
from src.amas.services.tracing_service import init_tracing
import os

# Initialize tracing on startup
@app.on_event("startup")
async def startup_tracing():
    tracing = init_tracing(
        service_name="amas-backend",
        service_version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("ENVIRONMENT", "production"),
        jaeger_endpoint=os.getenv("JAEGER_ENDPOINT", "jaeger:6831"),
        otlp_endpoint=os.getenv("OTLP_ENDPOINT")
    )
    
    # Instrument FastAPI app
    tracing.instrument_app(app)
    
    logger.info("Tracing initialized and app instrumented")
```

***

**This completes Part 6B - OpenTelemetry Tracing + Complete Monitoring Stack**

**What's Implemented**:
1. ✅ OpenTelemetry distributed tracing service
2. ✅ Automatic FastAPI instrumentation
3. ✅ Library instrumentation (httpx, asyncpg, redis)
4. ✅ Custom span creation for tasks/agents
5. ✅ Complete monitoring stack (Docker Compose)
6. ✅ Jaeger for trace visualization
7. ✅ Alertmanager for alert routing
8. ✅ Loki + Promtail for log aggregation
9. ✅ Structured JSON logging
10. ✅ All exporters configured

**Monitoring Stack Components**:
- ✅ Prometheus (metrics)
- ✅ Grafana (visualization)
- ✅ Jaeger (tracing)
- ✅ Loki (logs)
- ✅ Alertmanager (alerts)
- ✅ Node Exporter (system)
- ✅ cAdvisor (containers)
- ✅ PostgreSQL Exporter
- ✅ Redis Exporter

**Next Steps**:
- **Part 7**: Frontend Complete Integration
- **Part 8**: Production Deployment Configuration
- **Part 9**: Testing Strategy
- **Part 10**: Final Production Checklist

