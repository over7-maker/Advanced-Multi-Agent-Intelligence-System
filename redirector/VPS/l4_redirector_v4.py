#!/usr/bin/env python3
"""
L4 REDIRECTOR v4.0 - EMERGENCY BACKEND PUSH FIX
"""

import asyncio
import aiohttp
import json
import socket
import signal
import os
from loguru import logger
from collections import defaultdict
from datetime import datetime

# ==================== CONFIGURATION ====================
BACKEND_API_TOKEN = os.getenv("BACKEND_API_TOKEN", "")
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "")
LOCALTONET_IP = os.getenv("LOCALTONET_IP", "")
LOCALTONET_PORT = int(os.getenv("LOCALTONET_PORT", 1))
PORT_MAP_STR = os.getenv("PORT_MAP", "{}")
PORT_MAP = json.loads(PORT_MAP_STR)

# ✅ CRITICAL FIX: Changed from /api/push to /connections
BACKEND_API_URL = f"http://{LOCALTONET_IP}:{LOCALTONET_PORT}/connections"
HTTP_MONITOR_PORT = 9090

logger.info("=" * 100)
logger.info("🚀 L4 REDIRECTOR v4.0 PRODUCTION FINAL")
logger.info("=" * 100)
logger.info(f"📡 Backend API: {BACKEND_API_URL}")
logger.info(f"🔧 Ports: {tuple(PORT_MAP.keys())}")
logger.info("=" * 100)

# ==================== GLOBAL STATS ====================
stats = {
    "total_connections": 0,
    "backend_pushes": 0,
    "backend_push_failures": 0,
    "by_port": defaultdict(lambda: {
        "connections": 0,
        "bytes_sent": 0,
        "bytes_received": 0
    })
}

# ==================== HTTP SESSION ====================
http_session = None

async def init_http_session():
    global http_session
    timeout = aiohttp.ClientTimeout(total=10, connect=5)
    http_session = aiohttp.ClientSession(timeout=timeout)
    logger.info("✅ HTTP session initialized")

async def close_http_session():
    global http_session
    if http_session:
        await http_session.close()

