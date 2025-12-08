@echo off
REM Setup Git Authentication for GitHub
echo Setting up Git authentication...

REM Check if GitHub CLI is installed
where gh >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo GitHub CLI not found. Installing...
    winget install --id GitHub.cli
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install GitHub CLI. Please install manually.
        echo Download from: https://cli.github.com/
        pause
        exit /b 1
    )
)

REM Authenticate with GitHub
echo.
echo Please authenticate with GitHub...
gh auth login

REM Configure Git credential helper
git config --global credential.helper manager-core

REM Test authentication
echo.
echo Testing authentication...
gh auth status

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Authentication successful!
    echo You can now push to GitHub.
) else (
    echo.
    echo ❌ Authentication failed. Please try again.
    pause
    exit /b 1
)

pause



