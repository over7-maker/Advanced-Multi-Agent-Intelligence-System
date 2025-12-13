@echo off
echo ========================================
echo Kill Process on Port 8000
echo ========================================
echo.

echo Finding process on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    set PID=%%a
    echo Found process: %%a
    echo Attempting to kill process %%a...
    taskkill /F /PID %%a /T 2>nul
    if %errorlevel% equ 0 (
        echo [OK] Process %%a killed
    ) else (
        echo [WARN] Could not kill process %%a - may require admin rights
        echo Try running as administrator
    )
)

echo.
echo Checking if port is free...
timeout /t 2 /nobreak >nul
netstat -ano | findstr :8000 | findstr LISTENING
if %errorlevel% equ 0 (
    echo [WARN] Port 8000 is still in use!
    echo You may need to:
    echo   1. Run this script as administrator
    echo   2. Stop Docker containers: docker stop amas-backend
    echo   3. Check for other services using port 8000
) else (
    echo [OK] Port 8000 is now free!
)

echo.
pause

