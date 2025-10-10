"""
Standardized Error Handling for AMAS
Implements RFC7807 Problem Details for HTTP APIs
"""

import logging
import traceback
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Standard error types"""

    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND_ERROR = "not_found_error"
    CONFLICT_ERROR = "conflict_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    INTERNAL_ERROR = "internal_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    TIMEOUT_ERROR = "timeout_error"
    CONFIGURATION_ERROR = "configuration_error"
    SECURITY_ERROR = "security_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"


class ErrorSeverity(str, Enum):
    """Error severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProblemDetail(BaseModel):
    """RFC7807 Problem Details for HTTP APIs"""

    type: str = Field(description="A URI reference that identifies the problem type")
    title: str = Field(
        description="A short, human-readable summary of the problem type"
    )
    status: int = Field(description="The HTTP status code")
    detail: str = Field(
        description="A human-readable explanation specific to this occurrence"
    )
    instance: Optional[str] = Field(
        None, description="A URI reference that identifies the specific occurrence"
    )
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    errors: Optional[List[Dict[str, Any]]] = Field(
        None, description="Additional error details"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Additional context information"
    )
    severity: ErrorSeverity = Field(default=ErrorSeverity.MEDIUM)
    retry_after: Optional[int] = Field(None, description="Seconds after which to retry")


class AMASException(Exception):
    """Base exception for AMAS with RFC7807 support"""

    def __init__(
        self,
        error_type: ErrorType,
        title: str,
        detail: str,
        status_code: int = 500,
        instance: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        retry_after: Optional[int] = None,
    ):
        self.error_type = error_type
        self.title = title
        self.detail = detail
        self.status_code = status_code
        self.instance = instance
        self.errors = errors or []
        self.context = context or {}
        self.severity = severity
        self.retry_after = retry_after
        super().__init__(detail)


class ValidationError(AMASException):
    """Validation error exception"""

    def __init__(
        self,
        detail: str,
        errors: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_type=ErrorType.VALIDATION_ERROR,
            title="Validation Error",
            detail=detail,
            status_code=400,
            errors=errors,
            context=context,
            severity=ErrorSeverity.MEDIUM,
        )


class AuthenticationError(AMASException):
    """Authentication error exception"""

    def __init__(
        self,
        detail: str = "Authentication required",
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_type=ErrorType.AUTHENTICATION_ERROR,
            title="Authentication Error",
            detail=detail,
            status_code=401,
            context=context,
            severity=ErrorSeverity.HIGH,
        )


class AuthorizationError(AMASException):
    """Authorization error exception"""

    def __init__(
        self,
        detail: str = "Insufficient permissions",
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_type=ErrorType.AUTHORIZATION_ERROR,
            title="Authorization Error",
            detail=detail,
            status_code=403,
            context=context,
            severity=ErrorSeverity.HIGH,
        )


class NotFoundError(AMASException):
    """Not found error exception"""

    def __init__(
        self, resource: str, identifier: str, context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            error_type=ErrorType.NOT_FOUND_ERROR,
            title="Resource Not Found",
            detail=f"{resource} with identifier '{identifier}' not found",
            status_code=404,
            context=context,
            severity=ErrorSeverity.MEDIUM,
        )


class ConflictError(AMASException):
    """Conflict error exception"""

    def __init__(self, detail: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_type=ErrorType.CONFLICT_ERROR,
            title="Conflict Error",
            detail=detail,
            status_code=409,
            context=context,
            severity=ErrorSeverity.MEDIUM,
        )


class RateLimitError(AMASException):
    """Rate limit error exception"""

    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_type=ErrorType.RATE_LIMIT_ERROR,
            title="Rate Limit Exceeded",
            detail=detail,
            status_code=429,
            context=context,
            severity=ErrorSeverity.MEDIUM,
            retry_after=retry_after,
        )


class InternalError(AMASException):
    """Internal error exception"""

    def __init__(
        self,
        detail: str = "Internal server error",
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_type=ErrorType.INTERNAL_ERROR,
            title="Internal Server Error",
            detail=detail,
            status_code=500,
            context=context,
            severity=ErrorSeverity.CRITICAL,
        )


class ExternalServiceError(AMASException):
    """External service error exception"""

    def __init__(
        self, service: str, detail: str, context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            error_type=ErrorType.EXTERNAL_SERVICE_ERROR,
            title="External Service Error",
            detail=f"Error calling {service}: {detail}",
            status_code=502,
            context=context,
            severity=ErrorSeverity.HIGH,
        )


class TimeoutError(AMASException):
    """Timeout error exception"""

    def __init__(
        self, service: str, timeout: float, context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            error_type=ErrorType.TIMEOUT_ERROR,
            title="Timeout Error",
            detail=f"Request to {service} timed out after {timeout} seconds",
            status_code=504,
            context=context,
            severity=ErrorSeverity.HIGH,
        )


class SecurityError(AMASException):
    """Security error exception"""

    def __init__(self, detail: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_type=ErrorType.SECURITY_ERROR,
            title="Security Error",
            detail=detail,
            status_code=403,
            context=context,
            severity=ErrorSeverity.CRITICAL,
        )


class BusinessLogicError(AMASException):
    """Business logic error exception"""

    def __init__(self, detail: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_type=ErrorType.BUSINESS_LOGIC_ERROR,
            title="Business Logic Error",
            detail=detail,
            status_code=422,
            context=context,
            severity=ErrorSeverity.MEDIUM,
        )


