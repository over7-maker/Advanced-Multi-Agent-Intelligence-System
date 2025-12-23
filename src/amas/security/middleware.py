"""
Security Middleware for FastAPI
Integrates authentication, authorization, and audit logging
"""

import logging
import time
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from .auth.jwt_middleware import auth_context, token_blacklist
from .audit.audit_logger import get_audit_logger, AuditEventType, AuditStatus
from .policies.opa_integration import get_policy_engine

logger = logging.getLogger(__name__)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log API requests to audit log"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request to audit trail"""
        start_time = time.time()
        trace_id = request.headers.get("X-Trace-ID") or request.headers.get("X-Request-ID")
        user_id = None
        status_code = 500
        error_message = None
        
        try:
            # Get user context if authenticated
            user_context = auth_context.get_user()
            if user_context:
                user_id = user_context.get("user_id")
            
            # Process request
            response = await call_next(request)
            status_code = response.status_code
            
            # Log successful request
            duration_ms = (time.time() - start_time) * 1000
            audit_logger = get_audit_logger()
            
            from .audit.audit_logger import AuditEvent
            from datetime import datetime, timezone
            
            event = AuditEvent(
                event_id=audit_logger._generate_event_id(),
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=AuditEventType.SYSTEM_EVENT,
                status=AuditStatus.SUCCESS if status_code < 400 else AuditStatus.FAILURE,
                user_id=user_id,
                action=f"{request.method} {request.url.path}",
                duration_ms=duration_ms,
                trace_id=trace_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                details={
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": status_code,
                }
            )
            
            await audit_logger.log_event(event)
            
            return response
            
        except HTTPException as e:
            status_code = e.status_code
            error_message = e.detail
            
            # Log failed request
            duration_ms = (time.time() - start_time) * 1000
            audit_logger = get_audit_logger()
            
            await audit_logger.log_security_violation(
                user_id=user_id,
                violation_type="http_error",
                severity="medium" if status_code < 500 else "high",
                description=f"{request.method} {request.url.path} - {error_message}",
                ip_address=request.client.host if request.client else None,
                trace_id=trace_id,
                details={
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": status_code,
                    "error": error_message,
                }
            )
            
            raise
            
        except Exception as e:
            status_code = 500
            error_message = str(e)
            
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            audit_logger = get_audit_logger()
            
            await audit_logger.log_security_violation(
                user_id=user_id,
                violation_type="system_error",
                severity="critical",
                description=f"{request.method} {request.url.path} - {error_message}",
                ip_address=request.client.host if request.client else None,
                trace_id=trace_id,
                details={
                    "method": request.method,
                    "path": str(request.url.path),
                    "error": error_message,
                    "error_type": type(e).__name__,
                }
            )
            
            raise


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce authentication on protected routes"""
    
    def __init__(self, app, exclude_paths: Optional[list] = None):
        super().__init__(app)
        import os
        # For development, allow unauthenticated access to API endpoints
        dev_mode = os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "test"]
        
        self.exclude_paths = exclude_paths or [
            "/",
            "/health",
            "/ready",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
        ]
        
        # In development mode, exclude all API paths from authentication requirement
        if dev_mode:
            # Exclude all /api/v1 paths for development
            self.exclude_paths.append("/api/v1")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check authentication for protected routes"""
        import os
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Check if route is in /api/v1 (protected area)
        if request.url.path.startswith("/api/v1"):
            # In test/dev mode, skip authentication
            dev_mode = os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "test"]
            if dev_mode:
                return await call_next(request)
            
            # Check if user is authenticated
            user_context = auth_context.get_user()
            if not user_context:
                # Try to authenticate via JWT in Authorization header
                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                
                # Authentication will be handled by AMASHTTPBearer dependency
                # This middleware just ensures the header is present for protected routes
        
        return await call_next(request)
