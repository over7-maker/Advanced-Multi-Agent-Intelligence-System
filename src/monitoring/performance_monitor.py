"""
Performance monitoring and profiling tools for AMAS
Implements RD-081: Performance profiling tools
"""

import asyncio
import logging
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Dict, List, Optional

import psutil
from prometheus_client import Counter, Gauge, Histogram, start_http_server

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "amas_requests_total", "Total requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram(
    "amas_request_duration_seconds", "Request duration", ["method", "endpoint"]
)
ACTIVE_CONNECTIONS = Gauge("amas_active_connections", "Active connections")
MEMORY_USAGE = Gauge("amas_memory_usage_bytes", "Memory usage in bytes")
CPU_USAGE = Gauge("amas_cpu_usage_percent", "CPU usage percentage")
DATABASE_CONNECTIONS = Gauge("amas_database_connections", "Database connections")
CACHE_HITS = Counter("amas_cache_hits_total", "Cache hits", ["cache_type"])
CACHE_MISSES = Counter("amas_cache_misses_total", "Cache misses", ["cache_type"])


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""

    timestamp: float
    cpu_percent: float
    memory_usage: int
    memory_percent: float
    disk_usage: int
    network_io: Dict[str, int]
    active_connections: int
    database_connections: int
    cache_hit_rate: float
    response_time_p95: float
    response_time_p99: float


class PerformanceProfiler:
    """Performance profiler for AMAS system"""

    def __init__(self, monitoring_interval: int = 30):
        self.monitoring_interval = monitoring_interval
        self.metrics_history: List[PerformanceMetrics] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.start_time = time.time()

    def start_monitoring(self):
        """Start performance monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)

                # Keep only last 1000 metrics to prevent memory issues
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]

                # Update Prometheus metrics
                self._update_prometheus_metrics(metrics)

                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                time.sleep(self.monitoring_interval)

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        # Disk usage
        disk = psutil.disk_usage("/")

        # Network I/O
        network = psutil.net_io_counters()

        # Active connections (simplified)
        connections = len(psutil.net_connections())

        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_usage=memory.used,
            memory_percent=memory.percent,
            disk_usage=disk.used,
            network_io={
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            },
            active_connections=connections,
            database_connections=0,  # Will be updated by database monitoring
            cache_hit_rate=0.0,  # Will be updated by cache monitoring
            response_time_p95=0.0,  # Will be updated by request monitoring
            response_time_p99=0.0,
        )

    def _update_prometheus_metrics(self, metrics: PerformanceMetrics):
        """Update Prometheus metrics"""
        MEMORY_USAGE.set(metrics.memory_usage)
        CPU_USAGE.set(metrics.cpu_percent)
        ACTIVE_CONNECTIONS.set(metrics.active_connections)
        DATABASE_CONNECTIONS.set(metrics.database_connections)

    def get_metrics_summary(self) -> Dict:
        """Get performance metrics summary"""
        if not self.metrics_history:
            return {}

        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements

        return {
            "uptime_seconds": time.time() - self.start_time,
            "avg_cpu_percent": sum(m.cpu_percent for m in recent_metrics)
            / len(recent_metrics),
            "avg_memory_percent": sum(m.memory_percent for m in recent_metrics)
            / len(recent_metrics),
            "current_connections": (
                recent_metrics[-1].active_connections if recent_metrics else 0
            ),
            "total_measurements": len(self.metrics_history),
        }


def performance_timer(func: Callable) -> Callable:
    """Decorator to measure function execution time"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method="function", endpoint=func.__name__).observe(
                duration
            )
            logger.debug(f"Function {func.__name__} took {duration:.4f} seconds")

    return wrapper


def async_performance_timer(func: Callable) -> Callable:
    """Decorator to measure async function execution time"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method="async_function", endpoint=func.__name__
            ).observe(duration)
            logger.debug(f"Async function {func.__name__} took {duration:.4f} seconds")

    return wrapper


class DatabaseConnectionMonitor:
    """Monitor database connections for performance"""

    def __init__(self):
        self.connection_pool_size = 0
        self.active_connections = 0
        self.max_connections = 0

    def update_connection_stats(self, pool_size: int, active: int, max_conn: int):
        """Update connection statistics"""
        self.connection_pool_size = pool_size
        self.active_connections = active
        self.max_connections = max_conn
        DATABASE_CONNECTIONS.set(active)

    def get_connection_utilization(self) -> float:
        """Get connection pool utilization percentage"""
        if self.max_connections == 0:
            return 0.0
        return (self.active_connections / self.max_connections) * 100


class CachePerformanceMonitor:
    """Monitor cache performance"""

    def __init__(self):
        self.hits = 0
        self.misses = 0

    def record_hit(self, cache_type: str = "default"):
        """Record cache hit"""
        self.hits += 1
        CACHE_HITS.labels(cache_type=cache_type).inc()

    def record_miss(self, cache_type: str = "default"):
        """Record cache miss"""
        self.misses += 1
        CACHE_MISSES.labels(cache_type=cache_type).inc()

    def get_hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100


# Global instances
profiler = PerformanceProfiler()
db_monitor = DatabaseConnectionMonitor()
cache_monitor = CachePerformanceMonitor()


def start_performance_monitoring(port: int = 8001):
    """Start performance monitoring and Prometheus metrics server"""
    profiler.start_monitoring()
    start_http_server(port)
    logger.info(f"Performance monitoring started on port {port}")


def stop_performance_monitoring():
    """Stop performance monitoring"""
    profiler.stop_monitoring()


def get_performance_summary() -> Dict:
    """Get current performance summary"""
    return profiler.get_metrics_summary()
