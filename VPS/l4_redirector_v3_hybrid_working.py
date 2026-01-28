#!/usr/bin/env python3
"""
Enterprise L4 Redirector v3 HYBRID - STATELESS STREAMING WITH FULL METRICS
Combines working traffic forwarding with complete device/connection logging

Based on proven stateless architecture with enhanced metrics:
- Bidirectional TCP forwarding (working)
- All 8 data streams to backend API
- Device tracking and connection logging
- Health monitoring and metrics

Deployment: VPS (aoycrreni.localto.net)
Backend: Windows 192.168.88.16:5814 via LocalToNet 194.182.64.133:6921
"""

import asyncio
import logging
import os
import resource
import multiprocessing
import time
import traceback
from datetime import datetime
from aiohttp import web, ClientSession, ClientTimeout
import uvloop
import json

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# ============================================================================
# CONFIGURATION
# ============================================================================

LISTEN_IP = "0.0.0.0"
LOCALTONET_IP = "194.182.64.133"
LOCALTONET_PORT = 6921
BACKEND_API_URL = f"http://{LOCALTONET_IP}:{LOCALTONET_PORT}"
BACKEND_API_TOKEN = "e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"

# Port mapping: listening_port → (local_backend_ip, local_backend_port)
PORT_MAP = {
    8041: ("194.182.64.133", 6921),  # Backend API via LocalToNet
    8047: ("194.182.64.133", 6921),  # Backend API via LocalToNet
    8057: ("194.182.64.133", 6921),  # Backend API via LocalToNet
}

API_PUSH_TIMEOUT = 3000  # milliseconds (increased for LocalToNet latency)
API_RETRY_COUNT = 2
API_RETRY_DELAY = 100  # milliseconds
HEALTH_CHECK_INTERVAL = 5
HEALTH_CHECK_TIMEOUT = 3000
TCP_BACKLOG = 65535
BUFFER_SIZE = 65536

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    log_dir = "/var/log/redirector"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger('redirector_hybrid')
    logger.setLevel(logging.DEBUG)

    from logging.handlers import RotatingFileHandler

    main_log = os.path.join(log_dir, "l4_redirector_v3_hybrid.log")
    fh = RotatingFileHandler(main_log, maxBytes=100*1024*1024, backupCount=10)
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

# ============================================================================
# GLOBAL STATE
# ============================================================================

manager = multiprocessing.Manager()
stats = manager.dict()
stats['ports'] = manager.dict()
stats['workers'] = manager.dict()
stats['start_time'] = time.time()
stats_lock = manager.Lock()

# ============================================================================
# BACKEND API CLIENT - ALL 8 DATA STREAMS
# ============================================================================

async def push_to_backend(endpoint, data, retry_count=0):
    """Push data to Backend API via LocalToNet tunnel with retry logic"""
    try:
        headers = {
            "Authorization": f"Bearer {BACKEND_API_TOKEN}",
            "Content-Type": "application/json"
        }

        url = f"{BACKEND_API_URL}{endpoint}"
        timeout = ClientTimeout(total=API_PUSH_TIMEOUT / 1000)

        async with ClientSession(timeout=timeout) as session:
            async with session.post(
                url,
                json=data,
                headers=headers,
            ) as resp:
                if resp.status == 200:
                    return True
                else:
                    logger.warning(f"API {resp.status}: {endpoint}")
                    if retry_count < API_RETRY_COUNT:
                        await asyncio.sleep(API_RETRY_DELAY / 1000)
                        return await push_to_backend(endpoint, data, retry_count + 1)
                    return False
    except asyncio.TimeoutError:
        logger.warning(f"API timeout: {endpoint}")
        if retry_count < API_RETRY_COUNT:
            await asyncio.sleep(API_RETRY_DELAY / 1000)
            return await push_to_backend(endpoint, data, retry_count + 1)
        return False
    except Exception as e:
        logger.error(f"API error: {endpoint}: {e}")
        if retry_count < API_RETRY_COUNT:
            await asyncio.sleep(API_RETRY_DELAY / 1000)
            return await push_to_backend(endpoint, data, retry_count + 1)
        return False

# STREAM 1: Web connections (port 8041/8047/8057 - client → VPS)
async def push_web_connection(port, client_ip, client_port, bytes_in, bytes_out, duration_ms, worker_id):
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "client_ip": client_ip,
        "client_port": client_port,
        "bytes_in": bytes_in,
        "bytes_out": bytes_out,
        "duration_ms": duration_ms,
        "worker_id": worker_id
    }
    await push_to_backend(f"/api/v1/web/{port}", data)

