Enterprise Layer 4 Redirector v4.1.6
Complete Technical Documentation
System Name: L4 Redirector v4.1.6 - Emergency Memory Leak Hotfix
Deployment: Production VPS (aoycrreni.localto.net)
Version: 4.1.6 (Released: January 2026)
Platform: Ubuntu Server 20.04+ LTS
Language: Python 3.8+ with uvloop
License: Enterprise Internal Use
________________________________________
Executive Summary
The Enterprise Layer 4 Redirector is a high-performance TCP/UDP reverse proxy system deployed on Ubuntu VPS infrastructure. It provides transparent Layer 4 (transport layer) packet forwarding between external clients and backend services hosted on Windows infrastructure via LocalToNet tunnel.
Key Capabilities:
	High Performance: Multi-process architecture supporting thousands of concurrent connections
	Comprehensive Monitoring: 8 distinct data streams providing real-time visibility
	Production Hardened: Memory leak fixes, automatic cleanup, health monitoring
	Protocol Support: Simultaneous TCP and UDP forwarding on multiple ports
	Zero Trust: All metrics pushed to backend API with authentication
________________________________________
Table of Contents
	System Architecture
	Network Topology
	Core Components
	Data Flow Analysis
	Eight Data Streams
	Process Architecture
	Configuration Reference
	Deployment Guide
	Operations Manual
	Monitoring & Metrics
	Troubleshooting Guide
	Performance Tuning
	Security Considerations
	API Reference
________________________________________
1. System Architecture
1.1 High-Level Overview
┌─────────────────────────────────────────────────────────────────────┐
│ INTERNET CLIENTS │
│ (Public IPs from anywhere) │
└───────────────────────────┬─────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────┐
│ UBUNTU VPS SERVER │
│ (aoycrreni.localto.net) │
│ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ L4 REDIRECTOR v4.1.6 │ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│ │ │ Port 8041│ │ Port 8047│ │ Port 8057│ │ │
│ │ │ TCP+UDP │ │ TCP+UDP │ │ TCP+UDP │ │ │
│ │ └────┬─────┘ └────┬─────┘ └────┬─────┘ │ │
│ │ │ │ │ │ │
│ │ └─────────────┴─────────────┘ │ │
│ │ │ │ │
│ │ ┌──────▼──────┐ │ │
│ │ │ Multi-Worker│ │ │
│ │ │ Forwarding │ │ │
│ │ │ Engine │ │ │
│ │ └──────┬──────┘ │ │
│ │ │ │ │
│ │ ┌─────────────┴──────────────┐ │ │
│ │ │ │ │ │
│ │ ┌────▼─────┐ ┌──────▼─────┐ │ │
│ │ │ Health │ │ Metrics │ │ │
│ │ │ Monitor │ │ Collection │ │ │
│ │ └──────────┘ └──────┬─────┘ │ │
│ │ │ │ │
│ │ ┌──────▼─────┐ │ │
│ │ │ HTTP API │ │ │
│ │ │ :9090 │ │ │
│ │ └────────────┘ │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ │ │
└────────────────────────────┼────────────────────────────────────────┘
│
│ LocalToNet Tunnel
│ 111.111.11.111:6921
▼
┌─────────────────────────────────────────────────────────────────────┐
│ WINDOWS BACKEND SERVER │
│ (192.168.88.16:5814) │
│ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Backend API v4 + PostgreSQL │ │
│ │ │ │
│ │ ┌──────────────┐ ┌──────────────┐ │ │
│ │ │ FastAPI │────────▶│ PostgreSQL │ │ │
│ │ │ :5814 │ │ Database │ │ │
│ │ └──────────────┘ └──────────────┘ │ │
│ │ │ │ │
│ │ ├─ 8 API Endpoints │ │
│ │ ├─ Data Ingestion │ │
│ │ ├─ Real-time Storage │ │
│ │ └─ Grafana Integration │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ACTUAL BACKEND SERVICES │ │
│ │ ┌────────────┐ ┌────────────┐ ┌────────────┐ │ │
│ │ │129.151. │ │129.151. │ │129.151. │ │ │
│ │ │142.36:1429 │ │142.36:8667 │ │142.36:7798 │ │ │
│ │ └────────────┘ └────────────┘ └────────────┘ │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
1.2 Design Principles
Stateless Forwarding:
	No session state maintained in redirector
	Pure packet forwarding with metrics collection
	Connection state only exists during active transfer
Multi-Process Parallelism:
	Independent worker processes per port
	CPU-count × 4 workers per port for maximum throughput
	Process isolation prevents cascading failures
Comprehensive Observability:
	8 distinct telemetry streams
	Real-time metrics pushed to backend API
	Prometheus-compatible metrics endpoint
Memory Safety:
	Fixed circular buffers (no unbounded growth)
	Aggressive cleanup every 30 seconds
	Process restart on memory threshold breach
________________________________________
2. Network Topology
2.1 Traffic Flow Path
Client Request Flow (TCP):
──────────────────────────────
	Client → VPS:8041
├─ TCP SYN packet arrives at Ubuntu VPS
└─ Captured by L4 Redirector listening socket
	Redirector → LocalToNet Gateway
├─ New connection to 111.111.11.111:6921
├─ Latency measured (backend_latency_ms)
└─ Tunnel established through NAT
	LocalToNet → Windows Backend
├─ Tunnel routes to 192.168.88.16:5814
├─ Windows firewall allows from L2N gateway
└─ Backend API receives on :5814
	Backend API → Real Service
├─ API proxies to 222.222.22.222:1429
└─ Actual service processes request
	Response Path (Reverse)
└─ 1429 → API → L2N → VPS → Client
2.2 Port Mapping Configuration
VPS Port	LocalToNet Gateway	Windows Backend API	Final Destination	Protocol
8041	111.111.11.111:6921	192.168.88.16:5814	222.222.22.222:1429	TCP+UDP
8047	111.111.11.111:6921	192.168.88.16:5814	222.222.22.222:8667	TCP+UDP
8057	111.111.11.111:6921	192.168.88.16:5814	222.222.22.222:7798	TCP+UDP

2.3 LocalToNet Tunnel Architecture
Tunnel Purpose:
	Bypass NAT/firewall restrictions on Windows server
	Provide stable public endpoint for VPS connection
	Handle network interruptions gracefully
Tunnel Characteristics:
	Protocol: TCP-based tunnel with keepalive
	Gateway: 111.111.11.111:6921 (LocalToNet infrastructure)
	Target: 192.168.88.16:5814 (Windows Backend API)
	Latency: Typically 20-50ms overhead
Why This Design:
	Windows server behind NAT (cannot accept direct inbound)
	VPS has public IP but needs to reach private network
	LocalToNet provides persistent tunnel with authentication
________________________________________
3. Core Components
3.1 Component Hierarchy
l4_redirector_v4.py (Main Process)
│
├─ Configuration Module
│ ├─ PORT_MAP (port → target mapping)
│ ├─ System tuning (ulimits, buffer sizes)
│ └─ API credentials
│
├─ Logging System
│ ├─ Rotating file logs (/var/log/redirector/)
│ └─ Console output (INFO level)
│
├─ Shared State (Multiprocessing Manager)
│ ├─ WORKER_STATS (per-worker metrics)
│ ├─ GLOBAL_STATS (aggregate counters)
│ ├─ MONITOR_STATE (health check results)
│ ├─ LATENCY_HISTOGRAM (latency distribution)
│ ├─ CONNECTION_EVENTS (event log buffer)
│ ├─ PERFORMANCE_METRICS (p50/p95/p99)
│ └─ THROUGHPUT_WINDOW (rate calculation)
│
├─ Process Pool
│ ├─ Monitor Process (health checks)
│ ├─ Cleanup Process (memory management)
│ ├─ HTTP Server Process (:9090)
│ ├─ TCP Workers (CPU × 4 × 3 ports)
│ └─ UDP Workers (1 per port)
│
└─ Backend API Client
└─ Async HTTP client with retry logic
3.2 TCP Worker Architecture
Worker Lifecycle:
Initialization Phase
	Raise file descriptor limits (1M)
	Initialize worker stats dictionary
	Create TCP listening socket (SO_REUSEPORT)
	Enter accept() loop
