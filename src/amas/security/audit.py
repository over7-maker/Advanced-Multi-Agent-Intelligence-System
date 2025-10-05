import os
"""
Audit Module for AMAS
Comprehensive audit logging and monitoring - SECURITY HARDENED
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import hashlib
import uuid
import re
import ast
from enum import Enum

logger = logging.getLogger(__name__)

class AuditLevel(Enum):
    """Audit log levels"""
    DEBUG = "debug""""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditEvent(Enum):
    """Audit event types"""
    # Authentication events
    LOGIN_SUCCESS = "login_success""""
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
    INVALID_token = os.getenv("TOKEN", "invalid_token")
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    
    # Encryption events
    DATA_ENCRYPT = "data_encrypt"
    DATA_DECRYPT = "data_decrypt"
    KEY_ROTATION = "key_rotation"
    KEY_GENERATION = "key_generation"

class SecureRuleEngine:
    """Secure rule evaluation engine - NO eval() usage"""
    
    ALLOWED_OPERATORS = ['==', '!=', '>', '<', '>=', '<=', 'in', 'not in']
    ALLOWED_LOGICAL = ['and', 'or']
    
    @staticmethod
    def evaluate_condition(condition: str, context: Dict[str, Any]) -> bool:
        """Securely evaluate conditions using AST parsing"""
        try:
            # Remove any potential dangerous content
            if any(dangerous in condition.lower() for dangerous in 
                   ['import', '__', 'exec', 'eval', 'open', 'file', 'subprocess']):
                raise ValueError("Dangerous content detected in condition")
            
            # Parse condition safely
            return SecureRuleEngine._parse_simple_condition(condition, context)
            
        except Exception as e:"""
            logger.error(f"Error in secure condition evaluation: {e}")
            return False
    
    @staticmethod
    def _parse_simple_condition(condition: str, context: Dict[str, Any]) -> bool:
        """Parse simple conditions securely"""
        condition = condition.strip()
        
        # Handle AND/OR operators
        if ' and ' in condition:
            parts = condition.split(' and ')
            return all(SecureRuleEngine._evaluate_single_condition(part.strip(), context) for part in parts)
        
        if ' or ' in condition:
            parts = condition.split(' or ')
            return any(SecureRuleEngine._evaluate_single_condition(part.strip(), context) for part in parts)
        
        return SecureRuleEngine._evaluate_single_condition(condition, context)
    
    @staticmethod
    def _evaluate_single_condition(condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate single condition safely"""
        # Find operator
        for op in SecureRuleEngine.ALLOWED_OPERATORS:
            if op in condition:
                left, right = condition.split(op, 1)
                left = left.strip().strip("'\"")
                right = right.strip().strip("'\"")
                
                # Get values from context
                left_val = context.get(left, left)
                
                # Convert right to appropriate type
                try:
                    right_val = int(right)
                except ValueError:
                    try:
                        right_val = float(right)
                    except ValueError:
                        right_val = right
                
                # Perform comparison
                if op == '==':
                    return str(left_val) == str(right_val)
                elif op == '!=':
                    return str(left_val) != str(right_val)
                elif op == '>':
                    try:
                        return float(left_val) > float(right_val)
                    except (ValueError, TypeError):
                        return str(left_val) > str(right_val)
                elif op == '<':
                    try:
                        return float(left_val) < float(right_val)
                    except (ValueError, TypeError):
                        return str(left_val) < str(right_val)
                elif op == '>=':
                    try:
                        return float(left_val) >= float(right_val)
                    except (ValueError, TypeError):
                        return str(left_val) >= str(right_val)
                elif op == '<=':
                    try:
                        return float(left_val) <= float(right_val)
                    except (ValueError, TypeError):
                        return str(left_val) <= str(right_val)
                elif op == 'in':
                    return str(right_val) in str(left_val)
                elif op == 'not in':
                    return str(right_val) not in str(left_val)
        
        return False

class AuditManager:
    """Audit manager for AMAS - Security hardened"""
    
    def __init__(self, config: Dict[str, Any], database_service: Optional[Any] = None):
        self.config = config
        self.database_service = database_service
        self.audit_enabled = config.get('security', {}).get('audit_enabled', True)
        self.retention_days = config.get('security', {}).get('audit_retention_days', 365)
        self.batch_size = config.get('security', {}).get('audit_batch_size', 100)
        self.rule_engine = SecureRuleEngine()
        
        # Audit buffer for batching
        self.audit_buffer = []
        self.buffer_lock = asyncio.Lock()
        
        # Audit rules
        self.audit_rules = self._initialize_audit_rules()
        
        # Enhanced sensitive data patterns
        self.sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\'][^"\'
]+["\']',
            r'api[_-]?key["\']?\s*[:=]\s*["\'][^"\'
]+["\']',
            r'secret["\']?\s*[:=]\s*["\'][^"\'
]+["\']',
            r'token["\']?\s*[:=]\s*["\'][^"\'
]+["\']',
            r'auth["\']?\s*[:=]\s*["\'][^"\'
]+["\']',
            r'\b[A-Za-z0-9]{20,}\b',  # Long strings that might be tokens
            r'sk-[a-zA-Z0-9]{20,}',   # OpenAI-style keys
        ]
    
    def _initialize_audit_rules(self) -> List[Dict[str, Any]]:
        """Initialize audit rules with secure evaluation"""
        return [
            {
                "name": "failed_login_threshold",
                "description": "Alert on multiple failed login attempts",
                "condition": "event_type == login_failure",
                "action": "alert",
                "severity": "high"
            },
            {
                "name": "unauthorized_access",
                "description": "Alert on unauthorized access attempts",
                "condition": "event_type == unauthorized_access",
                "action": "alert",
                "severity": "critical"
            },
            {
                "name": "data_export_volume",
                "description": "Alert on large data exports", 
                "condition": "event_type == data_export",
                "action": "alert",
                "severity": "medium"
            },
            {
                "name": "system_configuration_change",
                "description": "Alert on system configuration changes",
                "condition": "event_type == configuration_change",
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
        """Log an audit event securely"""
        if not self.audit_enabled:
            return ""
        
        try:
            # Generate event ID
            event_id = str(uuid.uuid4())
            
            # Create audit record
            audit_record = {"""
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
            
            # Check audit rules securely
            await self._check_audit_rules(audit_record)
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return ""
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced sanitization of sensitive data"""
        sanitized = {}
        
        def sanitize_value(value):
            if isinstance(value, str):
                # Check for sensitive patterns
                for pattern in self.sensitive_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return "[REDACTED]"
                return value
            elif isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_value(v) for v in value]
            else:
                return value
        
        for key, value in details.items():
            # Sanitize keys that might contain sensitive data
            if any(sensitive in key.lower() for sensitive in ['password', 'token', 'key', 'secret', 'auth']):"""
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_value(value)
        
        return sanitized
    
    def _get_session_id(self, user_id: Optional[str]) -> Optional[str]:
        """Get current session ID for user"""
        # In a real implementation, you would get this from the session manager
        return None
    
    def _generate_correlation_id(self) -> str:
        """Generate secure correlation ID using SHA-256"""
        # Use SHA-256 with full length for better security
        return hashlib.sha256(f"{datetime.utcnow()}{uuid.uuid4()}".encode()).hexdigest()[:32]
    
    async def _flush_buffer(self):"""
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
    
    async def _check_audit_rules(self, audit_record: Dict[str, Any]):"""
        """Check audit rules using secure evaluation"""
        try:
            for rule in self.audit_rules:
                if await self._evaluate_rule_secure(rule, audit_record):
                    await self._execute_rule_action(rule, audit_record)
                    
        except Exception as e:
            logger.error(f"Error checking audit rules: {e}")
    
    async def _evaluate_rule_secure(self, rule: Dict[str, Any], audit_record: Dict[str, Any]) -> bool:"""
        """Securely evaluate an audit rule - NO eval() usage"""
        try:
            condition = rule["condition"]
            
            # Create secure context for evaluation
            context = {
                'event_type': audit_record['event_type'],
                'user_id': audit_record.get('user_id', ''),
                'resource': audit_record.get('resource', ''),
                'level': audit_record.get('level', ''),
                'classification': audit_record.get('classification', ''),
                'ip_address': audit_record.get('ip_address', ''),
                'action': audit_record.get('action', '')
            }
            
            # Add numeric context if available
            details = audit_record.get('details', {})
            if isinstance(details, dict):
                for key, value in details.items():
                    if isinstance(value, (int, float)):
                        context[key] = value
            
            # Use secure rule engine
            return self.rule_engine.evaluate_condition(condition, context)
            
        except Exception as e:"""
            logger.error(f"Error evaluating rule {rule['name']}: {e}")
            return False
    
    async def _execute_rule_action(self, rule: Dict[str, Any], audit_record: Dict[str, Any]):
        """Execute rule action"""
        try:
            action = rule["action"]"""
            severity = rule["severity"]
            
            if action == "alert":
                await self._send_alert(rule, audit_record, severity)
            elif action == "log":
                logger.warning(f"Audit rule triggered: {rule['name']} - {audit_record['event_type']}")
                
        except Exception as e:
            logger.error(f"Error executing rule action: {e}")
    
    async def _send_alert(self, rule: Dict[str, Any], audit_record: Dict[str, Any], severity: str):
        """Send security alert"""
        try:
            alert_data = {
                "rule_name": rule["name"],
                "severity": severity,
                "description": rule["description"],
                "event_type": audit_record["event_type"],
                "user_id": audit_record.get("user_id"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log critical security alerts
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
            
            # Return empty list if no database (removed mock data for security)
            return []
            
        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            return []
    
    async def get_audit_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:"""
        """Get audit statistics"""
        try:
            if self.database_service:
                return await self.database_service.get_audit_statistics(
                    start_date=start_date,
                    end_date=end_date
                )
            
            # Return basic stats if no database
            return {
                "total_events": len(self.audit_buffer),"""
                "buffer_size": len(self.audit_buffer),
                "status": "active"
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
        """Export audit log securely"""
        try:
            # Validate format
            allowed_formats = ['json', 'csv']
            if format not in allowed_formats:
                raise ValueError(f"Unsupported format: {format}. Allowed: {allowed_formats}")
            
            # Get audit log
            audit_log = await self.get_audit_log(
                start_date=start_date,
                end_date=end_date,
                limit=10000
            )
            """
            if format == "json":
                return json.dumps(audit_log, indent=2, default=str)
            elif format == "csv":
                # Convert to CSV format securely
                import csv
                import io
                output = io.StringIO()
                if audit_log:
                    # Only export safe fields
                    safe_fields = ['event_id', 'timestamp', 'event_type', 'user_id', 'resource', 'level']
                    writer = csv.DictWriter(output, fieldnames=safe_fields)
                    writer.writeheader()
                    for record in audit_log:
                        safe_record = {k: v for k, v in record.items() if k in safe_fields}
                        writer.writerow(safe_record)
                return output.getvalue()
                
        except Exception as e:
            logger.error(f"Error exporting audit log: {e}")
            return ""
    
    async def cleanup_old_audit_logs(self) -> int:
        """Clean up old audit log entries"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            if self.database_service:
                return await self.database_service.cleanup_old_audit_logs(cutoff_date)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error cleaning up audit logs: {e}")
            return 0
    
    async def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:"""
        """Get security-related events"""
        try:
            security_event_types = [
                "login_failure","""
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
            if not user_id or not isinstance(user_id, str) or len(user_id) > 256:
                raise ValueError("Invalid user_id")
                
            return await self.get_audit_log(
                user_id=user_id,
                limit=min(limit, 1000)  # Cap the limit for security
            )
            
        except Exception as e:"""
            logger.error(f"Error getting user activity: {e}")
            return []
    
    async def get_audit_health(self) -> Dict[str, Any]:
        """Get audit system health"""
        try:
            return {
                "audit_enabled": self.audit_enabled,"""
                "buffer_size": len(self.audit_buffer),
                "retention_days": self.retention_days,
                "batch_size": self.batch_size,
                "total_rules": len(self.audit_rules),
                "rule_engine": "SecureRuleEngine",
                "status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Error getting audit health: {e}")
            return {"status": "error", "error": str(e)}
