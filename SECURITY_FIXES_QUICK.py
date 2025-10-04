#!/usr/bin/env python3
"""
Quick Security Fixes for Universal AI Manager
Addresses critical security concerns from code review
"""

import re
import os
from pathlib import Path
from typing import Optional

# ============================================================================
# 1. INPUT VALIDATION
# ============================================================================

def sanitize_prompt(prompt: str, max_length: int = 10000) -> str:
    """
    Sanitize user input prompt to prevent injection attacks
    
    Args:
        prompt: User-provided prompt
        max_length: Maximum allowed prompt length
        
    Returns:
        Sanitized prompt
        
    Raises:
        ValueError: If prompt is invalid
    """
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Prompt must be a non-empty string")
    
    # Remove control characters
    prompt = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', prompt)
    
    # Limit length
    if len(prompt) > max_length:
        raise ValueError(f"Prompt exceeds maximum length of {max_length}")
    
    return prompt.strip()


def validate_topic(topic: str) -> str:
    """
    Validate investigation topic for security
    
    Args:
        topic: Investigation topic
        
    Returns:
        Validated topic
        
    Raises:
        ValueError: If topic is invalid
    """
    if not topic or len(topic) > 500:
        raise ValueError("Topic must be between 1 and 500 characters")
    
    # Check for path traversal attempts
    dangerous_patterns = ['../', '..\\', '<script>', 'javascript:', 'file://']
    topic_lower = topic.lower()
    
    for pattern in dangerous_patterns:
        if pattern in topic_lower:
            raise ValueError(f"Invalid topic: contains prohibited pattern '{pattern}'")
    
    return topic.strip()


# ============================================================================
# 2. PATH SANITIZATION
# ============================================================================

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Allow only alphanumeric, dash, underscore, and dot
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Remove leading dots
    safe_filename = safe_filename.lstrip('.')
    
    # Ensure it's not empty
    if not safe_filename:
        safe_filename = 'file'
    
    return safe_filename


def safe_path_join(base_dir: str, filename: str) -> str:
    """
    Safely join paths to prevent directory traversal
    
    Args:
        base_dir: Base directory
        filename: Filename to join
        
    Returns:
        Safe absolute path
        
    Raises:
        ValueError: If path escapes base directory
    """
    # Sanitize filename
    safe_filename = sanitize_filename(filename)
    
    # Create absolute paths
    base_abs = os.path.abspath(base_dir)
    target_abs = os.path.abspath(os.path.join(base_dir, safe_filename))
    
    # Ensure target is within base directory
    if not target_abs.startswith(base_abs):
        raise ValueError(f"Path traversal attempt detected: {filename}")
    
    return target_abs


# ============================================================================
# 3. API KEY MASKING
# ============================================================================

def mask_api_key(api_key: Optional[str], visible_chars: int = 4) -> str:
    """
    Mask API key for safe logging
    
    Args:
        api_key: API key to mask
        visible_chars: Number of characters to show at end
        
    Returns:
        Masked API key
    """
    if not api_key:
        return "NOT_SET"
    
    if len(api_key) <= visible_chars:
        return "*" * len(api_key)
    
    return "*" * (len(api_key) - visible_chars) + api_key[-visible_chars:]


def sanitize_error_message(error: str, max_length: int = 200) -> str:
    """
    Sanitize error message to prevent information leakage
    
    Args:
        error: Original error message
        max_length: Maximum error message length
        
    Returns:
        Sanitized error message
    """
    # Truncate long messages
    if len(error) > max_length:
        error = error[:max_length] + "..."
    
    # Remove potential file paths
    error = re.sub(r'(/[a-zA-Z0-9_/.-]+)', '[PATH]', error)
    error = re.sub(r'([A-Z]:\\[a-zA-Z0-9_\\.-]+)', '[PATH]', error)
    
    # Remove API keys (common patterns)
    error = re.sub(r'(sk-[a-zA-Z0-9]{48})', '[API_KEY]', error)
    error = re.sub(r'(Bearer\s+[a-zA-Z0-9_-]+)', 'Bearer [TOKEN]', error)
    
    return error


# ============================================================================
# 4. SECURE FILE OPERATIONS
# ============================================================================

def create_secure_directory(path: str) -> str:
    """
    Create directory with secure permissions
    
    Args:
        path: Directory path
        
    Returns:
        Absolute directory path
    """
    # Ensure path is safe
    abs_path = os.path.abspath(path)
    
    # Create directory with restricted permissions (0o755)
    os.makedirs(abs_path, mode=0o755, exist_ok=True)
    
    return abs_path


def write_secure_file(content: str, base_dir: str, filename: str) -> str:
    """
    Write file with secure path handling
    
    Args:
        content: File content
        base_dir: Base directory
        filename: Filename
        
    Returns:
        Path to written file
    """
    # Create secure directory
    secure_dir = create_secure_directory(base_dir)
    
    # Get safe file path
    file_path = safe_path_join(secure_dir, filename)
    
    # Write file with restricted permissions
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Set file permissions (0o644 - rw-r--r--)
    os.chmod(file_path, 0o644)
    
    return file_path


# ============================================================================
# 5. USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example 1: Input validation
    try:
        safe_prompt = sanitize_prompt("Analyze this security threat")
        print(f"✅ Safe prompt: {safe_prompt}")
    except ValueError as e:
        print(f"❌ Invalid prompt: {e}")
    
    # Example 2: Path sanitization
    safe_path = safe_path_join("artifacts", "report.md")
    print(f"✅ Safe path: {safe_path}")
    
    # Example 3: API key masking
    masked = mask_api_key("sk-1234567890abcdef1234567890abcdef")
    print(f"✅ Masked key: {masked}")
    
    # Example 4: Error sanitization
    error = "Failed to connect to /home/user/secret/api.key with token sk-abc123"
    safe_error = sanitize_error_message(error)
    print(f"✅ Safe error: {safe_error}")
    
    # Example 5: Secure file write
    report_path = write_secure_file(
        content="Test report",
        base_dir="artifacts",
        filename="../../../etc/passwd"  # Attempt directory traversal
    )
    print(f"✅ File saved to: {report_path}")
