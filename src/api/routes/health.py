"""
Health check API routes
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.config.settings import get_settings
from src.database.connection import is_connected as db_connected
from src.cache.redis import is_connected as redis_connected
from src.graph.neo4j import is_connected as neo4j_connected

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint"""
    try:
        # Check all services
        db_status = await db_connected()
        redis_status = await redis_connected()
        neo4j_status = await neo4j_connected()
        
        services = {
            "database": "healthy" if db_status else "unhealthy",
            "redis": "healthy" if redis_status else "unhealthy",
            "neo4j": "healthy" if neo4j_status else "unhealthy"
        }
        
        overall_status = "healthy" if all([db_status, redis_status, neo4j_status]) else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "version": "1.0.0",
            "uptime": time.time() - time.time(),  # This would be actual uptime
            "services": services
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check endpoint"""
    try:
        db_ready = await db_connected()
        redis_ready = await redis_connected()
        neo4j_ready = await neo4j_connected()
        
        services = {
            "database": "healthy" if db_ready else "unhealthy",
            "redis": "healthy" if redis_ready else "unhealthy",
            "neo4j": "healthy" if neo4j_ready else "unhealthy"
        }
        
        overall_status = "ready" if all([db_ready, redis_ready, neo4j_ready]) else "not_ready"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "services": services
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Readiness check failed: {str(e)}")


@router.get("/health/metrics")
async def health_metrics() -> Dict[str, Any]:
    """Health metrics endpoint"""
    try:
        import psutil
        
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "active_connections": 0,  # This would be actual connection count
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics collection failed: {str(e)}")


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with system metrics"""
    try:
        import psutil
        
        # System metrics
        system = {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg()
        }
        
        # Database metrics
        database = {
            "connection_count": 0,  # This would be actual connection count
            "query_performance": "normal",
            "status": "healthy" if await db_connected() else "unhealthy"
        }
        
        # Cache metrics
        cache = {
            "hit_rate": 0.95,  # This would be actual hit rate
            "memory_usage": 0,  # This would be actual memory usage
            "status": "healthy" if await redis_connected() else "unhealthy"
        }
        
        # Graph metrics
        graph = {
            "node_count": 0,  # This would be actual node count
            "relationship_count": 0,  # This would be actual relationship count
            "status": "healthy" if await neo4j_connected() else "unhealthy"
        }
        
        return {
            "system": system,
            "database": database,
            "cache": cache,
            "graph": graph,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detailed health check failed: {str(e)}")