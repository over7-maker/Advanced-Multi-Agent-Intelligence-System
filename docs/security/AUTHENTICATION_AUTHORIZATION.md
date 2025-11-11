# 🔐 Authentication & Authorization Guide

## Overview

AMAS implements enterprise-grade authentication and authorization using industry-standard protocols and policy-as-code principles. This guide covers the complete authentication and authorization system implemented in PR-B.

---

## Table of Contents

1. [Authentication Architecture](#authentication-architecture)
2. [OIDC/JWT Authentication](#oidcjwt-authentication)
3. [Token Management](#token-management)
4. [Authorization with OPA](#authorization-with-opa)
5. [Agent Contract Validation](#agent-contract-validation)
6. [Security Headers](#security-headers)
7. [Configuration](#configuration)
8. [API Usage Examples](#api-usage-examples)
9. [Troubleshooting](#troubleshooting)

---

## Authentication Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Application                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Browser    │  │  Mobile App  │  │  API Client  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │  OIDC Flow       │  OIDC Flow       │  OIDC Flow
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              OIDC Provider (External)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Auth Server │  │   JWKS URI   │  │  Token Endpt │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │  JWT Token       │  Public Keys     │  Token Validation
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              AMAS API (FastAPI Application)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         AuthenticationMiddleware                      │   │
│  │  - Validates JWT tokens                               │   │
│  │  - Caches JWKS                                        │   │
│  │  - Manages token blacklist                            │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │         AuthorizationMiddleware (OPA)                 │   │
│  │  - Evaluates policies                                 │   │
│  │  - Checks agent contracts                             │   │
│  │  - Enforces RBAC                                      │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │         SecurityHeadersMiddleware                     │   │
│  │  - Adds HSTS, CSP, X-Frame-Options, etc.            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

**Location:** `src/amas/api/main.py`

- **Lines 47-49:** Global security components initialization
- **Lines 60-71:** SecurityHeadersMiddlewareWrapper
- **Lines 73-90:** AuthenticationMiddleware (protects `/api/v1/*` routes)
- **Lines 194-196:** SecureAuthenticationManager initialization in startup

---

## OIDC/JWT Authentication

### How It Works

1. **Client obtains JWT token** from OIDC provider (e.g., Auth0, Okta, Keycloak)
2. **Client sends token** in `Authorization: Bearer <token>` header
3. **AMAS validates token** using JWKS (JSON Web Key Set) from OIDC provider
4. **Token is cached** for performance (configurable TTL)
5. **Request proceeds** if token is valid, otherwise returns 401

### JWT Validation Process

```python
# Simplified validation flow (actual implementation in JWTMiddleware)
1. Extract token from Authorization header
2. Decode JWT header to get key ID (kid)
3. Fetch public key from JWKS (cached if available)
4. Verify signature using public key
5. Validate claims:
   - exp (expiration)
   - iat (issued at)
   - nbf (not before)
   - sub (subject)
   - aud (audience) - must match configured audience
   - iss (issuer) - must match configured issuer
6. Check token blacklist (if logout was called)
7. Extract user context for authorization
```

### Configuration

**File:** `config/security_config.yaml`

```yaml
authentication:
  oidc:
    issuer: "${OIDC_ISSUER:-https://your-oidc-provider.com}"
    audience: "${OIDC_AUDIENCE:-amas-api}"
    jwks_uri: "${OIDC_JWKS_URI:-https://your-oidc-provider.com/.well-known/jwks.json}"
    algorithms: ["RS256", "ES256"]
    cache_ttl: 3600  # JWKS cache TTL in seconds
    refresh_interval: 300  # Background refresh interval
    require_exp: true
    require_iat: true
    require_nbf: true
    require_sub: true
    max_token_age_days: 30
```

### Environment Variables

```bash
# Required for production
export OIDC_ISSUER="https://your-oidc-provider.com"
export OIDC_AUDIENCE="amas-api"
export OIDC_JWKS_URI="https://your-oidc-provider.com/.well-known/jwks.json"

# Optional
export OIDC_EXPECTED_AZP="your-client-id"  # Expected authorized party
```

### JWKS Caching

The system automatically caches JWKS (public keys) to reduce latency:

- **Cache TTL:** 3600 seconds (1 hour) by default
- **Background Refresh:** Every 5 minutes to ensure keys are up-to-date
- **Automatic Invalidation:** On token validation failure
- **Fallback:** Fetches fresh keys if cache miss

---

## Token Management

### Token Blacklisting

Tokens can be blacklisted for secure logout and session management:

```python
from amas.security.auth.jwt_middleware import TokenBlacklist

# Blacklist a token (called on logout)
blacklist = TokenBlacklist()
blacklist.add(token_id, expires_at)

# Check if token is blacklisted
if blacklist.is_blacklisted(token_id):
    raise HTTPException(status_code=401, detail="Token has been revoked")
```

### Token Lifecycle

```
┌─────────────┐
│   Client    │
│  Requests   │
│    Token    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  OIDC       │
│  Provider   │
│  Issues     │
│  JWT Token  │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌─────────────┐
│  AMAS API   │──────▶│  Validate   │
│  Receives   │       │  & Cache    │
│  Token      │       │  JWKS        │
└──────┬──────┘       └─────────────┘
       │
       ▼
┌─────────────┐
│  Check      │
│  Blacklist  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Extract    │
│  User Info  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Process    │
│  Request    │
└─────────────┘
```

### Secure Logout

```python
# Endpoint implementation (example)
@app.post("/api/v1/auth/logout")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(AMASHTTPBearer())
):
    """Secure logout - blacklists the current token"""
    token = credentials.credentials
    token_id = extract_token_id(token)  # Extract JTI from token
    
    # Add to blacklist
    blacklist = TokenBlacklist()
    blacklist.add(token_id, get_token_expiry(token))
    
    return {"message": "Logged out successfully"}
```

---

## Authorization with OPA

### Open Policy Agent Integration

AMAS uses Open Policy Agent (OPA) for policy-as-code authorization. All authorization decisions are made by evaluating Rego policies.

### Policy Structure

**Location:** `policies/agent_access.rego`

```rego
package agent.access

# Default deny
default allow = false

# Allow if agent role has permission for tool
allow {
    input.role == "security_analyst"
    input.tool == "vulnerability_scanner"
}

allow {
    input.role == "data_analyst"
    input.tool == "data_processor"
}
```

### Policy Evaluation

**Location:** `src/amas/security/policies/opa_integration.py`

```python
from amas.security.policies.opa_integration import get_policy_engine

# Initialize policy engine (done in startup)
policy_engine = get_policy_engine()

# Evaluate policy
result = policy_engine.check_permission(
    role="security_analyst",
    action="execute",
    resource="vulnerability_scanner",
    context={"user_id": "user123"}
)
```

### Configuration

**File:** `config/security_config.yaml`

```yaml
authorization:
  opa:
    url: "${OPA_URL:-http://localhost:8181}"
    timeout_seconds: 5.0
    retry_attempts: 3
    cache_enabled: true
    cache_ttl: 300  # 5 minutes
    cache_max_size: 1000
    policies:
      agent_access: "agent.access"
      tool_permission: "tool.permission"
      data_access: "data.access"
      user_permissions: "user.permissions"
```

**Environment Variable:**

```bash
export OPA_URL="http://localhost:8181"
```

### OPA Server Setup

```bash
# Run OPA server
docker run -d \
  --name opa \
  -p 8181:8181 \
  -v $(pwd)/policies:/policies \
  openpolicyagent/opa:latest \
  run --server --log-level debug /policies
```

---

## Agent Contract Validation

### Overview

Agent contract validation ensures that agents can only execute tasks they are authorized for, based on their role and the tool/action being performed.

### Implementation

**Location:** `src/amas/core/orchestrator.py` (Lines 636-661)

```python
# Validate agent contract before execution
try:
    from ...governance.agent_contracts import validate_agent_action
    
    agent_role = getattr(agent, 'role', None) or getattr(agent, 'agent_type', 'default')
    
    allowed, error = validate_agent_action(
        role_name=agent_role,
        tool_name=task.type,
        action_data=task.parameters or {}
    )
    
    if not allowed:
        error_msg = error or f"Agent {agent_role} not authorized for task {task.type}"
        self.logger.warning(f"Agent contract validation failed: {error_msg}")
        task.status = TaskStatus.FAILED
        task.error = f"Authorization failed: {error_msg}"
        return
except ImportError:
    self.logger.debug("Agent contracts not available, skipping validation")
except Exception as e:
    self.logger.warning(f"Agent contract validation error (continuing): {e}")
```

### How It Works

1. **Before task execution**, orchestrator calls `validate_agent_action()`
2. **Validation checks:**
   - Agent role is authorized for the tool
   - Action parameters are valid
   - No policy violations
3. **If validation fails:**
   - Task status set to `FAILED`
   - Error message logged
   - Task execution blocked
4. **If validation passes:**
   - Task proceeds normally

### Example

```python
# Agent tries to execute unauthorized tool
agent_role = "data_analyst"
tool_name = "vulnerability_scanner"

# Validation fails
allowed, error = validate_agent_action(
    role_name=agent_role,
    tool_name=tool_name,
    action_data={}
)
# Returns: (False, "data_analyst not authorized for vulnerability_scanner")

# Task is blocked
task.status = TaskStatus.FAILED
task.error = "Authorization failed: data_analyst not authorized for vulnerability_scanner"
```

---

## Security Headers

### Headers Applied

All HTTP responses include the following security headers:

- **Strict-Transport-Security (HSTS):** `max-age=31536000; includeSubDomains`
- **Content-Security-Policy (CSP):** Configurable policy
- **X-Frame-Options:** `DENY`
- **X-Content-Type-Options:** `nosniff`
- **X-XSS-Protection:** `1; mode=block`
- **Referrer-Policy:** `strict-origin-when-cross-origin`
- **Permissions-Policy:** Restricts browser features

### Implementation

**Location:** `src/amas/api/main.py` (Lines 60-71)

```python
class SecurityHeadersMiddlewareWrapper(BaseHTTPMiddleware):
    """Wrapper to add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        global security_headers_middleware
        if security_headers_middleware:
            await security_headers_middleware.add_security_headers(request, response)
        return response

app.add_middleware(SecurityHeadersMiddlewareWrapper)
```

### Configuration

**File:** `config/security_config.yaml`

```yaml
authentication:
  security_headers:
    enabled: true
    hsts_max_age: 31536000  # 1 year
    csp_enabled: true
```

---

## Configuration

### Complete Configuration Example

**File:** `config/security_config.yaml`

```yaml
authentication:
  oidc:
    issuer: "${OIDC_ISSUER}"
    audience: "${OIDC_AUDIENCE}"
    jwks_uri: "${OIDC_JWKS_URI}"
    algorithms: ["RS256", "ES256"]
    cache_ttl: 3600
    refresh_interval: 300
    require_exp: true
    require_iat: true
    require_nbf: true
    require_sub: true
    max_token_age_days: 30
  
  token_blacklist:
    enabled: true
    cleanup_interval: 3600
  
  security_headers:
    enabled: true
    hsts_max_age: 31536000
    csp_enabled: true

authorization:
  opa:
    url: "${OPA_URL:-http://localhost:8181}"
    timeout_seconds: 5.0
    retry_attempts: 3
    cache_enabled: true
    cache_ttl: 300
    cache_max_size: 1000
```

### Environment Variables

```bash
# OIDC Configuration (Required)
export OIDC_ISSUER="https://your-oidc-provider.com"
export OIDC_AUDIENCE="amas-api"
export OIDC_JWKS_URI="https://your-oidc-provider.com/.well-known/jwks.json"

# OPA Configuration (Required)
export OPA_URL="http://localhost:8181"

# Security Config Path (Optional)
export SECURITY_CONFIG="config/security_config.yaml"
```

---

## API Usage Examples

### Authenticated Request

```bash
# Get JWT token from OIDC provider
TOKEN=$(curl -X POST https://your-oidc-provider.com/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "grant_type": "client_credentials"
  }' | jq -r '.access_token')

# Make authenticated API call
curl -X GET https://amas.example.com/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

### Python Client Example

```python
import requests

# Get token
token_response = requests.post(
    "https://your-oidc-provider.com/oauth/token",
    json={
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "grant_type": "client_credentials"
    }
)
token = token_response.json()["access_token"]

# Make authenticated request
response = requests.get(
    "https://amas.example.com/api/v1/tasks",
    headers={"Authorization": f"Bearer {token}"}
)
print(response.json())
```

### JavaScript/TypeScript Example

```typescript
// Get token
const tokenResponse = await fetch('https://your-oidc-provider.com/oauth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    client_id: 'your-client-id',
    client_secret: 'your-client-secret',
    grant_type: 'client_credentials'
  })
});
const { access_token } = await tokenResponse.json();

// Make authenticated request
const response = await fetch('https://amas.example.com/api/v1/tasks', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const data = await response.json();
```

---

## Troubleshooting

### Common Issues

#### 1. 401 Unauthorized

**Symptoms:** All API calls return 401

**Possible Causes:**
- Missing or invalid JWT token
- Token expired
- Wrong OIDC issuer/audience configuration
- JWKS URI unreachable

**Solutions:**
```bash
# Check token validity
echo $TOKEN | cut -d. -f2 | base64 -d | jq

# Verify OIDC configuration
curl $OIDC_JWKS_URI

# Check logs
tail -f logs/amas.log | grep -i "jwt\|auth"
```

#### 2. 403 Forbidden

**Symptoms:** Authenticated but unauthorized

**Possible Causes:**
- Agent contract validation failed
- OPA policy denies access
- Insufficient role permissions

**Solutions:**
```bash
# Check agent role
curl -H "Authorization: Bearer $TOKEN" \
  https://amas.example.com/api/v1/agents

# Test OPA policy
curl -X POST http://localhost:8181/v1/data/agent/access \
  -H "Content-Type: application/json" \
  -d '{"input": {"role": "data_analyst", "tool": "vulnerability_scanner"}}'

# Check audit logs
tail -f logs/audit.log | grep -i "authorization\|forbidden"
```

#### 3. JWKS Cache Issues

**Symptoms:** Token validation fails after key rotation

**Solutions:**
```python
# Clear JWKS cache (if implemented)
from amas.security.auth.jwt_middleware import JWTMiddleware
middleware = JWTMiddleware(...)
middleware.clear_jwks_cache()
```

#### 4. OPA Connection Errors

**Symptoms:** Authorization fails with connection errors

**Solutions:**
```bash
# Check OPA server status
curl http://localhost:8181/health

# Verify OPA URL configuration
echo $OPA_URL

# Check network connectivity
telnet localhost 8181
```

---

## Security Best Practices

1. **Always use HTTPS** in production
2. **Rotate OIDC keys regularly** (every 90 days)
3. **Set appropriate token expiration** (max 1 hour for access tokens)
4. **Monitor authentication failures** for brute force attempts
5. **Review OPA policies regularly** for correctness
6. **Audit all authorization decisions** (logged automatically)
7. **Use least privilege** in agent contracts
8. **Keep OPA server updated** and patched

---

## Additional Resources

- [OIDC Specification](https://openid.net/specs/openid-connect-core-1_0.html)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [OPA Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Rego Policy Language](https://www.openpolicyagent.org/docs/latest/policy-language/)

---

**Last Updated:** After PR-B Integration  
**Version:** 1.0.0  
**Status:** Production Ready
