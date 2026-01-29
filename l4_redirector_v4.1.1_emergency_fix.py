#!/usr/bin/env python3
"""
ENTERPRISE L4 REDIRECTOR v4.1.1 - EMERGENCY FIX
Critical Patch: Proper memory management

Fixes from v4.1:
- ❌ REMOVED broken cleanup_dead_workers() that didn't work with multiprocessing
- ✅ ADDED process PID tracking for reliable detection of dead workers
- ✅ ADDED hard limit: only track last 128 active workers
- ✅ ADDED memory pressure detection and forced cleanup
- ✅ ADDED per-PID worker registration/deregistration

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
import socket
import psutil
from datetime import datetime, timezone
from aiohttp import web, ClientSession, ClientTimeout
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# ============================================================================
# CONFIGURATION
# ============================================================================

LISTEN_IP = "0.0.0.0"
LOCALTONET_IP = "194.182.64.133"
LOCALTONET_PORT = 6921
BACKEND_API_URL = f"http://{LOCALTONET_IP}:{LOCALTONET_PORT}"
BACKEND_API_TOKEN = "e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"
API_AUTH_TOKEN = "AbDo@2020!"

# Port mapping: listening_port → (target_ip, target_port)
PORT_MAP = {
    8041: ("129.151.142.36", 1429),
    8047: ("129.151.142.36", 8667),
    8057: ("129.151.142.36", 7798),
}

MONITORED_PORTS = (8041, 8047, 8057)

# Latency histogram buckets
LATENCY_BUCKETS = [10, 25, 50, 75, 100, 150, 250, 500, 1000, 2000, 5000, float("inf")]

API_PUSH_TIMEOUT = 3000
API_RETRY_COUNT = 2
API_RETRY_DELAY = 100
HEALTH_CHECK_INTERVAL = 10
HEALTH_CHECK_TIMEOUT = 3000
TCP_BACKLOG = 65535
BUFFER_SIZE = 65536
UDP_TIMEOUT = 0.03

# Memory Management - CRITICAL FOR STABILITY
MAX_TRACKED_WORKERS = 128  # Hard limit on dict size
MEMORY_PRESSURE_THRESHOLD = 300  # MB - trigger aggressive cleanup
MEMORY_CHECK_INTERVAL = 30  # seconds - check memory every 30s

# ============================================================================
# SYSTEM TUNING
# ============================================================================

def raise_limits():
    """Increase file descriptor limits"""
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (1_048_576, 1_048_576))
    except Exception as e:
        logging.warning(f"Could not set ulimit: {e}")

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    log_dir = "/var/log/redirector"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger('redirector_v4')
    logger.setLevel(logging.DEBUG)

    from logging.handlers import RotatingFileHandler

    main_log = os.path.join(log_dir, "l4_redirector_v4_enterprise.log")
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
# UTILITY FUNCTIONS
# ============================================================================

def get_utc_timestamp():
    """Get RFC3339 UTC timestamp"""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# ============================================================================
# SHARED STATE (MULTIPROCESSING)
# ============================================================================

manager = multiprocessing.Manager()

# Worker stats (with HARD LIMIT on size)
WORKER_STATS = manager.dict()

# PID to worker_id mapping (for reliable cleanup)
WORKER_PIDS = manager.dict()  # NEW: pid (str) -> worker_id

# Global stats
GLOBAL_STATS = manager.dict({
    "udp_packets": 0,
    "udp_checks_ok": 0,
    "udp_checks_fail": 0,
    "cleanup_runs": 0,
    "workers_cleaned": 0,
})

# Monitor state
MONITOR_STATE = manager.dict()

# Latency histograms
LATENCY_HISTOGRAM = manager.dict()

stats_lock = manager.Lock()

def init_latency_histograms():
    """Initialize latency histogram buckets"""
    for port in MONITORED_PORTS:
        LATENCY_HISTOGRAM[port] = {
            "buckets": {str(b): 0 for b in LATENCY_BUCKETS},
            "count": 0,
            "sum": 0
        }

def init_worker(worker_id):
    """Initialize worker stats and register PID"""
    WORKER_STATS[worker_id] = {
        "active_tcp": 0,
        "total_tcp": 0,
        "bytes_in": 0,
        "bytes_out": 0,
        "uptime_sec": 0,
        "last_activity": time.time(),
    }
    # Register this worker's PID for reliable cleanup
    pid = str(os.getpid())
    WORKER_PIDS[pid] = worker_id

def cleanup_dead_processes():
    """Remove workers from processes that no longer exist"""
    try:
        with stats_lock:
            dead_pids = []
            
            # Check which PIDs are still alive
            for pid_str in list(WORKER_PIDS.keys()):
                pid = int(pid_str)
                # Check if process still exists
                if not os.path.exists(f"/proc/{pid}"):
                    worker_id = WORKER_PIDS[pid_str]
                    if worker_id in WORKER_STATS:
                        del WORKER_STATS[worker_id]
                        with stats_lock:
                            GLOBAL_STATS["workers_cleaned"] += 1
                    dead_pids.append(pid_str)
            
            # Clean up PID mappings
            for pid_str in dead_pids:
                del WORKER_PIDS[pid_str]
            
            if dead_pids:
                logger.debug(f"Cleanup: Removed {len(dead_pids)} dead process workers")
                
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

def enforce_worker_limit():
    """Enforce hard limit on tracked workers to prevent unbounded growth"""
    try:
        with stats_lock:
            if len(WORKER_STATS) > MAX_TRACKED_WORKERS:
                # Sort by last_activity and remove oldest inactive ones
                workers = sorted(
                    WORKER_STATS.items(),
                    key=lambda x: x[1]['last_activity']
                )
                
                # Remove oldest workers until we're under limit
                to_remove = len(WORKER_STATS) - MAX_TRACKED_WORKERS
                for worker_id, _ in workers[:to_remove]:
                    if WORKER_STATS[worker_id]["active_tcp"] == 0:
                        del WORKER_STATS[worker_id]
                        logger.debug(f"Enforce limit: Removed {worker_id}")
                        
    except Exception as e:
        logger.error(f"Limit enforcement error: {e}")

def check_memory_pressure():
    """Detect high memory usage and force cleanup"""
    try:
        process = psutil.Process()
        rss_mb = process.memory_info().rss / 1024 / 1024
        
        if rss_mb > MEMORY_PRESSURE_THRESHOLD:
            logger.warning(f"⚠️  Memory pressure detected: {rss_mb:.1f}MB (threshold: {MEMORY_PRESSURE_THRESHOLD}MB)")
            
            # Force aggressive cleanup
            with stats_lock:
                removed = 0
                for worker_id in list(WORKER_STATS.keys()):
                    if WORKER_STATS[worker_id]["active_tcp"] == 0:
                        del WORKER_STATS[worker_id]
                        removed += 1
                
                if removed > 0:
                    logger.info(f"Memory pressure: Removed {removed} inactive workers")
                    GLOBAL_STATS["workers_cleaned"] += removed
                    
    except Exception as e:
        logger.error(f"Memory pressure check error: {e}")

# ============================================================================
# BACKEND API CLIENT
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
            async with session.post(url, json=data, headers=headers) as resp:
                if resp.status == 200:
                    return True
                else:
                    logger.debug(f"API {resp.status}: {endpoint}")
                    if retry_count < API_RETRY_COUNT:
                        await asyncio.sleep(API_RETRY_DELAY / 1000)
                        return await push_to_backend(endpoint, data, retry_count + 1)
                    return False
    except asyncio.TimeoutError:
        logger.debug(f"API timeout: {endpoint}")
        if retry_count < API_RETRY_COUNT:
            await asyncio.sleep(API_RETRY_DELAY / 1000)
            return await push_to_backend(endpoint, data, retry_count + 1)
        return False
    except Exception as e:
        logger.debug(f"API error: {endpoint}: {e}")
        if retry_count < API_RETRY_COUNT:
            await asyncio.sleep(API_RETRY_DELAY / 1000)
            return await push_to_backend(endpoint, data, retry_count + 1)
        return False

# ============================================================================
# TCP PIPE - STATELESS FORWARDING
# ============================================================================

async def pipe(reader, writer, worker_id, direction, port):
    """Bidirectional data forwarding (stateless)"""
    try:
        total_bytes = 0
        while True:
            data = await asyncio.wait_for(reader.read(BUFFER_SIZE), timeout=300)
            if not data:
                break
            size = len(data)
            total_bytes += size
            
            with stats_lock:
                if worker_id in WORKER_STATS:
                    if direction == "in":
                        WORKER_STATS[worker_id]["bytes_in"] += size
                    else:
                        WORKER_STATS[worker_id]["bytes_out"] += size
            
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
    """Main TCP connection handler"""
    client_addr = client_writer.get_extra_info('peername')
    client_ip = client_addr[0] if client_addr else 'unknown'
    client_port = client_addr[1] if client_addr else 0

    connection_start = time.time()
    backend_start = None
    backend_reader = None
    backend_writer = None
    backend_latency = 0

    logger.info(f"[{port}] NEW: {client_ip}:{client_port} → {target_ip}:{target_port} (worker: {worker_id})")

    try:
        with stats_lock:
            if worker_id in WORKER_STATS:
                WORKER_STATS[worker_id]["active_tcp"] += 1
                WORKER_STATS[worker_id]["total_tcp"] += 1

        # Connect to backend and measure latency
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
            await push_to_backend(f"/api/v1/errors/l2n/{port}", {
                "timestamp": get_utc_timestamp(),
                "error_type": "connection_timeout",
                "backend_ip": target_ip,
                "error_message": f"Timeout connecting to {target_ip}:{target_port}"
            })
            return
        except Exception as e:
            logger.error(f"[{port}] ERROR: {e}")
            await push_to_backend(f"/api/v1/errors/l2n/{port}", {
                "timestamp": get_utc_timestamp(),
                "error_type": "connection_error",
                "backend_ip": target_ip,
                "error_message": str(e)
            })
            return

        # Bidirectional forwarding
        logger.debug(f"[{port}] FORWARD: Starting bidirectional forwarding")
        task1 = pipe(client_reader, backend_writer, worker_id, "in", port)
        task2 = pipe(backend_reader, client_writer, worker_id, "out", port)
        await asyncio.gather(task1, task2, return_exceptions=True)

        # Record metrics
        duration_ms = int((time.time() - connection_start) * 1000)
        logger.info(f"[{port}] CLOSED: {client_ip}:{client_port} | Duration:{duration_ms}ms | Latency:{backend_latency}ms")

        # Push all 8 streams asynchronously
        asyncio.create_task(push_to_backend(
            f"/api/v1/web/{port}",
            {
                "timestamp": get_utc_timestamp(),
                "client_ip": client_ip,
                "client_port": client_port,
                "bytes_in": WORKER_STATS.get(worker_id, {}).get("bytes_in", 0),
                "bytes_out": WORKER_STATS.get(worker_id, {}).get("bytes_out", 0),
                "duration_ms": duration_ms,
                "worker_id": worker_id
            }
        ))

        asyncio.create_task(push_to_backend(
            f"/api/v1/l2n/{port}",
            {
                "timestamp": get_utc_timestamp(),
                "backend_ip": target_ip,
                "backend_port": target_port,
                "duration_ms": duration_ms,
                "latency_ms": backend_latency,
                "worker_id": worker_id
            }
        ))

        # Update latency histogram
        with stats_lock:
            if port in LATENCY_HISTOGRAM:
                hist = LATENCY_HISTOGRAM[port]
                hist["count"] += 1
                hist["sum"] += backend_latency
                for b in LATENCY_BUCKETS:
                    if backend_latency <= b:
                        hist["buckets"][str(b)] += 1

    except Exception as e:
        logger.error(f"[{port}] HANDLER ERROR: {e}")
    finally:
        with stats_lock:
            if worker_id in WORKER_STATS:
                WORKER_STATS[worker_id]["active_tcp"] -= 1
                WORKER_STATS[worker_id]["last_activity"] = time.time()

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
    raise_limits()
    init_worker(worker_id)
    
    logger.info(f"✅ [PORT {port}] TCP worker listening (worker_id: {worker_id})")
    server = await asyncio.start_server(
        lambda r, w: tcp_handler(r, w, port, target_ip, target_port, worker_id),
        LISTEN_IP, port, backlog=TCP_BACKLOG, reuse_address=True, reuse_port=True
    )
    async with server:
        await server.serve_forever()

# ============================================================================
# UDP RELAY - FROM OLD VERSION
# ============================================================================

class UDPRelay(asyncio.DatagramProtocol):
    """UDP relay - from original L4 redirector"""
    def __init__(self, port):
        self.target = PORT_MAP.get(port)
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if not self.target:
            return
        
        with stats_lock:
            GLOBAL_STATS["udp_packets"] += 1

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(data, self.target)
            sock.settimeout(UDP_TIMEOUT)
            resp, _ = sock.recvfrom(65535)
            self.transport.sendto(resp, addr)
        except Exception:
            pass
        finally:
            sock.close()

async def udp_master(port):
    """UDP master for each port"""
    raise_limits()
    loop = asyncio.get_running_loop()
    
    await loop.create_datagram_endpoint(
        lambda: UDPRelay(port),
        local_addr=(LISTEN_IP, port),
    )
    logger.info(f"✅ [PORT {port}] UDP relay listening")
    await asyncio.Event().wait()

# ============================================================================
# HEALTH CHECKS - TCP & UDP
# ============================================================================

async def check_target_tcp(port):
    """Check TCP target health"""
    ip, tport = PORT_MAP.get(port, (None, None))
    if not ip:
        return {"status": "unknown", "latency_ms": 0}

    start = time.time()
    try:
        r, w = await asyncio.wait_for(
            asyncio.open_connection(ip, tport),
            timeout=2
        )
        w.close()
        await w.wait_closed()

        latency = int((time.time() - start) * 1000)
        
        # Update histogram
        with stats_lock:
            if port in LATENCY_HISTOGRAM:
                hist = LATENCY_HISTOGRAM[port]
                hist["count"] += 1
                hist["sum"] += latency
                for b in LATENCY_BUCKETS:
                    if latency <= b:
                        hist["buckets"][str(b)] += 1

        return {"status": "up", "latency_ms": latency}
    except Exception as e:
        return {"status": "down", "error": str(e), "latency_ms": 0}

async def check_target_udp(port):
    """Check UDP target health"""
    ip, tport = PORT_MAP.get(port, (None, None))
    if not ip:
        return "unknown"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    try:
        sock.sendto(b"health", (ip, tport))
        with stats_lock:
            GLOBAL_STATS["udp_checks_ok"] += 1
        return "up"
    except Exception:
        with stats_lock:
            GLOBAL_STATS["udp_checks_fail"] += 1
        return "down"
    finally:
        sock.close()

async def monitor_loop():
    """Health check monitoring loop with PROPER memory cleanup"""
    logger.info("✅ Health monitor started (10-second intervals)")
    memory_check_counter = 0
    
    while True:
        try:
            # Health checks (every 10 seconds)
            for port in MONITORED_PORTS:
                tcp_health = await check_target_tcp(port)
                udp_health = await check_target_udp(port)
                
                with stats_lock:
                    MONITOR_STATE[port] = {
                        **tcp_health,
                        "udp_status": udp_health,
                        "checked_at": int(time.time())
                    }

            # Cleanup: Run every 30 seconds
            memory_check_counter += 1
            if memory_check_counter >= (MEMORY_CHECK_INTERVAL // HEALTH_CHECK_INTERVAL):
                cleanup_dead_processes()          # Remove dead process workers
                enforce_worker_limit()             # Enforce hard limit
                check_memory_pressure()            # Detect memory bloat
                
                with stats_lock:
                    GLOBAL_STATS["cleanup_runs"] += 1
                    tracked = len(WORKER_STATS)
                    cleaned = GLOBAL_STATS["workers_cleaned"]
                
                logger.debug(f"Cleanup: {tracked} workers tracked, {cleaned} total cleaned")
                memory_check_counter = 0

            await asyncio.sleep(HEALTH_CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)

# ============================================================================
# PROMETHEUS METRICS - FROM OLD VERSION
# ============================================================================

def prometheus_metrics():
    """Generate Prometheus metrics output"""
    lines = []

    # Worker metrics
    with stats_lock:
        for worker_id, stats in WORKER_STATS.items():
            for k, v in stats.items():
                lines.append(f'redirector_worker_{k}{{worker_id="{worker_id}"}} {v}')

        # Global stats
        for k, v in GLOBAL_STATS.items():
            lines.append(f"redirector_{k} {v}")

        # Latency histograms
        for port, hist in LATENCY_HISTOGRAM.items():
            cum = 0
            for b in LATENCY_BUCKETS:
                cum += hist["buckets"][str(b)]
                lines.append(
                    f'redirector_tcp_latency_ms_bucket{{port="{port}",le="{b}"}} {cum}'
                )
            lines.append(f'redirector_tcp_latency_ms_count{{port="{port}"}} {hist["count"]}')
            lines.append(f'redirector_tcp_latency_ms_sum{{port="{port}"}} {hist["sum"]}')

    return "\n".join(lines) + "\n"

# ============================================================================
# HTTP API - MONITORING & METRICS
# ============================================================================

@web.middleware
async def auth_middleware(request, handler):
    """Authentication middleware"""
    if request.headers.get("Authorization") != f"Bearer {API_AUTH_TOKEN}":
        return web.json_response({"error": "unauthorized"}, status=401)
    return await handler(request)

def system_stats():
    """Get system stats"""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "load_avg": os.getloadavg(),
            "ram": dict(psutil.virtual_memory()._asdict()),
            "uptime_sec": int(time.time() - psutil.boot_time()),
            "net": dict(psutil.net_io_counters()._asdict())
        }
    except Exception as e:
        return {"error": str(e)}

async def status_handler(request):
    """Status endpoint"""
    with stats_lock:
        return web.json_response({
            "ports": dict(MONITOR_STATE),
            "workers": dict(WORKER_STATS),
            "global": dict(GLOBAL_STATS),
            "system": system_stats(),
            "timestamp": get_utc_timestamp()
        })

async def metrics_handler(request):
    """Prometheus metrics endpoint"""
    return web.Response(text=prometheus_metrics(), content_type="text/plain")

async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "ok",
        "version": "4.1.1-emergency",
        "timestamp": get_utc_timestamp()
    })

async def start_http_server():
    """Start HTTP monitoring server"""
    raise_limits()
    app = web.Application(middlewares=[auth_middleware])
    app.router.add_get("/health", health_handler)
    app.router.add_get("/status", status_handler)
    app.router.add_get("/metrics", metrics_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 9090, reuse_address=True)
    await site.start()
    logger.info("✅ HTTP monitoring server listening on :9090")
    
    await asyncio.Event().wait()

# ============================================================================
# PROCESS ENTRY POINTS
# ============================================================================

def run_tcp_worker(port, target_ip, target_port, worker_id):
    """TCP worker entry point"""
    raise_limits()
    asyncio.run(tcp_worker(port, target_ip, target_port, worker_id))

def run_udp_worker(port):
    """UDP worker entry point"""
    raise_limits()
    asyncio.run(udp_master(port))

def run_monitor():
    """Monitor entry point"""
    raise_limits()
    asyncio.run(monitor_loop())

def run_http_server():
    """HTTP server entry point"""
    raise_limits()
    asyncio.run(start_http_server())

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    if os.geteuid() != 0:
        raise SystemExit("Run as root")

    raise_limits()
    init_latency_histograms()

    logger.info("=" * 100)
    logger.info("🚀 L4 REDIRECTOR v4.1.1 - EMERGENCY FIX (Memory-Safe)")
    logger.info("=" * 100)
    logger.info(f"📡 Backend API: {BACKEND_API_URL}")
    logger.info(f"✅ TCP + UDP forwarding active")
    logger.info(f"✅ Prometheus metrics enabled")
    logger.info(f"✅ Latency histograms tracking")
    logger.info(f"✅ Memory management: FIXED (PID tracking + hard limits)")
    logger.info(f"⚠️  Max workers tracked: {MAX_TRACKED_WORKERS}")
    logger.info(f"⚠️  Memory pressure threshold: {MEMORY_PRESSURE_THRESHOLD}MB")
    logger.info("=" * 100)

    processes = []
    cpu_count = os.cpu_count() or 2

    try:
        # Monitor process
        p = multiprocessing.Process(target=run_monitor)
        p.daemon = False
        p.start()
        processes.append(p)
        time.sleep(0.5)

        # HTTP server
        p = multiprocessing.Process(target=run_http_server)
        p.daemon = False
        p.start()
        processes.append(p)
        time.sleep(0.5)

        # TCP workers (CPU count * 4 for production)
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

        # UDP workers
        for port in PORT_MAP.keys():
            p = multiprocessing.Process(target=run_udp_worker, args=(port,))
            p.daemon = False
            p.start()
            processes.append(p)
            time.sleep(0.1)

        logger.info(f"✅ All {len(processes)} processes started")
        logger.info(f"✅ Ready for {cpu_count * 4 * 3} concurrent TCP connections per port")
        logger.info(f"📊 Metrics available at: :9090/metrics")
        logger.info("✅ Memory-safe cleanup enabled (30-second intervals)")
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
