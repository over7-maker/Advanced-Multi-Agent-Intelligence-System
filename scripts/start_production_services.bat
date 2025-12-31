@echo off
REM Script to start all production services (Backend + Frontend Preview)
echo ========================================
echo 🚀 Starting AMAS Production Services
echo ========================================
echo.

REM Check if backend is running
echo 📍 Checking Backend status...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Backend is not running on port 8000
    echo 📝 Starting Backend in new window...
    start "AMAS Backend" cmd /k "cd /d %~dp0\.. && set ENVIRONMENT=production && set DATABASE_URL=postgresql://postgres:amas_password@localhost:5432/amas && set REDIS_URL=redis://:amas_redis_password@localhost:6379/0 && set NEO4J_URI=bolt://localhost:7687 && set NEO4J_USER=neo4j && set NEO4J_PASSWORD=amas_password && python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000"
    echo ⏳ Waiting for backend to start...
    timeout /t 5 /nobreak >nul
) else (
    echo ✅ Backend is already running
)

echo.
echo 📍 Starting Frontend Preview (Port 4173)...
cd /d "%~dp0\..\frontend"

REM Check if frontend preview is already running
netstat -ano | findstr :4173 >nul 2>&1
if errorlevel 1 (
    echo 🚀 Starting Frontend Preview...
    start "AMAS Frontend Preview" cmd /k "cd /d %~dp0\..\frontend && npm run preview"
    echo ⏳ Waiting for frontend to start...
    timeout /t 3 /nobreak >nul
) else (
    echo ⚠️  Frontend preview is already running on port 4173
)

echo.
echo ========================================
echo ✅ Services Started!
echo ========================================
echo.
echo 🌐 Frontend Preview: http://localhost:4173
echo 🌐 Landing Page: http://localhost:4173/landing
echo 🌐 Testing Dashboard: http://localhost:4173/testing
echo 🌐 Dashboard: http://localhost:4173/dashboard
echo 🌐 Backend API: http://localhost:8000
echo 🌐 API Docs: http://localhost:8000/docs
echo.
echo 💡 Note: Make sure to rebuild frontend first if you made changes:
echo    scripts\rebuild_frontend_production.bat
echo.
pause

