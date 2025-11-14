# Performance Scaling Infrastructure Integration Guide

This guide shows how to integrate all performance scaling components together.

## Quick Start

```python
import asyncio
from src.amas.services.semantic_cache_service import get_semantic_cache
from src.amas.services.circuit_breaker_service import get_circuit_breaker_service
from src.amas.services.rate_limiting_service import get_rate_limiting_service
from src.amas.services.request_deduplication_service import get_deduplication_service
from src.amas.services.cost_tracking_service import get_cost_tracking_service
from src.amas.services.connection_pool_service import get_connection_pool_service

async def main():
    # Initialize all services
    semantic_cache = await get_semantic_cache()
    circuit_breaker = get_circuit_breaker_service()
    rate_limiter = await get_rate_limiting_service()
    deduplication = get_deduplication_service()
    cost_tracker = await get_cost_tracking_service()
    connection_pool = get_connection_pool_service()
    
    # Use in your agent calls
    async def agent_call(query: str, user_id: str):
        # 1. Check rate limits
        rate_limit = await rate_limiter.check_rate_limit(user_id)
        if not rate_limit.allowed:
            raise Exception(f"Rate limit exceeded. Retry after {rate_limit.retry_after}s")
        
        # 2. Check semantic cache
        cached = await semantic_cache.get(query, agent_id="research_agent")
        if cached:
            return cached
        
        # 3. Use deduplication for expensive operations
        async def expensive_operation():
            # 4. Use circuit breaker for external calls
            breaker = circuit_breaker.get_breaker("external_api")
            client = connection_pool.get_client()
            
            async def api_call():
                response = await client.post("/api/agent", json={"query": query})
                return response.json()
            
            result = await breaker.call(api_call)
            
            # 5. Track costs
            await cost_tracker.record_request(
                request_id="req_123",
                provider="openai",
                model="gpt-4",
                tokens_input=100,
                tokens_output=200,
                latency_ms=1500,
                success=True
            )
            
            # 6. Cache result
            await semantic_cache.set(query, result, agent_id="research_agent")
            
            return result
        
        return await deduplication.deduplicate(
            {"query": query, "user": user_id},
            expensive_operation
        )
    
    # Use the integrated agent call
    result = await agent_call("What is AI?", "user123")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Component Integration

### 1. Semantic Caching

```python
from src.amas.services.semantic_cache_service import get_semantic_cache

cache = await get_semantic_cache(
    redis_url="redis://localhost:6379/0",
    similarity_threshold=0.85
)

# Cache agent response
await cache.set("What is machine learning?", {"answer": "..."}, agent_id="research")

# Get cached response (exact match)
result = await cache.get("What is machine learning?", agent_id="research")

# Get semantically similar response
result = await cache.get("Tell me about ML", agent_id="research", use_semantic=True)
```

### 2. Circuit Breakers

```python
from src.amas.services.circuit_breaker_service import get_circuit_breaker_service

breaker_service = get_circuit_breaker_service()

# Get or create breaker
breaker = breaker_service.get_breaker("external_api")

# Use in API calls
try:
    result = await breaker.call(external_api_function, arg1, arg2)
except CircuitBreakerOpenException:
    # Circuit is open, use fallback
    result = fallback_function()
```

### 3. Rate Limiting

```python
from src.amas.services.rate_limiting_service import get_rate_limiting_service

rate_limiter = await get_rate_limiting_service()

# Check rate limit before processing
result = await rate_limiter.check_rate_limit(user_id="user123", endpoint="api/agent")

if not result.allowed:
    return {"error": "Rate limit exceeded", "retry_after": result.retry_after}

# Process request
...
```

### 4. Request Deduplication

```python
from src.amas.services.request_deduplication_service import get_deduplication_service

dedup = get_deduplication_service()

# Deduplicate expensive operations
async def expensive_llm_call(query):
    # Expensive API call
    return await llm_api.call(query)

# Multiple identical requests will share the same result
result = await dedup.deduplicate(
    {"query": "What is AI?"},
    expensive_llm_call
)
```

### 5. Cost Tracking

```python
from src.amas.services.cost_tracking_service import get_cost_tracking_service

cost_tracker = await get_cost_tracking_service(daily_budget_usd=100.0)

# Track request costs
await cost_tracker.record_request(
    request_id="req_123",
    provider="openai",
    model="gpt-4",
    tokens_input=1000,
    tokens_output=500,
    latency_ms=2000,
    success=True
)

# Get optimization recommendations
recommendations = await cost_tracker.get_optimization_recommendations()
for rec in recommendations:
    print(f"{rec['priority']}: {rec['message']}")
```

### 6. Connection Pooling

```python
from src.amas.services.connection_pool_service import get_connection_pool_service

pool = get_connection_pool_service(
    max_connections=100,
    max_keepalive_connections=20
)

# Get optimized client
client = pool.get_client(base_url="https://api.example.com")

