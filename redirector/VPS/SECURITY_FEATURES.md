# L4 Redirector v4.0 - Security Features
**Enterprise-grade security improvements**

---

## Overview

L4 Redirector v4.0 implements **9 critical security improvements** over previous versions:

1. ✅ **Environment-based Configuration**
2. ✅ **Fail-fast Validation**
3. ✅ **Timing Attack Protection**
4. ✅ **Circuit Breaker Pattern**
5. ✅ **Connection Pooling**
6. ✅ **Request Batching**
7. ✅ **Input Validation**
8. ✅ **systemd Hardening**
9. ✅ **Secure File Permissions**

---

## 1. Environment-based Configuration

### Problem (v3)
```python
# Hardcoded credentials in source code
BACKEND_API_TOKEN = "abc123"
API_AUTH_TOKEN = "xyz789"
```

### Solution (v4)
```python
# Load from environment
BACKEND_API_TOKEN = os.getenv("BACKEND_API_TOKEN")
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")
```

### Benefits
- ✅ No credentials in version control
- ✅ Different tokens per environment
- ✅ Secure config file (600 permissions)
- ✅ Easy token rotation

### Implementation
```bash
# Secure configuration file
/etc/l4-redirector/config.env

# Permissions
chmod 600 /etc/l4-redirector/config.env
chown root:root /etc/l4-redirector/config.env
```

---

## 2. Fail-fast Validation

### Problem (v3)
Service starts with invalid config, fails later with cryptic errors.

### Solution (v4)
```python
# Validate on startup
if not LOCALTONET_IP:
    sys.exit("FATAL: LOCALTONET_IP environment variable not set")

if not BACKEND_API_TOKEN:
    sys.exit("FATAL: BACKEND_API_TOKEN environment variable not set")

# Validate PORT_MAP format
try:
    PORT_MAP = json.loads(PORT_MAP_JSON)
    # Validate port ranges
    for port, (target_ip, target_port) in PORT_MAP.items():
        if port < 1 or port > 65535:
            raise ValueError(f"Invalid port: {port}")
except Exception as e:
    sys.exit(f"FATAL: Invalid PORT_MAP: {e}")
```

### Benefits
- ✅ Immediate error detection
- ✅ Clear error messages
- ✅ Prevents runtime failures
- ✅ Easier debugging

---

## 3. Timing Attack Protection

### Problem (v3)
```python
# Vulnerable to timing attacks
if auth_header != expected_token:
    return unauthorized
```

**Attack:** Attacker can measure response time to guess token character-by-character.

### Solution (v4)
```python
# Constant-time comparison
import secrets

if not secrets.compare_digest(auth_header, expected):
    # Add random delay to prevent timing analysis
    await asyncio.sleep(0.1 + secrets.randbelow(100) / 1000)
    return unauthorized
```

### Benefits
- ✅ Prevents timing attacks
- ✅ Constant-time comparison
- ✅ Random delay obfuscation
- ✅ Industry best practice

### Technical Details

**Standard comparison (vulnerable):**
```python
if token == "secret123":
    # Stops at first mismatch
    # "xecret123" takes ~1 comparison
    # "secret12x" takes ~8 comparisons
    # Attacker can measure timing difference!
```

**Constant-time comparison (secure):**
```python
secrets.compare_digest(token, "secret123")
# Always takes same time regardless of where mismatch occurs
# No information leaked via timing
```

---

## 4. Circuit Breaker Pattern

### Problem (v3)
When backend API is down:
- ❌ Every request attempts connection
- ❌ Wastes resources
- ❌ Increases latency
- ❌ No automatic recovery

### Solution (v4)

