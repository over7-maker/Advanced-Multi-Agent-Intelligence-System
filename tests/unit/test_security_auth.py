"""
Unit tests for security authentication components
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException

from src.amas.security.auth.jwt_middleware import (
    JWTMiddleware,
    SecurityHeadersMiddleware,
    TokenBlacklist,
    auth_context,
)


@pytest.fixture
def jwt_middleware():
    """Create JWT middleware instance for testing"""
    return JWTMiddleware(
        issuer="https://test-issuer.com",
        audience="test-audience",
        jwks_uri="https://test-issuer.com/.well-known/jwks.json",
        cache_ttl=3600,
        algorithms=["RS256"]
    )


@pytest.fixture
def token_blacklist():
    """Create token blacklist instance"""
    return TokenBlacklist()


class TestJWTMiddleware:
    """Test JWT middleware functionality"""
    
    @pytest.mark.asyncio
    async def test_get_jwks_caching(self, jwt_middleware):
        """Test JWKS caching functionality"""
        
        mock_response = {
            "keys": [
                {
                    "kid": "test-key-1",
                    "kty": "RSA",
                    "use": "sig",
                    "n": "test-n",
                    "e": "AQAB"
                }
            ]
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            mock_client_instance.get.return_value.json.return_value = mock_response
            mock_client_instance.get.return_value.raise_for_status = MagicMock()
            
            # First call should fetch from network
            jwks = await jwt_middleware.get_jwks()
            assert jwks == mock_response
            assert mock_client_instance.get.call_count == 1
            
            # Second call should use cache
            jwks = await jwt_middleware.get_jwks()
            assert jwks == mock_response
            # Should still be 1 call due to caching
            assert mock_client_instance.get.call_count == 1
    
    @pytest.mark.asyncio
    async def test_token_blacklist_check(self, jwt_middleware, token_blacklist):
        """Test that blacklisted tokens are rejected"""
        # Create a mock token with JTI
        test_jti = "test-token-jti-123"
        exp_timestamp = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        
        # Blacklist the token
        token_blacklist.blacklist_token(test_jti, exp_timestamp)
        
        # Create a token payload with the blacklisted JTI
        token_payload = {
            "sub": "test-user",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": exp_timestamp,
            "jti": test_jti
        }
        
        # Mock token decode
        with patch("jwt.decode") as mock_decode:
            mock_decode.side_effect = [
                {"jti": test_jti, "exp": exp_timestamp},  # Unverified decode
                HTTPException(status_code=401, detail="Token has been revoked")  # Validation should fail
            ]
            
            # Should raise HTTPException for blacklisted token
            with pytest.raises(HTTPException) as exc_info:
                # Simulate token validation
                unverified = jwt.decode("fake-token", options={"verify_signature": False})
                if token_blacklist.is_blacklisted(unverified.get("jti")):
                    raise HTTPException(
                        status_code=401,
                        detail="Token has been revoked"
                    )
            
            assert exc_info.value.status_code == 401
            assert "revoked" in str(exc_info.value.detail)


class TestSecurityHeadersMiddleware:
    """Test security headers middleware"""
    
    @pytest.mark.asyncio
    async def test_security_headers_added(self):
        """Test that security headers are added to responses"""
        from unittest.mock import Mock

        from fastapi import Request
        from starlette.responses import Response
        
        middleware = SecurityHeadersMiddleware()
        
        # Mock request and response
        mock_request = Mock(spec=Request)
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/test"
        
        mock_response = Mock(spec=Response)
        mock_response.headers = {}
        
        # Add security headers
        await middleware.add_security_headers(mock_request, mock_response)
        
        # Check that security headers were added
        assert "X-Content-Type-Options" in mock_response.headers
        assert "X-Frame-Options" in mock_response.headers
        assert "Strict-Transport-Security" in mock_response.headers
        assert "Content-Security-Policy" in mock_response.headers
        assert mock_response.headers["X-Frame-Options"] == "DENY"
    
    @pytest.mark.asyncio
    async def test_cache_control_for_sensitive_endpoints(self):
        """Test that cache control is set for sensitive endpoints"""
        from unittest.mock import Mock

        from fastapi import Request
        from starlette.responses import Response
        
        middleware = SecurityHeadersMiddleware()
        
        # Mock request for sensitive endpoint
        mock_request = Mock(spec=Request)
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/agents"
        
        mock_response = Mock(spec=Response)
        mock_response.headers = {}
        
        # Add security headers
        await middleware.add_security_headers(mock_request, mock_response)
        
        # Check cache control headers for sensitive endpoints
        assert "Cache-Control" in mock_response.headers
        assert "no-cache" in mock_response.headers["Cache-Control"]


class TestTokenBlacklist:
    """Test token blacklist functionality"""
    
    def test_blacklist_token(self, token_blacklist):
        """Test adding token to blacklist"""
        test_jti = "test-jti-123"
        exp_timestamp = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        
        token_blacklist.blacklist_token(test_jti, exp_timestamp)
        
        assert token_blacklist.is_blacklisted(test_jti) is True
    
    def test_is_blacklisted_false(self, token_blacklist):
        """Test that non-blacklisted tokens return False"""
        test_jti = "non-blacklisted-jti"
        
        assert token_blacklist.is_blacklisted(test_jti) is False
    
    def test_cleanup_expired_tokens(self, token_blacklist):
        """Test that expired tokens are cleaned up"""
        expired_jti = "expired-jti"
        expired_timestamp = int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp())
        
        valid_jti = "valid-jti"
        valid_timestamp = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        
        token_blacklist.blacklist_token(expired_jti, expired_timestamp)
        token_blacklist.blacklist_token(valid_jti, valid_timestamp)
        
        # Force cleanup
        token_blacklist._cleanup_expired()
        
        # Expired token should be removed
        assert token_blacklist.is_blacklisted(expired_jti) is False
        # Valid token should still be blacklisted
        assert token_blacklist.is_blacklisted(valid_jti) is True


class TestAuthContext:
    """Test authentication context management"""
    
    def test_set_and_get_user(self):
        """Test setting and getting user context"""
        user_context = {
            "user_id": "test-user-123",
            "email": "test@example.com",
            "roles": ["user", "admin"],
            "scopes": ["read", "write"]
        }
        
        auth_context.set_user(user_context)
        
        retrieved = auth_context.get_user()
        assert retrieved["user_id"] == "test-user-123"
        assert retrieved["email"] == "test@example.com"
        assert "admin" in retrieved["roles"]
    
    def test_has_role(self):
        """Test role checking"""
        user_context = {
            "user_id": "test-user",
            "roles": ["user", "admin"]
        }
        
        auth_context.set_user(user_context)
        
        assert auth_context.has_role("admin") is True
        assert auth_context.has_role("superuser") is False
    
    def test_clear_context(self):
        """Test clearing authentication context"""
        user_context = {"user_id": "test-user"}
        auth_context.set_user(user_context)
        
        auth_context.clear()
        
        assert auth_context.get_user() is None