Connection Handling Phase
	Accept client connection
	Measure backend connection latency
	Start bidirectional forwarding (asyncio.gather)
	Stream data with buffer management
	Collect metrics (bytes, duration, latency)
	Close both connections gracefully
Metrics Publishing Phase
	Push web connection metrics (Stream 1)
	Push L2N tunnel metrics (Stream 2)
	Update latency histograms
	Log connection event (Stream 8)
Worker Process Isolation:
	Each worker is independent Python process
	SO_REUSEPORT allows kernel-level load balancing
	Worker crash doesn't affect other workers
	Process supervision in main loop
3.3 UDP Relay System
UDP Challenge:
	Connectionless protocol (no stream)
	Request/response pattern with 30ms timeout
	No persistent state between datagrams
Relay Implementation:
class UDPRelay(asyncio.DatagramProtocol):
def datagram_received(self, data, addr):
# 1. Receive UDP packet from client
# 2. Forward to backend (sync socket)
# 3. Wait 30ms for response
# 4. Forward response back to client
# 5. Close temporary socket
UDP vs TCP Differences:
	TCP: Persistent connection with streaming
	UDP: Per-packet forwarding with timeout
	TCP: Full bidirectional pipe with flow control
	UDP: Fire-and-forget with optional response
3.4 Health Monitoring System
Monitor Process Responsibilities:
Every 10 seconds:
├─ Check TCP connectivity to each backend
│ ├─ Attempt connection with 2s timeout
│ ├─ Measure connection latency
│ └─ Record status (up/down/error)
│
├─ Check UDP responsiveness
│ ├─ Send health datagram
│ └─ Record success/failure
│
└─ Push health status to API (Stream 7)
└─ Backend stores in port_health table
Health Check Flow:
async def check_target_tcp(port):
start = time.time()
try:
reader, writer = await asyncio.wait_for(
asyncio.open_connection(target_ip, target_port),
timeout=2.0
)
latency_ms = int((time.time() - start) * 1000)
writer.close()
return {"status": "up", "latency_ms": latency_ms}
except Exception as e:
return {"status": "down", "error": str(e)}
3.5 Memory Cleanup System
Critical Fix (v4.1.6):
	Problem: Task backlog accumulation (1.8GB in 2 minutes)
	Root Cause: asyncio.create_task() inside stats_lock
	Solution: Collect data inside lock, await tasks outside lock
Cleanup Process Flow:
Every 30 seconds:
├─ Collect metrics snapshots (inside lock, fast)
│ ├─ Throughput window data
│ ├─ Performance metrics (latencies)
│ ├─ Connection events buffer
│ └─ Worker health stats
│
├─ Create API push tasks (list of awaitables)
│ ├─ Stream 4: Performance metrics
│ ├─ Stream 5: Throughput stats
│ ├─ Stream 6: Worker status
│ └─ Stream 8: Event logs
│
├─ Await all tasks concurrently (outside lock)
│ └─ asyncio.gather(*tasks)
│
└─ Reset circular buffers (inside lock, fast)
├─ Clear throughput windows
├─ Reset connection counters
└─ Maintain memory target (7-10MB)
________________________________________
4. Data Flow Analysis
4.1 Connection Establishment
TIME ACTION STATE
────── ────────────────────────────────── ─────────────────────
0ms Client connects to VPS:8041 TCP SYN received
1ms Worker accepts connection Socket created
2ms Worker stats incremented active_tcp++
Global counter incremented total_connections++
Throughput window updated connections++
5ms Backend connection initiated Connecting...
25ms Backend connection established Latency: 20ms
Tunnel metrics recorded backend_latency_ms
Latency histogram updated buckets[25]++
26ms Bidirectional forwarding starts Streaming data
Pipe tasks launched (in/out) asyncio.gather()
... Data transfer ongoing Bytes counted
Bytes_in/bytes_out tracked Per worker + global
Throughput window accumulates Real-time rates
5000ms Client closes connection TCP FIN
Pipes terminate gracefully Both directions stop
Duration calculated 4995ms
Connection event logged Stream 8
5001ms Metrics pushed to API All 8 streams
/api/v1/web/8041 Stream 1
/api/v1/l2n/8041 Stream 2
Performance metrics updated Stream 4
Event log appended Stream 8
5002ms Worker stats decremented active_tcp--
Resources freed Sockets closed
Worker ready for next connection Waiting...
4.2 Data Stream Timing
Metric Collection Points:
────────────────────────────
Connection Start (Time 0):
├─ Connection metadata captured
│ ├─ Client IP, port
│ ├─ Timestamp (UTC ISO 8601)
│ └─ Worker ID
Backend Connection (Time 0 + latency):
├─ Tunnel establishment latency measured
├─ Backend IP/port recorded
└─ Latency histogram updated (live)
During Transfer (Continuous):
├─ Bytes in/out counted (per buffer read)
├─ Throughput window accumulates
└─ Duration counter running
Connection End (Time 0 + duration):
├─ Final metrics calculated
├─ API push tasks created
└─ Metrics sent asynchronously
Cleanup Cycle (Every 30s):
├─ Aggregate metrics published
├─ Percentile calculations (p50/p95/p99)
├─ Event log flushed
└─ Throughput rates computed
4.3 Metrics Aggregation Pipeline
Raw Event → Buffer → Aggregation → Push → Storage
────────────────────────────────────────────────────
Example: TCP Connection Latency
	Connection established in 23ms
↓
	Recorded in LATENCY_HISTOGRAM[8041]
├─ buckets[25] += 1 (23ms falls in ≤25ms bucket)
├─ count += 1
├─ sum += 23
├─ min = min(existing, 23)
└─ max = max(existing, 23)
↓
	Also added to PERFORMANCE_METRICS[8041]
└─ latencies.append(23) (circular buffer, max 1000)
↓
	Every 30s cleanup cycle:
├─ Sort latencies: [12, 15, 18, 23, 27, 30, 45, ...]
├─ Calculate p50: latencies[n * 0.50]
├─ Calculate p95: latencies[n * 0.95]
└─ Calculate p99: latencies[n * 0.99]
↓
	Push to API (Stream 4):
POST /api/v1/performance/8041
{
"p50": 23,
"p95": 45,
"p99": 78,
"min": 12,
"max": 95,
"sample_count": 1000
}
↓
	Backend API stores in performance_metrics table
↓
	Grafana queries PostgreSQL for visualization
________________________________________
5. Eight Data Streams
Stream 1: Web Traffic Metrics (/api/v1/web/{port})
Purpose: Track client-side connection characteristics
Triggered: On connection close (per connection)
Payload Example:
{
"timestamp": "2026-01-31T08:47:15.234Z",
"client_ip": "203.0.113.45",
"client_port": 52341,
"bytes_in": 45678,
"bytes_out": 123456,
"duration_ms": 4523,
"worker_id": "tcp_8041_2",
"connection_id": "203.0.113.45:52341_1738315635234"
}
Database Table: web_connections
Use Cases:
	Client geographic analysis (by IP)
	Connection duration distribution
	Bandwidth consumption per client
	Worker load distribution
