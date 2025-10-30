"""
Error Recovery Service for AMAS
Implements comprehensive error recovery procedures and automated healing
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class RecoveryStrategy(str, Enum):
    """Error recovery strategies"""

    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    MANUAL_INTERVENTION = "manual_intervention"
    RESTART_SERVICE = "restart_service"
    FAILOVER = "failover"


class ErrorSeverity(str, Enum):
    """Error severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RecoveryConfig:
    """Configuration for error recovery"""

    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    max_retry_delay: float = 60.0
    fallback_timeout: float = 30.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    auto_healing_enabled: bool = True
    manual_intervention_threshold: int = 10


@dataclass
class ErrorContext:
    """Context information for error recovery"""

    error_type: str
    error_message: str
    severity: ErrorSeverity
    component: str
    operation: str
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp: datetime = None
    retry_count: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class RecoveryAction:
    """Base class for recovery actions"""

    def __init__(self, name: str, config: RecoveryConfig):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"recovery.{name}")

    async def execute(self, context: ErrorContext) -> bool:
        """Execute the recovery action"""
        raise NotImplementedError


class RetryAction(RecoveryAction):
    """Retry the failed operation"""

    async def execute(self, context: ErrorContext) -> bool:
        """Execute retry with exponential backoff"""
        if context.retry_count >= self.config.max_retries:
            self.logger.warning(f"Max retries exceeded for {context.operation}")
            return False

        # Calculate delay with exponential backoff
        delay = self.config.retry_delay
        if self.config.exponential_backoff:
            delay *= 2**context.retry_count

        delay = min(delay, self.config.max_retry_delay)

        self.logger.info(
            f"Retrying {context.operation} in {delay}s (attempt {context.retry_count + 1})"
        )
        await asyncio.sleep(delay)

        return True


class FallbackAction(RecoveryAction):
    """Execute fallback operation"""

    def __init__(self, name: str, config: RecoveryConfig, fallback_func: Callable):
        super().__init__(name, config)
        self.fallback_func = fallback_func

    async def execute(self, context: ErrorContext) -> bool:
        """Execute fallback operation"""
        try:
            self.logger.info(f"Executing fallback for {context.operation}")

            if asyncio.iscoroutinefunction(self.fallback_func):
                result = await asyncio.wait_for(
                    self.fallback_func(context), timeout=self.config.fallback_timeout
                )
            else:
                result = self.fallback_func(context)

            self.logger.info(f"Fallback successful for {context.operation}")
            return True

        except Exception as e:
            self.logger.error(f"Fallback failed for {context.operation}: {e}")
            return False


class CircuitBreakerAction(RecoveryAction):
    """Open circuit breaker to prevent cascading failures"""

    def __init__(self, name: str, config: RecoveryConfig, circuit_breaker_name: str):
        super().__init__(name, config)
        self.circuit_breaker_name = circuit_breaker_name

    async def execute(self, context: ErrorContext) -> bool:
        """Open circuit breaker"""
        try:
            from src.amas.services.circuit_breaker_service import (
                get_circuit_breaker_service,
            )

            service = get_circuit_breaker_service()
            breaker = service.get_breaker(self.circuit_breaker_name)

            if breaker:
                breaker._transition_to_open()
                self.logger.warning(
                    f"Circuit breaker '{self.circuit_breaker_name}' opened due to errors"
                )
                return True
            else:
                self.logger.error(
                    f"Circuit breaker '{self.circuit_breaker_name}' not found"
                )
                return False

        except Exception as e:
            self.logger.error(f"Failed to open circuit breaker: {e}")
            return False


class GracefulDegradationAction(RecoveryAction):
    """Implement graceful degradation"""

    def __init__(self, name: str, config: RecoveryConfig, degraded_func: Callable):
        super().__init__(name, config)
        self.degraded_func = degraded_func

    async def execute(self, context: ErrorContext) -> bool:
        """Execute degraded operation"""
        try:
            self.logger.info(f"Executing degraded operation for {context.operation}")

            if asyncio.iscoroutinefunction(self.degraded_func):
                result = await self.degraded_func(context)
            else:
                result = self.degraded_func(context)

            self.logger.info(f"Degraded operation successful for {context.operation}")
            return True

        except Exception as e:
            self.logger.error(f"Degraded operation failed for {context.operation}: {e}")
            return False


