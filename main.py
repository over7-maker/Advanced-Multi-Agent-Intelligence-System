"""
AMAS - Advanced Multi-Agent Intelligence System
Production-ready FastAPI application
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from src.api.routes import agents, health, tasks, users, auth
from src.config.settings import get_settings, validate_configuration
from src.middleware.logging import LoggingMiddleware
from src.middleware.monitoring import MonitoringMiddleware
from src.middleware.security import SecurityMiddleware
from src.middleware.rate_limiting import RateLimitingMiddleware, RequestSizeLimitingMiddleware
from src.amas.security.security_manager import initialize_security
from src.amas.security.middleware import AuditLoggingMiddleware, AuthenticationMiddleware
from src.amas.security.auth.jwt_middleware import SecurityHeadersMiddleware
from src.amas.errors.error_handling import (
    handle_amas_exception,
    handle_http_exception,
    handle_general_exception
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
        # Initialize security layer first (before other services)
        try:
            security_manager = await initialize_security()
            logger.info("Security layer initialized")
        except Exception as e:
            logger.warning(f"Security initialization failed (may be expected in dev): {e}")
            # Don't fail startup if security config is missing (for development)

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
        # Shutdown audit logger
        try:
            from src.amas.security.audit.audit_logger import get_audit_logger
            audit_logger = get_audit_logger()
            await audit_logger.shutdown()
            logger.info("Audit logger shutdown complete")
        except Exception as e:
            logger.warning(f"Error shutting down audit logger: {e}")

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
    lifespan=lifespan,
)

# Add middleware (order matters - first added is outermost)
# Security headers middleware (innermost - applied last)
try:
    from src.amas.security.auth.jwt_middleware import SecurityHeadersMiddleware
    security_headers_mw = SecurityHeadersMiddleware()
    # Note: SecurityHeadersMiddleware is not a FastAPI middleware, 
    # it's applied via dependency injection in routes
except Exception as e:
    logger.warning(f"Could not initialize security headers: {e}")

# Standard middleware stack
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(SecurityMiddleware)  # Existing security middleware
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(RequestSizeLimitingMiddleware, max_size=10 * 1024 * 1024)  # 10MB
app.add_middleware(AuthenticationMiddleware)  # JWT authentication check
app.add_middleware(AuditLoggingMiddleware)  # Audit trail logging
app.add_middleware(LoggingMiddleware)
app.add_middleware(MonitoringMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().security.cors_origins,
    allow_credentials=get_settings().security.cors_allow_credentials,
    allow_methods=get_settings().security.cors_allow_methods,
    allow_headers=get_settings().security.cors_allow_headers,
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
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
        "docs": "/docs" if get_settings().features.enable_api_documentation else None,
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        from src.amas.services.prometheus_metrics_service import get_metrics_service
        from src.amas.services.structured_logging_service import get_logger
        
        health_logger = get_logger("amas.health", "health")
        metrics_service = get_metrics_service()
        
        # Initialize health status
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "uptime": time.time() - getattr(app.state, "start_time", time.time()),
            "services": {},
            "metrics": {},
            "checks": []
        }
        
        # Check database
        try:
            from src.database.connection import is_connected as db_connected
            db_status = await db_connected()
            health_status["services"]["database"] = "healthy" if db_status else "unhealthy"
            health_status["checks"].append({
                "name": "database",
                "status": "pass" if db_status else "fail",
                "message": "Database connection successful" if db_status else "Database connection failed"
            })
        except Exception as e:
            health_status["services"]["database"] = "unhealthy"
            health_status["checks"].append({
                "name": "database",
                "status": "fail",
                "message": f"Database check error: {str(e)}"
            })
            health_logger.error(f"Database health check failed: {e}")

        # Check Redis
        try:
            from src.cache.redis import is_connected as redis_connected
            redis_status = await redis_connected()
            health_status["services"]["redis"] = "healthy" if redis_status else "unhealthy"
            health_status["checks"].append({
                "name": "redis",
                "status": "pass" if redis_status else "fail",
                "message": "Redis connection successful" if redis_status else "Redis connection failed"
            })
        except Exception as e:
            health_status["services"]["redis"] = "unhealthy"
            health_status["checks"].append({
                "name": "redis",
                "status": "fail",
                "message": f"Redis check error: {str(e)}"
            })
            health_logger.error(f"Redis health check failed: {e}")

        # Check Neo4j
        try:
            from src.graph.neo4j import is_connected as neo4j_connected
            neo4j_status = await neo4j_connected()
            health_status["services"]["neo4j"] = "healthy" if neo4j_status else "unhealthy"
            health_status["checks"].append({
                "name": "neo4j",
                "status": "pass" if neo4j_status else "fail",
                "message": "Neo4j connection successful" if neo4j_status else "Neo4j connection failed"
            })
        except Exception as e:
            health_status["services"]["neo4j"] = "unhealthy"
            health_status["checks"].append({
                "name": "neo4j",
                "status": "fail",
                "message": f"Neo4j check error: {str(e)}"
            })
            health_logger.error(f"Neo4j health check failed: {e}")

        # Check system resources
        try:
            import psutil
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            health_status["metrics"]["memory_usage_percent"] = memory.percent
            health_status["metrics"]["cpu_usage_percent"] = cpu_percent
            health_status["metrics"]["memory_available_gb"] = memory.available / (1024**3)
            
            # Check if system resources are healthy
            memory_healthy = memory.percent < 90
            cpu_healthy = cpu_percent < 90
            
            health_status["checks"].append({
                "name": "memory",
                "status": "pass" if memory_healthy else "warn",
                "message": f"Memory usage: {memory.percent:.1f}%"
            })
            
            health_status["checks"].append({
                "name": "cpu",
                "status": "pass" if cpu_healthy else "warn",
                "message": f"CPU usage: {cpu_percent:.1f}%"
            })
            
        except ImportError:
            health_status["checks"].append({
                "name": "system_resources",
                "status": "skip",
                "message": "psutil not available for system metrics"
            })

        # Check authentication service
        try:
            from src.amas.security.enhanced_auth import get_auth_manager
            auth_manager = get_auth_manager()
            health_status["services"]["authentication"] = "healthy"
            health_status["checks"].append({
                "name": "authentication",
                "status": "pass",
                "message": "Authentication service is running"
            })
        except Exception as e:
            health_status["services"]["authentication"] = "unhealthy"
            health_status["checks"].append({
                "name": "authentication",
                "status": "fail",
                "message": f"Authentication service error: {str(e)}"
            })

        # Determine overall status
        service_statuses = list(health_status["services"].values())
        overall_healthy = all(status == "healthy" for status in service_statuses)
        health_status["status"] = "healthy" if overall_healthy else "unhealthy"
        
        # Record health check metrics
        metrics_service.record_http_request(
            method="GET",
            endpoint="/health",
            status_code=200 if overall_healthy else 503,
            duration=0.1  # Placeholder duration
        )

        # Log health check
        health_logger.info(
            f"Health check completed: {health_status['status']}",
            action="health_check",
            metadata=health_status
        )

        status_code = 200 if overall_healthy else 503
        return JSONResponse(
            status_code=status_code,
            content=health_status
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e),
                "message": "Health check system failure"
            },
        )


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if all services are ready
        from src.cache.redis import is_connected as redis_connected
        from src.database.connection import is_connected as db_connected
        from src.graph.neo4j import is_connected as neo4j_connected

        db_ready = await db_connected()
        redis_ready = await redis_connected()
        neo4j_ready = await neo4j_connected()

        services = {
            "database": "healthy" if db_ready else "unhealthy",
            "redis": "healthy" if redis_ready else "unhealthy",
            "neo4j": "healthy" if neo4j_ready else "unhealthy",
        }

        overall_status = (
            "ready" if all([db_ready, redis_ready, neo4j_ready]) else "not_ready"
        )

        return {
            "status": overall_status,
            "timestamp": time.time(),
            "services": services,
        }

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "timestamp": time.time(), "error": str(e)},
        )


# Add exception handlers
app.add_exception_handler(Exception, handle_general_exception)
app.add_exception_handler(HTTPException, handle_http_exception)


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.monitoring.log_level.lower(),
    )
