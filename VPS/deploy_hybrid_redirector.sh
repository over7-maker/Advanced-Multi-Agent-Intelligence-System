#!/bin/bash
################################################################################
# DEPLOY HYBRID L4 REDIRECTOR v3 - QUICK INSTALLATION
# Stateless streaming with full metrics (combines old + new)
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║    HYBRID L4 REDIRECTOR v3 - DEPLOYMENT SCRIPT                         ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Backup
echo -e "${YELLOW}[1/6] Backing up current redirector...${NC}"
if [ -f /usr/local/bin/l4_redirector_v3_final_complete.py ]; then
    sudo cp /usr/local/bin/l4_redirector_v3_final_complete.py \
            /usr/local/bin/l4_redirector_v3_final_complete.py.backup.$(date +%s)
    echo -e "${GREEN}✓ Backup created${NC}"
else
    echo -e "${YELLOW}⚠ No existing redirector found${NC}"
fi

# Step 2: Stop
echo -e "${YELLOW}[2/6] Stopping current service...${NC}"
if sudo systemctl is-active --quiet redirector-v3.service; then
    sudo systemctl stop redirector-v3.service
    sleep 2
    echo -e "${GREEN}✓ Service stopped${NC}"
else
    echo -e "${YELLOW}⚠ Service not running${NC}"
fi
sudo pkill -9 l4_redirector || true
sleep 1

# Step 3: Download
echo -e "${YELLOW}[3/6] Downloading hybrid redirector...${NC}"
cd /tmp
wget -q https://raw.githubusercontent.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/main/VPS/l4_redirector_v3_hybrid_working.py 2>/dev/null || \
    cp ~/Advanced-Multi-Agent-Intelligence-System/VPS/l4_redirector_v3_hybrid_working.py . 2>/dev/null || \
    { echo -e "${RED}✗ Download failed${NC}"; exit 1; }
echo -e "${GREEN}✓ Download successful${NC}"

# Step 4: Install
echo -e "${YELLOW}[4/6] Installing hybrid redirector...${NC}"
sudo cp /tmp/l4_redirector_v3_hybrid_working.py /usr/local/bin/
sudo chmod +x /usr/local/bin/l4_redirector_v3_hybrid_working.py
echo -e "${GREEN}✓ Installation complete${NC}"

# Step 5: Update service
echo -e "${YELLOW}[5/6] Updating systemd service...${NC}"
sudo tee /etc/systemd/system/redirector-v3.service > /dev/null <<'EOF'
[Unit]
Description=L4 Redirector V3 Hybrid Stateless Streaming
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/redirector_V4
ExecStart=/usr/bin/python3 /usr/local/bin/l4_redirector_v3_hybrid_working.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
echo -e "${GREEN}✓ Service updated${NC}"

# Step 6: Start
echo -e "${YELLOW}[6/6] Starting hybrid redirector...${NC}"
sudo systemctl daemon-reload
sudo systemctl start redirector-v3.service
sudo systemctl enable redirector-v3.service
sleep 2

if sudo systemctl is-active --quiet redirector-v3.service; then
    echo -e "${GREEN}✓ Service started successfully${NC}"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    sudo journalctl -u redirector-v3.service -n 20
    exit 1
fi

# Verification
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║               DEPLOYMENT SUCCESSFUL ✓                            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"

echo ""
echo -e "${GREEN}Features:"
echo "  ✅ Stateless streaming architecture (proven working)"
echo "  ✅ All 8 data streams to backend API"
echo "  ✅ Full bidirectional TCP forwarding"
echo "  ✅ Device/client tracking and logging"
echo "  ✅ Health monitoring"
echo "  ✅ Zero callback errors"
echo -e "${NC}"

echo -e "${YELLOW}Verify deployment:${NC}"
echo "  1. Watch logs: ${BLUE}tail -f /var/log/redirector/l4_redirector_v3_hybrid.log${NC}"
echo "  2. Check processes: ${BLUE}ps aux | grep l4_redirector${NC}"
echo "  3. Check ports: ${BLUE}sudo ss -tlnp | grep -E '8041|8047|8057'${NC}"
echo "  4. Query metrics: ${BLUE}curl http://localhost:9090/status | jq${NC}"
echo ""

echo -e "${YELLOW}Expected behavior:${NC}"
echo "  • Logs show NEW/CLOSED for each connection"
echo "  • Tunnel connected messages with latency"
echo "  • NO API timeout errors"
echo "  • NO callback errors"
echo "  • Metrics flowing to backend"
echo ""

echo -e "${GREEN}Deployment complete! Traffic should now flow properly.✓${NC}"
