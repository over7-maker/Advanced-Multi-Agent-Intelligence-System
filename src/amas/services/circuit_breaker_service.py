"""
Circuit Breaker Service for AMAS
Implements circuit breaker pattern for external service calls
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Type
from enum import Enum
from dataclasses import dataclass
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 3
    timeout: float = 30.0
    expected_exceptions: List[Type[Exception]] = None
    
    def __post_init__(self):
        if self.expected_exceptions is None:
            self.expected_exceptions = [Exception]


class CircuitBreaker:
    """Circuit breaker implementation"""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"circuit_breaker.{name}")
        
        # State
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
        # Statistics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.circuit_opened_count = 0

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.state != CircuitState.OPEN:
            return False
        
        if not self.last_failure_time:
            return False
        
        return time.time() - self.last_failure_time >= self.config.recovery_timeout

    def _should_close_circuit(self) -> bool:
        """Check if we should close the circuit (move from half-open to closed)"""
        return (
            self.state == CircuitState.HALF_OPEN and
            self.success_count >= self.config.success_threshold
        )

    def _should_open_circuit(self) -> bool:
        """Check if we should open the circuit"""
        return self.failure_count >= self.config.failure_threshold

    def _transition_to_open(self):
        """Transition circuit to open state"""
        self.state = CircuitState.OPEN
        self.failure_count = 0
        self.success_count = 0
        self.circuit_opened_count += 1
        self.logger.warning(f"Circuit breaker '{self.name}' opened after {self.failure_count} failures")

    def _transition_to_half_open(self):
        """Transition circuit to half-open state"""
        self.state = CircuitState.HALF_OPEN
        self.failure_count = 0
        self.success_count = 0
        self.logger.info(f"Circuit breaker '{self.name}' transitioned to half-open")

    def _transition_to_closed(self):
        """Transition circuit to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.logger.info(f"Circuit breaker '{self.name}' closed - service recovered")

    def _record_success(self):
        """Record a successful call"""
        self.success_count += 1
        self.successful_calls += 1
        self.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN and self._should_close_circuit():
            self._transition_to_closed()

    def _record_failure(self, exception: Exception):
        """Record a failed call"""
        self.failure_count += 1
        self.failed_calls += 1
        self.last_failure_time = time.time()
        
        if self._should_open_circuit():
            self._transition_to_open()

    def _is_call_allowed(self) -> bool:
        """Check if calls are allowed in current state"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.HALF_OPEN:
            return True
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
                return True
            return False
        
        return False

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        self.total_calls += 1
        
        if not self._is_call_allowed():
            raise CircuitBreakerOpenException(f"Circuit breaker '{self.name}' is open")
        
        try:
            # Add timeout if specified
            if self.config.timeout > 0:
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
            else:
                result = await func(*args, **kwargs)
            
            self._record_success()
            return result
            
        except asyncio.TimeoutError:
            self._record_failure(asyncio.TimeoutError())
            raise CircuitBreakerTimeoutException(f"Circuit breaker '{self.name}' timeout after {self.config.timeout}s")
        
        except Exception as e:
            # Check if this exception should be counted as a failure
            if any(isinstance(e, exc_type) for exc_type in self.config.expected_exceptions):
                self._record_failure(e)
            else:
                # Unexpected exception, don't count as circuit breaker failure
                self.logger.warning(f"Unexpected exception in circuit breaker '{self.name}': {e}")
            
            raise e

    def call_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Execute synchronous function with circuit breaker protection"""
        self.total_calls += 1
        
        if not self._is_call_allowed():
            raise CircuitBreakerOpenException(f"Circuit breaker '{self.name}' is open")
        
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
            
        except Exception as e:
            if any(isinstance(e, exc_type) for exc_type in self.config.expected_exceptions):
                self._record_failure(e)
            else:
                self.logger.warning(f"Unexpected exception in circuit breaker '{self.name}': {e}")
            
            raise e

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "circuit_opened_count": self.circuit_opened_count,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "success_rate": (
                self.successful_calls / self.total_calls * 100
                if self.total_calls > 0 else 0
            )
        }

    def reset(self):
        """Reset circuit breaker to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.logger.info(f"Circuit breaker '{self.name}' manually reset")


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreakerTimeoutException(Exception):
    """Exception raised when circuit breaker times out"""
    pass


class CircuitBreakerService:
    """Service for managing circuit breakers"""

    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.logger = logging.getLogger(__name__)

    def create_breaker(
        self,
        name: str,
        config: CircuitBreakerConfig = None
    ) -> CircuitBreaker:
        """Create a new circuit breaker"""
        if name in self.breakers:
            self.logger.warning(f"Circuit breaker '{name}' already exists, replacing")
        
        config = config or CircuitBreakerConfig()
        breaker = CircuitBreaker(name, config)
        self.breakers[name] = breaker
        
        self.logger.info(f"Created circuit breaker '{name}' with config: {config}")
        return breaker

    def get_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self.breakers.get(name)

    def remove_breaker(self, name: str) -> bool:
        """Remove circuit breaker"""
        if name in self.breakers:
            del self.breakers[name]
            self.logger.info(f"Removed circuit breaker '{name}'")
            return True
        return False

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers"""
        return {name: breaker.get_stats() for name, breaker in self.breakers.items()}

    def reset_breaker(self, name: str) -> bool:
        """Reset circuit breaker"""
        breaker = self.get_breaker(name)
        if breaker:
            breaker.reset()
            return True
        return False

    def reset_all_breakers(self):
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker.reset()
        self.logger.info("Reset all circuit breakers")

    @asynccontextmanager
    async def breaker_context(self, name: str, func: Callable, *args, **kwargs):
        """Context manager for circuit breaker calls"""
        breaker = self.get_breaker(name)
        if not breaker:
            # If breaker doesn't exist, just call the function
            yield await func(*args, **kwargs)
            return
        
        try:
            result = await breaker.call(func, *args, **kwargs)
            yield result
        except (CircuitBreakerOpenException, CircuitBreakerTimeoutException) as e:
            self.logger.warning(f"Circuit breaker '{name}' prevented call: {e}")
            raise


