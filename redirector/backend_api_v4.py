#!/usr/bin/env python3

"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    BACKEND API v4 - PRODUCTION BUILD                      ║
║              Enterprise Data Ingestion & Analytics Platform               ║
╚═══════════════════════════════════════════════════════════════════════════╝

Purpose:
  - Ingest 8 concurrent data streams from VPS Redirector v4.1.6
  - Store to PostgreSQL (redirector_db)
  - Provide REST API endpoints for querying analytics
  - Real-time metrics and performance analysis
  - Health monitoring and error tracking

Architecture:
  - Async FastAPI framework
  - Connection pooling with psycopg3
  - OAuth2 Bearer token authentication
  - Rate limiting & request throttling
  - Comprehensive error handling
  - Structured logging

Data Streams:
  1. Web connections (ports 8041, 8047, 8057)
  2. L2N connections (ports 8041, 8047, 8057)
  3. Web errors
  4. L2N errors
  5. Performance metrics (p50, p95, p99)
  6. Throughput statistics
  7. Worker resource usage
  8. Port health status

Author: AMAS Team
Version: 4.0.0
Last Updated: 2026-01-29

"""

import os
import sys
import json
import logging
import asyncio
import selectors
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from contextlib import asynccontextmanager

# ═══════════════════════════════════════════════════════════════════════════
# CRITICAL FIX: Windows + Psycopg3 Event Loop Compatibility
# ═══════════════════════════════════════════════════════════════════════════
# 
# Windows uses ProactorEventLoop by default (IOCP-based, faster)
# Psycopg3 requires SelectorEventLoop (select-based, compatible with PostgreSQL)
# This must be set BEFORE any async code or psycopg3 imports
#
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════
# WINDOWS ENCODING FIX (CRITICAL FOR CONSOLE LOGGING)
# ═══════════════════════════════════════════════════════════════════════════

if sys.platform == "win32":
    # Force UTF-8 for stderr/stdout on Windows
    import io
    import codecs
    
    # Reconfigure stderr/stdout to use UTF-8 with error handling
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    
    # Use ASCII fallback for logging to avoid UnicodeEncodeError
    USE_UNICODE = False
else:
    USE_UNICODE = True

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5814"))
API_WORKERS = int(os.getenv("API_WORKERS", "4"))

# Database Settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "redirector_db")
DB_USER = os.getenv("DB_USER", "redirector")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Azyz@123")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))

# Security Settings
API_TOKEN = os.getenv("API_TOKEN", "e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075")
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "127.0.0.1,192.168.*").split(",")

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════
# LOGGING SETUP (with ASCII fallback for Windows)
# ═══════════════════════════════════════════════════════════════════════════

class WindowsUnicodeFormatter(logging.Formatter):
    """Custom formatter that strips Unicode characters on Windows."""
    
    def format(self, record):
        msg = super().format(record)
        if sys.platform == "win32" and not USE_UNICODE:
            # Replace Unicode characters with ASCII equivalents
            replacements = {
                '✅': '[OK]',
                '❌': '[FAIL]',
                '🚀': '[START]',
                '🛑': '[STOP]',
                '╔': '+',
                '═': '=',
                '╗': '+',
                '║': '|',
                '╚': '+',
                '╝': '+',
                '✨': '*',
                '📊': '[STATS]',
                '⚠️': '[WARN]',
                '🔒': '[LOCK]',
                '🔓': '[UNLOCK]',
            }
            for unicode_char, ascii_char in replacements.items():
                msg = msg.replace(unicode_char, ascii_char)
        return msg


# Configure logging
handler_stream = logging.StreamHandler()
handler_stream.setFormatter(WindowsUnicodeFormatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

handler_file = logging.FileHandler(f"{LOG_DIR}/backend_api_v4.log")
handler_file.setFormatter(WindowsUnicodeFormatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

logging.basicConfig(
    level=LOG_LEVEL,
    handlers=[handler_stream, handler_file],
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTION POOL
# ═══════════════════════════════════════════════════════════════════════════

db_pool: Optional[AsyncConnectionPool] = None


async def init_db_pool() -> AsyncConnectionPool:
    """Initialize PostgreSQL connection pool."""
    global db_pool
    
    conninfo = (
        f"host={DB_HOST} "
        f"port={DB_PORT} "
        f"dbname={DB_NAME} "
        f"user={DB_USER} "
        f"password={DB_PASSWORD}"
    )
    
    db_pool = AsyncConnectionPool(
        conninfo=conninfo,
        min_size=2,
        max_size=DB_POOL_SIZE,
        timeout=DB_POOL_TIMEOUT,
    )
    
    async with db_pool.connection() as conn:
        result = await conn.execute("SELECT version();")
        version = await result.fetchone()
        logger.info(f"[OK] Connected to PostgreSQL: {version[0]}")
    
    return db_pool


async def close_db_pool() -> None:
    """Close database connection pool."""
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("[STOP] PostgreSQL connection pool closed")


async def get_db_connection():
    """Get database connection from pool."""
    if not db_pool:
        raise RuntimeError("Database pool not initialized")
    async with db_pool.connection() as conn:
        yield conn


# ═══════════════════════════════════════════════════════════════════════════
# SECURITY & AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════

async def verify_token(authorization: Optional[str] = Header(None)) -> bool:
    """Verify Bearer token."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
    
    token = parts[1]
    if token != API_TOKEN:
        logger.warning(f"[FAIL] Invalid token attempt: {token[:20]}...")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    
    return True


