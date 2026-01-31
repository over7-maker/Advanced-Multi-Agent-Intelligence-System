# L4 Redirector v4.0 - Complete Deployment Guide
**Comprehensive production deployment instructions**

---

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Post-Deployment](#post-deployment)

---

## System Requirements

### Minimum Requirements
- **OS:** Ubuntu 24.04 LTS
- **CPU:** 2 cores
- **RAM:** 2GB
- **Disk:** 10GB
- **Network:** Public IP, ports 8041, 8047, 8057, 9090

### Recommended
- **CPU:** 4+ cores
- **RAM:** 4GB+
- **Disk:** 20GB+ SSD
- **Network:** 1Gbps+

### Software Dependencies
- Python 3.12+
- python3-pip
- python3-aiohttp
- python3-psutil
- uvloop

---

## Pre-Deployment Checklist

- [ ] Ubuntu 24.04 LTS installed
- [ ] Root access available
- [ ] Firewall configured (ports open)
- [ ] Backend API running (Windows)
- [ ] LocalToNet/WireGuard gateway configured
- [ ] DNS/IP addresses confirmed
- [ ] Backup of existing v3 (if upgrading)

---

## Installation Steps

### Step 1: System Preparation

**Update system:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Install dependencies:**
```bash
sudo apt install -y \
    python3-pip \
    python3-aiohttp \
    python3-psutil \
    git \
    curl \
    jq
```

**Install uvloop:**
```bash
sudo pip3 install uvloop --break-system-packages
```

### Step 2: Clone Repository
```bash
cd /root
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System/redirector/VPS/
```

### Step 3: Generate Security Credentials

**Generate backend API token:**
```bash
BACKEND_TOKEN=$(openssl rand -hex 32)
echo "Backend API Token: $BACKEND_TOKEN"
```

**Generate monitoring API token:**
```bash
MONITORING_TOKEN=$(openssl rand -hex 32)
echo "Monitoring API Token: $MONITORING_TOKEN"
```

**Save to secure file:**
```bash
cat > /tmp/tokens.txt <<EOF
BACKEND_API_TOKEN=$BACKEND_TOKEN
API_AUTH_TOKEN=$MONITORING_TOKEN
EOF
chmod 600 /tmp/tokens.txt
```

**CRITICAL:** Save these tokens securely. You'll need them for:
- Backend API configuration (Windows)
- Monitoring API access
- Configuration file

### Step 4: Create Configuration

**Create secure config directory:**
```bash
sudo mkdir -p /etc/l4-redirector
sudo chmod 700 /etc/l4-redirector
```

**Copy template:**
```bash
sudo cp config.env.template /etc/l4-redirector/config.env
```

**Edit configuration:**
```bash
sudo nano /etc/l4-redirector/config.env
```

Update these values:

```bash
# Backend API Communication
BACKEND_API_TOKEN=<backend_token_from_step_3>
API_AUTH_TOKEN=<monitoring_token_from_step_3>

# LocalToNet/WireGuard Gateway
LOCALTONET_IP=111.111.11.111  # Your gateway IP
LOCALTONET_PORT=6921  # Your gateway port

# Port Mapping (JSON format)
PORT_MAP={"8041": ["222.222.22.222", 1429], "8047": ["222.222.22.222", 8667], "8057": ["222.222.22.222", 7798]}
```

**Secure the configuration:**
```bash
sudo chmod 600 /etc/l4-redirector/config.env
sudo chown root:root /etc/l4-redirector/config.env
```

### Step 5: Deploy Script

**Copy to system location:**
```bash
sudo cp l4_redirector_v4.py /usr/local/bin/
sudo chmod +x /usr/local/bin/l4_redirector_v4.py
sudo chown root:root /usr/local/bin/l4_redirector_v4.py
```

**Verify deployment:**
```bash
ls -lh /usr/local/bin/l4_redirector_v4.py
```

### Step 6: Install systemd Service

**Copy service file:**
```bash
sudo cp l4-redirector-v4.service /etc/systemd/system/
```

**Reload systemd:**
```bash
sudo systemctl daemon-reload
```

**Verify service file:**
```bash
sudo systemctl cat l4-redirector-v4
```

### Step 7: Start Service

**Start service:**
```bash
sudo systemctl start l4-redirector-v4
```

**Check status:**
```bash
sudo systemctl status l4-redirector-v4
```

**Enable auto-start:**
```bash
sudo systemctl enable l4-redirector-v4
```

---

## Configuration

### Port Mapping Format

JSON format with string keys and array values:
```json
{
  "listen_port": ["target_ip", target_port],
  "8041": ["192.168.1.100", 1429]
}
```

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|----------|
| `BACKEND_API_TOKEN` | Yes | Backend API auth token | 64 hex chars |
| `API_AUTH_TOKEN` | Yes | Monitoring API token | 64 hex chars |
| `LOCALTONET_IP` | Yes | Gateway IP address | 111.111.11.111 |
| `LOCALTONET_PORT` | No | Gateway port (default 6921) | 6921 |
| `PORT_MAP` | Yes | Port mappings (JSON) | See above |

---

## Verification

### Service Health
```bash
# Service status
sudo systemctl status l4-redirector-v4
# Expected: active (running)
```

### Process Count
```bash
# Count processes
ps aux | grep l4_redirector_v4 | wc -l
# Expected: 20-30 processes (varies by CPU count)
```

### Listening Ports
```bash
# Check ports
sudo netstat -tulpn | grep -E "8041|8047|8057|9090"
# Expected: All ports listening
```

### API Health Check
```bash
# Get token
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)

# Test health endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:9090/health
# Expected: {"status":"ok","version":"4.0.0-final",...}
```

### Circuit Breaker State
```bash
# Check circuit breaker
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:9090/status | jq .circuit_breaker
# Expected: {"state":"closed","failure_count":0,...}
```

### Logs
```bash
# View logs
sudo journalctl -u l4-redirector-v4 -f
# Expected: INFO level messages, no errors
```

---

## Post-Deployment

### Update Backend API
Update Windows backend API with `BACKEND_API_TOKEN` from Step 3.

### Configure Firewall
```bash
# Allow ports
sudo ufw allow 8041/tcp
sudo ufw allow 8047/tcp
sudo ufw allow 8057/tcp
sudo ufw allow 9090/tcp  # Monitoring (restrict to trusted IPs)
```

### Set Up Monitoring

**Create monitoring script:**
```bash
cat > /usr/local/bin/check-redirector.sh <<'EOF'
#!/bin/bash
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:9090/status | jq .
EOF
chmod +x /usr/local/bin/check-redirector.sh
```

**Run it:**
```bash
/usr/local/bin/check-redirector.sh
```

### Configure Log Rotation
Already configured via `RotatingFileHandler` (100MB per file, 10 backups).

### Test Connections
```bash
# Test from client
telnet YOUR_VPS_IP 8041
# Should connect to backend
```

---

## Troubleshooting

See `TROUBLESHOOTING.md` for complete guide.

---

**Deployment Time:** 15-30 minutes  
**Difficulty:** Intermediate  
**Support:** GitHub issues
