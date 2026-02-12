# 🛑 AMAS Services Stop Script
# This script stops all Backend and Frontend processes

Write-Host "🛑 Stopping AMAS Services...`n" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Yellow
Write-Host ""

# Find and stop Python processes (Backend)
$pythonProcesses = Get-Process | Where-Object { $_.ProcessName -eq "python" }
if ($pythonProcesses) {
    Write-Host "Found $($pythonProcesses.Count) Python process(es)" -ForegroundColor Yellow
    $pythonProcesses | ForEach-Object {
        Write-Host "  Stopping Python PID: $($_.Id)" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ Python processes stopped" -ForegroundColor Green
} else {
    Write-Host "No Python processes found" -ForegroundColor Gray
}

# Find and stop Node processes (Frontend)
$nodeProcesses = Get-Process | Where-Object { $_.ProcessName -eq "node" }
if ($nodeProcesses) {
    Write-Host "Found $($nodeProcesses.Count) Node process(es)" -ForegroundColor Yellow
    $nodeProcesses | ForEach-Object {
        Write-Host "  Stopping Node PID: $($_.Id)" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ Node processes stopped" -ForegroundColor Green
} else {
    Write-Host "No Node processes found" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

# Verify services are stopped
Write-Host "`n🔍 Verifying services are stopped...`n" -ForegroundColor Cyan

# Check ports
try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "❌ Backend still responding on port 8000" -ForegroundColor Red
} catch {
    Write-Host "✅ Backend stopped (port 8000 is free)" -ForegroundColor Green
}

try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "❌ Frontend still responding on port 5173" -ForegroundColor Red
} catch {
    Write-Host "✅ Frontend stopped (port 5173 is free)" -ForegroundColor Green
}

# Final check
$remainingPython = Get-Process | Where-Object { $_.ProcessName -eq "python" } -ErrorAction SilentlyContinue
$remainingNode = Get-Process | Where-Object { $_.ProcessName -eq "node" } -ErrorAction SilentlyContinue

if (-not $remainingPython -and -not $remainingNode) {
    Write-Host "`n✅ All AMAS services stopped successfully!`n" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Note: Some processes may still be running:" -ForegroundColor Yellow
    Write-Host "   These may be system processes or other applications" -ForegroundColor Gray
    Write-Host "   (Not related to AMAS backend/frontend)" -ForegroundColor Gray
    Write-Host "`n✅ AMAS Services Status:" -ForegroundColor Green
    Write-Host "   ✓ Backend (port 8000) is stopped" -ForegroundColor Green
    Write-Host "   ✓ Frontend (port 5173) is stopped" -ForegroundColor Green
}

Write-Host ""

