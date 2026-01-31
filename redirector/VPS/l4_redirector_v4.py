#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║               L4 REDIRECTOR v4.0 - PRODUCTION FINAL                       ║
║          Enterprise-Grade Security & Performance Edition                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

Release: 2026-01-31
Version: 4.0.0-final
Compatible: Ubuntu 24.04 LTS + Python 3.12
Repository: github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System
"""

import asyncio
import logging
import os
import sys
import json
import secrets
import resource
import multiprocessing
import time
import socket
import psutil
import collections
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from aiohttp import web, ClientSession, ClientTimeout, TCPConnector
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION FROM ENVIRONMENT (FIX #1, #8)
# ════════════════════════════════════════════════════════════════════════════

LOCALTONET_IP = os.getenv("LOCALTONET_IP")
LOCALTONET_PORT = int(os.getenv("LOCALTONET_PORT", "6921"))
BACKEND_API_TOKEN = os.getenv("BACKEND_API_TOKEN")
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")

# FIX #2: Fail-fast validation
if not LOCALTONET_IP:
    sys.exit("FATAL: LOCALTONET_IP environment variable not set")
if not BACKEND_API_TOKEN:
    sys.exit("FATAL: BACKEND_API_TOKEN environment variable not set")
if not API_AUTH_TOKEN:
    sys.exit("FATAL: API_AUTH_TOKEN environment variable not set")

PORT_MAP_JSON = os.getenv("PORT_MAP")
if not PORT_MAP_JSON:
    sys.exit("FATAL: PORT_MAP environment variable not set")

try:
    PORT_MAP = json.loads(PORT_MAP_JSON)
    PORT_MAP = {int(k): (v[0], int(v[1])) for k, v in PORT_MAP.items()}
    for port, (target_ip, target_port) in PORT_MAP.items():
        if port < 1 or port > 65535 or target_port < 1 or target_port > 65535:
            raise ValueError(f"Invalid port numbers: {port}, {target_port}")
except (json.JSONDecodeError, ValueError, KeyError) as e:
    sys.exit(f"FATAL: Invalid PORT_MAP format: {e}")

MONITORED_PORTS = tuple(PORT_MAP.keys())
BACKEND_API_URL = f"http://{LOCALTONET_IP}:{LOCALTONET_PORT}"
LISTEN_IP = "0.0.0.0"

# Performance tuning
BATCH_SIZE_THRESHOLD = 100
BATCH_TIME_THRESHOLD = 5
BUFFER_SIZE = 65536
TCP_BACKLOG = 65535

# ════════════════════════════════════════════════════════════════════════════
# LOGGING
# ════════════════════════════════════════════════════════════════════════════

def setup_logging():
    log_dir = "/var/log/redirector"
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger('redirector_v4')
    logger.setLevel(logging.DEBUG)
    
    from logging.handlers import RotatingFileHandler
    
    fh = RotatingFileHandler(
        f"{log_dir}/l4_redirector_v4.log",
        maxBytes=100*1024*1024,
        backupCount=10
    )
    fh.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = setup_logging()

# ════════════════════════════════════════════════════════════════════════════
# CIRCUIT BREAKER (FIX #7)
# ════════════════════════════════════════════════════════════════════════════

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60, success_threshold=2):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
    
    def can_proceed(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("🔄 Circuit breaker: OPEN → HALF_OPEN")
                return True
            return False
        return True
    
    def record_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                logger.info("✅ Circuit breaker: HALF_OPEN → CLOSED")
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("⚠️ Circuit breaker: HALF_OPEN → OPEN")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"🔴 Circuit breaker: CLOSED → OPEN ({self.failure_count} failures)")
    
    def get_stats(self) -> dict:
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count
        }

backend_circuit_breaker = CircuitBreaker()

# ════════════════════════════════════════════════════════════════════════════
# SHARED STATE
# ════════════════════════════════════════════════════════════════════════════

manager = multiprocessing.Manager()
WORKER_STATS = manager.dict()
GLOBAL_STATS = manager.dict({
    "backend_pushes": 0,
    "backend_push_failures": 0,
    "total_connections": 0,
    "total_bytes_in": 0,
    "total_bytes_out": 0,
    "circuit_breaker_drops": 0,
})
CONNECTION_BUFFERS = manager.dict()
stats_lock = manager.Lock()

def init_buffers():
    for port in MONITORED_PORTS:
        CONNECTION_BUFFERS[port] = {
            "web": manager.list(),
            "l2n": manager.list(),
            "last_flush": time.time()
        }

# ════════════════════════════════════════════════════════════════════════════
# HTTP SESSION (FIX #9)
# ════════════════════════════════════════════════════════════════════════════

http_session: Optional[ClientSession] = None

async def init_http_session():
    global http_session
    connector = TCPConnector(
        limit=100,
        limit_per_host=50,
        ttl_dns_cache=300,
        force_close=False,
    )
    timeout = ClientTimeout(total=30, connect=5, sock_read=30)
    http_session = ClientSession(
        connector=connector,
        timeout=timeout,
        headers={
            "Authorization": f"Bearer {BACKEND_API_TOKEN}",
            "Content-Type": "application/json"
        }
    )
    logger.info("✅ HTTP session initialized")

async def close_http_session():
    global http_session
    if http_session:
        await http_session.close()
        logger.info("🛑 HTTP session closed")

# ════════════════════════════════════════════════════════════════════════════
# API CLIENT
# ════════════════════════════════════════════════════════════════════════════

async def push_to_backend(endpoint: str, data: Any, retry_count: int = 0) -> bool:
    if not http_session:
        return False
    
    if not backend_circuit_breaker.can_proceed():
        with stats_lock:
            GLOBAL_STATS["backend_push_failures"] += 1
            GLOBAL_STATS["circuit_breaker_drops"] += 1
        return False
    
    try:
        url = f"{BACKEND_API_URL}{endpoint}"
        async with http_session.post(url, json=data) as resp:
            if resp.status == 200:
                backend_circuit_breaker.record_success()
                with stats_lock:
                    GLOBAL_STATS["backend_pushes"] += 1
                return True
            else:
                backend_circuit_breaker.record_failure()
                with stats_lock:
                    GLOBAL_STATS["backend_push_failures"] += 1
                if retry_count < 2:
                    await asyncio.sleep(0.1)
                    return await push_to_backend(endpoint, data, retry_count + 1)
                return False
    except Exception as e:
        backend_circuit_breaker.record_failure()
        with stats_lock:
            GLOBAL_STATS["backend_push_failures"] += 1
        if retry_count < 2:
            await asyncio.sleep(0.1)
            return await push_to_backend(endpoint, data, retry_count + 1)
        return False

# ════════════════════════════════════════════════════════════════════════════
# REQUEST BATCHING (FIX #10)
# ════════════════════════════════════════════════════════════════════════════

async def push_buffered(stream_type: str, port: int, data: Dict[str, Any]):
    with stats_lock:
        if port not in CONNECTION_BUFFERS:
            return
        CONNECTION_BUFFERS[port][stream_type].append(data)
        buffer_size = len(CONNECTION_BUFFERS[port][stream_type])
        elapsed = time.time() - CONNECTION_BUFFERS[port]["last_flush"]
        should_flush = buffer_size >= BATCH_SIZE_THRESHOLD or elapsed >= BATCH_TIME_THRESHOLD
    
    if should_flush:
        with stats_lock:
            items = list(CONNECTION_BUFFERS[port][stream_type])
            CONNECTION_BUFFERS[port][stream_type] = manager.list()
            CONNECTION_BUFFERS[port]["last_flush"] = time.time()
        
        if items:
            await push_to_backend(f"/api/v1/{stream_type}/{port}", items)

# ════════════════════════════════════════════════════════════════════════════
# TCP HANDLER
# ════════════════════════════════════════════════════════════════════════════

async def tcp_handler(client_reader, client_writer, port, target_ip, target_port, worker_id):
    client_addr = client_writer.get_extra_info('peername')
    client_ip = client_addr[0] if client_addr else 'unknown'
    client_port = client_addr[1] if client_addr else 0
    connection_start = time.time()
    backend_latency = 0
    
    try:
        # Connect to backend
        backend_start = time.time()
        backend_reader, backend_writer = await asyncio.wait_for(
            asyncio.open_connection(target_ip, target_port),
            timeout=30
        )
        backend_latency = int((time.time() - backend_start) * 1000)
        
        # Bidirectional forwarding
        async def pipe(reader, writer):
            try:
                while True:
                    data = await asyncio.wait_for(reader.read(BUFFER_SIZE), timeout=300)
                    if not data:
                        break
                    writer.write(data)
                    await writer.drain()
            except:
                pass
        
        await asyncio.gather(
            pipe(client_reader, backend_writer),
            pipe(backend_reader, client_writer),
            return_exceptions=True
        )
        
        duration_ms = int((time.time() - connection_start) * 1000)
        
        # Batched push
        await push_buffered("web", port, {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "client_ip": client_ip,
            "client_port": client_port,
            "duration_ms": duration_ms,
            "worker_id": worker_id
        })
        
        await push_buffered("l2n", port, {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "backend_ip": target_ip,
            "backend_port": target_port,
            "latency_ms": backend_latency,
            "duration_ms": duration_ms,
            "worker_id": worker_id
        })
        
    except Exception as e:
        logger.error(f"[{port}] Handler error: {e}")
    finally:
        try:
            client_writer.close()
            await client_writer.wait_closed()
        except:
            pass

async def tcp_worker(port, target_ip, target_port, worker_id):
    logger.info(f"✅ [PORT {port}] TCP worker {worker_id} started")
    server = await asyncio.start_server(
        lambda r, w: tcp_handler(r, w, port, target_ip, target_port, worker_id),
        LISTEN_IP, port, backlog=TCP_BACKLOG, reuse_address=True, reuse_port=True
    )
    async with server:
        await server.serve_forever()

# ════════════════════════════════════════════════════════════════════════════
# HTTP API (FIX #5: TIMING ATTACK PROTECTION)
# ════════════════════════════════════════════════════════════════════════════

@web.middleware
async def auth_middleware(request, handler):
    auth_header = request.headers.get("Authorization")
    expected = f"Bearer {API_AUTH_TOKEN}"
    # FIX #5: Constant-time comparison
    if not auth_header or not secrets.compare_digest(auth_header, expected):
        await asyncio.sleep(0.1 + secrets.randbelow(100) / 1000)
        return web.json_response({"error": "unauthorized"}, status=401)
    
    return await handler(request)

async def health_handler(request):
    return web.json_response({
        "status": "ok",
        "version": "4.0.0-final",
        "timestamp": datetime.utcnow().isoformat()
    })

async def status_handler(request):
    with stats_lock:
        return web.json_response({
            "version": "4.0.0-final",
            "global": dict(GLOBAL_STATS),
            "circuit_breaker": backend_circuit_breaker.get_stats(),
            "timestamp": datetime.utcnow().isoformat()
        })

async def start_http_server():
    await init_http_session()
    app = web.Application(middlewares=[auth_middleware])
    app.router.add_get("/health", health_handler)
    app.router.add_get("/status", status_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 9090, reuse_address=True)
    await site.start()
    logger.info("✅ HTTP monitoring server listening on :9090")
    
    try:
        await asyncio.Event().wait()
    finally:
        await close_http_session()

# ════════════════════════════════════════════════════════════════════════════
# PROCESS ENTRY POINTS
# ════════════════════════════════════════════════════════════════════════════

def run_tcp_worker(port, target_ip, target_port, worker_id):
    asyncio.run(tcp_worker(port, target_ip, target_port, worker_id))

def run_http_server():
    asyncio.run(start_http_server())

# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    if os.geteuid() != 0:
        raise SystemExit("Run as root")
    
    init_buffers()
    
    logger.info("=" * 100)
    logger.info("🚀 L4 REDIRECTOR v4.0 PRODUCTION FINAL")
    logger.info("=" * 100)
    logger.info(f"📡 Backend API: {BACKEND_API_URL}")
    logger.info(f"🔧 Ports: {MONITORED_PORTS}")
    logger.info("=" * 100)
    
    processes = []
    cpu_count = os.cpu_count() or 2
    
    try:
        # HTTP server
        p = multiprocessing.Process(target=run_http_server)
        p.daemon = False
        p.start()
        processes.append(p)
        time.sleep(0.5)
        
        # TCP workers
        for port, (target_ip, target_port) in PORT_MAP.items():
            for i in range(cpu_count * 4):
                worker_id = f"tcp_{port}_{i}"
                p = multiprocessing.Process(
                    target=run_tcp_worker,
                    args=(port, target_ip, target_port, worker_id)
                )
                p.daemon = False
                p.start()
                processes.append(p)
                time.sleep(0.05)
        
        logger.info(f"✅ All {len(processes)} processes started")
        
        # Wait forever
        for p in processes:
            p.join()
    
    except KeyboardInterrupt:
        logger.info("⏹️  Shutting down...")
    finally:
        for p in processes:
            if p.is_alive():
                p.terminate()
        for p in processes:
            p.join(timeout=5)
            if p.is_alive():
                p.kill()
        logger.info("✅ All processes stopped")

if __name__ == '__main__':
    main()
