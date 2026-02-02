# TLS/HTTPS Setup Guide - Windows Backend API v4.0.3

**Complete Implementation Guide for Enabling HTTPS with Self-Signed Certificates**

---

## 🎯 Overview

This guide walks you through enabling HTTPS/TLS encryption on the Windows Backend API, including:
- Self-signed certificate generation
- Backend configuration for HTTPS
- VPS L4 Redirector configuration
- Testing and verification
- Troubleshooting common issues

**Version:** 4.0.3-https-enabled  
**Release Date:** February 02, 2026  
**Compatibility:** Windows Server 2019/2022, Windows 10/11 with Python 3.12+

---

## 🔑 Why HTTPS?

### Security Benefits
- **Encryption:** All data in transit is encrypted using TLS 1.2/1.3
- **Authentication:** Verifies server identity to prevent MITM attacks
- **Integrity:** Ensures data isn't tampered with during transmission
- **Compliance:** Meets security standards and best practices

### Production Requirements
⚠️ **HTTPS is REQUIRED for production deployments**
- Protects API tokens and connection metadata
- Prevents eavesdropping on database credentials
- Secures communication between VPS and Windows machine

---

## 📊 Implementation Overview

```
┌───────────────────────────────────────────────┐
│           VPS L4 Redirector (Ubuntu)              │
│   Public Internet → Frontend Port 8041           │
│                                                   │
│   Configured with:                               │
│   - BACKEND_USE_HTTPS=true                       │
│   - BACKEND_VERIFY_SSL=false (self-signed)       │
└────────────────────────┬───────────────────────┘
                         │ HTTPS (TLS 1.2/1.3)
                         │ Port 6922
                         │ Encrypted
                         │
┌────────────────────────┴───────────────────────┐
│      Windows Backend API (v4.0.3-https)          │
│                                                   │
│   Listening on: https://0.0.0.0:6922             │
│   Certificate: C:\backend_api\certs\*.pem        │
│   TLS: 1.2/1.3                                   │
│   HSTS: Enabled                                  │
└───────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- [x] Windows Server 2019/2022 or Windows 10/11
- [x] Python 3.12+ installed
- [x] PowerShell 5.1+ (Administrator access)
- [x] Existing Backend API v4.0.2 installation
- [x] OpenSSL (optional, for advanced certificate operations)

### 5-Minute Setup

```powershell
# 1. Generate self-signed certificate
cd C:\backend_api
.\generate_ssl_cert.ps1 -CertName "YOUR_WINDOWS_IP"

# 2. Extract private key from PFX
# (Requires OpenSSL)
openssl pkcs12 -in C:\backend_api\certs\backend_api.pfx `
               -nocerts -out C:\backend_api\certs\backend_api_key.pem -nodes
# Password is in: C:\backend_api\certs\pfx_password.txt

# 3. Update config.env
cp config.env.https config.env
# Edit config.env with your settings

# 4. Restart backend service
Restart-Service BackendAPIv4

# 5. Test HTTPS
curl -k https://localhost:6922/health
```

---

## 📖 Detailed Implementation

### Step 1: Generate SSL Certificate

#### Method 1: Using PowerShell Script (Recommended)

```powershell
# Basic usage (creates cert for localhost/127.0.0.1)
.\generate_ssl_cert.ps1

# For specific IP address
.\generate_ssl_cert.ps1 -CertName "192.168.1.100"

# With custom validity (2 years)
.\generate_ssl_cert.ps1 -CertName "192.168.1.100" -ValidDays 730

# With multiple SANs
.\generate_ssl_cert.ps1 `
    -CertName "backend-api.local" `
    -SANs "192.168.1.100,10.0.0.50,backend.example.com"
```

**What this does:**
- Creates RSA 4096-bit key pair
- Generates self-signed certificate with SHA-256
- Adds Subject Alternative Names (SANs)
- Installs to Windows Certificate Store
- Exports to PFX format
- Exports certificate to PEM format
- Sets secure file permissions

**Output files:**
```
C:\backend_api\certs\
├── backend_api.pfx            # PKCS#12 bundle (cert + key)
├── backend_api_cert.pem       # Certificate (PEM format)
├── pfx_password.txt           # PFX password
└── certificate_summary.txt    # Generation summary
```

#### Method 2: Using OpenSSL Directly

```bash
# Generate private key
openssl genrsa -out backend_api_key.pem 4096

# Create certificate signing request
openssl req -new -key backend_api_key.pem -out backend_api.csr `
  -subj "/CN=192.168.1.100/O=Backend API/OU=Development"

# Self-sign the certificate (365 days)
openssl x509 -req -days 365 -in backend_api.csr `
  -signkey backend_api_key.pem -out backend_api_cert.pem `
  -extfile <(echo "subjectAltName=IP:192.168.1.100")
```

---

### Step 2: Extract Private Key from PFX

⚠️ **Required:** The Python backend needs the private key in PEM format.

#### Using OpenSSL

```powershell
# Read the PFX password
$pfxPassword = Get-Content "C:\backend_api\certs\pfx_password.txt" | ConvertFrom-SecureString | ConvertTo-SecureString

# Extract private key (no password protection)
openssl pkcs12 `
  -in "C:\backend_api\certs\backend_api.pfx" `
  -nocerts `
  -out "C:\backend_api\certs\backend_api_key.pem" `
  -nodes
# Enter the PFX password when prompted
```

**Verify extraction:**
```powershell
# Check private key
openssl rsa -in C:\backend_api\certs\backend_api_key.pem -check

# Check certificate
openssl x509 -in C:\backend_api\certs\backend_api_cert.pem -text -noout
```

---

### Step 3: Configure Backend API for HTTPS

#### Update config.env

```powershell
# Copy HTTPS template
cp config.env.https config.env

# Edit configuration
notepad config.env
```

**Required settings:**

```ini
# Enable HTTPS
ENABLE_HTTPS=true

# Certificate paths
SSL_CERT_PATH=C:\backend_api\certs\backend_api_cert.pem
SSL_KEY_PATH=C:\backend_api\certs\backend_api_key.pem

# HTTPS port (different from HTTP)
SSL_PORT=6922

# TLS version (TLS1_2 recommended for compatibility)
SSL_MIN_VERSION=TLS1_2

# Enable HTTP Strict Transport Security
ENABLE_HSTS=true
HSTS_MAX_AGE=31536000  # 1 year
```

#### Update Python Script

**Option A:** Use new HTTPS-enabled backend

```powershell
# Replace backend_api_v4.py with HTTPS version
cp backend_api_v4_https.py backend_api_v4.py
```

**Option B:** Run side-by-side

```powershell
# Keep HTTP on port 6921
# Run HTTPS on port 6922
python backend_api_v4_https.py
```

---

### Step 4: Configure Firewall

```powershell
# Add firewall rule for HTTPS
New-NetFirewallRule `
  -DisplayName "Backend API HTTPS" `
  -Direction Inbound `
  -LocalPort 6922 `
  -Protocol TCP `
  -Action Allow

# Verify rule
Get-NetFirewallRule -DisplayName "Backend API HTTPS" | Get-NetFirewallPortFilter
```

---

### Step 5: Test Locally

```powershell
# Test HTTPS health endpoint (ignore self-signed cert warning)
curl -k https://localhost:6922/health

# Expected response:
{
  "status": "ok",
  "version": "4.0.3-https-enabled",
  "database": "connected",
  "timestamp": "2026-02-02T06:00:00Z"
}

# Test with authentication
$token = (Get-Content config.env | Where-Object { $_ -match "API_TOKEN" }).Split("=")[1]

curl -k -H "Authorization: Bearer $token" `
     -H "Content-Type: application/json" `
     -X POST https://localhost:6922/connections `
     -d '{
       "client_ip": "test",
       "client_port": 1,
       "frontend_port": 8041,
       "backend_host": "test",
       "backend_port": 1429,
       "timestamp": "2026-02-02T06:00:00Z"
     }'

# Expected response:
{"status": "success", "port": 8041, "client": "test:1"}
```

---

### Step 6: Configure VPS L4 Redirector

#### Update VPS Configuration

```bash
# SSH to VPS
ssh user@your-vps-ip

# Edit L4 Redirector config
sudo nano /etc/l4-redirector/config.env
```

**Add/update these settings:**

```bash
# Backend API connection
LOCALTONET_IP=YOUR_WINDOWS_IP
LOCALTONET_PORT=6922  # HTTPS port

# HTTPS settings
BACKEND_USE_HTTPS=true
BACKEND_VERIFY_SSL=false  # For self-signed certificates

# Authentication
BACKEND_API_TOKEN=YOUR_64_CHAR_TOKEN
```

#### Update L4 Redirector Python Script

If using `requests` library for HTTP calls, update:

```python
import requests

# HTTPS connection to backend
url = f"https://{LOCALTONET_IP}:{LOCALTONET_PORT}/connections"

