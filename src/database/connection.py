"""
Database connection management
"""

import asyncio
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# Database setup
Base = declarative_base()
engine: Optional[create_async_engine] = None
async_session: Optional[async_sessionmaker[AsyncSession]] = None


async def init_database():
    """Initialize database connection"""
    global engine, async_session
    
    try:
        settings = get_settings()
        
        # Create async engine
        engine = create_async_engine(
            settings.database.url,
            echo=settings.database.echo,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
        )
        
        # Create session maker
        async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("Database connection initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_database():
    """Close database connection"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


async def get_session() -> AsyncSession:
    """Get database session"""
    if not async_session:
        raise RuntimeError("Database not initialized")
    
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def is_connected() -> bool:
    """Check if database is connected"""
    try:
        if not engine:
            return False
        
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
        
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False