class ErrorHandler:
    """Centralized error handling service"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_problem_detail(
        self, error: Union[AMASException, Exception], request: Optional[Request] = None
    ) -> ProblemDetail:
        """Create RFC7807 Problem Detail from exception"""

        if isinstance(error, AMASException):
            return ProblemDetail(
                type=f"https://api.amas.local/problems/{error.error_type.value}",
                title=error.title,
                status=error.status_code,
                detail=error.detail,
                instance=error.instance or (request.url.path if request else None),
                correlation_id=error.context.get("correlation_id", str(uuid.uuid4())),
                errors=error.errors,
                context=error.context,
                severity=error.severity,
                retry_after=error.retry_after,
            )

        # Handle standard Python exceptions
        if isinstance(error, HTTPException):
            return ProblemDetail(
                type="https://api.amas.local/problems/http_error",
                title="HTTP Error",
                status=error.status_code,
                detail=error.detail,
                instance=request.url.path if request else None,
                severity=ErrorSeverity.MEDIUM,
            )

        # Handle generic exceptions
        return ProblemDetail(
            type="https://api.amas.local/problems/internal_error",
            title="Internal Server Error",
            status=500,
            detail="An unexpected error occurred",
            instance=request.url.path if request else None,
            severity=ErrorSeverity.CRITICAL,
            context={
                "exception_type": type(error).__name__,
                "traceback": traceback.format_exc(),
            },
        )

    def log_error(
        self,
        error: Exception,
        request: Optional[Request] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Log error with context"""
        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "correlation_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if request:
            error_context.update(
                {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "client_ip": request.client.host if request.client else None,
                }
            )

        if context:
            error_context.update(context)

        # Log based on severity
        if isinstance(error, AMASException):
            if error.severity == ErrorSeverity.CRITICAL:
                self.logger.critical(
                    f"Critical error: {error.detail}", extra=error_context
                )
            elif error.severity == ErrorSeverity.HIGH:
                self.logger.error(
                    f"High severity error: {error.detail}", extra=error_context
                )
            else:
                self.logger.warning(f"Error: {error.detail}", extra=error_context)
        else:
            self.logger.error(f"Unexpected error: {str(error)}", extra=error_context)

    def handle_exception(
        self,
        error: Exception,
        request: Optional[Request] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        """Handle exception and return JSON response"""

        # Log the error
        self.log_error(error, request, context)

        # Create problem detail
        problem_detail = self.create_problem_detail(error, request)

        # Add retry-after header if applicable
        headers = {}
        if problem_detail.retry_after:
            headers["Retry-After"] = str(problem_detail.retry_after)

        # Add correlation ID header
        headers["X-Correlation-ID"] = problem_detail.correlation_id

        return JSONResponse(
            status_code=problem_detail.status,
            content=problem_detail.dict(),
            headers=headers,
        )


# Global error handler instance
error_handler = ErrorHandler()


def handle_amas_exception(request: Request, exc: AMASException) -> JSONResponse:
    """FastAPI exception handler for AMAS exceptions"""
    return error_handler.handle_exception(exc, request)


def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """FastAPI exception handler for HTTP exceptions"""
    return error_handler.handle_exception(exc, request)


def handle_general_exception(request: Request, exc: Exception) -> JSONResponse:
    """FastAPI exception handler for general exceptions"""
    return error_handler.handle_exception(exc, request)


def create_error_response(
    error_type: ErrorType,
    title: str,
    detail: str,
    status_code: int = 500,
    instance: Optional[str] = None,
    errors: Optional[List[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    retry_after: Optional[int] = None,
) -> AMASException:
    """Create a standardized error response"""
    return AMASException(
        error_type=error_type,
        title=title,
        detail=detail,
        status_code=status_code,
        instance=instance,
        errors=errors,
        context=context,
        severity=severity,
        retry_after=retry_after,
    )


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that required fields are present in data"""
    missing_fields = [
        field for field in required_fields if field not in data or data[field] is None
    ]
    if missing_fields:
        raise ValidationError(
            detail=f"Missing required fields: {', '.join(missing_fields)}",
            errors=[
                {"field": field, "message": "This field is required"}
                for field in missing_fields
            ],
        )


def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> None:
    """Validate field types in data"""
    errors = []
    for field, expected_type in field_types.items():
        if field in data and not isinstance(data[field], expected_type):
            errors.append(
                {
                    "field": field,
                    "message": f"Expected {expected_type.__name__}, got {type(data[field]).__name__}",
                }
            )

    if errors:
        raise ValidationError(detail="Field type validation failed", errors=errors)


def validate_string_length(
    value: str, min_length: int = 0, max_length: int = None, field_name: str = "field"
) -> None:
    """Validate string length"""
    if len(value) < min_length:
        raise ValidationError(
            detail=f"{field_name} must be at least {min_length} characters long",
            errors=[
                {"field": field_name, "message": f"Minimum length is {min_length}"}
            ],
        )

    if max_length and len(value) > max_length:
        raise ValidationError(
            detail=f"{field_name} must be no more than {max_length} characters long",
            errors=[
                {"field": field_name, "message": f"Maximum length is {max_length}"}
            ],
        )


def validate_email(email: str) -> None:
    """Validate email format"""
    import re

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValidationError(
            detail="Invalid email format",
            errors=[{"field": "email", "message": "Must be a valid email address"}],
        )


def validate_username(username: str) -> None:
    """Validate username format"""
    import re

    username_pattern = r"^[a-zA-Z0-9_-]{3,30}$"
    if not re.match(username_pattern, username):
        raise ValidationError(
            detail="Invalid username format",
            errors=[
                {
                    "field": "username",
                    "message": "Must be 3-30 characters, alphanumeric, underscore, or hyphen only",
                }
            ],
        )
