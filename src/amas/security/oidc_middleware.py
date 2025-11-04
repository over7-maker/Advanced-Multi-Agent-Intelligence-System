"""
OIDC/JWT Authentication Middleware for FastAPI
Implements JWKS caching, audience/issuer verification, and key rotation
"""

import logging
import time
from typing import Dict, Optional

import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class JWKSCache:
    """JWKS cache with automatic refresh"""

    def __init__(self, jwks_url: str, cache_ttl: int = 3600):
        self.jwks_url = jwks_url
        self.cache_ttl = cache_ttl
        self.keys: Dict[str, Dict] = {}
        self.last_fetch: float = 0

    async def get_keys(self) -> Dict[str, Dict]:
        """Get JWKS keys, refreshing if needed"""
        now = time.time()
        if now - self.last_fetch > self.cache_ttl or not self.keys:
            await self._fetch_keys()
        return self.keys

    async def _fetch_keys(self):
        """Fetch JWKS from issuer"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_url, timeout=10.0)
                response.raise_for_status()
                jwks = response.json()
                self.keys = {key["kid"]: key for key in jwks.get("keys", [])}
                self.last_fetch = time.time()
                logger.info(f"Refreshed JWKS cache with {len(self.keys)} keys")
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            if not self.keys:
                raise

    def get_key(self, kid: Optional[str]) -> Optional[rsa.RSAPublicKey]:
        """Get public key by kid"""
        if not kid or kid not in self.keys:
            return None

        key_data = self.keys[kid]
        try:
            # Convert JWK to RSA public key
            # In production, use cryptography.jose or similar
            # This is a simplified implementation
            return self._jwk_to_rsa(key_data)
        except Exception as e:
            logger.error(f"Failed to convert JWK to RSA: {e}")
            return None

    def _jwk_to_rsa(self, jwk: Dict) -> rsa.RSAPublicKey:
        """Convert JWK to RSA public key"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization

        # Extract modulus and exponent
        n = int.from_bytes(
            jwt.utils.base64url_decode(jwk["n"]), byteorder="big"
        )
        e = int.from_bytes(
            jwt.utils.base64url_decode(jwk["e"]), byteorder="big"
        )

        # Construct RSA public key
        public_numbers = rsa.RSAPublicNumbers(e, n)
        return public_numbers.public_key()


class OIDCAuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for OIDC/JWT authentication with JWKS verification"""

    def __init__(
        self,
        app,
        issuer: str,
        audience: str,
        jwks_url: Optional[str] = None,
        skip_paths: Optional[list] = None,
        auto_error: bool = True,
    ):
        super().__init__(app)
        self.issuer = issuer
        self.audience = audience
        self.jwks_url = jwks_url or f"{issuer}/.well-known/jwks.json"
        self.skip_paths = skip_paths or ["/health", "/metrics", "/docs", "/openapi.json"]
        self.auto_error = auto_error
        self.jwks_cache = JWKSCache(self.jwks_url)

        # Security scheme
        self.security = HTTPBearer(auto_error=auto_error)

    async def dispatch(self, request: Request, call_next):
        """Process request with OIDC authentication"""

        # Skip authentication for health/metrics/docs endpoints
        if any(request.url.path.startswith(path) for path in self.skip_paths):
            return await call_next(request)

        # Extract token from Authorization header
        credentials: Optional[HTTPAuthorizationCredentials] = None
        try:
            credentials = await self.security(request)
        except HTTPException:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authentication token",
                )
            # Continue without authentication if auto_error is False
            return await call_next(request)

        if not credentials:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing authentication token",
                )
            return await call_next(request)

        # Verify JWT token
        try:
            payload = await self._verify_token(credentials.credentials)
            request.state.user = payload
            request.state.auth_token = credentials.credentials
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid authentication token: {str(e)}",
                )

        return await call_next(request)

    async def _verify_token(self, token: str) -> Dict:
        """Verify JWT token with JWKS"""
        try:
            # Decode token header to get kid (without verification)
            # This is safe because we:
            # 1. Only extract the 'kid' from the header to fetch the correct key
            # 2. Perform full verification with the correct key in the next step
            # 3. Never trust this unverified payload - we verify it below
            # nosemgrep: python.jwt.security.unverified-jwt-decode.unverified-jwt-decode
            unverified = jwt.decode(
                token, options={"verify_signature": False}
            )

            # Verify issuer
            if unverified.get("iss") != self.issuer:
                raise ValueError(f"Issuer mismatch: expected {self.issuer}")

            # Verify audience
            aud = unverified.get("aud")
            if aud and self.audience not in (aud if isinstance(aud, list) else [aud]):
                raise ValueError(f"Audience mismatch: expected {self.audience}")

            # Get key from JWKS
            kid = jwt.get_unverified_header(token).get("kid")
            public_key = await self._get_public_key(kid)
            if not public_key:
                raise ValueError(f"Key not found for kid: {kid}")

            # Verify token signature and claims
            decoded = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                    "verify_aud": True,
                },
            )

            return decoded

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise

    async def _get_public_key(self, kid: Optional[str]) -> Optional[rsa.RSAPublicKey]:
        """Get public key from JWKS cache"""
        keys = await self.jwks_cache.get_keys()
        return self.jwks_cache.get_key(kid)


def create_oidc_middleware(
    app,
    issuer: str,
    audience: str,
    jwks_url: Optional[str] = None,
    skip_paths: Optional[list] = None,
) -> OIDCAuthenticationMiddleware:
    """Factory function to create OIDC middleware"""
    return OIDCAuthenticationMiddleware(
        app=app,
        issuer=issuer,
        audience=audience,
        jwks_url=jwks_url,
        skip_paths=skip_paths,
    )


# Dependency for FastAPI route authentication
async def verify_oidc_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = None,
) -> Dict:
    """FastAPI dependency to verify OIDC token"""
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return request.state.user
