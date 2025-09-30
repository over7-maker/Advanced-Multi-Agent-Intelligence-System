# AMAS Security Hardening Guide - Enhanced

## 🔐 **Core Security Principles**

### **1. Zero-Trust Architecture**
- Every component authenticated and authorized
- Network segmentation with isolated service networks
- Principle of least privilege for all services
- Continuous security monitoring and validation

### **2. Defense in Depth**
- Multiple security layers (Network, Application, Data, Infrastructure)
- Fail-safe defaults with explicit security controls
- Comprehensive audit logging with tamper detection
- Automated security response and incident handling

## 🛡️ **System-Level Security**

### **Windows Security Configuration**
```powershell
# Enable UAC at highest level
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -Value 2

# Configure Windows Defender
Set-MpPreference -DisableRealtimeMonitoring $false
Set-MpPreference -SubmitSamplesConsent SendAllSamples
Set-MpPreference -CloudBlockLevel High

# Enable BitLocker
Enable-BitLocker -MountPoint "C:" -EncryptionMethod XtsAes256 -UsedSpaceOnly -TpmProtector
```

### **Firewall Configuration**
```powershell
# AMAS-specific firewall rules
New-NetFirewallRule -DisplayName "AMAS Web Interface" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
New-NetFirewallRule -DisplayName "AMAS API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "AMAS Ollama" -Direction Inbound -Protocol TCP -LocalPort 11434 -Action Allow -RemoteAddress LocalSubnet
```

## 🔒 **Application Security**

### **Authentication & Authorization**
```python
# JWT Configuration
JWT_SECRET_KEY = os.getenv("AMAS_JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

# RBAC Implementation
class Role(Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    RESEARCHER = "researcher"
    VIEWER = "viewer"

class Permission(Enum):
    READ_SYSTEM_STATUS = "read:system:status"
    WRITE_SYSTEM_CONFIG = "write:system:config"
    EXECUTE_AGENTS = "execute:agents"
    VIEW_AUDIT_LOGS = "view:audit:logs"
```

### **Input Validation**
```python
from pydantic import BaseModel, validator
from typing import Optional

class TaskRequest(BaseModel):
    description: str
    priority: int = 1
    agent_type: str
    
    @validator('description')
    def validate_description(cls, v):
        if len(v) > 1000:
            raise ValueError('Description too long')
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()
    
    @validator('priority')
    def validate_priority(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Priority must be between 1 and 5')
        return v
```

## 🔐 **Data Protection**

