"""
Redis cache client for database operations
Compatible with health_checker and other services
"""

import logging
from typing import Optional

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Global Redis client instance
redis_client: Optional[redis.Redis] = None


async def init_redis_cache() -> None:
    """Initialize Redis cache connection"""
    global redis_client
    
    if not REDIS_AVAILABLE:
        logger.warning("Redis library not available")
        return
    
    try:
        from src.config.settings import get_settings
        
        settings = get_settings()
        
        redis_client = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            password=settings.redis.password,
            db=settings.redis.db,
            max_connections=settings.redis.max_connections,
            decode_responses=True,
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis cache connection initialized successfully")
        
    except Exception as e:
        # Redis is optional in development - don't raise, just log
        logger.debug(f"Redis cache not available (expected in dev): {e}")
        redis_client = None


async def close_redis_cache() -> None:
    """Close Redis cache connection"""
    global redis_client
    
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis cache connection closed")


async def is_connected() -> bool:
    """Check if Redis cache is connected"""
    if not redis_client:
        return False
    
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.debug(f"Redis cache connection check failed: {e}")
        return False

