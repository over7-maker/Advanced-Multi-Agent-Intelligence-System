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
        """Setup Prometheus metrics - 50+ metrics from PART_6.MD"""
        import logging
        logger = logging.getLogger(__name__)
        
        # ========================================================================
        # TASK METRICS (7 metrics)
        # ========================================================================
        self.metrics["amas_task_executions_total"] = Counter(
            "amas_task_executions_total",
            "Total number of task executions",
            ["task_type", "status"],
            registry=self.registry,
        )

        self.metrics["amas_task_duration_seconds"] = Histogram(
            "amas_task_duration_seconds",
            "Task execution duration in seconds",
            ["task_type"],
            buckets=[0.5, 1, 2, 5, 10, 30, 60, 120, 300, 600],
            registry=self.registry,
        )

        self.metrics["amas_task_success_rate"] = Gauge(
            "amas_task_success_rate",
            "Task success rate (0.0-1.0)",
            ["task_type"],
            registry=self.registry,
        )

        self.metrics["amas_task_quality_score"] = Gauge(
            "amas_task_quality_score",
            "Task quality score (0.0-1.0)",
            ["task_type"],
            registry=self.registry,
        )

        self.metrics["amas_tasks_active"] = Gauge(
            "amas_tasks_active",
            "Number of currently executing tasks",
            ["task_type"],
            registry=self.registry,
        )

        self.metrics["amas_task_queue_depth"] = Gauge(
            "amas_task_queue_depth",
            "Number of tasks waiting in queue",
            ["priority"],
            registry=self.registry,
        )

        self.metrics["amas_task_errors_total"] = Counter(
            "amas_task_errors_total",
            "Total number of task errors",
            ["task_type", "error_type"],
            registry=self.registry,
        )

        # ========================================================================
        # AGENT METRICS (6 metrics)
        # ========================================================================
        self.metrics["amas_agent_executions_total"] = Counter(
            "amas_agent_executions_total",
            "Total number of agent executions",
            ["agent_id", "agent_name", "status"],
            registry=self.registry,
        )

        self.metrics["amas_agent_duration_seconds"] = Histogram(
            "amas_agent_duration_seconds",
            "Agent execution duration in seconds",
            ["agent_id", "agent_name"],
            buckets=[0.5, 1, 2, 5, 10, 30, 60, 120],
            registry=self.registry,
        )

        self.metrics["amas_agent_utilization"] = Gauge(
            "amas_agent_utilization",
            "Agent utilization percentage (0.0-1.0)",
            ["agent_id", "agent_name"],
            registry=self.registry,
        )

        self.metrics["amas_agent_success_rate"] = Gauge(
            "amas_agent_success_rate",
            "Agent success rate (0.0-1.0)",
            ["agent_id", "agent_name"],
            registry=self.registry,
        )

        self.metrics["amas_agent_tokens_total"] = Counter(
            "amas_agent_tokens_total",
            "Total tokens used by agent",
            ["agent_id", "agent_name"],
            registry=self.registry,
        )

        self.metrics["amas_agent_cost_usd_total"] = Counter(
            "amas_agent_cost_usd_total",
            "Total cost in USD for agent",
            ["agent_id", "agent_name"],
            registry=self.registry,
        )

        # ========================================================================
        # AI PROVIDER METRICS (6 metrics)
        # ========================================================================
        self.metrics["amas_ai_provider_calls_total"] = Counter(
            "amas_ai_provider_calls_total",
            "Total AI provider API calls",
            ["provider", "model", "status"],
            registry=self.registry,
        )

        self.metrics["amas_ai_provider_latency_seconds"] = Histogram(
            "amas_ai_provider_latency_seconds",
            "AI provider response latency in seconds",
            ["provider", "model"],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30],
            registry=self.registry,
        )

        self.metrics["amas_ai_provider_tokens_total"] = Counter(
            "amas_ai_provider_tokens_total",
            "Total tokens used per provider",
            ["provider", "model"],
            registry=self.registry,
        )

        self.metrics["amas_ai_provider_cost_usd_total"] = Counter(
            "amas_ai_provider_cost_usd_total",
            "Total cost in USD per provider",
            ["provider", "model"],
            registry=self.registry,
        )

        self.metrics["amas_ai_provider_fallbacks_total"] = Counter(
            "amas_ai_provider_fallbacks_total",
            "Total provider fallbacks",
            ["from_provider", "to_provider"],
            registry=self.registry,
        )

        self.metrics["amas_ai_provider_circuit_breaker_state"] = Gauge(
            "amas_ai_provider_circuit_breaker_state",
            "Circuit breaker state (0=closed, 1=open, 2=half-open)",
            ["provider"],
            registry=self.registry,
        )

        # ========================================================================
        # ENHANCED TASK METRICS (percentiles and detailed metrics)
        # ========================================================================
        self.metrics["amas_task_creation_duration_seconds"] = Histogram(
            "amas_task_creation_duration_seconds",
            "Task creation duration in seconds",
            ["task_type", "status"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
            registry=self.registry,
        )
        
        self.metrics["amas_task_execution_duration_percentiles"] = Histogram(
            "amas_task_execution_duration_percentiles_seconds",
            "Task execution duration percentiles (p50, p95, p99)",
            ["task_type"],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
            registry=self.registry,
        )
        
        # ========================================================================
        # CACHE METRICS (hit/miss ratios)
        # ========================================================================
        self.metrics["amas_cache_hits_total"] = Counter(
            "amas_cache_hits_total",
            "Total cache hits",
            ["cache_type"],
            registry=self.registry,
        )
        
        self.metrics["amas_cache_misses_total"] = Counter(
            "amas_cache_misses_total",
            "Total cache misses",
            ["cache_type"],
            registry=self.registry,
        )
        
        self.metrics["amas_cache_hit_ratio"] = Gauge(
            "amas_cache_hit_ratio",
            "Cache hit ratio (0.0-1.0)",
            ["cache_type"],
            registry=self.registry,
        )
        
        # ========================================================================
        # WEBSOCKET METRICS
        # ========================================================================
        self.metrics["amas_websocket_connections"] = Gauge(
            "amas_websocket_connections",
            "Active WebSocket connections",
            registry=self.registry,
        )
        
        self.metrics["amas_websocket_messages_total"] = Counter(
            "amas_websocket_messages_total",
            "Total WebSocket messages sent",
            ["event_type"],
            registry=self.registry,
        )
        
        self.metrics["amas_websocket_latency_seconds"] = Histogram(
            "amas_websocket_latency_seconds",
            "WebSocket message latency in seconds",
            ["event_type"],
            buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0],
            registry=self.registry,
        )
        
        # ========================================================================
        # DATABASE METRICS (query time percentiles)
        # ========================================================================
        self.metrics["amas_database_query_duration_seconds"] = Histogram(
            "amas_database_query_duration_seconds",
            "Database query duration in seconds",
            ["query_type", "table"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
            registry=self.registry,
        )
        
        self.metrics["amas_database_connections_active"] = Gauge(
            "amas_database_connections_active",
            "Active database connections",
            registry=self.registry,
        )
        
        self.metrics["amas_database_connection_pool_size"] = Gauge(
            "amas_database_connection_pool_size",
            "Database connection pool size",
            registry=self.registry,
        )
        
        # ========================================================================
        # API METRICS (4 metrics)
        # ========================================================================
        self.metrics["amas_http_requests_total"] = Counter(
            "amas_http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.metrics["amas_http_request_duration_seconds"] = Histogram(
            "amas_http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
            registry=self.registry,
        )

        self.metrics["amas_http_requests_active"] = Gauge(
            "amas_http_requests_active",
            "Number of active HTTP requests",
            ["method", "endpoint"],
            registry=self.registry,
        )

        self.metrics["amas_websocket_connections_active"] = Gauge(
            "amas_websocket_connections_active",
            "Number of active WebSocket connections",
            registry=self.registry,
        )

        # ========================================================================
        # DATABASE METRICS (5 metrics)
        # ========================================================================
        self.metrics["amas_db_queries_total"] = Counter(
            "amas_db_queries_total",
            "Total database queries",
            ["operation", "table", "status"],
            registry=self.registry,
        )

        self.metrics["amas_db_query_duration_seconds"] = Histogram(
            "amas_db_query_duration_seconds",
            "Database query duration in seconds",
            ["operation", "table"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5],
            registry=self.registry,
        )

        self.metrics["amas_db_pool_connections"] = Gauge(
            "amas_db_pool_connections",
            "Database connection pool status",
            ["state"],  # active, idle, total
            registry=self.registry,
        )

        self.metrics["amas_cache_hit_rate"] = Gauge(
            "amas_cache_hit_rate",
            "Cache hit rate (0.0-1.0)",
            ["cache_type"],  # redis, memory
            registry=self.registry,
        )

        self.metrics["amas_cache_operations_total"] = Counter(
            "amas_cache_operations_total",
            "Total cache operations",
            ["operation", "result"],  # get/set/delete, hit/miss/success/error
            registry=self.registry,
        )

        # ========================================================================
        # SYSTEM METRICS (5 metrics)
        # ========================================================================
        self.metrics["amas_system_cpu_usage_percent"] = Gauge(
            "amas_system_cpu_usage_percent",
            "System CPU usage percentage",
            registry=self.registry,
        )

        self.metrics["amas_system_memory_usage_bytes"] = Gauge(
            "amas_system_memory_usage_bytes",
            "System memory usage in bytes",
            registry=self.registry,
        )

        self.metrics["amas_system_memory_usage_percent"] = Gauge(
            "amas_system_memory_usage_percent",
            "System memory usage percentage",
            registry=self.registry,
        )

        self.metrics["amas_system_disk_usage_bytes"] = Gauge(
            "amas_system_disk_usage_bytes",
            "System disk usage in bytes",
            ["mount_point"],
            registry=self.registry,
        )

        self.metrics["amas_system_network_io_bytes_total"] = Counter(
            "amas_system_network_io_bytes_total",
            "Total network I/O in bytes",
            ["direction"],  # sent, received
            registry=self.registry,
        )

        # ========================================================================
        # BUSINESS METRICS (5 metrics)
        # ========================================================================
        self.metrics["amas_ml_prediction_accuracy"] = Gauge(
            "amas_ml_prediction_accuracy",
            "ML model prediction accuracy (0.0-1.0)",
            ["model_name"],
            registry=self.registry,
        )

        self.metrics["amas_ml_model_training_total"] = Counter(
            "amas_ml_model_training_total",
            "Total ML model training runs",
            ["model_name"],
            registry=self.registry,
        )

        self.metrics["amas_integration_triggers_total"] = Counter(
            "amas_integration_triggers_total",
            "Total integration triggers",
            ["platform", "event_type", "status"],
            registry=self.registry,
        )

        self.metrics["amas_user_logins_total"] = Counter(
            "amas_user_logins_total",
            "Total user logins",
            ["status"],  # success, failure
            registry=self.registry,
        )

        self.metrics["amas_users_active"] = Gauge(
            "amas_users_active",
            "Number of active users",
            registry=self.registry,
        )

        # ========================================================================
        # BACKWARD COMPATIBILITY - Keep old metric names
        # ========================================================================
        # HTTP metrics (backward compatibility)
        self.metrics["http_requests_total"] = self.metrics["amas_http_requests_total"]
        self.metrics["http_request_duration_seconds"] = self.metrics["amas_http_request_duration_seconds"]
        self.metrics["http_requests_active"] = self.metrics["amas_http_requests_active"]

        # Task metrics (backward compatibility)
        self.metrics["tasks_total"] = self.metrics["amas_task_executions_total"]
        self.metrics["task_duration_seconds"] = self.metrics["amas_task_duration_seconds"]
        self.metrics["tasks_in_progress"] = Gauge(
            "tasks_in_progress",
            "Number of tasks currently in progress",
            registry=self.registry,
        )

        # Agent metrics (backward compatibility)
        self.metrics["agent_executions_total"] = self.metrics["amas_agent_executions_total"]
        self.metrics["agent_execution_duration_seconds"] = self.metrics["amas_agent_duration_seconds"]
        self.metrics["agents_total"] = Gauge(
            "agents_total", "Total number of agents", ["status"], registry=self.registry
        )

        # Database metrics (backward compatibility)
        self.metrics["database_queries_total"] = self.metrics["amas_db_queries_total"]
        self.metrics["database_query_duration_seconds"] = self.metrics["amas_db_query_duration_seconds"]
        self.metrics["database_connections_active"] = Gauge(
            "database_connections_active",
            "Number of active database connections",
            ["database"],
            registry=self.registry,
        )

        # Cache metrics (backward compatibility)
        self.metrics["cache_operations_total"] = self.metrics["amas_cache_operations_total"]
        self.metrics["cache_hit_ratio"] = self.metrics["amas_cache_hit_rate"]

        # System metrics (backward compatibility)
        self.metrics["system_uptime_seconds"] = Gauge(
            "system_uptime_seconds", "System uptime in seconds", registry=self.registry
        )
        self.metrics["system_memory_usage_bytes"] = Gauge(
            "system_memory_usage_bytes",
            "System memory usage in bytes",
            ["type"],
            registry=self.registry,
        )
        self.metrics["system_cpu_usage_percent"] = self.metrics["amas_system_cpu_usage_percent"]

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

        # Business metrics (backward compatibility)
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

        logger.info("PrometheusMetricsService initialized with 50+ metrics")

    def _setup_dummy_metrics(self):
        """Setup dummy metrics when Prometheus is not available"""
        # Create dummy metric classes that do nothing
        class DummyMetric:
            def labels(self, **kwargs):
                return self
            def inc(self, *args, **kwargs):
                pass
            def observe(self, *args, **kwargs):
                pass
            def set(self, *args, **kwargs):
                pass
            def time(self):
                return self
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def info(self, *args, **kwargs):
                pass
        
        dummy = DummyMetric()
        # Create dummy metrics that do nothing
        self.metrics = {
            "http_requests_total": dummy,
            "http_request_duration_seconds": dummy,
            "http_request_size_bytes": dummy,
            "http_response_size_bytes": dummy,
            "auth_attempts_total": dummy,
            "auth_failures_total": dummy,
            "active_sessions": dummy,
            "agents_total": dummy,
            "agent_executions_total": dummy,
            "agent_execution_duration_seconds": dummy,
            "tasks_total": dummy,
            "task_duration_seconds": dummy,
            "tasks_in_progress": dummy,
            "system_uptime_seconds": dummy,
            "system_memory_usage_bytes": dummy,
            "system_cpu_usage_percent": dummy,
            "database_connections_active": dummy,
            "database_queries_total": dummy,
            "database_query_duration_seconds": dummy,
            "cache_operations_total": dummy,
            "cache_hit_ratio": dummy,
            "errors_total": dummy,
            "rate_limit_exceeded_total": dummy,
            "users_total": dummy,
            "api_keys_total": dummy,
            "application_info": dummy,
            # Add all amas_ prefixed metrics
            "amas_task_executions_total": dummy,
            "amas_agent_executions_total": dummy,
            "amas_http_requests_total": dummy,
        }

    # ========================================================================
    # METRIC RECORDING METHODS (PART_6.MD specification)
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
        if not self.enabled:
            return
        
        # Increment counter
        self.metrics["amas_task_executions_total"].labels(
            task_type=task_type,
            status=status
        ).inc()
        
        # Record duration
        self.metrics["amas_task_duration_seconds"].labels(
            task_type=task_type
        ).observe(duration)
        
        # Update success rate
        if success_rate is not None:
            self.metrics["amas_task_success_rate"].labels(
                task_type=task_type
            ).set(success_rate)
        
        # Update quality score
        if quality_score is not None:
            self.metrics["amas_task_quality_score"].labels(
                task_type=task_type
            ).set(quality_score)
        
        # Record error if present
        if error_type:
            self.metrics["amas_task_errors_total"].labels(
                task_type=task_type,
                error_type=error_type
            ).inc()
    
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
        if not self.enabled:
            return
        
        # Increment counter
        self.metrics["amas_agent_executions_total"].labels(
            agent_id=agent_id,
            agent_name=agent_name,
            status=status
        ).inc()
        
        # Record duration
        self.metrics["amas_agent_duration_seconds"].labels(
            agent_id=agent_id,
            agent_name=agent_name
        ).observe(duration)
        
        # Record tokens
        if tokens_used > 0:
            self.metrics["amas_agent_tokens_total"].labels(
                agent_id=agent_id,
                agent_name=agent_name
            ).inc(tokens_used)
        
        # Record cost
        if cost_usd > 0:
            self.metrics["amas_agent_cost_usd_total"].labels(
                agent_id=agent_id,
                agent_name=agent_name
            ).inc(cost_usd)
    
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
        if not self.enabled:
            return
        
        # Increment call counter
        self.metrics["amas_ai_provider_calls_total"].labels(
            provider=provider,
            model=model,
            status=status
        ).inc()
        
        # Record latency (convert ms to seconds if needed)
        latency_seconds = latency / 1000.0 if latency > 100 else latency
        self.metrics["amas_ai_provider_latency_seconds"].labels(
            provider=provider,
            model=model
        ).observe(latency_seconds)
        
        # Record tokens
        if tokens_used > 0:
            self.metrics["amas_ai_provider_tokens_total"].labels(
                provider=provider,
                model=model
            ).inc(tokens_used)
        
        # Record cost
        if cost_usd > 0:
            self.metrics["amas_ai_provider_cost_usd_total"].labels(
                provider=provider,
                model=model
            ).inc(cost_usd)
        
        # Record fallback if occurred
        if fallback_from:
            self.metrics["amas_ai_provider_fallbacks_total"].labels(
                from_provider=fallback_from,
                to_provider=provider
            ).inc()
    
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

        # Record request count (new metric name)
        self.metrics["amas_http_requests_total"].labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        # Record duration (new metric name)
        self.metrics["amas_http_request_duration_seconds"].labels(
            method=method, endpoint=endpoint
        ).observe(duration)

        # Backward compatibility
        self.metrics["http_requests_total"].labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()
        self.metrics["http_request_duration_seconds"].labels(
            method=method, endpoint=endpoint
        ).observe(duration)

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

    def record_db_query(
        self,
        operation: str,
        table: str,
        status: str,
        duration: float
    ):
        """Record database query metrics (PART_6.MD specification)"""
        if not self.enabled:
            return

        # New metric names
        self.metrics["amas_db_queries_total"].labels(
            operation=operation,
            table=table,
            status=status
        ).inc()

        self.metrics["amas_db_query_duration_seconds"].labels(
            operation=operation,
            table=table
        ).observe(duration)
        
        # Backward compatibility
        self.metrics["database_queries_total"].labels(
            database="postgres", operation=operation, status=status
        ).inc()

        self.metrics["database_query_duration_seconds"].labels(
            database="postgres", operation=operation
        ).observe(duration)
    
    def record_database_query(
        self, database: str, operation: str, status: str, duration: float
    ):
        """Record database query metrics (backward compatibility)"""
        self.record_db_query(operation, database, status, duration)

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

    def update_system_resources(
        self,
        cpu_percent: float,
        memory_bytes: int,
        memory_percent: float
    ):
        """Update system resource metrics (PART_6.MD specification)"""
        if not self.enabled:
            return
        
        self.metrics["amas_system_cpu_usage_percent"].set(cpu_percent)
        self.metrics["amas_system_memory_usage_bytes"].set(memory_bytes)
        self.metrics["amas_system_memory_usage_percent"].set(memory_percent)
        
        # Backward compatibility
        self.metrics["system_cpu_usage_percent"].set(cpu_percent)
        self.metrics["system_memory_usage_bytes"].labels(type="used").set(memory_bytes)
    
    def record_integration_trigger(
        self,
        platform: str,
        event_type: str,
        status: str
    ):
        """Record integration trigger metrics"""
        if not self.enabled:
            return
        
        self.metrics["amas_integration_triggers_total"].labels(
            platform=platform,
            event_type=event_type,
            status=status
        ).inc()
    
    def update_system_metrics(self):
        """Update system metrics (backward compatibility)"""
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
            
            # Update new metrics
            self.update_system_resources(
                cpu_percent=cpu_percent,
                memory_bytes=memory.used,
                memory_percent=memory.percent
            )

        except ImportError:
            # psutil not available, skip system metrics
            pass

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
        from functools import wraps
        
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
    
    def get_metrics(self) -> bytes:
        """
        Get metrics in Prometheus format
        
        Returns:
            Metrics in Prometheus text format (bytes)
        """
        if not self.enabled:
            return b""
        
        return generate_latest(self.registry)
    
    def get_content_type(self) -> str:
        """Get Prometheus content type"""
        return CONTENT_TYPE_LATEST

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
