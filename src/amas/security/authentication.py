"""
Enhanced Authentication Module for AMAS
"""

import asyncio
import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import bcrypt
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

logger = logging.getLogger(__name__)


class AuthenticationManager:
    """Enhanced authentication manager for AMAS"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jwt_secret = config.get("security", {}).get(
            "jwt_secret", secrets.token_urlsafe(32)
        )
        self.jwt_algorithm = config.get("security", {}).get("jwt_algorithm", "HS256")
        self.jwt_expiration = config.get("security", {}).get(
            "jwt_expiration", 3600
        )  # 1 hour
        self.refresh_expiration = config.get("security", {}).get(
            "refresh_expiration", 86400 * 7
        )  # 7 days

        # Password hashing context
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12
        )

        # Rate limiting
        self.login_attempts = {}
        self.max_attempts = config.get("security", {}).get("max_login_attempts", 5)
        self.lockout_duration = config.get("security", {}).get(
            "lockout_duration", 900
        )  # 15 minutes

        # Session management
        self.active_sessions = {}
        self.max_sessions_per_user = config.get("security", {}).get(
            "max_sessions_per_user", 5
        )

    async def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_access_token(
        self, user_id: str, roles: List[str], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=self.jwt_expiration)

        to_encode = {
            "sub": str(user_id),
            "roles": roles,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }

        encoded_jwt = jwt.encode(
            to_encode, self.jwt_secret, algorithm=self.jwt_algorithm
        )
        return encoded_jwt

    async def create_refresh_token(
        self, user_id: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=self.refresh_expiration)

        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }

        encoded_jwt = jwt.encode(
            to_encode, self.jwt_secret, algorithm=self.jwt_algorithm
        )
        return encoded_jwt

    async def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token"""
        try:
            decoded_token = jwt.decode(
                token, self.jwt_secret, algorithms=[self.jwt_algorithm]
            )
            return decoded_token
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None

    async def authenticate_user(
        self, username: str, password: str, ip_address: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate a user with rate limiting"""
        # Check rate limiting
        if await self._is_rate_limited(username, ip_address):
            logger.warning(f"Rate limit exceeded for user {username} from {ip_address}")
            return None

        # In a real implementation, you would check against a database
        # For now, we'll use mock authentication
        if username == "admin" and password == "admin123":
            return {
                "user_id": "admin",
                "username": "admin",
                "roles": ["admin", "user"],
                "email": "admin@amas.local",
            }
        elif username == "user" and password == "user123":
            return {
                "user_id": "user",
                "username": "user",
                "roles": ["user"],
                "email": "user@amas.local",
            }

        # Record failed attempt
        await self._record_failed_attempt(username, ip_address)
        return None

    async def _is_rate_limited(self, username: str, ip_address: str) -> bool:
        """Check if user or IP is rate limited"""
        now = datetime.utcnow()
        key = f"{username}:{ip_address}"

        if key in self.login_attempts:
            attempts = self.login_attempts[key]
            # Remove old attempts
            attempts = [
                attempt
                for attempt in attempts
                if now - attempt < timedelta(seconds=self.lockout_duration)
            ]
            self.login_attempts[key] = attempts

            if len(attempts) >= self.max_attempts:
                return True

        return False

    async def _record_failed_attempt(self, username: str, ip_address: str):
        """Record a failed login attempt"""
        now = datetime.utcnow()
        key = f"{username}:{ip_address}"

        if key not in self.login_attempts:
            self.login_attempts[key] = []

        self.login_attempts[key].append(now)

    async def create_session(
        self, user_id: str, ip_address: str, user_agent: str
    ) -> str:
        """Create a new user session"""
        session_id = secrets.token_urlsafe(32)

        # Clean up old sessions for this user
        await self._cleanup_user_sessions(user_id)

        session_data = {
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
        }

        self.active_sessions[session_id] = session_data
        return session_id

    async def _cleanup_user_sessions(self, user_id: str):
        """Clean up old sessions for a user"""
        user_sessions = [
            (sid, session)
            for sid, session in self.active_sessions.items()
            if session["user_id"] == user_id
        ]

        if len(user_sessions) >= self.max_sessions_per_user:
            # Remove oldest sessions
            user_sessions.sort(key=lambda x: x[1]["created_at"])
            sessions_to_remove = user_sessions[: -self.max_sessions_per_user + 1]

            for session_id, _ in sessions_to_remove:
                del self.active_sessions[session_id]

    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate a session and return session data"""
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]

        # Check if session is expired (24 hours)
        if datetime.utcnow() - session["created_at"] > timedelta(hours=24):
            del self.active_sessions[session_id]
            return None

        # Update last activity
        session["last_activity"] = datetime.utcnow()
        return session

    async def revoke_session(self, session_id: str):
        """Revoke a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

    async def revoke_user_sessions(self, user_id: str):
        """Revoke all sessions for a user"""
        sessions_to_remove = [
            sid
            for sid, session in self.active_sessions.items()
            if session["user_id"] == user_id
        ]

        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]

    async def get_user_permissions(self, user_id: str, roles: List[str]) -> List[str]:
        """Get user permissions based on roles"""
        permissions = []

        for role in roles:
            if role == "admin":
                permissions.extend(
                    [
                        "read:all",
                        "write:all",
                        "delete:all",
                        "manage:users",
                        "manage:agents",
                        "manage:system",
                    ]
                )
            elif role == "user":
                permissions.extend(["read:own", "write:own", "submit:tasks"])
            elif role == "viewer":
                permissions.extend(["read:all"])

        return list(set(permissions))  # Remove duplicates

    async def check_permission(
        self, user_permissions: List[str], required_permission: str
    ) -> bool:
        """Check if user has required permission"""
        return required_permission in user_permissions

    async def generate_api_key(
        self, user_id: str, name: str, permissions: List[str]
    ) -> str:
        """Generate an API key for a user"""
        api_key = secrets.token_urlsafe(32)

        # In a real implementation, you would store this in a database
        # For now, we'll store it in memory
        key_data = {
            "user_id": user_id,
            "name": name,
            "permissions": permissions,
            "created_at": datetime.utcnow(),
            "last_used": None,
        }

        # Store API key (in production, use secure storage)
        self.api_keys = getattr(self, "api_keys", {})
        self.api_keys[api_key] = key_data

        return api_key

    async def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key"""
        if not hasattr(self, "api_keys") or api_key not in self.api_keys:
            return None

        key_data = self.api_keys[api_key]
        key_data["last_used"] = datetime.utcnow()

        return key_data

    async def revoke_api_key(self, api_key: str):
        """Revoke an API key"""
        if hasattr(self, "api_keys") and api_key in self.api_keys:
            del self.api_keys[api_key]

    async def get_security_events(
        self, user_id: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get security events for audit purposes"""
        events = []

        # Add login attempts
        for key, attempts in self.login_attempts.items():
            username, ip_address = key.split(":", 1)
            if not user_id or username == user_id:
                for attempt in attempts:
                    events.append(
                        {
                            "event_type": "login_attempt",
                            "user_id": username,
                            "ip_address": ip_address,
                            "timestamp": attempt.isoformat(),
                            "success": False,
                        }
                    )

        # Add active sessions
        for session_id, session in self.active_sessions.items():
            if not user_id or session["user_id"] == user_id:
                events.append(
                    {
                        "event_type": "active_session",
                        "user_id": session["user_id"],
                        "session_id": session_id,
                        "ip_address": session["ip_address"],
                        "timestamp": session["created_at"].isoformat(),
                    }
                )

        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x["timestamp"], reverse=True)

        return events[:limit]
