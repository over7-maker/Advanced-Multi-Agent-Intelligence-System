# AMAS Devcontainer Setup

## 🐳 Why Use Docker/Devcontainer?

**Benefits:**
- ✅ **Consistent Environment** - Same setup across all machines
- ✅ **Isolation** - No conflicts with host system dependencies
- ✅ **Production-like** - Test in environment similar to production
- ✅ **Easy Setup** - One command to get everything working
- ✅ **Team Collaboration** - Everyone has identical development environment
- ✅ **Clean Slate** - Easy to reset if something breaks

## 🚀 Quick Start

### Option 1: Using Cursor/VS Code (Recommended)

1. **Open in Cursor/VS Code:**
   - Open the project folder in Cursor
   - When prompted, click "Reopen in Container"
   - Or use Command Palette: `Dev Containers: Reopen in Container`

2. **Wait for build:**
   - First time will take 5-10 minutes to build
   - Subsequent opens are much faster (uses cache)

3. **Start developing:**
   - Container automatically sets up dependencies
   - All tools pre-installed
   - Ports configured via environment variables (see Port Configuration below)

### Option 2: Manual Docker Build

```bash
# Build the container
docker-compose -f .devcontainer/docker-compose.yml build

# Run the container
docker-compose -f .devcontainer/docker-compose.yml up -d

# Access the container
docker-compose -f .devcontainer/docker-compose.yml exec amas-dev bash
```

## 🔧 Configuration

### Port Configuration

The devcontainer uses **docker-compose** for port management. Ports are configurable via environment variables to avoid conflicts.

**Default Ports:**
- **8000** - Backend API (FastAPI)
- **8080** - Dashboard/Admin UI
- **3000** - Frontend (React)

**If ports are in use**, set environment variables **before opening the devcontainer**:

**PowerShell (Windows):**
```powershell
$env:BACKEND_PORT=8001
$env:DASHBOARD_PORT=8081
$env:FRONTEND_PORT=3001
```

**Bash/WSL (Linux):**
```bash
export BACKEND_PORT=8001
export DASHBOARD_PORT=8081
export FRONTEND_PORT=3001
```

**Quick setup scripts:**
- Linux/WSL: `source .devcontainer/set-amas-ports.sh`
- PowerShell: `.\.devcontainer\set-amas-ports.ps1`

**Check port usage:**
```bash
bash .devcontainer/fix-ports.sh
```

For detailed port conflict resolution, see: `.devcontainer/RESOLVE_PORT_CONFLICT.md`

### Volumes

Persistent volumes for:
- `amas-pip-cache` - Python package cache (faster installs)
- `amas-node-modules` - Node modules cache

### Environment Variables

**Port Configuration (Set BEFORE opening devcontainer):**
- `BACKEND_PORT` - Backend API port (default: 8000)
- `DASHBOARD_PORT` - Dashboard port (default: 8080)
- `FRONTEND_PORT` - Frontend port (default: 3000)

**Application Environment:**
The `.env` file is automatically created in the project root if missing. See `.devcontainer/.env.example` for all available options.

**Example `.env` file:**
```env
AMAS_ENV=development
PYTHONPATH=/workspaces/Advanced-Multi-Agent-Intelligence-System

# Add your API keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
# ... see .devcontainer/.env.example for full list
```

## 🛠️ Troubleshooting

### Docker Proxy Issues

If you encounter TLS handshake timeouts:

1. **Check Docker Desktop Settings:**
   - Settings → Resources → Proxies
   - Disable proxy if not needed
   - Or configure correct proxy settings

2. **Update Docker daemon.json:**
   ```json
   {
     "proxies": {
       "http-proxy": "",
       "https-proxy": "",
       "no-proxy": "*"
     }
   }
   ```
   Then restart Docker Desktop

3. **Test Docker connectivity:**
   ```bash
   docker pull python:3.11-slim
   ```

### Build Fails

1. **Clear Docker cache:**
   ```bash
   docker system prune -a
   ```

2. **Rebuild from scratch:**
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml build --no-cache
   ```

### Container Won't Start / Port Conflicts

1. **Check Docker Desktop is running**
2. **Check ports aren't in use:**
   ```bash
   # Windows PowerShell
   Get-NetTCPConnection | Where-Object {$_.LocalPort -in @(8000,8080,3000)}
   
   # Linux/WSL
   netstat -tulpn | grep -E ":(8000|8080|3000)"
   # Or use the helper script:
   bash .devcontainer/fix-ports.sh
   ```
3. **Use different ports:**
   - Set `BACKEND_PORT`, `DASHBOARD_PORT`, `FRONTEND_PORT` environment variables
   - See `.devcontainer/RESOLVE_PORT_CONFLICT.md` for detailed instructions
4. **Check Docker logs:**
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml logs
   ```

### Dependencies Not Installing

1. **Check network connectivity in container:**
   ```bash
   ping -c 3 pypi.org
   ```

2. **Try installing manually:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## 📦 What's Included

- **Python 3.11** - Latest stable Python
- **FastAPI & Uvicorn** - Web framework
- **Development Tools:**
  - Black, Ruff, isort - Code formatting
  - Pytest - Testing framework
  - IPython, Jupyter - Interactive development
- **Node.js 18** - For frontend development
- **Git** - Version control
- **Docker-in-Docker** - For testing Docker builds
- **GitHub CLI** - For PR management

## 🔄 Updating the Container

To update dependencies:

1. **Update requirements files**
2. **Rebuild container:**
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml build
   ```
3. **Or rebuild in Cursor:**
   - Command Palette: `Dev Containers: Rebuild Container`

## 💡 Tips

- **First build is slow** - Subsequent builds use cache and are much faster
- **Use volumes** - Keeps pip/node caches between rebuilds
- **Port configuration** - Uses docker-compose for flexible port management
- **Port conflicts** - Use environment variables to change ports if needed
- **Git config** - Automatically set up for the workspace
- **.env file** - Created automatically if missing (see `.devcontainer/.env.example`)
- **Helper scripts** - Use `set-amas-ports.sh` or `set-amas-ports.ps1` for quick port setup

## 🆚 Local vs Container Development

| Feature | Local | Container |
|---------|-------|-----------|
| Setup Time | 10-30 min | 5-10 min (first time) |
| Consistency | Varies by machine | Identical everywhere |
| Isolation | Can conflict | Fully isolated |
| Reset | Manual cleanup | One command |
| Production-like | No | Yes |
| Resource Usage | Lower | Higher |

**Recommendation:** Use containers for consistency and production-like testing, use local for quick edits.

---

**Need help?** Check the main README.md or open an issue.

