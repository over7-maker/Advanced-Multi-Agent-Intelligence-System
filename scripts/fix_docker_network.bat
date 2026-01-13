@echo off
REM Script to fix Docker network conflicts
echo ========================================
echo 🔧 Fixing Docker Network Conflicts
echo ========================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running!
    echo 💡 Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo 🔍 Checking for conflicting networks...
echo.

REM List all networks
echo 📋 Current Docker networks:
docker network ls | findstr amas-network
echo.

echo 🔧 Attempting to remove conflicting network...
docker network rm advanced-multi-agent-intelligence-system_amas-network 2>nul
if errorlevel 1 (
    echo ℹ️  Network not found or already removed
) else (
    echo ✅ Network removed successfully
)

echo.
echo 🧹 Cleaning up unused networks...
docker network prune -f

echo.
echo ========================================
echo ✅ Network cleanup complete!
echo ========================================
echo.
echo 💡 Now try running: scripts\start_databases.bat
echo.
pause

