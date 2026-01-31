<#
.SYNOPSIS
    Windows Backend API v4.0 - Automated Installation Script
.DESCRIPTION
    Complete installation and configuration for Windows Server 2019/2022
.NOTES
    Version: 4.0.0-final
    Date: 2026-01-31
    Run as Administrator
#>

#Requires -RunAsAdministrator

param(
    [string]$InstallPath = "C:\backend_api",
    [string]$LogPath = "C:\Logs\backend_api",
    [string]$DBPassword,
    [string]$APIToken
)

# Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Color output functions
function Write-Info { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Warn { Write-Host "⚠️  $args" -ForegroundColor Yellow }
function Write-Fail { Write-Host "❌ $args" -ForegroundColor Red }

Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  WINDOWS BACKEND API v4.0 - PRODUCTION INSTALLATION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "`n"

# Step 1: Validate prerequisites
Write-Info "Checking prerequisites..."

# Check Python
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(1[2-9]|[2-9]\d)") {
        Write-Info "Python found: $pythonVersion"
    } else {
        Write-Fail "Python 3.12+ required. Current: $pythonVersion"
        exit 1
    }
} catch {
    Write-Fail "Python not found. Install from: https://www.python.org/downloads/"
    exit 1
}

# Check PostgreSQL
try {
    $pgVersion = psql --version 2>&1
    Write-Info "PostgreSQL found: $pgVersion"
} catch {
    Write-Fail "PostgreSQL not found. Install from: https://www.postgresql.org/download/windows/"
    exit 1
}

# Step 2: Create directories
Write-Info "Creating directory structure..."
@($InstallPath, $LogPath) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -Path $_ -ItemType Directory -Force | Out-Null
        Write-Info "Created: $_"
    }
}

# Step 3: Install Python dependencies
Write-Info "Installing Python packages..."
$packages = @("aiohttp", "asyncpg", "python-dotenv")
pip install --upgrade pip | Out-Null
pip install $packages | Out-Null
Write-Info "Packages installed: $($packages -join ', ')"

# Step 4: Generate secure credentials if not provided
if (-not $DBPassword) {
    $DBPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    Write-Warn "Generated DB Password: $DBPassword"
}

if (-not $APIToken) {
    $APIToken = -join ((48..57) + (97..102) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    Write-Warn "Generated API Token: $APIToken"
}

# Step 5: Create config.env
Write-Info "Creating configuration file..."
$configContent = @"
# Windows Backend API v4.0 Configuration
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=redirector_db
DB_USER=redirector_user
DB_PASSWORD=$DBPassword

# API Configuration
API_HOST=0.0.0.0
API_PORT=6921
API_TOKEN=$APIToken
"@

$configContent | Out-File -FilePath "$InstallPath\config.env" -Encoding UTF8
Write-Info "Config file created: $InstallPath\config.env"

# Step 6: Database setup
Write-Info "Setting up PostgreSQL database..."

$env:PGPASSWORD = "postgres_admin_password"
$dbCommands = @"
CREATE DATABASE redirector_db;
CREATE USER redirector_user WITH ENCRYPTED PASSWORD '$DBPassword';
GRANT ALL PRIVILEGES ON DATABASE redirector_db TO redirector_user;
"@

try {
    $dbCommands | psql -U postgres -h localhost 2>&1 | Out-Null
    Write-Info "Database and user created"
} catch {
    Write-Warn "Database may already exist or incorrect postgres password"
}

# Step 7: Load schema
if (Test-Path "$InstallPath\database_schema.sql") {
    Write-Info "Loading database schema..."
    $env:PGPASSWORD = $DBPassword
    psql -U redirector_user -d redirector_db -h localhost -f "$InstallPath\database_schema.sql" 2>&1 | Out-Null
    Write-Info "Schema loaded successfully"
}

# Step 8: Install as Windows Service using NSSM
Write-Info "Installing Windows Service..."

# Check if NSSM is installed
if (-not (Get-Command nssm -ErrorAction SilentlyContinue)) {
    Write-Warn "NSSM not found. Download from: https://nssm.cc/download"
    Write-Warn "After installing NSSM, run:"
    Write-Host "  nssm install BackendAPIv4 `"$(where.exe python)`" `"$InstallPath\backend_api_v4.py`"" -ForegroundColor Yellow
    Write-Host "  nssm set BackendAPIv4 AppEnvironmentExtra :env_file=$InstallPath\config.env" -ForegroundColor Yellow
    Write-Host "  nssm start BackendAPIv4" -ForegroundColor Yellow
} else {
    # Remove existing service if present
    $service = Get-Service -Name "BackendAPIv4" -ErrorAction SilentlyContinue
    if ($service) {
        Write-Info "Removing existing service..."
        nssm stop BackendAPIv4 | Out-Null
        nssm remove BackendAPIv4 confirm | Out-Null
    }
    
    # Install service
    $pythonExe = (Get-Command python).Source
    nssm install BackendAPIv4 "$pythonExe" "$InstallPath\backend_api_v4.py" | Out-Null
    nssm set BackendAPIv4 AppDirectory $InstallPath | Out-Null
    nssm set BackendAPIv4 AppEnvironmentExtra "env_file=$InstallPath\config.env" | Out-Null
    nssm set BackendAPIv4 DisplayName "Backend API v4.0" | Out-Null
    nssm set BackendAPIv4 Description "Enterprise Data Collection API for L4 Redirector" | Out-Null
    nssm set BackendAPIv4 Start SERVICE_AUTO_START | Out-Null
    
    Write-Info "Service installed successfully"
}

# Step 9: Firewall rule
Write-Info "Configuring Windows Firewall..."
$firewallRule = Get-NetFirewallRule -DisplayName "Backend API v4.0" -ErrorAction SilentlyContinue
if (-not $firewallRule) {
    New-NetFirewallRule -DisplayName "Backend API v4.0" `
                       -Direction Inbound `
                       -Protocol TCP `
                       -LocalPort 6921 `
                       -Action Allow `
                       -Profile Domain,Private | Out-Null
    Write-Info "Firewall rule created for port 6921"
} else {
    Write-Info "Firewall rule already exists"
}

# Step 10: Summary
Write-Host "`n"
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "`n"

Write-Host "📁 Installation Path: " -NoNewline
Write-Host $InstallPath -ForegroundColor Yellow

Write-Host "📊 Database: " -NoNewline
Write-Host "redirector_db (localhost:5432)" -ForegroundColor Yellow

Write-Host "🌐 API Endpoint: " -NoNewline
Write-Host "http://localhost:6921" -ForegroundColor Yellow

Write-Host "`n🔐 IMPORTANT - Save these credentials:" -ForegroundColor Red
Write-Host "  DB Password: " -NoNewline
Write-Host $DBPassword -ForegroundColor Yellow
Write-Host "  API Token: " -NoNewline
Write-Host $APIToken -ForegroundColor Yellow

Write-Host "`n✅ Next steps:" -ForegroundColor Green
Write-Host "  1. Test health: curl http://localhost:6921/health"
Write-Host "  2. Start service: nssm start BackendAPIv4"
Write-Host "  3. Check logs: Get-Content $LogPath\backend_api_v4.log -Tail 50 -Wait"
Write-Host "  4. Configure VPS L4 Redirector with this API token"

Write-Host "`n"
