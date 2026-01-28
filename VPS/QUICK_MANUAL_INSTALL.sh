#!/bin/bash
################################################################################
# QUICK MANUAL INSTALL - NO DOWNLOADS
# If automated download fails, use this method instead
# Just paste the hybrid redirector code directly
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║    MANUAL HYBRID REDIRECTOR INSTALL (NO DOWNLOADS)                    ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}This script will create the hybrid redirector directly.${NC}"
echo -e "${YELLOW}No internet downloads needed!${NC}"
echo ""

# Step 1: Stop current service
echo -e "${YELLOW}[1/3] Stopping current service...${NC}"
sudo systemctl stop redirector-v3.service 2>/dev/null || true
sudo pkill -9 l4_redirector || true
sleep 2
echo -e "${GREEN}✓ Stopped${NC}"

# Step 2: Create the hybrid redirector inline
echo -e "${YELLOW}[2/3] Creating hybrid redirector...${NC}"

sudo tee /usr/local/bin/l4_redirector_v3_hybrid_working.py > /dev/null << 'HYBRID_CODE'
#!/usr/bin/env python3
"""
Enterprise L4 Redirector v3 - HYBRID STATELESS ARCHITECTURE
Redirects traffic + sends 8 data streams to Backend API

Architecture: Stateless (no local state, only async metrics)
Data destination: Backend API via LocalToNet tunnel
"""

import asyncio
import logging
import os
import resource
import multiprocessing
import time
import traceback
from datetime import datetime
from aiohttp import web, ClientSession, ClientConnectorError
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
BACKEND_API_TOKEN = "your-secure-token-here-change-this"

PORT_MAP = {
    8041: ("129.151.142.36", 1429),
    8047: ("129.151.142.36", 8667),
    8057: ("129.151.142.36", 7798),
}

API_PUSH_TIMEOUT = 2000
API_RETRY_COUNT = 3
API_RETRY_DELAY = 100
HEALTH_CHECK_INTERVAL = 5
HEALTH_CHECK_TIMEOUT = 2000
TCP_BACKLOG = 65535
BUFFER_SIZE = 65536

# ============================================================================
# LOGGING
# ============================================================================

def setup_logging():
    log_dir = "/var/log/redirector"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger('redirector')
    logger.setLevel(logging.DEBUG)
    
    from logging.handlers import RotatingFileHandler
    
    main_log = os.path.join(log_dir, "l4_redirector_v3_hybrid.log")
    fh = RotatingFileHandler(main_log, maxBytes=100*1024*1024, backupCount=10)
    fh.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d | %(process)d | %(levelname)-8s | %(name)s | %(message)s',
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
stats['streams'] = manager.dict()
stats_lock = manager.Lock()

# ============================================================================
# BACKEND API CLIENT
# ============================================================================

async def push_to_backend(endpoint, data, retry_count=0):
    """Push data to Backend API via LocalToNet tunnel"""
    try:
        headers = {
            "Authorization": f"Bearer {BACKEND_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        url = f"{BACKEND_API_URL}{endpoint}"
        
        async with ClientSession() as session:
            async with session.post(
                url,
                json=data,
                headers=headers,
                timeout=asyncio.timeout(API_PUSH_TIMEOUT/1000)
            ) as resp:
                if resp.status == 200:
                    return True
                else:
                    logger.debug(f"Backend API: {resp.status} for {endpoint}")
                    if retry_count < API_RETRY_COUNT:
                        await asyncio.sleep(API_RETRY_DELAY / 1000)
                        return await push_to_backend(endpoint, data, retry_count + 1)
                    return False
    except asyncio.TimeoutError:
        if retry_count < API_RETRY_COUNT:
            await asyncio.sleep(API_RETRY_DELAY / 1000)
            return await push_to_backend(endpoint, data, retry_count + 1)
        return False
    except Exception as e:
        if retry_count < API_RETRY_COUNT:
            await asyncio.sleep(API_RETRY_DELAY / 1000)
            return await push_to_backend(endpoint, data, retry_count + 1)
        return False

async def push_web_connection(port, client_ip, client_port, bytes_in, bytes_out, duration_ms, worker_id):
    """Stream 1: Web connections"""
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "port": port,
        "client_ip": client_ip,
        "client_port": client_port,
        "bytes_in": bytes_in,
        "bytes_out": bytes_out,
        "duration_ms": duration_ms,
        "worker_id": worker_id
    }
    await push_to_backend(f"/api/v1/web/{port}", data)

