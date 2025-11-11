# 🔒 Security Setup Guide

## Quick Start

This guide will help you set up the enterprise security features implemented in PR-B.

---

## Prerequisites

- AMAS application installed and running
- Access to an OIDC provider (Auth0, Okta, Keycloak, etc.)
- Open Policy Agent (OPA) server (optional, for authorization)
- Python 3.11+

---

## Step 1: Configure OIDC Provider

### 1.1 Set Up OIDC Provider

Choose and configure your OIDC provider:

**Option A: Auth0**
1. Create an Auth0 account
2. Create a new application (Machine to Machine)
3. Note the Domain, Client ID, and Client Secret
4. Configure API audience

**Option B: Keycloak**
1. Install Keycloak
2. Create a realm
3. Create a client
4. Note the issuer URL and client credentials

**Option C: Okta**
1. Create an Okta developer account
2. Create an application
3. Note the issuer URL and client credentials

### 1.2 Get OIDC Configuration

You'll need:
- **Issuer URL:** `https://your-provider.com` or `https://your-provider.com/realms/your-realm`
- **JWKS URI:** Usually `https://your-provider.com/.well-known/jwks.json`
- **Audience:** Your API identifier (e.g., `amas-api`)

---

## Step 2: Configure Environment Variables

### 2.1 Create `.env` File

```bash
# OIDC Configuration (Required)
OIDC_ISSUER=https://your-oidc-provider.com
OIDC_AUDIENCE=amas-api
OIDC_JWKS_URI=https://your-oidc-provider.com/.well-known/jwks.json

# OPA Configuration (Required for authorization)
OPA_URL=http://localhost:8181

# Audit Logging (Optional)
AUDIT_LOG_FILE=logs/audit.jsonl
AUDIT_BUFFER_SIZE=100
AUDIT_FLUSH_INTERVAL=30
AUDIT_REDACT_PII=true

# OpenTelemetry (Optional)
OTLP_ENDPOINT=http://localhost:4317
OTLP_ENABLE_CONSOLE=false

# Security Config Path (Optional)
SECURITY_CONFIG=config/security_config.yaml
```

### 2.2 Update `config/security_config.yaml`

```yaml
authentication:
  oidc:
    issuer: "${OIDC_ISSUER}"
    audience: "${OIDC_AUDIENCE}"
    jwks_uri: "${OIDC_JWKS_URI}"
    algorithms: ["RS256", "ES256"]
    cache_ttl: 3600
    refresh_interval: 300

authorization:
  opa:
    url: "${OPA_URL:-http://localhost:8181}"
    timeout_seconds: 5.0
    retry_attempts: 3
    cache_enabled: true
    cache_ttl: 300

audit:
  log_file: "${AUDIT_LOG_FILE:-logs/audit.jsonl}"
  buffer_size: 100
  flush_interval: 30
  redact_sensitive: true
```

---

## Step 3: Set Up OPA Server (Optional)

### 3.1 Install OPA

**Using Docker:**
```bash
docker run -d \
  --name opa \
  -p 8181:8181 \
  -v $(pwd)/policies:/policies \
  openpolicyagent/opa:latest \
  run --server --log-level debug /policies
```

**Using Binary:**
```bash
# Download OPA
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa

# Run OPA server
./opa run --server --log-level debug policies/
```

### 3.2 Create Policy Files

**File:** `policies/agent_access.rego`

```rego
package agent.access

# Default deny
default allow = false

# Security analysts can use vulnerability scanners
allow {
    input.role == "security_analyst"
    input.tool == "vulnerability_scanner"
}

# Data analysts can use data processors
allow {
    input.role == "data_analyst"
    input.tool == "data_processor"
}

# Admins can use all tools
allow {
    input.role == "admin"
}
```

### 3.3 Load Policies

```bash
# Load policy into OPA
curl -X PUT http://localhost:8181/v1/policies/agent.access \
  -H "Content-Type: text/plain" \
  --data-binary @policies/agent_access.rego

# Verify policy loaded
curl http://localhost:8181/v1/policies/agent.access
```

---

## Step 4: Test Authentication

### 4.1 Get JWT Token

**Using curl:**
```bash
# Get token from OIDC provider
TOKEN=$(curl -X POST https://your-oidc-provider.com/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "grant_type": "client_credentials",
    "audience": "amas-api"
  }' | jq -r '.access_token')

echo $TOKEN
```

### 4.2 Test API Call

```bash
# Test authenticated request
curl -X GET http://localhost:8000/api/v1/health \
  -H "Authorization: Bearer $TOKEN"

# Should return 200 OK
```

