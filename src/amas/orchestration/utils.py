"""
Orchestration Utilities

Common utilities for error handling, retries, metrics, and observability.
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryStrategy(str, Enum):
    """Retry strategies for failed operations"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    NO_RETRY = "no_retry"

class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    retryable_exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for retrying async functions with configurable backoff strategies.
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries
        strategy: Retry strategy (exponential, linear, fixed, or no retry)
        retryable_exceptions: Tuple of exceptions that should trigger retry
        on_retry: Optional callback function called on each retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}",
                            exc_info=True
                        )
                        raise
                    
                    # Calculate delay based on strategy
                    if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                        delay = min(initial_delay * (2 ** (attempt - 1)), max_delay)
                    elif strategy == RetryStrategy.LINEAR_BACKOFF:
                        delay = min(initial_delay * attempt, max_delay)
                    elif strategy == RetryStrategy.FIXED_DELAY:
                        delay = initial_delay
                    else:
                        raise  # No retry
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    if on_retry:
                        try:
                            on_retry(e, attempt)
                        except Exception as callback_error:
                            logger.error(f"Error in retry callback: {callback_error}")
                    
                    await asyncio.sleep(delay)
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator

class MetricsCollector:
    """Collects and tracks metrics for orchestration operations"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "operation_counts": {},
            "operation_durations": {},
            "error_counts": {},
            "success_rates": {},
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        self._lock = asyncio.Lock()
    
    async def record_operation(
        self,
        operation_name: str,
        duration: float,
        success: bool = True,
        error: Optional[Exception] = None
    ):
        """Record an operation metric"""
        async with self._lock:
            # Update counts
            if operation_name not in self.metrics["operation_counts"]:
                self.metrics["operation_counts"][operation_name] = {"total": 0, "success": 0, "failed": 0}
            
            self.metrics["operation_counts"][operation_name]["total"] += 1
            if success:
                self.metrics["operation_counts"][operation_name]["success"] += 1
            else:
                self.metrics["operation_counts"][operation_name]["failed"] += 1
                if error:
                    error_type = type(error).__name__
                    if operation_name not in self.metrics["error_counts"]:
                        self.metrics["error_counts"][operation_name] = {}
                    self.metrics["error_counts"][operation_name][error_type] = \
                        self.metrics["error_counts"][operation_name].get(error_type, 0) + 1
            
            # Update durations
            if operation_name not in self.metrics["operation_durations"]:
                self.metrics["operation_durations"][operation_name] = []
            
            self.metrics["operation_durations"][operation_name].append(duration)
            
            # Keep only last 1000 durations per operation
            if len(self.metrics["operation_durations"][operation_name]) > 1000:
                self.metrics["operation_durations"][operation_name] = \
                    self.metrics["operation_durations"][operation_name][-1000:]
            
            # Update success rate
            counts = self.metrics["operation_counts"][operation_name]
            total = counts["total"]
            success_count = counts["success"]
            self.metrics["success_rates"][operation_name] = success_count / total if total > 0 else 0.0
            
            self.metrics["last_updated"] = datetime.now(timezone.utc).isoformat()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        metrics_snapshot = {
            "operation_counts": dict(self.metrics["operation_counts"]),
            "success_rates": dict(self.metrics["success_rates"]),
            "error_counts": dict(self.metrics["error_counts"]),
            "last_updated": self.metrics["last_updated"]
        }
        
        # Calculate average durations
        avg_durations = {}
        for op_name, durations in self.metrics["operation_durations"].items():
            if durations:
                avg_durations[op_name] = {
                    "avg": sum(durations) / len(durations),
                    "min": min(durations),
                    "max": max(durations),
                    "p95": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else durations[-1],
                    "count": len(durations)
                }
        
        metrics_snapshot["operation_durations"] = avg_durations
        return metrics_snapshot
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            "operation_counts": {},
            "operation_durations": {},
            "error_counts": {},
            "success_rates": {},
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

def track_metrics(operation_name: Optional[str] = None):
    """
    Decorator to track operation metrics (duration, success rate, errors).
    
    Args:
        operation_name: Name for the operation (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        metrics = MetricsCollector()
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = False
            error = None
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error = e
                raise
            finally:
                duration = time.time() - start_time
                await metrics.record_operation(op_name, duration, success, error)
        
        wrapper.metrics = metrics
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Circuit breaker pattern implementation for preventing cascading failures.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half_open
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            current_time = datetime.now(timezone.utc)
            
            # Check if we should attempt recovery
            if self.state == "open":
                if self.last_failure_time:
                    time_since_failure = (current_time - self.last_failure_time).total_seconds()
                    if time_since_failure >= self.recovery_timeout:
                        self.state = "half_open"
                        logger.info("Circuit breaker transitioning to half-open state")
                    else:
                        raise Exception(
                            f"Circuit breaker is OPEN. "
                            f"Retry after {self.recovery_timeout - time_since_failure:.1f}s"
                        )
            
            # Attempt the operation
            try:
                result = await func(*args, **kwargs)
                
                # Success - reset failure count if in half-open
                if self.state == "half_open":
                    self.state = "closed"
                    self.failure_count = 0
                    logger.info("Circuit breaker closed after successful recovery")
                elif self.state == "closed":
                    self.failure_count = 0
                
                return result
                
            except self.expected_exception as e:
                self.failure_count += 1
                self.last_failure_time = current_time
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
                    logger.error(
                        f"Circuit breaker OPENED after {self.failure_count} failures. "
                        f"Last error: {e}"
                    )
                
                raise

def with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: type = Exception
):
    """
    Decorator to add circuit breaker protection to async functions.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery
        expected_exception: Exception type that triggers circuit breaker
    """
    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            return await breaker.call(func, *args, **kwargs)
        
        wrapper.circuit_breaker = breaker
        return wrapper
    return decorator

# Global metrics collector
_global_metrics: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = MetricsCollector()
    return _global_metrics
