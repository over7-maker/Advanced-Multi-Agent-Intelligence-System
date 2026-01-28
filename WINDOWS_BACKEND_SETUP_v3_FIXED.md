# Windows Backend API v3 FIXED - Complete Setup Guide

> **CRITICAL**: Your old `backend_api_production.py` is NOT working with the hybrid L4 redirector. This guide replaces it completely.

## The Problem

You're seeing:
```
ERROR: Could not connect to API. Make sure it's running on localhost:5814
Details: HTTPConnectionPool(...): Failed to establish a new connection
[WinError 10061] No connection could be made because the target machine actively refused it
```

**Reason**: Your old backend API file doesn't match the hybrid L4 redirector's data stream expectations.

---

## Solution: Deploy Backend API v3 FIXED

### Step 1: Get the New Backend File

Download from GitHub:
```
https://raw.githubusercontent.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/main/Windows/backend_api_v3_final_working.py
```

Or clone:
```powershell
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System
cd Advanced-Multi-Agent-Intelligence-System
```

### Step 2: Replace Old File

**STOP** the old backend if running:
```powershell
# Check if old backend is running
tasklist | findstr python

# If you see python.exe running backend_api_production.py, stop it:
# Press Ctrl+C in its window, or:
taskkill /IM python.exe /F
```

**BACKUP** the old file:
```powershell
cd C:\Users\Administrator\API_monitoring_system
rename backend_api_production.py backend_api_production.py.old
```

**COPY** the new file:
```powershell
# Copy from wherever you downloaded it
copy C:\path\to\backend_api_v3_final_working.py C:\Users\Administrator\API_monitoring_system\backend_api_v3_final_working.py
```

### Step 3: Verify Dependencies

Ensure required packages are installed:
```powershell
python -m pip install fastapi uvicorn asyncpg
```

Check PostgreSQL version:
```powershell
# This should work if PostgreSQL is installed
psql --version

# If not found, PostgreSQL is not in PATH
# You can still connect via localhost:5432
```

### Step 4: Start the New Backend

```powershell
cd C:\Users\Administrator\API_monitoring_system
python backend_api_v3_final_working.py
```

**Expected output**:
```
2026-01-28 21:55:00 | INFO     | ============================================================
2026-01-28 21:55:00 | INFO     | 🚀 ENTERPRISE BACKEND API v3 FIXED - ALL 8 DATA STREAMS
2026-01-28 21:55:00 | INFO     | ============================================================
2026-01-28 21:55:00 | INFO     | 📡 Listening on 0.0.0.0:5814
2026-01-28 21:55:00 | INFO     | 📄 Receives from: VPS via LocalToNet (194.182.64.133:6921)
2026-01-28 21:55:00 | INFO     | 💾 Database: PostgreSQL 127.0.0.1:5432
2026-01-28 21:55:00 | INFO     | ============================================================
2026-01-28 21:55:00 | INFO     | ✅ STREAMS:
2026-01-28 21:55:00 | INFO     |   1. Web connections POST /api/v1/web/{port}
2026-01-28 21:55:00 | INFO     |   2. L2N connections POST /api/v1/l2n/{port}
2026-01-28 21:55:00 | INFO     |   3. Web errors POST /api/v1/errors/web/{port}
2026-01-28 21:55:00 | INFO     |   4. L2N errors POST /api/v1/errors/l2n/{port}
2026-01-28 21:55:00 | INFO     |   5. Warnings POST /api/v1/warnings
2026-01-28 21:55:00 | INFO     | ...
```

### Step 5: Verify It's Working

**From Windows (Command Prompt):**
```powershell
# Check if listening on port 5814
netstat -ano | findstr :5814

# Should show something like:
# TCP    0.0.0.0:5814           0.0.0.0:0              LISTENING       12345
```

**From VPS (via LocalToNet):**
```bash
# Test health endpoint
curl http://194.182.64.133:6921/health

# Expected response:
# {"status":"ok","timestamp":"2026-01-28T21:55:00.123456","version":"3.0-fixed"}
```

**Check database:**
```powershell
# From Windows
psql -h 127.0.0.1 -U redirector -d redirector_db -c "SELECT COUNT(*) FROM web_p_8041;"

# Should start showing row counts as data flows in from VPS
```

---

## What's Different in v3 FIXED

