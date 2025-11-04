"""
Comprehensive Audit Logging for AMAS

Provides structured audit logging with PII redaction,
buffered writes, and compliance-ready audit trails.
"""

import json
import logging
import asyncio
import hashlib
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from contextlib import asynccontextmanager
import re

logger = logging.getLogger(__name__)

class AuditEventType(str, Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    AGENT_EXECUTION = "agent_execution"
    TOOL_USAGE = "tool_usage"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_VIOLATION = "security_violation"
    SYSTEM_EVENT = "system_event"

class AuditStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class AuditEvent:
    """Structured audit event"""
    event_id: str
    timestamp: str
    event_type: AuditEventType
    status: AuditStatus
    
    # Actor information
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_roles: List[str] = field(default_factory=list)
    
    # Resource information  
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    agent_id: Optional[str] = None
    tool_name: Optional[str] = None
    
    # Action details
    action: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Request context
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Security context
    authentication_method: Optional[str] = None
    authorization_result: Optional[str] = None
    risk_score: float = 0.0
    
    # Data governance
    data_classification: Optional[str] = None
    pii_detected: bool = False
    sensitive_data_redacted: bool = True
    
    # Performance metrics
    duration_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None

class PIIRedactor:
    """Redacts PII from audit log data"""
    
    def __init__(self):
        # PII patterns
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.IGNORECASE),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'),
            'phone': re.compile(r'\b\d{3}-\d{3}-\d{4}\b|\(\d{3}\)\s?\d{3}-\d{4}'),
            'credit_card': re.compile(r'\b(?:4\d{12}(?:\d{3})?|5[1-5]\d{14}|3[47]\d{13})\b'),
            'api_key': re.compile(r'\b[A-Za-z0-9]{32,}\b|sk-[A-Za-z0-9]{48}'),
            'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        }
        
        # Sensitive field names
        self.sensitive_fields = {
            'password', 'secret', 'token', 'key', 'credential', 'auth',
            'api_key', 'access_token', 'refresh_token', 'private_key',
            'ssn', 'social_security', 'credit_card', 'card_number',
            'phone', 'mobile', 'address', 'location', 'gps'
        }
    
    def redact_text(self, text: str) -> tuple[str, bool]:
        """Redact PII from text content"""
        if not text or not isinstance(text, str):
            return text, False
        
        redacted_text = text
        pii_found = False
        
        # Apply PII patterns
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(redacted_text):
                pii_found = True
                redacted_text = pattern.sub(f'[{pii_type.upper()}_REDACTED]', redacted_text)
        
        return redacted_text, pii_found
    
    def redact_dict(self, data: Dict[str, Any]) -> tuple[Dict[str, Any], bool]:
        """Recursively redact PII from dictionary"""
        if not isinstance(data, dict):
            return data, False
        
        redacted_data = {}
        any_pii_found = False
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if field name indicates sensitive data
            if any(sensitive_field in key_lower for sensitive_field in self.sensitive_fields):
                redacted_data[key] = "[REDACTED]"
                any_pii_found = True
            elif isinstance(value, str):
                # Redact text content
                redacted_value, pii_found = self.redact_text(value)
                redacted_data[key] = redacted_value
                if pii_found:
                    any_pii_found = True
            elif isinstance(value, dict):
                # Recursively redact nested dictionaries
                redacted_nested, pii_found = self.redact_dict(value)
                redacted_data[key] = redacted_nested
                if pii_found:
                    any_pii_found = True
            elif isinstance(value, list):
                # Redact list items
                redacted_list = []
                for item in value:
                    if isinstance(item, dict):
                        redacted_item, pii_found = self.redact_dict(item)
                        redacted_list.append(redacted_item)
                        if pii_found:
                            any_pii_found = True
                    elif isinstance(item, str):
                        redacted_item, pii_found = self.redact_text(item)
                        redacted_list.append(redacted_item)
                        if pii_found:
                            any_pii_found = True
                    else:
                        redacted_list.append(item)
                redacted_data[key] = redacted_list
            else:
                # Keep non-string, non-dict values as-is
                redacted_data[key] = value
        
        return redacted_data, any_pii_found

