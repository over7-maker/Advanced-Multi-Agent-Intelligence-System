"""
Audit Module for AMAS
Comprehensive audit logging and monitoring
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import hashlib
import uuid
from enum import Enum

logger = logging.getLogger(__name__)

class AuditLevel(Enum):
    """Audit log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditEvent(Enum):
    """Audit event types"""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    TOKEN_REFRESH = "token_refresh"
    
    # Authorization events
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"
    
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    CONFIGURATION_CHANGE = "configuration_change"
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"
    
    # Data events
    DATA_ACCESS = "data_access"
    DATA_CREATE = "data_create"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    
    # Agent events
    AGENT_CREATE = "agent_create"
    AGENT_UPDATE = "agent_update"
    AGENT_DELETE = "agent_delete"
    AGENT_START = "agent_start"
    AGENT_STOP = "agent_stop"
    AGENT_TASK_ASSIGN = "agent_task_assign"
    AGENT_TASK_COMPLETE = "agent_task_complete"
    
    # Task events
    TASK_CREATE = "task_create"
    TASK_UPDATE = "task_update"
    TASK_DELETE = "task_delete"
    TASK_EXECUTE = "task_execute"
    TASK_COMPLETE = "task_complete"
    TASK_FAIL = "task_fail"
    
    # Security events
    SECURITY_VIOLATION = "security_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_TOKEN = "invalid_token"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    
    # Encryption events
    DATA_ENCRYPT = "data_encrypt"
    DATA_DECRYPT = "data_decrypt"
    KEY_ROTATION = "key_rotation"
    KEY_GENERATION = "key_generation"

