"""
OIDC/JWT Authentication Middleware for AMAS

Provides enterprise-grade authentication with JWKS caching,
token validation, and comprehensive security headers.
"""

import jwt
import httpx
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List, Any
from functools import lru_cache
from fastapi import HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import hashlib

logger = logging.getLogger(__name__)

class JWTMiddleware:
    """JWT authentication middleware with OIDC provider integration"""
    
    def __init__(self, 
                 issuer: str, 
                 audience: str, 
                 jwks_uri: str,
                 cache_ttl: int = 3600,
                 algorithms: List[str] = None):
        self.issuer = issuer
        self.audience = audience
        self.jwks_uri = jwks_uri
        self.cache_ttl = cache_ttl
        self.algorithms = algorithms or ['RS256']
        self._jwks_cache = {}
        self._cache_timestamp = None
        self._cache_lock = asyncio.Lock()
        
        logger.info(f"JWT Middleware initialized for issuer: {issuer}")
    
    async def get_jwks(self) -> Dict:
        """Fetch and cache JWKS from OIDC provider with thread-safe caching"""
        now = datetime.now(timezone.utc)
        
        async with self._cache_lock:
            # Check if cache is still valid
            if (self._cache_timestamp is not None and 
                (now - self._cache_timestamp).seconds < self.cache_ttl and
                self._jwks_cache):
                return self._jwks_cache
            
            try:
                logger.debug(f"Fetching JWKS from {self.jwks_uri}")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(self.jwks_uri)
                    response.raise_for_status()
                    
                    self._jwks_cache = response.json()
                    self._cache_timestamp = now
                    
                    logger.info(f"JWKS cache updated with {len(self._jwks_cache.get('keys', []))} keys")
                    return self._jwks_cache
                    
            except Exception as e:
                logger.error(f"Failed to fetch JWKS: {e}")
                # Return cached keys if available, even if expired
                if self._jwks_cache:
                    logger.warning("Using expired JWKS cache due to fetch failure")
                    return self._jwks_cache
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Unable to validate tokens - JWKS unavailable"
                )
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return verified claims"""
        try:
            # Decode header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            alg = unverified_header.get('alg')
            
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing 'kid' header",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            if alg not in self.algorithms:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Unsupported algorithm: {alg}",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Get public key from JWKS
            jwks = await self.get_jwks()
            key = None
            
            for jwk in jwks.get('keys', []):
                if jwk.get('kid') == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                    break
            
            if not key:
                logger.warning(f"No matching key found for kid: {kid}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate signing key",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Validate token with all standard claims
            payload = jwt.decode(
                token,
                key,
                algorithms=self.algorithms,
                issuer=self.issuer,
                audience=self.audience,
                options={
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_nbf": True,
                    "require": ["exp", "iat", "sub"]
                }
            )
            
            # Additional validation
            if 'sub' not in payload or not payload['sub']:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing subject claim",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Check token age (optional security measure)
            iat = payload.get('iat')
            if iat:
                token_age = datetime.now(timezone.utc) - datetime.fromtimestamp(iat, tz=timezone.utc)
                if token_age.days > 30:  # Reject tokens older than 30 days
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token too old",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
            
            logger.debug(f"Token validated successfully for subject: {payload.get('sub')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token validation failed: expired signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidAudienceError:
            logger.warning(f"Token validation failed: invalid audience (expected: {self.audience})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token audience mismatch",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidIssuerError:
            logger.warning(f"Token validation failed: invalid issuer (expected: {self.issuer})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token issuer mismatch",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token validation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token validation failed"
            )
    
    async def extract_user_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user context from validated JWT payload"""
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "roles": payload.get("roles", []),
            "scopes": payload.get("scope", "").split() if payload.get("scope") else [],
            "organization": payload.get("org"),
            "groups": payload.get("groups", []),
            "iat": payload.get("iat"),
            "exp": payload.get("exp"),
            "token_id": payload.get("jti")
        }

class SecurityHeadersMiddleware:
    """Middleware to add comprehensive security headers"""
    
    def __init__(self):
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            )
        }
    
    async def add_security_headers(self, request: Request, response: Response):
        """Add all security headers to response"""
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Add cache control for sensitive endpoints
        if any(path in str(request.url) for path in ["/api/", "/auth/", "/admin/"]):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

class AuthenticationContext:
    """Thread-local authentication context"""
    
    def __init__(self):
        self._context = {}
    
    def set_user(self, user_context: Dict[str, Any]):
        """Set current user context"""
        self._context = user_context
    
    def get_user(self) -> Optional[Dict[str, Any]]:
        """Get current user context"""
        return self._context.copy() if self._context else None
    
    def get_user_id(self) -> Optional[str]:
        """Get current user ID"""
        return self._context.get("user_id")
    
    def get_user_roles(self) -> List[str]:
        """Get current user roles"""
        return self._context.get("roles", [])
    
    def get_user_scopes(self) -> List[str]:
        """Get current user scopes"""
        return self._context.get("scopes", [])
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return role in self.get_user_roles()
    
    def has_scope(self, scope: str) -> bool:
        """Check if user has specific scope"""
        return scope in self.get_user_scopes()
    
    def clear(self):
        """Clear authentication context"""
        self._context = {}

# Global authentication context
auth_context = AuthenticationContext()

