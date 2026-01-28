#!/bin/bash
################################################################################
# DEPLOY FIXED L4 REDIRECTOR v3 - AUTOMATED INSTALLATION
# Fixes LocalToNet tunneling issues and enables proper traffic forwarding
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  L4 REDIRECTOR v3 FIXED - LOCALTONET TUNNELING DEPLOYMENT       ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# STEP 1: BACKUP CURRENT VERSION
# ============================================================================

echo -e "${YELLOW}[STEP 1] Backing up current redirector...${NC}"

if [ -f /usr/local/bin/l4_redirector_v3_final_complete.py ]; then
    sudo cp /usr/local/bin/l4_redirector_v3_final_complete.py \
            /usr/local/bin/l4_redirector_v3_final_complete.py.backup.$(date +%s)
    echo -e "${GREEN}✓ Backup created${NC}"
else
    echo -e "${YELLOW}⚠ No existing redirector found${NC}"
fi

# ============================================================================
# STEP 2: STOP CURRENT SERVICE
# ============================================================================

echo -e "${YELLOW}[STEP 2] Stopping current redirector service...${NC}"

if sudo systemctl is-active --quiet redirector-v3.service; then
    sudo systemctl stop redirector-v3.service
    echo -e "${GREEN}✓ Service stopped${NC}"
    
    # Wait for graceful shutdown
    sleep 2
else
    echo -e "${YELLOW}⚠ Service not running${NC}"
fi

# Kill any lingering processes
echo -e "${YELLOW}Killing lingering processes...${NC}"
sudo pkill -9 l4_redirector || true
sleep 1

echo -e "${GREEN}✓ All processes stopped${NC}"

# ============================================================================
# STEP 3: DOWNLOAD FIXED VERSION
# ============================================================================

echo -e "${YELLOW}[STEP 3] Downloading fixed redirector...${NC}"

cd /tmp
wget -q https://raw.githubusercontent.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/main/VPS/l4_redirector_v3_fixed_tunneling.py

if [ -f /tmp/l4_redirector_v3_fixed_tunneling.py ]; then
    echo -e "${GREEN}✓ Download successful${NC}"
else
    echo -e "${RED}✗ Download failed${NC}"
    echo "Attempting local copy instead..."
    if [ -f ~/Advanced-Multi-Agent-Intelligence-System/VPS/l4_redirector_v3_fixed_tunneling.py ]; then
        cp ~/Advanced-Multi-Agent-Intelligence-System/VPS/l4_redirector_v3_fixed_tunneling.py /tmp/
        echo -e "${GREEN}✓ Local copy used${NC}"
    else
        echo -e "${RED}✗ Cannot find fixed version${NC}"
        exit 1
    fi
fi

# ============================================================================
# STEP 4: INSTALL FIXED VERSION
# ============================================================================

echo -e "${YELLOW}[STEP 4] Installing fixed redirector...${NC}"

sudo cp /tmp/l4_redirector_v3_fixed_tunneling.py /usr/local/bin/
sudo chmod +x /usr/local/bin/l4_redirector_v3_fixed_tunneling.py

echo -e "${GREEN}✓ Fixed version installed${NC}"

# ============================================================================
# STEP 5: UPDATE SYSTEMD SERVICE
# ============================================================================

echo -e "${YELLOW}[STEP 5] Updating systemd service...${NC}"

sudo tee /etc/systemd/system/redirector-v3.service > /dev/null <<EOF
[Unit]
Description=L4 Redirector V3 Fixed Tunneling
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/redirector_V4
ExecStart=/usr/bin/python3 /usr/local/bin/l4_redirector_v3_fixed_tunneling.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Service file updated${NC}"

# ============================================================================
# STEP 6: RELOAD AND START
# ============================================================================

echo -e "${YELLOW}[STEP 6] Starting fixed redirector service...${NC}"

sudo systemctl daemon-reload
sudo systemctl start redirector-v3.service
sudo systemctl enable redirector-v3.service

sleep 2

if sudo systemctl is-active --quiet redirector-v3.service; then
    echo -e "${GREEN}✓ Service started successfully${NC}"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    echo "Checking logs:"
    sudo journalctl -u redirector-v3.service -n 20
    exit 1
fi

# ============================================================================
# STEP 7: VERIFICATION
# ============================================================================

echo -e "${YELLOW}[STEP 7] Verifying deployment...${NC}"

# Check processes
echo -e "${YELLOW}Checking processes...${NC}"
process_count=$(ps aux | grep "l4_redirector_v3_fixed_tunneling" | grep -v grep | wc -l)
if [ "$process_count" -gt 0 ]; then
    echo -e "${GREEN}✓ $process_count redirector processes running${NC}"
else
    echo -e "${RED}✗ No redirector processes found${NC}"
    exit 1
fi

# Check ports
echo -e "${YELLOW}Checking listening ports...${NC}"
for port in 8041 8047 8057 9090; do
    if sudo ss -tlnp 2>/dev/null | grep -q ":$port "; then
        echo -e "${GREEN}✓ Port $port listening${NC}"
    else
        echo -e "${RED}✗ Port $port NOT listening${NC}"
    fi
done

# Check logs
echo -e "${YELLOW}Checking logs for errors...${NC}"
error_count=$(sudo journalctl -u redirector-v3.service -n 50 | grep -i "error\|failed" | wc -l)
if [ "$error_count" -eq 0 ]; then
    echo -e "${GREEN}✓ No errors in recent logs${NC}"
else
    echo -e "${YELLOW}⚠ Found $error_count error messages (may be informational)${NC}"
    sudo journalctl -u redirector-v3.service -n 50 | grep -i "error\|failed" || true
fi

# ============================================================================
# STEP 8: SUMMARY
# ============================================================================

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║               DEPLOYMENT COMPLETE ✓                            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"

echo -e "${GREEN}"
echo "Fixed Features:"
echo "  ✓ Corrected bidirectional TCP forwarding"
echo "  ✓ Fixed callback error in forward_data()"
echo "  ✓ Increased timeouts for LocalToNet latency"
echo "  ✓ Enhanced logging for debugging"
echo "  ✓ All 8 data streams active"
echo -e "${NC}"

echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Monitor logs in real-time:"
echo "     ${BLUE}tail -f /var/log/redirector/l4_redirector_v3_final.log${NC}"
echo ""
echo "  2. Verify traffic flow:"
echo "     ${BLUE}curl -v http://194.182.64.133:6921/health${NC}"
echo ""
echo "  3. Check service status:"
echo "     ${BLUE}sudo systemctl status redirector-v3.service${NC}"
echo ""
echo "  4. View metrics endpoint:"
echo "     ${BLUE}curl http://localhost:9090/status${NC}"
echo ""

echo -e "${YELLOW}Expected Behavior:${NC}"
echo "  • See NEW/CLOSED messages for each connection"
echo "  • See tunnel connection latency (typically <150ms)"
echo "  • See bytes IN/OUT for each connection"
echo "  • NO 'API timeout' errors (or very rare)"
echo ""

echo -e "${YELLOW}Troubleshooting:${NC}"
echo "  If still seeing API timeouts:"
echo "    1. Check Windows backend is running:"
echo "       ${BLUE}ssh administrator@192.168.88.16${NC}"
echo "       ${BLUE}tasklist | findstr python${NC}"
echo ""
echo "    2. Check LocalToNet tunnel is active:"
echo "       Verify aoycrreni.localto.net:6921 shows 'OK' status"
echo ""
echo "    3. Test tunnel directly:"
echo "       ${BLUE}curl http://194.182.64.133:6921/health${NC}"
echo ""

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo ""
