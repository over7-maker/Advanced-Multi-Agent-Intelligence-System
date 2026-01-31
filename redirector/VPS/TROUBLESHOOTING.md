# L4 Redirector v4.0 - Troubleshooting Guide
**Common issues and solutions**

---

## Table of Contents
1. [Service Won't Start](#service-wont-start)
2. [Authentication Failures](#authentication-failures)
3. [Connection Issues](#connection-issues)
4. [Performance Problems](#performance-problems)
5. [Circuit Breaker Open](#circuit-breaker-open)
6. [Log Analysis](#log-analysis)
7. [Debug Commands](#debug-commands)

---

## Service Won't Start

### Symptom
```bash
sudo systemctl status l4-redirector-v4
# Shows: failed or inactive (dead)
```

### Diagnosis

**Check logs:**
```bash
sudo journalctl -u l4-redirector-v4 -n 50 --no-pager
```

**Check configuration:**
```bash
sudo cat /etc/l4-redirector/config.env
```

### Common Causes

#### 1. Missing Environment Variables

**Error message:**
```
FATAL: LOCALTONET_IP environment variable not set
```

**Solution:**
```bash
# Edit config
sudo nano /etc/l4-redirector/config.env

# Ensure all required variables are set:
# - BACKEND_API_TOKEN
# - API_AUTH_TOKEN
# - LOCALTONET_IP
# - PORT_MAP

# Restart service
sudo systemctl restart l4-redirector-v4
```

#### 2. Invalid PORT_MAP Format

**Error message:**
```
FATAL: Invalid PORT_MAP format: json.JSONDecodeError
```

**Solution:**
```bash
# Check PORT_MAP syntax
grep PORT_MAP /etc/l4-redirector/config.env

# Must be valid JSON with string keys:
PORT_MAP={"8041": ["192.168.1.100", 1429]}

# NOT like this (wrong):
# PORT_MAP={8041: ["192.168.1.100", 1429]}  # Keys must be strings
```

#### 3. Ports Already in Use

**Error message:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find what's using the port
sudo netstat -tulpn | grep 8041

# Kill the process or change port
sudo kill -9 <PID>

# Restart service
sudo systemctl restart l4-redirector-v4
```

#### 4. Not Running as Root

**Error message:**
```
SystemExit: Run as root
```

**Solution:**
- Service is configured to run as root in `l4-redirector-v4.service`
- Check service file: `User=root`
- If manually running: `sudo python3 /usr/local/bin/l4_redirector_v4.py`

---

## Authentication Failures

### Symptom
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:9090/health
# Returns: {"error":"unauthorized"}
```

### Diagnosis

**Check token:**
```bash
grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2
```

### Solutions

#### 1. Wrong Token

**Verify token length (should be 64 characters):**
```bash
grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2 | wc -c
# Should output: 65 (64 chars + newline)
```

**Regenerate token:**
```bash
# Generate new token
NEW_TOKEN=$(openssl rand -hex 32)
echo $NEW_TOKEN

# Update config
sudo sed -i "s/^API_AUTH_TOKEN=.*/API_AUTH_TOKEN=$NEW_TOKEN/" /etc/l4-redirector/config.env

# Restart service
sudo systemctl restart l4-redirector-v4
```

#### 2. Token with Spaces/Special Characters

**Check for extra spaces:**
```bash
cat -A /etc/l4-redirector/config.env | grep API_AUTH_TOKEN
# Should not show trailing spaces or special chars
```

**Fix:**
```bash
# Remove any trailing spaces
sudo sed -i 's/[[:space:]]*$//' /etc/l4-redirector/config.env
```

---

## Connection Issues

### Symptom
Clients can't connect to VPS ports (8041, 8047, 8057)

### Diagnosis

**Test locally:**
```bash
telnet localhost 8041
```

**Test remotely:**
```bash
telnet YOUR_VPS_IP 8041
```

### Solutions

#### 1. Firewall Blocking

**Check firewall status:**
```bash
sudo ufw status
```

**Open ports:**
```bash
sudo ufw allow 8041/tcp
sudo ufw allow 8047/tcp
sudo ufw allow 8057/tcp
```

#### 2. Backend Not Reachable

**Check backend connectivity:**
```bash
# Get LocalToNet IP from config
LOCALTONET_IP=$(grep LOCALTONET_IP /etc/l4-redirector/config.env | cut -d= -f2)

# Test connection
telnet $LOCALTONET_IP 6921
```

**Check circuit breaker state:**
```bash
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:9090/status | jq .circuit_breaker
```

#### 3. Target Backend Down

**Check logs for connection errors:**
```bash
sudo journalctl -u l4-redirector-v4 | grep "Handler error"
```

**Test backend directly:**
```bash
# Get target IP and port from PORT_MAP
telnet TARGET_IP TARGET_PORT
```

---

## Performance Problems

### Symptom
High latency or slow connections

### Diagnosis

**Check CPU usage:**
```bash
top -b -n 1 | grep l4_redirector
```

**Check memory:**
```bash
ps aux | grep l4_redirector | awk '{sum+=$6} END {print sum/1024 " MB"}'
```

**Check connections:**
```bash
sudo netstat -anp | grep 8041 | wc -l
```

### Solutions

#### 1. Too Many Connections

**Increase worker count (edit script):**
```python
# In l4_redirector_v4.py, change:
for i in range(cpu_count * 4):  # Increase multiplier
```

#### 2. System Limits Too Low

**Check limits:**
```bash
ulimit -n
```

**Increase limits (already set in service file):**
```bash
# Verify in service file
sudo systemctl cat l4-redirector-v4 | grep LimitNOFILE
# Should show: LimitNOFILE=1048576
```

#### 3. Backend Slow

**Check backend latency:**
```bash
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:9090/status | jq .global
```

---

## Circuit Breaker Open

### Symptom
```json
{"state": "open", "failure_count": 5}
```

### Cause
Backend API is unreachable or returning errors

### Solutions

#### 1. Check Backend API

**Test backend API directly:**
```bash
LOCALTONET_IP=$(grep LOCALTONET_IP /etc/l4-redirector/config.env | cut -d= -f2)
LOCALTONET_PORT=$(grep LOCALTONET_PORT /etc/l4-redirector/config.env | cut -d= -f2)
BACKEND_TOKEN=$(grep BACKEND_API_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)

curl -H "Authorization: Bearer $BACKEND_TOKEN" \
     http://$LOCALTONET_IP:$LOCALTONET_PORT/api/v1/health
```

#### 2. Wait for Auto-Recovery

Circuit breaker will automatically transition:
- **OPEN** → (60 seconds) → **HALF_OPEN** → (2 successes) → **CLOSED**

**Monitor recovery:**
```bash
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)
watch -n 5 "curl -s -H 'Authorization: Bearer $TOKEN' http://localhost:9090/status | jq .circuit_breaker"
```

#### 3. Manual Service Restart

**If backend is now healthy:**
```bash
sudo systemctl restart l4-redirector-v4
```

---

## Log Analysis

### View Recent Logs
```bash
sudo journalctl -u l4-redirector-v4 -n 100 --no-pager
```

### Follow Logs in Real-Time
```bash
sudo journalctl -u l4-redirector-v4 -f
```

### Search for Errors
```bash
sudo journalctl -u l4-redirector-v4 | grep -i error
```

### Filter by Time
```bash
# Last hour
sudo journalctl -u l4-redirector-v4 --since "1 hour ago"

# Specific date
sudo journalctl -u l4-redirector-v4 --since "2026-01-31 10:00"
```

### View Specific Log File
```bash
sudo tail -f /var/log/redirector/l4_redirector_v4.log
```

---

## Debug Commands

### Complete Health Check
```bash
#!/bin/bash
echo "=== L4 Redirector Debug Report ==="
echo ""

echo "1. Service Status:"
systemctl status l4-redirector-v4 | head -10
echo ""

echo "2. Process Count:"
ps aux | grep l4_redirector_v4 | wc -l
echo ""

echo "3. Listening Ports:"
sudo netstat -tulpn | grep -E "8041|8047|8057|9090"
echo ""

echo "4. Recent Errors:"
sudo journalctl -u l4-redirector-v4 --since "10 minutes ago" | grep -i error
echo ""

echo "5. Circuit Breaker:"
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:9090/status | jq .circuit_breaker
echo ""

echo "6. Configuration:"
cat /etc/l4-redirector/config.env | grep -v TOKEN
```

Save as `/usr/local/bin/debug-redirector.sh` and run:
```bash
chmod +x /usr/local/bin/debug-redirector.sh
/usr/local/bin/debug-redirector.sh
```

---

## Emergency Recovery

### Complete Service Reset
```bash
# Stop service
sudo systemctl stop l4-redirector-v4

# Kill any remaining processes
sudo pkill -9 -f l4_redirector_v4

# Check ports are freed
sudo netstat -tulpn | grep -E "8041|8047|8057|9090"

# Start service
sudo systemctl start l4-redirector-v4

# Verify
sudo systemctl status l4-redirector-v4
```

### Rollback to v3
If you backed up v3 before upgrading:
```bash
# Stop v4
sudo systemctl stop l4-redirector-v4
sudo systemctl disable l4-redirector-v4

# Restore v3 service
sudo systemctl start l4-redirector-v3
sudo systemctl enable l4-redirector-v3
```

---

## Getting Help

### Collect Debug Information
```bash
# Run debug script
/usr/local/bin/debug-redirector.sh > /tmp/redirector-debug.txt

# Collect logs
sudo journalctl -u l4-redirector-v4 --since "1 hour ago" > /tmp/redirector-logs.txt

# Create support bundle
tar -czf /tmp/redirector-support.tar.gz /tmp/redirector-debug.txt /tmp/redirector-logs.txt
```

### Report Issue
- **GitHub Issues:** https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues
- Include: Debug output, logs, configuration (without tokens)

---

**Updated:** 2026-01-31  
**Version:** 4.0.0-final  
**Support:** GitHub Issues
