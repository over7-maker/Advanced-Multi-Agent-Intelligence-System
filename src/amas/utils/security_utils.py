"""Security utilities for AMAS system"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List

def validate_file_path(file_path: str, allowed_dirs: List[str] = None) -> str:
    """Validate and sanitize file paths to prevent traversal attacks"""
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    # Remove any dangerous characters
    safe_path = os.path.normpath(file_path)
    
    # Check for path traversal attempts
    if '..' in safe_path or safe_path.startswith('/'):
        raise ValueError(f"Dangerous path detected: {file_path}")
    
    # Validate against allowed directories if specified
    if allowed_dirs:
        path_obj = Path(safe_path)
        if not any(str(path_obj).startswith(allowed_dir) for allowed_dir in allowed_dirs):
            raise ValueError(f"Path not in allowed directories: {file_path}")
    
    return safe_path

def sanitize_user_input(user_input: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not isinstance(user_input, str):
        raise TypeError("Input must be a string")
    
    # Limit length
    if len(user_input) > max_length:
        user_input = user_input[:max_length]
    
    # Remove dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',               # XSS
        r'on\w+\s*=',                # Event handlers
        r'eval\s*\(',                # Code execution
        r'exec\s*\(',                # Code execution
        r'__import__',               # Dynamic imports
    ]
    
    for pattern in dangerous_patterns:
        user_input = re.sub(pattern, '', user_input, flags=re.IGNORECASE)
    
    return user_input.strip()

def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic validation - should be at least 20 characters
    if len(api_key) < 20:
        return False
    
    # Should contain only alphanumeric characters and common symbols
    if not re.match(r'^[a-zA-Z0-9_.-]+$', api_key):
        return False
    
    return True

def secure_random_string(length: int = 32) -> str:
    """Generate a secure random string"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_sensitive_data(data: str, salt: str = None) -> str:
    """Securely hash sensitive data using SHA-256"""
    import hashlib
    import secrets
    
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Use SHA-256 with salt
    return hashlib.sha256((data + salt).encode()).hexdigest()
