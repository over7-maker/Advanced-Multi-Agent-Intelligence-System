"""
AMAS Secrets Management
Production-ready secrets management with external secret support
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)


class SecretsManager:
    """Production-ready secrets management"""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize secrets manager"""
        self.master_key = master_key or os.getenv('AMAS_MASTER_KEY')
        self.secrets_file = Path(os.getenv('AMAS_SECRETS_FILE', 'secrets.json.encrypted'))
        self._fernet = None
        
        if self.master_key:
            self._fernet = self._create_fernet(self.master_key)
    
    def _create_fernet(self, password: str) -> Fernet:
        """Create Fernet encryption from password"""
        password_bytes = password.encode()
        salt = b'amas_salt_2024'  # In production, use random salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return Fernet(key)
    
    def encrypt_secret(self, secret: str) -> str:
        """Encrypt a secret value"""
        if not self._fernet:
            raise ValueError("Master key not set")
        
        return self._fernet.encrypt(secret.encode()).decode()
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt a secret value"""
        if not self._fernet:
            raise ValueError("Master key not set")
        
        return self._fernet.decrypt(encrypted_secret.encode()).decode()
    
    def store_secret(self, key: str, value: str) -> None:
        """Store a secret"""
        if not self._fernet:
            raise ValueError("Master key not set")
        
        # Load existing secrets
        secrets = self.load_secrets()
        
        # Add new secret
        secrets[key] = self.encrypt_secret(value)
        
        # Save encrypted secrets
        with open(self.secrets_file, 'w') as f:
            json.dump(secrets, f)
        
        logger.info(f"Secret '{key}' stored successfully")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret value"""
        if not self._fernet:
            raise ValueError("Master key not set")
        
        secrets = self.load_secrets()
        encrypted_value = secrets.get(key)
        
        if encrypted_value is None:
            return default
        
        try:
            return self.decrypt_secret(encrypted_value)
        except Exception as e:
            logger.error(f"Failed to decrypt secret '{key}': {e}")
            return default
    
    def load_secrets(self) -> Dict[str, str]:
        """Load encrypted secrets from file"""
        if not self.secrets_file.exists():
            return {}
        
        try:
            with open(self.secrets_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            return {}
    
    def delete_secret(self, key: str) -> bool:
        """Delete a secret"""
        secrets = self.load_secrets()
        
        if key not in secrets:
            return False
        
        del secrets[key]
        
        with open(self.secrets_file, 'w') as f:
            json.dump(secrets, f)
        
        logger.info(f"Secret '{key}' deleted successfully")
        return True
    
    def list_secrets(self) -> list:
        """List all secret keys"""
        secrets = self.load_secrets()
        return list(secrets.keys())
    
    def rotate_secrets(self) -> None:
        """Rotate all secrets (requires new master key)"""
        if not self._fernet:
            raise ValueError("Master key not set")
        
        secrets = self.load_secrets()
        new_secrets = {}
        
        for key, encrypted_value in secrets.items():
            try:
                # Decrypt with old key
                decrypted_value = self.decrypt_secret(encrypted_value)
                # Re-encrypt with new key (same key for now)
                new_secrets[key] = self.encrypt_secret(decrypted_value)
            except Exception as e:
                logger.error(f"Failed to rotate secret '{key}': {e}")
        
        # Save rotated secrets
        with open(self.secrets_file, 'w') as f:
            json.dump(new_secrets, f)
        
        logger.info("Secrets rotation completed")


class ExternalSecretsManager:
    """External secrets management (AWS Secrets Manager, Azure Key Vault, etc.)"""
    
    def __init__(self, provider: str = "aws"):
        """Initialize external secrets manager"""
        self.provider = provider
        self._client = None
        
        if provider == "aws":
            self._init_aws_secrets_manager()
        elif provider == "azure":
            self._init_azure_key_vault()
        elif provider == "gcp":
            self._init_gcp_secret_manager()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _init_aws_secrets_manager(self):
        """Initialize AWS Secrets Manager"""
        try:
            import boto3
            self._client = boto3.client('secretsmanager')
            logger.info("AWS Secrets Manager initialized")
        except ImportError:
            logger.warning("boto3 not installed, AWS Secrets Manager not available")
        except Exception as e:
            logger.error(f"Failed to initialize AWS Secrets Manager: {e}")
    
    def _init_azure_key_vault(self):
        """Initialize Azure Key Vault"""
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            credential = DefaultAzureCredential()
            vault_url = os.getenv('AZURE_VAULT_URL')
            if vault_url:
                self._client = SecretClient(vault_url=vault_url, credential=credential)
                logger.info("Azure Key Vault initialized")
        except ImportError:
            logger.warning("azure-keyvault-secrets not installed, Azure Key Vault not available")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Key Vault: {e}")
    
    def _init_gcp_secret_manager(self):
        """Initialize GCP Secret Manager"""
        try:
            from google.cloud import secretmanager
            
            self._client = secretmanager.SecretManagerServiceClient()
            logger.info("GCP Secret Manager initialized")
        except ImportError:
            logger.warning("google-cloud-secret-manager not installed, GCP Secret Manager not available")
        except Exception as e:
            logger.error(f"Failed to initialize GCP Secret Manager: {e}")
    
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from external provider"""
        if not self._client:
            logger.warning(f"External secrets client not initialized for {self.provider}")
            return default
        
        try:
            if self.provider == "aws":
                response = self._client.get_secret_value(SecretId=secret_name)
                return response['SecretString']
            elif self.provider == "azure":
                secret = self._client.get_secret(secret_name)
                return secret.value
            elif self.provider == "gcp":
                project_id = os.getenv('GCP_PROJECT_ID')
                if not project_id:
                    raise ValueError("GCP_PROJECT_ID environment variable not set")
                
                name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
                response = self._client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Failed to get secret '{secret_name}' from {self.provider}: {e}")
            return default
        
        return default
    
    def store_secret(self, secret_name: str, secret_value: str) -> bool:
        """Store secret in external provider"""
        if not self._client:
            logger.warning(f"External secrets client not initialized for {self.provider}")
            return False
        
        try:
            if self.provider == "aws":
                self._client.create_secret(
                    Name=secret_name,
                    SecretString=secret_value
                )
            elif self.provider == "azure":
                self._client.set_secret(secret_name, secret_value)
            elif self.provider == "gcp":
                project_id = os.getenv('GCP_PROJECT_ID')
                if not project_id:
                    raise ValueError("GCP_PROJECT_ID environment variable not set")
                
                parent = f"projects/{project_id}"
                self._client.create_secret(
                    request={
                        "parent": parent,
                        "secret_id": secret_name,
                        "secret": {"replication": {"automatic": {}}},
                    }
                )
                self._client.add_secret_version(
                    request={
                        "parent": f"{parent}/secrets/{secret_name}",
                        "payload": {"data": secret_value.encode("UTF-8")},
                    }
                )
            
            logger.info(f"Secret '{secret_name}' stored in {self.provider}")
            return True
        except Exception as e:
            logger.error(f"Failed to store secret '{secret_name}' in {self.provider}: {e}")
            return False


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None
_external_secrets_manager: Optional[ExternalSecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get the global secrets manager instance"""
    global _secrets_manager
    
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    
    return _secrets_manager


def get_external_secrets_manager(provider: str = "aws") -> ExternalSecretsManager:
    """Get the external secrets manager instance"""
    global _external_secrets_manager
    
    if _external_secrets_manager is None:
        _external_secrets_manager = ExternalSecretsManager(provider)
    
    return _external_secrets_manager


def get_secret(key: str, default: Optional[str] = None, use_external: bool = False) -> Optional[str]:
    """Get a secret value from the appropriate manager"""
    # First try environment variables
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # Try external secrets manager if enabled
    if use_external:
        external_manager = get_external_secrets_manager()
        external_value = external_manager.get_secret(key)
        if external_value:
            return external_value
    
    # Try local secrets manager
    local_manager = get_secrets_manager()
    if local_manager._fernet:
        local_value = local_manager.get_secret(key)
        if local_value:
            return local_value
    
    return default


def store_secret(key: str, value: str, use_external: bool = False) -> bool:
    """Store a secret value in the appropriate manager"""
    if use_external:
        external_manager = get_external_secrets_manager()
        return external_manager.store_secret(key, value)
    else:
        local_manager = get_secrets_manager()
        if local_manager._fernet:
            local_manager.store_secret(key, value)
            return True
        else:
            logger.error("Local secrets manager not initialized (no master key)")
            return False


# CLI interface for secrets management
def main():
    """CLI interface for secrets management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AMAS Secrets Manager")
    parser.add_argument("action", choices=["get", "set", "delete", "list", "rotate"])
    parser.add_argument("--key", help="Secret key")
    parser.add_argument("--value", help="Secret value")
    parser.add_argument("--external", action="store_true", help="Use external secrets manager")
    parser.add_argument("--provider", default="aws", help="External provider (aws, azure, gcp)")
    
    args = parser.parse_args()
    
    if args.action == "get":
        if not args.key:
            print("Error: --key required for get action")
            return 1
        
        value = get_secret(args.key, use_external=args.external)
        if value:
            print(value)
        else:
            print("Secret not found")
            return 1
    
    elif args.action == "set":
        if not args.key or not args.value:
            print("Error: --key and --value required for set action")
            return 1
        
        success = store_secret(args.key, args.value, use_external=args.external)
        if success:
            print(f"Secret '{args.key}' stored successfully")
        else:
            print("Failed to store secret")
            return 1
    
    elif args.action == "delete":
        if not args.key:
            print("Error: --key required for delete action")
            return 1
        
        if args.external:
            print("Delete not supported for external secrets manager")
            return 1
        
        manager = get_secrets_manager()
        success = manager.delete_secret(args.key)
        if success:
            print(f"Secret '{args.key}' deleted successfully")
        else:
            print("Secret not found")
            return 1
    
    elif args.action == "list":
        if args.external:
            print("List not supported for external secrets manager")
            return 1
        
        manager = get_secrets_manager()
        secrets = manager.list_secrets()
        for secret in secrets:
            print(secret)
    
    elif args.action == "rotate":
        if args.external:
            print("Rotate not supported for external secrets manager")
            return 1
        
        manager = get_secrets_manager()
        manager.rotate_secrets()
        print("Secrets rotation completed")
    
    return 0


if __name__ == "__main__":
    exit(main())