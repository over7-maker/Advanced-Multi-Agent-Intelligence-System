<#
.SYNOPSIS
    Backend API v4.0 - Comprehensive Test Suite
.DESCRIPTION
    Tests all 8 data stream endpoints and monitoring endpoints
.NOTES
    Version: 4.0.0-final
    Date: 2026-01-31
#>

param(
    [string]$ConfigPath = "C:\backend_api\config.env",
    [string]$BaseURL = "http://localhost:6921"
)

# Load configuration
if (Test-Path $ConfigPath) {
    Get-Content $ConfigPath | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.+)$') {
            Set-Variable -Name $matches[1].Trim() -Value $matches[2].Trim()
        }
    }
} else {
    Write-Host "❌ Config file not found: $ConfigPath" -ForegroundColor Red
    exit 1
}

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$URL,
        [string]$Method = "GET",
        [object]$Body = $null,
        [bool]$RequireAuth = $true
    )
    
    Write-Host "`n🧪 Testing: $Name" -ForegroundColor Cyan
    
    try {
        $headers = @{}
        if ($RequireAuth) {
            $headers["Authorization"] = "Bearer $API_TOKEN"
        }
        
        $params = @{
            Uri = $URL
            Method = $Method
            Headers = $headers
            ContentType = "application/json"
        }
        
        if ($Body) {
            $params["Body"] = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-RestMethod @params
        Write-Host "✅ PASS - Status: OK" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 10
        return $true
    } catch {
        Write-Host "❌ FAIL - Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  BACKEND API v4.0 - COMPREHENSIVE TEST SUITE" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

$results = @()

# Test 1: Health Check (no auth)
$results += Test-Endpoint -Name "Health Check" -URL "$BaseURL/health" -RequireAuth $false

# Test 2: Stats (no auth)
$results += Test-Endpoint -Name "Statistics" -URL "$BaseURL/stats" -RequireAuth $false

# Test 3: Web Connections (Stream 1)
$webData = @(
    @{
        timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        client_ip = "192.168.1.100"
        client_port = 54321
        bytes_in = 1024
        bytes_out = 2048
        duration_ms = 150
        worker_id = "test_worker"
        connection_id = "test_conn_1"
    }
)
$results += Test-Endpoint -Name "Web Connections (Stream 1)" `
                          -URL "$BaseURL/api/v1/web/8041" `
                          -Method "POST" `
                          -Body $webData

# Test 4: L2N Tunnels (Stream 2)
$l2nData = @(
    @{
        timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        backend_ip = "192.168.1.50"
        backend_port = 8080
        duration_ms = 200
        latency_ms = 15
        worker_id = "test_worker"
        tunnel_status = "active"
        localtonet_gateway = "gateway.localtonet.com"
        bytes_transferred = 5120
    }
)
$results += Test-Endpoint -Name "L2N Tunnels (Stream 2)" `
                          -URL "$BaseURL/api/v1/l2n/8041" `
                          -Method "POST" `
                          -Body $l2nData

# Test 5: Connection Errors (Stream 3)
$errorData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    error_type = "connection_timeout"
    backend_ip = "192.168.1.50"
    backend_port = 8080
    client_ip = "203.0.113.45"
    client_port = 54322
    error_message = "Connection timeout after 30s"
    worker_id = "test_worker"
}
$results += Test-Endpoint -Name "Connection Errors (Stream 3)" `
                          -URL "$BaseURL/api/v1/errors/l2n/8041" `
                          -Method "POST" `
                          -Body $errorData

# Test 6: Performance Metrics (Stream 4)
$perfData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    p50 = 25
    p95 = 150
    p99 = 300
    min = 10
    max = 500
    sample_count = 1000
}
$results += Test-Endpoint -Name "Performance Metrics (Stream 4)" `
                          -URL "$BaseURL/api/v1/performance/8041" `
                          -Method "POST" `
                          -Body $perfData

# Test 7: Throughput Stats (Stream 5)
$throughputData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    bytes_per_sec = 1048576
    connections_per_sec = 50.5
    total_bytes_in = 1073741824
    total_bytes_out = 2147483648
    total_connections = 10000
}
$results += Test-Endpoint -Name "Throughput Stats (Stream 5)" `
                          -URL "$BaseURL/api/v1/throughput/8041" `
                          -Method "POST" `
                          -Body $throughputData

# Test 8: Worker Health (Stream 6)
$workerData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    workers = @{
        worker_0 = @{ active_connections = 25; status = "healthy" }
        worker_1 = @{ active_connections = 30; status = "healthy" }
    }
    worker_count = 2
}
$results += Test-Endpoint -Name "Worker Health (Stream 6)" `
                          -URL "$BaseURL/api/v1/workers/status" `
                          -Method "POST" `
                          -Body $workerData

# Test 9: Port Health (Stream 7)
$healthData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    tcp_status = "UP"
    tcp_latency_ms = 12
    udp_status = "DOWN"
    uptime_sec = 86400
}
$results += Test-Endpoint -Name "Port Health (Stream 7)" `
                          -URL "$BaseURL/api/v1/health/8041" `
                          -Method "POST" `
                          -Body $healthData

# Test 10: Lifecycle Events (Stream 8)
$eventsData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    events = @(
        @{ type = "start"; message = "Service started" }
        @{ type = "config_reload"; message = "Configuration reloaded" }
    )
    count = 2
}
$results += Test-Endpoint -Name "Lifecycle Events (Stream 8)" `
                          -URL "$BaseURL/api/v1/events/8041" `
                          -Method "POST" `
                          -Body $eventsData

# Summary
Write-Host "`n"
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

$passed = ($results | Where-Object { $_ -eq $true }).Count
$failed = ($results | Where-Object { $_ -eq $false }).Count

Write-Host "`n✅ Passed: $passed" -ForegroundColor Green
Write-Host "❌ Failed: $failed" -ForegroundColor Red
Write-Host "📊 Total: $($results.Count)" -ForegroundColor Yellow

if ($failed -eq 0) {
    Write-Host "`n🎉 ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  SOME TESTS FAILED - Check logs for details" -ForegroundColor Yellow
}

Write-Host "`n"
