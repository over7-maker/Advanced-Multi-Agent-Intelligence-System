"""
AMAS - Advanced Multi-Agent Intelligence System
Production-ready FastAPI application
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.amas.errors.error_handling import (
    handle_general_exception,
    handle_http_exception,
)
from src.amas.security.auth.jwt_middleware import SecurityHeadersMiddleware
from src.amas.security.middleware import (
    AuditLoggingMiddleware,
    AuthenticationMiddleware,
)
from src.amas.security.security_manager import initialize_security
from src.api.routes import agents, analytics, auth, health, integrations, metrics, predictions, system, tasks, users, workflows
from src.api.websocket import start_websocket_heartbeat, websocket_endpoint
from src.config.settings import get_settings, validate_configuration
from src.middleware.logging import LoggingMiddleware
from src.middleware.monitoring import MonitoringMiddleware
from src.middleware.rate_limiting import (
    RateLimitingMiddleware,
    RequestSizeLimitingMiddleware,
)
from src.middleware.security import SecurityMiddleware

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

        # Initialize database (optional)
        try:
            from src.database.connection import init_database
            await init_database()
            logger.info("Database initialized")
        except Exception as e:
            logger.debug(f"Database not available (expected in dev): {e}")
            # Database is optional - continue without it

        # Initialize Redis (optional)
        try:
            from src.cache.redis import init_redis
            await init_redis()
            logger.info("Redis initialized")
        except Exception as e:
            logger.debug(f"Redis not available (expected in dev): {e}")
            # Redis is optional - continue without it

        # Initialize Neo4j (optional)
        try:
            from src.graph.neo4j import init_neo4j
            await init_neo4j()
            logger.info("Neo4j initialized")
        except Exception as e:
            logger.debug(f"Neo4j not available (expected in dev): {e}")
            # Neo4j is optional - continue without it

        # Initialize monitoring (optional)
        try:
            from src.monitoring.prometheus import init_prometheus
            init_prometheus()
            logger.info("Monitoring initialized")
        except Exception as e:
            logger.warning(f"Prometheus initialization failed (optional): {e}")
            # Monitoring is optional - continue without it

        # Initialize structured logging (early, before other services)
        try:
            from src.utils.logging_config import setup_logging
            import os
            setup_logging(environment=os.getenv("ENVIRONMENT", "production"))
            logger.info("Structured logging configured")
        except Exception as e:
            logger.warning(f"Logging configuration failed (optional): {e}")

        # Initialize orchestrator (for task execution)
        try:
            from src.amas.core.unified_intelligence_orchestrator import get_unified_orchestrator
            orchestrator = get_unified_orchestrator()
            logger.info("Unified Intelligence Orchestrator initialized")
        except Exception as e:
            logger.warning(f"Orchestrator initialization failed (optional): {e}")

        # Initialize intelligence manager (for ML predictions)
        try:
            from src.amas.intelligence.intelligence_manager import get_intelligence_manager
            intelligence_manager = get_intelligence_manager()
            logger.info("Intelligence Manager initialized")
        except Exception as e:
            logger.warning(f"Intelligence Manager initialization failed (optional): {e}")

        # Initialize metrics service (for Prometheus metrics)
        try:
            from src.amas.services.prometheus_metrics_service import get_metrics_service
            metrics_service = get_metrics_service()
            logger.info("Prometheus Metrics Service initialized")
        except Exception as e:
            logger.warning(f"Metrics service initialization failed (optional): {e}")

        # Initialize cache services (for caching)
        try:
            from src.amas.services.task_cache_service import get_task_cache_service
            from src.amas.services.agent_cache_service import get_agent_cache_service
            from src.amas.services.prediction_cache_service import get_prediction_cache_service
            task_cache = get_task_cache_service()
            agent_cache = get_agent_cache_service()
            prediction_cache = get_prediction_cache_service()
            logger.info("Cache services initialized")
        except Exception as e:
            logger.warning(f"Cache services initialization failed (optional): {e}")

        # Start WebSocket heartbeat
        try:
            await start_websocket_heartbeat()
            logger.info("WebSocket heartbeat started")
        except Exception as e:
            logger.warning(f"WebSocket heartbeat failed (optional): {e}")

        # Start system monitor
        try:
            from src.amas.services.system_monitor import get_system_monitor
            system_monitor = get_system_monitor()
            await system_monitor.start()
            logger.info("System monitor started")
        except Exception as e:
            logger.warning(f"System monitor failed (optional): {e}")

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

        # Stop system monitor
        try:
            from src.amas.services.system_monitor import get_system_monitor
            system_monitor = get_system_monitor()
            await system_monitor.stop()
            logger.info("System monitor stopped")
        except Exception as e:
            logger.warning(f"Error stopping system monitor: {e}")

        logger.info("AMAS application shutdown complete")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="AMAS - Advanced Multi-Agent Intelligence System",
    description="Production-ready AI agent management system with full API endpoints",
    version="1.0.0",
    docs_url="/docs" if get_settings().features.enable_api_documentation else None,
    redoc_url="/redoc" if get_settings().features.enable_api_documentation else None,
    openapi_url="/openapi.json" if get_settings().features.enable_api_documentation else None,
    lifespan=lifespan,
)

# Initialize tracing after app creation (for FastAPI instrumentation)
try:
    from src.amas.services.tracing_service import init_tracing
    import os
    tracing = init_tracing(
        service_name="amas-backend",
        service_version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "production"),
        jaeger_endpoint=os.getenv("JAEGER_ENDPOINT"),
        otlp_endpoint=os.getenv("OTLP_ENDPOINT")
    )
    # Instrument FastAPI app
    tracing.instrument_app(app)
    logger.info("Tracing initialized and FastAPI instrumented")
except Exception as e:
    logger.warning(f"Tracing initialization failed (optional): {e}")
    # Tracing is optional - continue without it

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

# Metrics middleware (add early to track all requests)
from src.api.middleware.metrics_middleware import MetricsMiddleware
app.add_middleware(MetricsMiddleware)

# Rate limiting - use more lenient config for development
from src.middleware.rate_limiting import RateLimitConfig

rate_limit_config = RateLimitConfig(
    requests_per_minute=1000,  # Very high limit for development
    requests_per_hour=10000,
    burst_limit=100
)
app.add_middleware(RateLimitingMiddleware, config=rate_limit_config)
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
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["ML Predictions"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(workflows.router, prefix="/api/v1", tags=["workflows"])
app.include_router(integrations.router, prefix="/api/v1", tags=["integrations"])
app.include_router(system.router, prefix="/api/v1", tags=["System"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(metrics.router, tags=["Monitoring"])

# WebSocket endpoint
app.websocket("/ws")(websocket_endpoint)

# Health and readiness endpoints (must be before static mount)
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


# ---------- Frontend Static Serving ----------
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"

# Log frontend status at startup
logger.info(f"🔍 Checking frontend build...")
logger.info(f"   BASE_DIR: {BASE_DIR}")
logger.info(f"   FRONTEND_DIST: {FRONTEND_DIST}")
logger.info(f"   FRONTEND_INDEX: {FRONTEND_INDEX}")
logger.info(f"   FRONTEND_INDEX exists: {FRONTEND_INDEX.exists()}")
logger.info(f"   FRONTEND_ASSETS exists: {FRONTEND_ASSETS.exists()}")

if FRONTEND_ASSETS.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_ASSETS)),
        name="frontend-assets",
    )
    logger.info("✅ Frontend assets mounted at /assets")
elif FRONTEND_DIST.exists():
    logger.warning("Frontend dist found but /assets directory missing")
else:
    logger.warning(
        "Frontend build directory not found. Run: cd frontend && npm run build"
    )

if FRONTEND_DIST.exists():
    vite_svg = FRONTEND_DIST / "vite.svg"
    if vite_svg.exists():
        @app.get("/vite.svg", include_in_schema=False)
        async def serve_vite_svg() -> FileResponse:
            return FileResponse(str(vite_svg))


def _frontend_ready() -> bool:
    """Check if frontend is ready to serve"""
    exists = FRONTEND_INDEX.exists()
    if not exists:
        logger.warning(f"Frontend index not found at: {FRONTEND_INDEX.resolve()}")
        logger.warning(f"BASE_DIR: {BASE_DIR.resolve()}")
        logger.warning(f"FRONTEND_DIST exists: {FRONTEND_DIST.exists()}")
    return exists


def _should_bypass_spa(path: str) -> bool:
    protected_prefixes = (
        "api/",
        "docs",
        "redoc",
        "metrics",
        "health",
        "ready",
        "ws",
        "assets",
        "static",
    )
    protected_exact = {"openapi.json"}

    if path in protected_exact:
        return True

    return any(path.startswith(prefix) for prefix in protected_prefixes if path)


def _spa_response() -> Union[FileResponse, JSONResponse]:
    """Return SPA response - ALWAYS try to serve frontend first"""
    # Re-check file existence at runtime
    frontend_index_path = BASE_DIR / "frontend" / "dist" / "index.html"
    
    if frontend_index_path.exists():
        logger.info(f"Serving React frontend from: {frontend_index_path}")
        response = FileResponse(
            str(frontend_index_path),
            media_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )
        return response
    
    # Only return JSON if frontend truly doesn't exist
    logger.error(f"Frontend not found at: {frontend_index_path.resolve()}")
    return JSONResponse(
        {
            "message": "AMAS - Advanced Multi-Agent AI System API (Basic Version)",
            "version": "1.0.0-basic",
            "status": "running",
            "timestamp": time.time(),
            "note": f"Frontend not found at: {frontend_index_path}",
            "frontend_path": str(frontend_index_path.resolve()),
        }
    )


@app.get("/", include_in_schema=False)
async def serve_frontend_root():
    """Serve React SPA root or fallback JSON."""
    # Re-check file existence at runtime (not just at module load)
    frontend_index_path = BASE_DIR / "frontend" / "dist" / "index.html"
    
    if frontend_index_path.exists():
        logger.info(f"Serving React frontend from root: {frontend_index_path}")
        return FileResponse(
            str(frontend_index_path),
            media_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )
    
    logger.warning(f"Frontend not found, serving JSON fallback. Path: {frontend_index_path.resolve()}")
    return JSONResponse({
        "message": "AMAS - Advanced Multi-Agent AI System API",
        "version": "1.0.0",
        "status": "running",
        "error": f"Frontend not found at: {frontend_index_path.resolve()}",
        "frontend_path": str(frontend_index_path.resolve()),
        "note": "Run 'cd frontend && npm run build' to build the frontend",
    })


# SPA catch-all route for frontend client-side routing
# This must come AFTER all API routes to avoid interfering with them
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend_spa(full_path: str):
    """
    Serve React SPA for client-side routing.
    This route only handles non-API paths (API routes are matched first).
    """
    # Skip API routes, static assets, and special paths
    if (
        full_path.startswith("api/")
        or full_path.startswith("assets/")
        or full_path.startswith("docs")
        or full_path.startswith("redoc")
        or full_path.startswith("openapi.json")
        or full_path.startswith("health")
        or full_path.startswith("ready")
        or full_path.startswith("metrics")
        or full_path.startswith("ws")
        or full_path in {"favicon.ico", "robots.txt", "vite.svg"}
    ):
        # Return 404 for missing static assets (don't serve SPA for these)
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve frontend index.html for all other paths (SPA routing)
    frontend_index_path = BASE_DIR / "frontend" / "dist" / "index.html"
    
    if frontend_index_path.exists():
        logger.info(f"Serving React SPA for path: {full_path}")
        return FileResponse(
            str(frontend_index_path),
            media_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )
    
    raise HTTPException(status_code=404, detail="Frontend not found")


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
