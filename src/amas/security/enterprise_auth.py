"""
Enterprise Authentication Module for AMAS
Implements SSO, LDAP/AD, MFA, and device-based authentication
"""

import asyncio
import base64
import hashlib
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode, urlparse

import httpx
import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class SSOProvider:
    """Base class for SSO providers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        self.scope = config.get("scope", "openid profile email")
        self.discovery_url = config.get("discovery_url")

    async def get_authorization_url(self, state: str) -> str:
        """Get authorization URL for OAuth flow"""
        raise NotImplementedError

    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from access token"""
        raise NotImplementedError


class SAMLProvider(SSOProvider):
    """SAML SSO provider implementation"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.entity_id = config.get("entity_id")
        self.sso_url = config.get("sso_url")
        self.slo_url = config.get("slo_url")
        self.certificate = config.get("certificate")
        self.private_key = config.get("private_key")

    async def get_authorization_url(self, state: str) -> str:
        """Generate SAML authentication request URL"""
        # In a real implementation, you would use a SAML library like python3-saml
        # For now, we'll create a mock implementation
        params = {
            "SAMLRequest": self._create_saml_request(),
            "RelayState": state,
        }
        return f"{self.sso_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, saml_response: str, state: str) -> Dict[str, Any]:
        """Process SAML response"""
        # Mock implementation - in reality, you'd parse and validate the SAML response
        return {
            "access_token": f"saml_token_{secrets.token_urlsafe(32)}",
            "token_type": "SAML",
            "expires_in": 3600,
        }

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Extract user info from SAML token"""
        # Mock implementation
        return {
            "sub": f"saml_user_{secrets.token_hex(8)}",
            "name": "SAML User",
            "email": "user@saml.example.com",
            "groups": ["users", "saml_users"],
        }

    def _create_saml_request(self) -> str:
        """Create SAML authentication request"""
        # Mock implementation
        return base64.b64encode(b"<samlp:AuthnRequest>...</samlp:AuthnRequest>").decode()


class OAuth2Provider(SSOProvider):
    """OAuth2 SSO provider implementation"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.authorization_url = config.get("authorization_url")
        self.token_url = config.get("token_url")
        self.userinfo_url = config.get("userinfo_url")

    async def get_authorization_url(self, state: str) -> str:
        """Get OAuth2 authorization URL"""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": state,
        }
        return f"{self.authorization_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from access token"""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(self.userinfo_url, headers=headers)
            response.raise_for_status()
            return response.json()


class LDAPProvider:
    """LDAP/Active Directory provider implementation"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.server = config.get("server")
        self.port = config.get("port", 389)
        self.use_ssl = config.get("use_ssl", False)
        self.base_dn = config.get("base_dn")
        self.bind_dn = config.get("bind_dn")
        self.bind_password = config.get("bind_password")
        self.user_search_filter = config.get("user_search_filter", "(uid={username})")
        self.group_search_filter = config.get("group_search_filter", "(member={user_dn})")

    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user against LDAP/AD"""
        try:
            # In a real implementation, you would use python-ldap or ldap3
            # For now, we'll create a mock implementation
            if self._mock_ldap_authenticate(username, password):
                return await self._get_user_info(username)
            return None
        except Exception as e:
            logger.error(f"LDAP authentication error: {e}")
            return None

    async def get_user_groups(self, user_dn: str) -> List[str]:
        """Get user groups from LDAP/AD"""
        # Mock implementation
        return ["users", "ldap_users"]

    def _mock_ldap_authenticate(self, username: str, password: str) -> bool:
        """Mock LDAP authentication for development"""
        # In production, replace with actual LDAP authentication
        return username == "ldap_user" and password == "ldap_password"

    async def _get_user_info(self, username: str) -> Dict[str, Any]:
        """Get user information from LDAP"""
        return {
            "sub": f"ldap_user_{username}",
            "username": username,
            "name": f"LDAP User {username}",
            "email": f"{username}@ldap.example.com",
            "groups": await self.get_user_groups(f"uid={username},{self.base_dn}"),
        }


