"""
Enhanced Authentication and Authorization System for AMAS
Implements JWT/OIDC with RBAC for production security
"""

import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from enum import Enum

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)


class TokenType(str, Enum):
    """Token types for JWT tokens"""
    ACCESS = "access"
    REFRESH = "refresh"
    API_KEY = "api_key"


class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    ANALYST = "analyst"
    MANAGER = "manager"


class Permission(str, Enum):
    """System permissions"""
    # User management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"
    
    # Agent management
    AGENT_READ = "agent:read"
    AGENT_WRITE = "agent:write"
    AGENT_DELETE = "agent:delete"
    AGENT_MANAGE = "agent:manage"
    AGENT_EXECUTE = "agent:execute"
    
    # Task management
    TASK_READ = "task:read"
    TASK_WRITE = "task:write"
    TASK_DELETE = "task:delete"
    TASK_SUBMIT = "task:submit"
    TASK_EXECUTE = "task:execute"
    
    # System management
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_MANAGE = "system:manage"
    SYSTEM_MONITOR = "system:monitor"
    
    # Data access
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"
    DATA_EXPORT = "data:export"
    
    # Security
    SECURITY_READ = "security:read"
    SECURITY_MANAGE = "security:manage"
    SECURITY_AUDIT = "security:audit"


class User(BaseModel):
    """User model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    full_name: Optional[str] = None
    roles: List[UserRole] = Field(default_factory=list)
    permissions: List[Permission] = Field(default_factory=list)
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None


class TokenData(BaseModel):
    """Token payload data"""
    sub: str  # user_id
    username: str
    roles: List[str]
    permissions: List[str]
    token_type: TokenType
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for token revocation


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class RolePermissionMatrix:
    """Role-based permission matrix"""
    
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: [
            Permission.USER_READ, Permission.USER_WRITE, Permission.USER_DELETE, Permission.USER_MANAGE,
            Permission.AGENT_READ, Permission.AGENT_WRITE, Permission.AGENT_DELETE, Permission.AGENT_MANAGE, Permission.AGENT_EXECUTE,
            Permission.TASK_READ, Permission.TASK_WRITE, Permission.TASK_DELETE, Permission.TASK_SUBMIT, Permission.TASK_EXECUTE,
            Permission.SYSTEM_READ, Permission.SYSTEM_WRITE, Permission.SYSTEM_MANAGE, Permission.SYSTEM_MONITOR,
            Permission.DATA_READ, Permission.DATA_WRITE, Permission.DATA_DELETE, Permission.DATA_EXPORT,
            Permission.SECURITY_READ, Permission.SECURITY_MANAGE, Permission.SECURITY_AUDIT,
        ],
        UserRole.MANAGER: [
            Permission.USER_READ, Permission.USER_WRITE,
            Permission.AGENT_READ, Permission.AGENT_WRITE, Permission.AGENT_EXECUTE,
            Permission.TASK_READ, Permission.TASK_WRITE, Permission.TASK_SUBMIT, Permission.TASK_EXECUTE,
            Permission.SYSTEM_READ, Permission.SYSTEM_MONITOR,
            Permission.DATA_READ, Permission.DATA_WRITE, Permission.DATA_EXPORT,
            Permission.SECURITY_READ,
        ],
        UserRole.ANALYST: [
            Permission.AGENT_READ, Permission.AGENT_EXECUTE,
            Permission.TASK_READ, Permission.TASK_SUBMIT, Permission.TASK_EXECUTE,
            Permission.SYSTEM_READ,
            Permission.DATA_READ, Permission.DATA_EXPORT,
        ],
        UserRole.USER: [
            Permission.AGENT_READ, Permission.AGENT_EXECUTE,
            Permission.TASK_READ, Permission.TASK_SUBMIT,
            Permission.DATA_READ,
        ],
        UserRole.VIEWER: [
            Permission.AGENT_READ,
            Permission.TASK_READ,
            Permission.DATA_READ,
        ],
    }
    
    @classmethod
    def get_permissions_for_roles(cls, roles: List[UserRole]) -> List[Permission]:
        """Get all permissions for given roles"""
        permissions = set()
        for role in roles:
            if role in cls.ROLE_PERMISSIONS:
                permissions.update(cls.ROLE_PERMISSIONS[role])
        return list(permissions)


class EnhancedAuthManager:
    """Enhanced authentication manager with JWT/OIDC and RBAC"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jwt_secret = config.get("jwt_secret_key", secrets.token_urlsafe(32))
        self.jwt_algorithm = config.get("jwt_algorithm", "HS256")
        self.access_token_expire_minutes = config.get("jwt_access_token_expire_minutes", 30)
        self.refresh_token_expire_days = config.get("jwt_refresh_token_expire_days", 7)
        
        # Password hashing
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto", 
            bcrypt__rounds=config.get("bcrypt_rounds", 12)
        )
        
        # Rate limiting
        self.login_attempts: Dict[str, List[datetime]] = {}
        self.max_attempts = config.get("max_login_attempts", 5)
        self.lockout_duration = config.get("lockout_duration", 900)  # 15 minutes
        
        # Session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.revoked_tokens: set = set()
        
        # User storage (in production, use database)
        self.users: Dict[str, User] = {}
        self._initialize_default_users()

    def _initialize_default_users(self):
        """Initialize default users for development"""
        # Admin user
        admin_user = User(
            username="admin",
            email="admin@amas.local",
            full_name="System Administrator",
            roles=[UserRole.ADMIN],
            is_active=True,
            is_verified=True
        )
        admin_user.permissions = RolePermissionMatrix.get_permissions_for_roles(admin_user.roles)
        self.users["admin"] = admin_user
        
        # Regular user
        user = User(
            username="user",
            email="user@amas.local",
            full_name="Regular User",
            roles=[UserRole.USER],
            is_active=True,
            is_verified=True
        )
        user.permissions = RolePermissionMatrix.get_permissions_for_roles(user.roles)
        self.users["user"] = user

    async def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_access_token(
        self, 
        user: User, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        token_data = TokenData(
            sub=user.id,
            username=user.username,
            roles=[role.value for role in user.roles],
            permissions=[perm.value for perm in user.permissions],
            token_type=TokenType.ACCESS,
            exp=expire,
            iat=datetime.utcnow(),
            jti=str(uuid.uuid4())
        )

        encoded_jwt = jwt.encode(
            token_data.dict(), 
            self.jwt_secret, 
            algorithm=self.jwt_algorithm
        )
        return encoded_jwt

    async def create_refresh_token(
        self, 
        user: User, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        token_data = TokenData(
            sub=user.id,
            username=user.username,
            roles=[role.value for role in user.roles],
            permissions=[perm.value for perm in user.permissions],
            token_type=TokenType.REFRESH,
            exp=expire,
            iat=datetime.utcnow(),
            jti=str(uuid.uuid4())
        )

        encoded_jwt = jwt.encode(
            token_data.dict(), 
            self.jwt_secret, 
            algorithm=self.jwt_algorithm
        )
        return encoded_jwt

    async def decode_token(self, token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token"""
        try:
            # Check if token is revoked
            if token in self.revoked_tokens:
                logger.warning("Attempted to use revoked token")
                return None

            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.jwt_algorithm]
            )
            
            token_data = TokenData(**payload)
            
            # Check if token is expired
            if token_data.exp < datetime.utcnow():
                logger.warning("Token has expired")
                return None
                
            return token_data
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None

    async def authenticate_user(
        self, 
        username: str, 
        password: str, 
        ip_address: str
    ) -> Optional[User]:
        """Authenticate a user with rate limiting and account lockout"""
        # Check rate limiting
        if await self._is_rate_limited(username, ip_address):
            logger.warning(f"Rate limit exceeded for user {username} from {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )

        # Get user
        user = self.users.get(username)
        if not user:
            await self._record_failed_attempt(username, ip_address)
            return None

        # Check if user is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            logger.warning(f"User {username} is locked until {user.locked_until}")
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to too many failed attempts."
            )

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user {username} attempted to login")
            return None

        # Verify password (in production, get from database)
        # For now, use environment variables for default passwords
        import os
        admin_password = os.environ.get("AMAS_ADMIN_PASSWORD", "admin123")
        user_password = os.environ.get("AMAS_USER_PASSWORD", "user123")
        
        expected_password = None
        if username == "admin":
            expected_password = admin_password
        elif username == "user":
            expected_password = user_password
        
        if not expected_password or password != expected_password:
            await self._record_failed_attempt(username, ip_address)
            user.failed_login_attempts += 1
            
            # Lock account after max attempts
            if user.failed_login_attempts >= self.max_attempts:
                user.locked_until = datetime.utcnow() + timedelta(seconds=self.lockout_duration)
                logger.warning(f"User {username} locked due to too many failed attempts")
            
            return None

        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        
        return user

    async def _is_rate_limited(self, username: str, ip_address: str) -> bool:
        """Check if user or IP is rate limited"""
        now = datetime.utcnow()
        key = f"{username}:{ip_address}"

        if key in self.login_attempts:
            attempts = self.login_attempts[key]
            # Remove old attempts
            attempts = [
                attempt for attempt in attempts
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

    async def login(self, login_request: LoginRequest, ip_address: str) -> TokenResponse:
        """Perform user login and return tokens"""
        user = await self.authenticate_user(
            login_request.username, 
            login_request.password, 
            ip_address
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Create tokens
        access_token = await self.create_access_token(user)
        refresh_token = await self.create_refresh_token(user)

        # Create session
        session_id = await self.create_session(user.id, ip_address, "web")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_expire_minutes * 60,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "roles": [role.value for role in user.roles],
                "permissions": [perm.value for perm in user.permissions],
                "session_id": session_id
            }
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        token_data = await self.decode_token(refresh_token)
        
        if not token_data or token_data.token_type != TokenType.REFRESH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = self.users.get(token_data.sub)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new access token
        access_token = await self.create_access_token(user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Keep the same refresh token
            expires_in=self.access_token_expire_minutes * 60,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "roles": [role.value for role in user.roles],
                "permissions": [perm.value for perm in user.permissions]
            }
        )

    async def create_session(
        self, 
        user_id: str, 
        ip_address: str, 
        user_agent: str
    ) -> str:
        """Create a new user session"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
        }

        self.active_sessions[session_id] = session_data
        return session_id

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

    async def revoke_token(self, token: str):
        """Revoke a token"""
        self.revoked_tokens.add(token)

    async def revoke_user_tokens(self, user_id: str):
        """Revoke all tokens for a user"""
        # In production, maintain a token blacklist in Redis
        pass

    async def check_permission(
        self, 
        user_permissions: List[str], 
        required_permission: Union[str, Permission]
    ) -> bool:
        """Check if user has required permission"""
        if isinstance(required_permission, Permission):
            required_permission = required_permission.value
        return required_permission in user_permissions

    async def check_role(
        self, 
        user_roles: List[str], 
        required_role: Union[str, UserRole]
    ) -> bool:
        """Check if user has required role"""
        if isinstance(required_role, UserRole):
            required_role = required_role.value
        return required_role in user_roles

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username)

    async def create_user(
        self, 
        username: str, 
        email: str, 
        password: str, 
        roles: List[UserRole] = None,
        full_name: str = None
    ) -> User:
        """Create a new user"""
        if username in self.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        if roles is None:
            roles = [UserRole.USER]

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            roles=roles,
            is_active=True,
            is_verified=False
        )
        
        user.permissions = RolePermissionMatrix.get_permissions_for_roles(user.roles)
        self.users[username] = user
        
        return user

    async def update_user_roles(self, user_id: str, roles: List[UserRole]) -> bool:
        """Update user roles"""
        user = self.users.get(user_id)
        if not user:
            return False

        user.roles = roles
        user.permissions = RolePermissionMatrix.get_permissions_for_roles(roles)
        return True

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user"""
        user = self.users.get(user_id)
        if not user:
            return False

        user.is_active = False
        await self.revoke_user_tokens(user_id)
        return True

    async def get_security_events(
        self, 
        user_id: Optional[str] = None, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get security events for audit purposes"""
        events = []

        # Add login attempts
        for key, attempts in self.login_attempts.items():
            username, ip_address = key.split(":", 1)
            if not user_id or username == user_id:
                for attempt in attempts:
                    events.append({
                        "event_type": "login_attempt",
                        "user_id": username,
                        "ip_address": ip_address,
                        "timestamp": attempt.isoformat(),
                        "success": False,
                    })

        # Add active sessions
        for session_id, session in self.active_sessions.items():
            if not user_id or session["user_id"] == user_id:
                events.append({
                    "event_type": "active_session",
                    "user_id": session["user_id"],
                    "session_id": session_id,
                    "ip_address": session["ip_address"],
                    "timestamp": session["created_at"].isoformat(),
                })

        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x["timestamp"], reverse=True)
        return events[:limit]


# Global auth manager instance
auth_manager: Optional[EnhancedAuthManager] = None


def get_auth_manager() -> EnhancedAuthManager:
    """Get the global auth manager instance"""
    global auth_manager
    if auth_manager is None:
        from src.config.settings import get_settings
        settings = get_settings()
        auth_manager = EnhancedAuthManager(settings.security.dict())
    return auth_manager


# FastAPI security scheme
security_scheme = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> User:
    """Get current authenticated user from JWT token"""
    auth_manager = get_auth_manager()
    
    token_data = await auth_manager.decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await auth_manager.get_user_by_id(token_data.sub)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    return user


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_permission(permission: Union[str, Permission]):
    """Decorator to require specific permission"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs or dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            auth_manager = get_auth_manager()
            has_permission = await auth_manager.check_permission(
                current_user.permissions, 
                permission
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: Union[str, UserRole]):
    """Decorator to require specific role"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            auth_manager = get_auth_manager()
            has_role = await auth_manager.check_role(
                current_user.roles, 
                role
            )
            
            if not has_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator