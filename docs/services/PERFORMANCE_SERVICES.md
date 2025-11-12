# ⚡ Performance & Scaling Services

> **Version**: 1.0.0 | **Last Updated**: 2025-11-09 | **Status**: ✅ Production Ready

## Overview

This document provides comprehensive documentation for all performance, scaling, and resilience services implemented in AMAS. These services work together to provide intelligent autoscaling, caching, cost optimization, and system resilience.

## 📋 Table of Contents

- [Semantic Cache Service](#semantic-cache-service)
- [Circuit Breaker Service](#circuit-breaker-service)
- [Rate Limiting Service](#rate-limiting-service)
- [Request Deduplication Service](#request-deduplication-service)
- [Cost Tracking Service](#cost-tracking-service)
- [Connection Pool Service](#connection-pool-service)
- [Scaling Metrics Service](#scaling-metrics-service)
- [Integration Examples](#integration-examples)

---

## 🗄️ Semantic Cache Service

**Location**: `src/amas/services/semantic_cache_service.py`

### Overview

Intelligent Redis-based caching for agent responses using embedding-based semantic similarity matching. Provides 30%+ speed improvement for repeated or similar requests.

### Features

- **Semantic Similarity**: Uses `sentence-transformers` for embedding-based matching
- **Configurable TTL**: Per-key and default TTL support
- **Hit/Miss Tracking**: Comprehensive cache statistics
- **Redis-Backed**: Distributed caching with in-memory fallback

### Usage

```python
from amas.services import SemanticCacheService, get_semantic_cache

# Get service instance
cache = get_semantic_cache()

# Store a response
await cache.set(
    key="user_query_123",
    value={"response": "AI-generated answer", "metadata": {...}},
    ttl=3600  # 1 hour
)

# Retrieve by exact key
cached = await cache.get("user_query_123")

# Retrieve by semantic similarity
similar = await cache.get_similar(
    query="What is artificial intelligence?",
    threshold=0.85,  # Similarity threshold
    max_results=5
)

# Get cache statistics
stats = await cache.get_stats()
# Returns: {"hits": 150, "misses": 50, "hit_rate": 0.75}
```

### Configuration

```python
from amas.services import SemanticCacheService

cache = SemanticCacheService(
    redis_url="redis://localhost:6379",
    default_ttl=3600,
    similarity_threshold=0.85,
    embedding_model="all-MiniLM-L6-v2"
)
```

### API Reference

- `set(key: str, value: Any, ttl: Optional[int] = None) -> None`
- `get(key: str) -> Optional[Any]`
- `get_similar(query: str, threshold: float = 0.85, max_results: int = 5) -> List[Dict]`
- `delete(key: str) -> None`
- `clear() -> None`
- `get_stats() -> Dict[str, Any]`

---

## 🔌 Circuit Breaker Service

**Location**: `src/amas/services/circuit_breaker_service.py`

### Overview

Implements the circuit breaker pattern to prevent cascade failures in external service calls. Automatically opens when failure threshold is exceeded and attempts recovery.

### Features

- **Three States**: CLOSED (normal), OPEN (failing), HALF_OPEN (testing recovery)
- **Configurable Thresholds**: Failure count, timeout, recovery window
- **Exception Handling**: Custom exception types and handling
- **Metrics Integration**: Tracks state transitions and failures

### Usage

```python
from amas.services import CircuitBreakerService, CircuitBreakerConfig, get_circuit_breaker_service

# Get service instance
breaker = get_circuit_breaker_service()

# Configure circuit breaker
config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=Exception
)

# Use with async context manager
async with breaker.circuit("external_api") as cb:
    try:
        result = await external_api_call()
        cb.record_success()
        return result
    except Exception as e:
        cb.record_failure()
        raise

# Or use decorator pattern
@breaker.protect("external_api")
async def call_external_api():
    return await external_api_call()
```

### Configuration

```python
config = CircuitBreakerConfig(
    failure_threshold=5,        # Open after 5 failures
    recovery_timeout=60,        # Wait 60s before half-open
    expected_exception=Exception,
    half_open_max_calls=3       # Test with 3 calls in half-open
)
```

### API Reference

- `circuit(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker`
- `protect(name: str, config: Optional[CircuitBreakerConfig] = None) -> Callable`
- `get_state(name: str) -> str`
- `reset(name: str) -> None`

---

## 🚦 Rate Limiting Service

**Location**: `src/amas/services/rate_limiting_service.py`

### Overview

Intelligent rate limiting with user-based quotas using a sliding window algorithm. Supports multiple time windows (minute, hour, day) with Redis-backed distributed limiting.

### Features

- **Sliding Window**: Accurate rate limiting without fixed windows
- **User-Based Quotas**: Per-user rate limits
- **Multiple Windows**: Minute, hour, and daily limits
- **Redis-Backed**: Distributed rate limiting with in-memory fallback

### Usage

```python
from amas.services import RateLimitingService, RateLimitConfig, get_rate_limiting_service

# Get service instance
rate_limiter = get_rate_limiting_service()

# Check rate limit
result = await rate_limiter.check_limit(
    user_id="user_123",
    resource="api_calls",
    limit=100,  # 100 requests
    window=60   # per minute
)

if result.allowed:
    # Process request
    await process_request()
else:
    # Rate limit exceeded
    raise RateLimitExceeded(
        f"Rate limit exceeded. Retry after {result.retry_after} seconds"
    )

# Get current usage
usage = await rate_limiter.get_usage("user_123", "api_calls")
# Returns: {"used": 45, "limit": 100, "remaining": 55}
```

### Configuration

```python
config = RateLimitConfig(
    default_limit=100,
    default_window=60,
    redis_url="redis://localhost:6379",
    enable_distributed=True
)
```

### API Reference

- `check_limit(user_id: str, resource: str, limit: int, window: int) -> RateLimitResult`
- `get_usage(user_id: str, resource: str) -> Dict[str, Any]`
- `reset_limit(user_id: str, resource: str) -> None`

---

## 🔄 Request Deduplication Service

**Location**: `src/amas/services/request_deduplication_service.py`

### Overview

Eliminates duplicate concurrent requests by tracking in-flight requests and sharing results. Reduces redundant API calls and improves efficiency.

### Features

- **Concurrent Request Tracking**: Tracks in-flight requests
- **Result Sharing**: Shares results between identical concurrent requests
- **TTL-Based Cleanup**: Automatic cleanup of stale entries
- **Background Tasks**: Async cleanup tasks

### Usage

```python
from amas.services import RequestDeduplicationService, DeduplicationConfig, get_deduplication_service

# Get service instance
dedup = get_deduplication_service()

# Deduplicate request
async def expensive_operation(request_id: str, params: dict):
    async with dedup.deduplicate(
        key=f"operation_{request_id}",
        ttl=300  # 5 minutes
    ) as result:
        if result.is_duplicate:
            # Another request is processing this, wait for result
            return await result.wait()
        else:
            # This is the first request, execute operation
            result = await perform_expensive_operation(params)
            result.set_result(result)
            return result
```

### Configuration

```python
config = DeduplicationConfig(
    default_ttl=300,  # 5 minutes
    cleanup_interval=60  # Cleanup every minute
)
```

### API Reference

- `deduplicate(key: str, ttl: int = 300) -> DeduplicationContext`
- `is_duplicate(key: str) -> bool`
- `get_result(key: str) -> Optional[Any]`

---

## 💰 Cost Tracking Service

**Location**: `src/amas/services/cost_tracking_service.py`

### Overview

Tracks token usage, API costs, and infrastructure costs per request. Provides cost analytics and optimization recommendations.

### Features

- **Token Tracking**: Tracks input/output tokens per provider/model
- **Cost Calculation**: Automatic cost calculation by provider/model
- **Budget Monitoring**: Daily budget tracking and alerts
- **Optimization Recommendations**: Cost-saving suggestions

### Usage

```python
from amas.services import CostTrackingService, CostEntry, get_cost_tracking_service

# Get service instance
cost_tracker = get_cost_tracking_service()

# Track API call cost
await cost_tracker.track_request(
    user_id="user_123",
    provider="openai",
    model="gpt-4",
    input_tokens=1000,
    output_tokens=500,
    metadata={"request_id": "req_456"}
)

# Get cost summary
summary = await cost_tracker.get_summary(
    user_id="user_123",
    start_date="2025-11-01",
    end_date="2025-11-09"
)
# Returns: CostSummary with total_cost, token_usage, by_provider, etc.

# Get optimization recommendations
recommendations = await cost_tracker.get_recommendations("user_123")
# Returns: List of optimization suggestions
```

### Configuration

```python
from amas.services import CostTrackingService

cost_tracker = CostTrackingService(
    redis_url="redis://localhost:6379",
    cost_config={
        "openai": {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        }
    }
)
```

### API Reference

- `track_request(user_id: str, provider: str, model: str, input_tokens: int, output_tokens: int, metadata: Optional[Dict] = None) -> None`
- `get_summary(user_id: str, start_date: str, end_date: str) -> CostSummary`
- `get_recommendations(user_id: str) -> List[Dict]`
- `check_budget(user_id: str, daily_budget: float) -> Dict[str, Any]`

---

## 🔗 Connection Pool Service

**Location**: `src/amas/services/connection_pool_service.py`

### Overview

Manages optimized `httpx.AsyncClient` instances with connection pooling, configurable limits, timeouts, and HTTP/2 support for efficient connection reuse.

### Features

- **Connection Pooling**: Reuses connections for better performance
- **HTTP/2 Support**: Automatic HTTP/2 negotiation
- **Configurable Limits**: Max connections, timeouts, retries
- **Per-Domain Pools**: Separate pools for different domains

### Usage

```python
from amas.services import ConnectionPoolService, get_connection_pool_service

# Get service instance
pool_service = get_connection_pool_service()

# Get optimized client
client = await pool_service.get_client(
    base_url="https://api.example.com",
    max_connections=100,
    timeout=30.0
)

# Use client
response = await client.get("/endpoint")
data = response.json()

# Client is automatically pooled and reused
```

### Configuration

```python
from amas.services import ConnectionPoolService

pool_service = ConnectionPoolService(
    default_timeout=30.0,
    default_max_connections=100,
    enable_http2=True
)
```

### API Reference

- `get_client(base_url: str, max_connections: int = 100, timeout: float = 30.0) -> httpx.AsyncClient`
- `close_all() -> None`

---

## 📊 Scaling Metrics Service

**Location**: `src/amas/services/scaling_metrics_service.py`

### Overview

Tracks autoscaling decisions and events, including scale-up/down, reasons, triggers, and effectiveness. Integrates with Prometheus for exporting scaling metrics.

### Features

- **Event Tracking**: Records all scaling events
- **Effectiveness Metrics**: Tracks scaling success/failure
- **Prometheus Integration**: Exports metrics for monitoring
- **Historical Analysis**: Query scaling history

### Usage

```python
from amas.services import ScalingMetricsService, ScalingEvent, get_scaling_metrics_service

# Get service instance
metrics = get_scaling_metrics_service()

# Record scaling event
await metrics.record_event(
    deployment="amas-orchestrator",
    action="scale_up",
    from_replicas=2,
    to_replicas=5,
    trigger="http_rps",
    reason="HTTP RPS exceeded threshold (25 RPS > 15 RPS)",
    metadata={"rps": 25, "threshold": 15}
)

# Get scaling history
history = await metrics.get_history(
    deployment="amas-orchestrator",
    start_time="2025-11-01T00:00:00Z",
    end_time="2025-11-09T23:59:59Z"
)

# Get effectiveness metrics
effectiveness = await metrics.get_effectiveness("amas-orchestrator")
# Returns: {"success_rate": 0.95, "avg_scale_time": 45.2, ...}
```

### API Reference

- `record_event(deployment: str, action: str, from_replicas: int, to_replicas: int, trigger: str, reason: str, metadata: Optional[Dict] = None) -> None`
- `get_history(deployment: str, start_time: str, end_time: str) -> List[ScalingEvent]`
- `get_effectiveness(deployment: str) -> Dict[str, Any]`

---

## 🔗 Integration Examples

### Complete Integration Example

See [Performance Scaling Integration Guide](../PERFORMANCE_SCALING_INTEGRATION.md) for a complete example of integrating all services together in an `OptimizedAgentService`.

### Quick Integration

```python
from amas.services import (
    get_semantic_cache,
    get_circuit_breaker_service,
    get_rate_limiting_service,
    get_deduplication_service,
    get_cost_tracking_service,
    get_connection_pool_service,
)

# Initialize services
cache = get_semantic_cache()
breaker = get_circuit_breaker_service()
rate_limiter = get_rate_limiting_service()
dedup = get_deduplication_service()
cost_tracker = get_cost_tracking_service()
pool = get_connection_pool_service()

# Use in agent service
async def process_request(user_id: str, query: str):
    # Rate limiting
    limit_result = await rate_limiter.check_limit(user_id, "api_calls", 100, 60)
    if not limit_result.allowed:
        raise RateLimitExceeded()
    
    # Deduplication
    async with dedup.deduplicate(f"query_{hash(query)}") as result:
        if result.is_duplicate:
            return await result.wait()
        
        # Semantic cache
        cached = await cache.get_similar(query, threshold=0.85)
        if cached:
            return cached[0]["value"]
        
        # Circuit breaker
        async with breaker.circuit("ai_provider") as cb:
            try:
                # Use connection pool
                client = await pool.get_client("https://api.openai.com")
                response = await client.post("/v1/chat/completions", ...)
                
                # Track cost
                await cost_tracker.track_request(
                    user_id, "openai", "gpt-4",
                    input_tokens=1000, output_tokens=500
                )
                
                # Cache result
                await cache.set(f"query_{hash(query)}", response.json())
                
                cb.record_success()
                result.set_result(response.json())
                return response.json()
            except Exception as e:
                cb.record_failure()
                raise
```

---

## 📚 Related Documentation

- [Performance Scaling Guide](../PERFORMANCE_SCALING_GUIDE.md) - Complete infrastructure guide
- [Performance Scaling Integration](../PERFORMANCE_SCALING_INTEGRATION.md) - Integration examples
- [Performance Benchmarks](../performance_benchmarks.md) - Performance metrics
- [Architecture Documentation](../architecture.md) - System architecture

---

## ✅ Status

All services are **✅ Production Ready** and fully tested. See `tests/performance/test_resilience_patterns.py` for test coverage.
