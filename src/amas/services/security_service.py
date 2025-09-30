"""
Security Service Implementation for AMAS
"""

import asyncio
import logging
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class SecurityService:
    """Security Service for AMAS Intelligence System"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jwt_secret = config.get('jwt_secret', 'amas_jwt_secret_key_2024_secure')
        self.encryption_key = config.get('encryption_key', 'amas_encryption_key_2024_secure_32_chars')
        self.audit_enabled = config.get('audit_enabled', True)
        
        # Initialize encryption
        self.cipher = Fernet(Fernet.generate_key())
        
        # User roles and permissions
        self.roles = {
            'admin': ['read', 'write', 'delete', 'manage_users', 'system_config'],
            'analyst': ['read', 'write', 'submit_tasks'],
            'viewer': ['read']
        }

    async def initialize(self):
        """Initialize security service"""
        try:
            logger.info("Security service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize security service: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check security service health"""
        try:
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'security',
                'encryption_enabled': True,
                'audit_enabled': self.audit_enabled
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'security'
            }

    def generate_token(self, user_id: str, role: str = 'viewer', expires_in: int = 3600) -> str:
        """Generate JWT token"""
        try:
            payload = {
                'user_id': user_id,
                'role': role,
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'iat': datetime.utcnow(),
                'iss': 'amas'
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate token: {e}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        try:
            salt = secrets.token_hex(16)
            hashed = hashlib.sha256((password + salt).encode()).hexdigest()
            return f"{salt}:{hashed}"
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = hashed_password.split(':')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return test_hash == hash_value
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False

    def encrypt_data(self, data: str) -> str:
        """Encrypt data"""
        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"Data encryption failed: {e}")
            raise

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Data decryption failed: {e}")
            raise

    def check_permission(self, user_role: str, required_permission: str) -> bool:
        """Check if user has required permission"""
        try:
            if user_role not in self.roles:
                return False
            
            user_permissions = self.roles[user_role]
            return required_permission in user_permissions
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False

    async def log_audit_event(self, event_type: str, user_id: str, action: str, 
                            details: str, classification: str = 'system',
                            ip_address: Optional[str] = None,
                            user_agent: Optional[str] = None) -> bool:
        """Log audit event"""
        try:
            if not self.audit_enabled:
                return True

            audit_data = {
                'event_type': event_type,
                'user_id': user_id,
                'action': action,
                'details': details,
                'classification': classification,
                'timestamp': datetime.utcnow(),
                'ip_address': ip_address,
                'user_agent': user_agent
            }

            # In a real implementation, this would be saved to database
            logger.info(f"Audit event: {audit_data}")
            return True

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return False

    async def get_audit_log(self, user_id: Optional[str] = None,
                          event_type: Optional[str] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log"""
        try:
            # In a real implementation, this would query the database
            # For now, return mock data
            mock_audit_log = [
                {
                    'id': 1,
                    'event_type': 'login',
                    'user_id': 'admin',
                    'action': 'user_login',
                    'details': 'User logged in successfully',
                    'classification': 'system',
                    'timestamp': datetime.utcnow().isoformat(),
                    'ip_address': '127.0.0.1',
                    'user_agent': 'Mozilla/5.0'
                }
            ]
            
            return mock_audit_log[:limit]

        except Exception as e:
            logger.error(f"Failed to get audit log: {e}")
            return []

    def validate_input(self, data: Any, input_type: str) -> bool:
        """Validate input data"""
        try:
            if input_type == 'email':
                import re
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                return bool(re.match(pattern, str(data)))
            
            elif input_type == 'url':
                import re
                pattern = r'^https?://[^\s/$.?#].[^\s]*$'
                return bool(re.match(pattern, str(data)))
            
            elif input_type == 'ip_address':
                import ipaddress
                try:
                    ipaddress.ip_address(str(data))
                    return True
                except ValueError:
                    return False
            
            elif input_type == 'task_id':
                import uuid
                try:
                    uuid.UUID(str(data))
                    return True
                except ValueError:
                    return False
            
            return True

        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return False

    def sanitize_input(self, data: str) -> str:
        """Sanitize input data"""
        try:
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
            sanitized = data
            
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, '')
            
            return sanitized.strip()
        except Exception as e:
            logger.error(f"Input sanitization failed: {e}")
            return data

    def generate_session_id(self) -> str:
        """Generate secure session ID"""
        try:
            return secrets.token_urlsafe(32)
        except Exception as e:
            logger.error(f"Session ID generation failed: {e}")
            return secrets.token_hex(16)

    def check_rate_limit(self, user_id: str, action: str, limit: int = 100, window: int = 3600) -> bool:
        """Check rate limit for user action"""
        try:
            # In a real implementation, this would use Redis or similar
            # For now, always return True
            return True
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True

    async def close(self):
        """Close security service"""
        try:
            logger.info("Security service closed")
        except Exception as e:
            logger.error(f"Error closing security service: {e}")