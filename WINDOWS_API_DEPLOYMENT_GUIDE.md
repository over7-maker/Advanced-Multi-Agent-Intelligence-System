# Windows Backend API v4 - Complete Deployment & Troubleshooting Guide

## ✅ UNICODE FIX STATUS: RESOLVED!

Your Backend API v4 is now **running without UnicodeEncodeError**! 

**Proof from your console:**
```
2026-01-29 06:16:49,303 [INFO] __main__: ==================================================================
2026-01-29 06:16:49,304 [INFO] __main__: Backend API v4 - Enterprise Edition
2026-01-29 06:16:49,304 [INFO] __main__: Starting Server...
2026-01-29 06:16:50,500 [INFO] backend_api_v4: [START] Backend API v4 starting...
2026-01-29 06:16:50,602 [INFO] backend_api_v4: [OK] Connected to PostgreSQL: PostgreSQL 18.1
INFO:     Uvicorn running on http://0.0.0.0:5814 (Press CTRL+C to quit)
```

✅ **No errors, no encoding issues, clean startup!**

---

## ⚠️ NEW ISSUE: Endpoint Routing (404 Errors)

Your VPS Redirector is sending requests to **WRONG endpoints**. Look at the logs:

```
INFO:     192.168.88.16:48973 - "POST /api/v1/l2n/8041 HTTP/1.1" 404 Not Found
INFO:     192.168.88.16:48974 - "POST /api/v1/web/8057 HTTP/1.1" 404 Not Found
INFO:     192.168.88.16:48849 - "POST /api/v1/l2n/8041 HTTP/1.1" 404 Not Found
```

### Problem

Your `backend_api_v4.py` only has ONE data ingestion endpoint:
- ✅ `/api/v1/stream/ingest` (generic endpoint for all streams)

