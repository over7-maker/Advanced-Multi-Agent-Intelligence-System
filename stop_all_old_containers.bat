@echo off
echo ========================================
echo Stopping Old AMAS Docker Containers
echo ========================================
echo.

echo Stopping old backend container...
docker stop amas-backend 2>nul
if %errorlevel% equ 0 (
    echo [OK] amas-backend stopped
) else (
    echo [INFO] amas-backend not running or already stopped
)

echo.
echo Stopping old web container...
docker stop amas-web 2>nul
if %errorlevel% equ 0 (
    echo [OK] amas-web stopped
) else (
    echo [INFO] amas-web not running or already stopped
)

echo.
echo Stopping old agent orchestrator...
docker stop amas-agent-orchestrator 2>nul
if %errorlevel% equ 0 (
    echo [OK] amas-agent-orchestrator stopped
) else (
    echo [INFO] amas-agent-orchestrator not running or already stopped
)

echo.
echo Stopping old security service...
docker stop amas-security-service 2>nul
if %errorlevel% equ 0 (
    echo [OK] amas-security-service stopped
) else (
    echo [INFO] amas-security-service not running or already stopped
)

echo.
echo ========================================
echo Checking port 8000...
echo ========================================
netstat -ano | findstr :8000 | findstr LISTENING
if %errorlevel% equ 0 (
    echo [WARN] Port 8000 is still in use!
    echo Please check the output above for the PID and kill it manually:
    echo   taskkill /F /PID <pid>
) else (
    echo [OK] Port 8000 is free!
)

echo.
echo ========================================
echo Done!
echo ========================================
echo.
echo You can now start your new server with:
echo   restart_server.bat
echo.

pause

