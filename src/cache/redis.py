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
        import os
        from src.config.settings import get_settings

        settings = get_settings()

        # Check password from env var first, then settings
        env_password = os.getenv("REDIS_PASSWORD")
        password = env_password or settings.redis.password
        redis_url = settings.redis.url
        
        logger.debug(f"Initial Redis URL from settings: {redis_url}")
        logger.debug(f"Password available: {'Yes' if password else 'No'} (env: {'Yes' if env_password else 'No'}, settings: {'Yes' if settings.redis.password else 'No'})")
        
        # If URL doesn't contain password but password is set, construct URL with password
        if redis_url and redis_url.startswith("redis://"):
            # Check if URL already has password (format: redis://:password@host:port/db)
            url_parts = redis_url.split("://", 1)
            if len(url_parts) == 2:
                after_protocol = url_parts[1]
                url_has_password = "@" in after_protocol and ":" in after_protocol.split("@")[0]
            else:
                url_has_password = False
            
            logger.debug(f"URL has password: {url_has_password}")
            
            if not url_has_password and password:
                # Construct URL with password: redis://:password@host:port/db
                try:
                    # Parse existing URL
                    # Format: redis://host:port/db or redis://host:port
                    url_without_protocol = redis_url.replace("redis://", "")
                    
                    # Split by / to get host:port and db
                    if "/" in url_without_protocol:
                        parts = url_without_protocol.split("/", 1)
                        host_port = parts[0]  # host:port
                        db_part = parts[1] if len(parts) > 1 else "0"
                    else:
                        host_port = url_without_protocol
                        db_part = "0"
                    
                    # Construct new URL with password
                    redis_url = f"redis://:{password}@{host_port}/{db_part}"
                    logger.info(f"Added password to Redis URL: redis://:***@{host_port}/{db_part}")
                except Exception as e:
                    logger.warning(f"Failed to construct URL with password: {e}")

        # Try to use URL first (supports password in URL)
        if redis_url and redis_url.startswith("redis://"):
            try:
                _redis_client = redis.from_url(
                    redis_url,
                    max_connections=settings.redis.max_connections,
                    decode_responses=True,
                )
                # Test connection
                await _redis_client.ping()
                logger.info("Redis connection initialized successfully from URL")
                return
            except Exception as url_err:
                logger.warning(f"Failed to connect using URL ({url_err}), trying individual settings")

        # Fallback to individual settings
        # Extract password from URL if not already set
        if not password and redis_url and "@" in redis_url:
            # Try to extract password from URL: redis://:password@host:port/db
            try:
                url_parts = redis_url.split("@")[0].split("://")
                if len(url_parts) == 2 and ":" in url_parts[1]:
                    password = url_parts[1].split(":")[1]
                    logger.debug(f"Extracted password from URL")
            except Exception as e:
                logger.debug(f"Failed to extract password from URL: {e}")
        
        # Final fallback: check REDIS_PASSWORD env var if still no password
        if not password:
            password = os.getenv("REDIS_PASSWORD")
            if password:
                logger.debug(f"Using password from REDIS_PASSWORD env var")

        _redis_client = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            password=password,
            db=settings.redis.db,
            max_connections=settings.redis.max_connections,
            decode_responses=True,
        )

        # Test connection
        await _redis_client.ping()
        logger.info("Redis connection initialized successfully")

    except Exception as e:
        # Redis is optional in development - don't raise, just log
        logger.warning(f"Redis initialization failed: {e}")
        if 'settings' in locals():
            logger.warning(f"Redis URL was: {settings.redis.url}")
            logger.warning(f"Redis password was: {'***' if (password or (settings.redis.password if 'settings' in locals() else None)) else 'None'}")
        else:
            logger.warning(f"Redis URL was: N/A")
        # Don't raise - allow app to continue without Redis


async def close_redis() -> None:
    """Close Redis connection"""
    global _redis_client

    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


async def is_connected() -> bool:
    """Check if Redis is connected"""
    if not _redis_client:
        return False

    try:
        await _redis_client.ping()
        return True
    except Exception as e:
        logger.debug(f"Redis connection check failed (expected in dev): {e}")
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