________________________________________
Stream 2: L2N Tunnel Metrics (/api/v1/l2n/{port})
Purpose: Track LocalToNet tunnel performance and backend latency
Triggered: On connection close (per connection)
Payload Example:
{
"timestamp": "2026-01-31T08:47:15.234Z",
"backend_ip": "222.222.22.222",
"backend_port": 1429,
"duration_ms": 4523,
"latency_ms": 23,
"worker_id": "tcp_8041_2",
"tunnel_status": "closed",
"localtonet_gateway": "111.111.11.111:6921",
"bytes_transferred": 169134
}
Database Table: l2n_connections
Use Cases:
	Tunnel latency monitoring
	Backend service availability
	LocalToNet gateway performance
	Correlation with web traffic (same connection)
________________________________________
Stream 3: Connection Errors (/api/v1/errors/l2n/{port})
Purpose: Capture connection failures and timeouts
Triggered: On connection establishment failure
Payload Example:
{
"timestamp": "2026-01-31T08:50:23.456Z",
"error_type": "connection_timeout",
"backend_ip": "222.222.22.222",
"backend_port": 1429,
"client_ip": "203.0.113.45",
"client_port": 52341,
"error_message": "Timeout connecting to 222.222.22.222:1429",
"worker_id": "tcp_8041_2"
}
Database Table: l2n_errors
Error Types:
	connection_timeout: Backend unreachable within 3s
	connection_error: Socket errors, network failures
	tunnel_failure: LocalToNet gateway issues
Use Cases:
	Failure rate monitoring
	Backend outage detection
	Client impact analysis
	Root cause investigation
________________________________________
Stream 4: Performance Metrics (/api/v1/performance/{port})
Purpose: Latency percentile analysis (p50/p95/p99)
Triggered: Every 30 seconds (cleanup cycle)
Payload Example:
{
"timestamp": "2026-01-31T08:47:30.000Z",
"port": 8041,
"p50": 23,
"p95": 45,
"p99": 78,
"min": 12,
"max": 95,
"sample_count": 847
}
Database Table: performance_metrics
Calculation Method:
latencies = list(PERFORMANCE_METRICS[port]["latencies"])
latencies.sort()
n = len(latencies)
p50 = latencies[int(n * 0.50)]
p95 = latencies[int(n * 0.95)]
p99 = latencies[int(n * 0.99)]
Use Cases:
	SLA compliance monitoring (e.g., p95 < 50ms)
	Performance regression detection
	Capacity planning
	Alerting on latency spikes
________________________________________
Stream 5: Throughput Statistics (/api/v1/throughput/{port})
Purpose: Real-time bandwidth and connection rate analysis
Triggered: Every 30 seconds (cleanup cycle)
Payload Example:
{
"timestamp": "2026-01-31T08:47:30.000Z",
"port": 8041,
"bytes_per_sec": 2456789,
"connections_per_sec": 45.67,
"total_bytes_in": 35678901,
"total_bytes_out": 67890123,
"total_connections": 1370
}
Database Table: throughput_stats
Calculation:
elapsed = time.time() - window["window_start"]
bytes_per_sec = (bytes_in + bytes_out) / elapsed
connections_per_sec = connections / elapsed
Use Cases:
	Real-time bandwidth monitoring
	Traffic pattern analysis
	DDoS detection (abnormal connection rates)
	Capacity utilization tracking
________________________________________
Stream 6: Worker Health (/api/v1/workers/status)
Purpose: Per-worker resource usage and health metrics
Triggered: Every 30 seconds (cleanup cycle)
Payload Example:
{
"timestamp": "2026-01-31T08:47:30.000Z",
"workers": {
"tcp_8041_0": {
"active_tcp": 23,
"total_tcp": 1547,
"bytes_in": 45678901,
"bytes_out": 78901234,
"uptime_sec": 86400,
"last_activity": 1738315650.123
},
"tcp_8041_1": { ... },
...
},
"worker_count": 24
}
Database Table: worker_stats
Use Cases:
	Worker load balancing analysis
	Process health monitoring
	Resource exhaustion detection
	Worker crash investigation
________________________________________
Stream 7: Port Health Status (/api/v1/health/{port})
Purpose: Backend service availability and latency
Triggered: Every 10 seconds (health check cycle)
Payload Example:
{
"timestamp": "2026-01-31T08:47:20.000Z",
"port": 8041,
"tcp_status": "up",
"tcp_latency_ms": 23,
"udp_status": "up",
"uptime_sec": 86400
}
Database Table: port_health
Status Values:
	up: Service responding normally
	down: Connection failed
	unknown: Not yet checked
Use Cases:
	Service availability dashboard
	Uptime SLA reporting
	Alerting on service outages
	Historical availability analysis
________________________________________
Stream 8: Connection Events (/api/v1/events/{port})
Purpose: Recent connection lifecycle events (circular log)
Triggered: Every 30 seconds (cleanup cycle)
Payload Example:
{
"timestamp": "2026-01-31T08:47:30.000Z",
"port": 8041,
"events": [
{
"timestamp": "2026-01-31T08:47:15.234Z",
"event": "connection_closed",
"client": "203.0.113.45:52341",
"duration_ms": 4523,
"latency_ms": 23,
"bytes_transferred": 169134
},
{ ... }
],
"count": 45
}
Database Table: connection_events
Event Types:
	connection_closed: Normal closure
	connection_timeout: Timeout during transfer
	connection_error: Unexpected error
Buffer Size: 50 events per port (circular buffer)
Use Cases:
	Real-time activity feed
	Debugging specific connections
	Event correlation analysis
	Audit trail for security investigations
________________________________________
6. Process Architecture
6.1 Process Hierarchy
Main Process (PID 12345)
│
├─ Monitor Process (PID 12346)
│ └─ Health checks every 10s
│
├─ Cleanup Process (PID 12347)
│ └─ Memory management every 30s
│
├─ HTTP Server (PID 12348)
│ └─ API on :9090
│
├─ TCP Workers - Port 8041
│ ├─ Worker 0 (PID 12349)
│ ├─ Worker 1 (PID 12350)
│ ├─ Worker 2 (PID 12351)
│ ├─ Worker 3 (PID 12352)
│ ├─ Worker 4 (PID 12353)
│ ├─ Worker 5 (PID 12354)
│ ├─ Worker 6 (PID 12355)
│ └─ Worker 7 (PID 12356) [Total: CPU × 4 = 8 workers]
│
├─ TCP Workers - Port 8047
│ └─ [8 workers, PIDs 12357-12364]
│
├─ TCP Workers - Port 8057
│ └─ [8 workers, PIDs 12365-12372]
│
├─ UDP Relay - Port 8041 (PID 12373)
├─ UDP Relay - Port 8047 (PID 12374)
└─ UDP Relay - Port 8057 (PID 12375)
Total Processes: 1 main + 3 system + 24 TCP + 3 UDP = 31 processes
6.2 Inter-Process Communication
Multiprocessing Manager (Shared State):
manager = multiprocessing.Manager()
Shared dictionaries (thread-safe with locks)
WORKER_STATS = manager.dict()
GLOBAL_STATS = manager.dict()
MONITOR_STATE = manager.dict()
LATENCY_HISTOGRAM = manager.dict()
CONNECTION_EVENTS = manager.dict()
PERFORMANCE_METRICS = manager.dict()
THROUGHPUT_WINDOW = manager.dict()
Synchronization
stats_lock = manager.Lock()
Lock Usage Patterns:
✅ CORRECT: Minimal critical section
with stats_lock:
# Fast read/write of shared state
WORKER_STATS[worker_id]["active_tcp"] += 1
snapshot = dict(WORKER_STATS[worker_id])
Slow I/O operations OUTSIDE lock
await push_to_backend(endpoint, snapshot)
❌ WRONG: Holding lock during I/O (v4.1.5 bug!)
with stats_lock:
data = dict(WORKER_STATS[worker_id])
await push_to_backend(endpoint, data) # Deadlock risk!
6.3 Process Supervision
Main Process Responsibilities:
while True:
time.sleep(5)
alive = [p for p in processes if p.is_alive()]
if len(alive) < len(processes):
    # Process crashed!
    logger.warning(f"⚠️ Process crashed! ({len(alive)}/{len(processes)})")
    # Manual restart required (future: auto-restart)