# ==================== BACKEND PUSH ====================
async def push_to_backend(client_ip: str, client_port: int, frontend_port: int, backend_host: str, backend_port: int):
    """Push connection metadata to Windows backend API"""

    # ✅ CRITICAL FIX: INCREMENT STATS IMMEDIATELY
    stats["total_connections"] += 1
    stats["by_port"][str(frontend_port)]["connections"] += 1

    payload = {
        "client_ip": client_ip,
        "client_port": client_port,
        "frontend_port": frontend_port,
        "backend_host": backend_host,
        "backend_port": backend_port,
        "timestamp": datetime.utcnow().isoformat()
    }

    headers = {
        "Authorization": f"Bearer {BACKEND_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        async with http_session.post(BACKEND_API_URL, json=payload, headers=headers) as resp:
            if resp.status in (200, 201):
                stats["backend_pushes"] += 1
                logger.debug(f"✅ Backend push: {client_ip}:{client_port} → {backend_host}:{backend_port}")
            else:
                stats["backend_push_failures"] += 1
                logger.warning(f"⚠️  Backend push failed: HTTP {resp.status}")
    except asyncio.TimeoutError:
        stats["backend_push_failures"] += 1
        logger.warning("⚠️  Backend push timeout")
    except Exception as e:
        stats["backend_push_failures"] += 1
        logger.warning(f"⚠️  Backend push error: {e}")

# ==================== TCP FORWARDING ====================
async def forward_data(reader, writer, direction: str, frontend_port: int):
    """Forward data bidirectionally"""
    try:
        while True:
            data = await reader.read(8192)
            if not data:
                break

            writer.write(data)
            await writer.drain()

            # Track bytes
            if direction == "client_to_backend":
                stats["by_port"][str(frontend_port)]["bytes_sent"] += len(data)
            else:
                stats["by_port"][str(frontend_port)]["bytes_received"] += len(data)

    except (ConnectionResetError, BrokenPipeError):
        pass
    except Exception as e:
        logger.debug(f"Forward error ({direction}): {e}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass

async def handle_client(client_reader, client_writer, frontend_port: int, backend_host: str, backend_port: int):
    """Handle individual client connection with L4 TCP forwarding"""

    client_addr = client_writer.get_extra_info('peername')
    client_ip = client_addr[0] if client_addr else "unknown"
    client_port = client_addr[1] if client_addr else 0

    logger.info(f"[{frontend_port}] Client connected from {client_ip}:{client_port}, connecting to {backend_host}:{backend_port}")

    # ✅ CRITICAL FIX: PUSH TO BACKEND IMMEDIATELY (DON'T WAIT)
    asyncio.create_task(push_to_backend(client_ip, client_port, frontend_port, backend_host, backend_port))

    try:
        # Connect to backend
        backend_reader, backend_writer = await asyncio.wait_for(
            asyncio.open_connection(backend_host, backend_port),
            timeout=10
        )

        # Bidirectional forwarding
        await asyncio.gather(
            forward_data(client_reader, backend_writer, "client_to_backend", frontend_port),
            forward_data(backend_reader, client_writer, "backend_to_client", frontend_port),
            return_exceptions=True
        )

    except asyncio.TimeoutError:
        logger.warning(f"[{frontend_port}] Backend connection timeout: {backend_host}:{backend_port}")
    except Exception as e:
        logger.warning(f"[{frontend_port}] Connection error: {e}")
    finally:
        try:
            client_writer.close()
            await client_writer.wait_closed()
        except:
            pass

# ==================== TCP WORKERS ====================
async def tcp_worker(port: int, backend_host: str, backend_port: int, worker_id: int):
    """TCP worker process for specific port"""

    async def accept_client(reader, writer):
        await handle_client(reader, writer, port, backend_host, backend_port)

    server = await asyncio.start_server(accept_client, "0.0.0.0", port, reuse_port=True)
    logger.info(f"✅ [PORT {port}] TCP worker tcp_{port}_{worker_id} started")

    async with server:
        await server.serve_forever()

# ==================== HTTP MONITORING ====================
async def http_status_handler(request):
    """HTTP status endpoint"""

    # Auth check
    auth_header = request.headers.get("Authorization", "")
    if auth_header != f"Bearer {API_AUTH_TOKEN}":
        return aiohttp.web.json_response({"error": "unauthorized"}, status=401)

    response = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "global": {
            "total_connections": stats["total_connections"],
            "backend_pushes": stats["backend_pushes"],
            "backend_push_failures": stats["backend_push_failures"]
        },
        "by_port": dict(stats["by_port"])
    }

    return aiohttp.web.json_response(response)

async def http_server():
    """HTTP monitoring server"""
    app = aiohttp.web.Application()
    app.router.add_get("/status", http_status_handler)

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()

    site = aiohttp.web.TCPSite(runner, "0.0.0.0", HTTP_MONITOR_PORT)
    await site.start()

    logger.info(f"✅ HTTP monitoring server listening on :{HTTP_MONITOR_PORT}")

# ==================== MAIN ====================
async def main():
    await init_http_session()

    tasks = []

    # Start HTTP monitor
    tasks.append(asyncio.create_task(http_server()))

    # Start TCP workers (5 per port)
    for port_str, backend_info in PORT_MAP.items():
        port = int(port_str)
        backend_host, backend_port = backend_info

        for worker_id in range(5):
            tasks.append(asyncio.create_task(tcp_worker(port, backend_host, backend_port, worker_id)))

    # Wait for all tasks
    await asyncio.gather(*tasks, return_exceptions=True)

def shutdown_handler(signum, frame):
    logger.info("🛑 Shutdown signal received")
    asyncio.create_task(close_http_session())
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
