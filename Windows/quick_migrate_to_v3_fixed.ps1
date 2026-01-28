# ============================================================================
# QUICK MIGRATION SCRIPT - Backend API v3 FIXED
# Automatically upgrades old backend to new fixed version
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Backend API v3 FIXED - Quick Migration Script                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# STEP 1: Check if old backend is running
# ============================================================================

Write-Host "[STEP 1] Checking for running old backend..." -ForegroundColor Yellow

$oldBackendProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -match "backend_api_production"
}

if ($oldBackendProcess) {
    Write-Host "  Found running old backend (PID: $($oldBackendProcess.Id))" -ForegroundColor Yellow
    Write-Host "  Stopping old backend..." -ForegroundColor Yellow
    
    try {
        Stop-Process -InputObject $oldBackendProcess -Force -ErrorAction Stop
        Start-Sleep -Seconds 2
        Write-Host "  ✓ Old backend stopped" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to stop old backend: $_" -ForegroundColor Red
        Write-Host "  Please close it manually and run this script again" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✓ No old backend running" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# STEP 2: Backup old file
# ============================================================================

Write-Host "[STEP 2] Backing up old backend file..." -ForegroundColor Yellow

$backendDir = "C:\Users\Administrator\API_monitoring_system"
$oldFile = "$backendDir\backend_api_production.py"
$backupFile = "$backendDir\backend_api_production.py.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"

if (Test-Path $oldFile) {
    try {
        Copy-Item -Path $oldFile -Destination $backupFile -ErrorAction Stop
        Write-Host "  ✓ Backup created: $(Split-Path $backupFile -Leaf)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to backup: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ℹ Old backend file not found (fresh install?)" -ForegroundColor Gray
}
Write-Host ""

# ============================================================================
# STEP 3: Download new backend
# ============================================================================

Write-Host "[STEP 3] Downloading new backend from GitHub..." -ForegroundColor Yellow

$newFile = "$backendDir\backend_api_v3_final_working.py"
$githubUrl = "https://raw.githubusercontent.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/main/Windows/backend_api_v3_final_working.py"

try {
    Write-Host "  Downloading from: $githubUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $githubUrl -OutFile $newFile -ErrorAction Stop
    Write-Host "  ✓ Downloaded: $(Split-Path $newFile -Leaf)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to download: $_" -ForegroundColor Red
    Write-Host "  Manual download: $githubUrl" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# ============================================================================
# STEP 4: Verify file size
# ============================================================================

Write-Host "[STEP 4] Verifying downloaded file..." -ForegroundColor Yellow

$fileSize = (Get-Item $newFile).Length
$fileSizeMB = [Math]::Round($fileSize / 1MB, 2)

if ($fileSize -gt 10KB -and $fileSize -lt 100KB) {
    Write-Host "  ✓ File size OK: $fileSizeMB MB" -ForegroundColor Green
} else {
    Write-Host "  ✗ File size unexpected: $fileSizeMB MB" -ForegroundColor Red
    Write-Host "  Expected: ~20-30 KB" -ForegroundColor Red
    exit 1
}
Write-Host ""

# ============================================================================
# STEP 5: Check Python dependencies
# ============================================================================

Write-Host "[STEP 5] Checking Python dependencies..." -ForegroundColor Yellow

$pythonExe = "python"
$requiredPackages = @("fastapi", "uvicorn", "asyncpg")

try {
    $pythonVersion = & $pythonExe --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found in PATH" -ForegroundColor Red
    Write-Host "  Please install Python or add it to PATH" -ForegroundColor Red
    exit 1
}

foreach ($package in $requiredPackages) {
    $result = & $pythonExe -m pip show $package 2>&1 | Select-String "Name:"
    if ($result) {
        Write-Host "  ✓ $package is installed" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $package NOT installed - installing..." -ForegroundColor Yellow
        try {
            & $pythonExe -m pip install $package --quiet -ErrorAction Stop
            Write-Host "    ✓ $package installed" -ForegroundColor Green
        } catch {
            Write-Host "    ✗ Failed to install $package" -ForegroundColor Red
            exit 1
        }
    }
}
Write-Host ""

# ============================================================================
# STEP 6: Test the new backend
# ============================================================================

Write-Host "[STEP 6] Starting new backend (test run)..." -ForegroundColor Yellow

try {
    Write-Host "  Starting process..." -ForegroundColor Gray
    $process = Start-Process -FilePath $pythonExe -ArgumentList $newFile -WindowStyle Hidden -PassThru -ErrorAction Stop
    
    Write-Host "  Waiting for backend to initialize (5 seconds)..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    # Check if process is still running
    $isRunning = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
    
    if ($isRunning) {
        Write-Host "  ✓ Backend started successfully (PID: $($process.Id))" -ForegroundColor Green
        
        # Try to connect
        Write-Host "  Testing connectivity..." -ForegroundColor Gray
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5814/health" -TimeoutSec 3 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "  ✓ Backend is responding on port 5814" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ⚠ Backend not responding yet (may take longer)" -ForegroundColor Yellow
        }
        
        # Stop test process
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Test process stopped" -ForegroundColor Green
        
    } else {
        Write-Host "  ✗ Backend process crashed immediately" -ForegroundColor Red
        Write-Host "  Check the log output above for errors" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ✗ Failed to start backend: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# ============================================================================
# STEP 7: Success!
# ============================================================================

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✓ MIGRATION SUCCESSFUL!                           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "New backend file: $newFile" -ForegroundColor Green
Write-Host "Backup of old:    $backupFile" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Start the backend manually to keep it running:" -ForegroundColor Cyan
Write-Host "     cd C:\Users\Administrator\API_monitoring_system" -ForegroundColor Cyan
Write-Host "     python backend_api_v3_final_working.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Or set it up as Windows Service (see WINDOWS_BACKEND_SETUP_v3_FIXED.md)" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. From VPS, verify with:" -ForegroundColor Cyan
Write-Host "     curl http://194.182.64.133:6921/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Run health check:" -ForegroundColor Cyan
Write-Host "     bash VPS/backend_health_check.sh" -ForegroundColor Cyan
Write-Host ""

Pause
