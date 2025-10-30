"""
Prometheus Metrics Service for AMAS
Implements comprehensive metrics collection for monitoring and observability
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        Info,
        Summary,
        generate_latest,
        start_http_server,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

    # Create dummy classes for when prometheus_client is not available
    class Counter:
        def __init__(self, *args, **kwargs):
            pass

        def inc(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

        def time(self):
            return self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    class Gauge:
        def __init__(self, *args, **kwargs):
            pass

        def set(self, *args, **kwargs):
            pass

        def inc(self, *args, **kwargs):
            pass

        def dec(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Summary:
        def __init__(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

        def time(self):
            return self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    class Info:
        def __init__(self, *args, **kwargs):
            pass

        def info(self, *args, **kwargs):
            pass

    class CollectorRegistry:
        def __init__(self):
            pass

    def generate_latest(*args, **kwargs):
        return b""

    CONTENT_TYPE_LATEST = "text/plain"

    def start_http_server(*args, **kwargs):
        pass


class MetricType(str, Enum):
    """Metric types"""

    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    SUMMARY = "summary"
    INFO = "info"


@dataclass
class MetricConfig:
    """Configuration for a metric"""

    name: str
    description: str
    metric_type: MetricType
    labels: List[str] = None
    buckets: List[float] = None
    quantiles: List[float] = None


class PrometheusMetricsService:
    """Service for managing Prometheus metrics"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.registry = CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        self.enabled = self.config.get("enabled", True) and PROMETHEUS_AVAILABLE

        if self.enabled:
            self._setup_metrics()
        else:
            self._setup_dummy_metrics()

    def _setup_metrics(self):
        """Setup Prometheus metrics"""
        # HTTP metrics
        self.metrics["http_requests_total"] = Counter(
            "http_requests_total",
            "Total number of HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.metrics["http_request_duration_seconds"] = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry,
        )

        self.metrics["http_request_size_bytes"] = Histogram(
            "http_request_size_bytes",
            "HTTP request size in bytes",
            ["method", "endpoint"],
            buckets=[100, 1000, 10000, 100000, 1000000],
            registry=self.registry,
        )

        self.metrics["http_response_size_bytes"] = Histogram(
            "http_response_size_bytes",
            "HTTP response size in bytes",
            ["method", "endpoint"],
            buckets=[100, 1000, 10000, 100000, 1000000],
            registry=self.registry,
        )

        # Authentication metrics
        self.metrics["auth_attempts_total"] = Counter(
            "auth_attempts_total",
            "Total number of authentication attempts",
            ["result", "method"],
            registry=self.registry,
        )

        self.metrics["auth_failures_total"] = Counter(
            "auth_failures_total",
            "Total number of authentication failures",
            ["reason", "ip_address"],
            registry=self.registry,
        )

        self.metrics["active_sessions"] = Gauge(
            "active_sessions", "Number of active user sessions", registry=self.registry
        )

        # Agent metrics
        self.metrics["agents_total"] = Gauge(
            "agents_total", "Total number of agents", ["status"], registry=self.registry
        )

        self.metrics["agent_executions_total"] = Counter(
            "agent_executions_total",
            "Total number of agent executions",
            ["agent_id", "status"],
            registry=self.registry,
        )

        self.metrics["agent_execution_duration_seconds"] = Histogram(
            "agent_execution_duration_seconds",
            "Agent execution duration in seconds",
            ["agent_id"],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0],
            registry=self.registry,
        )

        # Task metrics
        self.metrics["tasks_total"] = Counter(
            "tasks_total",
            "Total number of tasks",
            ["status", "priority"],
            registry=self.registry,
        )

        self.metrics["task_duration_seconds"] = Histogram(
            "task_duration_seconds",
            "Task execution duration in seconds",
            ["task_type", "status"],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0],
            registry=self.registry,
        )

        self.metrics["tasks_in_progress"] = Gauge(
            "tasks_in_progress",
            "Number of tasks currently in progress",
            registry=self.registry,
        )

        # System metrics
        self.metrics["system_uptime_seconds"] = Gauge(
            "system_uptime_seconds", "System uptime in seconds", registry=self.registry
        )

        self.metrics["system_memory_usage_bytes"] = Gauge(
            "system_memory_usage_bytes",
            "System memory usage in bytes",
            ["type"],
            registry=self.registry,
        )

        self.metrics["system_cpu_usage_percent"] = Gauge(
            "system_cpu_usage_percent",
            "System CPU usage percentage",
            registry=self.registry,
        )

        # Database metrics
        self.metrics["database_connections_active"] = Gauge(
            "database_connections_active",
            "Number of active database connections",
            ["database"],
            registry=self.registry,
        )

        self.metrics["database_queries_total"] = Counter(
            "database_queries_total",
            "Total number of database queries",
            ["database", "operation", "status"],
            registry=self.registry,
        )

        self.metrics["database_query_duration_seconds"] = Histogram(
            "database_query_duration_seconds",
            "Database query duration in seconds",
            ["database", "operation"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            registry=self.registry,
        )

        # Cache metrics
        self.metrics["cache_operations_total"] = Counter(
            "cache_operations_total",
            "Total number of cache operations",
            ["operation", "status"],
            registry=self.registry,
        )

        self.metrics["cache_hit_ratio"] = Gauge(
            "cache_hit_ratio", "Cache hit ratio", registry=self.registry
        )

        # Error metrics
        self.metrics["errors_total"] = Counter(
            "errors_total",
            "Total number of errors",
            ["error_type", "component"],
            registry=self.registry,
        )

        self.metrics["rate_limit_exceeded_total"] = Counter(
            "rate_limit_exceeded_total",
            "Total number of rate limit exceeded events",
            ["endpoint", "ip_address"],
            registry=self.registry,
        )

        # Business metrics
        self.metrics["users_total"] = Gauge(
            "users_total", "Total number of users", ["status"], registry=self.registry
        )

        self.metrics["api_keys_total"] = Gauge(
            "api_keys_total",
            "Total number of API keys",
            ["status"],
            registry=self.registry,
        )

        # Application info
        self.metrics["application_info"] = Info(
            "application_info", "Application information", registry=self.registry
        )

        # Set application info
        self.metrics["application_info"].info(
            {
                "name": "AMAS",
                "version": "1.0.0",
                "environment": self.config.get("environment", "development"),
            }
        )

    def _setup_dummy_metrics(self):
        """Setup dummy metrics when Prometheus is not available"""
        # Create dummy metrics that do nothing
        self.metrics = {
            "http_requests_total": Counter(),
            "http_request_duration_seconds": Histogram(),
            "http_request_size_bytes": Histogram(),
            "http_response_size_bytes": Histogram(),
            "auth_attempts_total": Counter(),
            "auth_failures_total": Counter(),
            "active_sessions": Gauge(),
            "agents_total": Gauge(),
            "agent_executions_total": Counter(),
            "agent_execution_duration_seconds": Histogram(),
            "tasks_total": Counter(),
            "task_duration_seconds": Histogram(),
            "tasks_in_progress": Gauge(),
            "system_uptime_seconds": Gauge(),
            "system_memory_usage_bytes": Gauge(),
            "system_cpu_usage_percent": Gauge(),
            "database_connections_active": Gauge(),
            "database_queries_total": Counter(),
            "database_query_duration_seconds": Histogram(),
            "cache_operations_total": Counter(),
            "cache_hit_ratio": Gauge(),
            "errors_total": Counter(),
            "rate_limit_exceeded_total": Counter(),
            "users_total": Gauge(),
            "api_keys_total": Gauge(),
            "application_info": Info(),
        }

    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_size: int = None,
        response_size: int = None,
    ):
        """Record HTTP request metrics"""
        if not self.enabled:
            return

        # Record request count
        self.metrics["http_requests_total"].labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        # Record duration
        self.metrics["http_request_duration_seconds"].labels(
            method=method, endpoint=endpoint
        ).observe(duration)

        # Record request size
        if request_size is not None:
            self.metrics["http_request_size_bytes"].labels(
                method=method, endpoint=endpoint
            ).observe(request_size)

        # Record response size
        if response_size is not None:
            self.metrics["http_response_size_bytes"].labels(
                method=method, endpoint=endpoint
            ).observe(response_size)

    def record_auth_attempt(self, result: str, method: str = "password"):
        """Record authentication attempt"""
        if not self.enabled:
            return

        self.metrics["auth_attempts_total"].labels(result=result, method=method).inc()

    def record_auth_failure(self, reason: str, ip_address: str = "unknown"):
        """Record authentication failure"""
        if not self.enabled:
            return

        self.metrics["auth_failures_total"].labels(
            reason=reason, ip_address=ip_address
        ).inc()

    def set_active_sessions(self, count: int):
        """Set active sessions count"""
        if not self.enabled:
            return

        self.metrics["active_sessions"].set(count)

    def record_agent_execution(
        self, agent_id: str, status: str, duration: float = None
    ):
        """Record agent execution"""
        if not self.enabled:
            return

        self.metrics["agent_executions_total"].labels(
            agent_id=agent_id, status=status
        ).inc()

        if duration is not None:
            self.metrics["agent_execution_duration_seconds"].labels(
                agent_id=agent_id
            ).observe(duration)

    def set_agents_total(self, status: str, count: int):
        """Set total agents count"""
        if not self.enabled:
            return

        self.metrics["agents_total"].labels(status=status).set(count)

    def record_task(
        self, status: str, priority: str, task_type: str = None, duration: float = None
    ):
        """Record task metrics"""
        if not self.enabled:
            return

        self.metrics["tasks_total"].labels(status=status, priority=priority).inc()

        if duration is not None and task_type is not None:
            self.metrics["task_duration_seconds"].labels(
                task_type=task_type, status=status
            ).observe(duration)

    def set_tasks_in_progress(self, count: int):
        """Set tasks in progress count"""
        if not self.enabled:
            return

        self.metrics["tasks_in_progress"].set(count)

    def record_database_query(
        self, database: str, operation: str, status: str, duration: float
    ):
        """Record database query metrics"""
        if not self.enabled:
            return

        self.metrics["database_queries_total"].labels(
            database=database, operation=operation, status=status
        ).inc()

        self.metrics["database_query_duration_seconds"].labels(
            database=database, operation=operation
        ).observe(duration)

    def set_database_connections(self, database: str, count: int):
        """Set active database connections"""
        if not self.enabled:
            return

        self.metrics["database_connections_active"].labels(database=database).set(count)

    def record_cache_operation(self, operation: str, status: str):
        """Record cache operation"""
        if not self.enabled:
            return

        self.metrics["cache_operations_total"].labels(
            operation=operation, status=status
        ).inc()

    def set_cache_hit_ratio(self, ratio: float):
        """Set cache hit ratio"""
        if not self.enabled:
            return

        self.metrics["cache_hit_ratio"].set(ratio)

    def record_error(self, error_type: str, component: str):
        """Record error"""
        if not self.enabled:
            return

        self.metrics["errors_total"].labels(
            error_type=error_type, component=component
        ).inc()

    def record_rate_limit_exceeded(self, endpoint: str, ip_address: str):
        """Record rate limit exceeded"""
        if not self.enabled:
            return

        self.metrics["rate_limit_exceeded_total"].labels(
            endpoint=endpoint, ip_address=ip_address
        ).inc()

    def set_users_total(self, status: str, count: int):
        """Set total users count"""
        if not self.enabled:
            return

        self.metrics["users_total"].labels(status=status).set(count)

    def set_api_keys_total(self, status: str, count: int):
        """Set total API keys count"""
        if not self.enabled:
            return

        self.metrics["api_keys_total"].labels(status=status).set(count)

    def update_system_metrics(self):
        """Update system metrics"""
        if not self.enabled:
            return

        try:
            import psutil

            # Update uptime
            uptime = time.time() - self.config.get("start_time", time.time())
            self.metrics["system_uptime_seconds"].set(uptime)

            # Update memory usage
            memory = psutil.virtual_memory()
            self.metrics["system_memory_usage_bytes"].labels(type="used").set(
                memory.used
            )
            self.metrics["system_memory_usage_bytes"].labels(type="available").set(
                memory.available
            )
            self.metrics["system_memory_usage_bytes"].labels(type="total").set(
                memory.total
            )

            # Update CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics["system_cpu_usage_percent"].set(cpu_percent)

        except ImportError:
            # psutil not available, skip system metrics
            pass

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        if not self.enabled:
            return ""

        return generate_latest(self.registry).decode("utf-8")

    def start_metrics_server(self, port: int = 9090):
        """Start Prometheus metrics server"""
        if not self.enabled:
            return

        start_http_server(port, registry=self.registry)


# Global metrics service instance
metrics_service: Optional[PrometheusMetricsService] = None


def get_metrics_service() -> PrometheusMetricsService:
    """Get the global metrics service instance"""
    global metrics_service
    if metrics_service is None:
        from src.config.settings import get_settings

        settings = get_settings()
        metrics_service = PrometheusMetricsService(
            {
                "enabled": settings.monitoring.prometheus_enabled,
                "environment": settings.environment,
                "start_time": time.time(),
            }
        )
    return metrics_service


def record_http_request(*args, **kwargs):
    """Convenience function to record HTTP request"""
    get_metrics_service().record_http_request(*args, **kwargs)


def record_auth_attempt(*args, **kwargs):
    """Convenience function to record auth attempt"""
    get_metrics_service().record_auth_attempt(*args, **kwargs)


def record_error(*args, **kwargs):
    """Convenience function to record error"""
    get_metrics_service().record_error(*args, **kwargs)
