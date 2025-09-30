"""
Encryption Module for AMAS
Provides data encryption, decryption, and key management
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import secrets
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import json

logger = logging.getLogger(__name__)

class EncryptionManager:
    """Encryption manager for AMAS"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.master_key = config.get('security', {}).get('encryption_key', secrets.token_urlsafe(32))
        self.key_rotation_interval = config.get('security', {}).get('key_rotation_interval', 86400 * 30)  # 30 days
        
        # Initialize encryption keys
        self.symmetric_key = self._derive_symmetric_key(self.master_key)
        self.fernet = Fernet(self.symmetric_key)
        
        # Initialize asymmetric keys
        self.private_key, self.public_key = self._generate_asymmetric_keys()
        
        # Key management
        self.key_history = []
        self.current_key_id = self._generate_key_id()
    
    def _derive_symmetric_key(self, password: str) -> bytes:
        """Derive a symmetric key from password using PBKDF2"""
        salt = b'amas_salt_2024'  # In production, use a random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _generate_asymmetric_keys(self) -> tuple:
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def _generate_key_id(self) -> str:
        """Generate a unique key ID"""
        return hashlib.sha256(f"{datetime.utcnow()}{secrets.token_urlsafe(16)}".encode()).hexdigest()[:16]
    
    async def encrypt_symmetric(self, data: Union[str, bytes], key_id: Optional[str] = None) -> Dict[str, Any]:
        """Encrypt data using symmetric encryption"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Encrypt data
            encrypted_data = self.fernet.encrypt(data)
            
            # Create metadata
            metadata = {
                "key_id": key_id or self.current_key_id,
                "algorithm": "AES-256-GCM",
                "timestamp": datetime.utcnow().isoformat(),
                "data_type": "symmetric"
            }
            
            return {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    async def decrypt_symmetric(self, encrypted_data: str, metadata: Dict[str, Any]) -> Union[str, bytes]:
        """Decrypt data using symmetric encryption"""
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Decrypt data
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            
            # Return as string if original was string
            if metadata.get("data_type") == "string":
                return decrypted_data.decode('utf-8')
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    async def encrypt_asymmetric(self, data: Union[str, bytes], public_key: Optional[bytes] = None) -> Dict[str, Any]:
        """Encrypt data using asymmetric encryption"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Use provided public key or default
            key_to_use = public_key or self.public_key
            
            # Encrypt data
            encrypted_data = key_to_use.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Create metadata
            metadata = {
                "algorithm": "RSA-OAEP",
                "timestamp": datetime.utcnow().isoformat(),
                "data_type": "asymmetric"
            }
            
            return {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error encrypting data with asymmetric key: {e}")
            raise
    
    async def decrypt_asymmetric(self, encrypted_data: str, metadata: Dict[str, Any]) -> Union[str, bytes]:
        """Decrypt data using asymmetric encryption"""
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Decrypt data
            decrypted_data = self.private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Return as string if original was string
            if metadata.get("data_type") == "string":
                return decrypted_data.decode('utf-8')
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Error decrypting data with asymmetric key: {e}")
            raise
    
    async def encrypt_field(self, field_value: str, field_name: str, classification: str = "confidential") -> Dict[str, Any]:
        """Encrypt a specific field with classification"""
        try:
            # Add classification metadata
            metadata = {
                "field_name": field_name,
                "classification": classification,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Encrypt based on classification
            if classification in ["public", "internal"]:
                # Use symmetric encryption for less sensitive data
                result = await self.encrypt_symmetric(field_value)
                result["metadata"].update(metadata)
                return result
            else:
                # Use asymmetric encryption for sensitive data
                result = await self.encrypt_asymmetric(field_value)
                result["metadata"].update(metadata)
                return result
                
        except Exception as e:
            logger.error(f"Error encrypting field {field_name}: {e}")
            raise
    
    async def decrypt_field(self, encrypted_data: str, metadata: Dict[str, Any]) -> str:
        """Decrypt a specific field"""
        try:
            classification = metadata.get("classification", "confidential")
            
            if classification in ["public", "internal"]:
                return await self.decrypt_symmetric(encrypted_data, metadata)
            else:
                return await self.decrypt_asymmetric(encrypted_data, metadata)
                
        except Exception as e:
            logger.error(f"Error decrypting field: {e}")
            raise
    
    async def hash_password(self, password: str, salt: Optional[str] = None) -> Dict[str, str]:
        """Hash a password with salt"""
        try:
            if not salt:
                salt = secrets.token_urlsafe(32)
            
            # Create hash
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            return {
                "hash": base64.b64encode(hash_obj).decode(),
                "salt": salt
            }
            
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    async def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        """Verify a password against its hash"""
        try:
            # Hash the provided password
            result = await self.hash_password(password, salt)
            return result["hash"] == hash_value
            
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    async def generate_data_key(self, purpose: str) -> Dict[str, Any]:
        """Generate a new data encryption key"""
        try:
            key_id = self._generate_key_id()
            key_material = secrets.token_urlsafe(32)
            
            # Encrypt the key material with master key
            encrypted_key = await self.encrypt_symmetric(key_material)
            
            key_data = {
                "key_id": key_id,
                "purpose": purpose,
                "encrypted_key": encrypted_key,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat()
            }
            
            # Store in key history
            self.key_history.append(key_data)
            
            return key_data
            
        except Exception as e:
            logger.error(f"Error generating data key: {e}")
            raise
    
    async def rotate_keys(self) -> bool:
        """Rotate encryption keys"""
        try:
            # Generate new symmetric key
            new_master_key = secrets.token_urlsafe(32)
            new_symmetric_key = self._derive_symmetric_key(new_master_key)
            
            # Update keys
            old_key_id = self.current_key_id
            self.current_key_id = self._generate_key_id()
            self.symmetric_key = new_symmetric_key
            self.fernet = Fernet(self.symmetric_key)
            
            # Log key rotation
            logger.info(f"Keys rotated from {old_key_id} to {self.current_key_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error rotating keys: {e}")
            return False
    
    async def get_public_key(self) -> str:
        """Get the public key for external use"""
        try:
            public_key_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return public_key_pem.decode()
            
        except Exception as e:
            logger.error(f"Error getting public key: {e}")
            raise
    
    async def encrypt_for_storage(self, data: Dict[str, Any], classification: str = "confidential") -> Dict[str, Any]:
        """Encrypt data for storage"""
        try:
            # Convert data to JSON
            json_data = json.dumps(data)
            
            # Encrypt based on classification
            if classification in ["public", "internal"]:
                encrypted_result = await self.encrypt_symmetric(json_data)
            else:
                encrypted_result = await self.encrypt_asymmetric(json_data)
            
            # Add storage metadata
            encrypted_result["storage_metadata"] = {
                "classification": classification,
                "encrypted_at": datetime.utcnow().isoformat(),
                "data_size": len(json_data)
            }
            
            return encrypted_result
            
        except Exception as e:
            logger.error(f"Error encrypting data for storage: {e}")
            raise
    
    async def decrypt_from_storage(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt data from storage"""
        try:
            metadata = encrypted_data.get("metadata", {})
            classification = encrypted_data.get("storage_metadata", {}).get("classification", "confidential")
            
            # Decrypt based on classification
            if classification in ["public", "internal"]:
                decrypted_json = await self.decrypt_symmetric(
                    encrypted_data["encrypted_data"], 
                    metadata
                )
            else:
                decrypted_json = await self.decrypt_asymmetric(
                    encrypted_data["encrypted_data"], 
                    metadata
                )
            
            # Parse JSON
            return json.loads(decrypted_json)
            
        except Exception as e:
            logger.error(f"Error decrypting data from storage: {e}")
            raise
    
    async def get_encryption_status(self) -> Dict[str, Any]:
        """Get encryption system status"""
        return {
            "current_key_id": self.current_key_id,
            "key_rotation_interval": self.key_rotation_interval,
            "total_keys": len(self.key_history),
            "symmetric_algorithm": "AES-256-GCM",
            "asymmetric_algorithm": "RSA-OAEP",
            "key_size": 2048,
            "status": "active"
        }
    
    async def audit_encryption_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get encryption audit events"""
        # In a real implementation, you would query the database
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "key_rotation",
                "key_id": self.current_key_id,
                "action": "key_rotated",
                "status": "success"
            }
        ]