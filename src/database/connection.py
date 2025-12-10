"""
Database connection management
Production-ready PostgreSQL connection pool with health checks
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
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
            engine, class_=AsyncSession, expire_on_commit=False
        )

        logger.info("Database connection initialized")

    except Exception as e:
        # Database is optional in development - don't raise, just log
        logger.debug(f"Database not available (expected in dev): {e}")
        # Don't raise - allow app to continue without database


async def close_database():
    """Close database connection"""
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
            await conn.execute(text("SELECT 1"))
        return True

    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def health_check() -> Dict[str, Any]:
    """
    Comprehensive database health check (PART_4 requirement)
    
    Returns:
        Dict with health status and metrics
    """
    try:
        if not engine or not async_session:
            return {
                "status": "unhealthy",
                "error": "Database not initialized"
            }
        
        start_time = datetime.now()
        
        # Test query
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            
            # Get pool stats
            pool = engine.pool
            pool_size = pool.size()
            pool_checked_in = pool.checkedin()
            pool_checked_out = pool.checkedout()
            pool_overflow = pool.overflow()
            
            # Get database stats
            db_stats_result = await session.execute(text("""
                SELECT 
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections
                FROM pg_stat_activity
                WHERE datname = current_database()
            """))
            db_stats = db_stats_result.fetchone()
        
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "pool": {
                "size": pool_size,
                "checked_in": pool_checked_in,
                "checked_out": pool_checked_out,
                "overflow": pool_overflow,
                "max_overflow": pool._max_overflow if hasattr(pool, '_max_overflow') else 0
            },
            "database": {
                "total_connections": db_stats[0] if db_stats else 0,
                "active_connections": db_stats[1] if db_stats else 0,
                "idle_connections": db_stats[2] if db_stats else 0
            }
        }
    
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def get_table_stats() -> Dict[str, Any]:
    """
    Get statistics for all tables (PART_4 requirement)
    
    Useful for monitoring dashboard
    """
    try:
        if not engine or not async_session:
            return {"error": "Database not initialized"}
        
        async with async_session() as session:
            stats_result = await session.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    n_live_tup as row_count,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """))
            
            rows = stats_result.fetchall()
            
            tables = []
            for row in rows:
                tables.append({
                    "schema": row[0],
                    "table": row[1],
                    "size": row[2],
                    "row_count": row[3],
                    "inserts": row[4],
                    "updates": row[5],
                    "deletes": row[6],
                    "last_vacuum": row[7].isoformat() if row[7] else None,
                    "last_autovacuum": row[8].isoformat() if row[8] else None,
                    "last_analyze": row[9].isoformat() if row[9] else None,
                    "last_autoanalyze": row[10].isoformat() if row[10] else None
                })
            
            return {
                "tables": tables,
                "table_count": len(tables)
            }
    
    except Exception as e:
        logger.error(f"Failed to get table stats: {e}")
        return {"error": str(e)}