class AuditLogger:
    """High-performance audit logger with buffering and async writes"""
    
    def __init__(self, 
                 log_file: str = "logs/audit.jsonl",
                 buffer_size: int = 100,
                 flush_interval: int = 30,
                 enable_redaction: bool = True,
                 backup_count: int = 5):
        self.log_file = Path(log_file)
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.enable_redaction = enable_redaction
        self.backup_count = backup_count
        
        self._buffer: List[AuditEvent] = []
        self._buffer_lock = asyncio.Lock()
        self._last_flush = datetime.now(timezone.utc)
        self._flush_task: Optional[asyncio.Task] = None
        
        self.pii_redactor = PIIRedactor() if enable_redaction else None
        
        # Create log directory
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup structured logging
        self.logger = self._setup_logger()
        
        # Start background flush task
        self._start_flush_task()
        
        logger.info(f"Audit logger initialized: {log_file} (buffer: {buffer_size}, redaction: {enable_redaction})")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup structured audit logger"""
        audit_logger = logging.getLogger("amas.audit")
        audit_logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in audit_logger.handlers[:]:
            audit_logger.removeHandler(handler)
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(
            self.log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=self.backup_count
        )
        
        # JSON formatter
        handler.setFormatter(logging.Formatter('%(message)s'))
        audit_logger.addHandler(handler)
        
        # Prevent propagation to root logger
        audit_logger.propagate = False
        
        return audit_logger
    
    def _start_flush_task(self):
        """Start background task for periodic buffer flushing"""
        self._flush_task = asyncio.create_task(self._periodic_flush())
    
    async def _periodic_flush(self):
        """Periodically flush buffer to disk"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self.flush_buffer()
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")
    
    async def log_event(self, event: AuditEvent):
        """Log an audit event with automatic buffering and redaction"""
        # Redact PII if enabled
        if self.enable_redaction and self.pii_redactor:
            redacted_details, pii_found = self.pii_redactor.redact_dict(event.details)
            event.details = redacted_details
            event.pii_detected = pii_found
            event.sensitive_data_redacted = True
        
        # Add to buffer
        async with self._buffer_lock:
            self._buffer.append(event)
            
            # Check if immediate flush is needed
            buffer_full = len(self._buffer) >= self.buffer_size
            time_exceeded = (
                datetime.now(timezone.utc) - self._last_flush
            ).seconds >= self.flush_interval
            
            if buffer_full or time_exceeded:
                await self._flush_buffer_internal()
    
    async def flush_buffer(self):
        """Manually flush buffer to disk"""
        async with self._buffer_lock:
            await self._flush_buffer_internal()
    
    async def _flush_buffer_internal(self):
        """Internal buffer flush (must be called with buffer_lock held)"""
        if not self._buffer:
            return
        
        events_to_flush = self._buffer.copy()
        self._buffer.clear()
        self._last_flush = datetime.now(timezone.utc)
        
        # Write events to log file (outside the lock)
        try:
            for event in events_to_flush:
                event_dict = asdict(event)
                self.logger.info(json.dumps(event_dict, default=str))
            
            logger.debug(f"Flushed {len(events_to_flush)} audit events")
            
        except Exception as e:
            logger.error(f"Failed to flush audit events: {e}")
            # Re-add events to buffer for retry
            async with self._buffer_lock:
                self._buffer.extend(events_to_flush)
    
    # Convenience methods for common audit events
    async def log_authentication(self, 
                               user_id: str,
                               status: AuditStatus,
                               method: str = "jwt",
                               ip_address: Optional[str] = None,
                               user_agent: Optional[str] = None,
                               details: Optional[Dict] = None):
        """Log authentication event"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=AuditEventType.AUTHENTICATION,
            status=status,
            user_id=user_id,
            action="authenticate",
            authentication_method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
        await self.log_event(event)
    
    async def log_agent_execution(self,
                                user_id: str,
                                agent_id: str,
                                action: str,
                                status: AuditStatus,
                                duration_ms: Optional[float] = None,
                                tokens_used: Optional[int] = None,
                                cost_usd: Optional[float] = None,
                                trace_id: Optional[str] = None,
                                details: Optional[Dict] = None):
        """Log agent execution event"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=AuditEventType.AGENT_EXECUTION,
            status=status,
            user_id=user_id,
            agent_id=agent_id,
            resource_type="agent",
            resource_id=agent_id,
            action=action,
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            trace_id=trace_id,
            details=details or {}
        )
        await self.log_event(event)
    
    async def log_tool_usage(self,
                           user_id: str,
                           agent_id: str,
                           tool_name: str,
                           status: AuditStatus,
                           parameters: Dict[str, Any],
                           duration_ms: Optional[float] = None,
                           trace_id: Optional[str] = None):
        """Log tool usage event"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=AuditEventType.TOOL_USAGE,
            status=status,
            user_id=user_id,
            agent_id=agent_id,
            tool_name=tool_name,
            resource_type="tool",
            resource_id=tool_name,
            action="execute",
            duration_ms=duration_ms,
            trace_id=trace_id,
            details={
                "tool_name": tool_name,
                "parameters": parameters,
                "parameter_count": len(parameters)
            }
        )
        await self.log_event(event)
    
    async def log_security_violation(self,
                                   user_id: Optional[str],
                                   violation_type: str,
                                   severity: str,
                                   description: str,
                                   ip_address: Optional[str] = None,
                                   trace_id: Optional[str] = None,
                                   details: Optional[Dict] = None):
        """Log security violation"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=AuditEventType.SECURITY_VIOLATION,
            status=AuditStatus.BLOCKED,
            user_id=user_id,
            action="security_violation",
            ip_address=ip_address,
            trace_id=trace_id,
            risk_score=1.0 if severity == "critical" else 0.7,
            details={
                "violation_type": violation_type,
                "severity": severity,
                "description": description,
                **(details or {})
            }
        )
        await self.log_event(event)
    
    async def log_data_access(self,
                            user_id: str,
                            resource_type: str,
                            resource_id: str,
                            operation: str,
                            status: AuditStatus,
                            data_classification: str = "internal",
                            records_affected: Optional[int] = None,
                            trace_id: Optional[str] = None,
                            details: Optional[Dict] = None):
        """Log data access event"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=AuditEventType.DATA_ACCESS,
            status=status,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=operation,
            data_classification=data_classification,
            trace_id=trace_id,
            details={
                "operation": operation,
                "records_affected": records_affected,
                "data_classification": data_classification,
                **(details or {})
            }
        )
        await self.log_event(event)
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        random_data = os.urandom(8).hex()
        return hashlib.sha256(f"{timestamp}:{random_data}".encode()).hexdigest()[:16]
    
    async def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit summary for recent period"""
        # In production, this would query stored audit logs
        # For now, return summary from current buffer
        
        async with self._buffer_lock:
            buffer_copy = self._buffer.copy()
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        recent_events = [
            event for event in buffer_copy
            if datetime.fromisoformat(event.timestamp) >= cutoff_time
        ]
        
        # Count events by type and status
        event_counts = {}
        status_counts = {}
        user_activity = {}
        
        for event in recent_events:
            # Event type counts
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # Status counts
            status = event.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # User activity
            if event.user_id:
                if event.user_id not in user_activity:
                    user_activity[event.user_id] = {"events": 0, "last_activity": event.timestamp}
                user_activity[event.user_id]["events"] += 1
                user_activity[event.user_id]["last_activity"] = max(
                    user_activity[event.user_id]["last_activity"], event.timestamp
                )
        
        return {
            "period_hours": hours,
            "total_events": len(recent_events),
            "event_types": event_counts,
            "status_distribution": status_counts,
            "active_users": len(user_activity),
            "user_activity": user_activity,
            "pii_detections": len([e for e in recent_events if e.pii_detected]),
            "security_violations": len([e for e in recent_events if e.event_type == AuditEventType.SECURITY_VIOLATION])
        }
    
    async def search_audit_logs(self, 
                              user_id: Optional[str] = None,
                              event_type: Optional[AuditEventType] = None,
                              agent_id: Optional[str] = None,
                              hours: int = 24) -> List[AuditEvent]:
        """Search audit logs with filters"""
        async with self._buffer_lock:
            buffer_copy = self._buffer.copy()
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        filtered_events = []
        for event in buffer_copy:
            # Time filter
            if datetime.fromisoformat(event.timestamp) < cutoff_time:
                continue
                
            # User filter
            if user_id and event.user_id != user_id:
                continue
                
            # Event type filter
            if event_type and event.event_type != event_type:
                continue
                
            # Agent filter
            if agent_id and event.agent_id != agent_id:
                continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    @asynccontextmanager
    async def audit_context(self, 
                           user_id: str,
                           operation: str,
                           resource_type: str,
                           resource_id: str,
                           trace_id: Optional[str] = None):
        """Context manager for automatic audit logging"""
        start_time = datetime.now(timezone.utc)
        
        try:
            yield
            
            # Log successful operation
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            await self.log_event(AuditEvent(
                event_id=self._generate_event_id(),
                timestamp=start_time.isoformat(),
                event_type=AuditEventType.SYSTEM_EVENT,
                status=AuditStatus.SUCCESS,
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=operation,
                duration_ms=duration_ms,
                trace_id=trace_id,
                details={"operation": operation}
            ))
            
        except Exception as e:
            # Log failed operation
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            await self.log_event(AuditEvent(
                event_id=self._generate_event_id(),
                timestamp=start_time.isoformat(),
                event_type=AuditEventType.SYSTEM_EVENT,
                status=AuditStatus.ERROR,
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=operation,
                duration_ms=duration_ms,
                trace_id=trace_id,
                details={
                    "operation": operation,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            ))
            
            raise
    
    async def shutdown(self):
        """Graceful shutdown - flush remaining events"""
        logger.info("Shutting down audit logger...")
        
        # Cancel flush task
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        await self.flush_buffer()
        
        logger.info("Audit logger shutdown complete")

# Global audit logger instance
_global_audit_logger: Optional[AuditLogger] = None

def initialize_audit_logger(config: Dict[str, Any]) -> AuditLogger:
    """Initialize global audit logger"""
    global _global_audit_logger
    
    audit_config = config.get("audit", {})
    
    _global_audit_logger = AuditLogger(
        log_file=audit_config.get("log_file", "logs/audit.jsonl"),
        buffer_size=audit_config.get("buffer_size", 100),
        flush_interval=audit_config.get("flush_interval", 30),
        enable_redaction=audit_config.get("redact_sensitive", True),
        backup_count=audit_config.get("backup_count", 5)
    )
    
    return _global_audit_logger

def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    if _global_audit_logger is None:
        # Initialize with defaults
        return initialize_audit_logger({})
    return _global_audit_logger

# Decorator for automatic audit logging
def audit_operation(operation_name: str, 
                   resource_type: str, 
                   resource_id_param: str = "resource_id"):
    """Decorator to automatically audit operations"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            audit_logger = get_audit_logger()
            
            # Extract context from parameters
            user_id = kwargs.get("user_id", "system")
            resource_id = kwargs.get(resource_id_param, "unknown")
            trace_id = kwargs.get("trace_id")
            
            async with audit_logger.audit_context(
                user_id=user_id,
                operation=operation_name,
                resource_type=resource_type,
                resource_id=resource_id,
                trace_id=trace_id
            ):
                return await func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else func
    return decorator
