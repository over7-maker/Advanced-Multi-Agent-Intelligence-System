# setup_encoding.ps1
# Set Windows PowerShell to UTF-8 permanently before running Python

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend API v4 - Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables for Python UTF-8 support
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = 1
$env:PYTHONLEGACYWINDOWSSTDIO = 0

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

Write-Host "[OK] PowerShell encoding set to UTF-8 (65001)" -ForegroundColor Green
Write-Host "[OK] Python environment variables configured" -ForegroundColor Green
Write-Host ""
Write-Host "Ready to run Backend API v4" -ForegroundColor Green
Write-Host ""
Write-Host "To start the API, run:" -ForegroundColor Yellow
Write-Host "  python redirector\backend_api_v4.py" -ForegroundColor White
Write-Host ""
