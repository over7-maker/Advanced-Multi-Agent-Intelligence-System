"""
Timeout Service for AMAS
Implements comprehensive timeout handling for all external calls
"""

import asyncio
import logging
import signal
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class TimeoutType(str, Enum):
    """Types of timeouts"""

    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"
    CACHE_OPERATION = "cache_operation"
    EXTERNAL_API = "external_api"
    FILE_OPERATION = "file_operation"
    AGENT_EXECUTION = "agent_execution"
    TASK_EXECUTION = "task_execution"
    GENERAL = "general"


@dataclass
class TimeoutConfig:
    """Configuration for timeout handling"""

    default_timeout: float = 30.0
    timeouts: Dict[TimeoutType, float] = None
    enable_graceful_shutdown: bool = True
    max_timeout: float = 300.0  # 5 minutes max
    min_timeout: float = 0.1  # 100ms min

    def __post_init__(self):
        if self.timeouts is None:
            self.timeouts = {
                TimeoutType.HTTP_REQUEST: 30.0,
                TimeoutType.DATABASE_QUERY: 10.0,
                TimeoutType.CACHE_OPERATION: 5.0,
                TimeoutType.EXTERNAL_API: 60.0,
                TimeoutType.FILE_OPERATION: 30.0,
                TimeoutType.AGENT_EXECUTION: 300.0,
                TimeoutType.TASK_EXECUTION: 600.0,
                TimeoutType.GENERAL: 30.0,
            }

    def get_timeout(self, timeout_type: TimeoutType) -> float:
        """Get timeout for specific type"""
        timeout = self.timeouts.get(timeout_type, self.default_timeout)
        return max(self.min_timeout, min(timeout, self.max_timeout))


class TimeoutException(Exception):
    """Exception raised when operation times out"""

    def __init__(
        self, operation: str, timeout: float, timeout_type: TimeoutType = None
    ):
        self.operation = operation
        self.timeout = timeout
        self.timeout_type = timeout_type
        super().__init__(f"Operation '{operation}' timed out after {timeout}s")