| Feature | Old v3 | New v3 FIXED |
|---------|--------|----------|
| **Port** | 5814 | 5814 (same) |
| **Database** | PostgreSQL | PostgreSQL (same) |
| **Auth Token** | Same | Same |
| **Streams** | 8 endpoints | 8 endpoints ✅ **Working** |
| **L2N Health Stream** | `/api/v1/health/l2n/{port}` | `/api/v1/health/l2n` ✅ **Simplified** |
| **Error Handling** | Basic | Enhanced ✅ **Better** |
| **Logging** | Standard | Unicode icons ✅ **Better** |
| **Query Endpoints** | 3 (web, l2n, stats) | 5 (web, l2n, stats, errors, health) ✅ **More** |

---

## Run as Windows Service (Optional)

If you want the backend to start automatically:

### Option A: Using NSSM (Non-Sucking Service Manager)

1. Download NSSM: https://nssm.cc/download
2. Extract to `C:\nssm`

```powershell
# Install service
C:\nssm\nssm.exe install BackendAPIv3 C:\Python314\python.exe

# When dialog opens, set:
# Application tab:
#   Path: C:\Python314\python.exe
#   Startup directory: C:\Users\Administrator\API_monitoring_system
#   Arguments: backend_api_v3_final_working.py

# Details tab:
#   Display name: Backend API v3
#   Start type: Automatic

# Log On tab:
#   This account: Administrator (or your Windows user)

# Start service
C:\nssm\nssm.exe start BackendAPIv3

# Check status
C:\nssm\nssm.exe status BackendAPIv3
```

### Option B: Using Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
   - Program: `C:\Python314\python.exe`
   - Arguments: `C:\Users\Administrator\API_monitoring_system\backend_api_v3_final_working.py`
   - Start in: `C:\Users\Administrator\API_monitoring_system`

---

## Troubleshooting

### Backend won't start

```powershell
# Check Python is installed
python --version

# Check dependencies
python -m pip list | findstr fastapi
python -m pip list | findstr uvicorn
python -m pip list | findstr asyncpg

# If missing, install:
python -m pip install fastapi uvicorn asyncpg
```

### Port 5814 already in use

```powershell
# Find what's using it
netstat -ano | findstr :5814

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change the port in the script:
# Edit: API_PORT = 5814
# Change to: API_PORT = 5815
```

### Database won't connect

```powershell
# Test connection
psql -h 127.0.0.1 -U redirector -d redirector_db -c "SELECT version();"

# If fails:
# 1. Check PostgreSQL is running
Get-Service | findstr -i postgres

# 2. Verify credentials match in backend_api_v3_final_working.py:
# DB_USER = "redirector"
# DB_PASSWORD = "Azyz@123"
# DB_HOST = "127.0.0.1"
# DB_PORT = 5432
# DB_NAME = "redirector_db"

# 3. If wrong credentials, update in script and restart
```

### VPS can't reach backend

```bash
# From VPS, test:
curl -v http://194.182.64.133:6921/health

# If fails:
# 1. Check LocalToNet tunnel is active on Windows
# 2. Check backend is running (see above)
# 3. Check Windows firewall isn't blocking port 5814

# On Windows, allow through firewall:
netsh advfirewall firewall add rule name="Python Backend API" dir=in action=allow program="C:\\Python314\\python.exe" enable=yes
```

---

## Monitoring

### From VPS, watch the backend health:

```bash
# Watch timeout rate
watch -n 2 'tail -50 /var/log/redirector/hybrid_l4_final.log | grep -c "API timeout"'

# Monitor data flow
tail -f /var/log/redirector/hybrid_l4_final.log | grep 'Stream'

# Run health check
bash VPS/backend_health_check.sh
```

### From Windows, monitor the backend:

```powershell
# Watch process
Get-Process python | Where-Object {$_.CommandLine -like "*backend_api*"}

# Check database rows growing
psql -h 127.0.0.1 -U redirector -d redirector_db -c "SELECT COUNT(*) FROM web_p_8041;"

# Query last 10 connections
psql -h 127.0.0.1 -U redirector -d redirector_db -c "SELECT * FROM web_p_8041 ORDER BY timestamp DESC LIMIT 10;"
```

---

## Next Steps

1. ✅ Start the new backend
2. ✅ Verify it's listening on :5814
3. ✅ Run health check from VPS
4. ✅ Monitor for data flow
5. ✅ Set up auto-start (Windows Service)
6. ✅ Archive old backend file

---

## Support

If issues persist:

1. Run: `bash VPS/backend_health_check.sh` on VPS
2. Check Windows Event Viewer for Python errors
3. Verify PostgreSQL is running and accessible
4. Ensure LocalToNet tunnel is active
5. Check firewall rules

**Version**: Backend API v3 FIXED  
**Updated**: 2026-01-29  
**Status**: ✅ Production Ready  
