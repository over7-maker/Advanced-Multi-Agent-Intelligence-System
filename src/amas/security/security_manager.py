"""
Security Manager - Centralized security initialization and management
"""

import logging
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from .auth.jwt_middleware import (
    SecureAuthenticationManager,
    SecurityHeadersMiddleware,
)
from .policies.opa_integration import configure_policy_engine
from .audit.audit_logger import initialize_audit_logger

logger = logging.getLogger(__name__)


class SecurityManager:
    """Centralized security manager for AMAS"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv(
            "SECURITY_CONFIG_PATH",
            "config/security_config.yaml"
        )
        self.config: Dict[str, Any] = {}
        self.auth_manager: Optional[SecureAuthenticationManager] = None
        self.security_headers: Optional[SecurityHeadersMiddleware] = None
        self.audit_logger = None
        self._load_config()
    
    def _load_config(self):
        """Load security configuration from YAML file"""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                logger.warning(
                    f"Security config file not found: {self.config_path}. "
                    "Using default configuration."
                )
                self.config = self._default_config()
                return
            
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            
            # Expand environment variables
            self._expand_env_vars(self.config)
            
            logger.info(f"Security configuration loaded from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load security config: {e}. Using defaults.")
            self.config = self._default_config()
    
    def _expand_env_vars(self, data: Any) -> Any:
        """Recursively expand environment variables in config"""
        if isinstance(data, dict):
            return {k: self._expand_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._expand_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            # Format: ${VAR:-default}
            var_part = data[2:-1]
            if ":-" in var_part:
                var_name, default = var_part.split(":-", 1)
                return os.getenv(var_name, default)
            else:
                return os.getenv(var_part, data)
        else:
            return data
    
    def _default_config(self) -> Dict[str, Any]:
        """Default security configuration"""
        return {
            "authentication": {
                "oidc": {
                    "issuer": os.getenv("OIDC_ISSUER", "https://your-oidc-provider.com"),
                    "audience": os.getenv("OIDC_AUDIENCE", "amas-api"),
                    "jwks_uri": os.getenv("OIDC_JWKS_URI", "https://your-oidc-provider.com/.well-known/jwks.json"),
                    "algorithms": ["RS256", "ES256"],
                    "cache_ttl": 3600,
                },
                "token_blacklist": {
                    "enabled": True,
                    "cleanup_interval": 3600,
                },
                "security_headers": {
                    "enabled": True,
                    "hsts_max_age": 31536000,
                    "csp_enabled": True,
                },
            },
            "authorization": {
                "opa": {
                    "url": os.getenv("OPA_URL", "http://localhost:8181"),
                    "timeout_seconds": 5.0,
                    "retry_attempts": 3,
                    "cache_enabled": True,
                    "cache_ttl": 300,
                    "cache_max_size": 1000,
                },
            },
            "audit": {
                "log_file": os.getenv("AUDIT_LOG_FILE", "logs/audit.jsonl"),
                "buffer_size": 100,
                "flush_interval": 30,
                "backup_count": 5,
                "redact_sensitive": True,
            },
        }
    
    async def initialize(self):
        """Initialize all security components"""
        try:
            # Initialize authentication
            auth_config = self.config.get("authentication", {})
            oidc_config = auth_config.get("oidc", {})
            
            # Initialize auth manager
            self.auth_manager = SecureAuthenticationManager(self.config)
            
            # Start background JWKS refresh if available
            if hasattr(self.auth_manager, 'jwt_middleware') and hasattr(self.auth_manager.jwt_middleware, 'start_background_refresh'):
                await self.auth_manager.jwt_middleware.start_background_refresh()
            logger.info("Authentication manager initialized with background JWKS refresh")
            
            # Initialize security headers
            self.security_headers = SecurityHeadersMiddleware()
            logger.info("Security headers middleware initialized")
            
            # Initialize OPA policy engine
            opa_config = self.config.get("authorization", {}).get("opa", {})
            configure_policy_engine(
                opa_url=opa_config.get("url", "http://localhost:8181"),
                timeout_seconds=opa_config.get("timeout_seconds", 5.0),
                retry_attempts=opa_config.get("retry_attempts", 3),
                cache_ttl=opa_config.get("cache_ttl", 300),
                cache_size=opa_config.get("cache_max_size", 1000),
            )
            logger.info("Policy engine initialized")
            
            # Initialize audit logger
            self.audit_logger = initialize_audit_logger(self.config)
            logger.info("Audit logger initialized")
            
            logger.info("Security manager initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize security manager: {e}")
            raise
    
    def get_auth_manager(self) -> SecureAuthenticationManager:
        """Get authentication manager"""
        if not self.auth_manager:
            raise RuntimeError("Security manager not initialized. Call initialize() first.")
        return self.auth_manager
    
    def get_security_headers(self) -> SecurityHeadersMiddleware:
        """Get security headers middleware"""
        if not self.security_headers:
            raise RuntimeError("Security manager not initialized. Call initialize() first.")
        return self.security_headers
    
    def get_audit_logger(self):
        """Get audit logger"""
        if not self.audit_logger:
            raise RuntimeError("Security manager not initialized. Call initialize() first.")
        return self.audit_logger


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


async def get_security_manager(config_path: Optional[str] = None) -> SecurityManager:
    """Get global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(config_path)
        await _security_manager.initialize()
    return _security_manager


async def initialize_security(config_path: Optional[str] = None) -> SecurityManager:
    """Initialize global security manager"""
    global _security_manager
    _security_manager = SecurityManager(config_path)
    await _security_manager.initialize()
    return _security_manager