Process Restart Strategy:
	Current: Manual restart via systemd
	Future: Automatic process respawn with exponential backoff
	Rationale: Crash should trigger investigation, not silent restart
6.4 Graceful Shutdown
try:
# Main process blocks here
await asyncio.Event().wait()
except KeyboardInterrupt:
logger.info("⏹️ Shutting down...")
finally:
# Terminate all child processes
for p in processes:
if p.is_alive():
p.terminate() # Send SIGTERM
# Wait up to 5s for clean shutdown
for p in processes:
    p.join(timeout=5)
    if p.is_alive():
        p.kill()  # Force kill with SIGKILL

Clean Shutdown Sequence:
	SIGTERM received (Ctrl+C or systemd stop)
	Main process logs shutdown message
	All child processes sent SIGTERM
	5-second grace period for cleanup
	Force kill any remaining processes
	Log final statistics
________________________________________
7. Configuration Reference
7.1 Network Configuration
Listening Configuration
LISTEN_IP = "0.0.0.0" # Bind to all interfaces
Backend Tunnel Configuration
LOCALTONET_IP = "111.111.11.111"
LOCALTONET_PORT = 6921
BACKEND_API_URL = f"http://{LOCALTONET_IP}:{LOCALTONET_PORT}"
Port Forwarding Rules
PORT_MAP = {
8041: ("222.222.22.222", 1429), # VPS:8041 → Backend:1429
8047: ("222.222.22.222", 8667), # VPS:8047 → Backend:8667
8057: ("222.222.22.222", 7798), # VPS:8057 → Backend:7798
}
Modifying Port Configuration:
1. Edit configuration
sudo nano /usr/local/bin/l4_redirector_v4.py
2. Modify PORT_MAP
PORT_MAP = {
8041: ("NEW_IP", NEW_PORT),
# Add new ports as needed
}
3. Restart service
sudo systemctl restart l4-redirector
7.2 Performance Tuning
Connection Limits
TCP_BACKLOG = 65535 # Listen queue depth
BUFFER_SIZE = 65536 # Read/write buffer (64KB)
UDP_TIMEOUT = 0.03 # 30ms UDP response timeout
API Configuration
API_PUSH_TIMEOUT = 3000 # 3 seconds (in milliseconds)
API_RETRY_COUNT = 2 # Retry failed API calls twice
API_RETRY_DELAY = 100 # 100ms delay between retries
Health Monitoring
HEALTH_CHECK_INTERVAL = 10 # 10 seconds between checks
HEALTH_CHECK_TIMEOUT = 3000 # 3 seconds per check
Memory Management
MEMORY_CLEANUP_INTERVAL = 30 # 30 seconds cleanup cycle
CONNECTION_HISTORY_SIZE = 100 # Connections per worker
EVENT_LOG_SIZE = 50 # Events per port
Tuning Recommendations:
Scenario	Adjust	Reason
High connection rate	Increase TCP_BACKLOG	Prevent SYN drops
Large file transfers	Increase BUFFER_SIZE	Better throughput
Slow backend	Increase API_PUSH_TIMEOUT	Prevent metric loss
Limited memory	Decrease EVENT_LOG_SIZE	Reduce buffer size
Debugging	Decrease HEALTH_CHECK_INTERVAL	Faster failure detection

7.3 Security Configuration
API Authentication
BACKEND_API_TOKEN = "e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"
API_AUTH_TOKEN = "AbDo@2020!"
Security Best Practices:
	Token Rotation:
Generate new token
TOKEN=$(openssl rand -hex 32)
Update in redirector
sudo nano /usr/local/bin/l4_redirector_v4.py
Update BACKEND_API_TOKEN
Update in backend API
Update Windows backend_api_v4.py VALID_TOKENS
	Firewall Rules:
Allow only necessary ports
sudo ufw allow 8041/tcp
sudo ufw allow 8041/udp
sudo ufw allow 8047/tcp
sudo ufw allow 8047/udp
sudo ufw allow 8057/tcp
sudo ufw allow 8057/udp
Restrict monitoring port
sudo ufw allow from 192.168.88.0/24 to any port 9090
	File Permissions:
sudo chmod 750 /usr/local/bin/l4_redirector_v4.py
sudo chmod 640 /etc/systemd/system/l4-redirector.service
7.4 Logging Configuration
def setup_logging():
log_dir = "/var/log/redirector"
main_log = os.path.join(log_dir, "l4_redirector_v4_enterprise.log")
# Rotating file handler
fh = RotatingFileHandler(
    main_log,
    maxBytes=100*1024*1024,  # 100MB per file
    backupCount=10           # Keep 10 backups (1GB total)
)

Log Rotation Management:
Manual log rotation
sudo logrotate -f /etc/logrotate.d/l4-redirector
View current logs
sudo tail -f /var/log/redirector/l4_redirector_v4_enterprise.log
View archived logs
sudo ls -lh /var/log/redirector/.log
________________________________________
8. Deployment Guide
8.1 System Requirements
Minimum Requirements:
	OS: Ubuntu 20.04 LTS or newer
	CPU: 2 cores (4 cores recommended)
	RAM: 2GB (4GB recommended)
	Disk: 20GB (100GB for logs if high traffic)
	Network: 1Gbps interface
