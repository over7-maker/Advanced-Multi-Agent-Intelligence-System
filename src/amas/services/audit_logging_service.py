"""
Audit Logging Service for AMAS
Implements comprehensive audit logging for security and compliance
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events"""

    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"

    # Authorization events
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"

    # User management events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_DEACTIVATED = "user_deactivated"
    USER_ACTIVATED = "user_activated"

    # Agent management events
    AGENT_CREATED = "agent_created"
    AGENT_UPDATED = "agent_updated"
    AGENT_DELETED = "agent_deleted"
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    AGENT_EXECUTED = "agent_executed"

    # Task management events
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_SUBMITTED = "task_submitted"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"

    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGED = "configuration_changed"
    SECURITY_SCAN = "security_scan"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"

    # Data events
    DATA_ACCESSED = "data_accessed"
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"

    # Security events
    SECURITY_VIOLATION = "security_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_INPUT = "invalid_input"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

    # API events
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    API_ERROR = "api_error"

    # External service events
    EXTERNAL_SERVICE_CALL = "external_service_call"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    EXTERNAL_SERVICE_TIMEOUT = "external_service_timeout"


class AuditSeverity(str, Enum):
    """Audit event severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data structure"""

    id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: Optional[str]
    action: str
    details: Dict[str, Any]
    outcome: str  # success, failure, error
    error_message: Optional[str] = None
    correlation_id: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())