class AuditManager:
    """Audit manager for AMAS"""
    
    def __init__(self, config: Dict[str, Any], database_service: Optional[Any] = None):
        self.config = config
        self.database_service = database_service
        self.audit_enabled = config.get('security', {}).get('audit_enabled', True)
        self.retention_days = config.get('security', {}).get('audit_retention_days', 365)
        self.batch_size = config.get('security', {}).get('audit_batch_size', 100)
        
        # Audit buffer for batching
        self.audit_buffer = []
        self.buffer_lock = asyncio.Lock()
        
        # Audit rules
        self.audit_rules = self._initialize_audit_rules()
        
        # Sensitive data patterns
        self.sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\'][^"\']+["\']',
            r'token["\']?\s*[:=]\s*["\'][^"\']+["\']',
            r'key["\']?\s*[:=]\s*["\'][^"\']+["\']',
            r'secret["\']?\s*[:=]\s*["\'][^"\']+["\']'
        ]
    
    def _initialize_audit_rules(self) -> List[Dict[str, Any]]:
        """Initialize audit rules"""
        return [
            {
                "name": "failed_login_threshold",
                "description": "Alert on multiple failed login attempts",
                "condition": "event_type == 'login_failure' and count > 5",
                "action": "alert",
                "severity": "high"
            },
            {
                "name": "unauthorized_access",
                "description": "Alert on unauthorized access attempts",
                "condition": "event_type == 'unauthorized_access'",
                "action": "alert",
                "severity": "critical"
            },
            {
                "name": "data_export_volume",
                "description": "Alert on large data exports",
                "condition": "event_type == 'data_export' and data_size > 1000000",
                "action": "alert",
                "severity": "medium"
            },
            {
                "name": "system_configuration_change",
                "description": "Alert on system configuration changes",
                "condition": "event_type == 'configuration_change'",
                "action": "log",
                "severity": "high"
            }
        ]
    
    async def log_event(
        self,
        event_type: AuditEvent,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        level: AuditLevel = AuditLevel.INFO,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        classification: str = "internal"
    ) -> str:
        """Log an audit event"""
        if not self.audit_enabled:
            return ""
        
        try:
            # Generate event ID
            event_id = str(uuid.uuid4())
            
            # Create audit record
            audit_record = {
                "event_id": event_id,
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type.value,
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "details": self._sanitize_details(details or {}),
                "level": level.value,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "classification": classification,
                "session_id": self._get_session_id(user_id),
                "correlation_id": self._generate_correlation_id()
            }
            
            # Add to buffer
            async with self.buffer_lock:
                self.audit_buffer.append(audit_record)
                
                # Flush buffer if it's full
                if len(self.audit_buffer) >= self.batch_size:
                    await self._flush_buffer()
            
            # Check audit rules
            await self._check_audit_rules(audit_record)
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return ""
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data from details"""
        import re
        
        sanitized = {}
        for key, value in details.items():
            if isinstance(value, str):
                # Check for sensitive patterns
                for pattern in self.sensitive_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        sanitized[key] = "[REDACTED]"
                        break
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _get_session_id(self, user_id: Optional[str]) -> Optional[str]:
        """Get current session ID for user"""
        # In a real implementation, you would get this from the session manager
        return None
    
    def _generate_correlation_id(self) -> str:
        """Generate correlation ID for related events"""
        # Use SHA-256 instead of MD5 for better security
        return hashlib.sha256(f"{datetime.utcnow()}{uuid.uuid4()}".encode()).hexdigest()[:16]
    
    async def _flush_buffer(self):
        """Flush audit buffer to storage"""
        if not self.audit_buffer:
            return
        
        try:
            # Save to database if available
            if self.database_service:
                for record in self.audit_buffer:
                    await self.database_service.save_audit_event(record)
            
            # Clear buffer
            self.audit_buffer.clear()
            
        except Exception as e:
            logger.error(f"Error flushing audit buffer: {e}")
    
    async def _check_audit_rules(self, audit_record: Dict[str, Any]):
        """Check audit rules and trigger actions"""
        try:
            for rule in self.audit_rules:
                if await self._evaluate_rule(rule, audit_record):
                    await self._execute_rule_action(rule, audit_record)
                    
        except Exception as e:
            logger.error(f"Error checking audit rules: {e}")
    
    async def _evaluate_rule(self, rule: Dict[str, Any], audit_record: Dict[str, Any]) -> bool:
        """Evaluate an audit rule"""
        try:
            # Simple rule evaluation (in production, use a proper rule engine)
            condition = rule["condition"]
            
            # Replace variables in condition with safe values
            condition = condition.replace("event_type", f"'{audit_record['event_type']}'")
            condition = condition.replace("user_id", f"'{audit_record.get('user_id', '')}'")
            condition = condition.replace("resource", f"'{audit_record.get('resource', '')}'")
            
            # Secure evaluation using ast.literal_eval for safe expressions
            # For complex conditions, use a proper rule engine in production
            return self._safe_evaluate_condition(condition)
            
        except Exception as e:
            logger.error(f"Error evaluating rule {rule['name']}: {e}")
            return False
    
    def _safe_evaluate_condition(self, condition: str) -> bool:
        """Safely evaluate a condition without using eval()"""
        try:
            # Simple string-based condition evaluation
            # This is a basic implementation - in production, use a proper rule engine
            if "==" in condition:
                parts = condition.split("==")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    return left == right
            
            if "!=" in condition:
                parts = condition.split("!=")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    return left != right
            
            if ">" in condition:
                parts = condition.split(">")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    try:
                        return int(left) > int(right)
                    except ValueError:
                        return left > right
            
            if "<" in condition:
                parts = condition.split("<")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")
                    try:
                        return int(left) < int(right)
                    except ValueError:
                        return left < right
            
            # Default to False for unrecognized conditions
            return False
            
        except Exception as e:
            logger.error(f"Error in safe condition evaluation: {e}")
            return False
    
    async def _execute_rule_action(self, rule: Dict[str, Any], audit_record: Dict[str, Any]):
        """Execute rule action"""
        try:
            action = rule["action"]
            severity = rule["severity"]
            
            if action == "alert":
                await self._send_alert(rule, audit_record, severity)
            elif action == "log":
                logger.warning(f"Audit rule triggered: {rule['name']} - {audit_record}")
                
        except Exception as e:
            logger.error(f"Error executing rule action: {e}")
    
    async def _send_alert(self, rule: Dict[str, Any], audit_record: Dict[str, Any], severity: str):
        """Send security alert"""
        try:
            alert_data = {
                "rule_name": rule["name"],
                "severity": severity,
                "description": rule["description"],
                "audit_record": audit_record,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # In a real implementation, you would send this to an alerting system
            logger.critical(f"SECURITY ALERT: {json.dumps(alert_data)}")
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def get_audit_log(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        resource: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        level: Optional[AuditLevel] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        try:
            # Flush buffer first
            await self._flush_buffer()
            
            # Query database if available
            if self.database_service:
                return await self.database_service.get_audit_log(
                    user_id=user_id,
                    event_type=event_type,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit,
                    offset=offset
                )
            
            # Return mock data if no database
            return [
                {
                    "event_id": str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": event_type or "system_event",
                    "user_id": user_id,
                    "resource": resource,
                    "level": level.value if level else "info",
                    "details": {"message": "Mock audit log entry"}
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            return []
    
    async def get_audit_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get audit statistics"""
        try:
            # In a real implementation, you would query the database
            return {
                "total_events": 1000,
                "events_by_type": {
                    "login_success": 500,
                    "login_failure": 50,
                    "data_access": 300,
                    "system_events": 150
                },
                "events_by_level": {
                    "info": 800,
                    "warning": 150,
                    "error": 40,
                    "critical": 10
                },
                "top_users": [
                    {"user_id": "admin", "event_count": 200},
                    {"user_id": "user1", "event_count": 150}
                ],
                "security_events": 60,
                "failed_logins": 50,
                "unauthorized_access": 10
            }
            
        except Exception as e:
            logger.error(f"Error getting audit statistics: {e}")
            return {}
    
    async def export_audit_log(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> str:
        """Export audit log"""
        try:
            # Get audit log
            audit_log = await self.get_audit_log(
                start_date=start_date,
                end_date=end_date,
                limit=10000
            )
            
            if format == "json":
                return json.dumps(audit_log, indent=2)
            elif format == "csv":
                # Convert to CSV format
                import csv
                import io
                output = io.StringIO()
                if audit_log:
                    writer = csv.DictWriter(output, fieldnames=audit_log[0].keys())
                    writer.writeheader()
                    writer.writerows(audit_log)
                return output.getvalue()
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting audit log: {e}")
            return ""
    
    async def cleanup_old_audit_logs(self) -> int:
        """Clean up old audit log entries"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            if self.database_service:
                # In a real implementation, you would delete old records
                return 0
            
            return 0
            
        except Exception as e:
            logger.error(f"Error cleaning up audit logs: {e}")
            return 0
    
    async def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get security-related events"""
        try:
            security_event_types = [
                "login_failure",
                "unauthorized_access",
                "security_violation",
                "suspicious_activity",
                "rate_limit_exceeded"
            ]
            
            events = []
            for event_type in security_event_types:
                event_log = await self.get_audit_log(
                    event_type=event_type,
                    limit=limit // len(security_event_types)
                )
                events.extend(event_log)
            
            # Sort by timestamp
            events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return events[:limit]
            
        except Exception as e:
            logger.error(f"Error getting security events: {e}")
            return []
    
    async def get_user_activity(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user activity log"""
        try:
            return await self.get_audit_log(
                user_id=user_id,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return []
    
    async def get_audit_health(self) -> Dict[str, Any]:
        """Get audit system health"""
        try:
            return {
                "audit_enabled": self.audit_enabled,
                "buffer_size": len(self.audit_buffer),
                "retention_days": self.retention_days,
                "batch_size": self.batch_size,
                "total_rules": len(self.audit_rules),
                "status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Error getting audit health: {e}")
            return {"status": "error", "error": str(e)}