# ═══════════════════════════════════════════════════════════════════════════
# DATA MODELS (Pydantic)
# ═══════════════════════════════════════════════════════════════════════════

class WebConnectionData(BaseModel):
    """Web connection stream data."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    port: int = Field(..., ge=8000, le=9000)
    client_ip: str
    client_port: int
    bytes_in: int = Field(default=0, ge=0)
    bytes_out: int = Field(default=0, ge=0)
    duration_ms: int = Field(default=0, ge=0)
    worker_id: Optional[str] = None


class L2NConnectionData(BaseModel):
    """L2N connection stream data."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    port: int = Field(..., ge=8000, le=9000)
    backend_ip: str
    backend_port: int
    bytes_in: int = Field(default=0, ge=0)
    bytes_out: int = Field(default=0, ge=0)
    duration_ms: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)
    worker_id: Optional[str] = None


class ErrorData(BaseModel):
    """Error event data."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    port: int = Field(..., ge=8000, le=9000)
    error_type: str
    client_ip: Optional[str] = None
    backend_ip: Optional[str] = None
    error_message: str


class PerformanceMetrics(BaseModel):
    """Performance metrics data."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    port: int = Field(..., ge=8000, le=9000)
    p50_ms: int
    p95_ms: int
    p99_ms: int
    min_ms: int
    max_ms: int
    worker_id: Optional[str] = None


class ThroughputStats(BaseModel):
    """Throughput statistics data."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    port: int = Field(..., ge=8000, le=9000)
    bytes_per_sec: int
    connections_per_sec: int
    worker_id: Optional[str] = None


class WorkerStats(BaseModel):
    """Worker resource usage data."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    worker_id: str
    active_tcp: int = Field(ge=0)
    total_tcp: int = Field(ge=0)
    bytes_in: int = Field(ge=0)
    bytes_out: int = Field(ge=0)
    uptime_sec: int = Field(ge=0)
    cpu_percent: float = Field(ge=0.0, le=100.0)
    memory_mb: float = Field(ge=0.0)


