"""
Rate Limiting Service for AMAS

Provides intelligent rate limiting with user-based quotas,
sliding window algorithm, and configurable limits.
"""

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10  # Allow burst of requests
    enabled: bool = True


@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    remaining: int
    reset_time: float
    retry_after: Optional[float] = None  # Seconds to wait before retry


class RateLimitingService:
    """
    Rate limiting service with sliding window algorithm.
    
    Supports:
    - Per-user rate limits
    - Multiple time windows (minute, hour, day)
    - Burst handling
    - Redis-backed distributed rate limiting
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_config: RateLimitConfig = None
    ):
        """
        Initialize rate limiting service.
        
        Args:
            redis_url: Redis connection URL for distributed rate limiting
            default_config: Default rate limit configuration
        """
        self.redis_url = redis_url
        self.default_config = default_config or RateLimitConfig()
        
        self.redis_client: Optional[redis.Redis] = None
        self.user_configs: Dict[str, RateLimitConfig] = {}
        
        # In-memory fallback (for single-instance deployments)
        self._memory_windows: Dict[str, Dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )
    
    async def initialize(self):
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available. Using in-memory rate limiting.")
            return
        
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Rate limiting: Redis connection established")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis for rate limiting: {e}. Using in-memory.")
            self.redis_client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def set_user_config(self, user_id: str, config: RateLimitConfig):
        """Set rate limit configuration for a specific user"""
        self.user_configs[user_id] = config
    
    def get_user_config(self, user_id: str) -> RateLimitConfig:
        """Get rate limit configuration for user (or default)"""
        return self.user_configs.get(user_id, self.default_config)
    
    async def check_rate_limit(
        self,
        user_id: str,
        endpoint: str = "default"
    ) -> RateLimitResult:
        """
        Check if request is allowed under rate limits.
        
        Args:
            user_id: User identifier
            endpoint: Optional endpoint identifier for per-endpoint limits
            
        Returns:
            RateLimitResult with allowed status and remaining requests
        """
        config = self.get_user_config(user_id)
        
        if not config.enabled:
            return RateLimitResult(
                allowed=True,
                remaining=999999,
                reset_time=time.time() + 3600
            )
        
        if self.redis_client:
            return await self._check_redis_rate_limit(user_id, endpoint, config)
        else:
            return await self._check_memory_rate_limit(user_id, endpoint, config)
    
    async def _check_redis_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        config: RateLimitConfig
    ) -> RateLimitResult:
        """Check rate limit using Redis (distributed)"""
        current_time = time.time()
        key_prefix = f"ratelimit:{user_id}:{endpoint}"
        
        # Check all time windows
        windows = [
            ("minute", 60, config.requests_per_minute),
            ("hour", 3600, config.requests_per_hour),
            ("day", 86400, config.requests_per_day),
        ]
        
        allowed = True
        remaining = float('inf')
        reset_time = current_time + 60
        retry_after = None
        
        async with self.redis_client.pipeline() as pipe:
            for window_name, window_seconds, limit in windows:
                key = f"{key_prefix}:{window_name}"
                
                # Remove old entries outside window
                pipe.zremrangebyscore(key, 0, current_time - window_seconds)
                
                # Count requests in window
                pipe.zcard(key)
                
                # Add current request
                pipe.zadd(key, {str(current_time): current_time})
                
                # Set expiry
                pipe.expire(key, window_seconds)
            
            results = await pipe.execute()
            
            # Check each window
            for i, (window_name, window_seconds, limit) in enumerate(windows):
                # Results are: [zrem, zcard, zadd, expire] for each window
                # zcard is at index 1, 5, 9...
                count_index = 1 + i * 4
                count = results[count_index]
                
                if count >= limit:
                    allowed = False
                    # Calculate retry after
                    oldest_key = f"{key_prefix}:{window_name}"
                    oldest = await self.redis_client.zrange(oldest_key, 0, 0, withscores=True)
                    if oldest:
                        retry_after = oldest[0][1] + window_seconds - current_time
                    else:
                        retry_after = window_seconds
                    break
                
                remaining = min(remaining, limit - count)
                reset_time = min(reset_time, current_time + window_seconds)
        
        return RateLimitResult(
            allowed=allowed,
            remaining=int(remaining) if remaining != float('inf') else 999999,
            reset_time=reset_time,
            retry_after=retry_after
        )
    
    async def _check_memory_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        config: RateLimitConfig
    ) -> RateLimitResult:
        """Check rate limit using in-memory storage"""
        current_time = time.time()
        key = f"{user_id}:{endpoint}"
        
        windows = self._memory_windows[key]
        
        # Check all time windows
        window_configs = [
            ("minute", 60, config.requests_per_minute),
            ("hour", 3600, config.requests_per_hour),
            ("day", 86400, config.requests_per_day),
        ]
        
        allowed = True
        remaining = float('inf')
        reset_time = current_time + 60
        retry_after = None
        
        for window_name, window_seconds, limit in window_configs:
            window = windows[window_name]
            
            # Remove old entries
            window[:] = [t for t in window if current_time - t < window_seconds]
            
            # Check limit BEFORE adding current request
            # If window already has 'limit' entries, we've reached the limit
            if len(window) >= limit:
                allowed = False
                if window:
                    retry_after = window[0] + window_seconds - current_time
                else:
                    retry_after = window_seconds
                # Don't add request if limit exceeded
                remaining = 0
                # Calculate reset_time from the first window that failed
                reset_time = min(reset_time, current_time + window_seconds)
                break
            
            # Add current request only if within limit
            window.append(current_time)
            
            # Calculate remaining after adding this request
            remaining = min(remaining, limit - len(window))
            reset_time = min(reset_time, current_time + window_seconds)
        
        return RateLimitResult(
            allowed=allowed,
            remaining=int(remaining) if remaining != float('inf') else 999999,
            reset_time=reset_time,
            retry_after=retry_after
        )
    
    async def reset_user_limits(self, user_id: str):
        """Reset rate limits for a user"""
        if self.redis_client:
            pattern = f"ratelimit:{user_id}:*"
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
        else:
            # Remove from memory
            keys_to_remove = [k for k in self._memory_windows.keys() if k.startswith(f"{user_id}:")]
            for key in keys_to_remove:
                self._memory_windows.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        return {
            "redis_available": self.redis_client is not None,
            "user_configs_count": len(self.user_configs),
            "memory_windows_count": len(self._memory_windows),
            "default_config": {
                "requests_per_minute": self.default_config.requests_per_minute,
                "requests_per_hour": self.default_config.requests_per_hour,
                "requests_per_day": self.default_config.requests_per_day,
            }
        }


# Global instance
_rate_limiting_service: Optional[RateLimitingService] = None


async def get_rate_limiting_service(
    redis_url: str = "redis://localhost:6379/0",
    **kwargs
) -> RateLimitingService:
    """Get or create global rate limiting service instance"""
    global _rate_limiting_service
    
    if _rate_limiting_service is None:
        _rate_limiting_service = RateLimitingService(redis_url=redis_url, **kwargs)
        await _rate_limiting_service.initialize()
    
    return _rate_limiting_service
