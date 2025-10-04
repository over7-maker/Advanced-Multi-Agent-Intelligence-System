#!/usr/bin/env python3
"""
AI Security Utilities - Security and validation utilities for AI scripts
Part of the AI-Powered Project Upgrade System
"""

import os
import re
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urlparse
import json
import yaml

class AISecurityValidator:
    """Security validation utilities for AI scripts"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logging.getLogger(__name__)
        
        # Allowed file extensions for security
        self.allowed_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
            '.json', '.yaml', '.yml', '.md', '.txt', '.xml', '.sql',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd'
        }
        
        # Sensitive patterns to filter out
        self.sensitive_patterns = [
            r'password\s*=\s*[^\s\n]+',
            r'api[_-]?key\s*=\s*[^\s\n]+',
            r'secret\s*=\s*[^\s\n]+',
            r'token\s*=\s*[^\s\n]+',
            r'private[_-]?key\s*=\s*[^\s\n]+',
            r'credential\s*=\s*[^\s\n]+',
        ]
        
        # Maximum file sizes (in bytes)
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_total_size = 100 * 1024 * 1024  # 100MB
    
    def validate_path(self, path: Union[str, Path], allow_absolute: bool = False) -> Path:
        """Validate and sanitize file paths to prevent directory traversal"""
        try:
            path = Path(path)
            
            # Resolve the path
            if path.is_absolute():
                if not allow_absolute:
                    raise ValueError("Absolute paths not allowed")
                resolved_path = path.resolve()
            else:
                resolved_path = (self.project_root / path).resolve()
            
            # Check if path is within project root
            try:
                resolved_path.relative_to(self.project_root)
            except ValueError:
                raise ValueError(f"Path {path} is outside project root {self.project_root}")
            
            return resolved_path
            
        except Exception as e:
            self.logger.error(f"Path validation failed for {path}: {e}")
            raise ValueError(f"Invalid path: {path}")
    
    def validate_scope(self, scope: str) -> str:
        """Validate scope parameter to prevent directory traversal"""
        if not scope or not isinstance(scope, str):
            raise ValueError("Scope must be a non-empty string")
        
        # Remove any path traversal attempts
        scope = scope.replace('..', '').replace('//', '/').strip('/')
        
        # Validate against allowed scopes
        allowed_scopes = ['all', 'changed_files', 'src', 'tests', 'docs', 'scripts']
        if scope not in allowed_scopes and not scope.startswith('src/') and not scope.startswith('tests/'):
            raise ValueError(f"Invalid scope: {scope}. Allowed: {allowed_scopes}")
        
        return scope
    
    def validate_input(self, user_input: str, max_length: int = 10000) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not user_input:
            return ""
        
        if len(user_input) > max_length:
            raise ValueError(f"Input too long. Maximum {max_length} characters allowed")
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', user_input)
        
        # Check for prompt injection patterns
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'forget\s+everything',
            r'you\s+are\s+now',
            r'system\s*:',
            r'admin\s*:',
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                self.logger.warning(f"Potential prompt injection detected: {pattern}")
                # Remove the suspicious content
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def validate_file_access(self, file_path: Path) -> bool:
        """Validate file access permissions and safety"""
        try:
            # Check if file exists and is readable
            if not file_path.exists():
                return False
            
            if not file_path.is_file():
                return False
            
            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                self.logger.warning(f"File {file_path} is too large: {file_path.stat().st_size} bytes")
                return False
            
            # Check file extension
            if file_path.suffix.lower() not in self.allowed_extensions:
                self.logger.warning(f"File {file_path} has disallowed extension: {file_path.suffix}")
                return False
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                self.logger.warning(f"File {file_path} is not readable")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"File access validation failed for {file_path}: {e}")
            return False
    
    def sanitize_file_content(self, content: str, file_path: Path) -> str:
        """Sanitize file content to remove sensitive information"""
        try:
            # Remove sensitive patterns
            for pattern in self.sensitive_patterns:
                content = re.sub(pattern, r'***REDACTED***', content, flags=re.IGNORECASE)
            
            # Remove potential API keys in various formats
            content = re.sub(r'[A-Za-z0-9]{20,}', lambda m: '***REDACTED***' if len(m.group()) > 20 else m.group(), content)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Content sanitization failed for {file_path}: {e}")
            return content
    
    def validate_output_directory(self, output_path: Path) -> bool:
        """Validate output directory for safe writing"""
        try:
            # Ensure output is within project root
            output_path = output_path.resolve()
            output_path.relative_to(self.project_root)
            
            # Create directory if it doesn't exist
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Check write permissions
            if not os.access(output_path, os.W_OK):
                raise ValueError(f"No write permission for {output_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Output directory validation failed: {e}")
            return False
    
    def get_safe_file_list(self, scope: str, max_files: int = 50) -> List[Path]:
        """Get a safe list of files based on scope"""
        try:
            files = []
            
            if scope == 'all':
                # Get all safe files from project
                for ext in self.allowed_extensions:
                    files.extend(self.project_root.rglob(f'*{ext}'))
            elif scope == 'changed_files':
                # This would need git integration - placeholder for now
                files = [self.project_root / 'main.py']  # Placeholder
            else:
                # Specific directory
                target_dir = self.project_root / scope
                if target_dir.exists():
                    for ext in self.allowed_extensions:
                        files.extend(target_dir.rglob(f'*{ext}'))
            
            # Filter and validate files
            safe_files = []
            total_size = 0
            
            # Sensitive file patterns to exclude
            sensitive_patterns = [
                'secrets', 'password', 'key', 'token', 'credential',
                'config', 'env', '.env', 'private', 'secret'
            ]
            
            for file_path in files[:max_files]:  # Limit number of files
                # Check if file name contains sensitive patterns
                file_name_lower = file_path.name.lower()
                is_sensitive = any(pattern in file_name_lower for pattern in sensitive_patterns)
                
                if is_sensitive:
                    self.logger.warning(f"Skipping sensitive file: {file_path}")
                    continue
                
                if self.validate_file_access(file_path):
                    file_size = file_path.stat().st_size
                    if total_size + file_size > self.max_total_size:
                        self.logger.warning(f"Total size limit reached, stopping at {len(safe_files)} files")
                        break
                    
                    safe_files.append(file_path)
                    total_size += file_size
            
            return safe_files
            
        except Exception as e:
            self.logger.error(f"Failed to get safe file list: {e}")
            return []


class AILogger:
    """Enhanced logging for AI scripts"""
    
    def __init__(self, name: str, log_level: str = 'INFO'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)


class AIConfigManager:
    """Configuration management for AI scripts"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path(__file__).parent / 'ai_config.yaml'
        self.config = self._load_config()
        self.logger = AILogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        default_config = {
            'max_files': 50,
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'max_total_size': 100 * 1024 * 1024,  # 100MB
            'allowed_extensions': ['.py', '.js', '.ts', '.json', '.yaml', '.md'],
            'ai_providers': {
                'timeout': 30,
                'max_retries': 3,
                'rate_limit_delay': 1
            },
            'security': {
                'sanitize_input': True,
                'filter_sensitive': True,
                'max_input_length': 10000
            }
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                    default_config.update(file_config)
        except Exception as e:
            self.logger.warning(f"Failed to load config file: {e}")
        
        # Override with environment variables
        for key, value in os.environ.items():
            if key.startswith('AI_'):
                config_key = key[3:].lower()
                if '.' in config_key:
                    # Handle nested keys like AI_MAX_FILES
                    parts = config_key.split('_')
                    if len(parts) >= 2:
                        if parts[0] in default_config:
                            default_config[parts[0]][parts[1]] = value
                else:
                    default_config[config_key] = value
        
        return default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_max_files(self) -> int:
        """Get maximum number of files to process"""
        return self.get('max_files', 50)
    
    def get_max_file_size(self) -> int:
        """Get maximum file size in bytes"""
        return self.get('max_file_size', 10 * 1024 * 1024)
    
    def get_allowed_extensions(self) -> List[str]:
        """Get allowed file extensions"""
        return self.get('allowed_extensions', ['.py', '.js', '.ts', '.json', '.yaml', '.md'])


def setup_ai_logging(name: str, level: str = 'INFO') -> AILogger:
    """Setup logging for AI scripts"""
    return AILogger(name, level)


def validate_ai_response(response: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate AI response structure"""
    try:
        if not isinstance(response, dict):
            return False
        
        for field in required_fields:
            if field not in response:
                return False
        
        return True
    except Exception:
        return False


def sanitize_prompt(prompt: str, max_length: int = 50000) -> str:
    """Sanitize prompt to prevent injection attacks"""
    if not prompt:
        return ""
    
    if len(prompt) > max_length:
        prompt = prompt[:max_length]
    
    # Remove potential injection patterns
    injection_patterns = [
        r'ignore\s+previous\s+instructions',
        r'forget\s+everything',
        r'you\s+are\s+now',
        r'system\s*:',
        r'admin\s*:',
        r'<script>',
        r'javascript:',
        r'data:',
    ]
    
    for pattern in injection_patterns:
        prompt = re.sub(pattern, '', prompt, flags=re.IGNORECASE)
    
    return prompt.strip()


if __name__ == "__main__":
    # Test the security utilities
    validator = AISecurityValidator()
    logger = AILogger(__name__)
    config = AIConfigManager()
    
    logger.info("AI Security Utilities loaded successfully")
    logger.info(f"Max files: {config.get_max_files()}")
    logger.info(f"Allowed extensions: {config.get_allowed_extensions()}")