#!/usr/bin/env python3

"""
╔═══════════════════════════════════════════════════════════════════════════╗
║             BACKEND API v4.1.6 COMPATIBLE - HOTFIX RELEASE                ║
║              8-Stream Enterprise Data Ingestion Platform                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

Released: 2026-01-29 07:24 UTC+3
Compatibility: L4 Redirector v4.1.6 Emergency Hotfix

CRITICAL FIX:
  ✅ Accepts BOTH single objects AND lists from redirector
  ✅ Union[Dict, List[Dict]] for flexible validation
  ✅ No more 422 errors from v4.1.6

Data Streams: 8
  1. /api/v1/web/{port} - Client connections
  2. /api/v1/l2n/{port} - Backend tunnels
  3. /api/v1/errors/l2n/{port} - Connection errors
  4. /api/v1/performance/{port} - Latency metrics (NEW)
  5. /api/v1/throughput/{port} - Throughput stats (NEW)
  6. /api/v1/workers/status - Worker health (NEW)
  7. /api/v1/health/{port} - Port health (UPDATED)
  8. /api/v1/events/{port} - Lifecycle events (NEW)

"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union
from contextlib import asynccontextmanager

# ══════════════════════════════════════════════════════════════════════════
# CRITICAL FIX: Windows + Psycopg3 Event Loop Compatibility
# ══════════════════════════════════════════════════════════════════════════
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, Field, ConfigDict

# ══════════════════════════════════════════════════════════════════════════
# WINDOWS ENCODING FIX
# ══════════════════════════════════════════════════════════════════════════
if sys.platform == "win32":
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    USE_UNICODE = False
else:
    USE_UNICODE = True

# ══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5814"))
API_WORKERS = int(os.getenv("API_WORKERS", "4"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "redirector_db")
DB_USER = os.getenv("DB_USER", "redirector")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Azyz@123")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))

API_TOKEN = os.getenv("API_TOKEN", "e7595fe6ctoken815f7d18cd4cf63075")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════════════════
class WindowsUnicodeFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        if sys.platform == "win32" and not USE_UNICODE:
            replacements = {
                '✅': '[OK]', '❌': '[FAIL]', '🚀': '[START]', '🛑': '[STOP]',
                '╔': '+', '═': '=', '╗': '+', '║': '|', '╚': '+', '╝': '+',
            }
            for unicode_char, ascii_char in replacements.items():
                msg = msg.replace(unicode_char, ascii_char)
        return msg

handler_stream = logging.StreamHandler()
handler_stream.setFormatter(WindowsUnicodeFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
handler_file = logging.FileHandler(f"{LOG_DIR}/backend_api_v4.log")
handler_file.setFormatter(WindowsUnicodeFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

logging.basicConfig(level=LOG_LEVEL, handlers=[handler_stream, handler_file])
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTION POOL
# ══════════════════════════════════════════════════════════════════════════
db_pool: Optional[AsyncConnectionPool] = None

async def init_db_pool() -> AsyncConnectionPool:
    global db_pool
    conninfo = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    db_pool = AsyncConnectionPool(conninfo=conninfo, min_size=2, max_size=DB_POOL_SIZE, timeout=DB_POOL_TIMEOUT)
    async with db_pool.connection() as conn:
        result = await conn.execute("SELECT version();")
        version = await result.fetchone()
        logger.info(f"[OK] PostgreSQL: {version[0][:60]}...")
    return db_pool

async def close_db_pool() -> None:
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("[STOP] Database pool closed")

async def get_db_connection():
    if not db_pool:
        raise RuntimeError("Database pool not initialized")
    async with db_pool.connection() as conn:
        yield conn

# ══════════════════════════════════════════════════════════════════════════
# SECURITY
# ══════════════════════════════════════════════════════════════════════════
async def verify_token(authorization: Optional[str] = Header(None)) -> bool:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
    if parts[1] != API_TOKEN:
        logger.warning("[FAIL] Invalid token")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    return True

# ══════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS - ALL WITH extra="allow" FOR v4.1.6 COMPATIBILITY
# ══════════════════════════════════════════════════════════════════════════

class L2NError(BaseModel):
    """L2N Error stream - FIXED: accepts all v4.1.6 fields"""
    timestamp: Optional[str] = None
    error_type: str
    backend_ip: Optional[str] = None
    backend_port: Optional[int] = None
    client_ip: Optional[str] = None
    client_port: Optional[int] = None
    error_message: str
    worker_id: Optional[str] = None
    model_config = ConfigDict(extra="allow")

class PerformanceData(BaseModel):
    """Performance metrics with percentiles"""
    timestamp: Optional[str] = None
    port: int
    p50: Optional[int] = None
    p95: Optional[int] = None
    p99: Optional[int] = None
    min: Optional[int] = None
    max: Optional[int] = None
    sample_count: Optional[int] = None
    model_config = ConfigDict(extra="allow")

class ThroughputData(BaseModel):
    """Real-time throughput statistics"""
    timestamp: Optional[str] = None
    port: int
    bytes_per_sec: Optional[int] = None
    connections_per_sec: Optional[float] = None
    total_bytes_in: Optional[int] = None
    total_bytes_out: Optional[int] = None
    total_connections: Optional[int] = None
    model_config = ConfigDict(extra="allow")

class WorkerData(BaseModel):
    """Worker health & resource usage"""
    timestamp: Optional[str] = None
    workers: Optional[Dict[str, Any]] = None
    worker_count: Optional[int] = None
    model_config = ConfigDict(extra="allow")

class HealthData(BaseModel):
    """Port health status"""
    timestamp: Optional[str] = None
    port: int
    tcp_status: Optional[str] = None
    tcp_latency_ms: Optional[int] = None
    udp_status: Optional[str] = None
    uptime_sec: Optional[int] = None
    model_config = ConfigDict(extra="allow")

class EventData(BaseModel):
    """Connection lifecycle events"""
    timestamp: Optional[str] = None
    port: int
    events: Optional[List[Dict[str, Any]]] = None
    count: Optional[int] = None
    model_config = ConfigDict(extra="allow")

# ══════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ══════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[START] Backend API v4.1.6 starting...")
    await init_db_pool()
    yield
    logger.info("[STOP] Backend API v4.1.6 shutting down...")
    await close_db_pool()

app = FastAPI(
    title="Backend API v4.1.6 Compatible",
    description="8-Stream Enterprise Data Platform",
    version="4.1.6-compatible",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ══════════════════════════════════════════════════════════════════════════
# HEALTH CHECKS
# ══════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check(conn = Depends(get_db_connection)):
    try:
        result = await conn.execute("SELECT 1;")
        await result.fetchone()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "version": "4.1.6-compatible",
        }
    except Exception as e:
        logger.error(f"[FAIL] Health check: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)},
        )

# ══════════════════════════════════════════════════════════════════════════
# STREAM 1: WEB CONNECTIONS - ACCEPTS SINGLE DICT OR LIST
# ══════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/web/{port}")
async def ingest_web(
    port: int,
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    try:
        # Normalize to list
        items = [data] if isinstance(data, dict) else data
        table = f"web_p_{port}"
        
        for item in items:
            await conn.execute(
                f"""INSERT INTO {table} (timestamp, client_ip, client_port, bytes_in, bytes_out, duration_ms, worker_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    item.get("timestamp", datetime.utcnow().isoformat()),
                    item.get("client_ip"),
                    item.get("client_port"),
                    item.get("bytes_in", 0),
                    item.get("bytes_out", 0),
                    item.get("duration_ms", 0),
                    item.get("worker_id"),
                ),
            )
        logger.info(f"[OK] Web[{port}]: {len(items)} records")
        return {"status": "success", "port": port, "records": len(items)}
    except Exception as e:
        logger.error(f"[FAIL] Web ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════════════════
# STREAM 2: L2N CONNECTIONS - ACCEPTS SINGLE DICT OR LIST
# ══════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/l2n/{port}")
async def ingest_l2n(
    port: int,
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    try:
        # Normalize to list
        items = [data] if isinstance(data, dict) else data
        table = f"l2n_p_{port}"
        
        for item in items:
            await conn.execute(
                f"""INSERT INTO {table} (timestamp, backend_ip, backend_port, bytes_in, bytes_out, duration_ms, latency_ms, worker_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    item.get("timestamp", datetime.utcnow().isoformat()),
                    item.get("backend_ip"),
                    item.get("backend_port"),
                    item.get("bytes_in", 0),
                    item.get("bytes_out", 0),
                    item.get("duration_ms", 0),
                    item.get("latency_ms", 0),
                    item.get("worker_id"),
                ),
            )
        logger.info(f"[OK] L2N[{port}]: {len(items)} records")
        return {"status": "success", "port": port, "records": len(items)}
    except Exception as e:
        logger.error(f"[FAIL] L2N ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════════════════
# STREAM 3: L2N ERRORS (FIXED - ACCEPTS ALL FIELDS)
# ══════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/errors/l2n/{port}")
async def ingest_l2n_error(
    port: int,
    data: L2NError,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    try:
        await conn.execute(
            """INSERT INTO l2n_errors (timestamp, port, error_type, backend_ip, backend_port, client_ip, client_port, error_message, worker_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                data.timestamp or datetime.utcnow().isoformat(),
                port,
                data.error_type,
                data.backend_ip,
                data.backend_port,
                data.client_ip,
                data.client_port,
                data.error_message,
                data.worker_id,
            ),
        )
        logger.info(f"[OK] L2N Error[{port}]: {data.error_type}")
        return {"status": "success", "port": port, "error_type": data.error_type}
    except Exception as e:
        logger.error(f"[FAIL] L2N Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════════════════
# STREAM 4: PERFORMANCE METRICS (NEW)
# ══════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/performance/{port}")
async def ingest_performance(
    port: int,
    data: PerformanceData,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    try:
        await conn.execute(
            """INSERT INTO performance_metrics (timestamp, port, p50_ms, p95_ms, p99_ms, min_ms, max_ms, sample_count)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                data.timestamp or datetime.utcnow().isoformat(),
                port,
                data.p50,
                data.p95,
                data.p99,
                data.min,
                data.max,
                data.sample_count,
            ),
        )
        logger.info(f"[OK] Performance[{port}]: p50={data.p50}ms p95={data.p95}ms")
        return {"status": "success", "port": port}
    except Exception as e:
        logger.error(f"[FAIL] Performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════════════════
# STREAM 5: THROUGHPUT STATISTICS (NEW)
# ══════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/throughput/{port}")
async def ingest_throughput(
    port: int,
    data: ThroughputData,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    try:
        await conn.execute(
            """INSERT INTO throughput_stats (timestamp, port, bytes_per_sec, connections_per_sec, total_bytes_in, total_bytes_out, total_connections)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                data.timestamp or datetime.utcnow().isoformat(),
                port,
                data.bytes_per_sec,
                data.connections_per_sec,
                data.total_bytes_in,
                data.total_bytes_out,
                data.total_connections,
            ),
        )
        logger.info(f"[OK] Throughput[{port}]: {data.bytes_per_sec}B/s")
        return {"status": "success", "port": port}
    except Exception as e:
        logger.error(f"[FAIL] Throughput: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════════════════
# STREAM 6: WORKER STATUS (NEW)
# ══════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/workers/status")
async def ingest_worker_status(
    data: WorkerData,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    try:
        worker_json = json.dumps(data.workers) if data.workers else None
        await conn.execute(
            """INSERT INTO worker_stats (timestamp, worker_json, worker_count)
               VALUES (%s, %s, %s)""",
            (
                data.timestamp or datetime.utcnow().isoformat(),
                worker_json,
                data.worker_count,
            ),
        )
        logger.info(f"[OK] Workers: {data.worker_count}")
        return {"status": "success", "worker_count": data.worker_count}
    except Exception as e:
        logger.error(f"[FAIL] Worker status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════════════════
# STREAM 7: PORT HEALTH (UPDATED)
# ══════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/health/{port}")
async def ingest_health(
    port: int,
    data: HealthData,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    try:
        await conn.execute(
            """INSERT INTO port_health (timestamp, port, tcp_status, tcp_latency_ms, udp_status, uptime_sec)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                data.timestamp or datetime.utcnow().isoformat(),
                port,
                data.tcp_status,
                data.tcp_latency_ms,
                data.udp_status,
                data.uptime_sec,
            ),
        )
        logger.info(f"[OK] Health[{port}]: {data.tcp_status}")
        return {"status": "success", "port": port}
    except Exception as e:
        logger.error(f"[FAIL] Health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════════════════
# STREAM 8: CONNECTION EVENTS (NEW)
# ══════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/events/{port}")
async def ingest_events(
    port: int,
    data: EventData,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    try:
        events_json = json.dumps(data.events) if data.events else None
        await conn.execute(
            """INSERT INTO connection_events (timestamp, port, events_json, event_count)
               VALUES (%s, %s, %s, %s)""",
            (
                data.timestamp or datetime.utcnow().isoformat(),
                port,
                events_json,
                data.count,
            ),
        )
        logger.info(f"[OK] Events[{port}]: {data.count}")
        return {"status": "success", "port": port}
    except Exception as e:
        logger.error(f"[FAIL] Events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════════════════
# ROOT & QUERY ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "name": "Backend API v4.1.6 Compatible",
        "version": "4.1.6-compatible",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "streams": 8,
        "compatibility": "L4 Redirector v4.1.6",
        "accepts": "Both single objects and lists",
    }

@app.get("/api/v1/query/stats")
async def query_stats(
    hours: int = 1,
    port: Optional[int] = None,
    _: bool = Depends(verify_token),
    conn = Depends(get_db_connection),
):
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        table = f"web_p_{port or 8041}"
        
        result = await conn.execute(
            f"SELECT COUNT(*), SUM(bytes_in), SUM(bytes_out) FROM {table} WHERE timestamp > %s",
            (since,),
        )
        web_row = await result.fetchone()
        
        return {
            "period_hours": hours,
            "port": port or 8041,
            "stats": {
                "connections": web_row[0] or 0,
                "bytes_in": web_row[1] or 0,
                "bytes_out": web_row[2] or 0,
            },
        }
    except Exception as e:
        logger.error(f"[FAIL] Query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info("="*70)
    logger.info("Backend API v4.1.6 Compatible - 8-Stream Platform")
    logger.info("CRITICAL FIX: Accepts both single objects and lists")
    logger.info(f"Listening: {API_HOST}:{API_PORT}")
    logger.info(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    logger.info("="*70)
    
    uvicorn.run(
        "backend_api_v4:app",
        host=API_HOST,
        port=API_PORT,
        workers=API_WORKERS,
        reload=False,
        log_level=LOG_LEVEL.lower(),
    )