class AMASHTTPBearer(HTTPBearer):
    """Custom HTTP Bearer authentication for AMAS"""
    
    def __init__(self, jwt_middleware: JWTMiddleware):
        super().__init__(auto_error=True)
        self.jwt_middleware = jwt_middleware
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        """Authenticate request and set user context"""
        credentials = await super().__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate token
        payload = await self.jwt_middleware.validate_token(credentials.credentials)
        
        # Extract and set user context
        user_context = await self.jwt_middleware.extract_user_context(payload)
        auth_context.set_user(user_context)
        
        # Add user info to request state
        request.state.user = user_context
        request.state.authenticated = True
        
        logger.info(f"Authenticated user: {user_context.get('user_id')} with roles: {user_context.get('roles')}")
        
        return credentials

def require_role(required_role: str):
    """Decorator to require specific role for endpoint access"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_context = auth_context.get_user()
            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_roles = user_context.get("roles", [])
            if required_role not in user_roles:
                logger.warning(f"Access denied: user {user_context.get('user_id')} "
                             f"lacks required role {required_role}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required role '{required_role}' not found"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_scope(required_scope: str):
    """Decorator to require specific OAuth scope for endpoint access"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_context = auth_context.get_user()
            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_scopes = user_context.get("scopes", [])
            if required_scope not in user_scopes:
                logger.warning(f"Access denied: user {user_context.get('user_id')} "
                             f"lacks required scope {required_scope}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required scope '{required_scope}' not found"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class TokenBlacklist:
    """Simple in-memory token blacklist for logout/revocation"""
    
    def __init__(self, cleanup_interval: int = 3600):
        self._blacklisted_tokens: Dict[str, datetime] = {}
        self.cleanup_interval = cleanup_interval
        self._last_cleanup = datetime.now(timezone.utc)
    
    def blacklist_token(self, token_jti: str, exp_timestamp: int):
        """Add token to blacklist"""
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        self._blacklisted_tokens[token_jti] = exp_datetime
        logger.info(f"Token blacklisted: {token_jti[:8]}...")
    
    def is_blacklisted(self, token_jti: str) -> bool:
        """Check if token is blacklisted"""
        # Clean up expired tokens periodically
        self._cleanup_expired()
        return token_jti in self._blacklisted_tokens
    
    def _cleanup_expired(self):
        """Remove expired tokens from blacklist"""
        now = datetime.now(timezone.utc)
        
        # Only cleanup if enough time has passed
        if (now - self._last_cleanup).seconds < self.cleanup_interval:
            return
        
        expired_tokens = [
            jti for jti, exp_time in self._blacklisted_tokens.items()
            if now > exp_time
        ]
        
        for jti in expired_tokens:
            del self._blacklisted_tokens[jti]
        
        if expired_tokens:
            logger.debug(f"Cleaned up {len(expired_tokens)} expired blacklisted tokens")
        
        self._last_cleanup = now

# Global token blacklist instance
token_blacklist = TokenBlacklist()

class SecureAuthenticationManager:
    """Complete authentication management system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        auth_config = config.get("authentication", {})
        
        # Initialize JWT middleware
        oidc_config = auth_config.get("oidc", {})
        self.jwt_middleware = JWTMiddleware(
            issuer=oidc_config.get("issuer"),
            audience=oidc_config.get("audience"),
            jwks_uri=oidc_config.get("jwks_uri"),
            cache_ttl=oidc_config.get("cache_ttl", 3600)
        )
        
        # Initialize security headers
        self.security_headers = SecurityHeadersMiddleware()
        
        # Initialize HTTP Bearer authentication
        self.http_bearer = AMASHTTPBearer(self.jwt_middleware)
        
        logger.info("Secure Authentication Manager initialized")
    
    async def authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Authenticate incoming request"""
        try:
            credentials = await self.http_bearer(request)
            return auth_context.get_user()
        except HTTPException:
            # Re-raise authentication errors
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    async def logout_user(self, token: str):
        """Logout user by blacklisting their token"""
        try:
            # Decode token without verification to get JTI
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            jti = unverified_payload.get("jti")
            exp = unverified_payload.get("exp")
            
            if jti and exp:
                token_blacklist.blacklist_token(jti, exp)
                logger.info(f"User logged out successfully")
            else:
                logger.warning("Token logout failed: missing JTI or EXP claims")
                
        except Exception as e:
            logger.error(f"Logout error: {e}")
            # Don't raise exception for logout errors
    
    def create_auth_dependency(self):
        """Create FastAPI dependency for authentication"""
        return self.http_bearer
    
    def get_current_user_dependency(self):
        """Create FastAPI dependency to get current user"""
        def get_current_user() -> Dict[str, Any]:
            user = auth_context.get_user()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No authenticated user context"
                )
            return user
        return get_current_user

# Example FastAPI integration
"""
from fastapi import FastAPI, Depends
from src.amas.security.auth.jwt_middleware import SecureAuthenticationManager

# Initialize authentication
auth_config = {
    "authentication": {
        "oidc": {
            "issuer": "https://your-oidc-provider.com",
            "audience": "amas-api",
            "jwks_uri": "https://your-oidc-provider.com/.well-known/jwks.json"
        }
    }
}

auth_manager = SecureAuthenticationManager(auth_config)
app = FastAPI()

# Protected endpoint example
@app.get("/api/v1/agents")
async def list_agents(current_user: dict = Depends(auth_manager.get_current_user_dependency())):
    return {
        "message": f"Hello {current_user['name']}!",
        "agents": ["research_agent", "analysis_agent"]
    }

# Role-protected endpoint example
@app.post("/api/v1/agents/execute")
@require_role("agent_user")
async def execute_agent(
    request: dict,
    current_user: dict = Depends(auth_manager.get_current_user_dependency())
):
    return {"status": "executing", "user": current_user["user_id"]}
"""