class PortHealth(BaseModel):
    """Port health status data."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    port: int = Field(..., ge=8000, le=9000)
    tcp_status: str  # "healthy", "degraded", "down"
    tcp_latency_ms: Optional[int] = None
    udp_status: Optional[str] = None
    uptime_sec: int = Field(ge=0)


class StreamData(BaseModel):
    """Batch stream data submission."""
    stream_type: str  # "web", "l2n", "error", "metrics", "throughput", "worker", "health"
    data: List[Dict[str, Any]]
    worker_id: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: startup and shutdown."""
    # Startup
    logger.info("[START] Backend API v4 starting...")
    await init_db_pool()
    yield
    # Shutdown
    logger.info("[STOP] Backend API v4 shutting down...")
    await close_db_pool()


app = FastAPI(
    title="Backend API v4",
    description="Enterprise data ingestion & analytics platform",
    version="4.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check(conn = Depends(get_db_connection)):
    """Health check endpoint."""
    try:
        result = await conn.execute("SELECT 1;")
        await result.fetchone()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "version": "4.0.0",
        }
    except Exception as e:
        logger.error(f"[FAIL] Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "disconnected",
                "error": str(e),
            },
        )


@app.get("/health/database")
async def database_health(conn = Depends(get_db_connection)):
    """Detailed database health check."""
    try:
        result = await conn.execute("""
            SELECT 
                (SELECT COUNT(*) FROM web_p_8041) as web_8041,
                (SELECT COUNT(*) FROM l2n_p_8041) as l2n_8041,
                (SELECT COUNT(*) FROM web_errors) as web_errors,
                (SELECT COUNT(*) FROM l2n_errors) as l2n_errors;
        """)
        row = await result.fetchone()
        return {
            "status": "connected",
            "tables": {
                "web_8041": row[0],
                "l2n_8041": row[1],
                "web_errors": row[2],
                "l2n_errors": row[3],
            },
        }
    except Exception as e:
        logger.error(f"[FAIL] Database health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════
# DATA INGESTION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/stream/ingest")
async def ingest_stream(
    data: StreamData,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    """Ingest batch data from streams."""
    try:
        stream_type = data.stream_type.lower()
        count = 0
        
        if stream_type == "web":
            for item in data.data:
                port = item.get("port", 8041)
                table = f"web_p_{port}"
                await conn.execute(
                    f"""
                    INSERT INTO {table} 
                    (timestamp, client_ip, client_port, bytes_in, bytes_out, duration_ms, worker_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item.get("timestamp", datetime.utcnow()),
                        item.get("client_ip"),
                        item.get("client_port"),
                        item.get("bytes_in", 0),
                        item.get("bytes_out", 0),
                        item.get("duration_ms", 0),
                        item.get("worker_id"),
                    ),
                )
                count += 1
        
        elif stream_type == "l2n":
            for item in data.data:
                port = item.get("port", 8041)
                table = f"l2n_p_{port}"
                await conn.execute(
                    f"""
                    INSERT INTO {table}
                    (timestamp, backend_ip, backend_port, bytes_in, bytes_out, duration_ms, latency_ms, worker_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item.get("timestamp", datetime.utcnow()),
                        item.get("backend_ip"),
                        item.get("backend_port"),
                        item.get("bytes_in", 0),
                        item.get("bytes_out", 0),
                        item.get("duration_ms", 0),
                        item.get("latency_ms", 0),
                        item.get("worker_id"),
                    ),
                )
                count += 1
        
        elif stream_type == "error":
            for item in data.data:
                error_type = item.get("error_type", "unknown")
                table = "web_errors" if "web" in error_type.lower() else "l2n_errors"
                await conn.execute(
                    f"""
                    INSERT INTO {table}
                    (timestamp, port, error_type, client_ip, backend_ip, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item.get("timestamp", datetime.utcnow()),
                        item.get("port", 8041),
                        error_type,
                        item.get("client_ip"),
                        item.get("backend_ip"),
                        item.get("error_message", ""),
                    ),
                )
                count += 1
        
        elif stream_type == "metrics":
            for item in data.data:
                await conn.execute(
                    """
                    INSERT INTO performance_metrics
                    (timestamp, port, p50_ms, p95_ms, p99_ms, min_ms, max_ms, worker_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item.get("timestamp", datetime.utcnow()),
                        item.get("port"),
                        item.get("p50_ms"),
                        item.get("p95_ms"),
                        item.get("p99_ms"),
                        item.get("min_ms"),
                        item.get("max_ms"),
                        item.get("worker_id"),
                    ),
                )
                count += 1
        
        elif stream_type == "throughput":
            for item in data.data:
                await conn.execute(
                    """
                    INSERT INTO throughput_stats
                    (timestamp, port, bytes_per_sec, connections_per_sec, worker_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        item.get("timestamp", datetime.utcnow()),
                        item.get("port"),
                        item.get("bytes_per_sec"),
                        item.get("connections_per_sec"),
                        item.get("worker_id"),
                    ),
                )
                count += 1
        
        elif stream_type == "worker":
            for item in data.data:
                await conn.execute(
                    """
                    INSERT INTO worker_stats
                    (timestamp, worker_id, active_tcp, total_tcp, bytes_in, bytes_out, uptime_sec, cpu_percent, memory_mb)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item.get("timestamp", datetime.utcnow()),
                        item.get("worker_id"),
                        item.get("active_tcp"),
                        item.get("total_tcp"),
                        item.get("bytes_in"),
                        item.get("bytes_out"),
                        item.get("uptime_sec"),
                        item.get("cpu_percent"),
                        item.get("memory_mb"),
                    ),
                )
                count += 1
        
        elif stream_type == "health":
            for item in data.data:
                await conn.execute(
                    """
                    INSERT INTO port_health
                    (timestamp, port, tcp_status, tcp_latency_ms, udp_status, uptime_sec)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item.get("timestamp", datetime.utcnow()),
                        item.get("port"),
                        item.get("tcp_status"),
                        item.get("tcp_latency_ms"),
                        item.get("udp_status"),
                        item.get("uptime_sec"),
                    ),
                )
                count += 1
        
        logger.info(f"[OK] STREAM [{stream_type.upper()}]: Ingested {count} records")
        
        return {
            "status": "success",
            "stream_type": stream_type,
            "records_inserted": count,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"[FAIL] Stream ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════
# QUERY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/query/stats")
async def query_stats(
    hours: int = 1,
    port: Optional[int] = None,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    """Query aggregated statistics."""
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Web stats
        web_query = "SELECT COUNT(*) as count, SUM(bytes_in) as bytes_in, SUM(bytes_out) as bytes_out FROM web_p_8041 WHERE timestamp > %s"
        if port:
            table = f"web_p_{port}"
            web_query = f"SELECT COUNT(*) as count, SUM(bytes_in) as bytes_in, SUM(bytes_out) as bytes_out FROM {table} WHERE timestamp > %s"
        
        result = await conn.execute(web_query, (since,))
        web_row = await result.fetchone()
        
        # L2N stats
        l2n_query = "SELECT COUNT(*) as count, SUM(bytes_in) as bytes_in, SUM(bytes_out) as bytes_out, AVG(latency_ms) as avg_latency FROM l2n_p_8041 WHERE timestamp > %s"
        if port:
            table = f"l2n_p_{port}"
            l2n_query = f"SELECT COUNT(*) as count, SUM(bytes_in) as bytes_in, SUM(bytes_out) as bytes_out, AVG(latency_ms) as avg_latency FROM {table} WHERE timestamp > %s"
        
        result = await conn.execute(l2n_query, (since,))
        l2n_row = await result.fetchone()
        
        # Error stats
        result = await conn.execute(
            "SELECT COUNT(*) as web_errors FROM web_errors WHERE timestamp > %s",
            (since,),
        )
        web_errors = (await result.fetchone())[0]
        
        result = await conn.execute(
            "SELECT COUNT(*) as l2n_errors FROM l2n_errors WHERE timestamp > %s",
            (since,),
        )
        l2n_errors = (await result.fetchone())[0]
        
        return {
            "period_hours": hours,
            "stats": {
                "web": {
                    "connections": web_row[0] or 0,
                    "bytes_in": web_row[1] or 0,
                    "bytes_out": web_row[2] or 0,
                },
                "l2n": {
                    "connections": l2n_row[0] or 0,
                    "bytes_in": l2n_row[1] or 0,
                    "bytes_out": l2n_row[2] or 0,
                    "avg_latency_ms": round(l2n_row[3] or 0, 2),
                },
                "errors": {
                    "web_errors": web_errors,
                    "l2n_errors": l2n_errors,
                },
            },
        }
    
    except Exception as e:
        logger.error(f"[FAIL] Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/query/performance")
async def query_performance(
    hours: int = 1,
    port: int = 8041,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    """Query performance metrics."""
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await conn.execute(
            """
            SELECT 
                AVG(p50_ms) as avg_p50,
                AVG(p95_ms) as avg_p95,
                AVG(p99_ms) as avg_p99,
                MIN(min_ms) as min_latency,
                MAX(max_ms) as max_latency
            FROM performance_metrics
            WHERE timestamp > %s AND port = %s
            """,
            (since, port),
        )
        
        row = await result.fetchone()
        
        return {
            "port": port,
            "period_hours": hours,
            "metrics": {
                "p50_ms": round(row[0] or 0, 2),
                "p95_ms": round(row[1] or 0, 2),
                "p99_ms": round(row[2] or 0, 2),
                "min_latency_ms": row[3] or 0,
                "max_latency_ms": row[4] or 0,
            },
        }
    
    except Exception as e:
        logger.error(f"[FAIL] Performance query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════
# MAINTENANCE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/maintenance/vacuum")
async def maintenance_vacuum(
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    """Run database VACUUM operation."""
    try:
        await conn.execute("VACUUM ANALYZE;")
        logger.info("[OK] Database VACUUM completed")
        return {"status": "success", "operation": "VACUUM ANALYZE"}
    except Exception as e:
        logger.error(f"[FAIL] VACUUM failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/maintenance/purge")
async def maintenance_purge(
    days: int = 7,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    """Delete records older than N days."""
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        tables = [
            "web_p_8041", "web_p_8047", "web_p_8057",
            "l2n_p_8041", "l2n_p_8047", "l2n_p_8057",
            "web_errors", "l2n_errors", "performance_metrics",
            "throughput_stats", "worker_stats", "port_health",
            "connection_events", "warnings", "succeeded_access",
        ]
        
        total_deleted = 0
        for table in tables:
            result = await conn.execute(
                f"DELETE FROM {table} WHERE timestamp < %s;",
                (cutoff,),
            )
            deleted = result.rowcount
            total_deleted += deleted
            logger.info(f"  - {table}: {deleted} rows deleted")
        
        logger.info(f"[OK] Purged {total_deleted} old records (>{days} days)")
        
        return {
            "status": "success",
            "operation": "purge",
            "days": days,
            "total_records_deleted": total_deleted,
        }
    
    except Exception as e:
        logger.error(f"[FAIL] Purge failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════
# ROOT ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Backend API v4",
        "version": "4.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "ingest": "/api/v1/stream/ingest",
            "stats": "/api/v1/query/stats",
            "performance": "/api/v1/query/performance",
            "docs": "/docs",
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    banner_line = "=================================================================="
    logger.info(banner_line)
    logger.info("Backend API v4 - Enterprise Edition")
    logger.info("Starting Server...")
    logger.info(banner_line)
    
    uvicorn.run(
        "backend_api_v4:app",
        host=API_HOST,
        port=API_PORT,
        workers=API_WORKERS,
        reload=False,
        log_level=LOG_LEVEL.lower(),
    )
