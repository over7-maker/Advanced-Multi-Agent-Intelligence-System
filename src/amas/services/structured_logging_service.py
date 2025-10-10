"""
Structured Logging Service for AMAS
Implements correlation IDs and structured logging for better observability
"""

import json
import logging
import uuid
from contextvars import ContextVar
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

# Context variables for request tracking
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
session_id_var: ContextVar[Optional[str]] = ContextVar("session_id", default=None)
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class LogLevel(str):
    """Log levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(BaseModel):
    """Structured log entry"""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    level: str
    message: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    service: str = "amas"
    component: Optional[str] = None
    action: Optional[str] = None
    duration_ms: Optional[float] = None
    status_code: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class StructuredLogger:
    """Structured logger with correlation ID support"""

    def __init__(self, name: str, component: str = None):
        self.name = name
        self.component = component
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

    def _create_log_entry(self, level: str, message: str, **kwargs) -> LogEntry:
        """Create a structured log entry"""
        return LogEntry(
            level=level,
            message=message,
            correlation_id=correlation_id_var.get(),
            user_id=user_id_var.get(),
            session_id=session_id_var.get(),
            request_id=request_id_var.get(),
            component=self.component,
            **kwargs,
        )

    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method"""
        entry = self._create_log_entry(level, message, **kwargs)

        # Convert to JSON for structured logging
        log_data = entry.dict()
        log_json = json.dumps(log_data, default=str)

        # Log using appropriate level
        if level == "DEBUG":
            self.logger.debug(log_json)
        elif level == "INFO":
            self.logger.info(log_json)
        elif level == "WARNING":
            self.logger.warning(log_json)
        elif level == "ERROR":
            self.logger.error(log_json)
        elif level == "CRITICAL":
            self.logger.critical(log_json)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log("CRITICAL", message, **kwargs)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: str = None,
        **kwargs,
    ):
        """Log HTTP request"""
        self.info(
            f"HTTP {method} {path}",
            action="http_request",
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            metadata={
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
            **kwargs,
        )

    def log_authentication(
        self, username: str, success: bool, ip_address: str = None, **kwargs
    ):
        """Log authentication event"""
        level = "INFO" if success else "WARNING"
        self._log(
            level,
            f"Authentication {'successful' if success else 'failed'} for user {username}",
            action="authentication",
            user_id=username,
            metadata={
                "username": username,
                "success": success,
                "ip_address": ip_address,
            },
            tags=["authentication", "security"],
            **kwargs,
        )

    def log_authorization(
        self, user_id: str, resource: str, action: str, granted: bool, **kwargs
    ):
        """Log authorization event"""
        level = "INFO" if granted else "WARNING"
        self._log(
            level,
            f"Authorization {'granted' if granted else 'denied'} for {action} on {resource}",
            action="authorization",
            user_id=user_id,
            metadata={"resource": resource, "action": action, "granted": granted},
            tags=["authorization", "security"],
            **kwargs,
        )

    def log_agent_event(self, agent_id: str, event: str, user_id: str = None, **kwargs):
        """Log agent event"""
        self.info(
            f"Agent {agent_id} {event}",
            action="agent_event",
            user_id=user_id,
            metadata={"agent_id": agent_id, "event": event},
            tags=["agent", "automation"],
            **kwargs,
        )

    def log_task_event(self, task_id: str, event: str, user_id: str = None, **kwargs):
        """Log task event"""
        self.info(
            f"Task {task_id} {event}",
            action="task_event",
            user_id=user_id,
            metadata={"task_id": task_id, "event": event},
            tags=["task", "workflow"],
            **kwargs,
        )

    def log_error(self, error: Exception, context: str = None, **kwargs):
        """Log error with context"""
        import traceback

        self.error(
            f"Error in {context or 'unknown context'}: {str(error)}",
            error_code=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            metadata={"error_type": type(error).__name__, "context": context},
            tags=["error", "exception"],
            **kwargs,
        )

    def log_performance(self, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics"""
        self.info(
            f"Performance: {operation} took {duration_ms:.2f}ms",
            action="performance",
            duration_ms=duration_ms,
            metadata={"operation": operation, "duration_ms": duration_ms},
            tags=["performance", "metrics"],
            **kwargs,
        )

    def log_security_event(
        self,
        event: str,
        severity: str = "medium",
        user_id: str = None,
        ip_address: str = None,
        **kwargs,
    ):
        """Log security event"""
        level = "CRITICAL" if severity == "critical" else "WARNING"
        self._log(
            level,
            f"Security event: {event}",
            action="security_event",
            user_id=user_id,
            metadata={"event": event, "severity": severity, "ip_address": ip_address},
            tags=["security", "event"],
            **kwargs,
        )


class LoggingContext:
    """Context manager for logging with correlation IDs"""

    def __init__(
        self,
        correlation_id: str = None,
        user_id: str = None,
        session_id: str = None,
        request_id: str = None,
    ):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.user_id = user_id
        self.session_id = session_id
        self.request_id = request_id or str(uuid.uuid4())

        self._old_correlation_id = None
        self._old_user_id = None
        self._old_session_id = None
        self._old_request_id = None

    def __enter__(self):
        # Store old values
        self._old_correlation_id = correlation_id_var.get()
        self._old_user_id = user_id_var.get()
        self._old_session_id = session_id_var.get()
        self._old_request_id = request_id_var.get()

        # Set new values
        correlation_id_var.set(self.correlation_id)
        if self.user_id:
            user_id_var.set(self.user_id)
        if self.session_id:
            session_id_var.set(self.session_id)
        request_id_var.set(self.request_id)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old values
        correlation_id_var.set(self._old_correlation_id)
        user_id_var.set(self._old_user_id)
        session_id_var.set(self._old_session_id)
        request_id_var.set(self._old_request_id)


def get_logger(name: str, component: str = None) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name, component)


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str):
    """Set correlation ID for current context"""
    correlation_id_var.set(correlation_id)


def get_user_id() -> Optional[str]:
    """Get current user ID"""
    return user_id_var.get()


def set_user_id(user_id: str):
    """Set user ID for current context"""
    user_id_var.set(user_id)


def get_session_id() -> Optional[str]:
    """Get current session ID"""
    return session_id_var.get()


def set_session_id(session_id: str):
    """Set session ID for current context"""
    session_id_var.set(session_id)


def get_request_id() -> Optional[str]:
    """Get current request ID"""
    return request_id_var.get()


def set_request_id(request_id: str):
    """Set request ID for current context"""
    request_id_var.set(request_id)


def log_with_context(
    correlation_id: str = None,
    user_id: str = None,
    session_id: str = None,
    request_id: str = None,
):
    """Decorator for logging with context"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            with LoggingContext(correlation_id, user_id, session_id, request_id):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Global logger instances
main_logger = get_logger("amas.main", "main")
auth_logger = get_logger("amas.auth", "authentication")
agent_logger = get_logger("amas.agent", "agent")
task_logger = get_logger("amas.task", "task")
security_logger = get_logger("amas.security", "security")
performance_logger = get_logger("amas.performance", "performance")
