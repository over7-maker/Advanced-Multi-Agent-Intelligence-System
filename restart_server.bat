@echo off
echo ========================================
echo AMAS Server Restart Script
echo ========================================
echo.

echo Stopping any existing server processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Setting environment variables...
set ENVIRONMENT=development
set PYTHONPATH=%CD%

echo.
echo Starting server...
echo Server will be available at: http://localhost:8000
echo Frontend will be at: http://localhost:8000/
echo API docs will be at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Try port 8000 first, if busy use 8001
netstat -ano | findstr :8000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [WARN] Port 8000 is busy, using port 8001 instead
    python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
) else (
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
)

pause

