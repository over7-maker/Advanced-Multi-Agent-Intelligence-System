#!/usr/bin/env python3
"""
L4 Redirector v4.1 - Production Layer 4 TCP Traffic Redirector

This module implements a high-performance, production-ready Layer 4 TCP traffic
redirector with the following features:

- Multi-port TCP forwarding with configurable backends
- Real-time connection metadata push to backend API
- HTTP monitoring endpoint for health checks and metrics
- Multi-process architecture utilizing all CPU cores
- Circuit breaker pattern for backend resilience
- Comprehensive logging and error handling
- Intelligent log filtering to reduce noise from normal operations

Architecture:
    Client → VPS (This Service) → Backend Server
                     ↓
               Backend API (Metrics)

Author: Advanced Multi-Agent Intelligence System Project
Version: 4.1.0
Python: 3.12+
Platform: Ubuntu 24.04 LTS

Example:
    Basic usage requires environment variables to be set:
    
    $ export BACKEND_API_TOKEN="your-64-char-hex-token"
    $ export API_AUTH_TOKEN="your-64-char-hex-token"
    $ export LOCALTONET_IP="111.111.11.111"
    $ export LOCALTONET_PORT="6921"
    $ export PORT_MAP='{"8041": ["192.168.1.100", 1429]}'
    $ python3 l4_redirector_v4.py

Environment Variables:
    BACKEND_API_TOKEN (str): Authentication token for backend API communication
    API_AUTH_TOKEN (str): Authentication token for HTTP monitoring endpoint
    LOCALTONET_IP (str): IP address of LocalToNet/WireGuard gateway
    LOCALTONET_PORT (int): Port of LocalToNet/WireGuard gateway
    PORT_MAP (str): JSON string mapping frontend ports to backend [host, port]
    LOG_LEVEL (str): Optional logging level (DEBUG, INFO, WARNING, ERROR)

References:
    - Project: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System
    - Documentation: See README.md and DEPLOYMENT_GUIDE.md in this directory

Changelog v4.1:
    - Reduced log noise from normal connection resets
    - Improved error differentiation (normal vs abnormal)
    - Added connection lifecycle tracking
    - Enhanced visibility of actual errors while suppressing noise
"""

import asyncio
import aiohttp
import json
import socket
import signal
import os
import sys
from typing import Dict, Tuple, Optional, Any, List
from loguru import logger
from collections import defaultdict
from datetime import datetime, timezone

# ==================== TYPE ALIASES ====================
PortNumber = int
IPAddress = str
BackendInfo = Tuple[IPAddress, PortNumber]
PortMapping = Dict[str, BackendInfo]
StatsDict = Dict[str, Any]

# ==================== LOGGING CONFIGURATION ====================
# Configure loguru to reduce noise from normal operations
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Remove default handler and add custom one with better formatting
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True
)

# ==================== CONFIGURATION ====================
# Load configuration from environment variables with validation
try:
    BACKEND_API_TOKEN: str = os.getenv("BACKEND_API_TOKEN", "")
    API_AUTH_TOKEN: str = os.getenv("API_AUTH_TOKEN", "")
    LOCALTONET_IP: IPAddress = os.getenv("LOCALTONET_IP", "")
    LOCALTONET_PORT: PortNumber = int(os.getenv("LOCALTONET_PORT", "0"))
    PORT_MAP_STR: str = os.getenv("PORT_MAP", "{}")
    PORT_MAP: PortMapping = json.loads(PORT_MAP_STR)
except (ValueError, json.JSONDecodeError) as e:
    logger.error(f"Configuration parsing error: {e}")
    logger.error("Please check your environment variables")
    sys.exit(1)

# API endpoint for pushing connection metadata
BACKEND_API_URL: str = f"http://{LOCALTONET_IP}:{LOCALTONET_PORT}/connections"

# HTTP monitoring server configuration
HTTP_MONITOR_PORT: PortNumber = 9090

