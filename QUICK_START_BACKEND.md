# 🚀 Quick Start Backend - Port Conflict Fix

## ⚡ **Quick Fix for "Address already in use"**

If you see `ERROR: [Errno 98] Address already in use`, use one of these solutions:

### Solution 1: Use the Start Script (Easiest)

```bash
./START_BACKEND.sh
```

This script automatically:
- Kills any existing process on port 8000
- Starts the server
- Shows you the access URLs

### Solution 2: Kill Process Manually

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or kill all uvicorn processes
pkill -f "uvicorn main:app"

# Then start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Solution 3: Use a Different Port

```bash
# Use port 8001 instead
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Access at: http://localhost:8001
```

---

## ✅ **Verify Server is Running**

```bash
# Check if server is running
curl http://localhost:8000/health

# Or check process
ps aux | grep uvicorn
```

---

## 🎯 **Expected Output**

When server starts successfully:

```
INFO:     Started server process
INFO:     Waiting for application startup.
WARNING: Database initialization failed (optional)
WARNING: Redis initialization failed (optional)
WARNING: Neo4j initialization failed (optional)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Server is running!**

---

## 📋 **Access Points**

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **ReDoc**: http://localhost:8000/redoc

---

**Use `./START_BACKEND.sh` for easiest startup! 🚀**

