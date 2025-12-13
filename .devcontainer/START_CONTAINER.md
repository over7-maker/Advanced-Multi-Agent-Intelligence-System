# 🚀 Starting the AMAS Development Container

Complete guide to start and troubleshoot the AMAS devcontainer.

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Docker Desktop** installed and running (Windows/Mac) or **Docker Engine** (Linux)
- ✅ **VS Code** or **Cursor** with the "Dev Containers" extension installed
- ✅ **Git** installed (for cloning the repository)

## 🔍 Step 1: Validate Configuration

Before starting, validate your configuration:

```bash
# From project root directory
bash .devcontainer/validate-config.sh
```

This will check:
- ✅ Configuration files are valid
- ✅ Docker is running
- ✅ Ports are available
- ✅ All required files exist

**If validation fails**, fix the errors before proceeding.

## 🚀 Step 2: Start the Container

### Option A: Using VS Code / Cursor (Recommended)

1. **Open the project folder** in VS Code or Cursor
2. **When prompted**, click **"Reopen in Container"**
   - Or use Command Palette: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Type: `Dev Containers: Reopen in Container`
3. **Wait for build** (first time takes 5-10 minutes)
   - Subsequent starts are much faster (uses cache)

### Option B: Manual Docker Compose

```bash
# From project root
cd .devcontainer
docker-compose up -d --build

# Access the container
docker-compose exec amas-dev bash
```

## 🔌 Step 3: Handle Port Conflicts (If Needed)

If you see port conflict errors (`EADDRINUSE`), use different ports:

### Quick Fix Scripts

**Linux/WSL:**
```bash
source .devcontainer/set-amas-ports.sh
# Then reopen container
```

**PowerShell (Windows):**
```powershell
.\.devcontainer\set-amas-ports.ps1
# Then reopen container
```

### Manual Configuration

**Before opening the container**, set environment variables:

**Linux/WSL:**
```bash
export BACKEND_PORT=8001
export DASHBOARD_PORT=8081
export FRONTEND_PORT=3001
```

**PowerShell (Windows):**
```powershell
$env:BACKEND_PORT=8001
$env:DASHBOARD_PORT=8081
$env:FRONTEND_PORT=3001
```

**Then reopen the container** - it will use the new ports.

## ✅ Step 4: Verify Container is Running

After the container starts:

1. **Check container status:**
   ```bash
   docker ps | grep amas-dev
   ```

2. **Verify ports are forwarded:**
   - Open VS Code/Cursor "Ports" panel
   - You should see ports 8000, 8080, 3000 (or your custom ports)

3. **Test inside container:**
   ```bash
   # In container terminal
   python --version
   pip list | grep fastapi
   ```

## 🔍 Step 5: Test Backend After Container Starts

After the container is running, test if the backend can start:

### Quick Diagnostic Test

```bash
# Run comprehensive diagnostic
bash .devcontainer/test-backend.sh
```

This will:
- ✅ Check Python version
- ✅ Find application entry point (main.py)
- ✅ Test imports
- ✅ Verify dependencies
- ✅ Check port availability
- ✅ Test if uvicorn can load the app

### Quick Start Test

```bash
# Actually start the backend and test it
bash .devcontainer/start-backend-test.sh
```

This will:
- ✅ Start the backend server
- ✅ Test the /health endpoint
- ✅ Verify server is responding
- ✅ Stop the test server
- ✅ Show you the correct startup command

### Easy Startup (Recommended)

```bash
# Use the startup script (auto-detects correct entry point)
bash .devcontainer/start-backend.sh
```

### Manual Startup

If you prefer to start manually:

```bash
# Option 1: If main.py exists at root
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: If using src/amas/api/main.py
uvicorn src.amas.api.main:app --reload --host 0.0.0.0 --port 8000
```

The diagnostic script will tell you which command to use.

### Understanding Warnings

When the backend starts, you may see warnings like:
- `WARNING: Database initialization failed (optional)`
- `WARNING: Redis initialization failed (optional)`
- `WARNING: Neo4j initialization failed (optional)`

**These are NORMAL and expected!** The backend is designed to work without these services. The application will still function - you just won't have database/Redis/Neo4j features until you configure them.

## 🛠️ Troubleshooting

### Container Won't Start

**Problem:** Container fails to start or build

**Solutions:**
1. **Check Docker is running:**
   ```bash
   docker info
   ```
   If this fails, start Docker Desktop or Docker daemon.

2. **Check logs:**
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml logs
   ```

3. **Rebuild from scratch:**
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml build --no-cache
   ```

4. **Clear Docker cache:**
   ```bash
   docker system prune -a
   ```

### Port Already in Use

**Problem:** `EADDRINUSE: address already in use`

**Solutions:**
1. **Find what's using the port:**
   ```bash
   bash .devcontainer/fix-ports.sh
   ```

2. **Use different ports** (see Step 3 above)