response = requests.post(
    url,
    json=data,
    headers={
        "Authorization": f"Bearer {BACKEND_API_TOKEN}",
        "Content-Type": "application/json"
    },
    verify=False  # Disable SSL verification for self-signed certs
)
```

**Note:** Add `verify=False` or point to certificate:
```python
verify=False  # Don't verify (insecure but works with self-signed)
# OR
verify="/path/to/backend_api_cert.pem"  # Verify against cert
```

#### Restart VPS Service

```bash
# Restart L4 Redirector
sudo systemctl restart l4-redirector-v4

# Check status
sudo systemctl status l4-redirector-v4

# Monitor logs
sudo journalctl -u l4-redirector-v4 -f
```

---

### Step 7: Test End-to-End

#### From VPS

```bash
# Test health endpoint
curl -k https://YOUR_WINDOWS_IP:6922/health

# Test /connections endpoint with authentication
curl -k \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST https://YOUR_WINDOWS_IP:6922/connections \
  -d '{
    "client_ip": "203.0.113.45",
    "client_port": 54321,
    "frontend_port": 8041,
    "backend_host": "192.168.1.100",
    "backend_port": 1429,
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'

# Expected: {"status": "success", "port": 8041, "client": "203.0.113.45:54321"}
```

#### Check Windows Logs

```powershell
# Real-time log monitoring
Get-Content C:\Logs\backend_api\backend_api_v4.log -Tail 50 -Wait

# Look for:
# - 🔒 SSL context created successfully
# - 🚀 WINDOWS BACKEND API v4.0.3 HTTPS EDITION
# - 🔒 HTTPS Server: 0.0.0.0:6922
# - 💾 Connection metadata stored: ...
```

#### Verify Database

```sql
-- Connect to PostgreSQL
psql -U redirector_user -d redirector_db

-- Check recent connections
SELECT * FROM web_connections 
ORDER BY timestamp DESC 
LIMIT 10;

-- Verify connection_id is populated
SELECT connection_id, client_ip, client_port, timestamp 
FROM web_connections 
WHERE worker_id = 'l4-redirector' 
ORDER BY timestamp DESC 
LIMIT 5;
```

---

## 🔧 Advanced Configuration

### Using CA-Signed Certificates

For production with a proper CA-signed certificate:

1. **Obtain certificate from CA** (Let's Encrypt, DigiCert, etc.)
2. **Place files:**
   ```
   C:\backend_api\certs\
   ├── ca_cert.pem          # Your domain certificate
   ├── ca_key.pem           # Private key
   └── ca_chain.pem         # CA chain (optional)
   ```
3. **Update config.env:**
   ```ini
   SSL_CERT_PATH=C:\backend_api\certs\ca_cert.pem
   SSL_KEY_PATH=C:\backend_api\certs\ca_key.pem
   ```
4. **Update VPS:**
   ```bash
   BACKEND_VERIFY_SSL=true  # Enable verification
   ```

### Dual HTTP/HTTPS Mode

Run both HTTP and HTTPS simultaneously during migration:

```powershell
# Terminal 1: HTTP (port 6921)
$env:ENABLE_HTTPS="false"
python backend_api_v4.py

# Terminal 2: HTTPS (port 6922)
$env:ENABLE_HTTPS="true"
python backend_api_v4_https.py
```

Configure VPS to use either port based on testing progress.

### TLS 1.3 Only

For maximum security (may have compatibility issues):

```ini
SSL_MIN_VERSION=TLS1_3
```

Test compatibility:
```powershell
# Test TLS 1.3
openssl s_client -connect localhost:6922 -tls1_3
```

---

## 🚫 Troubleshooting

### Issue: Certificate Not Found

**Error:**
```
❌ SSL certificate not found: C:\backend_api\certs\backend_api_cert.pem
```

**Solution:**
```powershell
# Verify file exists
Test-Path C:\backend_api\certs\backend_api_cert.pem

# If missing, regenerate
.\generate_ssl_cert.ps1
```

---

### Issue: Private Key Not Found

**Error:**
```
❌ SSL private key not found: C:\backend_api\certs\backend_api_key.pem
```

**Solution:**
```powershell
# Extract from PFX
openssl pkcs12 -in C:\backend_api\certs\backend_api.pfx `
               -nocerts -out C:\backend_api\certs\backend_api_key.pem -nodes

# Enter password from pfx_password.txt
```

---

### Issue: VPS Connection Refused

**Error:**
```
curl: (7) Failed to connect to 192.168.1.100 port 6922: Connection refused
```

**Diagnosis:**
```powershell
# Check if backend is listening
netstat -ano | findstr 6922

# Check firewall
Get-NetFirewallRule -DisplayName "Backend API HTTPS" | Get-NetFirewallPortFilter

# Test from Windows
curl -k https://localhost:6922/health
```