# Global circuit breaker service
circuit_breaker_service = CircuitBreakerService()


def get_circuit_breaker_service() -> CircuitBreakerService:
    """Get the global circuit breaker service"""
    return circuit_breaker_service


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    success_threshold: int = 3,
    timeout: float = 30.0,
    expected_exceptions: List[Type[Exception]] = None
):
    """Decorator for circuit breaker pattern"""
    def decorator(func: Callable) -> Callable:
        # Create circuit breaker
        config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            success_threshold=success_threshold,
            timeout=timeout,
            expected_exceptions=expected_exceptions or [Exception]
        )
        
        breaker = circuit_breaker_service.create_breaker(name, config)
        
        @asynccontextmanager
        async def async_context(*args, **kwargs):
            async with circuit_breaker_service.breaker_context(name, func, *args, **kwargs) as result:
                yield result
        
        @asynccontextmanager
        def sync_context(*args, **kwargs):
            try:
                result = breaker.call_sync(func, *args, **kwargs)
                yield result
            except (CircuitBreakerOpenException, CircuitBreakerTimeoutException) as e:
                logger.warning(f"Circuit breaker '{name}' prevented call: {e}")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_context
        else:
            return sync_context
    
    return decorator


# Predefined circuit breaker configurations
DATABASE_BREAKER_CONFIG = CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=30.0,
    success_threshold=2,
    timeout=10.0,
    expected_exceptions=[Exception]
)

REDIS_BREAKER_CONFIG = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60.0,
    success_threshold=3,
    timeout=5.0,
    expected_exceptions=[Exception]
)

EXTERNAL_API_BREAKER_CONFIG = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=120.0,
    success_threshold=3,
    timeout=30.0,
    expected_exceptions=[Exception]
)

# Create default circuit breakers
def initialize_default_breakers():
    """Initialize default circuit breakers"""
    service = get_circuit_breaker_service()
    
    # Database circuit breaker
    service.create_breaker("database", DATABASE_BREAKER_CONFIG)
    
    # Redis circuit breaker
    service.create_breaker("redis", REDIS_BREAKER_CONFIG)
    
    # External API circuit breaker
    service.create_breaker("external_api", EXTERNAL_API_BREAKER_CONFIG)
    
    logger.info("Initialized default circuit breakers")


# Initialize default breakers
initialize_default_breakers()