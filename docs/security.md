# AMAS Security Hardening Guide

## 1. Authentication & Authorization

### 1.1 JWT Token Security
```
# Implement token rotation
JWT_EXPIRATION = 15 * 60  # 15 minutes
REFRESH_TOKEN_EXPIRATION = 7 * 24 * 60 * 60  # 7 days

# Use strong secret keys (minimum 32 bytes)
SECRET_KEY = secrets.token_urlsafe(32)
JWT_SECRET = secrets.token_urlsafe(32)
```

### 1.2 Password Policy
- Minimum 12 characters
- Require uppercase, lowercase, numbers, special characters
- Use bcrypt with cost factor 12+
- Implement password history (prevent reuse)
- Enable account lockout after 5 failed attempts

### 1.3 Multi-Factor Authentication (MFA)
```
# Enable MFA for all admin accounts
MFA_REQUIRED_ROLES = ['admin', 'security_admin']
MFA_METHODS = ['totp', 'sms', 'email']
```

## 2. API Security

### 2.1 Rate Limiting
```
# Nginx configuration
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
```

### 2.2 Input Validation
- Validate all user inputs
- Use Pydantic models for request validation
- Sanitize HTML/SQL to prevent injection
- Implement file upload restrictions (size, type)

### 2.3 CORS Configuration
```
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com"
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE"]
```

## 3. Database Security

### 3.1 Connection Security
```
# Use SSL/TLS for database connections
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"

# Rotate database passwords quarterly
# Use separate credentials for different environments
```

### 3.2 SQL Injection Prevention
- Use parameterized queries (ALWAYS)
- Never concatenate user input into SQL
- Use ORM (SQLAlchemy) for complex queries

### 3.3 Data Encryption
```
# Encrypt sensitive fields at rest
from cryptography.fernet import Fernet

class EncryptedField:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

## 4. Network Security

### 4.1 HTTPS/TLS
- Use TLS 1.2 or higher
- Strong cipher suites only
- Implement HSTS (HTTP Strict Transport Security)
- Renew certificates before expiration

### 4.2 Firewall Rules
```
# Allow only necessary ports
iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP (redirect to HTTPS)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH (from specific IPs only)
iptables -A INPUT -j DROP  # Drop all other traffic
```

### 4.3 DDoS Protection
- Use Cloudflare or AWS WAF
- Implement request throttling
- Set up IP whitelisting for admin endpoints

## 5. Secrets Management

### 5.1 Environment Variables
```
# Never commit secrets to Git
# Use secret management services
export DATABASE_URL=$(aws secretsmanager get-secret-value --secret-id prod/db/url --query SecretString --output text)
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value --secret-id prod/openai/key --query SecretString --output text)
```

### 5.2 Kubernetes Secrets
```
apiVersion: v1
kind: Secret
metadata:
  name: amas-secrets
type: Opaque
data:
  db-password: <base64-encoded>
  jwt-secret: <base64-encoded>
```

### 5.3 Secret Rotation
- Rotate all secrets every 90 days
- Implement automated rotation for API keys
- Log all secret access

## 6. Logging & Monitoring

### 6.1 Security Logging
```
# Log all security events
security_logger.info(
    "login_attempt",
    extra={
        "user_id": user_id,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "success": True
    }
)
```

### 6.2 Audit Trail
- Log all administrative actions
- Track data access and modifications
- Retain logs for minimum 1 year
- Enable log encryption

### 6.3 Security Alerts
```
# Prometheus alert rules
- alert: MultipleFailedLogins
  expr: rate(login_failures[5m]) > 10
  annotations:
    summary: "Multiple failed login attempts detected"
    
- alert: UnauthorizedAccess
  expr: rate(http_requests_total{status="403"}[5m]) > 5
  annotations:
    summary: "High rate of unauthorized access attempts"
```

## 7. Container Security

### 7.1 Docker Best Practices
```
# Use minimal base images
FROM python:3.11-slim

# Run as non-root user
USER amas

# Scan images for vulnerabilities
# trivy image your-image:latest
```

### 7.2 Kubernetes Security
```
# Security context
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: true
```

## 8. Dependency Management

### 8.1 Vulnerability Scanning
```
# Scan Python dependencies
pip-audit

# Scan npm dependencies
npm audit

# Automated scanning in CI/CD
- name: Security scan
  run: |
    pip install safety
    safety check --json
```

### 8.2 Update Policy
- Review and update dependencies monthly
- Subscribe to security advisories
- Test updates in staging before production

## 9. Incident Response

### 9.1 Response Plan
1. **Detection** - Automated alerts via Prometheus/Grafana
2. **Assessment** - Evaluate severity and impact
3. **Containment** - Isolate affected systems
4. **Eradication** - Remove threat
5. **Recovery** - Restore from backup if needed
6. **Post-Incident** - Document and improve

### 9.2 Emergency Contacts
```
oncall:
  - role: Security Lead
    contact: security@your-domain.com
    phone: +1-xxx-xxx-xxxx
  - role: DevOps Lead
    contact: devops@your-domain.com
    phone: +1-xxx-xxx-xxxx
```

## 10. Compliance

### 10.1 GDPR Compliance
- Implement right to access
- Implement right to be forgotten
- Data minimization
- Consent management

### 10.2 SOC 2 Compliance
- Access controls
- Encryption at rest and in transit
- Audit logging
- Incident response procedures

## Security Checklist

- [ ] All secrets in secret manager (not in code)
- [ ] HTTPS/TLS enabled with strong ciphers
- [ ] Rate limiting configured
- [ ] Authentication with MFA for admins
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] CORS properly configured
- [ ] Security headers set (HSTS, CSP, X-Frame-Options)
- [ ] Container images scanned for vulnerabilities
- [ ] Logging and monitoring active
- [ ] Automated backups configured
- [ ] Disaster recovery plan documented
- [ ] Security incident response plan
- [ ] Regular security audits scheduled
