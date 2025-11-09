# 📝 Audit Logging Guide

## Overview

AMAS implements comprehensive audit logging with automatic PII (Personally Identifiable Information) redaction, structured JSON logging, and compliance-ready audit trails. This guide covers the complete audit logging system implemented in PR-B.

---

## Table of Contents

1. [Audit Logging Architecture](#audit-logging-architecture)
2. [Features](#features)
3. [PII Redaction](#pii-redaction)
4. [Event Types](#event-types)
5. [Log Format](#log-format)
6. [Configuration](#configuration)
7. [Integration](#integration)
8. [Querying Audit Logs](#querying-audit-logs)
9. [Compliance](#compliance)
10. [Troubleshooting](#troubleshooting)

---

## Audit Logging Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Application                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Endpoints  │  │  Middleware  │  │  Services    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                  │
│                            ▼                                  │
│  ┌──────────────────────────────────────────────────────┐     │
│  │         AuditLoggingMiddleware                       │     │
│  │  - Captures all HTTP requests                        │     │
│  │  - Extracts request context                          │     │
│  │  - Adds to audit queue                               │     │
│  └──────────────────┬───────────────────────────────────┘     │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐     │
│  │              AuditLogger                             │     │
│  │  ┌──────────────────────────────────────────────┐   │     │
│  │  │  PIIRedactor                                  │   │     │
│  │  │  - Detects sensitive data                     │   │     │
│  │  │  - Redacts PII patterns                       │   │     │
│  │  └──────────────────────────────────────────────┘   │     │
│  │                                                      │     │
│  │  ┌──────────────────────────────────────────────┐   │     │
│  │  │  Buffered Writer                             │   │     │
│  │  │  - Batches log entries                        │   │     │
│  │  │  - Async writes                               │   │     │
│  │  │  - Automatic flushing                         │   │     │
│  │  └──────────────────────────────────────────────┘   │     │
│  └──────────────────┬───────────────────────────────────┘     │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐     │
│  │         Audit Log File (JSONL)                      │     │
│  │  logs/audit.jsonl                                    │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

**Location:** `src/amas/api/main.py`

- **Line 74:** `AuditLoggingMiddleware` added to middleware stack
- **Lines 160-171:** Audit logger initialization in `startup_event()`
- **Lines 307-314:** Audit logger shutdown in `shutdown_event()`

---

## Features

### 1. Automatic Request Logging

All HTTP requests are automatically logged with:
- Request method, path, and query parameters
- Request headers (sanitized)
- Request body (sanitized)
- Response status code
- Response time
- User context (from JWT token)
- IP address
- Timestamp

### 2. PII Redaction

Sensitive data is automatically detected and redacted:
- Email addresses → `[REDACTED:email]`
- Social Security Numbers → `[REDACTED:ssn]`
- Phone numbers → `[REDACTED:phone]`
- Credit card numbers → `[REDACTED:credit_card]`
- API keys → `[REDACTED:api_key]`
- IP addresses (optional) → `[REDACTED:ip_address]`

### 3. Structured JSON Logging

All logs are in JSON Lines (JSONL) format for easy parsing:

```json
{"timestamp": "2025-01-15T10:30:45.123Z", "event_type": "api_request", "method": "POST", "path": "/api/v1/tasks", "status": 200, "user_id": "user123", "ip": "192.168.1.100", "duration_ms": 45}
```

### 4. Buffered Async Writes

Logs are buffered and written asynchronously for performance:
- **Buffer Size:** 100 events (configurable)
- **Flush Interval:** 30 seconds (configurable)
- **Automatic Flush:** On buffer full or shutdown

### 5. Event Classification

Events are classified by type for easy filtering:
- `authentication` - Login, logout, token validation
- `authorization` - Permission checks, policy evaluations
- `api_request` - HTTP API requests
- `agent_execution` - Agent task execution
- `tool_usage` - Tool/API usage
- `data_access` - Database/file access
- `configuration_change` - Config updates
- `security_violation` - Security policy violations
- `system_event` - System-level events

---

## PII Redaction

### Redaction Patterns

**Location:** `src/amas/security/audit/audit_logger.py`

The `PIIRedactor` class automatically detects and redacts:

1. **Email Addresses**
   - Pattern: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
   - Example: `user@example.com` → `[REDACTED:email]`

2. **Social Security Numbers**
   - Pattern: `\b\d{3}-\d{2}-\d{4}\b`
   - Example: `123-45-6789` → `[REDACTED:ssn]`

3. **Phone Numbers**
   - Pattern: `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`
   - Example: `555-123-4567` → `[REDACTED:phone]`

4. **Credit Card Numbers**
   - Pattern: `\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b`
   - Example: `4532-1234-5678-9010` → `[REDACTED:credit_card]`

5. **API Keys**
   - Pattern: `(api[_-]?key|apikey|secret[_-]?key)\s*[:=]\s*['"]?([a-zA-Z0-9_-]{20,})['"]?`
   - Example: `api_key: abc123xyz789` → `api_key: [REDACTED:api_key]`

6. **IP Addresses** (optional)
   - Pattern: `\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b`
   - Example: `192.168.1.100` → `[REDACTED:ip_address]`

### Custom Redaction Patterns

You can add custom patterns in `config/security_config.yaml`:

```yaml
audit:
  redaction_patterns:
    - email
    - ssn
    - phone
    - credit_card
    - api_key
    - ip_address
    - custom_pattern:  # Add your own
        name: "employee_id"
        pattern: "EMP-\\d{6}"
```

### Redaction Example

**Before:**
```json
{
  "user_email": "john.doe@example.com",
  "phone": "555-123-4567",
  "ssn": "123-45-6789",
  "api_key": "sk_live_abc123xyz789"
}
```

**After:**
```json
{
  "user_email": "[REDACTED:email]",
  "phone": "[REDACTED:phone]",
  "ssn": "[REDACTED:ssn]",
  "api_key": "[REDACTED:api_key]"
}
```

---

## Event Types

### Authentication Events

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "event_type": "authentication",
  "action": "login",
  "status": "success",
  "user_id": "user123",
  "ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "metadata": {
    "auth_method": "oidc",
    "provider": "auth0"
  }
}
```

### Authorization Events

```json
{
  "timestamp": "2025-01-15T10:30:46.123Z",
  "event_type": "authorization",
  "action": "policy_evaluation",
  "status": "denied",
  "user_id": "user123",
  "resource": "vulnerability_scanner",
  "policy": "agent.access",
  "reason": "Insufficient role permissions"
}
```

### API Request Events

```json
{
  "timestamp": "2025-01-15T10:30:47.123Z",
  "event_type": "api_request",
  "method": "POST",
  "path": "/api/v1/tasks",
  "status": 200,
  "user_id": "user123",
  "ip": "192.168.1.100",
  "duration_ms": 45,
  "request_size": 1024,
  "response_size": 2048
}
```

### Agent Execution Events

```json
{
  "timestamp": "2025-01-15T10:30:48.123Z",
  "event_type": "agent_execution",
  "action": "task_execution",
  "status": "success",
  "agent_id": "agent-456",
  "agent_role": "security_analyst",
  "task_id": "task-789",
  "task_type": "vulnerability_scan",
  "duration_ms": 5000
}
```

---

## Log Format

### JSON Lines Format

Each log entry is a single JSON object on one line:

```jsonl
{"timestamp": "2025-01-15T10:30:45.123Z", "event_type": "api_request", "method": "GET", "path": "/api/v1/health", "status": 200, "ip": "192.168.1.100", "duration_ms": 5}
{"timestamp": "2025-01-15T10:30:46.123Z", "event_type": "authentication", "action": "login", "status": "success", "user_id": "user123", "ip": "192.168.1.100"}
{"timestamp": "2025-01-15T10:30:47.123Z", "event_type": "api_request", "method": "POST", "path": "/api/v1/tasks", "status": 201, "user_id": "user123", "ip": "192.168.1.100", "duration_ms": 45}
```

### Common Fields

All log entries include:

- `timestamp` - ISO 8601 timestamp
- `event_type` - Type of event (see Event Types)
- `status` - Status (`success`, `failure`, `denied`, etc.)
- `ip` - Client IP address (may be redacted)
- `user_id` - User identifier (from JWT token)
- `duration_ms` - Duration in milliseconds (for timed events)

---

## Configuration

### Configuration File

**File:** `config/security_config.yaml`

```yaml
audit:
  # Log File Settings
  log_file: "${AUDIT_LOG_FILE:-logs/audit.jsonl}"
  buffer_size: 100  # Events to buffer before flushing
  flush_interval: 30  # Seconds between automatic flushes
  backup_count: 5  # Number of rotated log files to keep
  
  # PII Protection
  redact_sensitive: true
  redaction_patterns:
    - email
    - ssn
    - phone
    - credit_card
    - api_key
    - ip_address
  
  # Event Types to Log
  log_event_types:
    - authentication
    - authorization
    - agent_execution
    - tool_usage
    - data_access
    - configuration_change
    - security_violation
    - system_event
  
  # Retention
  retention_days: 90  # Days to retain audit logs
```

### Environment Variables

```bash
# Audit Log File Path
export AUDIT_LOG_FILE="logs/audit.jsonl"

# Buffer Configuration
export AUDIT_BUFFER_SIZE="100"
export AUDIT_FLUSH_INTERVAL="30"

# PII Redaction
export AUDIT_REDACT_PII="true"

# Retention
export AUDIT_RETENTION_DAYS="90"
```

---

## Integration

### Automatic Integration

The audit logger is automatically integrated via middleware:

**Location:** `src/amas/api/main.py`

```python
# Line 74: Middleware added
app.add_middleware(AuditLoggingMiddleware)

# Lines 160-171: Initialization
initialize_audit_logger(
    log_file=audit_log_file,
    buffer_size=int(os.getenv("AUDIT_BUFFER_SIZE", "100")),
    enable_redaction=os.getenv("AUDIT_REDACT_PII", "true").lower() == "true"
)
```

### Manual Logging

You can also log custom events:

```python
from amas.security.audit.audit_logger import get_audit_logger

audit_logger = get_audit_logger()

# Log custom event
audit_logger.log_event(
    event_type="custom_event",
    action="data_export",
    status="success",
    user_id="user123",
    metadata={
        "export_type": "csv",
        "record_count": 1000
    }
)
```

---

## Querying Audit Logs

### Using jq

```bash
# Find all authentication events
cat logs/audit.jsonl | jq 'select(.event_type == "authentication")'

# Find failed authorization attempts
cat logs/audit.jsonl | jq 'select(.event_type == "authorization" and .status == "denied")'

# Find events for a specific user
cat logs/audit.jsonl | jq 'select(.user_id == "user123")'

# Find events in time range
cat logs/audit.jsonl | jq 'select(.timestamp >= "2025-01-15T00:00:00Z" and .timestamp <= "2025-01-15T23:59:59Z")'
```

### Using Python

```python
import json

# Read audit logs
with open('logs/audit.jsonl', 'r') as f:
    for line in f:
        event = json.loads(line)
        if event['event_type'] == 'authentication':
            print(event)

# Search for specific events
def search_audit_logs(log_file, event_type=None, user_id=None, start_time=None, end_time=None):
    results = []
    with open(log_file, 'r') as f:
        for line in f:
            event = json.loads(line)
            
            if event_type and event['event_type'] != event_type:
                continue
            if user_id and event.get('user_id') != user_id:
                continue
            if start_time and event['timestamp'] < start_time:
                continue
            if end_time and event['timestamp'] > end_time:
                continue
            
            results.append(event)
    return results

# Usage
events = search_audit_logs(
    'logs/audit.jsonl',
    event_type='authorization',
    user_id='user123',
    start_time='2025-01-15T00:00:00Z',
    end_time='2025-01-15T23:59:59Z'
)
```

### Using Elasticsearch (if integrated)

```bash
# Search authentication events
curl -X GET "http://localhost:9200/audit-logs/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "match": {
        "event_type": "authentication"
      }
    }
  }'
```

---

## Compliance

### GDPR Compliance

- **Right to Access:** Users can request their audit log data
- **Right to Erasure:** Audit logs can be anonymized (not deleted for compliance)
- **Data Minimization:** Only necessary data is logged
- **PII Protection:** Automatic redaction of sensitive data

### SOC 2 Compliance

- **Access Controls:** All access attempts logged
- **Change Management:** Configuration changes logged
- **Security Events:** Security violations logged
- **Audit Trail:** Immutable audit trail maintained

### HIPAA Compliance

- **PHI Protection:** Health information automatically redacted
- **Access Logging:** All PHI access logged
- **Audit Requirements:** 6-year retention (configurable)
- **Breach Detection:** Unauthorized access attempts logged

---

## Troubleshooting

### Logs Not Being Written

**Symptoms:** No audit log file created

**Solutions:**
```bash
# Check file permissions
ls -la logs/audit.jsonl

# Check directory exists
mkdir -p logs

# Check buffer flush
# Logs are buffered - wait up to flush_interval seconds
```

### High Memory Usage

**Symptoms:** Memory usage increasing

**Solutions:**
```yaml
# Reduce buffer size
audit:
  buffer_size: 50  # Reduce from 100
  flush_interval: 10  # Flush more frequently
```

### Missing Events

**Symptoms:** Some events not logged

**Solutions:**
```yaml
# Check event types configuration
audit:
  log_event_types:
    - authentication
    - authorization
    - api_request
    # Add missing event types
```

### PII Not Redacted

**Symptoms:** Sensitive data visible in logs

**Solutions:**
```yaml
# Enable redaction
audit:
  redact_sensitive: true
  redaction_patterns:
    - email
    - ssn
    # Add missing patterns
```

---

## Best Practices

1. **Regular Log Rotation:** Configure log rotation to prevent disk space issues
2. **Secure Storage:** Store audit logs in encrypted storage
3. **Access Control:** Limit access to audit logs to authorized personnel only
4. **Regular Review:** Review audit logs regularly for anomalies
5. **Backup:** Backup audit logs regularly for compliance
6. **Monitoring:** Set up alerts for security events in audit logs
7. **Retention:** Follow compliance requirements for log retention

---

## Additional Resources

- [Audit Logger Implementation](../../src/amas/security/audit/audit_logger.py)
- [PII Redactor Implementation](../../src/amas/security/audit/audit_logger.py#PIIRedactor)
- [Security Configuration](../../config/security_config.yaml)
- [GDPR Compliance Guide](https://gdpr.eu/)
- [SOC 2 Requirements](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report.html)

---

**Last Updated:** After PR-B Integration  
**Version:** 1.0.0  
**Status:** Production Ready