**Circuit States:**
```
┌─────────────┐
│   CLOSED    │ ←─ Normal operation
│  (working)  │
└─────┬───────┘
     │ 5 failures
     │
┌────┴───────┐
│   OPEN      │ ←─ Reject all requests
│  (failing)  │     (fast-fail)
└─────┬───────┘
     │ 60 seconds
     │
┌────┴─────────┐
│  HALF_OPEN   │ ←─ Test recovery
│   (testing)  │     (allow limited)
└───────────────┘
     │ 2 successes? → CLOSED
     │ 1 failure? → OPEN
```

**Implementation:**
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
    
    def can_proceed(self) -> bool:
        if self.state == CircuitState.OPEN:
            if time_since_failure > self.timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False  # Fast-fail
        return True
```

### Benefits
- ✅ Fast-fail when backend down
- ✅ Automatic recovery testing
- ✅ Reduces load on failing backend
- ✅ Improves overall stability
- ✅ Prevents cascade failures

---

## 5. Connection Pooling

### Problem (v3)
```python
# New connection for every API call
async with aiohttp.ClientSession() as session:
    await session.post(url, json=data)
# Connection closed immediately
```

**Issues:**
- ❌ TCP handshake overhead
- ❌ TLS handshake overhead
- ❌ Connection establishment delay
- ❌ Resource waste

### Solution (v4)
```python
# Global persistent connection pool
connector = TCPConnector(
    limit=100,              # Max 100 connections
    limit_per_host=50,      # Max 50 per backend
    ttl_dns_cache=300,      # Cache DNS for 5 min
    force_close=False       # Reuse connections
)

http_session = ClientSession(
    connector=connector,
    timeout=ClientTimeout(total=30)
)

# Reuse connection across requests
await http_session.post(url, json=data)
```

### Benefits
- ✅ Eliminates handshake overhead
- ✅ Reduces latency (50-200ms saved)
- ✅ Fewer socket resources
- ✅ Better throughput
- ✅ DNS caching

### Performance Impact

**Before (new connection each time):**
```
Request 1: 150ms (100ms handshake + 50ms request)
Request 2: 150ms (100ms handshake + 50ms request)
Request 3: 150ms (100ms handshake + 50ms request)
Total: 450ms
```

**After (connection pooling):**
```
Request 1: 150ms (100ms handshake + 50ms request)
Request 2: 50ms  (reuse connection)
Request 3: 50ms  (reuse connection)
Total: 250ms (44% faster)
```

---

## 6. Request Batching

### Problem (v3)
```python
# Every connection = immediate API call
for connection in connections:
    await api_push(connection_data)  # 1000 connections = 1000 API calls
```

**Issues:**
- ❌ High API overhead
- ❌ Network congestion
- ❌ Backend overload
- ❌ Increased latency

### Solution (v4)
```python
# Batch requests
BATCH_SIZE_THRESHOLD = 100
BATCH_TIME_THRESHOLD = 5  # seconds

async def push_buffered(data):
    buffer.append(data)
    
    # Flush when buffer full OR time elapsed
    if len(buffer) >= 100 or elapsed > 5:
        await api_push_batch(buffer)  # 1 API call for 100 connections
        buffer.clear()
```

### Benefits
- ✅ 99% reduction in API calls
- ✅ Lower network overhead
- ✅ Reduced backend load
- ✅ Better throughput
- ✅ Automatic batching

### Example

**Before:**
```
1000 connections in 10 seconds
= 1000 API calls
= High overhead
```

**After:**
```
1000 connections in 10 seconds
= 10 batched API calls (100 each)
= 99% reduction
```

---

## 7. Input Validation

### Problem (v3)
Minimal validation, crashes on invalid input.

### Solution (v4)
```python
# Strict port validation
for port, (target_ip, target_port) in PORT_MAP.items():
    if port < 1 or port > 65535:
        raise ValueError(f"Invalid port: {port}")
    if target_port < 1 or target_port > 65535:
        raise ValueError(f"Invalid target port: {target_port}")

# JSON format validation
try:
    PORT_MAP = json.loads(PORT_MAP_JSON)
