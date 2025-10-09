"""
Redis cache implementation for AMAS
"""

import asyncio
import logging
from typing import Optional

import redis.asyncio as redis

logger = logging.getLogger(__name__)

# Global Redis connection
_redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """Initialize Redis connection"""
    global _redis_client
    
    try:
        from src.config.settings import get_settings
        
        settings = get_settings()
        
        _redis_client = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            password=settings.redis.password,
            db=settings.redis.db,
            max_connections=settings.redis.max_connections,
            decode_responses=True,
        )
        
        # Test connection
        await _redis_client.ping()
        logger.info("Redis connection initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        raise


async def close_redis() -> None:
    """Close Redis connection"""
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


async def is_connected() -> bool:
    """Check if Redis is connected"""
    global _redis_client
    
    if not _redis_client:
        return False
    
    try:
        await _redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection check failed: {e}")
        return False


def get_redis_client() -> Optional[redis.Redis]:
    """Get the Redis client instance"""
    return _redis_client


async def get(key: str) -> Optional[str]:
    """Get value from Redis"""
    if not _redis_client:
        return None
    
    try:
        return await _redis_client.get(key)
    except Exception as e:
        logger.error(f"Failed to get key {key}: {e}")
        return None


async def set(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """Set value in Redis"""
    if not _redis_client:
        return False
    
    try:
        if ttl:
            await _redis_client.setex(key, ttl, value)
        else:
            await _redis_client.set(key, value)
        return True
    except Exception as e:
        logger.error(f"Failed to set key {key}: {e}")
        return False


async def delete(key: str) -> bool:
    """Delete key from Redis"""
    if not _redis_client:
        return False
    
    try:
        await _redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Failed to delete key {key}: {e}")
        return False


async def exists(key: str) -> bool:
    """Check if key exists in Redis"""
    if not _redis_client:
        return False
    
    try:
        result = await _redis_client.exists(key)
        return bool(result)
    except Exception as e:
        logger.error(f"Failed to check key {key}: {e}")
        return False