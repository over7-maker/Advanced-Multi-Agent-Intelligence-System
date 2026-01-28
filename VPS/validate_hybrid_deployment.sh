#!/bin/bash
################################################################################
# VALIDATE HYBRID L4 REDIRECTOR DEPLOYMENT
# Run this after deployment to verify everything works
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNING=0

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║    HYBRID REDIRECTOR DEPLOYMENT VALIDATOR                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

echo -e "${YELLOW}Running 10 validation checks...${NC}"
echo ""

# CHECK 1: Service running
echo -n "[1/10] Service running... "
if sudo systemctl is-active --quiet redirector-v3.service; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
    echo "      Fix: sudo systemctl start redirector-v3.service"
fi

# CHECK 2: Processes running
echo -n "[2/10] Processes spawned... "
process_count=$(ps aux 2>/dev/null | grep -c "l4_redirector_v3_hybrid" || echo "0")
if [[ $process_count -gt 5 ]]; then
    echo -e "${GREEN}✓ ($process_count processes)${NC}"
    ((PASSED++))
elif [[ $process_count -gt 0 ]]; then
    echo -e "${YELLOW}⚠ WARNING ($process_count processes, expected 10+)${NC}"
    ((WARNING++))
else
    echo -e "${RED}✗ FAILED (no processes found)${NC}"
    ((FAILED++))
fi

# CHECK 3: Port 8041 listening
echo -n "[3/10] Port 8041 listening... "
if sudo ss -tlnp 2>/dev/null | grep -q ':8041'; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# CHECK 4: Port 8047 listening
echo -n "[4/10] Port 8047 listening... "
if sudo ss -tlnp 2>/dev/null | grep -q ':8047'; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# CHECK 5: Port 8057 listening
echo -n "[5/10] Port 8057 listening... "
if sudo ss -tlnp 2>/dev/null | grep -q ':8057'; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# CHECK 6: Status endpoint
echo -n "[6/10] Status endpoint (9090)... "
status_response=$(curl -s http://localhost:9090/status 2>&1 | head -1 || echo "error")
if [[ $status_response == "{" ]]; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# CHECK 7: Health endpoint
echo -n "[7/10] Health endpoint (9090)... "
health_response=$(curl -s http://localhost:9090/health 2>&1 | grep -o '"status":"ok"' || echo "")
if [[ ! -z $health_response ]]; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# CHECK 8: No callback errors in logs
echo -n "[8/10] No callback errors... "
error_count=$(tail -50 /var/log/redirector/l4_redirector_v3_hybrid.log 2>/dev/null | grep -c "callback" || echo "0")
if [[ $error_count -eq 0 ]]; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED ($error_count errors found)${NC}"
    ((FAILED++))
fi

# CHECK 9: Recent logs show connections
echo -n "[9/10] NEW/CLOSED messages in logs... "
connection_count=$(tail -100 /var/log/redirector/l4_redirector_v3_hybrid.log 2>/dev/null | grep -c "NEW\|CLOSED" || echo "0")
if [[ $connection_count -gt 0 ]]; then
    echo -e "${GREEN}✓ ($connection_count messages)${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ No connections yet (expected after traffic)${NC}"
    ((WARNING++))
fi

# CHECK 10: Tunnel accessible
echo -n "[10/10] LocalToNet tunnel reachable... "
tunnel_response=$(curl -s -w "%{http_code}" -o /dev/null http://194.182.64.133:6921/health 2>&1)
if [[ $tunnel_response == "200" || $tunnel_response == "401" ]]; then
    echo -e "${GREEN}✓ (HTTP $tunnel_response)${NC}"
    ((PASSED++))
elif [[ $tunnel_response == "000" ]]; then
    echo -e "${YELLOW}⚠ Timeout (tunnel may be offline)${NC}"
    ((WARNING++))
else
    echo -e "${RED}✗ FAILED (HTTP $tunnel_response)${NC}"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                         VALIDATION RESULTS                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}Passed:  $PASSED${NC}"
echo -e "${YELLOW}Warning: $WARNING${NC}"
echo -e "${RED}Failed:  $FAILED${NC}"
echo ""

if [[ $FAILED -eq 0 && $WARNING -eq 0 ]]; then
    echo -e "${GREEN}✅ PERFECT! All checks passed. Deployment successful!✅${NC}"
    exit 0
elif [[ $FAILED -eq 0 ]]; then
    echo -e "${YELLOW}⚠ GOOD! Most checks passed. Some warnings to monitor.${NC}"
    exit 0
else
    echo -e "${RED}✗ ISSUES DETECTED. Review failures above and fix before proceeding.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Service not running? Try: sudo systemctl restart redirector-v3.service"
    echo "  - Ports not listening? Check systemd logs: sudo journalctl -u redirector-v3.service -n 50"
    echo "  - Callback errors? Reinstall from main branch"
    echo ""
    exit 1
fi
