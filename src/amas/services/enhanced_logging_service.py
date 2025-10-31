#!/usr/bin/env python3
"""
Enhanced Logging Service for AMAS
Implements comprehensive logging with security hardening, structured logging, and observability features
"""

import json
import logging
import logging.config
import os
import re
import sys
import uuid
from contextvars import ContextVar
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

# Context variables for request tracking
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
session_id_var: ContextVar[Optional[str]] = ContextVar("session_id", default=None)
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


class LogLevel(str, Enum):
    """Log levels with numeric values for comparison"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @property
    def numeric_level(self) -> int:
        """Get numeric level for comparison"""
        return getattr(logging, self.value, logging.INFO)


class LogFormat(str, Enum):
    """Log output formats"""

    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"


class SecurityLevel(str, Enum):
    """Security levels for log redaction"""

    LOW = "low"  # No redaction
    MEDIUM = "medium"  # Redact sensitive data
    HIGH = "high"  # Redact sensitive data and PII
    MAXIMUM = "maximum"  # Redact all potentially sensitive data


@dataclass
class LoggingConfig:
    """Configuration for enhanced logging"""

    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.JSON
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    enable_correlation: bool = True
    enable_metrics: bool = True
    enable_audit: bool = True
    enable_performance: bool = True
    log_file: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_structured: bool = True
    timezone: str = "UTC"
    include_stack_traces: bool = True
    redact_patterns: List[str] = None

    def __post_init__(self):
        if self.redact_patterns is None:
            self.redact_patterns = [
                r"(?i)(password|passwd|pwd)\s*[:=]\s*\S+",
                r"(?i)(token|key|secret)\s*[:=]\s*\S+",
                r"(?i)(api[_-]?key)\s*[:=]\s*\S+",
                r"(?i)(auth[_-]?token)\s*[:=]\s*\S+",
                r"(?i)(access[_-]?token)\s*[:=]\s*\S+",
                r"(?i)(refresh[_-]?token)\s*[:=]\s*\S+",
                r"(?i)(bearer[_-]?token)\s*[:=]\s*\S+",
                r"(?i)(jwt[_-]?token)\s*[:=]\s*\S+",
                r"(?i)(session[_-]?id)\s*[:=]\s*\S+",
                r"(?i)(cookie)\s*[:=]\s*\S+",
                r"(?i)(authorization)\s*[:=]\s*\S+",
                r"(?i)(x-api-key)\s*[:=]\s*\S+",
                r"(?i)(x-auth-token)\s*[:=]\s*\S+",
                r"(?i)(x-access-token)\s*[:=]\s*\S+",
                r"(?i)(x-session-id)\s*[:=]\s*\S+",
                r"(?i)(x-csrf-token)\s*[:=]\s*\S+",
                r"(?i)(x-request-id)\s*[:=]\s*\S+",
                r"(?i)(x-correlation-id)\s*[:=]\s*\S+",
                r"(?i)(x-trace-id)\s*[:=]\s*\S+",
                r"(?i)(x-span-id)\s*[:=]\s*\S+",
                r"(?i)(x-b3-traceid)\s*[:=]\s*\S+",
                r"(?i)(x-b3-spanid)\s*[:=]\s*\S+",
                r"(?i)(x-b3-sampled)\s*[:=]\s*\S+",
                r"(?i)(x-b3-flags)\s*[:=]\s*\S+",
                r"(?i)(x-ot-span-context)\s*[:=]\s*\S+",
                r"(?i)(x-requested-with)\s*[:=]\s*\S+",
                r"(?i)(x-forwarded-for)\s*[:=]\s*\S+",
                r"(?i)(x-real-ip)\s*[:=]\s*\S+",
                r"(?i)(x-forwarded-proto)\s*[:=]\s*\S+",
                r"(?i)(x-forwarded-host)\s*[:=]\s*\S+",
                r"(?i)(x-forwarded-port)\s*[:=]\s*\S+",
                r"(?i)(x-original-forwarded-for)\s*[:=]\s*\S+",
                r"(?i)(x-original-real-ip)\s*[:=]\s*\S+",
                r"(?i)(x-original-forwarded-proto)\s*[:=]\s*\S+",
                r"(?i)(x-original-forwarded-host)\s*[:=]\s*\S+",
                r"(?i)(x-original-forwarded-port)\s*[:=]\s*\S+",
                r"(?i)(x-cluster-client-ip)\s*[:=]\s*\S+",
                r"(?i)(x-client-ip)\s*[:=]\s*\S+",
                r"(?i)(x-remote-addr)\s*[:=]\s*\S+",
                r"(?i)(x-remote-ip)\s*[:=]\s*\S+",
                r"(?i)(x-remote-host)\s*[:=]\s*\S+",
                r"(?i)(x-remote-port)\s*[:=]\s*\S+",
                r"(?i)(x-remote-user)\s*[:=]\s*\S+",
                r"(?i)(x-remote-group)\s*[:=]\s*\S+",
                r"(?i)(x-remote-uid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-gid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-pid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-ppid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-sid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-tid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-cid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-rid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-eid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-fid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-gid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-hid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-iid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-jid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-kid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-lid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-mid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-nid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-oid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-pid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-qid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-rid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-sid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-tid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-uid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-vid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-wid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-xid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-yid)\s*[:=]\s*\S+",
                r"(?i)(x-remote-zid)\s*[:=]\s*\S+",
            ]


class LogEntry(BaseModel):
    """Enhanced structured log entry with security and observability features"""

    # Core fields
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    level: str
    message: str
    logger_name: str

    # Context fields
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None

    # Service fields
    service: str = "amas"
    component: Optional[str] = None
    action: Optional[str] = None
    operation: Optional[str] = None

    # Performance fields
    duration_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

    # HTTP fields
    method: Optional[str] = None
    url: Optional[str] = None
    status_code: Optional[int] = None
    response_size_bytes: Optional[int] = None
    request_size_bytes: Optional[int] = None

    # Error fields
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None

    # Security fields
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    security_event: Optional[str] = None
    threat_level: Optional[str] = None

    # Business fields
    business_event: Optional[str] = None
    business_value: Optional[float] = None
    business_impact: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

    # Observability fields
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = Field(default_factory=dict)

    @validator("level")
    def validate_level(cls, v):
        """Validate log level"""
        if v not in [level.value for level in LogLevel]:
            raise ValueError(f"Invalid log level: {v}")
        return v

    @validator("timestamp")
    def validate_timestamp(cls, v):
        """Ensure timestamp is timezone-aware"""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class SecurityRedactor:
    """Security redactor for sensitive data"""

    def __init__(self, config: LoggingConfig):
        self.config = config
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in config.redact_patterns
        ]

    def redact_string(self, text: str) -> str:
        """Redact sensitive data from string"""
        if self.config.security_level == SecurityLevel.LOW:
            return text

        redacted = text
        for pattern in self.compiled_patterns:
            redacted = pattern.sub(r"\1=***REDACTED***", redacted)

        return redacted

    def redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively redact sensitive data from dictionary"""
        if self.config.security_level == SecurityLevel.LOW:
            return data

        redacted = {}
        for key, value in data.items():
            if isinstance(value, str):
                redacted[key] = self.redact_string(value)
            elif isinstance(value, dict):
                redacted[key] = self.redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = [
                    self.redact_string(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                redacted[key] = value

        return redacted


class EnhancedLogger:
    """Enhanced logger with security, observability, and performance features"""

    def __init__(self, name: str, config: LoggingConfig = None):
        self.name = name
        self.config = config or LoggingConfig()
        self.redactor = SecurityRedactor(self.config)

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.config.level.numeric_level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Setup handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup logging handlers based on configuration"""
        # Console handler
        if self.config.enable_console:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(self.config.level.numeric_level)
            console_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(console_handler)

        # File handler
        if self.config.log_file:
            from logging.handlers import RotatingFileHandler

            file_handler = RotatingFileHandler(
                self.config.log_file,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count,
            )
            file_handler.setLevel(self.config.level.numeric_level)
            file_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(file_handler)

    def _get_formatter(self):
        """Get appropriate formatter based on configuration"""
        if self.config.format == LogFormat.JSON:
            return JSONFormatter(self.redactor)
        elif self.config.format == LogFormat.STRUCTURED:
            return StructuredFormatter(self.redactor)
        else:
            return TextFormatter(self.redactor)

    def _create_log_entry(self, level: str, message: str, **kwargs) -> LogEntry:
        """Create a structured log entry"""
        # Get context variables
        context_data = {
            "correlation_id": correlation_id_var.get(),
            "user_id": user_id_var.get(),
            "session_id": session_id_var.get(),
            "request_id": request_id_var.get(),
            "trace_id": trace_id_var.get(),
        }

        # Merge with provided kwargs
        context_data.update(kwargs)

        # Create log entry
        entry = LogEntry(
            level=level, message=message, logger_name=self.name, **context_data
        )

        return entry

    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method"""
        entry = self._create_log_entry(level, message, **kwargs)

        # Redact sensitive data
        if self.config.security_level != SecurityLevel.LOW:
            entry_dict = entry.dict()
            redacted_dict = self.redactor.redact_dict(entry_dict)
            entry = LogEntry(**redacted_dict)

        # Log using appropriate level
        if level == "DEBUG":
            self.logger.debug(entry.json())
        elif level == "INFO":
            self.logger.info(entry.json())
        elif level == "WARNING":
            self.logger.warning(entry.json())
        elif level == "ERROR":
            self.logger.error(entry.json())
        elif level == "CRITICAL":
            self.logger.critical(entry.json())

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

    def log_http_request(
        self,
        method: str,
        url: str,
        status_code: int,
        duration_ms: float,
        request_size: int = None,
        response_size: int = None,
        **kwargs,
    ):
        """Log HTTP request with performance metrics"""
        self.info(
            f"HTTP {method} {url}",
            action="http_request",
            method=method,
            url=url,
            status_code=status_code,
            duration_ms=duration_ms,
            request_size_bytes=request_size,
            response_size_bytes=response_size,
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
            ip_address=ip_address,
            security_event="authentication",
            threat_level="low" if success else "medium",
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
            security_event="authorization",
            threat_level="low" if granted else "high",
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
            ip_address=ip_address,
            security_event=event,
            threat_level=severity,
            **kwargs,
        )

    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        memory_usage_mb: float = None,
        cpu_usage_percent: float = None,
        **kwargs,
    ):
        """Log performance metrics"""
        self.info(
            f"Performance: {operation} took {duration_ms:.2f}ms",
            action="performance",
            operation=operation,
            duration_ms=duration_ms,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            **kwargs,
        )

    def log_business_event(
        self, event: str, value: float = None, impact: str = None, **kwargs
    ):
        """Log business event"""
        self.info(
            f"Business event: {event}",
            action="business_event",
            business_event=event,
            business_value=value,
            business_impact=impact,
            **kwargs,
        )

    def log_error(self, error: Exception, context: str = None, **kwargs):
        """Log error with context and stack trace"""
        import traceback

        self.error(
            f"Error in {context or 'unknown context'}: {str(error)}",
            error_code=type(error).__name__,
            error_message=str(error),
            error_type=type(error).__name__,
            stack_trace=(
                traceback.format_exc() if self.config.include_stack_traces else None
            ),
            **kwargs,
        )


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def __init__(self, redactor: SecurityRedactor):
        super().__init__()
        self.redactor = redactor

    def format(self, record):
        """Format log record as JSON"""
        try:
            # Parse JSON from record message
            log_data = json.loads(record.getMessage())

            # Redact sensitive data
            redacted_data = self.redactor.redact_dict(log_data)

            return json.dumps(redacted_data, default=str, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            # Fallback to text format if JSON parsing fails
            return f"{record.levelname}: {record.getMessage()}"


class StructuredFormatter(logging.Formatter):
    """Structured formatter for human-readable structured logging"""

    def __init__(self, redactor: SecurityRedactor):
        super().__init__()
        self.redactor = redactor

    def format(self, record):
        """Format log record as structured text"""
        try:
            # Parse JSON from record message
            log_data = json.loads(record.getMessage())

            # Redact sensitive data
            redacted_data = self.redactor.redact_dict(log_data)

            # Format as structured text
            timestamp = redacted_data.get("timestamp", "")
            level = redacted_data.get("level", "")
            message = redacted_data.get("message", "")
            correlation_id = redacted_data.get("correlation_id", "")
            user_id = redacted_data.get("user_id", "")

            structured = f"[{timestamp}] {level} {message}"
            if correlation_id:
                structured += f" [correlation_id={correlation_id}]"
            if user_id:
                structured += f" [user_id={user_id}]"

            return structured
        except (json.JSONDecodeError, TypeError):
            # Fallback to text format if JSON parsing fails
            return f"{record.levelname}: {record.getMessage()}"


class TextFormatter(logging.Formatter):
    """Simple text formatter"""

    def __init__(self, redactor: SecurityRedactor):
        super().__init__()
        self.redactor = redactor

    def format(self, record):
        """Format log record as text"""
        message = record.getMessage()
        redacted_message = self.redactor.redact_string(message)
        return f"{record.levelname}: {redacted_message}"


class LoggingContext:
    """Context manager for logging with correlation IDs"""

    def __init__(
        self,
        correlation_id: str = None,
        user_id: str = None,
        session_id: str = None,
        request_id: str = None,
        trace_id: str = None,
    ):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.user_id = user_id
        self.session_id = session_id
        self.request_id = request_id or str(uuid.uuid4())
        self.trace_id = trace_id or str(uuid.uuid4())

        self._old_correlation_id = None
        self._old_user_id = None
        self._old_session_id = None
        self._old_request_id = None
        self._old_trace_id = None

    def __enter__(self):
        # Store old values
        self._old_correlation_id = correlation_id_var.get()
        self._old_user_id = user_id_var.get()
        self._old_session_id = session_id_var.get()
        self._old_request_id = request_id_var.get()
        self._old_trace_id = trace_id_var.get()

        # Set new values
        correlation_id_var.set(self.correlation_id)
        if self.user_id:
            user_id_var.set(self.user_id)
        if self.session_id:
            session_id_var.set(self.session_id)
        request_id_var.set(self.request_id)
        trace_id_var.set(self.trace_id)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old values
        correlation_id_var.set(self._old_correlation_id)
        user_id_var.set(self._old_user_id)
        session_id_var.set(self._old_session_id)
        request_id_var.set(self._old_request_id)
        trace_id_var.set(self._old_trace_id)


# Global configuration
_global_config: Optional[LoggingConfig] = None
_global_loggers: Dict[str, EnhancedLogger] = {}


def configure_logging(config: LoggingConfig = None):
    """Configure global logging"""
    global _global_config
    _global_config = config or LoggingConfig()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(_global_config.level.numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Setup handlers
    if _global_config.enable_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(_global_config.level.numeric_level)
        console_handler.setFormatter(JSONFormatter(SecurityRedactor(_global_config)))
        root_logger.addHandler(console_handler)

    if _global_config.log_file:
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            _global_config.log_file,
            maxBytes=_global_config.max_file_size,
            backupCount=_global_config.backup_count,
        )
        file_handler.setLevel(_global_config.level.numeric_level)
        file_handler.setFormatter(JSONFormatter(SecurityRedactor(_global_config)))
        root_logger.addHandler(file_handler)


def get_logger(name: str, component: str = None) -> EnhancedLogger:
    """Get an enhanced logger instance"""
    global _global_loggers, _global_config

    if name not in _global_loggers:
        config = _global_config or LoggingConfig()
        _global_loggers[name] = EnhancedLogger(name, config)

    return _global_loggers[name]


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


def get_trace_id() -> Optional[str]:
    """Get current trace ID"""
    return trace_id_var.get()


def set_trace_id(trace_id: str):
    """Set trace ID for current context"""
    trace_id_var.set(trace_id)


def log_with_context(
    correlation_id: str = None,
    user_id: str = None,
    session_id: str = None,
    request_id: str = None,
    trace_id: str = None,
):
    """Decorator for logging with context"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            with LoggingContext(
                correlation_id, user_id, session_id, request_id, trace_id
            ):
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
api_logger = get_logger("amas.api", "api")
database_logger = get_logger("amas.database", "database")
cache_logger = get_logger("amas.cache", "cache")
external_logger = get_logger("amas.external", "external")


if __name__ == "__main__":
    # Test the enhanced logging
    config = LoggingConfig(
        level=LogLevel.DEBUG,
        format=LogFormat.JSON,
        security_level=SecurityLevel.MEDIUM,
        enable_console=True,
    )

    configure_logging(config)

    logger = get_logger("test")

    with LoggingContext(correlation_id="test-123", user_id="test-user"):
        logger.info("Test message", action="test", component="test")
        logger.log_http_request("GET", "/test", 200, 150.5)
        logger.log_authentication("test-user", True, "127.0.0.1")
        logger.log_security_event("test_security_event", "medium")
        logger.log_performance("test_operation", 100.0, 50.0, 25.0)
        logger.log_business_event("test_business_event", 1000.0, "high")
