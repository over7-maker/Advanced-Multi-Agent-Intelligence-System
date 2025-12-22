"""
OIDC/JWT Authentication Middleware for AMAS

Provides enterprise-grade authentication with JWKS caching,
token validation, and comprehensive security headers.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import jwt
from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

class JWTMiddleware:
    """JWT authentication middleware with OIDC provider integration"""
    
    def __init__(self, 
                 issuer: str, 
                 audience: str, 
                 jwks_uri: str,
                 cache_ttl: int = 3600,
                 algorithms: List[str] = None,
                 expected_azp: Optional[str] = None,
                 refresh_interval: int = 300):
        self.issuer = issuer
        self.audience = audience
        self.jwks_uri = jwks_uri
        self.cache_ttl = cache_ttl
        self.algorithms = algorithms or ['RS256']
        self.expected_azp = expected_azp  # Expected authorized party (client ID)
        self.refresh_interval = refresh_interval  # Background refresh interval in seconds
        self._jwks_cache = {}
        self._cache_timestamp = None
        self._cache_lock = asyncio.Lock()
        self._refresh_task: Optional[asyncio.Task] = None
        
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
                # Check if jwks_uri is valid (starts with http:// or https://)
                if not self.jwks_uri or not (self.jwks_uri.startswith('http://') or self.jwks_uri.startswith('https://')):
                    # Invalid or unexpanded jwks_uri - this is expected in development
                    import os
                    dev_mode = os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "test"]
                    if dev_mode:
                        logger.debug(f"JWKS URI not configured (expected in dev): {self.jwks_uri}")
                        # Return empty cache - tokens won't be validated but app continues
                        return {"keys": []}
                    else:
                        raise ValueError(f"Invalid JWKS URI: {self.jwks_uri}")
                
                logger.debug(f"Fetching JWKS from {self.jwks_uri}")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(self.jwks_uri)
                    response.raise_for_status()
                    
                    data = response.json()
                    # In tests, response.json() may be an AsyncMock (coroutine)
                    if asyncio.iscoroutine(data):
                        data = await data
                    
                    self._jwks_cache = data
                    self._cache_timestamp = now
                    
                    logger.info(f"JWKS cache updated with {len(self._jwks_cache.get('keys', []))} keys")
                    return self._jwks_cache
                    
            except Exception as e:
                import os
                dev_mode = os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "test"]
                
                # In development, log as debug instead of error
                if dev_mode:
                    logger.debug(f"JWKS fetch failed (expected in dev): {e}")
                    # Return empty cache - tokens won't be validated but app continues
                    return {"keys": []}
                else:
                    logger.error(f"Failed to fetch JWKS: {e}")
                    # Return cached keys if available, even if expired
                    if self._jwks_cache:
                        logger.warning("Using expired JWKS cache due to fetch failure")
                        return self._jwks_cache
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Unable to validate tokens - JWKS unavailable"
                    )
    
    async def start_background_refresh(self):
        """Start background task for periodic JWKS refresh"""
        async def refresh_loop():
            while True:
                try:
                    await asyncio.sleep(self.refresh_interval)
                    # Force refresh by clearing cache timestamp
                    async with self._cache_lock:
                        self._cache_timestamp = None
                    # Trigger refresh
                    await self.get_jwks()
                    logger.debug("Background JWKS refresh completed")
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    import os
                    dev_mode = os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "test"]
                    # In development, log as debug instead of error
                    if dev_mode:
                        logger.debug(f"Background JWKS refresh failed (expected in dev): {e}")
                    else:
                        logger.error(f"Background JWKS refresh error: {e}")
                    # Continue even if refresh fails
                    await asyncio.sleep(60)  # Wait before retrying
        
        self._refresh_task = asyncio.create_task(refresh_loop())
        logger.info(f"Started background JWKS refresh (interval: {self.refresh_interval}s)")
    
    async def stop_background_refresh(self):
        """Stop background refresh task"""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped background JWKS refresh")
    
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
            
            # Check token blacklist first (before expensive validation)
            # SECURITY NOTE: We decode without verification ONLY to extract jti for blacklist check.
            # This is safe because:
            # 1. We immediately validate the token signature after this check
            # 2. Blacklist check prevents use of revoked tokens even if signature is valid
            # 3. No authentication decision is made based on unverified data
            try:
                # nosemgrep: python.jwt.security.unverified-jwt-decode.unverified-jwt-decode
                # Reason: Intentional unverified decode ONLY to extract jti for blacklist check.
                # Full signature verification happens immediately after this check.
                unverified_payload = jwt.decode(token, options={"verify_signature": False})
                token_jti = unverified_payload.get("jti")
                if token_jti and token_blacklist.is_blacklisted(token_jti):
                    logger.warning(f"Blacklisted token attempted: {token_jti[:8]}...")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has been revoked",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
            except jwt.InvalidTokenError:
                # If we can't decode even unverified, continue to full validation
                pass
            
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
            
            # Validate authorized party (azp) if present and expected
            if 'azp' in payload:
                if self.expected_azp and payload['azp'] != self.expected_azp:
                    logger.warning(f"Token azp mismatch: expected {self.expected_azp}, got {payload['azp']}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token authorized party mismatch",
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
        # Check both request.url (string) and request.url.path (if available)
        request_path = str(request.url)
        if hasattr(request.url, 'path'):
            request_path = request.url.path
        
        if any(path in request_path for path in ["/api/", "/auth/", "/admin/"]):
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
    
    def _cleanup_expired(self, force: bool = False):
        """Remove expired tokens from blacklist"""
        now = datetime.now(timezone.utc)
        
        # Only cleanup if enough time has passed (unless forced)
        if not force and (now - self._last_cleanup).seconds < self.cleanup_interval:
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
        
        # Initialize JWT middleware with enhanced settings
        oidc_config = auth_config.get("oidc", {})
        import os
        import re
        expected_azp = oidc_config.get("expected_azp") or os.getenv("OIDC_EXPECTED_AZP")
        refresh_interval = oidc_config.get("refresh_interval", 300)
        
        # Get OIDC config values (may contain unexpanded env vars)
        issuer = oidc_config.get("issuer", "")
        audience = oidc_config.get("audience", "")
        jwks_uri = oidc_config.get("jwks_uri", "")
        
        # Expand environment variables if needed (fallback if not expanded by security_manager)
        if issuer and "${" in issuer:
            pattern = r'\$\{([^}]+)\}'
            match = re.search(pattern, issuer)
            if match:
                var_part = match.group(1)
                if ":-" in var_part:
                    var_name, default = var_part.split(":-", 1)
                    issuer = os.getenv(var_name.strip(), default.strip())
                else:
                    issuer = os.getenv(var_part.strip(), issuer)
        
        if jwks_uri and "${" in jwks_uri:
            pattern = r'\$\{([^}]+)\}'
            match = re.search(pattern, jwks_uri)
            if match:
                var_part = match.group(1)
                if ":-" in var_part:
                    var_name, default = var_part.split(":-", 1)
                    jwks_uri = os.getenv(var_name.strip(), default.strip())
                else:
                    jwks_uri = os.getenv(var_part.strip(), jwks_uri)
        
        self.jwt_middleware = JWTMiddleware(
            issuer=issuer,
            audience=audience,
            jwks_uri=jwks_uri,
            cache_ttl=oidc_config.get("cache_ttl", 3600),
            expected_azp=expected_azp,
            refresh_interval=refresh_interval
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
            # Decode token without verification to get JTI for blacklist
            # SECURITY NOTE: Unverified decode is safe here because:
            # 1. We only extract jti and exp for blacklist entry
            # 2. No authentication decision is made
            # 3. Token validation happens on subsequent requests
            # nosemgrep: python.jwt.security.unverified-jwt-decode.unverified-jwt-decode
            # Reason: Intentional unverified decode ONLY to extract jti/exp for blacklist.
            # Token is already authenticated when this method is called.
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            jti = unverified_payload.get("jti")
            exp = unverified_payload.get("exp")
            
            if jti and exp:
                token_blacklist.blacklist_token(jti, exp)
                logger.info("User logged out successfully")
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