**Solution:**
1. Verify backend is running
2. Add firewall rule (see Step 4)
3. Check LocalToNet/WireGuard tunnel

---

### Issue: SSL Handshake Failed

**Error:**
```
SSL routines:tls_process_server_certificate:certificate verify failed
```

**Solution for Self-Signed:**
```bash
# VPS: Disable SSL verification
# In config.env:
BACKEND_VERIFY_SSL=false

# In curl:
curl -k https://...

# In Python requests:
requests.post(url, verify=False)
```

**Solution for CA-Signed:**
```bash
# Verify certificate chain
openssl s_client -connect YOUR_WINDOWS_IP:6922 -showcerts

# Check expiration
openssl x509 -in cert.pem -noout -dates
```

---

### Issue: HSTS Not Working

**Symptom:** No `Strict-Transport-Security` header in response

**Diagnosis:**
```powershell
curl -I -k https://localhost:6922/health
```

**Solution:**
```ini
# Ensure HTTPS is enabled
ENABLE_HTTPS=true
ENABLE_HSTS=true
```

---

## 📊 Security Best Practices

### Certificate Management

✅ **DO:**
- Use 4096-bit RSA keys
- Set certificate expiration reminders (30 days before)
- Secure private keys with restrictive permissions
- Use CA-signed certificates for production
- Include all relevant SANs (IPs, domains)

❌ **DON'T:**
- Commit certificates/keys to version control
- Share private keys via insecure channels
- Use weak key sizes (< 2048 bits)
- Ignore certificate expiration warnings
- Use the same certificate across multiple environments

### TLS Configuration

```ini
# Production-ready settings
SSL_MIN_VERSION=TLS1_2  # Or TLS1_3 if compatible
ENABLE_HSTS=true
HSTS_MAX_AGE=31536000  # 1 year
```

### File Permissions

```powershell
# Secure certificate directory
icacls C:\backend_api\certs /inheritance:r
icacls C:\backend_api\certs /grant:r "SYSTEM:(OI)(CI)F"
icacls C:\backend_api\certs /grant:r "${env:USERNAME}:(OI)(CI)F"

# Verify permissions
icacls C:\backend_api\certs
```

---

## 📝 Verification Checklist

Before deploying to production:

- [ ] Certificate generated with correct CN/SANs
- [ ] Private key extracted to PEM format
- [ ] `config.env` updated with HTTPS settings
- [ ] Firewall rule added for port 6922
- [ ] Backend starts without errors
- [ ] Local HTTPS test passes (`curl -k https://localhost:6922/health`)
- [ ] VPS can connect to Windows HTTPS endpoint
- [ ] `/connections` endpoint works from VPS
- [ ] Data appears in database with `connection_id` populated
- [ ] No SSL/TLS errors in logs
- [ ] Certificate expiration date noted in calendar
- [ ] Backup of certificate/key stored securely

---

## 📚 Additional Resources

### Documentation
- [README.md](./README.md) - Main backend documentation
- [PRODUCTION_STANDARDS_PLAN.md](./PRODUCTION_STANDARDS_PLAN.md) - Future enhancements
- [VPS DEPLOYMENT_GUIDE.md](../VPS/DEPLOYMENT_GUIDE.md) - VPS L4 Redirector setup

### Commands Reference

```powershell
# Generate certificate
.\generate_ssl_cert.ps1 -CertName "IP_OR_DOMAIN"

# Extract private key
openssl pkcs12 -in cert.pfx -nocerts -out key.pem -nodes

# Test HTTPS
curl -k https://localhost:6922/health

# View certificate info
openssl x509 -in cert.pem -text -noout

# Check certificate expiration
openssl x509 -in cert.pem -noout -dates

# Restart service
Restart-Service BackendAPIv4

# Monitor logs
Get-Content C:\Logs\backend_api\backend_api_v4.log -Tail 50 -Wait
```

---

## ℹ️ Support

If you encounter issues:

1. **Check logs:** `C:\Logs\backend_api\backend_api_v4.log`
2. **Verify configuration:** Review `config.env` settings
3. **Test locally first:** Before testing from VPS
4. **Review this guide:** Ensure all steps completed
5. **Open GitHub issue:** Include logs and configuration (redact secrets!)

**GitHub Issues:** https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues

---

**Version:** 1.0.0  
**Last Updated:** February 02, 2026  
**Status:** Production Ready  
**Compatibility:** Windows Backend API v4.0.3-https-enabled
