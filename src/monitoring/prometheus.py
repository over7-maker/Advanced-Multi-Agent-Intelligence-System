"""
Prometheus metrics collection
"""

import logging

from prometheus_client import Counter, Gauge, Histogram, start_http_server

logger = logging.getLogger(__name__)

# Metrics
request_count = Counter(
    "amas_requests_total", "Total requests", ["method", "endpoint", "status"]
)
request_duration = Histogram(
    "amas_request_duration_seconds", "Request duration", ["method", "endpoint"]
)
active_connections = Gauge("amas_active_connections", "Active connections")
active_agents = Gauge("amas_active_agents", "Active agents")
active_tasks = Gauge("amas_active_tasks", "Active tasks")


def init_prometheus():
    """Initialize Prometheus metrics"""
    try:
        from src.config.settings import get_settings

        settings = get_settings()

        if settings.monitoring.prometheus_enabled:
            # Start Prometheus metrics server
            start_http_server(settings.monitoring.prometheus_port)
            logger.info(
                f"Prometheus metrics server started on port {settings.monitoring.prometheus_port}"
            )

    except Exception as e:
        logger.error(f"Failed to initialize Prometheus: {e}")
        raise


def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record request metrics"""
    try:
        request_count.labels(method=method, endpoint=endpoint, status=status_code).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    except Exception as e:
        logger.error(f"Failed to record request metrics: {e}")


def update_active_connections(count: int):
    """Update active connections metric"""
    try:
        active_connections.set(count)
    except Exception as e:
        logger.error(f"Failed to update active connections metric: {e}")


def update_active_agents(count: int):
    """Update active agents metric"""
    try:
        active_agents.set(count)
    except Exception as e:
        logger.error(f"Failed to update active agents metric: {e}")


def update_active_tasks(count: int):
    """Update active tasks metric"""
    try:
        active_tasks.set(count)
    except Exception as e:
        logger.error(f"Failed to update active tasks metric: {e}")
