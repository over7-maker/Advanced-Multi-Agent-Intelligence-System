"""
Rate limiting middleware for AMAS
Implements token bucket algorithm for API rate limiting
"""

import asyncio
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, field

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.settings import get_settings


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    window_size: int = 60  # seconds


@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""
    capacity: int
    tokens: float = field(default_factory=lambda: 0)
    last_refill: float = field(default_factory=time.time)
    
    def refill(self, rate: float) -> None:
        """Refill tokens based on rate"""
        now = time.time()
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket"""
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


@dataclass
class ClientRateLimit:
    """Client rate limit tracking"""
    per_minute: TokenBucket
    per_hour: TokenBucket
    burst: TokenBucket
    requests: deque = field(default_factory=lambda: deque())
    
    def __init__(self, config: RateLimitConfig):
        self.per_minute = TokenBucket(config.requests_per_minute)
        self.per_hour = TokenBucket(config.requests_per_hour)
        self.burst = TokenBucket(config.burst_limit)
        self.requests = deque()


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using token bucket algorithm"""

    def __init__(self, app, config: Optional[RateLimitConfig] = None):
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self.clients: Dict[str, ClientRateLimit] = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Use IP address as primary identifier
        client_ip = request.client.host if request.client else "unknown"
        
        # Add user agent hash for additional uniqueness
        user_agent = request.headers.get("user-agent", "")
        user_agent_hash = hash(user_agent) % 1000
        
        return f"{client_ip}:{user_agent_hash}"

    def _cleanup_old_clients(self):
        """Clean up old client data to prevent memory leaks"""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return

        # Remove clients with no recent activity (older than 1 hour)
        cutoff_time = now - 3600
        clients_to_remove = []
        
        for client_id, client in self.clients.items():
            if not client.requests or client.requests[-1] < cutoff_time:
                clients_to_remove.append(client_id)
        
        for client_id in clients_to_remove:
            del self.clients[client_id]
        
        self.last_cleanup = now

    def _check_rate_limit(self, client_id: str) -> Tuple[bool, Dict[str, any]]:
        """Check if client is within rate limits"""
        now = time.time()
        
        # Get or create client rate limit
        if client_id not in self.clients:
            self.clients[client_id] = ClientRateLimit(self.config)
        
        client = self.clients[client_id]
        
        # Clean up old requests
        cutoff_time = now - 60  # Remove requests older than 1 minute
        while client.requests and client.requests[0] < cutoff_time:
            client.requests.popleft()
        
        # Add current request
        client.requests.append(now)
        
        # Refill token buckets
        client.per_minute.refill(self.config.requests_per_minute / 60)
        client.per_hour.refill(self.config.requests_per_hour / 3600)
        client.burst.refill(self.config.burst_limit / 60)
        
        # Check limits
        limits_exceeded = []
        
        # Check per-minute limit
        if not client.per_minute.consume():
            limits_exceeded.append("per_minute")
        
        # Check per-hour limit
        if not client.per_hour.consume():
            limits_exceeded.append("per_hour")
        
        # Check burst limit
        if not client.burst.consume():
            limits_exceeded.append("burst")
        
        # Check request count in current minute
        current_minute_requests = sum(1 for req_time in client.requests if now - req_time < 60)
        if current_minute_requests > self.config.requests_per_minute:
            limits_exceeded.append("per_minute_count")
        
        # Check request count in current hour
        current_hour_requests = sum(1 for req_time in client.requests if now - req_time < 3600)
        if current_hour_requests > self.config.requests_per_hour:
            limits_exceeded.append("per_hour_count")
        
        is_allowed = len(limits_exceeded) == 0
        
        # Prepare rate limit headers
        headers = {
            "X-RateLimit-Limit-Minute": str(self.config.requests_per_minute),
            "X-RateLimit-Limit-Hour": str(self.config.requests_per_hour),
            "X-RateLimit-Limit-Burst": str(self.config.burst_limit),
            "X-RateLimit-Remaining-Minute": str(int(client.per_minute.tokens)),
            "X-RateLimit-Remaining-Hour": str(int(client.per_hour.tokens)),
            "X-RateLimit-Remaining-Burst": str(int(client.burst.tokens)),
            "X-RateLimit-Reset-Minute": str(int(now + 60)),
            "X-RateLimit-Reset-Hour": str(int(now + 3600)),
        }
        
        return is_allowed, headers

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/ready", "/metrics", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Clean up old clients periodically
        self._cleanup_old_clients()
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limits
        is_allowed, headers = self._check_rate_limit(client_id)
        
        if not is_allowed:
            # Determine which limit was exceeded
            if "per_minute" in headers.get("X-RateLimit-Exceeded", []):
                retry_after = 60
                detail = "Rate limit exceeded: too many requests per minute"
            elif "per_hour" in headers.get("X-RateLimit-Exceeded", []):
                retry_after = 3600
                detail = "Rate limit exceeded: too many requests per hour"
            elif "burst" in headers.get("X-RateLimit-Exceeded", []):
                retry_after = 60
                detail = "Rate limit exceeded: burst limit exceeded"
            else:
                retry_after = 60
                detail = "Rate limit exceeded"
            
            headers["Retry-After"] = str(retry_after)
            
            raise HTTPException(
                status_code=429,
                detail=detail,
                headers=headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


class RequestSizeLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size"""

    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        """Check request size before processing"""
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Request body too large. Maximum size: {self.max_size} bytes"
                    )
            except ValueError:
                # Invalid content-length header, let it through
                pass
        
        return await call_next(request)


def create_rate_limiting_middleware(config: Optional[RateLimitConfig] = None):
    """Create rate limiting middleware with configuration"""
    return RateLimitingMiddleware, config or RateLimitConfig()


def create_request_size_limiting_middleware(max_size: int = 10 * 1024 * 1024):
    """Create request size limiting middleware"""
    return RequestSizeLimitingMiddleware, {"max_size": max_size}