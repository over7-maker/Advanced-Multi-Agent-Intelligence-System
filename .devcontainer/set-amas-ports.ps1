# Set AMAS devcontainer to use different ports to avoid conflicts
# Run this in PowerShell before opening the devcontainer if port 8000 is in use

$env:BACKEND_PORT = "8001"
$env:DASHBOARD_PORT = "8081"
$env:FRONTEND_PORT = "3001"

Write-Host "✅ AMAS devcontainer ports configured:" -ForegroundColor Green
Write-Host "   Backend:   http://localhost:$env:BACKEND_PORT"
Write-Host "   Dashboard: http://localhost:$env:DASHBOARD_PORT"
Write-Host "   Frontend:  http://localhost:$env:FRONTEND_PORT"
Write-Host ""
Write-Host "💡 These ports will be used when you open the devcontainer" -ForegroundColor Yellow
Write-Host "💡 Make sure to run this script in the same PowerShell session before opening the container" -ForegroundColor Yellow

