"""
AMAS - Advanced Multi-Agent Intelligence System
Production-ready FastAPI application
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from src.config.settings import get_settings, validate_configuration
from src.api.routes import health, agents, tasks, users
from src.middleware.logging import LoggingMiddleware
from src.middleware.security import SecurityMiddleware
from src.middleware.monitoring import MonitoringMiddleware


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AMAS application...")
    
    # Validate configuration
    if not validate_configuration():
        logger.error("Configuration validation failed")
        raise RuntimeError("Invalid configuration")
    
    # Initialize services
    try:
        # Initialize database
        from src.database.connection import init_database
        await init_database()
        logger.info("Database initialized")
        
        # Initialize Redis
        from src.cache.redis import init_redis
        await init_redis()
        logger.info("Redis initialized")
        
        # Initialize Neo4j
        from src.graph.neo4j import init_neo4j
        await init_neo4j()
        logger.info("Neo4j initialized")
        
        # Initialize monitoring
        from src.monitoring.prometheus import init_prometheus
        init_prometheus()
        logger.info("Monitoring initialized")
        
        logger.info("AMAS application started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AMAS application...")
    
    # Cleanup services
    try:
        from src.database.connection import close_database
        await close_database()
        logger.info("Database connection closed")
        
        from src.cache.redis import close_redis
        await close_redis()
        logger.info("Redis connection closed")
        
        from src.graph.neo4j import close_neo4j
        await close_neo4j()
        logger.info("Neo4j connection closed")
        
        logger.info("AMAS application shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="AMAS - Advanced Multi-Agent Intelligence System",
    description="Production-ready AI agent management system",
    version="1.0.0",
    docs_url="/docs" if get_settings().features.enable_api_documentation else None,
    redoc_url="/redoc" if get_settings().features.enable_api_documentation else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().security.cors_origins,
    allow_credentials=get_settings().security.cors_allow_credentials,
    allow_methods=get_settings().security.cors_allow_methods,
    allow_headers=get_settings().security.cors_allow_headers,
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityMiddleware)
app.add_middleware(MonitoringMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AMAS - Advanced Multi-Agent Intelligence System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if get_settings().features.enable_api_documentation else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        from src.database.connection import is_connected as db_connected
        db_status = await db_connected()
        
        # Check Redis
        from src.cache.redis import is_connected as redis_connected
        redis_status = await redis_connected()
        
        # Check Neo4j
        from src.graph.neo4j import is_connected as neo4j_connected
        neo4j_status = await neo4j_connected()
        
        services = {
            "database": "healthy" if db_status else "unhealthy",
            "redis": "healthy" if redis_status else "unhealthy",
            "neo4j": "healthy" if neo4j_status else "neo4j_status"
        }
        
        overall_status = "healthy" if all([db_status, redis_status, neo4j_status]) else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "version": "1.0.0",
            "uptime": time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
            "services": services
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if all services are ready
        from src.database.connection import is_connected as db_connected
        from src.cache.redis import is_connected as redis_connected
        from src.graph.neo4j import is_connected as neo4j_connected
        
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
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": time.time()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.monitoring.log_level.lower()
    )