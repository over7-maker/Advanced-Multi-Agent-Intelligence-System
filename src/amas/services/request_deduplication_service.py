"""
Request Deduplication Service for AMAS

Eliminates duplicate concurrent requests by tracking in-flight requests
and returning the same promise for identical requests.
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeduplicationConfig:
    """Configuration for request deduplication"""
    ttl_seconds: float = 60.0  # How long to track in-flight requests
    max_tracked: int = 10000   # Maximum number of tracked requests
    enabled: bool = True


class RequestDeduplicationService:
    """
    Service that deduplicates concurrent identical requests.
    
    When multiple identical requests arrive simultaneously, only one
    is executed and all others wait for the same result.
    """
    
    def __init__(self, config: DeduplicationConfig = None):
        """
        Initialize request deduplication service.
        
        Args:
            config: Deduplication configuration
        """
        self.config = config or DeduplicationConfig()
        
        # Track in-flight requests: key -> (future, timestamp)
        self._in_flight: Dict[str, tuple[asyncio.Future, float]] = {}
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
    
    def _generate_key(self, request_data: Any) -> str:
        """Generate deduplication key from request data"""
        # Normalize request data
        if isinstance(request_data, dict):
            # Sort keys for consistent hashing
            normalized = json.dumps(request_data, sort_keys=True)
        elif isinstance(request_data, str):
            normalized = request_data
        else:
            normalized = json.dumps(request_data, default=str, sort_keys=True)
        
        # Generate hash
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    async def deduplicate(
        self,
        request_data: Any,
        request_func: callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute request with deduplication.
        
        If an identical request is already in-flight, wait for its result.
        Otherwise, execute the request and share the result.
        
        Args:
            request_data: Data to use for deduplication key
            request_func: Async function to execute
            *args: Arguments for request_func
            **kwargs: Keyword arguments for request_func
            
        Returns:
            Result from request_func
        """
        if not self.config.enabled:
            return await request_func(*args, **kwargs)
        
        # Generate deduplication key
        key = self._generate_key(request_data)
        
        # Check if request is already in-flight
        if key in self._in_flight:
            future, _ = self._in_flight[key]
            logger.debug(f"Request deduplication: waiting for in-flight request {key[:8]}...")
            try:
                return await future
            except Exception as e:
                # If the original request failed, we still propagate the error
                raise e
        
        # Create new future for this request
        future = asyncio.create_task(request_func(*args, **kwargs))
        self._in_flight[key] = (future, time.time())
        
        # Start cleanup task if not running
        if not self._running:
            self._start_cleanup()
        
        try:
            result = await future
            return result
        except Exception as e:
            # Remove from in-flight on error
            self._in_flight.pop(key, None)
            raise e
        finally:
            # Remove from in-flight after completion
            # (with a small delay to allow other waiting requests to get the result)
            await asyncio.sleep(0.1)
            self._in_flight.pop(key, None)
    
    def _start_cleanup(self):
        """Start background cleanup task"""
        if self._running:
            return
        
        self._running = True
        
        async def cleanup_loop():
            while self._running:
                try:
                    await asyncio.sleep(5)  # Cleanup every 5 seconds
                    await self._cleanup()
                except Exception as e:
                    logger.error(f"Error in deduplication cleanup: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def _cleanup(self):
        """Clean up expired in-flight requests"""
        current_time = time.time()
        expired_keys = []
        
        for key, (future, timestamp) in self._in_flight.items():
            # Remove if expired
            if current_time - timestamp > self.config.ttl_seconds:
                expired_keys.append(key)
            # Remove if future is done (shouldn't happen, but safety check)
            elif future.done():
                expired_keys.append(key)
        
        for key in expired_keys:
            self._in_flight.pop(key, None)
        
        # If too many tracked requests, remove oldest
        if len(self._in_flight) > self.config.max_tracked:
            # Sort by timestamp and remove oldest
            sorted_items = sorted(
                self._in_flight.items(),
                key=lambda x: x[1][1]
            )
            to_remove = len(sorted_items) - self.config.max_tracked
            for key, _ in sorted_items[:to_remove]:
                self._in_flight.pop(key, None)
    
    async def shutdown(self):
        """Shutdown deduplication service"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all in-flight requests
        for key, (future, _) in list(self._in_flight.items()):
            if not future.done():
                future.cancel()
            self._in_flight.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics"""
        return {
            "in_flight_count": len(self._in_flight),
            "enabled": self.config.enabled,
            "max_tracked": self.config.max_tracked,
            "ttl_seconds": self.config.ttl_seconds
        }


# Global instance
_deduplication_service: Optional[RequestDeduplicationService] = None


def get_deduplication_service() -> RequestDeduplicationService:
    """Get global deduplication service instance"""
    global _deduplication_service
    
    if _deduplication_service is None:
        _deduplication_service = RequestDeduplicationService()
    
    return _deduplication_service
