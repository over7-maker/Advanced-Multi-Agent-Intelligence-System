# Issue #3: Mask API Keys in Logs

## Priority: High (Security Fix - Week 1)
## Labels: `security`, `logging`, `api-keys`, `critical`

## Description

Implement comprehensive API key masking in all logs, error messages, and debug output to prevent credential exposure and maintain security best practices.

## Current Security Issues Identified

### 1. API Key Exposure in Logs
- **Location**: `src/amas/services/llm_service.py`
- **Issue**: API keys logged in debug messages and error responses
- **Risk**: Credential exposure in log files

### 2. Configuration Logging
- **Location**: `src/amas/config/settings.py`
- **Issue**: Configuration values including API keys logged without masking
- **Risk**: Sensitive data exposure in configuration logs

### 3. Error Message Exposure
- **Location**: Multiple services
- **Issue**: API keys included in error messages and stack traces
- **Risk**: Credential exposure in error logs

### 4. Debug Output
- **Location**: Various services and utilities
- **Issue**: Debug information includes unmasked API keys
- **Risk**: Credential exposure in debug logs

## Implementation Plan

### Phase 1: Core Logging Security (Days 1-2)
1. **Create Logging Security Module**
   ```python
   # src/amas/utils/logging_security.py
   - API key masking functions
   - Sensitive data detection
   - Log sanitization utilities
   - Secure logging formatters
   ```

2. **Implement API Key Masking**
   - Create regex patterns for API key detection
   - Implement masking functions for different key formats
   - Add secure logging formatters

### Phase 2: Service Integration (Days 3-4)
1. **Update All Services**
   - Replace direct API key logging with masked versions
   - Update error handling to mask sensitive data
   - Implement secure debug output

2. **Configuration Security**
   - Mask API keys in configuration logging
   - Implement secure configuration display
   - Add configuration validation logging

### Phase 3: Advanced Security (Days 5-7)
1. **Comprehensive Data Masking**
   - Implement pattern-based sensitive data detection
   - Add custom masking for different data types
   - Implement secure audit logging

2. **Log Analysis and Monitoring**
   - Add log analysis for sensitive data exposure
   - Implement alerting for potential credential leaks
   - Add log integrity checking

## Technical Requirements

### API Key Masking Patterns
```python
# Common API key patterns to mask
API_KEY_PATTERNS = [
    r'sk-[a-zA-Z0-9]{20,}',  # OpenAI format
    r'[a-zA-Z0-9]{32,}',     # Generic API keys
    r'Bearer\s+[a-zA-Z0-9_-]+',  # Bearer tokens
    r'Authorization:\s*[a-zA-Z0-9_-]+',  # Auth headers
]

# Masking configuration
MASK_CHAR = '*'
MASK_LENGTH = 8
SHOW_FIRST = 4
SHOW_LAST = 4
```

### Secure Logging Implementation
```python
def mask_api_key(api_key: str) -> str:
    """Mask API key while preserving some characters for debugging"""
    if not api_key or len(api_key) < 8:
        return '*' * 8
    
    first_part = api_key[:SHOW_FIRST]
    last_part = api_key[-SHOW_LAST:]
    middle_part = '*' * (len(api_key) - SHOW_FIRST - SHOW_LAST)
    
    return f"{first_part}{middle_part}{last_part}"
```

## Security Considerations

### Data Classification
- **Public**: Safe to log without masking
- **Internal**: Mask sensitive parts
- **Confidential**: Full masking required
- **Secret**: Never log, use placeholders

### Logging Levels
- **DEBUG**: Full masking, minimal sensitive data
- **INFO**: Standard masking, no sensitive data
- **WARNING**: Masked sensitive data only
- **ERROR**: Masked sensitive data, no credentials

### Audit Requirements
- Log all access to sensitive data
- Monitor for potential credential exposure
- Alert on suspicious logging patterns

## Implementation Details

### 1. Logging Security Module
```python
# src/amas/utils/logging_security.py
import re
import logging
from typing import Any, Dict, List, Optional

class SecureLogger:
    def __init__(self):
        self.sensitive_patterns = [
            r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)',
            r'bearer\s+([a-zA-Z0-9_-]+)',
            r'authorization:\s*([a-zA-Z0-9_-]+)',
            r'password["\']?\s*[:=]\s*["\']?([^"\']+)',
        ]
    
    def mask_sensitive_data(self, message: str) -> str:
        """Mask sensitive data in log messages"""
        masked_message = message
        for pattern in self.sensitive_patterns:
            masked_message = re.sub(pattern, self._mask_match, masked_message, flags=re.IGNORECASE)
        return masked_message
    
    def _mask_match(self, match) -> str:
        """Mask a matched sensitive data pattern"""
        # Implementation details...
```