### 4.3 Test Unauthenticated Request

```bash
# Test without token (should return 401)
curl -X GET http://localhost:8000/api/v1/tasks

# Expected response:
# {"detail": "Not authenticated"}
```

---

## Step 5: Verify Audit Logging

### 5.1 Check Audit Log File

```bash
# Create logs directory if it doesn't exist
mkdir -p logs

# Make a few API calls, then check logs
tail -f logs/audit.jsonl

# Should see JSON log entries like:
# {"timestamp": "2025-01-15T10:30:45.123Z", "event_type": "api_request", "method": "GET", "path": "/api/v1/health", "status": 200, ...}
```

### 5.2 Verify PII Redaction

```bash
# Make a request with sensitive data
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "phone": "555-123-4567"
  }'

# Check audit log - sensitive data should be redacted
cat logs/audit.jsonl | jq 'select(.event_type == "api_request")' | tail -1
# Should show: "email": "[REDACTED:email]", "phone": "[REDACTED:phone]"
```

---

## Step 6: Verify Security Headers

### 6.1 Check Response Headers

```bash
# Make a request and check headers
curl -I -X GET http://localhost:8000/api/v1/health \
  -H "Authorization: Bearer $TOKEN"

# Should see headers like:
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Content-Security-Policy: default-src 'self'
```

---

## Step 7: Test Authorization

### 7.1 Test Agent Contract Validation

```python
# Test agent authorization
from amas.governance.agent_contracts import validate_agent_action

# This should fail (data_analyst cannot use vulnerability_scanner)
allowed, error = validate_agent_action(
    role_name="data_analyst",
    tool_name="vulnerability_scanner",
    action_data={}
)
print(f"Allowed: {allowed}, Error: {error}")
# Expected: Allowed: False, Error: "data_analyst not authorized for vulnerability_scanner"

# This should succeed
allowed, error = validate_agent_action(
    role_name="security_analyst",
    tool_name="vulnerability_scanner",
    action_data={}
)
print(f"Allowed: {allowed}, Error: {error}")
# Expected: Allowed: True, Error: None
```

---

## Troubleshooting

### Issue: 401 Unauthorized on All Requests

**Solution:**
1. Verify OIDC configuration:
   ```bash
   echo $OIDC_ISSUER
   echo $OIDC_AUDIENCE
   echo $OIDC_JWKS_URI
   ```

2. Test JWKS URI:
   ```bash
   curl $OIDC_JWKS_URI
   ```

3. Verify token is valid:
   ```bash
   echo $TOKEN | cut -d. -f2 | base64 -d | jq
   ```

### Issue: OPA Connection Errors

**Solution:**
1. Check OPA server is running:
   ```bash
   curl http://localhost:8181/health
   ```

2. Verify OPA_URL:
   ```bash
   echo $OPA_URL
   ```

3. Check network connectivity:
   ```bash
   telnet localhost 8181
   ```

### Issue: Audit Logs Not Created

**Solution:**
1. Check directory permissions:
   ```bash
   mkdir -p logs
   chmod 755 logs
   ```

2. Check environment variable:
   ```bash
   echo $AUDIT_LOG_FILE
   ```

3. Check application logs for errors

### Issue: PII Not Redacted

**Solution:**
1. Verify redaction is enabled:
   ```bash
   echo $AUDIT_REDACT_PII
   # Should be "true"
   ```

2. Check configuration:
   ```yaml
   audit:
     redact_sensitive: true
   ```

---

## Next Steps

1. **Review Security Configuration:** See [config/security_config.yaml](../../config/security_config.yaml)
2. **Customize Policies:** See [policies/agent_access.rego](../../policies/agent_access.rego)
3. **Read Full Documentation:**
   - [Authentication & Authorization Guide](AUTHENTICATION_AUTHORIZATION.md)
   - [Audit Logging Guide](AUDIT_LOGGING.md)
   - [Main Security Guide](../SECURITY.md)

---

## Production Checklist

Before deploying to production:

- [ ] OIDC provider configured and tested
- [ ] OPA server deployed and policies loaded
- [ ] Environment variables set in production environment
- [ ] Audit logging directory created and writable
- [ ] Security headers verified
- [ ] Token blacklisting tested
- [ ] Agent contract validation tested
- [ ] PII redaction verified
- [ ] Log rotation configured
- [ ] Backup procedures for audit logs
- [ ] Monitoring and alerting configured
- [ ] Security incident response plan documented

---

**Last Updated:** After PR-B Integration  
**Version:** 1.0.0  
**Status:** Production Ready