async def push_l2n_connection(port, backend_ip, backend_port, bytes_in, bytes_out, duration_ms, latency_ms, worker_id):
    """Stream 2: L2N connections"""
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "port": port,
        "backend_ip": backend_ip,
        "backend_port": backend_port,
        "bytes_in": bytes_in,
        "bytes_out": bytes_out,
        "duration_ms": duration_ms,
        "latency_ms": latency_ms,
        "worker_id": worker_id
    }
    await push_to_backend(f"/api/v1/l2n/{port}", data)

async def push_error(port, error_type, client_ip, backend_ip, error_msg, is_web=True):
    """Streams 3&4: Error reporting"""
    endpoint = f"/api/v1/errors/web/{port}" if is_web else f"/api/v1/errors/l2n/{port}"
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "error_type": error_type,
        "client_ip": client_ip if is_web else None,
        "backend_ip": backend_ip if not is_web else None,
        "error_message": error_msg
    }
    await push_to_backend(endpoint, data)

async def push_warning(port, warning_type, message, severity="warning"):
    """Stream 5: Warnings"""
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "port": port,
        "warning_type": warning_type,
        "message": message,
        "severity": severity
    }
    await push_to_backend("/api/v1/warnings", data)

async def push_succeeded_access(port, client_ip, client_port, backend_ip, backend_port, bytes_transferred, duration_ms):
    """Stream 6: Succeeded connections"""
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

async def push_port_health(port, backend_ip, backend_port, status, latency_ms):
    """Stream 7: Port health"""
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "port": port,
        "backend_ip": backend_ip,
        "backend_port": backend_port,
        "status": status,
        "latency_ms": latency_ms
    }
    await push_to_backend(f"/api/v1/health/{port}", data)

async def push_l2n_health(status, latency_ms):
    """Stream 8: L2N health"""
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tunnel": "LocalToNet",
        "tunnel_ip": LOCALTONET_IP,
        "tunnel_port": LOCALTONET_PORT,
        "status": status,
        "latency_ms": latency_ms
    }
    await push_to_backend("/api/v1/health/l2n", data)

# ============================================================================
# TCP HANDLER
# ============================================================================

