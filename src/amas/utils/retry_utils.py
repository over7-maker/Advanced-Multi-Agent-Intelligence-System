"""
Retry utilities with exponential backoff for AMAS
Implements robust retry mechanisms for external service calls
"""

import asyncio
import logging
import random
import time
from typing import Any, Callable, Dict, List, Optional, Type, Union
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)


class RetryStrategy(str, Enum):
    """Retry strategies"""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CUSTOM = "custom"


class RetryCondition(str, Enum):
    """Conditions for retrying"""
    ANY_EXCEPTION = "any_exception"
    HTTP_ERRORS = "http_errors"
    TIMEOUT_ERRORS = "timeout_errors"
    CONNECTION_ERRORS = "connection_errors"
    CUSTOM = "custom"


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        jitter: bool = True,
        backoff_multiplier: float = 2.0,
        condition: RetryCondition = RetryCondition.ANY_EXCEPTION,
        custom_condition: Optional[Callable[[Exception], bool]] = None,
        custom_delay_func: Optional[Callable[[int, float], float]] = None,
        exceptions: Optional[List[Type[Exception]]] = None
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.jitter = jitter
        self.backoff_multiplier = backoff_multiplier
        self.condition = condition
        self.custom_condition = custom_condition
        self.custom_delay_func = custom_delay_func
        self.exceptions = exceptions or [Exception]

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        if self.custom_delay_func:
            return self.custom_delay_func(attempt, self.base_delay)
        
        if self.strategy == RetryStrategy.FIXED:
            delay = self.base_delay
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay * attempt
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay * (self.backoff_multiplier ** (attempt - 1))
        else:
            delay = self.base_delay
        
        # Apply max delay limit
        delay = min(delay, self.max_delay)
        
        # Apply jitter to prevent thundering herd
        if self.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if we should retry based on exception and attempt"""
        if attempt >= self.max_attempts:
            return False
        
        if self.condition == RetryCondition.ANY_EXCEPTION:
            return isinstance(exception, tuple(self.exceptions))
        
        if self.condition == RetryCondition.HTTP_ERRORS:
            return self._is_http_error(exception)
        
        if self.condition == RetryCondition.TIMEOUT_ERRORS:
            return self._is_timeout_error(exception)
        
        if self.condition == RetryCondition.CONNECTION_ERRORS:
            return self._is_connection_error(exception)
        
        if self.condition == RetryCondition.CUSTOM and self.custom_condition:
            return self.custom_condition(exception)
        
        return False

    def _is_http_error(self, exception: Exception) -> bool:
        """Check if exception is an HTTP error"""
        try:
            from fastapi import HTTPException
            return isinstance(exception, HTTPException) and exception.status_code >= 500
        except ImportError:
            return False

    def _is_timeout_error(self, exception: Exception) -> bool:
        """Check if exception is a timeout error"""
        return (
            isinstance(exception, (asyncio.TimeoutError, TimeoutError)) or
            "timeout" in str(exception).lower() or
            "timed out" in str(exception).lower()
        )

    def _is_connection_error(self, exception: Exception) -> bool:
        """Check if exception is a connection error"""
        return (
            "connection" in str(exception).lower() or
            "network" in str(exception).lower() or
            "unreachable" in str(exception).lower()
        )


class RetryManager:
    """Manager for retry operations"""

    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.logger = logging.getLogger(__name__)

    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                if attempt > 1:
                    self.logger.info(f"Function {func.__name__} succeeded on attempt {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if not self.config.should_retry(e, attempt):
                    self.logger.warning(f"Function {func.__name__} failed on attempt {attempt}, not retrying: {e}")
                    break
                
                if attempt < self.config.max_attempts:
                    delay = self.config.calculate_delay(attempt)
                    self.logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt}, retrying in {delay:.2f}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"Function {func.__name__} failed after {attempt} attempts: {e}")
        
        # If we get here, all retries failed
        raise last_exception

    def execute_with_retry_sync(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute synchronous function with retry logic"""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 1:
                    self.logger.info(f"Function {func.__name__} succeeded on attempt {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if not self.config.should_retry(e, attempt):
                    self.logger.warning(f"Function {func.__name__} failed on attempt {attempt}, not retrying: {e}")
                    break
                
                if attempt < self.config.max_attempts:
                    delay = self.config.calculate_delay(attempt)
                    self.logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt}, retrying in {delay:.2f}s: {e}"
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"Function {func.__name__} failed after {attempt} attempts: {e}")
        
        # If we get here, all retries failed
        raise last_exception


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    jitter: bool = True,
    backoff_multiplier: float = 2.0,
    condition: RetryCondition = RetryCondition.ANY_EXCEPTION,
    custom_condition: Optional[Callable[[Exception], bool]] = None,
    custom_delay_func: Optional[Callable[[int, float], float]] = None,
    exceptions: Optional[List[Type[Exception]]] = None
):
    """Decorator for retrying function calls"""
    
    def decorator(func: Callable) -> Callable:
        config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=strategy,
            jitter=jitter,
            backoff_multiplier=backoff_multiplier,
            condition=condition,
            custom_condition=custom_condition,
            custom_delay_func=custom_delay_func,
            exceptions=exceptions
        )
        
        manager = RetryManager(config)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await manager.execute_with_retry(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return manager.execute_with_retry_sync(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_http_errors(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """Decorator for retrying HTTP errors specifically"""
    return retry(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        condition=RetryCondition.HTTP_ERRORS
    )


def retry_timeout_errors(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """Decorator for retrying timeout errors specifically"""
    return retry(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        condition=RetryCondition.TIMEOUT_ERRORS
    )


def retry_connection_errors(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """Decorator for retrying connection errors specifically"""
    return retry(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        condition=RetryCondition.CONNECTION_ERRORS
    )


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
        self.logger = logging.getLogger(__name__)

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            if asyncio.iscoroutinefunction(func):
                result = asyncio.run(func(*args, **kwargs))
            else:
                result = func(*args, **kwargs)
            
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.logger.info("Circuit breaker transitioning to CLOSED")

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception
):
    """Decorator for circuit breaker pattern"""
    
    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await breaker.call_async(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Predefined retry configurations
DEFAULT_RETRY_CONFIG = RetryConfig()
HTTP_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=30.0,
    condition=RetryCondition.HTTP_ERRORS
)
TIMEOUT_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=0.5,
    max_delay=10.0,
    condition=RetryCondition.TIMEOUT_ERRORS
)
CONNECTION_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    max_delay=60.0,
    condition=RetryCondition.CONNECTION_ERRORS
)

# Global retry manager instances
default_retry_manager = RetryManager(DEFAULT_RETRY_CONFIG)
http_retry_manager = RetryManager(HTTP_RETRY_CONFIG)
timeout_retry_manager = RetryManager(TIMEOUT_RETRY_CONFIG)
connection_retry_manager = RetryManager(CONNECTION_RETRY_CONFIG)