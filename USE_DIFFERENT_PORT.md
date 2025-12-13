# Use Different Port to Avoid Process 70328

## Problem
Process 70328 is stuck on port 8000 and cannot be killed. This is likely a Docker container process that's protected.

## Solution: Use Port 8001 Temporarily

Since we can't kill process 70328, let's use a different port for your new server.

### Step 1: Start Server on Port 8001
```bash
set ENVIRONMENT=development
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Step 2: Test on Port 8001
- **Frontend**: http://localhost:8001/
- **API Health**: http://localhost:8001/api/v1/health
- **API Agents**: http://localhost:8001/api/v1/agents
- **Swagger**: http://localhost:8001/docs

### Step 3: Update Frontend API URL (If Needed)
If frontend is configured to use port 8000, update it:
- Check `frontend/src/services/api.ts`
- Change `baseURL` to `http://localhost:8001/api/v1`

## Alternative: Kill Process 70328 with Admin Rights

1. Right-click Command Prompt → "Run as administrator"
2. Run: `taskkill /F /PID 70328 /T`
3. If still fails, restart computer (process will be gone)

## What Was Fixed

✅ **Catch-all route removed** - API routes will work now
✅ **CSP fixed** - Swagger UI will load
✅ **Frontend serving fixed** - Frontend will be served as HTML

## After Testing on Port 8001

Once you confirm everything works on port 8001, you can:
1. Restart computer to clear process 70328
2. Or keep using port 8001
3. Or change process 70328's port (if it's Docker, modify docker-compose)