Software Dependencies:
Python 3.8+
python3 --version
Required packages
pip3 install asyncio aiohttp uvloop psutil
8.2 Installation Steps
Step 1: Install Dependencies
Update system
sudo apt update && sudo apt upgrade -y
Install Python and pip
sudo apt install python3 python3-pip -y
Install required Python packages
sudo pip3 install aiohttp uvloop psutil
Step 2: Create System User
Create dedicated user (optional, but recommended)
sudo useradd -r -s /bin/false redirector
Step 3: Deploy Script
Copy script to system location
sudo cp l4_redirector_v4.py /usr/local/bin/
sudo chmod 750 /usr/local/bin/l4_redirector_v4.py
sudo chown root:root /usr/local/bin/l4_redirector_v4.py
Create log directory
sudo mkdir -p /var/log/redirector
sudo chown root:root /var/log/redirector
sudo chmod 755 /var/log/redirector
Step 4: Configure Systemd Service
Create service file
sudo nano /etc/systemd/system/l4-redirector.service
[Unit]
Description=Enterprise L4 Redirector v4.1.6
After=network.target
Wants=network-online.target
[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/bin/python3 /usr/local/bin/l4_redirector_v4.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=l4-redirector
Resource limits
LimitNOFILE=1048576
LimitNPROC=4096
Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/redirector
[Install]
WantedBy=multi-user.target
Step 5: Enable and Start Service
Reload systemd
sudo systemctl daemon-reload
Enable service (start on boot)
sudo systemctl enable l4-redirector
Start service
sudo systemctl start l4-redirector
Check status
sudo systemctl status l4-redirector
8.3 Verification Steps
Check Service Status:
Service health
sudo systemctl status l4-redirector
View logs
sudo journalctl -u l4-redirector -f
Check listening ports
sudo ss -tulnp | grep python3
Expected output:
tcp LISTEN 0 65535 0.0.0.0:8041 0.0.0.0:* users:(("python3",pid=XXX))
tcp LISTEN 0 65535 0.0.0.0:8047 0.0.0.0:* users:(("python3",pid=XXX))
tcp LISTEN 0 65535 0.0.0.0:8057 0.0.0.0:* users:(("python3",pid=XXX))
tcp LISTEN 0 128 0.0.0.0:9090 0.0.0.0:* users:(("python3",pid=XXX))
Test Connectivity:
Test TCP connectivity
nc -zv aoycrreni.localto.net 8041
nc -zv aoycrreni.localto.net 8047
nc -zv aoycrreni.localto.net 8057
Test HTTP monitoring API
curl -H "Authorization: Bearer AbDo@2020!" http://localhost:9090/health
Expected response:
{"status": "ok", "version": "4.1.6-hotfix", "timestamp": "2026-01-31T08:47:15.234Z"}
Test Backend Integration:
Check if metrics are being pushed
curl -H "Authorization: Bearer AbDo@2020!" http://localhost:9090/status | jq .
Verify on Windows backend
Query PostgreSQL: SELECT COUNT(*) FROM web_connections;
8.4 Troubleshooting Deployment
Issue: Service fails to start
Check logs
sudo journalctl -u l4-redirector -n 50
Common causes:
1. Port already in use
sudo ss -tulnp | grep :8041
2. Permission denied
sudo chmod +x /usr/local/bin/l4_redirector_v4.py
3. Python dependencies missing
sudo pip3 install -r requirements.txt
Issue: High memory usage
Check memory usage
ps aux | grep python3
If memory > 100MB:
1. Check for task backlog (fixed in v4.1.6)
2. Reduce buffer sizes in config
3. Restart service
sudo systemctl restart l4-redirector
________________________________________
9. Operations Manual
9.1 Daily Operations
Morning Checklist:
1. Check service health
sudo systemctl status l4-redirector
2. Review overnight logs
sudo journalctl -u l4-redirector --since "yesterday" | grep -i error
3. Check resource usage
free -h
df -h /var/log
top -b -n 1 | grep python3
4. Verify API connectivity
curl -H "Authorization: Bearer AbDo@2020!" http://localhost:9090/status
Monitoring Commands:
Real-time status
watch -n 2 'curl -s -H "Authorization: Bearer AbDo@2020!" http://localhost:9090/status | jq .'
Connection count
sudo ss -tn | grep -E ":(8041|8047|8057)" | wc -l
Process tree
pstree -p $(pgrep -f l4_redirector_v4.py | head -1)
Network throughput
sudo iftop -i eth0 -f "port 8041 or port 8047 or port 8057"
9.2 Maintenance Procedures
Restarting Service:
Graceful restart
sudo systemctl restart l4-redirector
Force restart (if hung)
sudo systemctl kill -s SIGKILL l4-redirector
sudo systemctl start l4-redirector
Log Management:
Archive old logs
sudo tar -czf /backup/redirector-logs-$(date +%Y%m%d).tar.gz /var/log/redirector/.log.
Clear old logs (keeps last 7 days)
sudo find /var/log/redirector -name ".log." -mtime +7 -delete
Check log disk usage
sudo du -sh /var/log/redirector/
Configuration Updates:
1. Backup current config
sudo cp /usr/local/bin/l4_redirector_v4.py /backup/l4_redirector_v4.py.$(date +%Y%m%d)
2. Edit configuration
sudo nano /usr/local/bin/l4_redirector_v4.py
3. Validate syntax
python3 -m py_compile /usr/local/bin/l4_redirector_v4.py
4. Restart service
sudo systemctl restart l4-redirector
5. Verify no errors
sudo journalctl -u l4-redirector -f
9.3 Performance Monitoring
Key Metrics to Track:
Metric	Command	Target	Alert Threshold
Memory Usage	ps aux \| grep python3	< 50MB	> 100MB
Process Count	pgrep -c python3	31	< 30
Connection Rate	ss -tn \| grep :8041 \| wc -l	Varies	> 5000
Log Growth	du -sh /var/log/redirector	< 10GB	> 50GB
API Response	curl localhost:9090/health	< 100ms	> 1s

Setting Up Alerts:
Create monitoring script
sudo nano /usr/local/bin/check-redirector.sh
#!/bin/bash
Check if service is running
if ! systemctl is-active --quiet l4-redirector; then
echo "ALERT: L4 Redirector service is DOWN!"
# Send notification (email, Slack, etc.)
fi
Check memory usage
MEM=$(ps aux | grep l4_redirector_v4.py | grep -v grep | awk '{sum+=$6} END {print sum/1024}')
if (( (echo"MEM > 100" | bc -l) )); then
echo "ALERT: High memory usage: ${MEM}MB"
fi
Check process count
PROCS=(pgrep-fl4_r edirector_v 4.py|wc-l)if["PROCS" -lt 30 ]; then
echo "ALERT: Low process count: $PROCS (expected 31)"
fi
Make executable
sudo chmod +x /usr/local/bin/check-redirector.sh
Add to cron (every 5 minutes)
sudo crontab -e
Add line:
*/5 * * * * /usr/local/bin/check-redirector.sh >> /var/log/redirector-alerts.log 2>&1
9.4 Backup and Recovery
Backup Strategy:
Create backup script
sudo nano /usr/local/bin/backup-redirector.sh
#!/bin/bash
BACKUP_DIR="/backup/redirector"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
Create backup directory
mkdir -p $BACKUP_DIR
Backup script
cp /usr/local/bin/l4_redirector_v4.py BACKUP_D IR/l4_r edirector_v 4.py.TIMESTAMP
Backup service file
cp /etc/systemd/system/l4-redirector.service BACKUP_D IR/l4-redirector.service.TIMESTAMP
Backup recent logs
tar -czf BACKUP_D IR/logs-TIMESTAMP.tar.gz /var/log/redirector/l4_redirector_v4_enterprise.log
Keep only last 30 days of backups
find $BACKUP_DIR -name ".py." -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
echo "Backup completed: $TIMESTAMP"
Recovery Procedure:
1. Stop service
sudo systemctl stop l4-redirector
2. Restore from backup
sudo cp /backup/redirector/l4_redirector_v4.py.YYYYMMDD /usr/local/bin/l4_redirector_v4.py
3. Restore service file
sudo cp /backup/redirector/l4-redirector.service.YYYYMMDD /etc/systemd/system/l4-redirector.service
4. Reload systemd
sudo systemctl daemon-reload
5. Start service
sudo systemctl start l4-redirector
6. Verify
sudo systemctl status l4-redirector
________________________________________
10. Monitoring & Metrics
10.1 Prometheus Metrics Endpoint
Accessing Metrics:
curl -H "Authorization: Bearer AbDo@2020!" http://localhost:9090/metrics
Metrics Format:
Worker-level metrics
redirector_worker_active_tcp{worker_id="tcp_8041_0"} 23
redirector_worker_total_tcp{worker_id="tcp_8041_0"} 1547
redirector_worker_bytes_in{worker_id="tcp_8041_0"} 45678901
redirector_worker_bytes_out{worker_id="tcp_8041_0"} 78901234
Global counters
redirector_total_connections 45678
redirector_total_bytes_in 123456789
redirector_total_bytes_out 234567890
redirector_backend_pushes 8934
redirector_backend_push_failures 23
Latency histograms (cumulative buckets)
redirector_tcp_latency_ms_bucket{port="8041",le="10"} 234
redirector_tcp_latency_ms_bucket{port="8041",le="25"} 567
redirector_tcp_latency_ms_bucket{port="8041",le="50"} 890
redirector_tcp_latency_ms_bucket{port="8041",le="100"} 1200
redirector_tcp_latency_ms_bucket{port="8041",le="+Inf"} 1547
redirector_tcp_latency_ms_count{port="8041"} 1547
redirector_tcp_latency_ms_sum{port="8041"} 38765
10.2 Status API Endpoint
Full Status Query:
curl -H "Authorization: Bearer AbDo@2020!" http://localhost:9090/status | jq .
Response Structure:
{
"ports": {
"8041": {
"status": "up",
"latency_ms": 23,
"udp_status": "up",
"checked_at": 1738315650
},
"8047": { ... },
"8057": { ... }
},
"workers": {
"tcp_8041_0": {
"active_tcp": 23,
"total_tcp": 1547,
"bytes_in": 45678901,
"bytes_out": 78901234,
"uptime_sec": 86400,
"last_activity": 1738315650.123
},
...
},
"global": {
"total_connections": 45678,
"total_bytes_in": 123456789,
"total_bytes_out": 234567890,
"backend_pushes": 8934,
"backend_push_failures": 23
},
"system": {
"cpu_percent": 15.2,
"load_avg": [1.2, 1.5, 1.8],
"ram": {
"total": 4294967296,
"available": 2147483648,
"percent": 50.0
},
"uptime_sec": 86400,
"net": {
"bytes_sent": 123456789,
"bytes_recv": 234567890
}
},
"timestamp": "2026-01-31T08:47:15.234Z"
}
10.3 Grafana Integration
Data Source Configuration:
	Prometheus (Redirector Metrics):
	URL: http://aoycrreni.localto.net:9090/metrics
	Auth: Custom header Authorization: Bearer AbDo@2020!
	Scrape interval: 10s
	PostgreSQL (Backend Data):
	Host: 192.168.88.16:5432
	Database: redirector_metrics
	User: redirector_ro (read-only)
	Query timeout: 30s
Dashboard Panels:
-- Panel: Connection Rate (Stream 1)
SELECT
date_trunc('minute', timestamp) AS time,
port,
COUNT(*) as connections_per_minute
FROM web_connections
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY time, port
ORDER BY time;
-- Panel: Latency Percentiles (Stream 4)
SELECT
timestamp AS time,
port,
p50, p95, p99
FROM performance_metrics
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY time;
-- Panel: Throughput (Stream 5)
SELECT
timestamp AS time,
port,
bytes_per_sec / 1024 / 1024 AS mbps
FROM throughput_stats
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY time;
-- Panel: Error Rate (Stream 3)
SELECT
date_trunc('minute', timestamp) AS time,
error_type,
COUNT(*) as errors
FROM l2n_errors
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY time, error_type
ORDER BY time;
10.4 Alerting Rules
Critical Alerts:
	Service Down:
	Condition: systemctl is-active l4-redirector != active
	Action: Immediate page + auto-restart
	High Error Rate:
	Condition: l2n_errors count > 100 in 5 minutes
	Action: Alert + investigate backend
	High Latency:
	Condition: p95 latency > 100ms for 10 minutes
	Action: Alert + check tunnel
	Memory Leak:
	Condition: Memory usage > 100MB for 10 minutes
	Action: Alert + restart service
Warning Alerts:
	Backend Push Failures:
	Condition: backend_push_failures > 50 in 5 minutes
	Action: Check backend API availability
	Worker Crash:
	Condition: Process count < 30
	Action: Investigate crash logs
	High CPU:
	Condition: CPU > 80% for 5 minutes
	Action: Check connection load
________________________________________
11. Troubleshooting Guide
11.1 Common Issues
Issue: Service won't start
Symptom
sudo systemctl start l4-redirector
Job for l4-redirector.service failed
Diagnosis
sudo journalctl -u l4-redirector -n 50
Common causes and fixes:
1. Port already in use
sudo ss -tulnp | grep :8041
Fix: Kill conflicting process
sudo kill -9 <PID>
2. Permission denied
Fix: Ensure running as root
sudo systemctl edit l4-redirector
Set: User=root
3. Python syntax error
Fix: Validate script
python3 -m py_compile /usr/local/bin/l4_redirector_v4.py
4. Missing dependencies
Fix: Install packages
sudo pip3 install aiohttp uvloop psutil
Issue: No metrics in Grafana
Symptom
All Grafana panels show "No data"
Diagnosis steps:
1. Check if redirector is pushing metrics
sudo journalctl -u l4-redirector | grep "backend_pushes"
2. Check backend API connectivity
curl -X POST http://111.111.11.111:6921/api/v1/health/8041 
-H "Authorization: Bearer e7595fe..."
-H "Content-Type: application/json"
-d '{"timestamp":"2026-01-31T08:47:15.234Z","port":8041,"tcp_status":"up"}'
3. Check PostgreSQL has data
On Windows:
psql -U redirector -d redirector_metrics
SELECT COUNT(*) FROM web_connections;
4. Check Grafana data source
Verify PostgreSQL connection in Grafana UI
5. Check query time ranges
If data is old, adjust "Last 1 hour" to "Last 24 hours"
Issue: High memory usage (pre-v4.1.6)
Symptom
ps aux | grep python3
Shows > 500MB RAM usage
Root cause (fixed in v4.1.6)
Task backlog accumulation in cleanup loop
Fix: Upgrade to v4.1.6+
sudo systemctl stop l4-redirector
sudo cp l4_redirector_v4.1.6.py /usr/local/bin/l4_redirector_v4.py
sudo systemctl start l4-redirector
Verify fix
ps aux | grep python3
Should show 7-10MB per process
Issue: Connection timeouts
Symptom
Clients getting connection timeouts
Diagnosis:
1. Check backend is reachable
nc -zv 111.111.11.111 6921
2. Check backend service is running (Windows)
curl http://192.168.88.16:5814/health
3. Check LocalToNet tunnel status
On Windows: Check LocalToNet client
4. Check firewall rules (VPS)
sudo ufw status
5. Check backend firewall (Windows)
netsh advfirewall firewall show rule name=all
6. Test direct connection
telnet 222.222.22.222 1429
11.2 Performance Issues
Issue: Low throughput
Diagnosis:
1. Check network interface speed
ethtool eth0 | grep Speed
2. Check buffer sizes
sysctl net.ipv4.tcp_rmem
sysctl net.ipv4.tcp_wmem
3. Check TCP window scaling
sysctl net.ipv4.tcp_window_scaling
4. Increase buffer size (if needed)
sudo nano /usr/local/bin/l4_redirector_v4.py
Change: BUFFER_SIZE = 131072 # 128KB instead of 64KB
5. Check for packet loss
ping -c 100 111.111.11.111
Look for packet loss percentage
6. Check connection count
ss -tn | grep -E ":(8041|8047|8057)" | wc -l
If > 5000, may be hitting limits
Issue: High latency
Diagnosis:
1. Check VPS → Tunnel latency
ping -c 10 111.111.11.111
2. Check Tunnel → Backend latency
On Windows: ping 192.168.88.16
3. Check backend service response time
curl -w "@curl-format.txt" http://192.168.88.16:5814/health
curl-format.txt:
time_namelookup: %{time_namelookup}\n
time_connect: %{time_connect}\n
time_starttransfer: %{time_starttransfer}\n
time_total: %{time_total}\n
4. Review Grafana latency dashboard
Check Stream 4: performance_metrics
Look for p95/p99 spikes
5. Check for CPU contention
top -b -n 1 | head -20
11.3 Debugging Techniques
Enable Debug Logging:
Edit /usr/local/bin/l4_redirector_v4.py
logger.setLevel(logging.DEBUG) # Change from INFO
Restart service
sudo systemctl restart l4-redirector
View detailed logs
sudo journalctl -u l4-redirector -f
Packet Capture:
Capture traffic on port 8041
sudo tcpdump -i eth0 -nn port 8041 -w /tmp/8041-capture.pcap
Capture for 60 seconds
timeout 60 sudo tcpdump -i eth0 -nn port 8041 -w /tmp/8041-capture.pcap
Analyze with Wireshark
wireshark /tmp/8041-capture.pcap
Connection State Inspection:
Show all connections to monitored ports
sudo ss -tnp | grep -E ":(8041|8047|8057)"
Show connection states distribution
sudo ss -tn state established | grep -E ":(8041|8047|8057)" | wc -l
sudo ss -tn state time-wait | grep -E ":(8041|8047|8057)" | wc -l
Show top client IPs
sudo ss -tn | grep -E ":(8041|8047|8057)" | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -10
Process Analysis:
Detailed process info
ps -eLf | grep python3
Thread count per process
ps -L -p $(pgrep -f l4_redirector_v4.py | head -1) | wc -l
File descriptor usage
ls -l /proc/$(pgrep -f l4_redirector_v4.py | head -1)/fd | wc -l
Check for memory leaks
pmap $(pgrep -f l4_redirector_v4.py | head -1)
________________________________________
12. Performance Tuning
12.1 System Kernel Tuning
Network Stack Optimization:
Create tuning script
sudo nano /etc/sysctl.d/99-l4-redirector.conf
TCP optimization
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.ip_local_port_range = 10000 65535
Buffer sizes
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
Connection tracking
net.netfilter.nf_conntrack_max = 1048576
net.netfilter.nf_conntrack_tcp_timeout_established = 600
File descriptors
fs.file-max = 2097152
Apply settings
sudo sysctl -p /etc/sysctl.d/99-l4-redirector.conf
Verify
sudo sysctl -a | grep -E "tcp_fin_timeout|tcp_tw_reuse"
12.2 Application-Level Tuning
Worker Count Optimization:
Current: CPU_COUNT × 4 workers per port
cpu_count = os.cpu_count() or 2
Low traffic: Reduce to CPU × 2
for i in range(cpu_count * 2):
...
High traffic: Increase to CPU × 8
for i in range(cpu_count * 8):
...
Buffer Size Tuning:
Small files/messages: 32KB
BUFFER_SIZE = 32768
Large file transfers: 128KB
BUFFER_SIZE = 131072
Ultra-high throughput: 256KB
BUFFER_SIZE = 262144
Connection Backlog:
Low traffic: 1024
TCP_BACKLOG = 1024
High traffic: 65535 (max)
TCP_BACKLOG = 65535
12.3 Monitoring and Profiling
CPU Profiling:
Install py-spy
pip3 install py-spy
Profile redirector
sudo py-spy top --pid $(pgrep -f l4_redirector_v4.py | head -1)
Generate flame graph
sudo py-spy record -o profile.svg --pid $(pgrep -f l4_redirector_v4.py | head -1)
Memory Profiling:
Track memory over time
while true; do
ps aux | grep l4_redirector_v4.py | grep -v grep | awk '{print strftime("%Y-%m-%d %H:%M:%S"), $6/1024 " MB"}'
sleep 60
done >> /tmp/memory-usage.log
Network Throughput:
Real-time bandwidth per port
sudo iftop -i eth0 -f "port 8041"
Total bandwidth
sudo iftop -i eth0 -f "port 8041 or port 8047 or port 8057"
Historical analysis (requires sysstat)
sar -n DEV 1 60
________________________________________
13. Security Considerations
13.1 Attack Surface
Exposed Services:
	Ports 8041, 8047, 8057 (TCP + UDP) - Public internet
	Port 9090 (HTTP API) - Should be internal only
Risk Mitigation:
	DDoS Protection:
Rate limiting with iptables
sudo iptables -A INPUT -p tcp --dport 8041 -m connlimit --connlimit-above 100 -j REJECT
sudo iptables -A INPUT -p tcp --dport 8041 -m limit --limit 25/sec --limit-burst 50 -j ACCEPT
	Port Knocking (Optional):
Install knockd
sudo apt install knockd
Configure knock sequence
sudo nano /etc/knockd.conf
	Firewall Hardening:
Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 8041/tcp
sudo ufw allow 8041/udp
sudo ufw allow 8047/tcp
sudo ufw allow 8047/udp
sudo ufw allow 8057/tcp
sudo ufw allow 8057/udp
Restrict monitoring port to internal network
sudo ufw allow from 192.168.88.0/24 to any port 9090
Enable firewall
sudo ufw enable
13.2 Authentication Security
Token Management:
Generate secure tokens
python3 -c "import secrets; print(secrets.token_hex(32))"
Rotate tokens quarterly
1. Generate new token
2. Update redirector config
3. Update backend API
4. Restart both services
5. Verify connectivity
Access Control:
File permissions
sudo chmod 750 /usr/local/bin/l4_redirector_v4.py # rwxr-x---
sudo chmod 640 /etc/systemd/system/l4-redirector.service # rw-r-----
Directory permissions
sudo chmod 755 /var/log/redirector # rwxr-xr-x
sudo chmod 640 /var/log/redirector/*.log # rw-r-----
13.3 Audit Logging
Connection Audit Trail:
All connections logged via Stream 1 and Stream 8:
	Client IP and port
	Timestamp (UTC)
	Duration and bytes transferred
	Backend latency
Security Events:
Stream 3 (errors) captures:
	Failed connection attempts
	Timeout events
	Backend unreachability
Log Retention:
Keep logs for 90 days
sudo nano /etc/logrotate.d/l4-redirector
/var/log/redirector/*.log {
daily
rotate 90
compress
delaycompress
missingok
notifempty
create 0640 root root
}
13.4 Security Monitoring
Anomaly Detection:
Unusual client IPs (new connections from never-seen IPs)
Query PostgreSQL:
SELECT client_ip, COUNT(



), MIN(timestamp), MAX(timestamp)FROM web_connectionsWHERE timestamp >= NOW() - INTERVAL '1 hour'GROUP BY client_ipORDER BY COUNT() DESC
LIMIT 20;
Abnormal traffic patterns
SELECT
date_trunc('minute', timestamp) AS time,
COUNT(



) as conn_per_minuteFROM web_connectionsWHERE timestamp >= NOW() - INTERVAL '1 hour'GROUP BY timeHAVING COUNT() > 1000 -- Alert if > 1000 connections/minute
ORDER BY time;
Intrusion Detection:
Port scan detection
sudo apt install fail2ban
Configure fail2ban for L4 redirector
sudo nano /etc/fail2ban/jail.local
[l4-redirector]
enabled = true
port = 8041,8047,8057
filter = l4-redirector
logpath = /var/log/redirector/l4_redirector_v4_enterprise.log
maxretry = 10
bantime = 3600
findtime = 60
________________________________________
14. API Reference
14.1 Monitoring API
Base URL: http://localhost:9090
Authentication: All endpoints require Authorization: Bearer AbDo@2020! header
GET /health
Health check endpoint for service monitoring.
Response:
{
"status": "ok",
"version": "4.1.6-hotfix",
"timestamp": "2026-01-31T08:47:15.234Z"
}
Status Codes:
	200: Service healthy
	401: Unauthorized (missing/invalid token)
________________________________________
GET /status
Comprehensive system status including ports, workers, and global metrics.
Response:
{
"ports": {
"8041": {
"status": "up",
"latency_ms": 23,
"udp_status": "up",
"checked_at": 1738315650
}
},
"workers": {
"tcp_8041_0": {
"active_tcp": 23,
"total_tcp": 1547,
"bytes_in": 45678901,
"bytes_out": 78901234,
"uptime_sec": 86400
}
},
"global": {
"total_connections": 45678,
"total_bytes_in": 123456789,
"total_bytes_out": 234567890,
"backend_pushes": 8934,
"backend_push_failures": 23
},
"system": {
"cpu_percent": 15.2,
"load_avg": [1.2, 1.5, 1.8],
"ram": {...}
}
}
________________________________________
GET /metrics
Prometheus-compatible metrics in text format.
Response: (text/plain)
redirector_total_connections 45678
redirector_total_bytes_in 123456789
redirector_tcp_latency_ms_bucket{port="8041",le="25"} 567
redirector_worker_active_tcp{worker_id="tcp_8041_0"} 23
Metrics Categories:
	Worker metrics: redirector_worker_*
	Global counters: redirector_*
	Latency histograms: redirector_tcp_latency_ms_*
________________________________________
14.2 Backend Push Endpoints
These endpoints are called by the redirector to push data to the backend API.
Base URL: http://111.111.11.111:6921 (via LocalToNet tunnel)
Authentication: All requests include Authorization: Bearer e7595fe6... header
POST /api/v1/web/{port}
Push client connection metrics (Stream 1).
Parameters:
	port (path): Port number (8041, 8047, or 8057)
Request Body:
{
"timestamp": "2026-01-31T08:47:15.234Z",
"client_ip": "203.0.113.45",
"client_port": 52341,
"bytes_in": 45678,
"bytes_out": 123456,
"duration_ms": 4523,
"worker_id": "tcp_8041_2",
"connection_id": "203.0.113.45:52341_1738315635234"
}
Response: {"status": "success"}
________________________________________
POST /api/v1/l2n/{port}
Push L2N tunnel metrics (Stream 2).
Request Body:
{
"timestamp": "2026-01-31T08:47:15.234Z",
"backend_ip": "222.222.22.222",
"backend_port": 1429,
"duration_ms": 4523,
"latency_ms": 23,
"worker_id": "tcp_8041_2",
"tunnel_status": "closed",
"localtonet_gateway": "111.111.11.111:6921",
"bytes_transferred": 169134
}
________________________________________
POST /api/v1/errors/l2n/{port}
Push connection error events (Stream 3).
Request Body:
{
"timestamp": "2026-01-31T08:50:23.456Z",
"error_type": "connection_timeout",
"backend_ip": "222.222.22.222",
"backend_port": 1429,
"client_ip": "203.0.113.45",
"client_port": 52341,
"error_message": "Timeout connecting to 222.222.22.222:1429",
"worker_id": "tcp_8041_2"
}
________________________________________
POST /api/v1/performance/{port}
Push latency percentile metrics (Stream 4).
Request Body:
{
"timestamp": "2026-01-31T08:47:30.000Z",
"port": 8041,
"p50": 23,
"p95": 45,
"p99": 78,
"min": 12,
"max": 95,
"sample_count": 847
}
________________________________________
POST /api/v1/throughput/{port}
Push throughput statistics (Stream 5).
Request Body:
{
"timestamp": "2026-01-31T08:47:30.000Z",
"port": 8041,
"bytes_per_sec": 2456789,
"connections_per_sec": 45.67,
"total_bytes_in": 35678901,
"total_bytes_out": 67890123,
"total_connections": 1370
}
________________________________________
POST /api/v1/workers/status
Push worker health metrics (Stream 6).
Request Body:
{
"timestamp": "2026-01-31T08:47:30.000Z",
"workers": {
"tcp_8041_0": {
"active_tcp": 23,
"total_tcp": 1547,
"bytes_in": 45678901,
"bytes_out": 78901234,
"uptime_sec": 86400
}
},
"worker_count": 24
}
________________________________________
POST /api/v1/health/{port}
Push port health status (Stream 7).
Request Body:
{
"timestamp": "2026-01-31T08:47:20.000Z",
"port": 8041,
"tcp_status": "up",
"tcp_latency_ms": 23,
"udp_status": "up",
"uptime_sec": 86400
}
________________________________________
POST /api/v1/events/{port}
Push connection events log (Stream 8).
Request Body:
{
"timestamp": "2026-01-31T08:47:30.000Z",
"port": 8041,
"events": [
{
"timestamp": "2026-01-31T08:47:15.234Z",
"event": "connection_closed",
"client": "203.0.113.45:52341",
"duration_ms": 4523,
"latency_ms": 23,
"bytes_transferred": 169134
}
],
"count": 45
}
________________________________________
Appendix A: Version History
v4.1.6 (January 2026)
Emergency Memory Leak Hotfix
	Fixed: Task backlog accumulation in cleanup loop
	Changed: Await tasks outside stats_lock
	Result: Memory usage reduced from 1.8GB to 7-10MB stable
v4.1.5 (December 2025)
	Added: 8 comprehensive data streams
	Added: Performance metrics (p50/p95/p99)
	Added: Connection events logging
	Improved: Health monitoring system
v4.1.0 (November 2025)
	Added: Multi-process architecture
	Added: UDP relay support
	Added: Prometheus metrics endpoint
	Improved: Latency histogram tracking
v4.0.0 (October 2025)
	Initial release
	Basic TCP forwarding
	Simple health checks
	API push integration
________________________________________
Appendix B: Glossary
Term	Definition
L4	Layer 4 (Transport Layer) in OSI model - TCP/UDP level
Redirector	Reverse proxy that forwards packets to backend
LocalToNet	Tunneling service providing public endpoint for private services
Backend API	Windows server receiving metrics from redirector
Worker	Independent process handling connections
Stream	Distinct data pipeline pushing metrics to backend
Latency	Time taken to establish backend connection
Throughput	Data transfer rate (bytes/sec)
Percentile (p50/p95/p99)	Statistical distribution of latency values
Circular Buffer	Fixed-size queue that overwrites oldest data

________________________________________
Appendix C: Quick Reference
Essential Commands
Service management
sudo systemctl start l4-redirector
sudo systemctl stop l4-redirector
sudo systemctl restart l4-redirector
sudo systemctl status l4-redirector
Monitoring
curl -H "Authorization: Bearer AbDo@2020!" http://localhost:9090/status
curl -H "Authorization: Bearer AbDo@2020!" http://localhost:9090/metrics
Logs
sudo journalctl -u l4-redirector -f
sudo tail -f /var/log/redirector/l4_redirector_v4_enterprise.log
Performance
ps aux | grep python3
ss -tn | grep -E ":(8041|8047|8057)" | wc -l
Port Configuration
Service Port	Backend Port	Protocol
8041	222.222.22.222:1429	TCP + UDP
8047	222.222.22.222:8667	TCP + UDP
8057	222.222.22.222:7798	TCP + UDP
9090	Monitoring API	HTTP

Critical Files
File	Purpose
/usr/local/bin/l4_redirector_v4.py	Main script
/etc/systemd/system/l4-redirector.service	Service file
/var/log/redirector/l4_redirector_v4_enterprise.log	Main log
/etc/sysctl.d/99-l4-redirector.conf	Kernel tuning

________________________________________
Appendix D: Contact and Support
System Administrator: over7-maker
GitHub Repository: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System
Documentation Version: 1.0
Last Updated: January 31, 2026
For issues or questions:
	Check troubleshooting guide (Section 11)
	Review logs: sudo journalctl -u l4-redirector -n 100
	Verify configuration matches this documentation
	Create GitHub issue with diagnostic output
________________________________________
END OF DOCUMENTATION
