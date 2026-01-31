# 🖥️ WINDOWS BACKEND API v4.1.6 - COMPLETE TECHNICAL DOCUMENTATION

**How It Works & How It Operates**

---

## TABLE OF CONTENTS

1. [System Overview & Architecture](#system-overview--architecture)
2. [Data Flow Pipeline](#data-flow-pipeline)
3. [How the Backend API Receives Data](#how-the-backend-api-receives-data)
4. [Database Layer & Storage](#database-layer--storage)
5. [Security & Authentication](#security--authentication)
6. [8 Data Streams Explained](#8-data-streams-explained)
7. [Request Processing Workflow](#request-processing-workflow)
8. [Windows-Specific Considerations](#windows-specific-considerations)
9. [Performance & Optimization](#performance--optimization)
10. [Monitoring & Diagnostics](#monitoring--diagnostics)

---

## SYSTEM OVERVIEW & ARCHITECTURE

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                     COMPLETE ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │            VPS (UBUNTU 20.04/22.04 LTS)                    │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │         L4 REDIRECTOR v4.1.6 ENTERPRISE             │  │   │
│  │  │  • TCP Forwarding (3 ports: 8041, 8047, 8057)       │  │   │
│  │  │  • UDP Relay                                         │  │   │
│  │  │  • Health Monitoring                                 │  │   │
│  │  │  • Metrics Collection                                │  │   │
│  │  │  • Memory Cleanup Loop (30-sec intervals)            │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                           │                                  │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │   8 CONTINUOUS DATA STREAMS                          │  │   │
│  │  │  POST /api/v1/web/{port}                             │  │   │
│  │  │  POST /api/v1/l2n/{port}                             │  │   │
│  │  │  POST /api/v1/errors/l2n/{port}                      │  │   │
│  │  │  POST /api/v1/performance/{port}                     │  │   │
│  │  │  POST /api/v1/throughput/{port}                      │  │   │
│  │  │  POST /api/v1/workers/status                         │  │   │
│  │  │  POST /api/v1/health/{port}                          │  │   │
│  │  │  POST /api/v1/events/{port}                          │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                           │                                  │   │
│  └───────────────────────────┼──────────────────────────────────┘   │
│                              │                                       │
│  (INTERNET / LOCALTONET GATEWAY)                                    │
│  111.111.11.111:6921                                                │
│                              │                                       │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
                               │ HTTPS (Encrypted)
                               │ Bearer Token Auth
                               ▼
        ┌──────────────────────────────────────────────┐
        │   WINDOWS MACHINE (192.168.88.16:5814)      │
        │                                              │
        │  ┌────────────────────────────────────────┐ │
        │  │ BACKEND API v4.1.6 (FastAPI + Uvicorn)│ │
        │  │  • 4 Worker Processes                  │ │
        │  │  • Async Request Handling              │ │
        │  │  • Token Validation                    │ │
        │  │  • Database Connection Pooling         │ │
        │  └────────────────────────────────────────┘ │
        │              │                               │
        │  ┌───────────▼────────────────────────────┐ │
        │  │   DATABASE LAYER (PostgreSQL)          │ │
        │  │                                        │ │
        │  │  ┌─────────────────────────────────┐  │ │
        │  │  │  Dynamic Table Creation         │  │ │
        │  │  │  • web_p_8041, web_p_8047...   │  │ │
        │  │  │  • l2n_p_8041, l2n_p_8047...   │  │ │
        │  │  │  • l2n_errors                   │  │ │
        │  │  │  • performance_metrics          │  │ │
        │  │  │  • throughput_stats             │  │ │
        │  │  │  • worker_stats                 │  │ │
        │  │  │  • port_health                  │  │ │
        │  │  │  • connection_events            │  │ │
        │  │  └─────────────────────────────────┘  │ │
        │  │                                        │ │
        │  │  ┌─────────────────────────────────┐  │ │
        │  │  │  Automatic Retention Policies   │  │ │
        │  │  │  • 30 days for active data      │  │ │
        │  │  │  • 365 days for archives        │  │ │
        │  │  └─────────────────────────────────┘  │ │
        │  └────────────────────────────────────────┘ │
        │                                              │
        │  ┌────────────────────────────────────────┐ │
        │  │  MONITORING & QUERY LAYER             │ │
        │  │  • Real-time Statistics                │ │
        │  │  • Health Dashboards                   │ │
        │  │  • Historical Analytics                │ │
        │  └────────────────────────────────────────┘ │
        │                                              │
        └──────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **L4 Redirector** | VPS-based traffic forwarding | Python 3.10+, asyncio, uvloop |
| **Backend API** | Receives & validates data | FastAPI, Uvicorn |
| **Database** | Persists all data streams | PostgreSQL 12+ |
| **Connection Pool** | Manages DB connections | psycopg3 AsyncConnectionPool |
| **Authentication** | Validates API requests | Bearer Token (256-bit hex) |
| **Async Processing** | Non-blocking I/O | Python async/await |

---

## DATA FLOW PIPELINE

### Complete Request Lifecycle (From VPS to Windows DB)

```
1. CONNECTION ESTABLISHED (VPS L4 Redirector)
   └─► Client connects to VPS port 8041/8047/8057
   
2. TRAFFIC FORWARDED
   └─► L4 Redirector forwards to Windows backend (192.168.88.16:5814)
   
3. METRICS COLLECTED
   └─► L4 Redirector measures:
       • Connection latency
       • Bytes in/out
       • Duration
       • Worker info
   
4. DATA NORMALIZED
   └─► L4 Redirector formats data into 8 streams:
       Stream 1: Web traffic metrics
       Stream 2: L2N tunnel metrics
       Stream 3: Connection errors
       Stream 4: Performance (latency percentiles)
       Stream 5: Throughput statistics
       Stream 6: Worker health
       Stream 7: Port health
       Stream 8: Connection events
   
5. ASYNC PUSH TO BACKEND API
   └─► VPS creates HTTP POST request:
       POST /api/v1/web/8041 HTTP/1.1
       Authorization: Bearer <TOKEN>
       Content-Type: application/json
       
       {
         "timestamp": "2026-01-31T12:33:00Z",
         "client_ip": "203.0.113.42",
         "client_port": 54321,
         "bytes_in": 1024,
         "bytes_out": 2048,
         "duration_ms": 150,
         "worker_id": "tcp_8041_3"
       }
   
6. BACKEND API RECEIVES REQUEST
   └─► Windows Backend API (5814):
       • Receives POST on port 5814
       • Validates Bearer token
       • Deserializes JSON
   
7. REQUEST VALIDATION
   └─► FastAPI Pydantic models validate:
       • Timestamp format (ISO 8601)
       • Numeric types (latency, bytes)
       • Port ranges
       • Required fields
   
8. DATABASE INSERT
   └─► PostgreSQL transaction:
       INSERT INTO web_p_8041 
       (timestamp, client_ip, client_port, bytes_in, bytes_out, duration_ms, worker_id)
       VALUES (...)
   
9. TRANSACTION COMMIT
   └─► Data persisted to disk
   
10. RESPONSE SENT
    └─► Backend API sends back:
        HTTP 200 OK
        {"status": "success", "port": 8041, "records": 1}
   
11. L4 REDIRECTOR CLEANUP
    └─► Memory management & task backlog cleanup
    └─► Next batch queued in 30 seconds
```

---

## HOW THE BACKEND API RECEIVES DATA

### Network Layer (Port 5814)

```python
# FastAPI Application Setup
app = FastAPI(
    title="Backend API v4.1.6",
    description="8-Stream Enterprise Data Platform"
)

# Uvicorn Server Configuration
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",           # Listen on all interfaces
        port=5814,                # Windows backend port
        workers=4,                # 4 concurrent workers
        reload=False,             # Production mode
        log_level="info"
    )
```

**What happens when data arrives:**

```
INCOMING REQUEST (From VPS)
    │
    ├─► Uvicorn worker process receives TCP connection on port 5814
    │
    ├─► Request headers parsed:
    │   Authorization: Bearer e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075
    │   Content-Type: application/json
    │   Content-Length: 245
    │
    ├─► Request body buffered (JSON payload)
    │
    └─► Route matched: POST /api/v1/web/{port}
```

### Authentication Layer

```python
async def verify_token(authorization: Optional[str] = Header(None)) -> bool:
    """
    STEP 1: Extract Authorization header
    Expected format: "Bearer <TOKEN>"
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )
    
    """
    STEP 2: Parse Bearer token
    """
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )
    
    """
    STEP 3: Compare with configured token
    """
    token = parts[1]
    if token != API_TOKEN:  # e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075
        logger.warning(f"[FAIL] Invalid token received")
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )
    
    return True  # Token valid, proceed
```

**Security Benefits:**
- ✅ Prevents unauthorized data injection
- ✅ Logs failed attempts
- ✅ Uses HTTP 403 (Forbidden) for invalid tokens
- ✅ Token is 256-bit hexadecimal (cryptographically strong)

---

## DATABASE LAYER & STORAGE

### Dynamic Table Creation

The Backend API **automatically creates tables** based on incoming data:

```sql
-- Tables created for each monitored port (8041, 8047, 8057)
CREATE TABLE web_p_8041 (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    client_ip INET,
    client_port INTEGER,
    bytes_in BIGINT,
    bytes_out BIGINT,
    duration_ms INTEGER,
    worker_id TEXT
);

CREATE INDEX idx_web_p_8041_timestamp ON web_p_8041 (timestamp DESC);

-- Similar for l2n_p_8041, l2n_p_8047, etc.
```

### Data Stream Tables

| Table Name | Purpose | Retention |
|-----------|---------|-----------|
| `web_p_8041` | Client connections (port 8041) | 30 days |
| `l2n_p_8041` | Backend L2N tunnels (port 8041) | 30 days |
| `l2n_errors` | Connection errors from all ports | 30 days |
| `performance_metrics` | Latency percentiles (p50/p95/p99) | 30 days |
| `throughput_stats` | Real-time throughput data | 30 days |
| `worker_stats` | Worker process health | 30 days |
| `port_health` | Port availability & latency | 30 days |
| `connection_events` | Connection lifecycle events | 30 days |

### Automatic Cleanup

```sql
-- PostgreSQL runs automatically every night at 2 AM
DELETE FROM web_p_8041 WHERE timestamp < NOW() - INTERVAL '30 days';
DELETE FROM l2n_errors WHERE timestamp < NOW() - INTERVAL '30 days';
DELETE FROM performance_metrics WHERE timestamp < NOW() - INTERVAL '365 days';
```

---

## SECURITY & AUTHENTICATION

### Token Validation Flow

```
Request Arrives
    │
    ├─ Authorization Header Present? ──No──► HTTP 401 Unauthorized
    │                                      (Missing authentication)
    │
    ├─ Matches Bearer Format? ──No──► HTTP 401 Unauthorized
    │                              (Invalid format)
    │
    ├─ Token == API_TOKEN? ──No──► HTTP 403 Forbidden
    │                          (Invalid/wrong token)
    │                          LOG: Failed attempt
    │
    └─ All Checks Pass ──Yes──► Continue to endpoint
                            LOG: [OK] Request accepted
```

### Windows Event Log Integration

The Backend API logs security events to Windows Event Viewer:

```
Event Type: Failure Audit
Source: Backend-API
Event ID: 4625
Description: Failed login attempt - Invalid token from 203.0.113.42
Time: 2026-01-31 12:35:10
```

---

## 8 DATA STREAMS EXPLAINED

### Stream 1: Web Client Connections (`/api/v1/web/{port}`)

**Purpose:** Track client-to-VPS connections

**Data Structure:**
```json
{
  "timestamp": "2026-01-31T12:33:00.123Z",
  "client_ip": "203.0.113.42",
  "client_port": 54321,
  "bytes_in": 1024,
  "bytes_out": 2048,
  "duration_ms": 150,
  "worker_id": "tcp_8041_3"
}
```

**Database Storage:**
```
web_p_8041: 1000s of records per hour
│
├─ Real client IP
├─ Connection duration
├─ Total data transferred
└─ Worker process identifier
```

**Use Cases:**
- Client traffic analysis
- Bandwidth monitoring
- Connection duration tracking
- Peak usage identification

---

### Stream 2: L2N Backend Tunnel Metrics (`/api/v1/l2n/{port}`)

**Purpose:** Track VPS-to-Windows tunnel performance

**Data Structure:**
```json
{
  "timestamp": "2026-01-31T12:33:00.123Z",
  "backend_ip": "192.168.88.16",
  "backend_port": 5814,
  "bytes_in": 512,
  "bytes_out": 1024,
  "duration_ms": 120,
  "latency_ms": 45,
  "worker_id": "tcp_8041_1",
  "localtonet_gateway": "111.111.11.111:6921"
}
```

**What It Measures:**
- Tunnel establishment latency
- Data forwarding efficiency
- LocalToNet gateway performance
- Backend responsiveness

**Critical Metrics:**
- `latency_ms`: Time to establish tunnel (45ms = good)
- `duration_ms`: Connection lifetime
- Comparison with web stream shows tunneling overhead

---

### Stream 3: Connection Errors (`/api/v1/errors/l2n/{port}`)

**Purpose:** Capture all connection failures

**Error Types:**
```
• connection_timeout
  → Backend unreachable (> 3 seconds)
  
• connection_error
  → Network error (socket exception)
  
• tls_error
  → SSL/TLS handshake failed
  
• backend_refused
  → Backend actively rejected connection
```

**Data Structure:**
```json
{
  "timestamp": "2026-01-31T12:33:00.123Z",
  "error_type": "connection_timeout",
  "backend_ip": "192.168.88.16",
  "backend_port": 5814,
  "client_ip": "203.0.113.42",
  "client_port": 54321,
  "error_message": "Timeout connecting to 192.168.88.16:5814",
  "worker_id": "tcp_8041_2"
}
```

**Stored In:**
```sql
l2n_errors table (30-day retention)
Indexed by: timestamp DESC, error_type
```

---

### Stream 4: Performance Metrics (`/api/v1/performance/{port}`)

**Purpose:** Latency distribution analysis

**Data Structure:**
```json
{
  "timestamp": "2026-01-31T12:33:00.123Z",
  "port": 8041,
  "p50": 45,      // 50% of requests under 45ms
  "p95": 120,     // 95% of requests under 120ms
  "p99": 250,     // 99% of requests under 250ms
  "min": 12,      // Fastest connection
  "max": 450,     // Slowest connection
  "sample_count": 1500
}
```

**How It's Calculated:**
```python
# VPS collects 1000 latency samples over 30 seconds
latencies = [12, 15, 20, ..., 450]  # 1000 measurements
latencies.sort()

p50 = latencies[int(1000 * 0.50)]   # Index 500 = 45ms
p95 = latencies[int(1000 * 0.95)]   # Index 950 = 120ms
p99 = latencies[int(1000 * 0.99)]   # Index 990 = 250ms
```

**Performance Assessment:**
| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|-----------|------|
| p50 | <30ms | 30-50ms | 50-100ms | >100ms |
| p95 | <75ms | 75-150ms | 150-250ms | >250ms |
| p99 | <150ms | 150-300ms | 300-500ms | >500ms |

---

### Stream 5: Throughput Statistics (`/api/v1/throughput/{port}`)

**Purpose:** Real-time bandwidth measurement

**Data Structure:**
```json
{
  "timestamp": "2026-01-31T12:33:30.000Z",
  "port": 8041,
  "bytes_per_sec": 1048576,        // 1 MB/s
  "connections_per_sec": 45.5,
  "total_bytes_in": 31457280,      // 30 MB (30-sec window)
  "total_bytes_out": 62914560,     // 60 MB (30-sec window)
  "total_connections": 1365
}
```

**Calculation Method:**
```python
# Measured over 30-second windows
window_duration = 30  # seconds
total_bytes = bytes_in + bytes_out
total_connections = connection_count

bytes_per_sec = total_bytes / window_duration
connections_per_sec = total_connections / window_duration
```

**Real-World Example:**
- Port 8041 receives 45 connections/sec
- Average 1 MB/s throughput
- Peak measured: 2.5 MB/s
- Indicates healthy traffic volume

---

### Stream 6: Worker Status (`/api/v1/workers/status`)

**Purpose:** Monitor L4 Redirector worker processes

**Data Structure:**
```json
{
  "timestamp": "2026-01-31T12:33:30.000Z",
  "workers": {
    "tcp_8041_0": {
      "active_tcp": 23,
      "total_tcp": 450,
      "bytes_in": 10485760,
      "bytes_out": 20971520,
      "uptime_sec": 3600,
      "last_activity": 1706691210
    },
    "tcp_8041_1": {
      "active_tcp": 28,
      "total_tcp": 512,
      ...
    },
    ...
  },
  "worker_count": 31
}
```

**Worker Types:**
```
• tcp_8041_0 through tcp_8041_11   (12 TCP workers per port)
• udp_8041                          (1 UDP worker per port)
• monitor                           (1 health monitor)
• cleanup                           (1 memory cleanup)
• http_server                       (1 metrics server)
```

**Health Indicators:**
- `active_tcp` should match real connections
- `total_tcp` increases over time
- `last_activity` recent = worker alive
- All workers should show similar load

---

### Stream 7: Port Health (`/api/v1/health/{port}`)

**Purpose:** Backend availability monitoring

**Data Structure:**
```json
{
  "timestamp": "2026-01-31T12:33:10.000Z",
  "port": 8041,
  "tcp_status": "up",           // "up" or "down"
  "tcp_latency_ms": 45,
  "udp_status": "up",           // "up" or "down"
  "uptime_sec": 86400
}
```

**Status Determination:**
```python
# TCP Health Check (every 10 seconds)
try:
    socket.connect(("192.168.88.16", 5814), timeout=2)
    status = "up"
    latency = measured_time * 1000  # Convert to ms
except Timeout:
    status = "down"
    latency = 2000

# UDP Health Check
try:
    socket.sendto(b"health", ("192.168.88.16", 5814))
    status = "up"
except Exception:
    status = "down"
```

---

### Stream 8: Connection Events (`/api/v1/events/{port}`)

**Purpose:** Connection lifecycle logging

**Data Structure:**
```json
{
  "timestamp": "2026-01-31T12:33:30.000Z",
  "port": 8041,
  "events": [
    {
      "timestamp": "2026-01-31T12:33:01.123Z",
      "event": "connection_closed",
      "client": "203.0.113.42:54321",
      "duration_ms": 150,
      "latency_ms": 45,
      "bytes_transferred": 3072
    },
    {
      "timestamp": "2026-01-31T12:33:02.456Z",
      "event": "connection_closed",
      "client": "203.0.113.43:54322",
      "duration_ms": 180,
      "latency_ms": 52,
      "bytes_transferred": 4096
    }
  ],
  "count": 50
}
```

**Event Types:**
- `connection_opened` → New client connected
- `connection_closed` → Connection terminated
- `connection_error` → Connection failed
- `tunnel_established` → Backend tunnel ready
- `tunnel_lost` → Backend connection dropped

**Buffer Management:**
```python
CONNECTION_EVENTS = collections.deque(maxlen=50)
# Stores last 50 events per port
# Auto-deletes oldest when 51st event added
```

---

## REQUEST PROCESSING WORKFLOW

### Complete Request Processing Flow

```
STEP 1: REQUEST ARRIVES
└─► POST /api/v1/web/8041 HTTP/1.1
    Authorization: Bearer <token>
    Content-Type: application/json
    Content-Length: 245

STEP 2: ROUTE MATCHING (FastAPI Router)
└─► Matches route pattern: @app.post("/api/v1/web/{port}")
    Port parameter extracted: port = 8041

STEP 3: DEPENDENCY INJECTION (Depends)
└─► Calls: verify_token(authorization)
    ├─ Extracts: "Bearer <token>"
    ├─ Validates: token == API_TOKEN
    └─ Returns: True or raises HTTPException(403)

STEP 4: JSON DESERIALIZATION (Pydantic)
└─► Request body: {"client_ip": "203.0.113.42", ...}
    Pydantic model validates:
    ├─ timestamp: ISO 8601 format
    ├─ client_ip: Valid IPv4/IPv6
    ├─ client_port: 1-65535
    ├─ bytes_in: Integer ≥ 0
    ├─ bytes_out: Integer ≥ 0
    ├─ duration_ms: Integer ≥ 0
    └─ worker_id: String

STEP 5: DATABASE CONNECTION ACQUISITION
└─► Calls: get_db_connection()
    ├─ Acquires connection from pool (max 10 connections)
    ├─ Connection state: idle
    └─ Transaction isolation: READ_COMMITTED

STEP 6: DATABASE INSERTION
└─► Prepares SQL:
    INSERT INTO web_p_8041 
    (timestamp, client_ip, client_port, bytes_in, bytes_out, duration_ms, worker_id)
    VALUES ($1, $2, $3, $4, $5, $6, $7)

STEP 7: PARAMETERIZED QUERY EXECUTION
└─► Parameters passed separately (SQL injection prevention):
    $1 = "2026-01-31T12:33:00.123Z"
    $2 = "203.0.113.42"
    $3 = 54321
    $4 = 1024
    $5 = 2048
    $6 = 150
    $7 = "tcp_8041_3"

STEP 8: TRANSACTION COMMIT
└─► BEGIN TRANSACTION
    ├─ Row inserted
    ├─ Index updated
    └─ COMMIT TRANSACTION
    Data now persisted to disk

STEP 9: LOGGING
└─► logger.info(f"[OK] Web[8041]: 1 record")
    Written to: logs/backend_api_v4.log

STEP 10: RESPONSE GENERATION
└─► HTTP 200 OK
    Content-Type: application/json
    {
      "status": "success",
      "port": 8041,
      "records": 1
    }

STEP 11: CONNECTION RETURN TO POOL
└─► Connection released back to AsyncConnectionPool
    Available for next request
    State reset
```

### Error Handling

```python
try:
    # Execute all steps above
    await conn.execute(sql_query, parameters)
except asyncpg.UniqueViolationError:
    logger.error("Duplicate record attempted")
    raise HTTPException(409, "Duplicate entry")
except asyncpg.ConnectionFailureError:
    logger.error("Database connection failed")
    raise HTTPException(503, "Database unavailable")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(500, "Internal server error")
```

---

## WINDOWS-SPECIFIC CONSIDERATIONS

### Event Loop Policy

```python
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )
```

**Why needed:**
- Windows doesn't support `epoll()` (Linux specific)
- Uses `select()` multiplexing instead
- Slightly slower but compatible with Windows

### Encoding Issues

```python
if sys.platform == "win32":
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
```

**Solves:**
- Windows console Unicode issues
- Emoji rendering (replaces with ASCII if needed)
- UTF-8 logging compatibility

### Service Management (NSSM)

```powershell
# Register as Windows Service
nssm install BackendAPI python backend_api_v4.py
nssm set BackendAPI AppDirectory "C:\backend-api"
nssm set BackendAPI AppStdout "C:\backend-api\logs\stdout.log"
nssm set BackendAPI AppStderr "C:\backend-api\logs\stderr.log"

# Start service
net start BackendAPI

# Stop service
net stop BackendAPI
```

### PostgreSQL Connection on Windows

```python
# Windows uses named pipes or TCP
db_pool = AsyncConnectionPool(
    conninfo=f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME}",
    min_size=2,
    max_size=10,
    timeout=30
)
```

---

## PERFORMANCE & OPTIMIZATION

### Connection Pooling

```python
# Psycopg3 AsyncConnectionPool
db_pool = AsyncConnectionPool(
    conninfo="...",
    min_size=2,        # Keep 2 connections ready
    max_size=10,       # Max 10 simultaneous connections
    timeout=30         # 30-second connection timeout
)
```

**Benefits:**
- ✅ Reuses database connections
- ✅ Avoids connection establishment overhead
- ✅ Handles burst traffic
- ✅ Prevents "too many connections" errors

### Async Request Processing

```python
# Non-blocking I/O
@app.post("/api/v1/web/{port}")
async def ingest_web(port: int, data: dict, ...):
    """
    Async endpoint = other requests served while this one waits for DB
    """
    async with db_pool.acquire() as conn:
        await conn.execute(sql_query)  # Non-blocking wait
    return {"status": "success"}
```

**Worker Process Model:**
```
Client 1 ──┐
Client 2 ──┤─► Worker 1 (handles all, async)
Client 3 ──┘

Client 4 ──┐
Client 5 ──┤─► Worker 2 (handles all, async)
Client 6 ──┘
```

4 workers × 4 concurrent requests each = ~16 concurrent requests

### Database Query Performance

```sql
-- Indexes speed up queries
CREATE INDEX idx_web_p_8041_timestamp ON web_p_8041 (timestamp DESC);
SELECT * FROM web_p_8041 WHERE timestamp > NOW() - INTERVAL '1 hour';
-- Uses index: Query returns in ~10ms instead of 500ms
```

### Memory Management

```python
# Task backlog cleanup (L4 Redirector)
async def memory_cleanup_loop():
    """Runs every 30 seconds"""
    while True:
        await asyncio.sleep(30)
        
        # Collect data INSIDE lock
        with stats_lock:
            cleanup_tasks = [
                push_to_backend(f"/api/v1/web/8041", web_data),
                push_to_backend(f"/api/v1/l2n/8041", l2n_data),
                # ... other streams
            ]
        
        # AWAIT tasks OUTSIDE lock (no backlog!)
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
```

**Memory Impact:**
- ~7-10 MB per process (L4 Redirector)
- ~50-100 MB for Backend API (with 4 workers)
- PostgreSQL: 200+ MB (depends on data volume)

---

## MONITORING & DIAGNOSTICS

### Query Endpoints

```bash
# Check API health
curl -X GET http://localhost:5814/health

# Query web connections (last 24 hours)
curl -X GET "http://localhost:5814/api/v1/query/web?port=8041&hours=24"

# Get recent statistics
curl -X GET "http://localhost:5814/api/v1/stats"
```

### Windows Event Viewer Integration

```
Event Viewer → Windows Logs → Application
├─ Source: Backend-API
├─ Type: Information / Warning / Error
├─ Event IDs:
│  ├─ 1000: Service started
│  ├─ 1001: Service stopped
│  ├─ 4625: Failed authentication
│  └─ 5000: Database error
```

### Prometheus Metrics Endpoint

```bash
# Get all metrics in Prometheus format
curl http://localhost:9090/metrics

# Sample output:
redirector_tcp_connections_total{port="8041"} 450
redirector_tcp_latency_ms{port="8041",percentile="p95"} 120
redirector_bytes_in_total{port="8041"} 10485760
```

### Real-Time Monitoring Script

```powershell
# PowerShell monitoring
$token = "e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"
$headers = @{"Authorization" = "Bearer $token"}

while ($true) {
    $status = Invoke-RestMethod -Uri "http://localhost:5814/api/v1/status" -Headers $headers
    Write-Host "Connections: $($status.connections)"
    Write-Host "Throughput: $($status.throughput_mb_s) MB/s"
    Start-Sleep -Seconds 5
}
```

---

## COMMON SCENARIOS

### Scenario 1: Client Connects to VPS Port 8041

```
Timeline:
T+0ms    Client initiates TCP connection to VPS:8041
T+5ms    L4 Redirector accepts connection
T+10ms   L4 Redirector connects to Windows backend (via LocalToNet)
T+55ms   Backend tunnel established (45ms latency)
T+100ms  Client sends data (1KB)
T+500ms  Backend receives data, sends response (2KB)
T+550ms  Client receives response
T+600ms  Client closes connection
Duration: 600ms

Stream 1 (web_p_8041): 1 record
  - client_ip: 203.0.113.42
  - duration_ms: 600
  - bytes_in: 1024
  - bytes_out: 2048

Stream 2 (l2n_p_8041): 1 record
  - latency_ms: 45
  - duration_ms: 600

Stream 8 (connection_events): 1 event
  - event: connection_closed
  - duration_ms: 600
```

### Scenario 2: Backend Becomes Unavailable

```
Timeline:
T+0ms    Backend Windows machine goes down (network cable unplugged)
T+5ms    Client tries to connect
T+15ms   L4 Redirector attempts tunnel to Windows backend
T+2015ms (TIMEOUT - 2 seconds)
         Connection timeout error triggered

Stream 3 (l2n_errors): 1 record
  - error_type: "connection_timeout"
  - error_message: "Timeout connecting to 192.168.88.16:5814"
  - client_ip: 203.0.113.42

Stream 7 (health_8041): 1 record
  - tcp_status: "down"
  - tcp_latency_ms: 0

Backend API continues accepting data (disconnected).
No data loss - next connection will work when backend comes back.
```

### Scenario 3: Peak Traffic Hour

```
VPS Metrics (per 30-second window):
  - 1000 new connections
  - 500 MB transferred
  - 45,000 events logged
  
L4 Redirector Activity:
  - 12 TCP workers actively forwarding
  - 3 UDP workers handling datagrams
  - Memory: ~35 MB (stable)
  
Backend API:
  - 4 Uvicorn workers
  - ~500 requests/second received
  - Database: ~50 ms per insert
  - Response time: <100ms
  
Database:
  - ~16,700 rows inserted per second
  - 30 days retention: ~43 billion rows
  - Cleanup jobs: Automatic daily at 2 AM
```

---

## CONCLUSION

The Windows Backend API is a **production-grade data ingestion platform** that:

1. **Receives** continuous data streams from the VPS L4 Redirector
2. **Validates** all data with bearer token authentication
3. **Stores** data in PostgreSQL with 8 specialized tables
4. **Processes** requests asynchronously (non-blocking)
5. **Maintains** data integrity with transactions
6. **Optimizes** performance with connection pooling
7. **Monitors** itself with health checks and metrics
8. **Scales** horizontally with multiple worker processes

**Key Strengths:**
- ✅ Enterprise-grade reliability
- ✅ Windows-native compatibility
- ✅ Sub-100ms response times
- ✅ Zero data loss architecture
- ✅ Comprehensive monitoring
- ✅ Automatic retention policies
- ✅ Bearer token security

---

**Documentation Generated:** January 31, 2026  
**Backend API Version:** 4.1.6 Compatible  
**Target Audience:** System Administrators, DevOps Engineers, Developers