class AuditLogEntry(BaseModel):
    """Pydantic model for audit log entries"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    outcome: str = "success"
    error_message: Optional[str] = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tags: List[str] = Field(default_factory=list)


class AuditLoggingService:
    """Service for managing audit logging"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("audit")
        self.audit_handler = None
        self._setup_audit_logging()

    def _setup_audit_logging(self):
        """Setup audit logging configuration"""
        # Create audit logger
        self.audit_logger = logging.getLogger("audit")
        self.audit_logger.setLevel(logging.INFO)

        # Create file handler for audit logs
        audit_log_file = self.config.get("audit_log_file", "/app/logs/audit.log")
        handler = logging.FileHandler(audit_log_file)
        handler.setLevel(logging.INFO)

        # Create JSON formatter for structured logging
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}'
        )
        handler.setFormatter(formatter)

        self.audit_logger.addHandler(handler)
        self.audit_logger.propagate = False

    def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        outcome: str = "success",
        error_message: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        correlation_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Log an audit event"""
        try:
            # Create audit log entry
            entry = AuditLogEntry(
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                resource=resource,
                action=action,
                details=details or {},
                outcome=outcome,
                error_message=error_message,
                correlation_id=correlation_id or str(uuid.uuid4()),
                tags=tags or [],
            )

            # Log the event
            self.audit_logger.info(json.dumps(entry.dict(), default=str))

            # Also log to main logger for immediate visibility
            logger.info(
                f"Audit: {event_type.value} - {action} by {user_id or 'system'} - {outcome}"
            )

            return entry.id

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return str(uuid.uuid4())

    def log_authentication_event(
        self,
        event_type: AuditEventType,
        username: str,
        ip_address: str,
        user_agent: str = None,
        success: bool = True,
        error_message: str = None,
        session_id: str = None,
    ) -> str:
        """Log authentication-related events"""
        severity = AuditSeverity.HIGH if not success else AuditSeverity.MEDIUM

        return self.log_event(
            event_type=event_type,
            action=f"Authentication attempt for user {username}",
            user_id=username,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource="authentication",
            details={
                "username": username,
                "success": success,
                "ip_address": ip_address,
            },
            outcome="success" if success else "failure",
            error_message=error_message,
            severity=severity,
            tags=["authentication", "security"],
        )

    def log_authorization_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        resource: str,
        action: str,
        permission: str,
        granted: bool,
        ip_address: str = None,
        session_id: str = None,
    ) -> str:
        """Log authorization-related events"""
        severity = AuditSeverity.HIGH if not granted else AuditSeverity.MEDIUM

        return self.log_event(
            event_type=event_type,
            action=f"Authorization check for {action} on {resource}",
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            resource=resource,
            details={"permission": permission, "granted": granted, "action": action},
            outcome="success" if granted else "failure",
            severity=severity,
            tags=["authorization", "security"],
        )

    def log_user_management_event(
        self,
        event_type: AuditEventType,
        target_user_id: str,
        admin_user_id: str,
        action: str,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        session_id: str = None,
    ) -> str:
        """Log user management events"""
        return self.log_event(
            event_type=event_type,
            action=f"User management: {action}",
            user_id=admin_user_id,
            session_id=session_id,
            ip_address=ip_address,
            resource="user_management",
            details={
                "target_user_id": target_user_id,
                "admin_user_id": admin_user_id,
                "action": action,
                **(details or {}),
            },
            outcome="success",
            severity=AuditSeverity.MEDIUM,
            tags=["user_management", "administration"],
        )

    def log_agent_event(
        self,
        event_type: AuditEventType,
        agent_id: str,
        user_id: str,
        action: str,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        session_id: str = None,
    ) -> str:
        """Log agent-related events"""
        return self.log_event(
            event_type=event_type,
            action=f"Agent {action}",
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            resource=f"agent:{agent_id}",
            details={"agent_id": agent_id, "action": action, **(details or {})},
            outcome="success",
            severity=AuditSeverity.MEDIUM,
            tags=["agent", "automation"],
        )

    def log_task_event(
        self,
        event_type: AuditEventType,
        task_id: str,
        user_id: str,
        action: str,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        session_id: str = None,
    ) -> str:
        """Log task-related events"""
        return self.log_event(
            event_type=event_type,
            action=f"Task {action}",
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            resource=f"task:{task_id}",
            details={"task_id": task_id, "action": action, **(details or {})},
            outcome="success",
            severity=AuditSeverity.MEDIUM,
            tags=["task", "workflow"],
        )

    def log_security_event(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: str = None,
        ip_address: str = None,
        details: Dict[str, Any] = None,
        severity: AuditSeverity = AuditSeverity.HIGH,
    ) -> str:
        """Log security-related events"""
        return self.log_event(
            event_type=event_type,
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            resource="security",
            details=details or {},
            outcome="failure",
            severity=severity,
            tags=["security", "violation"],
        )

    def log_api_event(
        self,
        event_type: AuditEventType,
        method: str,
        path: str,
        user_id: str = None,
        ip_address: str = None,
        status_code: int = None,
        response_time: float = None,
        error_message: str = None,
        session_id: str = None,
    ) -> str:
        """Log API-related events"""
        outcome = "success" if status_code and status_code < 400 else "failure"
        severity = (
            AuditSeverity.HIGH
            if status_code and status_code >= 500
            else AuditSeverity.MEDIUM
        )

        return self.log_event(
            event_type=event_type,
            action=f"API {method} {path}",
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            resource=f"api:{path}",
            details={
                "method": method,
                "path": path,
                "status_code": status_code,
                "response_time": response_time,
            },
            outcome=outcome,
            error_message=error_message,
            severity=severity,
            tags=["api", "http"],
        )

    def log_system_event(
        self,
        event_type: AuditEventType,
        action: str,
        details: Dict[str, Any] = None,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
    ) -> str:
        """Log system-related events"""
        return self.log_event(
            event_type=event_type,
            action=action,
            resource="system",
            details=details or {},
            outcome="success",
            severity=severity,
            tags=["system", "infrastructure"],
        )

    def get_audit_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get audit events with filtering (placeholder implementation)"""
        # In a real implementation, this would query a database
        # For now, return empty list
        return []

    def export_audit_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        format: str = "json",
    ) -> str:
        """Export audit logs (placeholder implementation)"""
        # In a real implementation, this would export from database
        return "Audit logs exported successfully"


# Global audit logging service instance
audit_service: Optional[AuditLoggingService] = None


def get_audit_service() -> AuditLoggingService:
    """Get the global audit logging service instance"""
    global audit_service
    if audit_service is None:
        from src.config.settings import get_settings

        settings = get_settings()
        audit_service = AuditLoggingService(
            {
                "audit_log_file": settings.monitoring.log_file_path.replace(
                    ".log", "_audit.log"
                )
            }
        )
    return audit_service
