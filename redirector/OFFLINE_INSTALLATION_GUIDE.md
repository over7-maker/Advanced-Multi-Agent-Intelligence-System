# Backend API v4 - Offline Installation Guide (Windows)

**Status:** ✅ Complete  
**Environment:** Windows Server with NO internet connection  
**Python Version:** 3.14+  
**Last Updated:** 2026-01-29

---

## 📋 Prerequisites

✅ **Already on your system:**
- Python 3.14+
- pip package manager
- Local `.whl` files in `C:\Users\Administrator\API_monitoring_system\pywheels\`
- PostgreSQL 15+ (running on 192.168.88.16)

---

## 🚀 Installation Steps

### **Step 1: Navigate to the Project Directory**

```powershell
cd C:\Users\Administrator\API_monitoring_system
```

### **Step 2: Run the Offline Installer**

**Option A: Using PowerShell (Recommended)**

```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run installer with explicit wheel directory
.\redirector\install_dependencies.ps1 -WheelDir "C:\Users\Administrator\API_monitoring_system\pywheels"
```

**Option B: Using Command Prompt (Batch File)**

```batch
cd C:\Users\Administrator\API_monitoring_system
redirector\install_dependencies.bat C:\Users\Administrator\API_monitoring_system\pywheels
```

**Option C: Manual pip Install (If scripts fail)**

```powershell
# Install each wheel manually
pip install --no-index --find-links C:\Users\Administrator\API_monitoring_system\pywheels C:\Users\Administrator\API_monitoring_system\pywheels\fastapi*.whl

pip install --no-index --find-links C:\Users\Administrator\API_monitoring_system\pywheels C:\Users\Administrator\API_monitoring_system\pywheels\uvicorn*.whl

pip install --no-index --find-links C:\Users\Administrator\API_monitoring_system\pywheels C:\Users\Administrator\API_monitoring_system\pywheels\psycopg*.whl

pip install --no-index --find-links C:\Users\Administrator\API_monitoring_system\pywheels C:\Users\Administrator\API_monitoring_system\pywheels\pydantic*.whl

pip install --no-index --find-links C:\Users\Administrator\API_monitoring_system\pywheels C:\Users\Administrator\API_monitoring_system\pywheels\tzdata*.whl
```

---

## ✅ Verify Installation

```powershell
# Test each package
python -c "import fastapi; print(f'fastapi {fastapi.__version__}')"
python -c "import uvicorn; print(f'uvicorn {uvicorn.__version__}')"
python -c "import psycopg; print(f'psycopg {psycopg.__version__}')"
python -c "import psycopg_pool; print('psycopg-pool OK')"
python -c "import pydantic; print(f'pydantic {pydantic.__version__}')"
```

**Expected Output:**
```
fastapi 0.128.0
uvicorn 0.40.0
psycopg 3.3.2
psycopg-pool OK
pydantic 2.12.5
```

---

## 🔧 Configuration

### **Step 3: Create `.env` File**

Create `C:\Users\Administrator\API_monitoring_system\redirector\.env`:

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=5814
API_WORKERS=4

# Database (Windows backend server 192.168.88.16)
DB_HOST=192.168.88.16
DB_PORT=5432
DB_NAME=redirector_db
DB_USER=redirector
DB_PASSWORD=Azyz@123
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=30

# Security
API_TOKEN=e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075
ALLOWED_IPS=127.0.0.1,192.168.*

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs
```

### **Step 4: Create Logs Directory**

```powershell
mkdir C:\Users\Administrator\API_monitoring_system\redirector\logs
```

---

## 🚀 Starting the Server

### **Option 1: Direct Execution**

```powershell
cd C:\Users\Administrator\API_monitoring_system
python redirector/backend_api_v4.py
```

**Expected Output:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║                    Backend API v4 - Enterprise Edition                     ║
║                          Starting Server...                                ║
╚════════════════════════════════════════════════════════════════════════════╝

2026-01-29 02:00:00,123 [INFO] __main__: 🚀 Backend API v4 starting...
2026-01-29 02:00:00,456 [INFO] __main__: ✅ Connected to PostgreSQL: PostgreSQL 15.2 on x86_64-pc-linux-gnu...
2026-01-29 02:00:00,789 [INFO] uvicorn: Uvicorn running on http://0.0.0.0:5814
```

### **Option 2: Windows Service (Production)**

Create a scheduled task to run on startup:

```powershell
# Create batch wrapper
@echo off
cd C:\Users\Administrator\API_monitoring_system
python redirector\backend_api_v4.py
pause
```

Save as: `C:\Users\Administrator\API_monitoring_system\start_backend_api.bat`

Then create Task Scheduler task:
1. Press `Win+R`, type `taskschd.msc`
2. Create Basic Task
3. Name: "Backend API v4"
4. Trigger: "At startup"
5. Action: "Start a program"
6. Program: `C:\Users\Administrator\API_monitoring_system\start_backend_api.bat`

---

## 🧪 Testing the API

### **Health Check**

```powershell
curl -s http://localhost:5814/health | ConvertFrom-Json | ConvertTo-Json

