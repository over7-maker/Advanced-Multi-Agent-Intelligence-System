"""
Neo4j graph database management
"""

import logging
from typing import Optional

from neo4j import AsyncDriver, AsyncGraphDatabase

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# Neo4j connection
neo4j_driver: Optional[AsyncDriver] = None


async def init_neo4j():
    """Initialize Neo4j connection"""
    global neo4j_driver

    try:
        settings = get_settings()

        # Create Neo4j driver
        neo4j_driver = AsyncGraphDatabase.driver(
            settings.neo4j.uri,
            auth=(settings.neo4j.user, settings.neo4j.password),
            max_connection_lifetime=3600,
            max_connection_pool_size=settings.neo4j.max_connections,
        )

        # Test connection
        async with neo4j_driver.session() as session:
            await session.run("RETURN 1")

        logger.info("Neo4j connection initialized")

    except Exception as e:
        # Neo4j is optional in development - don't raise, just log
        logger.debug(f"Neo4j not available (expected in dev): {e}")
        # Don't raise - allow app to continue without Neo4j


async def close_neo4j():
    """Close Neo4j connection"""
    if neo4j_driver:
        await neo4j_driver.close()
        logger.info("Neo4j connection closed")


async def is_connected() -> bool:
    """Check if Neo4j is connected"""
    try:
        if not neo4j_driver:
            return False

        async with neo4j_driver.session() as session:
            await session.run("RETURN 1")
        return True

    except Exception as e:
        logger.debug(f"Neo4j connection check failed (expected in dev): {e}")
        return False


async def get_driver() -> AsyncDriver:
    """Get Neo4j driver"""
    if not neo4j_driver:
        raise RuntimeError("Neo4j not initialized")

    return neo4j_driver