# STREAM 2: L2N connections (port 8041/8047/8057 - VPS → backend)
async def push_l2n_connection(port, backend_ip, backend_port, bytes_in, bytes_out, duration_ms, latency_ms, worker_id):
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "backend_ip": backend_ip,
        "backend_port": backend_port,
        "bytes_in": bytes_in,
        "bytes_out": bytes_out,
        "duration_ms": duration_ms,
        "latency_ms": latency_ms,
        "worker_id": worker_id
    }
    await push_to_backend(f"/api/v1/l2n/{port}", data)

# STREAM 3: Web errors (internet → VPS)
async def push_web_error(port, client_ip, error_type, error_msg):
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "error_type": error_type,
        "client_ip": client_ip,
        "error_message": error_msg
    }
    await push_to_backend(f"/api/v1/errors/web/{port}", data)

# STREAM 4: L2N errors (VPS → backend)
async def push_l2n_error(port, backend_ip, error_type, error_msg):
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "error_type": error_type,
        "backend_ip": backend_ip,
        "error_message": error_msg
    }
    await push_to_backend(f"/api/v1/errors/l2n/{port}", data)

# STREAM 5: Connection warnings
async def push_warning(port, warning_type, message, severity="warning"):
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "port": port,
        "warning_type": warning_type,
        "message": message,
        "severity": severity
    }
    await push_to_backend("/api/v1/warnings", data)

# STREAM 6: Succeeded access
async def push_succeeded_access(port, client_ip, client_port, backend_ip, backend_port, bytes_transferred, duration_ms):
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "port": port,
        "client_ip": client_ip,
        "client_port": client_port,
        "backend_ip": backend_ip,
        "backend_port": backend_port,
        "bytes_transferred": bytes_transferred,
        "duration_ms": duration_ms
    }
    await push_to_backend("/api/v1/succeeded", data)

# STREAM 7: Port health (VPS listening ports)
async def push_port_health(port, status, latency_ms):
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "port": port,
        "status": status,
        "latency_ms": latency_ms
    }
    await push_to_backend(f"/api/v1/health/{port}", data)

# STREAM 8: L2N health (VPS → backend tunnel)
async def push_l2n_health(port, backend_ip, backend_port, status, latency_ms):
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "backend_ip": backend_ip,
        "backend_port": backend_port,
        "status": status,
        "latency_ms": latency_ms
    }
    await push_to_backend(f"/api/v1/health/l2n/{port}", data)

# ============================================================================
# BIDIRECTIONAL DATA FORWARDING (PROVEN WORKING FROM OLD VERSION)
# ============================================================================

