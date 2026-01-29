@echo off
REM ============================================================================
REM Backend API v4 - Offline Dependency Installer (Windows Batch)
REM ============================================================================
REM
REM Usage: install_dependencies.bat
REM or:    install_dependencies.bat C:\path\to\pywheels
REM
REM Installs all Python dependencies from local .whl files
REM No internet connection required
REM

setlocal enabledelayedexpansion

REM Color codes (Windows doesn't support ANSI, using text instead)
set "GREEN=[OK]"
set "RED=[ERROR]"
set "YELLOW=[WARN]"
set "INFO=[INFO]"

REM Get wheel directory from argument or use default
if "%~1"=="" (
    set "WHEEL_DIR=pywheels"
) else (
    set "WHEEL_DIR=%~1"
)

REM Header
echo.
echo ================================================================================
echo  Backend API v4 - Offline Dependency Installer (Windows Edition)
echo ================================================================================
echo.

REM Check if wheel directory exists
if not exist "%WHEEL_DIR%" (
    echo %RED% Wheel directory not found: %WHEEL_DIR%
    echo %INFO% Please provide the correct path:
    echo        install_dependencies.bat "C:\path\to\pywheels"
    echo.
    exit /b 1
)

echo %INFO% Wheel directory: %WHEEL_DIR%
echo.

REM List available wheels
echo %INFO% Scanning for .whl files...
echo.

setlocal enabledelayedexpansion
set count=0
for /r "%WHEEL_DIR%" %%F in (*.whl) do (
    set /a count+=1
    echo   - %%~nxF
)

if %count% equ 0 (
    echo %YELLOW% No .whl files found in %WHEEL_DIR%
    echo.
    echo %INFO% Required packages:
    echo   - fastapi
    echo   - uvicorn  
    echo   - psycopg[binary] or psycopg + tzdata
    echo   - psycopg-pool
    echo   - pydantic
    echo.
    exit /b 1
)

echo.
echo %GREEN% Found %count% wheel file(s)
echo.

REM Check Python
echo %INFO% Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED% Python not found or not in PATH
    exit /b 1
)
for /f "tokens=*" %%A in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%A"
echo %GREEN% Found: %PYTHON_VERSION%
echo.

REM Check pip
echo %INFO% Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo %RED% pip not found or not working
    exit /b 1
)
for /f "tokens=*" %%A in ('pip --version 2^>^&1') do set "PIP_VERSION=%%A"
echo %GREEN% Found: %PIP_VERSION%
echo.

REM Install packages
echo %INFO% Installing packages from local wheels...
echo.

setlocal enabledelayedexpansion
set success=0
set failed=0

for %%F in ("%WHEEL_DIR%\*.whl") do (
    set "wheel=%%~nxF"
    echo %INFO% Installing: !wheel!
    
    pip install --no-index --find-links "%WHEEL_DIR%" "%%F" >nul 2>&1
    if errorlevel 1 (
        echo %YELLOW% Installation skipped (may already be installed)
        set /a failed+=1
    ) else (
        echo %GREEN% Installed successfully
        set /a success+=1
    )
)

echo.
echo %INFO% Installation attempt completed
echo %GREEN% %success% packages installed/upgraded
if %failed% gtr 0 (
    echo %YELLOW% %failed% packages skipped/failed
)
echo.

REM Verify installations
echo %INFO% Verifying installations...
echo.

REM Check fastapi
python -c "import fastapi; print(fastapi.__version__)" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW% fastapi: NOT installed
) else (
    for /f "tokens=*" %%A in ('python -c "import fastapi; print(fastapi.__version__)" 2^>^&1') do echo %GREEN% fastapi: %%A
)

REM Check uvicorn
python -c "import uvicorn; print(uvicorn.__version__)" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW% uvicorn: NOT installed
) else (
    for /f "tokens=*" %%A in ('python -c "import uvicorn; print(uvicorn.__version__)" 2^>^&1') do echo %GREEN% uvicorn: %%A
)

REM Check psycopg
python -c "import psycopg; print(psycopg.__version__)" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW% psycopg: NOT installed
) else (
    for /f "tokens=*" %%A in ('python -c "import psycopg; print(psycopg.__version__)" 2^>^&1') do echo %GREEN% psycopg: %%A
)

REM Check psycopg-pool
python -c "import psycopg_pool" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW% psycopg-pool: NOT installed
) else (
    echo %GREEN% psycopg-pool: installed
)

REM Check pydantic
python -c "import pydantic; print(pydantic.__version__)" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW% pydantic: NOT installed
) else (
    for /f "tokens=*" %%A in ('python -c "import pydantic; print(pydantic.__version__)" 2^>^&1') do echo %GREEN% pydantic: %%A
)

REM Check tzdata
python -c "import tzdata" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW% tzdata: NOT installed (Windows may not need it)
) else (
    echo %GREEN% tzdata: installed
)

echo.
echo ================================================================================
echo  Installation complete!
echo ================================================================================
echo.
echo %INFO% Next steps:
echo   1. Set environment variables in .env file
echo   2. Run: python redirector\backend_api_v4.py
echo   3. Verify: curl http://localhost:5814/health
echo.
