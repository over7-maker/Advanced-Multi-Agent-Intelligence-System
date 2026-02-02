<#
.SYNOPSIS
    Backend API v4.0.2 - Comprehensive Test Suite
.DESCRIPTION
    Tests all 9 endpoints including NEW /connections endpoint for L4 Redirector compatibility
.NOTES
    Version: 4.0.2-timestamp-fix
    Date: 2026-02-01
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
Write-Host "  BACKEND API v4.0.2 - COMPREHENSIVE TEST SUITE" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0

# Test 1: Health Check (no auth)
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 1: Health Check (No Authentication)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
if (Test-Endpoint -Name "Health Check" -URL "$BaseURL/health" -RequireAuth $false) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 2: Stats (no auth)
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 2: Statistics (No Authentication)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
if (Test-Endpoint -Name "Statistics" -URL "$BaseURL/stats" -RequireAuth $false) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 3: Web Connections (Stream 1)
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 3: Web Connections (Stream 1)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
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
if (Test-Endpoint -Name "Web Connections" -URL "$BaseURL/api/v1/web/8041" -Method "POST" -Body $webData) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 4: L2N Tunnels (Stream 2)
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 4: L2N Tunnels (Stream 2)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
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
if (Test-Endpoint -Name "L2N Tunnels" -URL "$BaseURL/api/v1/l2n/8041" -Method "POST" -Body $l2nData) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 5: Connection Errors (Stream 3)
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 5: Connection Errors (Stream 3)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
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
if (Test-Endpoint -Name "Connection Errors" -URL "$BaseURL/api/v1/errors/l2n/8041" -Method "POST" -Body $errorData) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 6: Performance Metrics (Stream 4)
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 6: Performance Metrics (Stream 4)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
$perfData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    p50 = 25
    p95 = 150
    p99 = 300
    min = 10
    max = 500
    sample_count = 1000
}
if (Test-Endpoint -Name "Performance Metrics" -URL "$BaseURL/api/v1/performance/8041" -Method "POST" -Body $perfData) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 7: Throughput Stats (Stream 5)
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 7: Throughput Stats (Stream 5)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
$throughputData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    bytes_per_sec = 1048576
    connections_per_sec = 50.5
    total_bytes_in = 1073741824
    total_bytes_out = 2147483648
    total_connections = 10000
}
if (Test-Endpoint -Name "Throughput Stats" -URL "$BaseURL/api/v1/throughput/8041" -Method "POST" -Body $throughputData) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 8: Worker Health (Stream 6)
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 8: Worker Health (Stream 6)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
$workerData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    workers = @{
        worker_0 = @{ active_connections = 25; status = "healthy" }
        worker_1 = @{ active_connections = 30; status = "healthy" }
    }
    worker_count = 2
}
if (Test-Endpoint -Name "Worker Health" -URL "$BaseURL/api/v1/workers/status" -Method "POST" -Body $workerData) {
    $testsPassed++
} else {
    $testsFailed++
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 9: /connections Endpoint (v4.0.2+)
# ═══════════════════════════════════════════════════════════════════════════
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 9: /connections Endpoint (L4 Redirector compatibility v4.0.2+)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

$connectionBody = @{
    client_ip = "192.168.1.50"
    client_port = 54321
    frontend_port = 8041
    backend_host = "192.168.1.100"
    backend_port = 1429
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BaseURL/connections" `
                                  -Method POST `
                                  -Headers @{Authorization="Bearer $API_TOKEN"; "Content-Type"="application/json"} `
                                  -Body $connectionBody `
                                  -ErrorAction Stop
    
    if ($response.status -eq "success" -and $response.port -eq 8041) {
        Write-Host "✅ PASS: /connections endpoint working" -ForegroundColor Green
        Write-Host "   Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor DarkGray
        $testsPassed++
    } else {
        Write-Host "❌ FAIL: Unexpected response from /connections" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "❌ FAIL: /connections endpoint error: $($_.Exception.Message)" -ForegroundColor Red
    $testsFailed++
}

# Test 10: Port Health (Stream 7) - renumbered
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 10: Port Health (Stream 7)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
$healthData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    tcp_status = "UP"
    tcp_latency_ms = 12
    udp_status = "DOWN"
    uptime_sec = 86400
}
if (Test-Endpoint -Name "Port Health" -URL "$BaseURL/api/v1/health/8041" -Method "POST" -Body $healthData) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 11: Lifecycle Events (Stream 8) - renumbered
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "TEST 11: Lifecycle Events (Stream 8)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
$eventsData = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    events = @(
        @{ type = "start"; message = "Service started" }
        @{ type = "config_reload"; message = "Configuration reloaded" }
    )
    count = 2
}
if (Test-Endpoint -Name "Lifecycle Events" -URL "$BaseURL/api/v1/events/8041" -Method "POST" -Body $eventsData) {
    $testsPassed++
} else {
    $testsFailed++
}

# Summary
Write-Host "`n═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Total Tests: 11 (including /connections endpoint)" -ForegroundColor White
Write-Host "`n✅ Passed: $testsPassed" -ForegroundColor Green
Write-Host "❌ Failed: $testsFailed" -ForegroundColor Red

if ($testsFailed -eq 0) {
    Write-Host "`n🎉 ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  SOME TESTS FAILED - Check logs for details" -ForegroundColor Yellow
}

Write-Host "`n"
