"""
Credential Manager Service
Centralized credential management with encryption support
"""

import logging
import os
from typing import Any, Dict, Optional
import base64

# Optional encryption support - make it graceful if cryptography not available
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    Fernet = None
    PBKDF2HMAC = None
    CRYPTOGRAPHY_AVAILABLE = False

logger = logging.getLogger(__name__)


class CredentialManager:
    """
    Centralized credential management service
    
    Features:
    - Environment variable loading
    - Settings integration
    - Optional encryption for sensitive credentials
    - Credential validation
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize credential manager
        
        Args:
            encryption_key: Optional encryption key for sensitive credentials
        """
        self.encryption_key = encryption_key or os.getenv("CREDENTIAL_ENCRYPTION_KEY")
        self._cipher = None
        
        if self.encryption_key:
            try:
                self._init_encryption()
            except Exception as e:
                logger.warning(f"Failed to initialize encryption: {e}")
                self._cipher = None
    
    def _init_encryption(self):
        """Initialize encryption cipher"""
        if not self.encryption_key or not CRYPTOGRAPHY_AVAILABLE:
            return
        
        try:
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'amas_credential_salt',  # In production, use random salt
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))
            self._cipher = Fernet(key)
        except Exception as e:
            logger.warning(f"Failed to initialize encryption cipher: {e}")
            self._cipher = None
    
    def get_credential(
        self,
        env_name: str,
        settings_attr: Optional[str] = None,
        default: Optional[str] = None,
        encrypted: bool = False
    ) -> Optional[str]:
        """
        Get credential from environment or settings
        
        Args:
            env_name: Environment variable name
            settings_attr: Settings attribute path (e.g., "ai.openai_api_key")
            default: Default value if not found
            encrypted: Whether the credential is encrypted
        
        Returns:
            Credential value or None
        """
        # Priority 1: Environment variable
        value = os.getenv(env_name)
        if value:
            if encrypted and self._cipher:
                try:
                    return self._cipher.decrypt(value.encode()).decode()
                except Exception as e:
                    logger.warning(f"Failed to decrypt {env_name}: {e}")
                    return value
            return value.strip() if value else None
        
        # Priority 2: Settings
        if settings_attr:
            try:
                from src.config.settings import get_settings
                settings = get_settings()
                
                # Navigate nested attributes
                parts = settings_attr.split(".")
                obj = settings
                for part in parts:
                    obj = getattr(obj, part, None)
                    if obj is None:
                        break
                
                if obj:
                    value = str(obj).strip() if obj else None
                    if value and encrypted and self._cipher:
                        try:
                            return self._cipher.decrypt(value.encode()).decode()
                        except Exception:
                            return value
                    return value
            except Exception as e:
                logger.debug(f"Could not load credential from settings {settings_attr}: {e}")
        
        # Priority 3: Default
        return default
    
    def get_ai_api_key(self, provider: str) -> Optional[str]:
        """
        Get AI provider API key
        
        Args:
            provider: Provider name (e.g., "openai", "anthropic")
        
        Returns:
            API key or None
        """
        env_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google_ai": "GOOGLE_AI_API_KEY",
            "groq": "GROQ_API_KEY",
            "cohere": "COHERE_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
            "cerebras": "CEREBRAS_API_KEY",
            "nvidia": "NVIDIA_API_KEY",
            "groq2": "GROQ2_API_KEY",
            "groqai": "GROQAI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "codestral": "CODESTRAL_API_KEY",
            "glm": "GLM_API_KEY",
            "gemini2": "GEMINI2_API_KEY",
            "grok": "GROK_API_KEY",
            "kimi": "KIMI_API_KEY",
            "qwen": "QWEN_API_KEY",
            "gptoss": "GPTOSS_API_KEY",
            "chutes": "CHUTES_API_KEY",
            "together": "TOGETHER_API_KEY",
            "perplexity": "PERPLEXITY_API_KEY",
            "fireworks": "FIREWORKS_API_KEY",
            "replicate": "REPLICATE_API_KEY",
            "ai21": "AI21_API_KEY",
            "aleph_alpha": "ALEPH_ALPHA_API_KEY",
            "writer": "WRITER_API_KEY",
            "moonshot": "MOONSHOT_API_KEY",
            "mistral": "MISTRAL_API_KEY",
        }
        
        env_name = env_mapping.get(provider.lower())
        if not env_name:
            return None
        
        settings_attr = f"ai.{provider.lower()}_api_key"
        return self.get_credential(env_name, settings_attr)
    
    def get_integration_credentials(self, platform: str) -> Dict[str, Any]:
        """
        Get integration platform credentials
        
        Args:
            platform: Platform name (e.g., "n8n", "slack", "github")
        
        Returns:
            Dictionary of credentials
        """
        credentials = {}
        
        if platform.lower() == "n8n":
            credentials = {
                "base_url": self.get_credential("INTEGRATION_N8N_BASE_URL", "integration.n8n_base_url", "http://localhost:5678"),
                "api_key": self.get_credential("INTEGRATION_N8N_API_KEY", "integration.n8n_api_key"),
                "username": self.get_credential("INTEGRATION_N8N_USERNAME", "integration.n8n_username"),
                "password": self.get_credential("INTEGRATION_N8N_PASSWORD", "integration.n8n_password"),
            }
        elif platform.lower() == "slack":
            credentials = {
                "bot_token": self.get_credential("INTEGRATION_SLACK_BOT_TOKEN", "integration.slack_bot_token"),
                "signing_secret": self.get_credential("INTEGRATION_SLACK_SIGNING_SECRET", "integration.slack_signing_secret"),
                "app_token": self.get_credential("INTEGRATION_SLACK_APP_TOKEN", "integration.slack_app_token"),
            }
        elif platform.lower() == "github":
            credentials = {
                "access_token": self.get_credential("INTEGRATION_GITHUB_ACCESS_TOKEN", "integration.github_access_token"),
                "webhook_secret": self.get_credential("INTEGRATION_GITHUB_WEBHOOK_SECRET", "integration.github_webhook_secret"),
            }
        elif platform.lower() == "notion":
            credentials = {
                "api_key": self.get_credential("INTEGRATION_NOTION_API_KEY", "integration.notion_api_key"),
            }
        elif platform.lower() == "jira":
            credentials = {
                "server": self.get_credential("INTEGRATION_JIRA_SERVER", "integration.jira_server"),
                "email": self.get_credential("INTEGRATION_JIRA_EMAIL", "integration.jira_email"),
                "api_token": self.get_credential("INTEGRATION_JIRA_API_TOKEN", "integration.jira_api_token"),
            }
        elif platform.lower() == "salesforce":
            credentials = {
                "username": self.get_credential("INTEGRATION_SALESFORCE_USERNAME", "integration.salesforce_username"),
                "password": self.get_credential("INTEGRATION_SALESFORCE_PASSWORD", "integration.salesforce_password"),
                "security_token": self.get_credential("INTEGRATION_SALESFORCE_SECURITY_TOKEN", "integration.salesforce_security_token"),
                "access_token": self.get_credential("INTEGRATION_SALESFORCE_ACCESS_TOKEN", "integration.salesforce_access_token"),
                "instance_url": self.get_credential("INTEGRATION_SALESFORCE_INSTANCE_URL", "integration.salesforce_instance_url"),
                "client_id": self.get_credential("INTEGRATION_SALESFORCE_CLIENT_ID", "integration.salesforce_client_id"),
                "client_secret": self.get_credential("INTEGRATION_SALESFORCE_CLIENT_SECRET", "integration.salesforce_client_secret"),
            }
        
        # Remove None values
        return {k: v for k, v in credentials.items() if v is not None}
    
    def validate_credential(self, credential: Optional[str], min_length: int = 8) -> bool:
        """
        Validate credential format
        
        Args:
            credential: Credential value
            min_length: Minimum length requirement
        
        Returns:
            True if valid, False otherwise
        """
        if not credential:
            return False
        
        if len(credential.strip()) < min_length:
            return False
        
        return True


# Global credential manager instance
_credential_manager: Optional[CredentialManager] = None


def get_credential_manager() -> CredentialManager:
    """Get global credential manager instance"""
    global _credential_manager
    
    if _credential_manager is None:
        _credential_manager = CredentialManager()
    
    return _credential_manager

