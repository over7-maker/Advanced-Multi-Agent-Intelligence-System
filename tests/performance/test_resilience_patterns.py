"""
Tests for Resilience Patterns

Tests circuit breakers, rate limiting, request deduplication,
and other resilience patterns.
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock

from amas.services.circuit_breaker_service import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitBreakerOpenException,
    get_circuit_breaker_service
)
from amas.services.rate_limiting_service import (
    RateLimitingService,
    RateLimitConfig,
    get_rate_limiting_service
)
from amas.services.request_deduplication_service import (
    RequestDeduplicationService,
    DeduplicationConfig,
    get_deduplication_service
)


@pytest.mark.asyncio
async def test_circuit_breaker_closed_state():
    """Test circuit breaker in closed state allows calls"""
    config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=1.0,
        success_threshold=2
    )
    breaker = CircuitBreaker("test", config)
    
    assert breaker.state == CircuitState.CLOSED
    
    # Successful call
    async def success_func():
        return "success"
    
    result = await breaker.call(success_func)
    assert result == "success"
    assert breaker.success_count == 1
    assert breaker.failure_count == 0


@pytest.mark.asyncio
async def test_circuit_breaker_opens_on_failures():
    """Test circuit breaker opens after threshold failures"""
    config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=1.0,
        success_threshold=2
    )
    breaker = CircuitBreaker("test", config)
    
    # Fail 3 times
    async def fail_func():
        raise Exception("Test failure")
    
    for i in range(3):
        try:
            await breaker.call(fail_func)
        except Exception:
            pass
    
    # Circuit should be open
    assert breaker.state == CircuitState.OPEN
    assert breaker.circuit_opened_count == 1
    
    # Should fail fast
    with pytest.raises(CircuitBreakerOpenException):
        await breaker.call(fail_func)


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_recovery():
    """Test circuit breaker recovers through half-open state"""
    config = CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout=0.5,
        success_threshold=2
    )
    breaker = CircuitBreaker("test", config)
    
    # Open circuit
    async def fail_func():
        raise Exception("Test failure")
    
    for _ in range(2):
        try:
            await breaker.call(fail_func)
        except Exception:
            pass
    
    assert breaker.state == CircuitState.OPEN
    
    # Wait for recovery timeout
    await asyncio.sleep(0.6)
    
    # Next call should transition to half-open
    async def success_func():
        return "success"
    
    result = await breaker.call(success_func)
    assert breaker.state == CircuitState.HALF_OPEN
    
    # Second success should close circuit
    result = await breaker.call(success_func)
    assert breaker.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_rate_limiting_allows_requests():
    """Test rate limiting allows requests within limits"""
    config = RateLimitConfig(
        requests_per_minute=10,
        requests_per_hour=100,
        requests_per_day=1000
    )
    service = RateLimitingService(default_config=config)
    await service.initialize()
    
    # Make requests within limit
    for i in range(5):
        result = await service.check_rate_limit("user1")
        assert result.allowed is True
        assert result.remaining > 0
    
    await service.close()


@pytest.mark.asyncio
async def test_rate_limiting_blocks_excess():
    """Test rate limiting blocks requests exceeding limits"""
    config = RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=100,
        requests_per_day=1000
    )
    service = RateLimitingService(default_config=config)
    await service.initialize()
    
    # Clear any existing state for this user
    await service.reset_user_limits("user1")
    
    # Make requests up to limit (should all be allowed)
    for i in range(5):
        result = await service.check_rate_limit("user1")
        assert result.allowed is True, f"Request {i+1} should be allowed but got allowed={result.allowed}, remaining={result.remaining}"
        assert result.remaining >= 0, f"Request {i+1} should have remaining >= 0 but got {result.remaining}"
    
    # Next request should be blocked (6th request)
    result = await service.check_rate_limit("user1")
    assert result.allowed is False, f"6th request should be blocked but got allowed={result.allowed}, remaining={result.remaining}"
    assert result.retry_after is not None
    assert result.remaining == 0, f"Blocked request should have remaining=0 but got {result.remaining}"
    
    await service.close()


@pytest.mark.asyncio
async def test_rate_limiting_per_user():
    """Test rate limiting is per-user"""
    config = RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=100,
        requests_per_day=1000
    )
    service = RateLimitingService(default_config=config)
    await service.initialize()
    
    # Exhaust user1's limit
    for i in range(5):
        await service.check_rate_limit("user1")
    
    # user2 should still have requests
    result = await service.check_rate_limit("user2")
    assert result.allowed is True
    
    await service.close()


@pytest.mark.asyncio
async def test_request_deduplication():
    """Test request deduplication prevents duplicate concurrent requests"""
    service = RequestDeduplicationService()
    
    call_count = 0
    
    async def expensive_operation():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)
        return f"result_{call_count}"
    
    # Make 5 identical concurrent requests
    request_data = {"query": "test", "params": {"a": 1}}
    
    tasks = [
        service.deduplicate(request_data, expensive_operation)
        for _ in range(5)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Should only execute once
    assert call_count == 1
    # All should get same result
    assert all(r == "result_1" for r in results)
    
    await service.shutdown()


@pytest.mark.asyncio
async def test_request_deduplication_different_requests():
    """Test deduplication only applies to identical requests"""
    service = RequestDeduplicationService()
    
    call_count = 0
    
    async def operation(data):
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.05)
        return f"result_{data}"
    
    # Make different requests
    tasks = [
        service.deduplicate({"id": i}, operation, i)
        for i in range(5)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Should execute 5 times
    assert call_count == 5
    assert len(set(results)) == 5
    
    await service.shutdown()


@pytest.mark.asyncio
async def test_circuit_breaker_service_management():
    """Test circuit breaker service management"""
    service = get_circuit_breaker_service()
    
    # Create breaker
    breaker = service.create_breaker("test_breaker")
    assert service.get_breaker("test_breaker") is not None
    
    # Get stats
    stats = service.get_all_stats()
    assert "test_breaker" in stats
    
    # Reset breaker
    service.reset_breaker("test_breaker")
    
    # Remove breaker
    removed = service.remove_breaker("test_breaker")
    assert removed is True
    assert service.get_breaker("test_breaker") is None


@pytest.mark.asyncio
async def test_rate_limiting_custom_user_config():
    """Test rate limiting with custom user configuration"""
    service = RateLimitingService()
    await service.initialize()
    
    # Set custom config for user
    custom_config = RateLimitConfig(
        requests_per_minute=2,
        requests_per_hour=50,
        requests_per_day=500
    )
    service.set_user_config("premium_user", custom_config)
    
    # Premium user should have different limits
    result1 = await service.check_rate_limit("premium_user")
    assert result1.allowed is True
    
    result2 = await service.check_rate_limit("premium_user")
    assert result2.allowed is True
    
    # Third request should be blocked
    result3 = await service.check_rate_limit("premium_user")
    assert result3.allowed is False
    
    await service.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
