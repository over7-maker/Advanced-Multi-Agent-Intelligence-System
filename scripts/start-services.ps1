# 🚀 AMAS Services Startup Script
# This script starts both Backend and Frontend in separate PowerShell windows

Write-Host "🚀 Starting AMAS Services...`n" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Get the project root directory
$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $projectRoot "frontend"

# Check if .env file exists
$envFile = Join-Path $projectRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "⚠️  Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "   Creating from .env.example if available..." -ForegroundColor Gray
    $envExample = Join-Path $projectRoot ".env.example"
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "   ✅ Created .env from .env.example" -ForegroundColor Green
        Write-Host "   ⚠️  Please update .env with your actual values!" -ForegroundColor Yellow
    }
}

# Set environment variables
$env:ENVIRONMENT = "development"
if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "postgresql://postgres:amas_password@localhost:5432/amas"
}
if (-not $env:REDIS_URL) {
    $env:REDIS_URL = "redis://localhost:6379/0"
}

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Environment: $env:ENVIRONMENT" -ForegroundColor Gray
Write-Host "   Database: $env:DATABASE_URL" -ForegroundColor Gray
Write-Host "   Redis: $env:REDIS_URL" -ForegroundColor Gray
Write-Host ""

# Start Backend in a new PowerShell window
Write-Host "🚀 Starting Backend (FastAPI)...`n" -ForegroundColor Cyan
$backendScript = @"
`$env:ENVIRONMENT='development'
`$env:DATABASE_URL='$env:DATABASE_URL'
`$env:REDIS_URL='$env:REDIS_URL'
cd '$projectRoot'
Write-Host '🚀 AMAS Backend Server' -ForegroundColor Cyan
Write-Host '📍 URL: http://localhost:8000' -ForegroundColor Green
Write-Host '📚 Docs: http://localhost:8000/docs' -ForegroundColor Green
Write-Host '💚 Health: http://localhost:8000/health' -ForegroundColor Green
Write-Host ''
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --reload
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript -WindowStyle Normal
Write-Host "   ✅ Backend started in new window" -ForegroundColor Green
Start-Sleep -Seconds 2

# Check if frontend directory exists
if (-not (Test-Path $frontendDir)) {
    Write-Host "`n❌ Frontend directory not found: $frontendDir" -ForegroundColor Red
    Write-Host "   Skipping Frontend startup..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "✅ Backend is starting..." -ForegroundColor Green
    Write-Host "   Check the PowerShell window for Backend logs" -ForegroundColor Gray
    exit 0
}

# Check if node_modules exists
$nodeModules = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host "`n📦 Installing Frontend dependencies...`n" -ForegroundColor Yellow
    Set-Location $frontendDir
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n❌ Failed to install Frontend dependencies!" -ForegroundColor Red
        Write-Host "   Please run 'npm install' manually in the frontend directory" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "`n✅ Dependencies installed`n" -ForegroundColor Green
}

# Start Frontend in a new PowerShell window
Write-Host "🚀 Starting Frontend (Vite + React)...`n" -ForegroundColor Cyan
$frontendScript = @"
cd '$frontendDir'
Write-Host '🚀 AMAS Frontend Dev Server' -ForegroundColor Cyan
Write-Host '📍 URL: http://localhost:5173' -ForegroundColor Green
Write-Host '🌐 Landing: http://localhost:5173/landing' -ForegroundColor Green
Write-Host '🧪 Testing: http://localhost:5173/testing' -ForegroundColor Green
Write-Host '📊 Dashboard: http://localhost:5173/dashboard' -ForegroundColor Green
Write-Host ''
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal
Write-Host "   ✅ Frontend started in new window" -ForegroundColor Green

# Wait a bit for services to start
Write-Host "`n⏳ Waiting for services to start...`n" -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "📊 Checking Services Status...`n" -ForegroundColor Cyan

# Check Backend
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Backend: RUNNING" -ForegroundColor Green
    Write-Host "   URL: http://localhost:8000" -ForegroundColor Gray
    Write-Host "   Status: $($backendResponse.StatusCode)" -ForegroundColor Gray
} catch {
    Write-Host "⏳ Backend: Starting... (may take 10-15 seconds)" -ForegroundColor Yellow
    Write-Host "   Check the PowerShell window for Backend logs" -ForegroundColor Gray
}

# Check Frontend
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Frontend: RUNNING" -ForegroundColor Green
    Write-Host "   URL: http://localhost:5173" -ForegroundColor Gray
    Write-Host "   Status: $($frontendResponse.StatusCode)" -ForegroundColor Gray
} catch {
    Write-Host "⏳ Frontend: Starting... (Vite compilation may take 15-20 seconds)" -ForegroundColor Yellow
    Write-Host "   Check the PowerShell window for Frontend logs" -ForegroundColor Gray
}

Write-Host "`n🌐 Quick Access URLs:`n" -ForegroundColor Cyan
Write-Host "  Backend:" -ForegroundColor Yellow
Write-Host "    - API: http://localhost:8000" -ForegroundColor White
Write-Host "    - Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "    - Health: http://localhost:8000/health" -ForegroundColor White
Write-Host "`n  Frontend:" -ForegroundColor Yellow
Write-Host "    - Main: http://localhost:5173" -ForegroundColor White
Write-Host "    - Landing: http://localhost:5173/landing" -ForegroundColor White
Write-Host "    - Testing: http://localhost:5173/testing" -ForegroundColor White
Write-Host "    - Dashboard: http://localhost:5173/dashboard" -ForegroundColor White

Write-Host "`n💡 Both services are running in separate PowerShell windows.`n" -ForegroundColor Cyan
Write-Host "   To stop services, close the PowerShell windows or run:" -ForegroundColor Gray
Write-Host "   .\scripts\stop-services.ps1`n" -ForegroundColor Gray