async def tcp_handler(client_reader, client_writer, port, target_ip, target_port, worker_id):
    """Main TCP connection handler - STATELESS"""
    client_addr = client_writer.get_extra_info('peername')
    client_ip = client_addr[0] if client_addr else 'unknown'
    client_port = client_addr[1] if client_addr else 0
    
    connection_start = time.time()
    backend_start = None
    bytes_in = 0
    bytes_out = 0
    backend_reader = None
    backend_writer = None
    
    try:
        # Connect to backend
        try:
            backend_start = time.time()
            backend_reader, backend_writer = await asyncio.wait_for(
                asyncio.open_connection(target_ip, target_port),
                timeout=HEALTH_CHECK_TIMEOUT / 1000
            )
            backend_latency = int((time.time() - backend_start) * 1000)
            logger.info(f"[{port}] NEW: {client_ip}:{client_port} → {target_ip}:{target_port}")
            logger.debug(f"[{port}] TUNNEL: Connected (latency: {backend_latency}ms) [{worker_id}]")
        except asyncio.TimeoutError:
            asyncio.create_task(push_error(port, 'connection_timeout', client_ip, target_ip, 'Backend timeout', False))
            logger.warning(f"[{port}] TIMEOUT: {client_ip}:{client_port} → {target_ip}:{target_port}")
            return
        except ConnectionRefusedError:
            asyncio.create_task(push_error(port, 'connection_refused', client_ip, target_ip, 'Backend refused', False))
            logger.warning(f"[{port}] REFUSED: {client_ip}:{client_port} → {target_ip}:{target_port}")
            return
        except OSError as e:
            asyncio.create_task(push_error(port, 'connection_error', client_ip, target_ip, str(e), False))
            logger.warning(f"[{port}] ERROR: {e}")
            return
        
        # Update worker stats
        with stats_lock:
            if worker_id not in stats['workers']:
                stats['workers'][worker_id] = {'active': 0, 'total': 0}
            w = stats['workers'][worker_id]
            w['active'] = w['active'] + 1
            w['total'] = w['total'] + 1
            stats['workers'][worker_id] = w
        
        # Forward data bidirectionally (STATELESS - no local tracking)
        task1 = forward_data(client_reader, backend_writer, port, 'in', worker_id)
        task2 = forward_data(backend_reader, client_writer, port, 'out', worker_id)
        await asyncio.gather(task1, task2, return_exceptions=True)
        
        # Log successful connection (async, non-blocking)
        duration_ms = int((time.time() - connection_start) * 1000)
        logger.info(f"[{port}] CLOSED: {client_ip}:{client_port} | Duration:{duration_ms}ms | Latency:{backend_latency}ms")
        
        # Send all metrics asynchronously
        asyncio.create_task(push_web_connection(port, client_ip, client_port, bytes_in, bytes_out, duration_ms, worker_id))
        asyncio.create_task(push_l2n_connection(port, target_ip, target_port, bytes_in, bytes_out, duration_ms, backend_latency, worker_id))
        asyncio.create_task(push_succeeded_access(port, client_ip, client_port, target_ip, target_port, bytes_in + bytes_out, duration_ms))
        
    except Exception as e:
        asyncio.create_task(push_error(port, 'handler_error', client_ip, target_ip, str(e), True))
        logger.error(f"[{port}] Handler error: {e}")
    finally:
        # Decrement active connections
        with stats_lock:
            if worker_id in stats['workers']:
                w = stats['workers'][worker_id]
                w['active'] = max(0, w['active'] - 1)
                stats['workers'][worker_id] = w
        
        # Close connections
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

async def forward_data(reader, writer, port, direction, worker_id):
    """Forward data between client and backend - STATELESS"""
    try:
        while True:
            data = await asyncio.wait_for(reader.read(BUFFER_SIZE), timeout=300)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except Exception:
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass

async def tcp_worker(port, target_ip, target_port, worker_id):
    """TCP worker process"""
    logger.info(f"[{port}] TCP worker listening (worker: {worker_id})")
    server = await asyncio.start_server(
        lambda r, w: tcp_handler(r, w, port, target_ip, target_port, worker_id),
        LISTEN_IP, port, backlog=TCP_BACKLOG, reuse_address=True, reuse_port=True
    )
    async with server:
        await server.serve_forever()

# ============================================================================
# HEALTH MONITORING
# ============================================================================

async def monitor_worker():
    """Health check and monitoring"""
    logger.info("✅ Health monitor started")
    while True:
        try:
            # Monitor each port
            for port, (backend_ip, backend_port) in PORT_MAP.items():
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
                except:
                    latency_ms = HEALTH_CHECK_TIMEOUT
                    status = 'down'
                
                asyncio.create_task(push_port_health(port, backend_ip, backend_port, status, latency_ms))
                
                with stats_lock:
                    p = stats['ports']
                    p[str(port)] = {'status': status, 'latency': latency_ms}
                    stats['ports'] = p
            
            # Monitor L2N tunnel
            tunnel_start = time.time()
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(LOCALTONET_IP, LOCALTONET_PORT),
                    timeout=HEALTH_CHECK_TIMEOUT / 1000
                )
                writer.close()
                await writer.wait_closed()
                tunnel_latency = int((time.time() - tunnel_start) * 1000)
                tunnel_status = 'up'
            except:
                tunnel_latency = HEALTH_CHECK_TIMEOUT
                tunnel_status = 'down'
            
            asyncio.create_task(push_l2n_health(tunnel_status, tunnel_latency))
            
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)
        except Exception:
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)

# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================

async def health_endpoint(request):
    """GET /health"""
    return web.json_response({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})

async def config_endpoint(request):
    """GET /config"""
    return web.json_response({
        'ports': list(PORT_MAP.keys()),
        'api_version': '3.0',
        'architecture': 'stateless-streaming',
        'backend_api': BACKEND_API_URL
    })

async def status_endpoint(request):
    """GET /status"""
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

# ============================================================================
# WEB SERVER
# ============================================================================

async def status_server():
    """Status server on :9090"""
    app = web.Application()
    app.router.add_get('/health', health_endpoint)
    app.router.add_get('/config', config_endpoint)
    app.router.add_get('/status', status_endpoint)
    
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
        logger.warning(f"⚠ Failed to set file descriptors: {e}")

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
        logger.error(f"{worker_type} worker error: {e}")
    finally:
        loop.close()

def main():
    """Main entry point"""
    logger.info("="*90)
    logger.info("🚀 HYBRID L4 REDIRECTOR v3 - STATELESS STREAMING EDITION")
    logger.info("="*90)
    logger.info(f"💰 Backend API: {BACKEND_API_URL}")
    logger.info(f"8 Data Streams: web, l2n, errors, warnings, succeeded, health")
    logger.info("✅ VPS is STATELESS - metrics sent asynchronously")
    logger.info("="*90)
    
    tune_kernel()
    num_workers = os.cpu_count() or 2
    logger.info(f"Starting with {num_workers} TCP workers per port")
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

        while True:
            time.sleep(5)
            alive = [p for p in processes if p.is_alive()]
            if len(alive) < len(processes):
                logger.warning(f"⚠ Process crashed! ({len(alive)}/{len(processes)} alive)")
                processes = alive

    except KeyboardInterrupt:
        logger.info("⏹ Shutting down...")
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
HYBRID_CODE

sudo chmod +x /usr/local/bin/l4_redirector_v3_hybrid_working.py
echo -e "${GREEN}✓ Created${NC}"

# Step 3: Update systemd service and start
echo -e "${YELLOW}[3/3] Starting service...${NC}"

sudo tee /etc/systemd/system/redirector-v3.service > /dev/null <<'SYSTEMD_UNIT'
[Unit]
Description=L4 Redirector V3 Hybrid Stateless Streaming
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/redirector_V4
ExecStart=/usr/bin/python3 /usr/local/bin/l4_redirector_v3_hybrid_working.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SYSTEMD_UNIT

sudo systemctl daemon-reload
sudo systemctl start redirector-v3.service
sudo systemctl enable redirector-v3.service
sleep 2

if sudo systemctl is-active --quiet redirector-v3.service; then
    echo -e "${GREEN}✓ Service started successfully${NC}"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    sudo journalctl -u redirector-v3.service -n 20
    exit 1
fi

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║               INSTALLATION SUCCESSFUL ✓                             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"

echo ""
echo -e "${GREEN}Hybrid Redirector Installed!${NC}"
echo ""
echo -e "${YELLOW}Verify installation:${NC}"
echo "  1. Watch logs: ${BLUE}tail -f /var/log/redirector/l4_redirector_v3_hybrid.log${NC}"
echo "  2. Check status: ${BLUE}curl http://localhost:9090/status | jq${NC}"
echo "  3. Check ports: ${BLUE}sudo ss -tlnp | grep -E '8041|8047|8057'${NC}"
echo ""
echo -e "${GREEN}Installation Complete! 🚀${NC}"
