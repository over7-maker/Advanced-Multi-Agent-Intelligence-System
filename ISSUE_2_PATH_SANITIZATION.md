# Issue #2: Implement Path Sanitization

## Priority: High (Security Fix - Week 1)
## Labels: `security`, `path-sanitization`, `critical`

## Description

Implement comprehensive path sanitization for all file operations and data access to prevent directory traversal attacks, unauthorized file access, and system compromise.

## Current Security Issues Identified

### 1. File Path Operations
- **Location**: Multiple services and utilities
- **Issue**: File paths not sanitized before operations
- **Risk**: Directory traversal attacks (`../../../etc/passwd`)

### 2. Data Directory Access
- **Location**: `src/amas/config/settings.py` (data_dir, logs_dir, models_dir)
- **Issue**: Directory paths not validated
- **Risk**: Unauthorized access to sensitive directories

### 3. Model File Access
- **Location**: LLM and vector services
- **Issue**: Model file paths not sanitized
- **Risk**: Loading malicious model files

### 4. Log File Operations
- **Location**: Logging configuration
- **Issue**: Log file paths not validated
- **Risk**: Log injection, unauthorized log access

## Implementation Plan

### Phase 1: Core Path Sanitization (Days 1-2)
1. **Create Path Sanitization Module**
   ```python
   # src/amas/utils/path_sanitizer.py
   - Safe path resolution
   - Directory traversal prevention
   - File extension validation
   - Path length limits
   ```

2. **Path Validation Functions**
   - `sanitize_path()` - Clean and validate paths
   - `resolve_safe_path()` - Resolve paths safely
   - `validate_file_extension()` - Check allowed extensions
   - `check_path_permissions()` - Verify access permissions

### Phase 2: Service Integration (Days 3-4)
1. **File Service Integration**
   - Update all file operations to use sanitized paths
   - Implement safe file reading/writing
   - Add path validation to data access

2. **Configuration Path Validation**
   - Validate all directory configurations
   - Ensure paths are within allowed directories
   - Implement path restrictions

### Phase 3: Advanced Security (Days 5-7)
1. **Sandboxed File Operations**
   - Implement chroot-like restrictions
   - Add file access monitoring
   - Implement file quarantine for suspicious files

2. **Audit and Logging**
   - Log all file access attempts
   - Monitor for suspicious path patterns
   - Alert on potential attacks

## Technical Requirements

### Path Sanitization Rules
```python
# Security constraints
MAX_PATH_LENGTH = 4096
ALLOWED_BASE_DIRS = ['/app/data', '/app/logs', '/app/models']
FORBIDDEN_PATTERNS = ['../', '..\\', '~', '$HOME', '%USERPROFILE%']
ALLOWED_EXTENSIONS = ['.txt', '.json', '.csv', '.pdf', '.md', '.log']
```

### Safe Path Resolution
```python
def sanitize_path(user_path: str, base_dir: str) -> str:
    """
    Sanitize and resolve file paths safely
    - Remove directory traversal attempts
    - Validate against allowed base directories
    - Check file extensions
    - Ensure path length limits
    """
```

## Security Considerations

### Directory Traversal Prevention
- Resolve all paths relative to safe base directories
- Block any path containing `..` or similar traversal patterns
- Implement strict path validation

### File Access Control
- Restrict file operations to designated directories
- Implement file type restrictions
- Add file size limits

### Audit Trail
- Log all file access attempts
- Monitor for suspicious patterns
- Alert on potential security violations

## Implementation Details

### 1. Path Sanitization Module
```python
# src/amas/utils/path_sanitizer.py
import os
import re
from pathlib import Path
from typing import List, Optional

class PathSanitizer:
    def __init__(self, allowed_base_dirs: List[str]):
        self.allowed_base_dirs = [Path(d).resolve() for d in allowed_base_dirs]
        self.forbidden_patterns = [
            r'\.\./', r'\.\.\\', r'~', r'\$HOME', r'%USERPROFILE%'
        ]
    
    def sanitize_path(self, user_path: str, base_dir: str) -> Optional[Path]:
        """Sanitize and validate file path"""
        # Implementation details...
```

