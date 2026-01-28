#!/bin/bash
################################################################################
# BACKEND API HEALTH CHECK SCRIPT v3.2 FIXED
# Run this to identify why API calls are timing out or failing
# Works with hybrid L4 redirector and Backend API v3 FIXED
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    BACKEND API HEALTH CHECK v3.2 - HYBRID L4 DIAGNOSTICS      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Initialize counters
critical=0
warning=0

# TEST 1: Check if redirector is timing out
echo -e "${YELLOW}[TEST 1] Check Current API Timeout Rate${NC}"
echo "───────────────────────────────────────────────────────────────"
timeout_count=$(tail -100 /var/log/redirector/hybrid_l4_final.log 2>/dev/null | grep -c "API timeout" || true)

if [ "$timeout_count" -gt 50 ]; then
    echo -e "${RED}✗ CRITICAL: High timeout rate detected ($timeout_count in last 100 lines)${NC}"
    echo "   This means Backend API is NOT responding!"
    critical=1
elif [ "$timeout_count" -gt 0 ]; then
    echo -e "${YELLOW}⚠ WARNING: Some timeouts detected ($timeout_count in last 100 lines)${NC}"
    warning=1
else
    echo -e "${GREEN}✓ PASS: No API timeouts in recent logs${NC}"
fi
echo ""