But your VPS Redirector is trying to POST to:
- ❌ `/api/v1/l2n/8041` (stream-specific endpoints - don't exist!)
- ❌ `/api/v1/web/8041` (stream-specific endpoints - don't exist!)
- ❌ `/api/v1/health/8047` (health endpoints - don't exist!)

### Solution: Fix VPS Redirector to Use Correct Endpoint

**Find and update your VPS Redirector v4.1.6 configuration:**

Locate the VPS redirector config file (likely on Linux VPS at `192.168.88.1` or similar):

```bash
# SSH to VPS
ssh user@your_vps_ip

# Find redirector config
find / -name "*redirector*config*" -o -name "vps_config*" 2>/dev/null

# Common locations:
ls -la ~/vps_redirector/config.json
ls -la /etc/vps_redirector/config.json
ls -la /opt/redirector/config.json
```

**Update the backend API endpoint URLs from:**
```json
{
  "backend_api": {
    "web_endpoints": [
      "http://192.168.88.16:5814/api/v1/web/8041",
      "http://192.168.88.16:5814/api/v1/web/8047",
      "http://192.168.88.16:5814/api/v1/web/8057"
    ],
    "l2n_endpoints": [
      "http://192.168.88.16:5814/api/v1/l2n/8041",
      "http://192.168.88.16:5814/api/v1/l2n/8047",
      "http://192.168.88.16:5814/api/v1/l2n/8057"
    ],
    "error_endpoint": "http://192.168.88.16:5814/api/v1/error"
  }
}
```

**To:**
```json
{
  "backend_api": {
    "ingest_endpoint": "http://192.168.88.16:5814/api/v1/stream/ingest",
    "health_endpoint": "http://192.168.88.16:5814/health",
    "token": "e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"
  }
}
```

**Update all stream ingestion calls to send:**

```python
# WRONG - individual endpoints per port
requests.post(
    "http://192.168.88.16:5814/api/v1/web/8041",
    json={"connections": [...]}
)

# CORRECT - unified endpoint with stream type
requests.post(
    "http://192.168.88.16:5814/api/v1/stream/ingest",
    headers={
        "Authorization": "Bearer e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"
    },
    json={
        "stream_type": "web",  # or "l2n", "error", "metrics", etc.
        "data": [
            {
                "port": 8041,
                "client_ip": "192.168.1.100",
                "client_port": 45123,
                "bytes_in": 1024,
                "bytes_out": 2048,
                "duration_ms": 150,
                "worker_id": "worker-1"
            }
        ]
    }
)
```

---

## ⚠️ SECONDARY ISSUE: Port Binding Conflict (WinError 10022)

One of your Uvicorn worker processes failed to bind to port 5814:

```
OSError: [WinError 10022] An invalid argument was supplied
  File "...asyncio/base_events.py", line 1652, in create_server
    server._start_serving()
```

### Root Cause

On Windows, multiple worker processes can't always bind to the same port with certain socket configurations. This is a known Windows asyncio limitation.

### Solution: Run Single Worker on Windows

**Edit your API startup command:**

**Instead of:**
```bash
python redirector\backend_api_v4.py
# (defaults to 4 workers)
```

**Use:**
```bash
# Single worker mode (recommended for Windows)
uvicorn redirector.backend_api_v4:app --host 0.0.0.0 --port 5814 --workers 1

# Or set environment variable
set API_WORKERS=1
python redirector\backend_api_v4.py
```

**Or update your production deployment script:**

```powershell
# run_backend_api_windows.ps1
Param(
    [int]$Workers = 1,  # Changed from 4 to 1 for Windows
    [int]$Port = 5814
)

# ... environment setup ...

Write-Host "Starting Backend API v4 with $Workers worker(s)..."
uvicorn redirector.backend_api_v4:app `
    --host 0.0.0.0 `
    --port $Port `
    --workers $Workers `
    --loop asyncio
```

**Why single worker?**
- ✅ Works reliably on Windows
- ✅ No port binding conflicts
- ✅ Still handles thousands of concurrent connections
- ✅ Uvicorn's async handles concurrency, not just workers

---

## 🔧 Immediate Action Items

### Step 1: Fix VPS Redirector Endpoint URLs

1. SSH to your Linux VPS
2. Locate redirector config file
3. Update endpoints from `/api/v1/web/PORT` → `/api/v1/stream/ingest`
4. Include `Authorization: Bearer <token>` header
5. Restart VPS Redirector service

```bash
# Example restart
sudo systemctl restart vps_redirector
# or
sudo service vps_redirector restart
```

### Step 2: Switch Backend API to Single Worker

```powershell
# Stop current API
Ctrl+C

# Run with single worker
set API_WORKERS=1
python redirector\backend_api_v4.py
```

### Step 3: Verify Connectivity

```powershell
# Test health endpoint
$headers = @{
    "Authorization" = "Bearer e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"
}

curl -Headers $headers http://localhost:5814/health

# Expected response:
# {"status":"healthy","database":"connected","version":"4.0.0"}
```

### Step 4: Verify Stream Ingestion

```powershell
# Test stream endpoint with correct path
$body = @{
    stream_type = "web"
    data = @(@{
        port = 8041
        client_ip = "192.168.1.100"
        client_port = 45123
        bytes_in = 1024
        bytes_out = 2048
        duration_ms = 150
    })
} | ConvertTo-Json

curl -X POST `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075" `
  -Body $body `
  http://localhost:5814/api/v1/stream/ingest

# Expected response:
# {"status":"success","stream_type":"web","records_inserted":1}
```

---

## 📊 API Endpoints Reference

### Data Ingestion (Primary)
```
POST /api/v1/stream/ingest
Headers: Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "stream_type": "web|l2n|error|metrics|throughput|worker|health",
  "data": [...],
  "worker_id": "optional"
}
```

### Health Checks
```
GET /health
GET /health/database

Headers: Authorization: Bearer <token>
```

### Query Endpoints
```
GET /api/v1/query/stats?hours=1&port=8041
GET /api/v1/query/performance?hours=1&port=8041

Headers: Authorization: Bearer <token>
```

### Maintenance
```
POST /api/v1/maintenance/vacuum
DELETE /api/v1/maintenance/purge?days=7

Headers: Authorization: Bearer <token>
```

---

## ✅ Expected Output After Fixes

```
2026-01-29 06:20:00 [INFO] __main__: ==================================================================
2026-01-29 06:20:00 [INFO] __main__: Backend API v4 - Enterprise Edition
2026-01-29 06:20:00 [INFO] __main__: Starting Server...
2026-01-29 06:20:00 [INFO] __main__: ==================================================================
INFO:     Uvicorn running on http://0.0.0.0:5814 (Press CTRL+C to quit)
INFO:     Started server process [12345]
2026-01-29 06:20:01 [INFO] backend_api_v4: [START] Backend API v4 starting...
2026-01-29 06:20:01 [INFO] backend_api_v4: [OK] Connected to PostgreSQL: PostgreSQL 18.1
INFO:     Application startup complete.

INFO:     192.168.88.1:54321 - "POST /api/v1/stream/ingest HTTP/1.1" 200 OK
2026-01-29 06:20:02 [INFO] backend_api_v4: [OK] STREAM [WEB]: Ingested 5 records

INFO:     192.168.88.1:54322 - "POST /api/v1/stream/ingest HTTP/1.1" 200 OK  
2026-01-29 06:20:03 [INFO] backend_api_v4: [OK] STREAM [L2N]: Ingested 3 records
```

✅ **200 OK responses** instead of 404 errors
✅ **Records being ingested** instead of failing
✅ **Clean, single worker** running without port conflicts

---

## 📝 Summary

| Issue | Status | Fix |
|-------|--------|-----|
| Unicode Encoding | ✅ **FIXED** | Custom formatter with ASCII fallback |
| Endpoint Routing | ⚠️ **PENDING** | Update VPS Redirector to use `/api/v1/stream/ingest` |
| Port Binding | ⚠️ **PENDING** | Switch to single worker mode |

**Next Steps:**
1. Update VPS Redirector config
2. Set `API_WORKERS=1` on Windows
3. Restart both services
4. Monitor for 200 OK responses