### 2. Service Integration
```python
# Update all services to use secure logging
from amas.utils.logging_security import SecureLogger

class LLMService:
    def __init__(self, config):
        self.secure_logger = SecureLogger()
        self.api_key = config.get('api_key')
    
    async def _log_api_call(self, endpoint: str, response: dict):
        # Mask API key in logs
        safe_config = self.secure_logger.mask_config({'api_key': self.api_key})
        logger.info(f"API call to {endpoint} with config: {safe_config}")
```

## Testing Requirements

### Unit Tests
- Test API key masking with various formats
- Test sensitive data detection
- Test log sanitization functions
- Test edge cases and boundary conditions

### Security Tests
- Test with real API keys (in test environment)
- Test log output for credential exposure
- Test error message masking
- Test debug output security

### Integration Tests
- Test logging across all services
- Test configuration logging security
- Test error handling with masked data
- Test audit log security

## Acceptance Criteria

- [ ] All API keys are masked in logs
- [ ] Error messages don't expose credentials
- [ ] Debug output is secure
- [ ] Configuration logging is safe
- [ ] Audit logs are comprehensive
- [ ] Security tests pass
- [ ] Performance impact is minimal

## Files to Modify

### Core Files
- `src/amas/utils/logging_security.py` (new)
- `src/amas/config/settings.py`
- `src/amas/main.py`

### Service Files
- `src/amas/services/llm_service.py`
- `src/amas/services/vector_service.py`
- `src/amas/services/knowledge_graph_service.py`
- `src/amas/services/security_service.py`
- `src/amas/services/monitoring_service.py`
- `src/amas/services/universal_ai_manager.py`
- `src/amas/services/ultimate_fallback_system.py`

### Configuration Files
- All configuration files with API keys
- Environment variable handling
- Logging configuration

### Test Files
- `tests/unit/test_logging_security.py` (new)
- `tests/security/test_credential_exposure.py` (new)
- `tests/integration/test_secure_logging.py` (new)

## Configuration Updates

### Logging Security Configuration
```yaml
# Add to amas_config.yaml
logging:
  security:
    enabled: true
    mask_api_keys: true
    mask_passwords: true
    mask_tokens: true
    sensitive_patterns:
      - "api[_-]?key"
      - "password"
      - "token"
      - "secret"
    mask_char: "*"
    show_first_chars: 4
    show_last_chars: 4
```

### Environment Variables
```bash
# Add to .env
AMAS_LOG_SECURITY_ENABLED=true
AMAS_MASK_SENSITIVE_DATA=true
AMAS_LOG_LEVEL=INFO
```

## Dependencies

### New Dependencies
```python
# Add to requirements.txt
# No new dependencies required - using standard library
```

## Related Issues

- Issue #1: Add input validation
- Issue #2: Implement path sanitization
- Issue #4: Refactor provider initialization

## Estimated Effort

- **Development**: 3-5 days
- **Testing**: 2-3 days
- **Security Review**: 1 day
- **Total**: 6-9 days

## Risk Assessment

- **Security Risk**: High (credential exposure)
- **Implementation Risk**: Low
- **Performance Impact**: Minimal
- **Breaking Changes**: None (backward compatible)

## Security Impact

### Before Implementation
- API keys exposed in logs
- Credential exposure in error messages
- Sensitive data in debug output
- Potential security breaches

### After Implementation
- Secure logging practices
- Masked sensitive data
- Protected credentials
- Comprehensive audit trail

## Examples

### Before (Insecure)
```python
logger.info(f"API call with key: {api_key}")
logger.error(f"Authentication failed with key: {api_key}")
```

### After (Secure)
```python
logger.info(f"API call with key: {mask_api_key(api_key)}")
logger.error(f"Authentication failed with key: {mask_api_key(api_key)}")
```

### Log Output Examples
```
# Before
INFO: API call with key: sk-1234567890abcdef1234567890abcdef

# After
INFO: API call with key: sk-12******cdef
```

---

**Assignee**: TBD
**Milestone**: Security Fixes (Week 1)
**Created**: [Current Date]
**Last Updated**: [Current Date]