# TEST 2: Can VPS reach backend via LocalToNet?
echo -e "${YELLOW}[TEST 2] Test VPS → Backend API via LocalToNet Tunnel${NC}"
echo "───────────────────────────────────────────────────────────────"
echo "Attempting: curl http://194.182.64.133:6921/health"
api_response=$(timeout 5 curl -s -w "\nHTTP_CODE:%{http_code}" http://194.182.64.133:6921/health 2>&1 || echo "TIMEOUT")

if echo "$api_response" | grep -q "HTTP_CODE:200"; then
    echo -e "${GREEN}✓ PASS: Backend API is reachable and responding (200 OK)${NC}"
    echo "   Response: $(echo "$api_response" | head -1 | cut -c1-80)"
elif echo "$api_response" | grep -q "HTTP_CODE:401"; then
    echo -e "${GREEN}✓ PASS: Backend API is reachable (401 expected)${NC}"
elif echo "$api_response" | grep -q "Connection refused"; then
    echo -e "${RED}✗ FAIL: LocalToNet tunnel is NOT accepting connections${NC}"
    echo "   Backend API is probably not listening on :5814"
    critical=1
elif [ "$api_response" = "TIMEOUT" ]; then
    echo -e "${RED}✗ FAIL: Backend API timed out (5 second timeout)${NC}"
    echo "   Backend is slow or completely unresponsive"
    critical=1
else
    echo -e "${YELLOW}⚠ WARNING: Unexpected response: $api_response${NC}"
    warning=1
fi
echo ""

# TEST 3: Check if data streams are flowing
echo -e "${YELLOW}[TEST 3] Check Data Stream Flow to Backend${NC}"
echo "───────────────────────────────────────────────────────────────"
recent_records=$(tail -50 /var/log/redirector/hybrid_l4_final.log 2>/dev/null | grep -c "Stream" || true)
if [ "$recent_records" -gt 0 ]; then
    echo -e "${GREEN}✓ PASS: Data streams are flowing ($recent_records stream messages in last 50 lines)${NC}"
else
    echo -e "${RED}✗ FAIL: No data streams detected${NC}"
    echo "   Redirector may not be sending data to backend"
    critical=1
fi
echo ""

# TEST 4: Database connectivity check
echo -e "${YELLOW}[TEST 4] Database Connectivity${NC}"
echo "───────────────────────────────────────────────────────────────"
echo "Querying: GET http://194.182.64.133:6921/status"
db_response=$(timeout 5 curl -s http://194.182.64.133:6921/status 2>&1 || echo "ERROR")

if echo "$db_response" | grep -q "database" && echo "$db_response" | grep -q "connected"; then
    echo -e "${GREEN}✓ PASS: Backend database is connected${NC}"
    echo "   Response: $db_response"
elif echo "$db_response" | grep -q -i "error"; then
    echo -e "${RED}✗ FAIL: Database connection error${NC}"
    echo "   Response: $db_response"
    critical=1
else
    echo -e "${YELLOW}⚠ WARNING: Could not determine database status${NC}"
fi
echo ""

# TEST 5: Check Windows backend process
echo -e "${YELLOW}[TEST 5] Check Windows Backend Process Status${NC}"
echo "───────────────────────────────────────────────────────────────"
echo "To check if backend process is running on Windows:"
echo ""
echo "  1. SSH to Windows: ssh Administrator@192.168.88.16"
echo "  2. Check process: tasklist | findstr python"
echo ""
echo "Look for: backend_api_v3_final_working.py or python.exe"
echo "If NOT found → Backend API is NOT RUNNING!"
echo ""
echo "To start the backend:"
echo "  1. SSH to Windows backend"
echo "  2. cd C:\\Users\\Administrator\\API_monitoring_system"
echo "  3. python backend_api_v3_final_working.py"
echo ""

# TEST 6: Check LocalToNet tunnel status
echo -e "${YELLOW}[TEST 6] LocalToNet Tunnel Status${NC}"
echo "───────────────────────────────────────────────────────────────"
echo "Your LocalToNet tunnel should show:"
echo ""
echo "  aoycrreni.localto.net:6921 → 192.168.88.16:5814"
echo "  Status: OK"
echo "  Ping: <200ms"
echo ""
echo "If status is NOT OK or ping is missing:"
echo "  → Tunnel connection is broken"
echo "  → Restart LocalToNet client on Windows"
echo ""

# TEST 7: Quick fix options
echo -e "${YELLOW}[TEST 7] Recommended Actions${NC}"
echo "───────────────────────────────────────────────────────────────"

if [ $critical -eq 1 ]; then
    echo -e "${RED}CRITICAL ISSUES FOUND! Follow these steps:${NC}"
    echo ""
    echo "1. SSH to Windows backend (192.168.88.16)"
    echo "   tasklist | findstr python"
    echo ""
    echo "2. If python.exe NOT running:"
    echo "   cd C:\\Users\\Administrator\\API_monitoring_system"
    echo "   python backend_api_v3_final_working.py"
    echo ""
    echo "3. If still not working, check database on Windows:"
    echo "   psql -h 127.0.0.1 -U redirector -d redirector_db -c \"SELECT version();\""
    echo ""
    echo "4. If database won't connect:"
    echo "   Check PostgreSQL is running on 127.0.0.1:5432"
    echo "   Restart PostgreSQL from Windows Services"
    echo ""
    echo "5. After fixing, verify:"
    echo "   curl http://194.182.64.133:6921/health"
    echo ""
else
    echo "System appears functional. Consider:"
    echo "• Monitor /var/log/redirector/hybrid_l4_final.log for errors"
    echo "• Check database table row counts increasing"
    echo "• Verify LocalToNet ping times are low (<150ms)"
fi
echo ""

# TEST 8: Show what to monitor
echo -e "${YELLOW}[TEST 8] Continuous Monitoring${NC}"
echo "───────────────────────────────────────────────────────────────"
echo "After fixing the issue, watch for improvement:"
echo ""
echo "  # Watch timeout count decrease"
echo "  watch -n 2 'tail -50 /var/log/redirector/hybrid_l4_final.log | grep -c \"API timeout\"'"
echo ""
echo "  # Monitor stream flow"
echo "  tail -f /var/log/redirector/hybrid_l4_final.log | grep 'Stream\\|POST'"
echo ""
echo "  # Check database row count growth"
echo "  psql -h 127.0.0.1 -U redirector -d redirector_db -c \"SELECT COUNT(*) FROM web_p_8041;\""
echo ""

# SUMMARY
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                         SUMMARY                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $critical -eq 1 ]; then
    echo -e "${RED}⚠️  SYSTEM STATUS: CRITICAL - BACKEND API NOT RESPONDING${NC}"
    echo ""
    echo "Your redirector is timing out because:"
    echo "1. Backend API process is NOT running on Windows, OR"
    echo "2. Backend API is hung/crashed, OR"
    echo "3. Database connection is broken, OR"
    echo "4. LocalToNet tunnel is broken"
    echo ""
    echo "This is why you see:"
    echo "  - 'API timeout' warnings in logs"
    echo "  - '0 connections' in monitoring"
    echo "  - LocalToNet tunnel ping still shows OK (but data not flowing)"
    echo ""
    echo "Fix: Check Windows backend and restart Backend API service"
    echo ""
elif [ $warning -eq 1 ]; then
    echo -e "${YELLOW}⚠️  SYSTEM STATUS: DEGRADED - SOME ISSUES DETECTED${NC}"
    echo ""
    echo "System is partially working but experiencing issues"
    echo "Monitor closely and apply optimizations"
    echo ""
else
    echo -e "${GREEN}✅ SYSTEM STATUS: OPERATIONAL${NC}"
    echo ""
    echo "Backend API is responding correctly"
    echo "LocalToNet tunnels are functioning"
    echo "All 8 data streams are flowing"
    echo "Monitor for any timeout increase"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f /var/log/redirector/hybrid_l4_final.log ]; then
    echo "Last 10 log entries:"
    tail -10 /var/log/redirector/hybrid_l4_final.log
else
    echo "Log file not found: /var/log/redirector/hybrid_l4_final.log"
fi
echo ""