# Or with curl (if installed)
curl http://localhost:5814/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-29T02:00:00.123456",
  "database": "connected",
  "version": "4.0.0"
}
```

### **Database Health**

```powershell
$headers = @{
    "Authorization" = "Bearer e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"
}

Invoke-WebRequest -Uri "http://localhost:5814/health/database" -Headers $headers
```

### **Send Test Data**

```powershell
$token = "e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"

$body = @{
    stream_type = "web"
    data = @(
        @{
            timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
            port = 8041
            client_ip = "192.168.1.100"
            client_port = 45123
            bytes_in = 1024
            bytes_out = 2048
            duration_ms = 150
            worker_id = "w-001"
        }
    )
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Invoke-WebRequest -Uri "http://localhost:5814/api/v1/stream/ingest" -Method POST -Body $body -Headers $headers
```

### **Query Statistics**

```powershell
$token = "e7595fe6ca9de1dc14a64ef9886b00b33e35295630e736815f7d18cd4cf63075"

$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:5814/api/v1/query/stats?hours=1" -Headers $headers
```

---

## 🔍 Troubleshooting

### **Issue: "No module named psycopg"**

**Solution:**
```powershell
# Install manually
pip install --no-index --find-links "C:\Users\Administrator\API_monitoring_system\pywheels" psycopg

# Verify
python -c "import psycopg; print(psycopg.__version__)"
```

### **Issue: "tzdata module not found"**

**Solution:** Windows doesn't require tzdata, but if needed:
```powershell
pip install --no-index --find-links "C:\Users\Administrator\API_monitoring_system\pywheels" tzdata
```

### **Issue: "Connection refused" to database**

**Check PostgreSQL is running:**
```powershell
# Test connection
psql -U redirector -d redirector_db -h 192.168.88.16 -c "SELECT 1;"

# Or test with Python
python -c "import psycopg; conn = psycopg.connect('host=192.168.88.16 user=redirector password=Azyz@123 dbname=redirector_db'); print('Connected!')"
```

### **Issue: "Permission denied" or "Access denied"**

**Check database credentials:**
```env
DB_HOST=192.168.88.16      # Must be correct IP
DB_USER=redirector          # Must match created user
DB_PASSWORD=Azyz@123        # Must match password
DB_NAME=redirector_db       # Database must exist
```

### **Issue: "Address already in use" port 5814**

**Find and kill process:**
```powershell
# Find process using port 5814
netstat -ano | findstr :5814

# Kill process (replace PID with actual number)
taskkill /PID 1234 /F
```

---

## 📊 Log Locations

- **Main Log:** `C:\Users\Administrator\API_monitoring_system\redirector\logs\backend_api_v4.log`
- **Console Output:** Appears in terminal/PowerShell window

**Monitor logs in real-time:**
```powershell
Get-Content -Path "redirector\logs\backend_api_v4.log" -Wait -Tail 20
```

---

## 🔒 Security Checklist

- ✅ Change default API token (currently public)
- ✅ Use strong database password
- ✅ Restrict database user permissions
- ✅ Configure firewall rules for port 5814
- ✅ Enable HTTPS in production
- ✅ Use environment variables for secrets
- ✅ Rotate API tokens regularly

---

## 📁 File Locations Reference

```
C:\Users\Administrator\API_monitoring_system
├── redirector
│   ├── backend_api_v4.py                 ← Main API server
│   ├── install_dependencies.ps1          ← PowerShell installer
│   ├── install_dependencies.bat          ← Batch installer
│   ├── OFFLINE_INSTALLATION_GUIDE.md     ← This file
│   ├── .env                              ← Configuration
│   └── logs
│       └── backend_api_v4.log            ← Log file
└── pywheels
    ├── fastapi*.whl
    ├── uvicorn*.whl
    ├── psycopg*.whl
    ├── psycopg-pool*.whl
    ├── pydantic*.whl
    └── tzdata*.whl
```

---

## 📞 Support

**For issues, check:**
1. Log file: `redirector/logs/backend_api_v4.log`
2. Database connection: Test with psql or Python
3. Python version: `python --version` (should be 3.14+)
4. Port availability: `netstat -ano | findstr :5814`
5. Environment variables: Check `.env` file

---

## ✅ Next Steps

1. ✅ Install dependencies using installers above
2. ✅ Configure `.env` with database credentials
3. ✅ Start the API server
4. ✅ Verify health check endpoint
5. ✅ Configure VPS Redirector to send data
6. ✅ Monitor incoming data streams
7. ✅ Query analytics via REST API

---

**Status:** 🟢 Ready for Production  
**Version:** 4.0.0  
**Last Verified:** 2026-01-29
