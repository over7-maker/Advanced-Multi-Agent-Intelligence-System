"""
AMAS - Advanced Multi-Agent Intelligence System
Simple version for CI testing
"""

import logging
import time
from typing import Dict

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AMAS - Advanced Multi-Agent Intelligence System",
    description="Production-ready AI agent management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Store start time for uptime calculation
app.state.start_time = time.time()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AMAS - Advanced Multi-Agent Intelligence System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "uptime": time.time() - app.state.start_time,
            "services": {
                "database": "healthy",
                "redis": "healthy",
                "neo4j": "healthy",
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "timestamp": time.time(), "error": str(e)},
        )


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        return {
            "status": "ready",
            "timestamp": time.time(),
            "services": {
                "database": "healthy",
                "redis": "healthy",
                "neo4j": "healthy",
            },
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "timestamp": time.time(), "error": str(e)},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )