#!/usr/bin/env python3
"""
Enterprise Backend API v3 FIXED - PRODUCTION READY
Windows Backend Server (192.168.88.16:5814)
Receives all 8 data streams from hybrid L4 redirector on VPS

ALL 8 DATA STREAM ENDPOINTS:
  1. POST /api/v1/web/{port} - Web client connections
  2. POST /api/v1/l2n/{port} - L2N backend connections
  3. POST /api/v1/errors/web/{port} - Web errors
  4. POST /api/v1/errors/l2n/{port} - L2N errors
  5. POST /api/v1/warnings - Connection warnings
  6. POST /api/v1/succeeded - Succeeded access
  7. POST /api/v1/health/{port} - Port health
  8. POST /api/v1/health/l2n - L2N health

Plus comprehensive query endpoints for analytics.

Deployment: Windows Backend 192.168.88.16:5814
Receives: VPS via LocalToNet (194.182.64.133:6921)
Database: PostgreSQL
"""

from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.responses import JSONResponse
import asyncpg
import logging
import os
from datetime import datetime, timedelta
import time
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional, List
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

API_HOST = "0.0.0.0"
API_PORT = 5814
BACKEND_API_TOKEN = "e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"

DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_USER = "redirector"
DB_PASSWORD = "Azyz@123"
DB_NAME = "redirector_db"
DB_MIN_POOL = 10
DB_MAX_POOL = 30

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('backend_api_v3')

# ============================================================================
# DATABASE
# ============================================================================

class Database:
    def __init__(self):
        self.pool = None
    
    async def init(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                min_size=DB_MIN_POOL,
                max_size=DB_MAX_POOL
            )
            logger.info(f"\u2705 Database pool initialized ({DB_HOST}:{DB_PORT}/{DB_NAME})")
            
            # Create tables if they don't exist
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS web_p_8041 (
                        id BIGSERIAL PRIMARY KEY,
                        timestamp TIMESTAMP,
                        client_ip INET,
                        client_port INTEGER,
                        bytes_in BIGINT,
                        bytes_out BIGINT,
                        duration_ms INTEGER,
                        worker_id VARCHAR(50)
                    );
                    CREATE TABLE IF NOT EXISTS web_p_8047 (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, client_ip INET, client_port INTEGER, bytes_in BIGINT, bytes_out BIGINT, duration_ms INTEGER, worker_id VARCHAR(50));
                    CREATE TABLE IF NOT EXISTS web_p_8057 (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, client_ip INET, client_port INTEGER, bytes_in BIGINT, bytes_out BIGINT, duration_ms INTEGER, worker_id VARCHAR(50));
                    
                    CREATE TABLE IF NOT EXISTS l2n_p_8041 (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, backend_ip INET, backend_port INTEGER, bytes_in BIGINT, bytes_out BIGINT, duration_ms INTEGER, latency_ms INTEGER, worker_id VARCHAR(50));
                    CREATE TABLE IF NOT EXISTS l2n_p_8047 (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, backend_ip INET, backend_port INTEGER, bytes_in BIGINT, bytes_out BIGINT, duration_ms INTEGER, latency_ms INTEGER, worker_id VARCHAR(50));
                    CREATE TABLE IF NOT EXISTS l2n_p_8057 (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, backend_ip INET, backend_port INTEGER, bytes_in BIGINT, bytes_out BIGINT, duration_ms INTEGER, latency_ms INTEGER, worker_id VARCHAR(50));
                    
                    CREATE TABLE IF NOT EXISTS web_errors (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, port INTEGER, error_type VARCHAR(50), client_ip INET, error_message TEXT);
                    CREATE TABLE IF NOT EXISTS l2n_errors (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, port INTEGER, error_type VARCHAR(50), backend_ip INET, error_message TEXT);
                    
                    CREATE TABLE IF NOT EXISTS warnings (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, port INTEGER, warning_type VARCHAR(50), message TEXT, severity VARCHAR(20));
                    
                    CREATE TABLE IF NOT EXISTS succeeded_access (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, port INTEGER, client_ip INET, client_port INTEGER, backend_ip INET, backend_port INTEGER, bytes_transferred BIGINT, duration_ms INTEGER);
                    
                    CREATE TABLE IF NOT EXISTS port_health (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, port INTEGER, status VARCHAR(10), latency_ms INTEGER);
                    CREATE TABLE IF NOT EXISTS l2n_health (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, tunnel VARCHAR(50), tunnel_ip INET, tunnel_port INTEGER, status VARCHAR(10), latency_ms INTEGER);
                    
                    CREATE TABLE IF NOT EXISTS api_access_log (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMP, endpoint VARCHAR(200), status_code INTEGER, response_ms INTEGER);
                    
                    CREATE INDEX IF NOT EXISTS idx_web_8041_ts ON web_p_8041(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_web_8047_ts ON web_p_8047(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_web_8057_ts ON web_p_8057(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_l2n_8041_ts ON l2n_p_8041(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_l2n_8047_ts ON l2n_p_8047(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_l2n_8057_ts ON l2n_p_8057(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_web_err_ts ON web_errors(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_l2n_err_ts ON l2n_errors(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_warn_ts ON warnings(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_succ_ts ON succeeded_access(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_port_health_ts ON port_health(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_l2n_health_ts ON l2n_health(timestamp DESC);
                """)
                logger.info("\u2705 Database tables and indexes ready")
        except Exception as e:
            logger.error(f"\u274c Database initialization failed: {e}")
            raise
    
    async def close(self):
        """Close database pool"""
        if self.pool:
            await self.pool.close()
            logger.info("\u2705 Database pool closed")

db = Database()

# ============================================================================
# FASTAPI LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.init()
    yield
    # Shutdown
    await db.close()

app = FastAPI(title="Enterprise L4 Redirector Backend API v3 FIXED", lifespan=lifespan)

# ============================================================================
# SECURITY
# ============================================================================

async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify API token on all POST endpoints"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization[7:]
    if token != BACKEND_API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat(), "version": "3.0-fixed"}

@app.get("/status")
async def status():
    """API status endpoint"""
    try:
        async with db.pool.acquire() as conn:
            result = await conn.fetchval("SELECT COUNT(*) FROM web_p_8041")
        return {
            "status": "ok",
            "database": "connected",
            "records_web_8041": result,
            "version": "3.0-fixed"
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

# ============================================================================
# STREAM 1: WEB CONNECTIONS (8041/8047/8057)
# ============================================================================

@app.post("/api/v1/web/{port}")
async def receive_web_connection(port: int, data: dict, token: str = Depends(verify_token)):
    """STREAM 1: Receive web client connection data from VPS"""
    try:
        table = f'web_p_{port}'
        async with db.pool.acquire() as conn:
            await conn.execute(f"""
                INSERT INTO {table} (timestamp, client_ip, client_port, bytes_in, bytes_out, duration_ms, worker_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            data.get('timestamp'),
            data.get('client_ip'),
            data.get('client_port'),
            data.get('bytes_in', 0),
            data.get('bytes_out', 0),
            data.get('duration_ms', 0),
            data.get('worker_id')
            )
        return {"status": "success", "stream": 1}
    except Exception as e:
        logger.error(f"Stream 1 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STREAM 2: L2N CONNECTIONS (8041/8047/8057)
# ============================================================================

@app.post("/api/v1/l2n/{port}")
async def receive_l2n_connection(port: int, data: dict, token: str = Depends(verify_token)):
    """STREAM 2: Receive L2N backend connection data from VPS"""
    try:
        table = f'l2n_p_{port}'
        async with db.pool.acquire() as conn:
            await conn.execute(f"""
                INSERT INTO {table} (timestamp, backend_ip, backend_port, bytes_in, bytes_out, duration_ms, latency_ms, worker_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            data.get('timestamp'),
            data.get('backend_ip'),
            data.get('backend_port'),
            data.get('bytes_in', 0),
            data.get('bytes_out', 0),
            data.get('duration_ms', 0),
            data.get('latency_ms', 0),
            data.get('worker_id')
            )
        return {"status": "success", "stream": 2}
    except Exception as e:
        logger.error(f"Stream 2 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STREAM 3: WEB ERRORS
# ============================================================================

@app.post("/api/v1/errors/web/{port}")
async def receive_web_error(port: int, data: dict, token: str = Depends(verify_token)):
    """STREAM 3: Receive web error data from VPS"""
    try:
        async with db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO web_errors (timestamp, port, error_type, client_ip, error_message)
                VALUES ($1, $2, $3, $4, $5)
            """,
            data.get('timestamp'),
            port,
            data.get('error_type'),
            data.get('client_ip'),
            data.get('error_message')
            )
        return {"status": "success", "stream": 3}
    except Exception as e:
        logger.error(f"Stream 3 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STREAM 4: L2N ERRORS
# ============================================================================

@app.post("/api/v1/errors/l2n/{port}")
async def receive_l2n_error(port: int, data: dict, token: str = Depends(verify_token)):
    """STREAM 4: Receive L2N error data from VPS"""
    try:
        async with db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO l2n_errors (timestamp, port, error_type, backend_ip, error_message)
                VALUES ($1, $2, $3, $4, $5)
            """,
            data.get('timestamp'),
            port,
            data.get('error_type'),
            data.get('backend_ip'),
            data.get('error_message')
            )
        return {"status": "success", "stream": 4}
    except Exception as e:
        logger.error(f"Stream 4 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STREAM 5: WARNINGS
# ============================================================================

@app.post("/api/v1/warnings")
async def receive_warning(data: dict, token: str = Depends(verify_token)):
    """STREAM 5: Receive warning data from VPS"""
    try:
        async with db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO warnings (timestamp, port, warning_type, message, severity)
                VALUES ($1, $2, $3, $4, $5)
            """,
            data.get('timestamp'),
            data.get('port'),
            data.get('warning_type'),
            data.get('message'),
            data.get('severity', 'warning')
            )
        return {"status": "success", "stream": 5}
    except Exception as e:
        logger.error(f"Stream 5 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STREAM 6: SUCCEEDED ACCESS
# ============================================================================

@app.post("/api/v1/succeeded")
async def receive_succeeded(data: dict, token: str = Depends(verify_token)):
    """STREAM 6: Receive succeeded connection data from VPS"""
    try:
        async with db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO succeeded_access (timestamp, port, client_ip, client_port, backend_ip, backend_port, bytes_transferred, duration_ms)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            data.get('timestamp'),
            data.get('port'),
            data.get('client_ip'),
            data.get('client_port'),
            data.get('backend_ip'),
            data.get('backend_port'),
            data.get('bytes_transferred', 0),
            data.get('duration_ms', 0)
            )
        return {"status": "success", "stream": 6}
    except Exception as e:
        logger.error(f"Stream 6 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STREAM 7: PORT HEALTH (CLIENT → VPS)
# ============================================================================

@app.post("/api/v1/health/{port}")
async def receive_port_health(port: int, data: dict, token: str = Depends(verify_token)):
    """STREAM 7: Receive port health data"""
    try:
        async with db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO port_health (timestamp, port, status, latency_ms)
                VALUES ($1, $2, $3, $4)
            """,
            data.get('timestamp'),
            port,
            data.get('status'),
            data.get('latency_ms', 0)
            )
        return {"status": "success", "stream": 7}
    except Exception as e:
        logger.error(f"Stream 7 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STREAM 8: L2N HEALTH (VPS → BACKEND)
# ============================================================================

@app.post("/api/v1/health/l2n")
async def receive_l2n_health(data: dict, token: str = Depends(verify_token)):
    """STREAM 8: Receive L2N health data"""
    try:
        async with db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO l2n_health (timestamp, tunnel, tunnel_ip, tunnel_port, status, latency_ms)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
            data.get('timestamp'),
            data.get('tunnel', 'LocalToNet'),
            data.get('tunnel_ip'),
            data.get('tunnel_port'),
            data.get('status'),
            data.get('latency_ms', 0)
            )
        return {"status": "success", "stream": 8}
    except Exception as e:
        logger.error(f"Stream 8 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# QUERY ENDPOINTS (READ-ONLY, NO AUTH REQUIRED)
# ============================================================================

@app.get("/api/v1/query/web")
async def query_web(port: int = 8041, hours: int = 24, limit: int = 1000):
    """Query web connections"""
    try:
        table = f'web_p_{port}'
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT * FROM {table}
                WHERE timestamp > NOW() - INTERVAL '{hours} hours'
                ORDER BY timestamp DESC
                LIMIT {limit}
            """)
        return {"count": len(rows), "port": port, "data": [dict(row) for row in rows]}
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/query/l2n")
async def query_l2n(port: int = 8041, hours: int = 24):
    """Query L2N connection data"""
    try:
        table_name = f"l2n_p_{port}"
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT * FROM {table_name} WHERE timestamp > NOW() - INTERVAL '{hours} hours' ORDER BY timestamp DESC LIMIT 1000"
            )
        
        return {
            "stream": f"l2n_{port}",
            "count": len(rows),
            "hours": hours,
            "data": [dict(row) for row in rows]
        }
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/query/stats")
async def query_stats(hours: int = 24):
    """Query statistics summary"""
    try:
        async with db.pool.acquire() as conn:
            # Get stats for all ports
            rows = await conn.fetch(f"""
                SELECT 
                    8041 as port,
                    COUNT(*) as connections,
                    SUM(COALESCE(bytes_in, 0) + COALESCE(bytes_out, 0)) as total_bytes,
                    AVG(COALESCE(duration_ms, 0)) as avg_duration_ms
                FROM web_p_8041
                WHERE timestamp > NOW() - INTERVAL '{hours} hours'
                UNION ALL
                SELECT 
                    8047 as port,
                    COUNT(*) as connections,
                    SUM(COALESCE(bytes_in, 0) + COALESCE(bytes_out, 0)) as total_bytes,
                    AVG(COALESCE(duration_ms, 0)) as avg_duration_ms
                FROM web_p_8047
                WHERE timestamp > NOW() - INTERVAL '{hours} hours'
                UNION ALL
                SELECT 
                    8057 as port,
                    COUNT(*) as connections,
                    SUM(COALESCE(bytes_in, 0) + COALESCE(bytes_out, 0)) as total_bytes,
                    AVG(COALESCE(duration_ms, 0)) as avg_duration_ms
                FROM web_p_8057
                WHERE timestamp > NOW() - INTERVAL '{hours} hours'
            """)
        return {"stats": [dict(row) for row in rows]}
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/query/errors")
async def query_errors(hours: int = 24):
    """Query error data"""
    try:
        async with db.pool.acquire() as conn:
            web_errors = await conn.fetch(f"""
                SELECT * FROM web_errors
                WHERE timestamp > NOW() - INTERVAL '{hours} hours'
                ORDER BY timestamp DESC
                LIMIT 100
            """)
            l2n_errors = await conn.fetch(f"""
                SELECT * FROM l2n_errors
                WHERE timestamp > NOW() - INTERVAL '{hours} hours'
                ORDER BY timestamp DESC
                LIMIT 100
            """)
        return {
            "web_errors": [dict(row) for row in web_errors],
            "l2n_errors": [dict(row) for row in l2n_errors]
        }
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 90)
    logger.info("🚀 ENTERPRISE BACKEND API v3 FIXED - ALL 8 DATA STREAMS")
    logger.info("=" * 90)
    logger.info(f"💰 Listening on {API_HOST}:{API_PORT}")
    logger.info(f"📄 Receives from: VPS via LocalToNet (194.182.64.133:6921)")
    logger.info(f"💾 Database: PostgreSQL {DB_HOST}:{DB_PORT}/{DB_NAME}")
    logger.info("=" * 90)
    logger.info("\n퉰5 STREAMS:")
    logger.info("  1. Web connections POST /api/v1/web/{port}")
    logger.info("  2. L2N connections POST /api/v1/l2n/{port}")
    logger.info("  3. Web errors POST /api/v1/errors/web/{port}")
    logger.info("  4. L2N errors POST /api/v1/errors/l2n/{port}")
    logger.info("  5. Warnings POST /api/v1/warnings")
    logger.info("  6. Succeeded POST /api/v1/succeeded")
    logger.info("  7. Port health POST /api/v1/health/{port}")
    logger.info("  8. L2N health POST /api/v1/health/l2n")
    logger.info("=" * 90 + "\n")
    
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        workers=4,
        log_level="info"
    )
