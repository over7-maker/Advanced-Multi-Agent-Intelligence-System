"""
Neo4j graph database management
"""

import asyncio
import logging
from typing import Optional

from neo4j import AsyncDriver, AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# Neo4j connection
neo4j_driver: Optional[AsyncDriver] = None

# Retry configuration
MAX_RETRIES = 3
INITIAL_DELAY = 3  # seconds
MAX_DELAY = 30  # seconds


async def init_neo4j():
    """Initialize Neo4j connection with retry logic and exponential backoff"""
    global neo4j_driver

    settings = get_settings()

    # Strip whitespace from URI, user, and password
    uri = settings.neo4j.uri.strip()
    user = settings.neo4j.user.strip() if settings.neo4j.user else "neo4j"
    password = settings.neo4j.password.strip() if settings.neo4j.password else ""

    # Wait a bit before first connection attempt to avoid rate limiting
    # This helps if Neo4j was just restarted or if there were previous failed attempts
    await asyncio.sleep(INITIAL_DELAY)

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Close existing driver if any
            if neo4j_driver:
                try:
                    await neo4j_driver.close()
                except Exception:
                    pass
                neo4j_driver = None

            logger.info(f"Attempting to connect to Neo4j (attempt {attempt}/{MAX_RETRIES})...")

            # Create Neo4j driver
            neo4j_driver = AsyncGraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_lifetime=3600,
                max_connection_pool_size=settings.neo4j.max_connections,
            )

            # Test connection with timeout
            async with neo4j_driver.session() as session:
                await asyncio.wait_for(
                    session.run("RETURN 1"),
                    timeout=10.0
                )

            logger.info("Neo4j connection initialized successfully")
            return

        except (ServiceUnavailable, AuthError) as e:
            last_error = e
            error_code = getattr(e, 'code', '')
            error_message = str(e)
            
            # Check if it's a rate limit error
            if 'AuthenticationRateLimit' in error_message or 'rate limit' in error_message.lower():
                if attempt < MAX_RETRIES:
                    # Exponential backoff: 3s, 6s, 12s
                    delay = min(INITIAL_DELAY * (2 ** (attempt - 1)), MAX_DELAY)
                    logger.warning(
                        f"Neo4j authentication rate limit hit. "
                        f"Waiting {delay}s before retry (attempt {attempt}/{MAX_RETRIES})..."
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(
                        f"Neo4j authentication rate limit persists after {MAX_RETRIES} attempts. "
                        f"Please restart Neo4j container or wait a few minutes."
                    )
            else:
                # Other auth errors - don't retry
                logger.warning(f"Neo4j authentication failed: {error_message}")
                break

        except asyncio.TimeoutError:
            last_error = Exception("Connection timeout")
            if attempt < MAX_RETRIES:
                delay = min(INITIAL_DELAY * (2 ** (attempt - 1)), MAX_DELAY)
                logger.warning(
                    f"Neo4j connection timeout. "
                    f"Retrying in {delay}s (attempt {attempt}/{MAX_RETRIES})..."
                )
                await asyncio.sleep(delay)
                continue

        except Exception as e:
            last_error = e
            error_message = str(e)
            logger.warning(f"Neo4j connection attempt {attempt} failed: {error_message}")
            
            if attempt < MAX_RETRIES:
                delay = min(INITIAL_DELAY * (2 ** (attempt - 1)), MAX_DELAY)
                logger.info(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)
                continue
            else:
                break

    # All retries failed
    logger.warning(
        f"Neo4j initialization failed after {MAX_RETRIES} attempts: {last_error}"
    )
    logger.warning(f"Neo4j URI was: {uri}")
    logger.warning(
        "Neo4j is optional - application will continue without it. "
        "To fix: restart Neo4j container or check credentials."
    )
    
    # Clean up failed driver
    if neo4j_driver:
        try:
            await neo4j_driver.close()
        except Exception:
            pass
        neo4j_driver = None
    
    # Don't raise - allow app to continue without Neo4j


async def close_neo4j():
    """Close Neo4j connection"""
    global neo4j_driver
    if neo4j_driver:
        try:
            await neo4j_driver.close()
            logger.info("Neo4j connection closed")
        except Exception as e:
            logger.debug(f"Error closing Neo4j connection (non-critical): {e}")
        finally:
            neo4j_driver = None


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


def get_driver() -> AsyncDriver:
    """Get Neo4j driver"""
    if not neo4j_driver:
        raise RuntimeError("Neo4j not initialized")

    return neo4j_driver