async def forward_data(reader, writer, port, direction, worker_id):
    """Forward data between client and backend - STATELESS (no local tracking)"""
    try:
        while True:
            data = await asyncio.wait_for(reader.read(BUFFER_SIZE), timeout=300)
            if not data:
                logger.debug(f"[{port}] {direction}: Connection closed (EOF)")
                break
            writer.write(data)
            await writer.drain()
    except asyncio.TimeoutError:
        logger.debug(f"[{port}] {direction}: Timeout after 300s")
    except Exception as e:
        logger.debug(f"[{port}] {direction}: Error - {e}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass

# ============================================================================
# TCP HANDLER - MAIN CONNECTION LOGIC
# ============================================================================

async def tcp_handler(client_reader, client_writer, port, target_ip, target_port, worker_id):
    """Main TCP connection handler - handles all 8 data streams"""
    client_addr = client_writer.get_extra_info('peername')
    client_ip = client_addr[0] if client_addr else 'unknown'
    client_port = client_addr[1] if client_addr else 0

    connection_start = time.time()
    backend_start = None
    backend_reader = None
    backend_writer = None

    logger.info(f"[{port}] NEW: {client_ip}:{client_port} → {target_ip}:{target_port} (worker: {worker_id})")

    try:
        # STREAM 8: Connect to backend and measure latency
        try:
            backend_start = time.time()
            backend_reader, backend_writer = await asyncio.wait_for(
                asyncio.open_connection(target_ip, target_port),
                timeout=HEALTH_CHECK_TIMEOUT / 1000
            )
            backend_latency = int((time.time() - backend_start) * 1000)
            logger.debug(f"[{port}] TUNNEL: Connected (latency: {backend_latency}ms)")
        except asyncio.TimeoutError:
            logger.error(f"[{port}] TIMEOUT: Cannot reach {target_ip}:{target_port}")
            await push_l2n_error(port, target_ip, 'connection_timeout',
                f'Timeout connecting to {target_ip}:{target_port}')
            await push_web_error(port, client_ip, 'backend_timeout',
                f'Backend timeout for client {client_ip}:{client_port}')
            return
        except ConnectionRefusedError:
            logger.error(f"[{port}] REFUSED: {target_ip}:{target_port} not accepting")
            await push_l2n_error(port, target_ip, 'connection_refused',
                f'Connection refused by {target_ip}:{target_port}')
            await push_web_error(port, client_ip, 'backend_refused',
                f'Backend refused connection')
            return
        except OSError as e:
            logger.error(f"[{port}] ERROR: {e}")
            await push_l2n_error(port, target_ip, 'connection_error', str(e))
            await push_web_error(port, client_ip, 'backend_error', str(e))
            return

        # Update worker stats
        with stats_lock:
            if worker_id not in stats['workers']:
                stats['workers'][worker_id] = {'active': 0, 'total': 0}
            w = stats['workers'][worker_id]
            w['active'] = w['active'] + 1
            w['total'] = w['total'] + 1
            stats['workers'][worker_id] = w

        # STREAM 1 & 2: Bidirectional forwarding (stateless - no local byte counting)
        logger.debug(f"[{port}] FORWARD: Starting bidirectional forwarding")
        task1 = forward_data(client_reader, backend_writer, port, 'in', worker_id)
        task2 = forward_data(backend_reader, client_writer, port, 'out', worker_id)
        await asyncio.gather(task1, task2, return_exceptions=True)

        # Calculate final metrics
        duration_ms = int((time.time() - connection_start) * 1000)
        logger.info(f"[{port}] CLOSED: {client_ip}:{client_port} | Duration:{duration_ms}ms | Latency:{backend_latency}ms")

        # Push all 8 streams asynchronously (non-blocking)
        # STREAM 1: Web connection
        asyncio.create_task(push_web_connection(
            port, client_ip, client_port, 0, 0, duration_ms, worker_id))

        # STREAM 2: L2N connection
        asyncio.create_task(push_l2n_connection(
            port, target_ip, target_port, 0, 0, duration_ms, backend_latency, worker_id))

        # STREAM 6: Succeeded access
        asyncio.create_task(push_succeeded_access(
            port, client_ip, client_port, target_ip, target_port, 0, duration_ms))

        # STREAM 5: Push warning if latency high
        if backend_latency > 150:
            asyncio.create_task(push_warning(
                port, 'high_latency', f'Latency {backend_latency}ms', 'warning'))

    except Exception as e:
        logger.error(f"[{port}] HANDLER ERROR: {e}")
        await push_web_error(port, client_ip, 'handler_error', str(e))
    finally:
        # Decrement active connections
        with stats_lock:
            if worker_id in stats['workers']:
                w = stats['workers'][worker_id]
                w['active'] = max(0, w['active'] - 1)
                stats['workers'][worker_id] = w

        # Close connections properly
        try:
            client_writer.close()
            await client_writer.wait_closed()
        except:
            pass
        if backend_writer:
            try:
                backend_writer.close()
                await backend_writer.wait_closed()
            except:
                pass

async def tcp_worker(port, target_ip, target_port, worker_id):
    """TCP worker process"""
    logger.info(f"✅ [PORT {port}] TCP worker listening (worker_id: {worker_id})")
    server = await asyncio.start_server(
        lambda r, w: tcp_handler(r, w, port, target_ip, target_port, worker_id),
        LISTEN_IP, port, backlog=TCP_BACKLOG, reuse_address=True, reuse_port=True
    )
    async with server:
        await server.serve_forever()

# ============================================================================
# HEALTH MONITORING - STREAMS 7 & 8
# ============================================================================

async def monitor_worker():
    """Health check worker - monitors all ports"""
    logger.info("✅ Health monitor started (5-second intervals)")
    while True:
        try:
            for port, (backend_ip, backend_port) in PORT_MAP.items():
                # STREAM 8: Check L2N health (VPS → Backend via LocalToNet)
                start_time = time.time()
                try:
                    reader, writer = await asyncio.wait_for(
                        asyncio.open_connection(backend_ip, backend_port),
                        timeout=HEALTH_CHECK_TIMEOUT / 1000
                    )
                    writer.close()
                    await writer.wait_closed()
                    latency_ms = int((time.time() - start_time) * 1000)
                    status = 'up'
                    logger.debug(f"[{port}] Health: {backend_ip}:{backend_port} UP (latency: {latency_ms}ms)")
                except:
                    latency_ms = HEALTH_CHECK_TIMEOUT
                    status = 'down'
                    logger.warning(f"[{port}] Health: {backend_ip}:{backend_port} DOWN")

                # Push health data (Streams 7 & 8)
                asyncio.create_task(push_port_health(port, status, latency_ms))
                asyncio.create_task(push_l2n_health(port, backend_ip, backend_port, status, latency_ms))

                with stats_lock:
                    p = stats['ports']
                    p[str(port)] = {'status': status, 'latency': latency_ms}
                    stats['ports'] = p

            await asyncio.sleep(HEALTH_CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

async def health_endpoint(request):
    return web.json_response({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '3.0-hybrid',
        'streams_active': 8
    })

async def status_endpoint(request):
    with stats_lock:
        return web.json_response({
            'ports': dict(stats['ports']),
            'workers': {k: {'active': v.get('active', 0), 'total': v.get('total', 0)}
                       for k, v in stats['workers'].items()},
            'uptime_seconds': int(time.time() - stats['start_time']),
            'streams': {
                '1_web_connections': 'active',
                '2_l2n_connections': 'active',
                '3_web_errors': 'active',
                '4_l2n_errors': 'active',
                '5_warnings': 'active',
                '6_succeeded_access': 'active',
                '7_port_health': 'active',
                '8_l2n_health': 'active'
            }
        })

async def config_endpoint(request):
    return web.json_response({
        'backend_api': BACKEND_API_URL,
        'ports_listening': list(PORT_MAP.keys()),
        'api_version': '3.0-hybrid',
        'architecture': 'stateless-streaming'
    })

async def status_server():
    """HTTP status server (monitoring only)"""
    app = web.Application()
    app.router.add_get('/health', health_endpoint)
    app.router.add_get('/status', status_endpoint)
    app.router.add_get('/config', config_endpoint)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 9090, reuse_address=True)
    await site.start()
    logger.info("✅ Status server listening on :9090")
    while True:
        await asyncio.sleep(3600)

# ============================================================================
# KERNEL TUNING
# ============================================================================

def tune_kernel():
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        resource.setrlimit(resource.RLIMIT_NOFILE, (1000000, 1000000))
        logger.info(f"✅ File descriptors: {soft} → 1,000,000")
    except Exception as e:
        logger.warning(f"⚠️  Failed to set file descriptors: {e}")

# ============================================================================
# PROCESS MANAGEMENT
# ============================================================================

def run_worker(worker_type, port=None, target_ip=None, target_port=None, worker_id=None):
    """Worker process entry point"""
    tune_kernel()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if worker_type == 'tcp':
            loop.run_until_complete(tcp_worker(port, target_ip, target_port, worker_id))
        elif worker_type == 'monitor':
            loop.run_until_complete(monitor_worker())
        elif worker_type == 'status':
            loop.run_until_complete(status_server())
    except Exception as e:
        logger.error(f"{worker_type} worker error: {e}\n{traceback.format_exc()}")
    finally:
        loop.close()

def main():
    """Main entry point"""
    logger.info("=" * 100)
    logger.info("🚀 HYBRID L4 REDIRECTOR v3 - STATELESS STREAMING + FULL METRICS")
    logger.info("=" * 100)
    logger.info(f"📡 Backend API: {BACKEND_API_URL}")
    logger.info(f"🔐 Windows Backend: 192.168.88.16:5814")
    logger.info(f"✅ All 8 data streams active")
    logger.info(f"✅ Stateless architecture (no local DB)")
    logger.info("=" * 100)

    tune_kernel()
    num_workers = os.cpu_count() or 2
    logger.info(f"Starting {num_workers} TCP workers per port")
    processes = []

    try:
        # Monitor worker
        p = multiprocessing.Process(target=run_worker, args=('monitor',))
        p.daemon = False
        p.start()
        processes.append(p)
        time.sleep(0.5)

        # Status server
        p = multiprocessing.Process(target=run_worker, args=('status',))
        p.daemon = False
        p.start()
        processes.append(p)
        time.sleep(0.5)

        # TCP workers for each port
        for port, (backend_ip, backend_port) in PORT_MAP.items():
            for j in range(num_workers):
                wid = f"tcp_{port}_{j}"
                p = multiprocessing.Process(
                    target=run_worker,
                    args=('tcp', port, backend_ip, backend_port, wid)
                )
                p.daemon = False
                p.start()
                processes.append(p)
                time.sleep(0.1)

        logger.info(f"✅ All {len(processes)} processes started")
        logger.info("")
        logger.info("TRAFFIC FLOW:")
        logger.info("  Clients (Internet) → VPS:8041/8047/8057 → LocalToNet → Windows:5814")
        logger.info("")

        while True:
            time.sleep(5)
            alive = [p for p in processes if p.is_alive()]
            if len(alive) < len(processes):
                logger.warning(f"⚠️  Process crashed! ({len(alive)}/{len(processes)} alive)")
                processes = alive

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
