"""
Security Service for AMAS Intelligence System
"""

import asyncio
import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import bcrypt
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SecurityService:
    """Security service for AMAS Intelligence System"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jwt_secret = config.get("jwt_secret", secrets.token_urlsafe(32))
        self.encryption_key = config.get("encryption_key", Fernet.generate_key())
        self.fernet = Fernet(self.encryption_key)
        self.audit_log = []
        self.access_control = {}

    async def initialize(self):
        """Initialize security service"""
        try:
            logger.info("Initializing security service...")

            # Initialize access control
            await self._initialize_access_control()

            # Initialize audit logging
            await self._initialize_audit_logging()

            logger.info("Security service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize security service: {e}")
            raise

    async def _initialize_access_control(self):
        """Initialize access control system"""
        try:
            # Default roles and permissions
            self.access_control = {
                "roles": {
                    "admin": ["read", "write", "delete", "execute", "manage"],
                    "analyst": ["read", "write", "execute"],
                    "viewer": ["read"],
                    "system": ["read", "write", "execute", "manage"],
                },
                "permissions": {
                    "read": "Read access to data and reports",
                    "write": "Write access to create and modify data",
                    "delete": "Delete access to remove data",
                    "execute": "Execute access to run tasks and workflows",
                    "manage": "Manage access to system configuration",
                },
            }

            logger.info("Access control system initialized")

        except Exception as e:
            logger.error(f"Error initializing access control: {e}")
            raise

    async def _initialize_audit_logging(self):
        """Initialize audit logging system"""
        try:
            # Initialize audit log with system startup
            await self.log_audit_event(
                event_type="system_startup",
                user_id="system",
                action="initialize",
                details="Security service initialized",
                classification="system",
            )

            logger.info("Audit logging system initialized")

        except Exception as e:
            logger.error(f"Error initializing audit logging: {e}")
            raise

    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user"""
        try:
            # Mock authentication - in production, this would check against a user database
            # SECURITY WARNING: This is for development only - use proper authentication in production
            admin_password = os.getenv("AMAS_ADMIN_PASSWORD", "admin123")
            if username == "admin" and password == admin_password:
                user_data = {
                    "user_id": "admin",
                    "username": "admin",
                    "role": "admin",
                    "permissions": self.access_control["roles"]["admin"],
                }

                # Generate JWT token
                token = await self.generate_jwt_token(user_data)

                await self.log_audit_event(
                    event_type="authentication",
                    user_id=username,
                    action="login",
                    details="User authenticated successfully",
                    classification="security",
                )

                return {
                    "success": True,
                    "user": user_data,
                    "token": token,
                    "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                }
            else:
                await self.log_audit_event(
                    event_type="authentication",
                    user_id=username,
                    action="login_failed",
                    details="Invalid credentials",
                    classification="security",
                )

                return {"success": False, "error": "Invalid credentials"}

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return {"success": False, "error": str(e)}

    async def generate_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """Generate JWT token"""
        try:
            payload = {
                "user_id": user_data["user_id"],
                "username": user_data["username"],
                "role": user_data["role"],
                "permissions": user_data["permissions"],
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=24),
            }

            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            return token

        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            raise

    async def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return {"valid": True, "user_data": payload}

        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            return {"valid": False, "error": str(e)}

    async def check_permission(
        self, user_id: str, permission: str, resource: str = None
    ) -> bool:
        """Check if user has permission"""
        try:
            # Mock permission check - in production, this would check against user roles
            if user_id == "admin":
                return True
            elif user_id == "analyst":
                return permission in ["read", "write", "execute"]
            elif user_id == "viewer":
                return permission == "read"
            else:
                return False

        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False

    async def encrypt_data(self, data: str) -> str:
        """Encrypt data"""
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return encrypted_data.decode()

        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise

    async def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()

        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise

    async def hash_password(self, password: str) -> str:
        """Hash password"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode(), salt)
            return hashed.decode()

        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password"""
        try:
            return bcrypt.checkpw(password.encode(), hashed_password.encode())

        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    async def log_audit_event(
        self,
        event_type: str,
        user_id: str,
        action: str,
        details: str,
        classification: str = "unclassified",
    ) -> bool:
        """Log audit event"""
        try:
            audit_event = {
                "event_id": secrets.token_urlsafe(16),
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "user_id": user_id,
                "action": action,
                "details": details,
                "classification": classification,
                "ip_address": "127.0.0.1",  # Mock IP address
                "user_agent": "AMAS-System",
            }

            self.audit_log.append(audit_event)

            # In production, this would be stored in a secure audit database
            logger.info(f"Audit event logged: {event_type} - {action} by {user_id}")

            return True

        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return False

    async def get_audit_log(
        self,
        user_id: str = None,
        event_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> List[Dict[str, Any]]:
        """Get audit log"""
        try:
            filtered_log = self.audit_log.copy()

            if user_id:
                filtered_log = [
                    event for event in filtered_log if event["user_id"] == user_id
                ]

            if event_type:
                filtered_log = [
                    event for event in filtered_log if event["event_type"] == event_type
                ]

            if start_date:
                filtered_log = [
                    event
                    for event in filtered_log
                    if datetime.fromisoformat(event["timestamp"]) >= start_date
                ]

            if end_date:
                filtered_log = [
                    event
                    for event in filtered_log
                    if datetime.fromisoformat(event["timestamp"]) <= end_date
                ]

            return filtered_log

        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            return []

    async def classify_data(self, data: Dict[str, Any]) -> str:
        """Classify data based on content"""
        try:
            # Mock classification logic
            content = str(data).lower()

            if any(
                keyword in content for keyword in ["classified", "secret", "top secret"]
            ):
                return "classified"
            elif any(keyword in content for keyword in ["confidential", "internal"]):
                return "confidential"
            elif any(keyword in content for keyword in ["public", "open"]):
                return "public"
            else:
                return "unclassified"

        except Exception as e:
            logger.error(f"Error classifying data: {e}")
            return "unclassified"

    async def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for security"""
        try:
            sanitized_data = {}

            for key, value in data.items():
                if isinstance(value, str):
                    # Remove potentially dangerous characters
                    sanitized_value = value.replace("<script>", "").replace(
                        "</script>", ""
                    )
                    sanitized_value = sanitized_value.replace("javascript:", "")
                    sanitized_data[key] = sanitized_value
                else:
                    sanitized_data[key] = value

            return sanitized_data

        except Exception as e:
            logger.error(f"Error sanitizing data: {e}")
            return data

    async def health_check(self) -> Dict[str, Any]:
        """Check security service health"""
        try:
            return {
                "status": "healthy",
                "encryption_available": True,
                "jwt_available": True,
                "audit_logging": True,
                "access_control": True,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error checking security service health: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
