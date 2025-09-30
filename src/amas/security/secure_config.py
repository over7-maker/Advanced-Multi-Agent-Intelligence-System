"""
Secure Configuration Management for AMAS
Handles sensitive configuration data securely
"""
import os
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64
import json

logger = logging.getLogger(__name__)

class SecureConfigManager:
    """Secure configuration manager for AMAS"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.config_cache = {}
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive config data"""
        key_file = os.getenv('AMAS_CONFIG_KEY_FILE', '/app/config/encryption.key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            return key
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get secure database configuration"""
        return {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', '5432')),
            'user': os.getenv('POSTGRES_USER', 'amas'),
            'password': os.getenv('POSTGRES_PASSWORD', ''),
            'database': os.getenv('POSTGRES_DB', 'amas'),
            'ssl_mode': os.getenv('POSTGRES_SSL_MODE', 'prefer')
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get secure Redis configuration"""
        return {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', '6379')),
            'db': int(os.getenv('REDIS_DB', '0')),
            'password': os.getenv('REDIS_PASSWORD', ''),
            'ssl': os.getenv('REDIS_SSL', 'false').lower() == 'true'
        }
    
    def get_neo4j_config(self) -> Dict[str, Any]:
        """Get secure Neo4j configuration"""
        return {
            'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            'username': os.getenv('NEO4J_USERNAME', 'neo4j'),
            'password': os.getenv('NEO4J_PASSWORD', ''),
            'database': os.getenv('NEO4J_DATABASE', 'neo4j')
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get secure LLM configuration"""
        return {
            'provider': os.getenv('LLM_PROVIDER', 'ollama'),
            'base_url': os.getenv('LLM_BASE_URL', 'http://localhost:11434'),
            'model': os.getenv('LLM_MODEL', 'llama2'),
            'api_key': os.getenv('LLM_API_KEY', ''),
            'timeout': int(os.getenv('LLM_TIMEOUT', '30'))
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get secure security configuration"""
        return {
            'jwt_secret': os.getenv('JWT_SECRET', ''),
            'jwt_algorithm': os.getenv('JWT_ALGORITHM', 'HS256'),
            'jwt_expiration': int(os.getenv('JWT_EXPIRATION', '3600')),
            'encryption_key': os.getenv('ENCRYPTION_KEY', ''),
            'audit_enabled': os.getenv('AUDIT_ENABLED', 'true').lower() == 'true',
            'max_login_attempts': int(os.getenv('MAX_LOGIN_ATTEMPTS', '5')),
            'lockout_duration': int(os.getenv('LOCKOUT_DURATION', '900'))
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get secure monitoring configuration"""
        return {
            'prometheus_url': os.getenv('PROMETHEUS_URL', 'http://localhost:9090'),
            'grafana_url': os.getenv('GRAFANA_URL', 'http://localhost:3001'),
            'metrics_enabled': os.getenv('METRICS_ENABLED', 'true').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO')
        }
    
    def encrypt_sensitive_value(self, value: str) -> str:
        """Encrypt a sensitive configuration value"""
        try:
            encrypted = self.fernet.encrypt(value.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Error encrypting value: {e}")
            return value
    
    def decrypt_sensitive_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive configuration value"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error decrypting value: {e}")
            return encrypted_value
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all secure configuration"""
        return {
            'database': self.get_database_config(),
            'redis': self.get_redis_config(),
            'neo4j': self.get_neo4j_config(),
            'llm': self.get_llm_config(),
            'security': self.get_security_config(),
            'monitoring': self.get_monitoring_config()
        }
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            'POSTGRES_PASSWORD',
            'JWT_SECRET',
            'ENCRYPTION_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
        
        return True
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary (without sensitive data)"""
        config = self.get_all_config()
        
        # Remove sensitive data from summary
        safe_config = {}
        for service, settings in config.items():
            safe_config[service] = {}
            for key, value in settings.items():
                if 'password' in key.lower() or 'secret' in key.lower() or 'key' in key.lower():
                    safe_config[service][key] = '***REDACTED***'
                else:
                    safe_config[service][key] = value
        
        return safe_config