class MFAProvider:
    """Multi-Factor Authentication provider"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.totp_secret_length = config.get("totp_secret_length", 32)
        self.totp_window = config.get("totp_window", 1)
        self.sms_provider = config.get("sms_provider", "mock")

    async def generate_totp_secret(self, user_id: str) -> str:
        """Generate TOTP secret for user"""
        return base64.b32encode(secrets.token_bytes(self.totp_secret_length)).decode()

    async def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=self.totp_window)
        except ImportError:
            logger.warning("pyotp not installed, using mock TOTP verification")
            # Mock implementation for development
            return token == "123456"

    async def send_sms_code(self, phone_number: str) -> str:
        """Send SMS verification code"""
        code = f"{secrets.randbelow(900000) + 100000:06d}"  # 6-digit code
        
        if self.sms_provider == "mock":
            logger.info(f"Mock SMS sent to {phone_number}: {code}")
        else:
            # In production, integrate with real SMS provider
            await self._send_real_sms(phone_number, code)
        
        return code

    async def _send_real_sms(self, phone_number: str, code: str):
        """Send real SMS (implement with actual SMS provider)"""
        # Implement with Twilio, AWS SNS, etc.
        pass

    async def verify_sms_code(self, phone_number: str, code: str, stored_code: str) -> bool:
        """Verify SMS code"""
        return code == stored_code


class DeviceAuthProvider:
    """Device-based authentication provider"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device_registration_required = config.get("device_registration_required", True)
        self.trusted_device_duration = config.get("trusted_device_duration", 30)  # days
        self.max_devices_per_user = config.get("max_devices_per_user", 5)

    async def register_device(self, user_id: str, device_info: Dict[str, Any]) -> str:
        """Register a new device for user"""
        device_id = self._generate_device_id(device_info)
        
        device_data = {
            "device_id": device_id,
            "user_id": user_id,
            "device_info": device_info,
            "registered_at": datetime.utcnow(),
            "last_used": datetime.utcnow(),
            "is_trusted": False,
        }
        
        # In production, store in database
        self._store_device(device_data)
        return device_id

    async def verify_device(self, user_id: str, device_id: str) -> bool:
        """Verify if device is registered and trusted"""
        device = self._get_device(device_id)
        if not device or device["user_id"] != user_id:
            return False
        
        # Update last used timestamp
        device["last_used"] = datetime.utcnow()
        self._store_device(device)
        
        return device.get("is_trusted", False)

    async def trust_device(self, user_id: str, device_id: str) -> bool:
        """Mark device as trusted"""
        device = self._get_device(device_id)
        if device and device["user_id"] == user_id:
            device["is_trusted"] = True
            self._store_device(device)
            return True
        return False

    def _generate_device_id(self, device_info: Dict[str, Any]) -> str:
        """Generate unique device ID based on device characteristics"""
        device_string = f"{device_info.get('user_agent', '')}{device_info.get('platform', '')}{device_info.get('browser', '')}"
        return hashlib.sha256(device_string.encode()).hexdigest()[:32]

    def _store_device(self, device_data: Dict[str, Any]):
        """Store device data (in production, use database)"""
        # Mock implementation
        pass

    def _get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device data (in production, use database)"""
        # Mock implementation
        return None


class EnterpriseAuthManager:
    """Enterprise authentication manager"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sso_providers = {}
        self.ldap_provider = None
        self.mfa_provider = None
        self.device_provider = None
        
        # Initialize providers based on configuration
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize authentication providers"""
        # Initialize SSO providers
        for provider_name, provider_config in self.config.get("sso_providers", {}).items():
            if provider_config.get("type") == "saml":
                self.sso_providers[provider_name] = SAMLProvider(provider_config)
            elif provider_config.get("type") == "oauth2":
                self.sso_providers[provider_name] = OAuth2Provider(provider_config)

        # Initialize LDAP provider
        if self.config.get("ldap"):
            self.ldap_provider = LDAPProvider(self.config["ldap"])

        # Initialize MFA provider
        if self.config.get("mfa"):
            self.mfa_provider = MFAProvider(self.config["mfa"])

        # Initialize device auth provider
        if self.config.get("device_auth"):
            self.device_provider = DeviceAuthProvider(self.config["device_auth"])

    async def authenticate_sso(self, provider_name: str, code: str, state: str) -> Optional[Dict[str, Any]]:
        """Authenticate user via SSO"""
        if provider_name not in self.sso_providers:
            logger.error(f"SSO provider {provider_name} not configured")
            return None

        provider = self.sso_providers[provider_name]
        
        try:
            # Exchange code for token
            token_data = await provider.exchange_code_for_token(code, state)
            access_token = token_data.get("access_token")
            
            if not access_token:
                logger.error("No access token received from SSO provider")
                return None

            # Get user information
            user_info = await provider.get_user_info(access_token)
            
            # Add provider information
            user_info["auth_provider"] = provider_name
            user_info["auth_method"] = "sso"
            
            return user_info

        except Exception as e:
            logger.error(f"SSO authentication error: {e}")
            return None

    async def authenticate_ldap(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user via LDAP/AD"""
        if not self.ldap_provider:
            logger.error("LDAP provider not configured")
            return None

        try:
            user_info = await self.ldap_provider.authenticate_user(username, password)
            if user_info:
                user_info["auth_provider"] = "ldap"
                user_info["auth_method"] = "ldap"
            return user_info

        except Exception as e:
            logger.error(f"LDAP authentication error: {e}")
            return None

    async def setup_mfa(self, user_id: str) -> Dict[str, Any]:
        """Setup MFA for user"""
        if not self.mfa_provider:
            raise ValueError("MFA provider not configured")

        totp_secret = await self.mfa_provider.generate_totp_secret(user_id)
        
        return {
            "totp_secret": totp_secret,
            "qr_code_url": f"otpauth://totp/AMAS:{user_id}?secret={totp_secret}&issuer=AMAS",
            "backup_codes": [secrets.token_hex(8) for _ in range(10)],
        }

    async def verify_mfa(self, user_id: str, totp_secret: str, token: str) -> bool:
        """Verify MFA token"""
        if not self.mfa_provider:
            return True  # MFA not required

        return await self.mfa_provider.verify_totp(totp_secret, token)

    async def register_device(self, user_id: str, device_info: Dict[str, Any]) -> str:
        """Register device for user"""
        if not self.device_provider:
            return "no_device_auth"

        return await self.device_provider.register_device(user_id, device_info)

    async def verify_device(self, user_id: str, device_id: str) -> bool:
        """Verify device for user"""
        if not self.device_provider:
            return True  # Device verification not required

        return await self.device_provider.verify_device(user_id, device_id)

    async def get_sso_authorization_url(self, provider_name: str, state: str) -> Optional[str]:
        """Get SSO authorization URL"""
        if provider_name not in self.sso_providers:
            return None

        return await self.sso_providers[provider_name].get_authorization_url(state)

    async def get_available_auth_methods(self) -> List[Dict[str, Any]]:
        """Get available authentication methods"""
        methods = []

        # Add SSO methods
        for provider_name, provider in self.sso_providers.items():
            methods.append({
                "name": provider_name,
                "type": "sso",
                "display_name": provider_name.upper(),
                "enabled": True,
            })

        # Add LDAP method
        if self.ldap_provider:
            methods.append({
                "name": "ldap",
                "type": "ldap",
                "display_name": "LDAP/Active Directory",
                "enabled": True,
            })

        # Add MFA method
        if self.mfa_provider:
            methods.append({
                "name": "mfa",
                "type": "mfa",
                "display_name": "Multi-Factor Authentication",
                "enabled": True,
            })

        return methods

    async def create_enterprise_session(
        self, 
        user_info: Dict[str, Any], 
        device_id: Optional[str] = None,
        mfa_verified: bool = False
    ) -> Dict[str, Any]:
        """Create enterprise session with all security features"""
        session_data = {
            "user_id": user_info["sub"],
            "username": user_info.get("username", user_info["sub"]),
            "email": user_info.get("email"),
            "roles": user_info.get("groups", []),
            "auth_provider": user_info.get("auth_provider"),
            "auth_method": user_info.get("auth_method"),
            "mfa_verified": mfa_verified,
            "device_id": device_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "session_id": secrets.token_urlsafe(32),
        }

        # Store session (in production, use database)
        self._store_session(session_data)
        
        return session_data

    def _store_session(self, session_data: Dict[str, Any]):
        """Store session data (in production, use database)"""
        # Mock implementation
        pass

    async def get_enterprise_user_permissions(self, user_info: Dict[str, Any]) -> List[str]:
        """Get enterprise user permissions based on roles and groups"""
        permissions = []
        roles = user_info.get("groups", [])
        
        # Map enterprise roles to permissions
        role_permissions = {
            "admin": ["read:all", "write:all", "delete:all", "manage:users", "manage:system"],
            "manager": ["read:all", "write:all", "manage:users", "manage:agents"],
            "analyst": ["read:all", "write:own", "submit:tasks", "execute:workflows"],
            "user": ["read:own", "write:own", "submit:tasks"],
            "viewer": ["read:all"],
            "ldap_users": ["read:own", "write:own"],
            "saml_users": ["read:own", "write:own"],
        }

        for role in roles:
            if role in role_permissions:
                permissions.extend(role_permissions[role])

        # Add enterprise-specific permissions
        if user_info.get("auth_provider") in ["saml", "oauth2"]:
            permissions.append("sso:authenticated")
        
        if user_info.get("auth_provider") == "ldap":
            permissions.append("ldap:authenticated")

        return list(set(permissions))  # Remove duplicates
