# L4 Redirector v4.0 - Quick Start Guide
**Deploy in 5 minutes**

---

## Prerequisites
- Ubuntu 24.04 LTS VPS
- Root access
- Python 3.12+
- 2GB+ RAM

---

## Installation Steps

### Step 1: Clone Repository
```bash
cd /root
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System/redirector/VPS/
```

### Step 2: Generate Security Tokens
```bash
echo "Backend API Token:"
openssl rand -hex 32
echo ""
echo "Monitoring API Token:"
openssl rand -hex 32
```

**SAVE THESE TOKENS** - you'll need them in the next step.

### Step 3: Configure

**Create config directory:**
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

**Replace these values:**
- `BACKEND_API_TOKEN` - First token from Step 2
- `API_AUTH_TOKEN` - Second token from Step 2
- `LOCALTONET_IP` - Your LocalToNet/WireGuard gateway IP
- `PORT_MAP` - Your port mappings in JSON format

**Secure the config:**
```bash
sudo chmod 600 /etc/l4-redirector/config.env
sudo chown root:root /etc/l4-redirector/config.env
```

### Step 4: Deploy Script
```bash
sudo cp l4_redirector_v4.py /usr/local/bin/
sudo chmod +x /usr/local/bin/l4_redirector_v4.py
sudo chown root:root /usr/local/bin/l4_redirector_v4.py
```

### Step 5: Install Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip python3-aiohttp python3-psutil
sudo pip3 install uvloop --break-system-packages
```

### Step 6: Install Service
```bash
sudo cp l4-redirector-v4.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### Step 7: Start Service
```bash
sudo systemctl start l4-redirector-v4
sudo systemctl enable l4-redirector-v4
```

### Step 8: Verify

**Check service status:**
```bash
sudo systemctl status l4-redirector-v4
```

**View logs:**
```bash
sudo journalctl -u l4-redirector-v4 -f
```

**Check processes (should be ~20-30):**
```bash
ps aux | grep l4_redirector_v4 | wc -l
```

**Test API (replace TOKEN with your API_AUTH_TOKEN):**
```bash
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)
curl -H "Authorization: Bearer $TOKEN" http://localhost:9090/health
```

---

## Expected Results

✅ **Service status:** `active (running)`
✅ **Process count:** 20-30 processes
✅ **Health check:** `{"status":"ok","version":"4.0.0-final"}`
✅ **Logs:** No errors, only INFO level messages

---

## Next Steps

1. **Test connections** - Connect to your VPS on configured ports
2. **Monitor metrics** - Check `/status` endpoint for statistics
3. **Read full guide** - See `DEPLOYMENT_GUIDE.md` for details
4. **Review security** - See `SECURITY_FEATURES.md`

---

## Troubleshooting

**Service won't start:**
```bash
# Check logs
sudo journalctl -u l4-redirector-v4 -n 50

# Validate config
sudo cat /etc/l4-redirector/config.env
```

**Authentication failing:**
```bash
# Check token length (should be 64 characters)
grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2 | wc -c
```

See `TROUBLESHOOTING.md` for complete guide.

---

**Deployment time:** 5 minutes  
**Difficulty:** Easy  
**Support:** See repository issues