class ServiceRestartAction(RecoveryAction):
    """Restart a service component"""

    def __init__(
        self,
        name: str,
        config: RecoveryConfig,
        service_name: str,
        restart_func: Callable,
    ):
        super().__init__(name, config)
        self.service_name = service_name
        self.restart_func = restart_func

    async def execute(self, context: ErrorContext) -> bool:
        """Restart the service"""
        try:
            self.logger.warning(
                f"Restarting service '{self.service_name}' due to errors"
            )

            if asyncio.iscoroutinefunction(self.restart_func):
                await self.restart_func(context)
            else:
                self.restart_func(context)

            self.logger.info(f"Service '{self.service_name}' restarted successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to restart service '{self.service_name}': {e}")
            return False


class ErrorRecoveryService:
    """Service for managing error recovery procedures"""

    def __init__(self, config: RecoveryConfig = None):
        self.config = config or RecoveryConfig()
        self.logger = logging.getLogger(__name__)
        self.recovery_actions: Dict[str, List[RecoveryAction]] = {}
        self.error_history: List[ErrorContext] = []
        self.recovery_stats: Dict[str, Dict[str, int]] = {}

        # Initialize default recovery strategies
        self._setup_default_recovery_strategies()

    def _setup_default_recovery_strategies(self):
        """Setup default recovery strategies for common error types"""

        # Database errors
        self.add_recovery_strategy(
            "database_error",
            [
                RetryAction("retry", self.config),
                CircuitBreakerAction("circuit_breaker", self.config, "database"),
                FallbackAction("fallback", self.config, self._database_fallback),
            ],
        )

        # Redis errors
        self.add_recovery_strategy(
            "redis_error",
            [
                RetryAction("retry", self.config),
                CircuitBreakerAction("circuit_breaker", self.config, "redis"),
                FallbackAction("fallback", self.config, self._redis_fallback),
            ],
        )

        # External API errors
        self.add_recovery_strategy(
            "external_api_error",
            [
                RetryAction("retry", self.config),
                CircuitBreakerAction("circuit_breaker", self.config, "external_api"),
                GracefulDegradationAction(
                    "degradation", self.config, self._api_degradation
                ),
            ],
        )

        # Authentication errors
        self.add_recovery_strategy(
            "auth_error",
            [
                RetryAction("retry", self.config),
                FallbackAction("fallback", self.config, self._auth_fallback),
            ],
        )

        # Memory errors
        self.add_recovery_strategy(
            "memory_error",
            [
                GracefulDegradationAction(
                    "degradation", self.config, self._memory_degradation
                ),
                ServiceRestartAction(
                    "restart", self.config, "memory_cleanup", self._cleanup_memory
                ),
            ],
        )

    def add_recovery_strategy(self, error_type: str, actions: List[RecoveryAction]):
        """Add recovery strategy for specific error type"""
        self.recovery_actions[error_type] = actions
        self.logger.info(
            f"Added recovery strategy for {error_type} with {len(actions)} actions"
        )

    async def handle_error(self, context: ErrorContext) -> bool:
        """Handle error with appropriate recovery strategy"""
        self.logger.error(
            f"Handling error: {context.error_type} - {context.error_message}"
        )

        # Record error in history
        self.error_history.append(context)

        # Update statistics
        self._update_recovery_stats(context.error_type, "error_occurred")

        # Get recovery strategy
        strategy = self.recovery_actions.get(context.error_type, [])
        if not strategy:
            self.logger.warning(f"No recovery strategy found for {context.error_type}")
            return False

        # Execute recovery actions
        for action in strategy:
            try:
                success = await action.execute(context)
                if success:
                    self._update_recovery_stats(
                        context.error_type, f"{action.name}_success"
                    )
                    self.logger.info(
                        f"Recovery action '{action.name}' succeeded for {context.error_type}"
                    )
                    return True
                else:
                    self._update_recovery_stats(
                        context.error_type, f"{action.name}_failed"
                    )
                    self.logger.warning(
                        f"Recovery action '{action.name}' failed for {context.error_type}"
                    )
            except Exception as e:
                self.logger.error(
                    f"Recovery action '{action.name}' raised exception: {e}"
                )
                self._update_recovery_stats(
                    context.error_type, f"{action.name}_exception"
                )

        # All recovery actions failed
        self.logger.error(f"All recovery actions failed for {context.error_type}")
        self._update_recovery_stats(context.error_type, "all_actions_failed")
        return False

    def _update_recovery_stats(self, error_type: str, action: str):
        """Update recovery statistics"""
        if error_type not in self.recovery_stats:
            self.recovery_stats[error_type] = {}

        if action not in self.recovery_stats[error_type]:
            self.recovery_stats[error_type][action] = 0

        self.recovery_stats[error_type][action] += 1

    def get_recovery_stats(self) -> Dict[str, Dict[str, int]]:
        """Get recovery statistics"""
        return self.recovery_stats

    def get_error_history(self, limit: int = 100) -> List[ErrorContext]:
        """Get recent error history"""
        return self.error_history[-limit:]

    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.logger.info("Error history cleared")

    # Fallback implementations
    async def _database_fallback(self, context: ErrorContext) -> Any:
        """Fallback for database errors"""
        self.logger.info("Using database fallback - returning cached data")
        # In a real implementation, return cached data or use read-only mode
        return {"status": "degraded", "data": "cached"}

    async def _redis_fallback(self, context: ErrorContext) -> Any:
        """Fallback for Redis errors"""
        self.logger.info("Using Redis fallback - using in-memory cache")
        # In a real implementation, use in-memory cache
        return {"status": "degraded", "cache": "memory"}

    async def _api_degradation(self, context: ErrorContext) -> Any:
        """Graceful degradation for external API errors"""
        self.logger.info("Using API degradation - returning limited functionality")
        # In a real implementation, return limited functionality
        return {"status": "degraded", "features": "limited"}

    async def _auth_fallback(self, context: ErrorContext) -> Any:
        """Fallback for authentication errors"""
        self.logger.info("Using auth fallback - allowing read-only access")
        # In a real implementation, allow read-only access
        return {"status": "degraded", "access": "read_only"}

    async def _memory_degradation(self, context: ErrorContext) -> Any:
        """Graceful degradation for memory errors"""
        self.logger.info("Using memory degradation - reducing functionality")
        # In a real implementation, reduce functionality to save memory
        return {"status": "degraded", "memory": "conservative"}

    async def _cleanup_memory(self, context: ErrorContext) -> Any:
        """Clean up memory"""
        self.logger.info("Performing memory cleanup")
        import gc

        gc.collect()
        return {"status": "cleaned", "memory": "freed"}


