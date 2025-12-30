@echo off
REM Script to rebuild frontend with all latest changes for production
echo ========================================
echo 🔄 Rebuilding Frontend for Production
echo ========================================
echo.

cd /d "%~dp0\..\frontend"

echo 📦 Step 1: Cleaning old build...
if exist dist (
    rmdir /s /q dist
    echo ✅ Old build removed
) else (
    echo ℹ️  No old build found
)

echo.
echo 📦 Step 2: Installing dependencies...
call npm install
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo 🔨 Step 3: Building frontend...
call npm run build:prod
if errorlevel 1 (
    echo ❌ Build failed
    exit /b 1
)
echo ✅ Build completed successfully

echo.
echo 📊 Step 4: Verifying build...
if exist dist\index.html (
    echo ✅ index.html found
) else (
    echo ❌ index.html not found!
    exit /b 1
)

if exist dist\assets (
    echo ✅ Assets directory found
) else (
    echo ⚠️  Assets directory not found
)

echo.
echo ========================================
echo ✅ Frontend rebuild complete!
echo ========================================
echo.
echo 📍 Build location: frontend\dist
echo 🌐 To preview: cd frontend && npm run preview
echo 🚀 Or access via backend: http://localhost:8000
echo.
pause