except json.JSONDecodeError as e:
    sys.exit(f"Invalid JSON: {e}")

# Type validation
PORT_MAP = {int(k): (v[0], int(v[1])) for k, v in PORT_MAP.items()}
```

### Benefits
- ✅ Prevents invalid configurations
- ✅ Clear error messages
- ✅ Fail-fast behavior
- ✅ Type safety

---

## 8. systemd Hardening

### Service File Security
```ini
[Service]
# Security hardening
NoNewPrivileges=true    # Prevent privilege escalation
PrivateTmp=true         # Isolated /tmp directory
ProtectSystem=strict    # Read-only /usr, /boot, /efi
ProtectHome=true        # Inaccessible /home
ReadWritePaths=/var/log/redirector  # Only this path writable

# Resource limits
LimitNOFILE=1048576     # Max open files
LimitNPROC=65536        # Max processes

# Auto-restart
Restart=always
RestartSec=10
```

### Benefits
- ✅ Principle of least privilege
- ✅ Isolated filesystem
- ✅ Resource limits
- ✅ Automatic recovery
- ✅ Attack surface reduction

---

## 9. Secure File Permissions

### Configuration Security
```bash
# Secure config directory
sudo mkdir -p /etc/l4-redirector
sudo chmod 700 /etc/l4-redirector

# Secure config file
sudo chmod 600 /etc/l4-redirector/config.env
sudo chown root:root /etc/l4-redirector/config.env
```

**Permissions breakdown:**
- `700` - Only root can access directory
- `600` - Only root can read/write config
- No group access
- No other access

### Benefits
- ✅ Prevents unauthorized access
- ✅ Protects tokens
- ✅ Audit trail (root only)
- ✅ Compliance friendly

---

## Security Checklist

### Deployment
- [ ] Generated strong tokens (64 hex chars)
- [ ] Config file permissions set to 600
- [ ] Config directory permissions set to 700
- [ ] Owned by root:root
- [ ] No tokens in version control
- [ ] Firewall configured
- [ ] Monitoring API restricted to trusted IPs

### Operations
- [ ] Regular token rotation
- [ ] Monitor circuit breaker state
- [ ] Review logs for unauthorized access
- [ ] Keep system packages updated
- [ ] Monitor resource usage

### Audit
- [ ] Verify file permissions quarterly
- [ ] Review systemd security settings
- [ ] Check for security updates
- [ ] Audit access logs

---

## Threat Model

### Protected Against
- ✅ **Timing attacks** - Constant-time comparison
- ✅ **Brute force** - 64-char random tokens
- ✅ **Token leakage** - No hardcoded credentials
- ✅ **DoS via backend** - Circuit breaker
- ✅ **Resource exhaustion** - Connection limits
- ✅ **Unauthorized access** - File permissions
- ✅ **Privilege escalation** - systemd hardening

### Not Protected Against
- ❌ **DDoS** - Deploy behind CDN/DDoS protection
- ❌ **Zero-day exploits** - Keep system updated
- ❌ **Physical access** - Secure datacenter required

---

## Best Practices

### Token Management
1. **Generate strong tokens:**
   ```bash
   openssl rand -hex 32
   ```
2. **Rotate tokens quarterly**
3. **Use different tokens per environment**
4. **Never commit tokens to git**

### Monitoring
1. **Monitor circuit breaker state**
2. **Alert on high failure rates**
3. **Track unauthorized access attempts**
4. **Review logs weekly**

### Updates
1. **Keep system packages updated**
2. **Monitor security advisories**
3. **Test updates in staging first**
4. **Maintain rollback capability**

---

## Compliance

Security features support compliance with:
- **GDPR** - Data protection, access control
- **SOC 2** - Security, availability, confidentiality
- **ISO 27001** - Information security management
- **PCI DSS** - Network security, access control

---

**Updated:** 2026-01-31  
**Version:** 4.0.0-final  
**Classification:** Production Security Review