class TimeoutService:
    """Service for managing timeouts"""

    def __init__(self, config: TimeoutConfig = None):
        self.config = config or TimeoutConfig()
        self.logger = logging.getLogger(__name__)
        self.active_timeouts: Dict[str, asyncio.Task] = {}
        self.timeout_stats: Dict[str, Dict[str, Any]] = {}

    def _get_timeout(
        self, timeout_type: TimeoutType, custom_timeout: float = None
    ) -> float:
        """Get timeout value"""
        if custom_timeout is not None:
            return max(
                self.config.min_timeout, min(custom_timeout, self.config.max_timeout)
            )
        return self.config.get_timeout(timeout_type)

    def _record_timeout_stats(
        self,
        operation: str,
        timeout_type: TimeoutType,
        timed_out: bool,
        duration: float,
    ):
        """Record timeout statistics"""
        if operation not in self.timeout_stats:
            self.timeout_stats[operation] = {
                "total_calls": 0,
                "timeouts": 0,
                "total_duration": 0.0,
                "max_duration": 0.0,
                "min_duration": float("inf"),
                "timeout_type": timeout_type.value,
            }

        stats = self.timeout_stats[operation]
        stats["total_calls"] += 1
        stats["total_duration"] += duration
        stats["max_duration"] = max(stats["max_duration"], duration)
        stats["min_duration"] = min(stats["min_duration"], duration)

        if timed_out:
            stats["timeouts"] += 1

    async def with_timeout(
        self,
        operation: str,
        func: Callable,
        *args,
        timeout_type: TimeoutType = TimeoutType.GENERAL,
        custom_timeout: float = None,
        **kwargs,
    ) -> Any:
        """Execute function with timeout"""
        timeout_value = self._get_timeout(timeout_type, custom_timeout)
        start_time = time.time()

        try:
            # Create timeout task
            timeout_task = asyncio.create_task(
                asyncio.wait_for(
                    (
                        func(*args, **kwargs)
                        if asyncio.iscoroutinefunction(func)
                        else func(*args, **kwargs)
                    ),
                    timeout=timeout_value,
                )
            )

            # Store active timeout
            self.active_timeouts[operation] = timeout_task

            try:
                result = await timeout_task
                duration = time.time() - start_time
                self._record_timeout_stats(operation, timeout_type, False, duration)
                return result

            except asyncio.TimeoutError:
                duration = time.time() - start_time
                self._record_timeout_stats(operation, timeout_type, True, duration)
                self.logger.warning(
                    f"Operation '{operation}' timed out after {timeout_value}s"
                )
                raise TimeoutException(operation, timeout_value, timeout_type)

        finally:
            # Clean up active timeout
            if operation in self.active_timeouts:
                del self.active_timeouts[operation]

    def with_timeout_sync(
        self,
        operation: str,
        func: Callable,
        *args,
        timeout_type: TimeoutType = TimeoutType.GENERAL,
        custom_timeout: float = None,
        **kwargs,
    ) -> Any:
        """Execute synchronous function with timeout"""
        timeout_value = self._get_timeout(timeout_type, custom_timeout)
        start_time = time.time()

        try:
            # Use asyncio.run to handle timeout for sync functions
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                result = loop.run_until_complete(
                    asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, lambda: func(*args, **kwargs)
                        ),
                        timeout=timeout_value,
                    )
                )
                duration = time.time() - start_time
                self._record_timeout_stats(operation, timeout_type, False, duration)
                return result

            except asyncio.TimeoutError:
                duration = time.time() - start_time
                self._record_timeout_stats(operation, timeout_type, True, duration)
                self.logger.warning(
                    f"Operation '{operation}' timed out after {timeout_value}s"
                )
                raise TimeoutException(operation, timeout_value, timeout_type)

        finally:
            loop.close()

    @asynccontextmanager
    async def timeout_context(
        self,
        operation: str,
        timeout_type: TimeoutType = TimeoutType.GENERAL,
        custom_timeout: float = None,
    ):
        """Context manager for timeout handling"""
        timeout_value = self._get_timeout(timeout_type, custom_timeout)
        start_time = time.time()

        try:
            yield
            duration = time.time() - start_time
            self._record_timeout_stats(operation, timeout_type, False, duration)

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self._record_timeout_stats(operation, timeout_type, True, duration)
            self.logger.warning(
                f"Operation '{operation}' timed out after {timeout_value}s"
            )
            raise TimeoutException(operation, timeout_value, timeout_type)

    def cancel_operation(self, operation: str) -> bool:
        """Cancel a running operation"""
        if operation in self.active_timeouts:
            task = self.active_timeouts[operation]
            task.cancel()
            del self.active_timeouts[operation]
            self.logger.info(f"Cancelled operation '{operation}'")
            return True
        return False

    def cancel_all_operations(self):
        """Cancel all running operations"""
        for operation, task in self.active_timeouts.items():
            task.cancel()
            self.logger.info(f"Cancelled operation '{operation}'")

        self.active_timeouts.clear()

    def get_timeout_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get timeout statistics"""
        stats = {}
        for operation, data in self.timeout_stats.items():
            stats[operation] = {
                "total_calls": data["total_calls"],
                "timeouts": data["timeouts"],
                "timeout_rate": (
                    data["timeouts"] / data["total_calls"] * 100
                    if data["total_calls"] > 0
                    else 0
                ),
                "avg_duration": (
                    data["total_duration"] / data["total_calls"]
                    if data["total_calls"] > 0
                    else 0
                ),
                "max_duration": data["max_duration"],
                "min_duration": (
                    data["min_duration"] if data["min_duration"] != float("inf") else 0
                ),
                "timeout_type": data["timeout_type"],
            }
        return stats

    def get_active_operations(self) -> List[str]:
        """Get list of active operations"""
        return list(self.active_timeouts.keys())

    def update_timeout_config(self, timeout_type: TimeoutType, timeout_value: float):
        """Update timeout configuration"""
        self.config.timeouts[timeout_type] = max(
            self.config.min_timeout, min(timeout_value, self.config.max_timeout)
        )
        self.logger.info(
            f"Updated timeout for {timeout_type.value} to {timeout_value}s"
        )


# Global timeout service
timeout_service: Optional[TimeoutService] = None


def get_timeout_service() -> TimeoutService:
    """Get the global timeout service"""
    global timeout_service
    if timeout_service is None:
        timeout_service = TimeoutService()
    return timeout_service


def with_timeout(
    operation: str,
    timeout_type: TimeoutType = TimeoutType.GENERAL,
    custom_timeout: float = None,
):
    """Decorator for timeout handling"""

    def decorator(func: Callable) -> Callable:
        service = get_timeout_service()

        async def async_wrapper(*args, **kwargs):
            return await service.with_timeout(
                operation,
                func,
                *args,
                timeout_type=timeout_type,
                custom_timeout=custom_timeout,
                **kwargs,
            )

        def sync_wrapper(*args, **kwargs):
            return service.with_timeout_sync(
                operation,
                func,
                *args,
                timeout_type=timeout_type,
                custom_timeout=custom_timeout,
                **kwargs,
            )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Convenience decorators for common timeout types
def http_timeout(timeout: float = 30.0):
    """Decorator for HTTP request timeouts"""
    return with_timeout("http_request", TimeoutType.HTTP_REQUEST, timeout)


def database_timeout(timeout: float = 10.0):
    """Decorator for database operation timeouts"""
    return with_timeout("database_query", TimeoutType.DATABASE_QUERY, timeout)


def cache_timeout(timeout: float = 5.0):
    """Decorator for cache operation timeouts"""
    return with_timeout("cache_operation", TimeoutType.CACHE_OPERATION, timeout)


def external_api_timeout(timeout: float = 60.0):
    """Decorator for external API timeouts"""
    return with_timeout("external_api", TimeoutType.EXTERNAL_API, timeout)


def agent_timeout(timeout: float = 300.0):
    """Decorator for agent execution timeouts"""
    return with_timeout("agent_execution", TimeoutType.AGENT_EXECUTION, timeout)


def task_timeout(timeout: float = 600.0):
    """Decorator for task execution timeouts"""
    return with_timeout("task_execution", TimeoutType.TASK_EXECUTION, timeout)


# Graceful shutdown handling
class GracefulShutdownHandler:
    """Handler for graceful shutdown with timeout management"""

    def __init__(self, timeout_service: TimeoutService):
        self.timeout_service = timeout_service
        self.logger = logging.getLogger(__name__)
        self.shutdown_requested = False

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, "SIGINT"):
            signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
        self.timeout_service.cancel_all_operations()

    def is_shutdown_requested(self) -> bool:
        """Check if shutdown has been requested"""
        return self.shutdown_requested


# Initialize graceful shutdown handler
def initialize_graceful_shutdown():
    """Initialize graceful shutdown handling"""
    service = get_timeout_service()
    handler = GracefulShutdownHandler(service)
    handler.setup_signal_handlers()
    return handler
