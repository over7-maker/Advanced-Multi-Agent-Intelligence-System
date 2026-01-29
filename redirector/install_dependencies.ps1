#Requires -Version 5.0
<#
.SYNOPSIS
    Offline dependency installer for Backend API v4 on Windows
.DESCRIPTION
    Installs all required Python packages from local .whl files
    No internet connection required
.PARAMETER WheelDir
    Directory containing .whl files (default: ./pywheels)
.EXAMPLE
    .\install_dependencies.ps1 -WheelDir "C:\Users\Administrator\API_monitoring_system\pywheels"
#>

param(
    [string]$WheelDir = "./pywheels"
)

# Colors for output
$Red = '\033[91m'
$Green = '\033[92m'
$Yellow = '\033[93m'
$Blue = '\033[94m'
$Reset = '\033[0m'

function Write-Header {
    Write-Host "$Blue"
    Write-Host "┌" + ("─" * 70) + "┐"
    Write-Host "│" + (" " * 10) + "Backend API v4 - Offline Dependency Installer" + (" " * 15) + "│"
    Write-Host "│" + (" " * 15) + "Windows PowerShell Edition" + (" " * 30) + "│"
    Write-Host "└" + ("─" * 70) + "┘"
    Write-Host "$Reset"
}

function Write-Success {
    param([string]$Message)
    Write-Host "$Green✅ $Message$Reset"
}

function Write-Error {
    param([string]$Message)
    Write-Host "$Red❌ $Message$Reset"
}

function Write-Warning {
    param([string]$Message)
    Write-Host "$Yellow⚠️  $Message$Reset"
}

function Write-Info {
    param([string]$Message)
    Write-Host "$Blueℹ️  $Message$Reset"
}

# Check if wheel directory exists
if (-not (Test-Path $WheelDir)) {
    Write-Error "Wheel directory not found: $WheelDir"
    Write-Info "Please provide the correct path using: .\install_dependencies.ps1 -WheelDir 'C:\path\to\pywheels'"
    exit 1
}

Write-Header

Write-Info "Wheel directory: $WheelDir"

# List available wheels
$wheels = Get-ChildItem $WheelDir -Filter "*.whl" -ErrorAction SilentlyContinue

if ($wheels.Count -eq 0) {
    Write-Warning "No .whl files found in $WheelDir"
    Write-Info "Required packages:"
    Write-Host "  - fastapi"
    Write-Host "  - uvicorn"
    Write-Host "  - psycopg[binary] or psycopg + tzdata"
    Write-Host "  - psycopg-pool"
    Write-Host "  - pydantic"
    exit 1
}

Write-Success "Found $($wheels.Count) wheel file(s):"
foreach ($wheel in $wheels) {
    Write-Host "  - $($wheel.Name)"
}

# Check Python
Write-Info ""
Write-Info "Checking Python installation..."
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python not found or not in PATH"
    exit 1
}
Write-Success "Found: $pythonVersion"

# Check pip
Write-Info ""
Write-Info "Checking pip installation..."
$pipVersion = pip --version
if ($LASTEXITCODE -ne 0) {
    Write-Error "pip not found or not working"
    exit 1
}
Write-Success "Found: $pipVersion"

# Upgrade pip first
Write-Info ""
Write-Info "Upgrading pip..."
python -m pip install --upgrade pip --no-index --find-links $WheelDir 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "pip upgraded successfully"
} else {
    Write-Warning "pip upgrade skipped (may be latest version)"
}

# Install wheels
Write-Info ""
Write-Info "Installing packages from local wheels..."
Write-Info ""

$successCount = 0
$failCount = 0

foreach ($wheel in $wheels) {
    $wheelPath = $wheel.FullName
    $wheelName = $wheel.Name
    
    Write-Info "Installing: $wheelName"
    
    # Extract package name from wheel filename
    # Format: {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl
    $parts = $wheelName -split '-'
    $packageName = $parts[0]
    
    pip install --no-index --find-links $WheelDir $wheelPath 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "$packageName installed"
        $successCount++
    } else {
        Write-Warning "$packageName install failed (may already be installed)"
        $failCount++
    }
}

Write-Info ""
Write-Info "Installation attempt completed"
Write-Success "$successCount packages installed/upgraded"
if ($failCount -gt 0) {
    Write-Warning "$failCount packages skipped/failed"
}

# Verify installations
Write-Info ""
Write-Info "Verifying installations..."
Write-Info ""

$packages = @(
    @{name = "fastapi"; cmd = "import fastapi; print(fastapi.__version__)"},
    @{name = "uvicorn"; cmd = "import uvicorn; print(uvicorn.__version__)"},
    @{name = "psycopg"; cmd = "import psycopg; print(psycopg.__version__)"},
    @{name = "psycopg-pool"; cmd = "import psycopg_pool; print(psycopg_pool.__version__)"},
    @{name = "pydantic"; cmd = "import pydantic; print(pydantic.__version__)"},
    @{name = "tzdata"; cmd = "import tzdata; print('installed')"}
)

foreach ($pkg in $packages) {
    $result = python -c $pkg.cmd 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "$($pkg.name): $result"
    } else {
        Write-Warning "$($pkg.name): NOT installed"
    }
}

Write-Info ""
Write-Info "Installation complete!"
Write-Info ""
Write-Info "Next steps:"
Write-Host "  1. Set environment variables in .env file"
Write-Host "  2. Run: python redirector/backend_api_v4.py"
Write-Host "  3. Verify: curl http://localhost:5814/health"
Write-Info ""