### **Encryption at Rest**
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class EncryptionManager:
    def __init__(self, password: str):
        self.password = password.encode()
        self.salt = b'amas_salt_2024'
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
    
    def _derive_key(self) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password))
    
    def encrypt_data(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### **Windows DPAPI Integration**
```python
import win32crypt
import win32con

class WindowsDPAPI:
    @staticmethod
    def protect_data(data: bytes) -> bytes:
        return win32crypt.CryptProtectData(
            data, 
            None, 
            None, 
            None, 
            None, 
            win32con.CRYPTPROTECT_UI_FORBIDDEN
        )
    
    @staticmethod
    def unprotect_data(protected_data: bytes) -> bytes:
        return win32crypt.CryptUnprotectData(
            protected_data, 
            None, 
            None, 
            None, 
            win32con.CRYPTPROTECT_UI_FORBIDDEN
        )[1]
```

## 📊 **Audit & Compliance**

### **Tamper-Evident Logging**
```python
import hashlib
import hmac
import json
from datetime import datetime

class AuditLogger:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def log_event(self, event_type: str, user_id: str, details: dict):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details
        }
        
        # Create HMAC signature
        event_json = json.dumps(event, sort_keys=True)
        signature = hmac.new(
            self.secret_key, 
            event_json.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        event["signature"] = signature
        
        # Write to append-only log
        with open("logs/audit.log", "a") as f:
            f.write(json.dumps(event) + "\n")
    
    def verify_log_integrity(self):
        with open("logs/audit.log", "r") as f:
            for line in f:
                event = json.loads(line.strip())
                signature = event.pop("signature")
                event_json = json.dumps(event, sort_keys=True)
                expected_signature = hmac.new(
                    self.secret_key, 
                    event_json.encode(), 
                    hashlib.sha256
                ).hexdigest()
                
                if signature != expected_signature:
                    raise SecurityError("Log tampering detected")
```

## 🚨 **Security Monitoring**

### **Intrusion Detection**
```python
from collections import defaultdict, deque
import time

class IntrusionDetectionSystem:
    def __init__(self):
        self.failed_attempts = defaultdict(deque)
        self.request_rates = defaultdict(deque)
        self.max_failed_logins = 5
        self.max_requests_per_minute = 60
    
    def check_failed_login(self, ip_address: str) -> bool:
        now = time.time()
        # Clean old entries
        while (self.failed_attempts[ip_address] and 
               now - self.failed_attempts[ip_address][0] > 300):
            self.failed_attempts[ip_address].popleft()
        
        self.failed_attempts[ip_address].append(now)
        
        if len(self.failed_attempts[ip_address]) >= self.max_failed_logins:
            self.block_ip(ip_address, "Excessive failed logins")
            return True
        return False
    
    def check_request_rate(self, ip_address: str) -> bool:
        now = time.time()
        # Clean old entries
        while (self.request_rates[ip_address] and 
               now - self.request_rates[ip_address][0] > 60):
            self.request_rates[ip_address].popleft()
        
        self.request_rates[ip_address].append(now)
        
        if len(self.request_rates[ip_address]) > self.max_requests_per_minute:
            self.block_ip(ip_address, "Rate limit exceeded")
            return True
        return False
```

## 🔧 **Security Scripts**

### **Security Configuration Script**
```powershell
# security/scripts/configure_security.ps1
param(
    [Switch]$EnableFirewall,
    [Switch]$EnableBitLocker,
    [Switch]$ConfigureUAC,
    [Switch]$All
)

if ($All -or $EnableFirewall) {
    Write-Host "Configuring Windows Firewall..." -ForegroundColor Green
    .\configure_firewall.ps1
}

if ($All -or $EnableBitLocker) {
    Write-Host "Enabling BitLocker..." -ForegroundColor Green
    .\enable_bitlocker.ps1
}

if ($All -or $ConfigureUAC) {
    Write-Host "Configuring UAC..." -ForegroundColor Green
    .\configure_uac.ps1
}

Write-Host "Security configuration completed!" -ForegroundColor Green
```

### **Security Audit Script**
```powershell
# security/scripts/security_audit.ps1
Write-Host "=== AMAS Security Audit ===" -ForegroundColor Cyan

# Check firewall status
$firewall = Get-NetFirewallProfile
Write-Host "Firewall Status: $($firewall.State)" -ForegroundColor White

# Check BitLocker status
$bitlocker = Get-BitLockerVolume -MountPoint "C:"
Write-Host "BitLocker Status: $($bitlocker.VolumeStatus)" -ForegroundColor White

# Check UAC status
$uac = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA"
Write-Host "UAC Status: $($uac.EnableLUA)" -ForegroundColor White

# Check Windows Defender status
$defender = Get-MpComputerStatus
Write-Host "Windows Defender: $($defender.RealTimeProtectionEnabled)" -ForegroundColor White

Write-Host "=== Security Audit Complete ===" -ForegroundColor Cyan
```

## 📋 **Security Checklist**

### **Pre-Deployment**
- [ ] UAC enabled at highest level
- [ ] Windows Defender configured
- [ ] Firewall rules configured
- [ ] BitLocker enabled
- [ ] Strong passwords set
- [ ] JWT secrets generated
- [ ] Encryption keys created
- [ ] Audit logging enabled

### **Post-Deployment**
- [ ] All services running with non-root users
- [ ] Network segmentation active
- [ ] SSL/TLS certificates installed
- [ ] Rate limiting configured
- [ ] Input validation active
- [ ] Security monitoring enabled
- [ ] Backup encryption configured
- [ ] Incident response procedures tested

## 🚨 **Incident Response**

### **Security Incident Response Plan**
1. **Detection**: Automated monitoring alerts
2. **Assessment**: Determine severity and scope
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat and vulnerabilities
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Update security measures

### **Emergency Procedures**
```powershell
# Emergency shutdown
.\scripts\emergency_shutdown.ps1

# Isolate system
.\scripts\isolate_system.ps1

# Backup critical data
.\scripts\emergency_backup.ps1
```

---

**🔐 Security is not a feature, it's a fundamental requirement. This guide ensures AMAS operates with enterprise-grade security from day one.**