3. **Stop conflicting process:**
   ```bash
   # Linux/WSL
   lsof -ti:8000 | xargs kill -9
   
   # Windows PowerShell
   Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
   Stop-Process -Id <PID> -Force
   ```

### Build Fails

**Problem:** Docker build fails with errors

**Solutions:**
1. **Check internet connection:**
   ```bash
   ping -c 3 pypi.org
   ```

2. **Check Docker proxy settings:**
   - Docker Desktop → Settings → Resources → Proxies
   - Disable proxy if not needed

3. **Try building manually:**
   ```bash
   cd .devcontainer
   docker build -f Dockerfile -t amas-dev ..
   ```

### Dependencies Not Installing

**Problem:** `pip install` fails in post-create script

**Solutions:**
1. **Install manually:**
   ```bash
   # In container
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Check network in container:**
   ```bash
   # In container
   ping -c 3 pypi.org
   curl -I https://pypi.org
   ```

### Backend Won't Start

**Problem:** Backend fails to start or shows import errors

**Solutions:**
1. **Run diagnostic test:**
   ```bash
   bash .devcontainer/test-backend.sh
   ```
   This will identify the exact issue.

2. **Check for import errors:**
   ```bash
   # Test if main.py can be imported
   python -c "import main; print('✅ OK')"
   
   # Or test src/amas/api/main.py
   python -c "from src.amas.api.main import app; print('✅ OK')"
   ```

3. **Check missing dependencies:**
   ```bash
   pip list | grep -E "(fastapi|uvicorn|pydantic)"
   ```

4. **Install missing packages:**
   ```bash
   pip install -r requirements.txt
   ```

### Container Starts But Can't Access Services

**Problem:** Container runs but ports aren't accessible

**Solutions:**
1. **Check port forwarding:**
   - VS Code/Cursor → Ports panel
   - Verify ports are forwarded
   - Manually forward if needed

2. **Check service is running:**
   ```bash
   # In container
   ps aux | grep uvicorn
   netstat -tulpn | grep 8000
   ```

3. **Start service manually:**
   ```bash
   # Run diagnostic first to find correct command
   bash .devcontainer/test-backend.sh
   
   # Then use the command it suggests, or:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   # OR
   uvicorn src.amas.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📊 Port Configuration Reference

| Service | Default Port | Environment Variable | Description |
|---------|-------------|---------------------|-------------|
| Backend API | 8000 | `BACKEND_PORT` | FastAPI backend |
| Dashboard | 8080 | `DASHBOARD_PORT` | Admin/Dashboard UI |
| Frontend | 3000 | `FRONTEND_PORT` | React frontend |

## 🔄 Common Commands

### Rebuild Container
```bash
# In VS Code/Cursor
Command Palette → "Dev Containers: Rebuild Container"

# Or manually
docker-compose -f .devcontainer/docker-compose.yml build
```

### Stop Container
```bash
# In VS Code/Cursor
Command Palette → "Dev Containers: Reopen Folder Locally"

# Or manually
docker-compose -f .devcontainer/docker-compose.yml down
```

### View Logs
```bash
docker-compose -f .devcontainer/docker-compose.yml logs -f
```

### Access Container Shell
```bash
docker-compose -f .devcontainer/docker-compose.yml exec amas-dev bash
```

## 📚 Additional Resources

- **Main README:** `.devcontainer/README.md`
- **Port Conflict Guide:** `.devcontainer/RESOLVE_PORT_CONFLICT.md`
- **Configuration Reference:** `.devcontainer/env.example`

## 🆘 Still Having Issues?

### Diagnostic Checklist

1. **Validate container configuration:**
   ```bash
   bash .devcontainer/validate-config.sh
   ```

2. **Test backend startup:**
   ```bash
   bash .devcontainer/test-backend.sh
   ```

3. **Try quick start test:**
   ```bash
   bash .devcontainer/start-backend-test.sh
   ```

4. **Check Docker logs:**
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml logs
   ```

5. **Verify configuration:**
   - Check `.devcontainer/devcontainer.json` syntax
   - Check `.devcontainer/docker-compose.yml` syntax
   - Ensure Dockerfile exists

6. **Check system requirements:**
   - Docker Desktop/Engine running
   - Sufficient disk space
   - Sufficient memory (recommended: 4GB+)

### Common Error Messages

**"ModuleNotFoundError"**
- Run: `pip install -r requirements.txt`
- Check: `bash .devcontainer/test-backend.sh` for missing packages

**"Address already in use"**
- Use different port: `export BACKEND_PORT=8001`
- Or stop conflicting process: `bash .devcontainer/fix-ports.sh`

**"No module named 'main'"**
- Check which main.py exists: `ls -la main.py src/amas/api/main.py`
- Run diagnostic: `bash .devcontainer/test-backend.sh`

---

**Need more help?** Check the main project README or open an issue.