### 2. Service Integration
```python
# Update all services to use path sanitization
from amas.utils.path_sanitizer import PathSanitizer

class LLMService:
    def __init__(self, config):
        self.path_sanitizer = PathSanitizer(config.allowed_dirs)
    
    async def load_model(self, model_path: str):
        safe_path = self.path_sanitizer.sanitize_path(model_path, self.models_dir)
        if not safe_path:
            raise ValueError("Invalid model path")
        # Continue with safe path...
```

## Testing Requirements

### Unit Tests
- Test path sanitization with various inputs
- Test directory traversal prevention
- Test file extension validation
- Test path length limits

### Security Tests
- Test with malicious path inputs
- Test directory traversal attempts
- Test with various encoding schemes
- Test with symbolic links

### Integration Tests
- Test file operations with sanitized paths
- Test configuration loading with path validation
- Test service initialization with path restrictions

## Acceptance Criteria

- [ ] All file operations use sanitized paths
- [ ] Directory traversal attacks are prevented
- [ ] File access is restricted to allowed directories
- [ ] Path validation is comprehensive
- [ ] Security tests pass
- [ ] Performance impact is minimal

## Files to Modify

### Core Files
- `src/amas/utils/path_sanitizer.py` (new)
- `src/amas/config/settings.py`
- `src/amas/main.py`

### Service Files
- `src/amas/services/llm_service.py`
- `src/amas/services/vector_service.py`
- `src/amas/services/knowledge_graph_service.py`
- `src/amas/services/security_service.py`
- `src/amas/services/monitoring_service.py`

### Utility Files
- All files with file operations
- Configuration files
- Logging setup

### Test Files
- `tests/unit/test_path_sanitizer.py` (new)
- `tests/security/test_path_traversal.py` (new)
- `tests/integration/test_file_operations.py` (new)

## Configuration Updates

### Path Restrictions
```yaml
# Add to amas_config.yaml
security:
  path_sanitization:
    enabled: true
    allowed_base_dirs:
      - "/app/data"
      - "/app/logs"
      - "/app/models"
    forbidden_patterns:
      - "../"
      - "..\\"
      - "~"
    max_path_length: 4096
    allowed_extensions:
      - ".txt"
      - ".json"
      - ".csv"
      - ".pdf"
      - ".md"
      - ".log"
```

### Environment Variables
```bash
# Add to .env
AMAS_PATH_SANITIZATION_ENABLED=true
AMAS_ALLOWED_BASE_DIRS="/app/data,/app/logs,/app/models"
AMAS_MAX_PATH_LENGTH=4096
```

## Dependencies

### New Dependencies
```python
# Add to requirements.txt
pathlib2>=2.3.7  # Enhanced path operations
```

## Related Issues

- Issue #1: Add input validation
- Issue #3: Mask API keys in logs
- Issue #4: Refactor provider initialization

## Estimated Effort

- **Development**: 5-7 days
- **Testing**: 2-3 days
- **Security Review**: 1 day
- **Total**: 8-11 days

## Risk Assessment

- **Security Risk**: High (without sanitization)
- **Implementation Risk**: Medium
- **Performance Impact**: Low
- **Breaking Changes**: Minimal (backward compatible)

## Security Impact

### Before Implementation
- Directory traversal vulnerabilities
- Unauthorized file access
- Potential system compromise
- Data exfiltration risks

### After Implementation
- Secure file operations
- Restricted directory access
- Comprehensive path validation
- Audit trail for file access

---

**Assignee**: TBD
**Milestone**: Security Fixes (Week 1)
**Created**: [Current Date]
**Last Updated**: [Current Date]