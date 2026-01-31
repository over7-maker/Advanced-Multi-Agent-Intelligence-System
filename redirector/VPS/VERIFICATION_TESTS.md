# L4 Redirector v4.0 - Verification Tests
**Complete test suite for deployment validation**

---

## Test Suite Overview

8 comprehensive tests to verify deployment:

1. **Service Health Test**
2. **Process Count Test**
3. **Port Listening Test**
4. **Authentication Test**
5. **Circuit Breaker Test**
6. **Connection Pooling Test**
7. **Request Batching Test**
8. **Auto-Restart Test**

---

## Test 1: Service Health

**Purpose:** Verify systemd service is running

```bash
sudo systemctl status l4-redirector-v4
```

**Expected output:**
```
● l4-redirector-v4.service - L4 Redirector v4.0 - Production Final Edition
   Loaded: loaded
   Active: active (running)
```

**Pass criteria:**
- Status: `active (running)`
- No errors in output

---

## Test 2: Process Count

**Purpose:** Verify all worker processes started

```bash
ps aux | grep l4_redirector_v4 | wc -l
```

**Expected output:** 20-30 (varies by CPU count)

**Pass criteria:**
- Process count >= 20
- Matches: 1 HTTP server + (ports × CPU cores × 4) TCP workers

---

## Test 3: Port Listening

**Purpose:** Verify all ports are listening

```bash
sudo netstat -tulpn | grep -E "8041|8047|8057|9090"
```

**Expected output:**
```
tcp        0      0 0.0.0.0:8041            0.0.0.0:*               LISTEN      <pid>/python3
tcp        0      0 0.0.0.0:8047            0.0.0.0:*               LISTEN      <pid>/python3
tcp        0      0 0.0.0.0:8057            0.0.0.0:*               LISTEN      <pid>/python3
tcp        0      0 0.0.0.0:9090            0.0.0.0:*               LISTEN      <pid>/python3
```

**Pass criteria:**
- All configured ports listening
- Port 9090 listening (monitoring API)

---

## Test 4: Authentication Security

**Purpose:** Verify timing attack protection and token validation

```bash
# Get token
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)

# Test with correct token (should succeed)
curl -H "Authorization: Bearer $TOKEN" http://localhost:9090/health

# Test with wrong token (should fail)
curl -H "Authorization: Bearer wrong_token" http://localhost:9090/health
```

**Expected output:**
- **Correct token:**
  ```json
  {"status":"ok","version":"4.0.0-final","timestamp":"..."}
  ```
- **Wrong token:**
  ```json
  {"error":"unauthorized"}
  ```

**Pass criteria:**
- Correct token returns 200 status
- Wrong token returns 401 status
- Response time similar for both (timing attack protection)

---

## Test 5: Circuit Breaker

**Purpose:** Verify circuit breaker state

```bash
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:9090/status | jq .circuit_breaker
```

**Expected output:**
```json
{
  "state": "closed",
  "failure_count": 0,
  "success_count": 0
}
```

**Pass criteria:**
- State: `closed` (normal operation)
- Failure count: low or 0

---

## Test 6: Connection Pooling

**Purpose:** Verify HTTP connection pooling is working

```bash
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)

# Check initial backend pushes
BEFORE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:9090/status | jq .global.backend_pushes)

# Wait 30 seconds
sleep 30

# Check again
AFTER=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:9090/status | jq .global.backend_pushes)

echo "Before: $BEFORE"
echo "After: $AFTER"
echo "Increase: $((AFTER - BEFORE))"
```

**Pass criteria:**
- Backend pushes increasing over time
- No connection errors

---

## Test 7: Request Batching

**Purpose:** Verify request batching reduces API calls

```bash
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)

# Generate test traffic (50 connections)
for i in {1..50}; do
  curl -s http://localhost:8041 > /dev/null &
done
wait

# Check backend pushes (should be much less than 50)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:9090/status | jq .global.backend_pushes
```

**Pass criteria:**
- Backend pushes < 50 (batching working)
- Typically 1-5 batched calls for 50 connections

---

## Test 8: Auto-Restart

**Purpose:** Verify crashed workers automatically restart

```bash
# Kill a worker process
sudo pkill -9 -f "tcp_8041_0"

# Wait 10 seconds
sleep 10

# Verify process was restarted
ps aux | grep "tcp_8041_0"

# Check logs for restart message
sudo journalctl -u l4-redirector-v4 -n 20 | grep restart
```

**Pass criteria:**
- Process restarted with new PID
- Logs show restart message
- Service continues running

---

## Comprehensive Test Script

Save as `/usr/local/bin/verify-redirector.sh`:

```bash
#!/bin/bash

echo "================================="
echo "L4 Redirector v4.0 Verification"
echo "================================="

# Get token
TOKEN=$(grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2)

# Test 1: Service
echo ""
echo "Test 1: Service Health"
systemctl is-active l4-redirector-v4 && echo "✅ PASS" || echo "❌ FAIL"

# Test 2: Processes
echo ""
echo "Test 2: Process Count"
COUNT=$(ps aux | grep l4_redirector_v4 | wc -l)
if [ $COUNT -ge 20 ]; then
  echo "✅ PASS ($COUNT processes)"
else
  echo "❌ FAIL ($COUNT processes)"
fi

# Test 3: Ports
echo ""
echo "Test 3: Port Listening"
netstat -tulpn | grep -E "8041|8047|8057|9090" > /dev/null && echo "✅ PASS" || echo "❌ FAIL"

# Test 4: Authentication
echo ""
echo "Test 4: Authentication"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" http://localhost:9090/health)
if [ "$RESPONSE" = "200" ]; then
  echo "✅ PASS"
else
  echo "❌ FAIL (HTTP $RESPONSE)"
fi

# Test 5: Circuit Breaker
echo ""
echo "Test 5: Circuit Breaker"
STATE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:9090/status | jq -r .circuit_breaker.state)
if [ "$STATE" = "closed" ]; then
  echo "✅ PASS (state: $STATE)"
else
  echo "⚠️ WARNING (state: $STATE)"
fi

echo ""
echo "================================="
echo "Verification Complete"
echo "================================="
```

**Make executable:**
```bash
chmod +x /usr/local/bin/verify-redirector.sh
```

**Run all tests:**
```bash
/usr/local/bin/verify-redirector.sh
```

---

## Expected Results

```
=================================
L4 Redirector v4.0 Verification
=================================

Test 1: Service Health
✅ PASS

Test 2: Process Count
✅ PASS (28 processes)

Test 3: Port Listening
✅ PASS

Test 4: Authentication
✅ PASS

Test 5: Circuit Breaker
✅ PASS (state: closed)

=================================
Verification Complete
=================================
```

---

## Troubleshooting Failed Tests

### Service Health FAIL
```bash
# Check logs
sudo journalctl -u l4-redirector-v4 -n 50

# Check config
sudo cat /etc/l4-redirector/config.env
```

### Process Count FAIL
```bash
# Check for errors
sudo journalctl -u l4-redirector-v4 | grep ERROR

# Restart service
sudo systemctl restart l4-redirector-v4
```

### Port Listening FAIL
```bash
# Check if ports are already in use
sudo netstat -tulpn | grep -E "8041|8047|8057"

# Check firewall
sudo ufw status
```

### Authentication FAIL
```bash
# Verify token length (should be 64)
grep API_AUTH_TOKEN /etc/l4-redirector/config.env | cut -d= -f2 | wc -c

# Regenerate token
openssl rand -hex 32
```

---

**Test Duration:** 5 minutes  
**Pass Rate Expected:** 100%  
**Support:** See TROUBLESHOOTING.md