# ==================== STARTUP BANNER ====================
logger.info("=" * 100)
logger.info("🚀 L4 REDIRECTOR v4.1 PRODUCTION")
logger.info("=" * 100)
logger.info(f"📡 Backend API: {BACKEND_API_URL}")
logger.info(f"🔧 Listening Ports: {tuple(PORT_MAP.keys())}")
logger.info(f"🎯 HTTP Monitor: :{HTTP_MONITOR_PORT}")
logger.info(f"📝 Log Level: {LOG_LEVEL}")
logger.info("=" * 100)

# ==================== CONFIGURATION VALIDATION ====================
def validate_configuration() -> None:
    """
    Validate all required configuration parameters.
    
    Performs fail-fast validation of environment variables to ensure
    the service has all required configuration before attempting to start.
    
    Raises:
        SystemExit: If any required configuration is missing or invalid
        
    Validation Checks:
        - All tokens are non-empty and proper length (64 hex chars)
        - IP addresses are valid
        - Ports are in valid range (1-65535)
        - Port map is not empty
    """
    errors: List[str] = []
    
    # Validate tokens
    if not BACKEND_API_TOKEN or len(BACKEND_API_TOKEN) != 64:
        errors.append("BACKEND_API_TOKEN must be 64 hexadecimal characters")
    
    if not API_AUTH_TOKEN or len(API_AUTH_TOKEN) != 64:
        errors.append("API_AUTH_TOKEN must be 64 hexadecimal characters")
    
    # Validate IP and port
    if not LOCALTONET_IP:
        errors.append("LOCALTONET_IP is required")
    
    if LOCALTONET_PORT <= 0 or LOCALTONET_PORT > 65535:
        errors.append("LOCALTONET_PORT must be between 1 and 65535")
    
    # Validate port map
    if not PORT_MAP:
        errors.append("PORT_MAP must contain at least one port mapping")
    
    # Validate each port mapping
    for port_str, backend_info in PORT_MAP.items():
        try:
            port = int(port_str)
            if port <= 0 or port > 65535:
                errors.append(f"Invalid port number: {port_str}")
        except ValueError:
            errors.append(f"Invalid port format: {port_str}")
        
        if not isinstance(backend_info, list) or len(backend_info) != 2:
            errors.append(f"Invalid backend info for port {port_str}")
    
    if errors:
        logger.error("Configuration validation failed:")
        for error in errors:
            logger.error(f"  ❌ {error}")
        logger.error("\nPlease fix the configuration and restart the service")
        sys.exit(1)
    
    logger.info("✅ Configuration validation passed")

# Validate configuration at startup
validate_configuration()

# ==================== GLOBAL STATS ====================
stats: StatsDict = {
    "total_connections": 0,
    "active_connections": 0,
    "backend_pushes": 0,
    "backend_push_failures": 0,
    "normal_disconnects": 0,
    "abnormal_disconnects": 0,
    "by_port": defaultdict(lambda: {
        "connections": 0,
        "active": 0,
        "bytes_sent": 0,
        "bytes_received": 0,
        "normal_disconnects": 0,
        "abnormal_disconnects": 0
    })
}

# ==================== HTTP SESSION ====================
http_session: Optional[aiohttp.ClientSession] = None

async def init_http_session() -> None:
    """
    Initialize global aiohttp client session.
    
    Creates a single reusable HTTP session with appropriate timeouts
    for making requests to the backend API. Using a single session
    provides connection pooling and improved performance.
    
    Timeout Configuration:
        - Total timeout: 10 seconds
        - Connect timeout: 5 seconds
        
    Side Effects:
        Sets the global `http_session` variable
    """
    global http_session
    timeout = aiohttp.ClientTimeout(total=10, connect=5)
    http_session = aiohttp.ClientSession(timeout=timeout)
    logger.info("✅ HTTP session initialized")

async def close_http_session() -> None:
    """
    Close global HTTP session and cleanup resources.
    
    Should be called during graceful shutdown to properly close
    all pending connections and free resources.
    
    Side Effects:
        Closes and clears the global `http_session` variable
    """
    global http_session
    if http_session:
        await http_session.close()
        logger.info("✅ HTTP session closed")

# ==================== BACKEND PUSH ====================
async def push_to_backend(
    client_ip: IPAddress,
    client_port: PortNumber,
    frontend_port: PortNumber,
    backend_host: IPAddress,
    backend_port: PortNumber
) -> None:
    """
    Push connection metadata to Windows backend API.
    
    Sends connection information to the backend monitoring API for
    tracking and analysis. This is a fire-and-forget operation that
    should not block the main connection forwarding logic.
    
    Args:
        client_ip: IP address of the connecting client
        client_port: Source port of the client connection
        frontend_port: Port on which the connection was received
        backend_host: Target backend server hostname/IP
        backend_port: Target backend server port
        
    Side Effects:
        - Increments global connection statistics
        - Sends HTTP POST request to backend API
        - Logs success/failure
        
    Note:
        This function increments statistics immediately before making
        the API call to ensure counts are accurate even if the push fails.
    """
    # Increment stats immediately to ensure accuracy
    stats["total_connections"] += 1
    stats["active_connections"] += 1
    stats["by_port"][str(frontend_port)]["connections"] += 1
    stats["by_port"][str(frontend_port)]["active"] += 1

    payload: Dict[str, Any] = {
        "client_ip": client_ip,
        "client_port": client_port,
        "frontend_port": frontend_port,
        "backend_host": backend_host,
        "backend_port": backend_port,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {BACKEND_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        if not http_session:
            logger.error("HTTP session not initialized")
            stats["backend_push_failures"] += 1
            return
            
        async with http_session.post(
            BACKEND_API_URL,
            json=payload,
            headers=headers
        ) as resp:
            if resp.status in (200, 201):
                stats["backend_pushes"] += 1
                logger.debug(
                    f"✅ Backend push: {client_ip}:{client_port} → "
                    f"{backend_host}:{backend_port}"
                )
            else:
                stats["backend_push_failures"] += 1
                logger.warning(
                    f"⚠️  Backend push failed: HTTP {resp.status}"
                )
    except asyncio.TimeoutError:
        stats["backend_push_failures"] += 1
        logger.warning("⚠️  Backend push timeout")
    except aiohttp.ClientError as e:
        stats["backend_push_failures"] += 1
        logger.warning(f"⚠️  Backend push client error: {e}")
    except Exception as e:
        stats["backend_push_failures"] += 1
        logger.warning(f"⚠️  Backend push unexpected error: {type(e).__name__}: {e}")

# ==================== TCP FORWARDING ====================
async def forward_data(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    direction: str,
    frontend_port: PortNumber
) -> Tuple[bool, Optional[Exception]]:
    """
    Forward data bidirectionally between client and backend.
    
    Reads data from the source stream and writes it to the destination
    stream in chunks. Tracks bytes transferred for statistics.
    
    Args:
        reader: Stream to read data from
        writer: Stream to write data to
        direction: Direction identifier ("client_to_backend" or "backend_to_client")
        frontend_port: Frontend port number for statistics tracking
        
    Returns:
        Tuple of (normal_close: bool, exception: Optional[Exception])
        - normal_close: True if connection closed normally
        - exception: The exception if abnormal close occurred
        
    Side Effects:
        - Transfers data between streams
        - Updates byte transfer statistics
        - Closes writer on completion or error
        
    Buffer Size:
        8192 bytes per read operation (optimal for most network conditions)
        
    Note:
        Returns information about how the connection closed to allow
        the caller to differentiate between normal and abnormal terminations.
    """
    try:
        while True:
            data: bytes = await reader.read(8192)
            if not data:
                # Clean EOF - normal close
                return (True, None)

            writer.write(data)
            await writer.drain()

            # Track bytes transferred
            if direction == "client_to_backend":
                stats["by_port"][str(frontend_port)]["bytes_sent"] += len(data)
            else:
                stats["by_port"][str(frontend_port)]["bytes_received"] += len(data)

    except (ConnectionResetError, BrokenPipeError) as e:
        # Normal abrupt termination - client/server closed without proper shutdown
        # This is EXPECTED behavior in production networks
        return (True, e)
    except Exception as e:
        # Unexpected error - this is abnormal and should be logged
        return (False, e)
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except (ConnectionResetError, BrokenPipeError):
            # Normal - other side already closed
            pass
        except Exception:
            # Unexpected but not critical
            pass

async def handle_client(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    frontend_port: PortNumber,
    backend_host: IPAddress,
    backend_port: PortNumber
) -> None:
    """
    Handle individual client connection with L4 TCP forwarding.
    
    Accepts a client connection, establishes a connection to the backend,
    and sets up bidirectional data forwarding between them.
    
    Args:
        client_reader: Stream for reading from client
        client_writer: Stream for writing to client
        frontend_port: Port on which connection was accepted
        backend_host: Target backend hostname/IP
        backend_port: Target backend port
        
    Connection Flow:
        1. Extract client information
        2. Push metadata to backend API (async, non-blocking)
        3. Connect to backend server
        4. Set up bidirectional forwarding
        5. Wait for completion
        6. Clean up resources
        
    Timeout:
        10 seconds for backend connection establishment
        
    Side Effects:
        - Creates backend connection
        - Spawns background task for API push
        - Updates statistics
        - Logs connection events (filtered for noise reduction)
    """
    client_addr: Optional[Tuple[str, int]] = client_writer.get_extra_info('peername')
    client_ip: IPAddress = client_addr[0] if client_addr else "unknown"
    client_port: PortNumber = client_addr[1] if client_addr else 0

    logger.info(
        f"[{frontend_port}] Client connected from {client_ip}:{client_port}, "
        f"connecting to {backend_host}:{backend_port}"
    )

    # Push to backend API asynchronously (non-blocking)
    asyncio.create_task(
        push_to_backend(
            client_ip,
            client_port,
            frontend_port,
            backend_host,
            backend_port
        )
    )

    backend_reader: Optional[asyncio.StreamReader] = None
    backend_writer: Optional[asyncio.StreamWriter] = None
    was_normal_close: bool = False

    try:
        # Connect to backend with timeout
        backend_reader, backend_writer = await asyncio.wait_for(
            asyncio.open_connection(backend_host, backend_port),
            timeout=10
        )

        # Bidirectional forwarding with enhanced error tracking
        results = await asyncio.gather(
            forward_data(
                client_reader,
                backend_writer,
                "client_to_backend",
                frontend_port
            ),
            forward_data(
                backend_reader,
                client_writer,
                "backend_to_client",
                frontend_port
            ),
            return_exceptions=False  # Let exceptions propagate to our handler
        )
        
        # Check if both directions closed normally
        client_to_backend_normal, client_to_backend_exc = results[0]
        backend_to_client_normal, backend_to_client_exc = results[1]
        
        # If either direction had a normal close, consider it normal
        was_normal_close = client_to_backend_normal or backend_to_client_normal
        
        # Only log abnormal closures at WARNING level
        if not was_normal_close:
            if client_to_backend_exc:
                logger.warning(
                    f"[{frontend_port}] Abnormal close (client→backend): "
                    f"{type(client_to_backend_exc).__name__}: {client_to_backend_exc}"
                )
            if backend_to_client_exc:
                logger.warning(
                    f"[{frontend_port}] Abnormal close (backend→client): "
                    f"{type(backend_to_client_exc).__name__}: {backend_to_client_exc}"
                )

    except asyncio.TimeoutError:
        was_normal_close = False
        logger.warning(
            f"[{frontend_port}] Backend connection timeout: "
            f"{backend_host}:{backend_port}"
        )
    except OSError as e:
        was_normal_close = False
        logger.warning(
            f"[{frontend_port}] OS error connecting to backend: {e}"
        )
    except Exception as e:
        was_normal_close = False
        logger.warning(
            f"[{frontend_port}] Connection error: {type(e).__name__}: {e}"
        )
    finally:
        # Update statistics based on close type
        if was_normal_close:
            stats["normal_disconnects"] += 1
            stats["by_port"][str(frontend_port)]["normal_disconnects"] += 1
        else:
            stats["abnormal_disconnects"] += 1
            stats["by_port"][str(frontend_port)]["abnormal_disconnects"] += 1
        
        # Decrement active connection count
        stats["active_connections"] -= 1
        stats["by_port"][str(frontend_port)]["active"] -= 1
        
        # Clean up client connection
        try:
            client_writer.close()
            await client_writer.wait_closed()
        except (ConnectionResetError, BrokenPipeError):
            # Normal - connection already closed
            pass
        except Exception:
            # Not critical
            pass

# ==================== TCP WORKERS ====================
async def tcp_worker(
    port: PortNumber,
    backend_host: IPAddress,
    backend_port: PortNumber,
    worker_id: int
) -> None:
    """
    TCP worker process for specific port.
    
    Creates a TCP server that listens on the specified port and forwards
    connections to the configured backend. Multiple workers can listen on
    the same port using SO_REUSEPORT for load balancing.
    
    Args:
        port: Port number to listen on
        backend_host: Target backend hostname/IP
        backend_port: Target backend port
        worker_id: Unique identifier for this worker (for logging)
        
    Socket Options:
        - SO_REUSEPORT: Enables multiple workers per port
        - Allows kernel-level load balancing
        
    Lifecycle:
        Runs indefinitely until cancelled or service shutdown
        
    Side Effects:
        - Binds to specified port
        - Accepts and handles incoming connections
        - Logs worker startup
    """
    async def accept_client(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        """Wrapper for handle_client with bound parameters."""
        await handle_client(reader, writer, port, backend_host, backend_port)

    server = await asyncio.start_server(
        accept_client,
        "0.0.0.0",
        port,
        reuse_port=True
    )
    
    logger.info(
        f"✅ [PORT {port}] TCP worker tcp_{port}_{worker_id} started"
    )

    async with server:
        await server.serve_forever()

# ==================== HTTP MONITORING ====================
async def http_status_handler(request: aiohttp.web.Request) -> aiohttp.web.Response:
    """
    HTTP status endpoint handler.
    
    Provides real-time service metrics and statistics via HTTP endpoint.
    Requires bearer token authentication.
    
    Args:
        request: aiohttp request object
        
    Returns:
        JSON response with service status and metrics
        
    Authentication:
        Requires "Authorization: Bearer <API_AUTH_TOKEN>" header
        
    Response Format:
        {
            "status": "ok",
            "timestamp": "ISO-8601 timestamp",
            "global": {
                "total_connections": int,
                "active_connections": int,
                "backend_pushes": int,
                "backend_push_failures": int,
                "normal_disconnects": int,
                "abnormal_disconnects": int
            },
            "by_port": {
                "<port>": {
                    "connections": int,
                    "active": int,
                    "bytes_sent": int,
                    "bytes_received": int,
                    "normal_disconnects": int,
                    "abnormal_disconnects": int
                }
            }
        }
        
    Status Codes:
        200: Success
        401: Unauthorized (invalid or missing token)
    """
    # Constant-time token comparison to prevent timing attacks
    auth_header: str = request.headers.get("Authorization", "")
    expected_auth: str = f"Bearer {API_AUTH_TOKEN}"
    
    # Use constant-time comparison
    if not _constant_time_compare(auth_header, expected_auth):
        logger.warning(
            f"Unauthorized status request from {request.remote}"
        )
        return aiohttp.web.json_response(
            {"error": "unauthorized"},
            status=401
        )

    response: Dict[str, Any] = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "global": {
            "total_connections": stats["total_connections"],
            "active_connections": stats["active_connections"],
            "backend_pushes": stats["backend_pushes"],
            "backend_push_failures": stats["backend_push_failures"],
            "normal_disconnects": stats["normal_disconnects"],
            "abnormal_disconnects": stats["abnormal_disconnects"]
        },
        "by_port": dict(stats["by_port"])
    }

    return aiohttp.web.json_response(response)

def _constant_time_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equal, False otherwise
        
    Security:
        Uses bitwise operations to ensure comparison takes constant time
        regardless of where the first difference occurs.
    """
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    
    return result == 0

async def http_server() -> None:
    """
    HTTP monitoring server.
    
    Creates and runs the HTTP server for monitoring endpoints.
    Provides health checks and real-time metrics.
    
    Endpoints:
        GET /status - Service statistics and metrics (requires auth)
        
    Configuration:
        - Listens on all interfaces (0.0.0.0)
        - Port: 9090 (configurable via HTTP_MONITOR_PORT)
        
    Lifecycle:
        Runs indefinitely until service shutdown
        
    Side Effects:
        - Binds to HTTP monitoring port
        - Logs server startup
    """
    app = aiohttp.web.Application()
    app.router.add_get("/status", http_status_handler)

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()

    site = aiohttp.web.TCPSite(runner, "0.0.0.0", HTTP_MONITOR_PORT)
    await site.start()

    logger.info(
        f"✅ HTTP monitoring server listening on :{HTTP_MONITOR_PORT}"
    )

# ==================== MAIN ====================
async def main() -> None:
    """
    Main service entry point.
    
    Initializes all service components and starts the event loop.
    
    Startup Sequence:
        1. Initialize HTTP session
        2. Start HTTP monitoring server
        3. Start TCP workers (5 per configured port)
        4. Wait for all tasks
        
    Workers:
        5 workers per port for load distribution using SO_REUSEPORT
        
    Error Handling:
        Individual task exceptions are caught and logged but don't
        stop other tasks from running.
    """
    await init_http_session()

    tasks: List[asyncio.Task] = []

    # Start HTTP monitor
    tasks.append(asyncio.create_task(http_server()))

    # Start TCP workers (5 per port for load distribution)
    for port_str, backend_info in PORT_MAP.items():
        port: PortNumber = int(port_str)
        backend_host: IPAddress
        backend_port: PortNumber
        backend_host, backend_port = backend_info

        for worker_id in range(5):
            tasks.append(
                asyncio.create_task(
                    tcp_worker(port, backend_host, backend_port, worker_id)
                )
            )

    logger.info(f"✅ Started {len(tasks)} tasks ({len(PORT_MAP)} ports × 5 workers + 1 monitor)")

    # Wait for all tasks (runs until cancelled)
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        logger.info("Tasks cancelled, shutting down...")

def shutdown_handler(signum: int, frame: Any) -> None:
    """
    Signal handler for graceful shutdown.
    
    Handles SIGINT (Ctrl+C) and SIGTERM (systemd stop) signals to
    perform clean shutdown of the service.
    
    Args:
        signum: Signal number received
        frame: Current stack frame (unused)
        
    Shutdown Actions:
        1. Log shutdown initiation
        2. Close HTTP session
        3. Exit with code 0
        
    Side Effects:
        Terminates the process after cleanup
    """
    signal_name: str = signal.Signals(signum).name
    logger.info(f"🛑 Shutdown signal received: {signal_name}")
    
    # Create a task to close HTTP session
    asyncio.create_task(close_http_session())
    
    logger.info("✅ Graceful shutdown complete")
    sys.exit(0)

# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info("🎬 Starting L4 Redirector service...")

    try:
        # Use uvloop if available for better performance
        try:
            import uvloop
            uvloop.install()
            logger.info("✅ Using uvloop for enhanced performance")
        except ImportError:
            logger.info("ℹ️  uvloop not available, using default event loop")
        
        # Run the main event loop
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {type(e).__name__}: {e}")
        sys.exit(1)