# Global error recovery service
error_recovery_service: Optional[ErrorRecoveryService] = None


def get_error_recovery_service() -> ErrorRecoveryService:
    """Get the global error recovery service"""
    global error_recovery_service
    if error_recovery_service is None:
        error_recovery_service = ErrorRecoveryService()
    return error_recovery_service


def recover_from_error(
    error_type: str,
    error_message: str,
    severity: ErrorSeverity,
    component: str,
    operation: str,
    user_id: str = None,
    correlation_id: str = None,
    metadata: Dict[str, Any] = None,
) -> bool:
    """Convenience function to recover from error"""
    context = ErrorContext(
        error_type=error_type,
        error_message=error_message,
        severity=severity,
        component=component,
        operation=operation,
        user_id=user_id,
        correlation_id=correlation_id,
        metadata=metadata or {},
    )

    service = get_error_recovery_service()
    return asyncio.run(service.handle_error(context))


# Decorator for automatic error recovery
def auto_recover(error_type: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """Decorator for automatic error recovery"""

    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                service = get_error_recovery_service()
                context = ErrorContext(
                    error_type=error_type,
                    error_message=str(e),
                    severity=severity,
                    component=func.__module__,
                    operation=func.__name__,
                )

                success = await service.handle_error(context)
                if not success:
                    raise e

                return None  # Recovery succeeded but operation failed

        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                service = get_error_recovery_service()
                context = ErrorContext(
                    error_type=error_type,
                    error_message=str(e),
                    severity=severity,
                    component=func.__module__,
                    operation=func.__name__,
                )

                success = asyncio.run(service.handle_error(context))
                if not success:
                    raise e

                return None  # Recovery succeeded but operation failed

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
