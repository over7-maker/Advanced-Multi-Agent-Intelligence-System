<#
.SYNOPSIS
    Windows Backend API - Quick Update to v4.0.2-timestamp-fix
.DESCRIPTION
    Automated update script for upgrading from v4.0.0-final to v4.0.2-timestamp-fix
.NOTES
    Version: 1.0
    Date: 2026-02-01
    Run as Administrator
#>

#Requires -RunAsAdministrator

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "║ WINDOWS BACKEND API v4.0.2 QUICK UPDATER                              ║" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ ERROR: Must run as Administrator" -ForegroundColor Red
    exit 1
}

# Configuration
$InstallPath = "C:\backend_api"

# Check if backend_api_v4.py exists
if (-not (Test-Path "$InstallPath\backend_api_v4.py")) {
    Write-Host "❌ ERROR: backend_api_v4.py not found at $InstallPath" -ForegroundColor Red
    Write-Host "   Please ensure the installation path is correct" -ForegroundColor Yellow
    exit 1
}

# Backup current version
Write-Host "`n[1/5] Backing up current backend_api_v4.py..." -ForegroundColor Yellow
$backupPath = "$InstallPath\backend_api_v4.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').py"
Copy-Item "$InstallPath\backend_api_v4.py" $backupPath -ErrorAction SilentlyContinue
Write-Host " ✅ Backup created: $backupPath" -ForegroundColor Green

# Check if service exists
Write-Host "`n[2/5] Checking for Windows Service..." -ForegroundColor Yellow
$service = Get-Service -Name "BackendAPIv4" -ErrorAction SilentlyContinue
if ($service) {
    Write-Host " Service found: $($service.Name) (Status: $($service.Status))" -ForegroundColor Cyan
    if ($service.Status -eq "Running") {
        Write-Host "   Stopping service..." -ForegroundColor Yellow
        Stop-Service -Name "BackendAPIv4" -Force
        Start-Sleep -Seconds 3
        Write-Host "   ✅ Service stopped" -ForegroundColor Green
    }
} else {
    Write-Host " ℹ️ No service found (manual run mode)" -ForegroundColor Gray
}

# Pull latest code from GitHub
Write-Host "`n[3/5] Pulling latest code from GitHub..." -ForegroundColor Yellow
try {
    Push-Location $InstallPath
    git pull origin main 2>&1 | Out-Null
    Pop-Location
    Write-Host " ✅ Code updated" -ForegroundColor Green
} catch {
    Write-Host " ⚠️ Git pull failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host " You may need to manually copy backend_api_v4.py from GitHub" -ForegroundColor Yellow
}

# Verify version
Write-Host "`n[4/5] Verifying version..." -ForegroundColor Yellow
$apiContent = Get-Content "$InstallPath\backend_api_v4.py" -Raw
if ($apiContent -match 'Version:\s*4.0.2-timestamp-fix') {
    Write-Host " ✅ Version v4.0.2-timestamp-fix confirmed" -ForegroundColor Green
} else {
    Write-Host " ⚠️ WARNING: Could not confirm v4.0.2-timestamp-fix" -ForegroundColor Yellow
    Write-Host " Check manually: Get-Content $InstallPath\backend_api_v4.py | Select-String 'Version'" -ForegroundColor Yellow
}

# Check for python-dateutil package
Write-Host "`n   Checking for python-dateutil package..." -ForegroundColor Yellow
try {
    python -c "import dateutil" 2>&1 | Out-Null
    Write-Host "   ✅ python-dateutil already installed" -ForegroundColor Green
} catch {
    Write-Host "   ℹ️ Installing python-dateutil..." -ForegroundColor Cyan
    pip install python-dateutil | Out-Null
    Write-Host "   ✅ python-dateutil installed" -ForegroundColor Green
}

# Restart service or provide manual run command
Write-Host "`n[5/5] Restarting..." -ForegroundColor Yellow
if ($service) {
    Start-Service -Name "BackendAPIv4"
    Start-Sleep -Seconds 3
    $serviceStatus = (Get-Service -Name "BackendAPIv4").Status
    if ($serviceStatus -eq "Running") {
        Write-Host "   ✅ Service restarted successfully" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Service failed to start. Check logs." -ForegroundColor Red
        Write-Host "   View logs: Get-Content C:\Logs\backend_api\backend_api_v4.log -Tail 50" -ForegroundColor Yellow
    }
} else {
    Write-Host " ℹ️ No service configured. To run manually:" -ForegroundColor Cyan
    Write-Host " `$env:DB_PASSWORD='your_password';`$env:API_TOKEN='your_token'; python $InstallPath\backend_api_v4.py" -ForegroundColor Gray
}

Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "UPDATE COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "`n📋 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Test /connections endpoint: .\test_api.ps1" -ForegroundColor White
Write-Host "2. Verify VPS L4 Redirector can connect (check VPS logs)" -ForegroundColor White
Write-Host "3. Monitor logs: Get-Content C:\Logs\backend_api\backend_api_v4.log -Tail 50 -Wait" -ForegroundColor White

Write-Host "`n⚠️ If issues occur, restore backup:" -ForegroundColor Yellow
Write-Host " Copy-Item $backupPath $InstallPath\backend_api_v4.py -Force" -ForegroundColor Gray
Write-Host " Restart-Service BackendAPIv4" -ForegroundColor Gray

Write-Host "`n🔗 VPS L4 Redirector Configuration:" -ForegroundColor Cyan
Write-Host " Edit /etc/l4-redirector/config.env on your VPS:" -ForegroundColor White
Write-Host " BACKEND_API_TOKEN=your_64_char_token" -ForegroundColor Gray
Write-Host " LOCALTONET_IP=YOUR_WINDOWS_IP" -ForegroundColor Gray
Write-Host " LOCALTONET_PORT=6921" -ForegroundColor Gray

Write-Host "`n✅ Update complete! Backend API v4.0.2-timestamp-fix is ready." -ForegroundColor Green
Write-Host ""