# Use client (connections are pooled and reused)
response = await client.get("/endpoint")
```

## Complete Integration Example

```python
"""
Complete integration example showing all components working together
"""

import asyncio
import uuid
from src.amas.services import (
    get_semantic_cache,
    get_circuit_breaker_service,
    get_rate_limiting_service,
    get_deduplication_service,
    get_cost_tracking_service,
    get_connection_pool_service
)

class OptimizedAgentService:
    """Agent service with all performance optimizations"""
    
    def __init__(self):
        self.cache = None
        self.breaker_service = None
        self.rate_limiter = None
        self.dedup = None
        self.cost_tracker = None
        self.connection_pool = None
    
    async def initialize(self):
        """Initialize all services"""
        self.cache = await get_semantic_cache()
        self.breaker_service = get_circuit_breaker_service()
        self.rate_limiter = await get_rate_limiting_service()
        self.dedup = get_deduplication_service()
        self.cost_tracker = await get_cost_tracking_service()
        self.connection_pool = get_connection_pool_service()
    
    async def process_request(self, query: str, user_id: str, agent_id: str = "default"):
        """Process request with all optimizations"""
        request_id = str(uuid.uuid4())
        
        # 1. Rate limiting
        rate_limit = await self.rate_limiter.check_rate_limit(user_id, endpoint=agent_id)
        if not rate_limit.allowed:
            return {
                "error": "rate_limit_exceeded",
                "retry_after": rate_limit.retry_after
            }
        
        # 2. Semantic cache check
        cached = await self.cache.get(query, agent_id=agent_id, use_semantic=True)
        if cached:
            return {
                "result": cached,
                "cached": True,
                "request_id": request_id
            }
        
        # 3. Deduplicate expensive operations
        async def execute_agent():
            # 4. Circuit breaker protection
            breaker = self.breaker_service.get_breaker("agent_api")
            client = self.connection_pool.get_client()
            
            start_time = asyncio.get_event_loop().time()
            
            try:
                async def api_call():
                    # Simulate agent API call
                    response = await client.post(
                        f"/api/agents/{agent_id}",
                        json={"query": query}
                    )
                    return response.json()
                
                result = await breaker.call(api_call)
                
                # 5. Track costs
                latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                await self.cost_tracker.record_request(
                    request_id=request_id,
                    provider="openai",
                    model="gpt-4",
                    tokens_input=len(query.split()) * 1.3,  # Approximate
                    tokens_output=len(str(result).split()) * 1.3,
                    latency_ms=latency_ms,
                    success=True
                )
                
                # 6. Cache result
                await self.cache.set(query, result, agent_id=agent_id)
                
                return result
                
            except Exception as e:
                # Track failed request
                latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                await self.cost_tracker.record_request(
                    request_id=request_id,
                    provider="openai",
                    model="gpt-4",
                    tokens_input=0,
                    tokens_output=0,
                    latency_ms=latency_ms,
                    success=False
                )
                raise
        
        result = await self.dedup.deduplicate(
            {"query": query, "user": user_id, "agent": agent_id},
            execute_agent
        )
        
        return {
            "result": result,
            "cached": False,
            "request_id": request_id
        }
    
    async def shutdown(self):
        """Shutdown all services"""
        if self.cache:
            await self.cache.close()
        if self.rate_limiter:
            await self.rate_limiter.close()
        if self.cost_tracker:
            await self.cost_tracker.close()
        if self.connection_pool:
            await self.connection_pool.close_all()
        if self.dedup:
            await self.dedup.shutdown()


# Usage
async def main():
    service = OptimizedAgentService()
    await service.initialize()
    
    try:
        result = await service.process_request(
            query="What is artificial intelligence?",
            user_id="user123",
            agent_id="research_agent"
        )
        print(result)
    finally:
        await service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

All services can be configured via environment variables or configuration files:

```python
# Environment variables
REDIS_URL=redis://localhost:6379/0
SEMANTIC_CACHE_SIMILARITY_THRESHOLD=0.85
RATE_LIMIT_REQUESTS_PER_MINUTE=60
COST_TRACKING_DAILY_BUDGET_USD=100.0
CONNECTION_POOL_MAX_CONNECTIONS=100
```

## Monitoring

All services expose statistics:

```python
# Get stats from all services
cache_stats = cache.get_stats()
breaker_stats = breaker_service.get_all_stats()
rate_limit_stats = rate_limiter.get_stats()
cost_stats = cost_tracker.get_stats()
pool_stats = connection_pool.get_stats()
```

## Best Practices

1. **Always check rate limits first** - Fail fast before expensive operations
2. **Use semantic cache** - Check cache before making API calls
3. **Enable deduplication** - For expensive operations that might be called concurrently
4. **Protect external calls** - Use circuit breakers for all external API calls
5. **Track costs** - Monitor and optimize costs continuously
6. **Reuse connections** - Use connection pooling for HTTP clients
