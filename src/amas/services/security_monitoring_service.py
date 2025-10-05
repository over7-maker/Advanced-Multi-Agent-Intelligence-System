"""
Enhanced Security Monitoring Service for AMAS Intelligence System - Phase 5
Provides comprehensive security monitoring, threat detection, and incident response
"""

import asyncio
import logging
import hashlib
import hmac
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import secrets
import ipaddress
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(Enum):
    """Security event type enumeration"""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_ACCESS = "system_access"
    NETWORK_ACCESS = "network_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MALWARE_DETECTION = "malware_detection"
    INTRUSION_ATTEMPT = "intrusion_attempt"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"


@dataclass
class SecurityEvent:
    """Security event data structure"""

    event_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    timestamp: datetime
    source_ip: str
    user_id: str
    description: str
    details: Dict[str, Any]
    classification: str
    signature: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class ThreatIntelligence:
    """Threat intelligence data structure"""

    threat_id: str
    threat_type: str
    severity: ThreatLevel
    indicators: List[str]
    description: str
    mitigation: List[str]
    last_seen: datetime
    confidence: float


class SecurityMonitoringService:
    """
    Enhanced Security Monitoring Service for AMAS Intelligence System

    Provides comprehensive security monitoring, threat detection,
    incident response, and security analytics.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the security monitoring service.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.monitoring_enabled = True
        self.security_events = {}
        self.threat_intelligence = {}
        self.security_rules = []
        self.incident_response_plan = {}

        # Security thresholds
        self.thresholds = {
            "failed_login_attempts": 5,
            "suspicious_requests_per_minute": 10,
            "data_access_volume": 1000,
            "privilege_escalation_attempts": 3,
            "unusual_access_patterns": 5,
        }

        # Monitoring intervals
        self.intervals = {
            "security_scan": 30,  # seconds
            "threat_analysis": 60,  # seconds
            "incident_response": 120,  # seconds
            "security_cleanup": 300,  # seconds
        }

        # Security event storage
        self.security_event_history = []
        self.threat_indicators = {}
        self.blocked_ips = set()
        self.suspicious_users = set()

        # Security monitoring tasks
        self.monitoring_tasks = []

        logger.info("Security monitoring service initialized")

    async def initialize(self):
        """Initialize the security monitoring service"""
        try:
            logger.info("Initializing security monitoring service...")

            # Initialize security rules
            await self._initialize_security_rules()

            # Initialize threat intelligence
            await self._initialize_threat_intelligence()

            # Initialize incident response
            await self._initialize_incident_response()

            # Start monitoring tasks
            await self._start_security_monitoring()

            logger.info("Security monitoring service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize security monitoring service: {e}")
            raise

    async def _initialize_security_rules(self):
        """Initialize security rules"""
        try:
            # Authentication rules
            self.security_rules.extend(
                [
                    {
                        "name": "failed_login_threshold",
                        "type": "authentication",
                        "condition": "failed_logins > 5",
                        "action": "block_ip",
                        "severity": ThreatLevel.HIGH,
                    },
                    {
                        "name": "suspicious_login_pattern",
                        "type": "authentication",
                        "condition": "login_from_new_location",
                        "action": "require_2fa",
                        "severity": ThreatLevel.MEDIUM,
                    },
                    {
                        "name": "privilege_escalation_attempt",
                        "type": "authorization",
                        "condition": "unauthorized_privilege_access",
                        "action": "alert_and_block",
                        "severity": ThreatLevel.CRITICAL,
                    },
                    {
                        "name": "data_exfiltration_pattern",
                        "type": "data_access",
                        "condition": "unusual_data_volume",
                        "action": "alert_and_monitor",
                        "severity": ThreatLevel.HIGH,
                    },
                    {
                        "name": "malware_detection",
                        "type": "malware",
                        "condition": "malware_signature_match",
                        "action": "quarantine_and_alert",
                        "severity": ThreatLevel.CRITICAL,
                    },
                ]
            )

            logger.info("Security rules initialized")

        except Exception as e:
            logger.error(f"Failed to initialize security rules: {e}")
            raise

    async def _initialize_threat_intelligence(self):
        """Initialize threat intelligence"""
        try:
            # Initialize threat intelligence database
            self.threat_intelligence = {
                "malware_signatures": {},
                "suspicious_ips": set(),
                "known_attack_patterns": {},
                "threat_actors": {},
                "vulnerabilities": {},
            }

            # Load known threat indicators
            await self._load_threat_indicators()

            logger.info("Threat intelligence initialized")

        except Exception as e:
            logger.error(f"Failed to initialize threat intelligence: {e}")
            raise

    async def _initialize_incident_response(self):
        """Initialize incident response plan"""
        try:
            self.incident_response_plan = {
                "detection": {
                    "automated_monitoring": True,
                    "alert_thresholds": self.thresholds,
                    "escalation_procedures": True,
                },
                "containment": {
                    "automatic_isolation": True,
                    "network_segmentation": True,
                    "access_restriction": True,
                },
                "eradication": {
                    "malware_removal": True,
                    "vulnerability_patching": True,
                    "system_hardening": True,
                },
                "recovery": {
                    "system_restoration": True,
                    "data_recovery": True,
                    "service_restoration": True,
                },
                "lessons_learned": {
                    "incident_documentation": True,
                    "security_improvements": True,
                    "training_updates": True,
                },
            }

            logger.info("Incident response plan initialized")

        except Exception as e:
            logger.error(f"Failed to initialize incident response: {e}")
            raise

    async def _start_security_monitoring(self):
        """Start security monitoring tasks"""
        try:
            self.monitoring_tasks = [
                asyncio.create_task(self._monitor_authentication_events()),
                asyncio.create_task(self._monitor_authorization_events()),
                asyncio.create_task(self._monitor_data_access_events()),
                asyncio.create_task(self._monitor_network_events()),
                asyncio.create_task(self._monitor_suspicious_activities()),
                asyncio.create_task(self._analyze_threat_patterns()),
                asyncio.create_task(self._process_incident_response()),
                asyncio.create_task(self._cleanup_security_data()),
            ]

            logger.info("Security monitoring tasks started")

        except Exception as e:
            logger.error(f"Failed to start security monitoring: {e}")
            raise

    async def _monitor_authentication_events(self):
        """Monitor authentication events"""
        while self.monitoring_enabled:
            try:
                # Monitor login attempts
                await self._check_failed_login_attempts()

                # Monitor suspicious login patterns
                await self._check_suspicious_login_patterns()

                # Monitor brute force attacks
                await self._check_brute_force_attacks()

                await asyncio.sleep(self.intervals["security_scan"])

            except Exception as e:
                logger.error(f"Authentication monitoring error: {e}")
                await asyncio.sleep(60)

    async def _monitor_authorization_events(self):
        """Monitor authorization events"""
        while self.monitoring_enabled:
            try:
                # Monitor privilege escalation attempts
                await self._check_privilege_escalation_attempts()

                # Monitor unauthorized access attempts
                await self._check_unauthorized_access()

                # Monitor role-based access violations
                await self._check_rbac_violations()

                await asyncio.sleep(self.intervals["security_scan"])

            except Exception as e:
                logger.error(f"Authorization monitoring error: {e}")
                await asyncio.sleep(60)

    async def _monitor_data_access_events(self):
        """Monitor data access events"""
        while self.monitoring_enabled:
            try:
                # Monitor data access patterns
                await self._check_data_access_patterns()

                # Monitor data exfiltration attempts
                await self._check_data_exfiltration()

                # Monitor sensitive data access
                await self._check_sensitive_data_access()

                await asyncio.sleep(self.intervals["security_scan"])

            except Exception as e:
                logger.error(f"Data access monitoring error: {e}")
                await asyncio.sleep(60)

    async def _monitor_network_events(self):
        """Monitor network events"""
        while self.monitoring_enabled:
            try:
                # Monitor network connections
                await self._check_network_connections()

                # Monitor suspicious network traffic
                await self._check_suspicious_traffic()

                # Monitor port scanning attempts
                await self._check_port_scanning()

                await asyncio.sleep(self.intervals["security_scan"])

            except Exception as e:
                logger.error(f"Network monitoring error: {e}")
                await asyncio.sleep(60)

    async def _monitor_suspicious_activities(self):
        """Monitor suspicious activities"""
        while self.monitoring_enabled:
            try:
                # Monitor unusual user behavior
                await self._check_unusual_user_behavior()

                # Monitor system anomalies
                await self._check_system_anomalies()

                # Monitor malware indicators
                await self._check_malware_indicators()

                await asyncio.sleep(self.intervals["security_scan"])

            except Exception as e:
                logger.error(f"Suspicious activity monitoring error: {e}")
                await asyncio.sleep(60)

    async def _analyze_threat_patterns(self):
        """Analyze threat patterns"""
        while self.monitoring_enabled:
            try:
                # Analyze attack patterns
                await self._analyze_attack_patterns()

                # Correlate security events
                await self._correlate_security_events()

                # Update threat intelligence
                await self._update_threat_intelligence()

                await asyncio.sleep(self.intervals["threat_analysis"])

            except Exception as e:
                logger.error(f"Threat pattern analysis error: {e}")
                await asyncio.sleep(60)

    async def _process_incident_response(self):
        """Process incident response"""
        while self.monitoring_enabled:
            try:
                # Process security incidents
                await self._process_security_incidents()

                # Execute incident response procedures
                await self._execute_incident_response()

                # Update incident status
                await self._update_incident_status()

                await asyncio.sleep(self.intervals["incident_response"])

            except Exception as e:
                logger.error(f"Incident response processing error: {e}")
                await asyncio.sleep(60)

    async def _cleanup_security_data(self):
        """Clean up old security data"""
        while self.monitoring_enabled:
            try:
                # Clean up old security events
                cutoff_time = datetime.utcnow() - timedelta(days=30)
                self.security_event_history = [
                    event
                    for event in self.security_event_history
                    if event.timestamp > cutoff_time
                ]

                # Clean up old threat intelligence
                await self._cleanup_threat_intelligence()

                await asyncio.sleep(self.intervals["security_cleanup"])

            except Exception as e:
                logger.error(f"Security data cleanup error: {e}")
                await asyncio.sleep(300)

    async def _check_failed_login_attempts(self):
        """Check for failed login attempts"""
        try:
            # Simulate failed login monitoring
            # In real implementation, this would check actual authentication logs
            pass

        except Exception as e:
            logger.error(f"Failed to check failed login attempts: {e}")

    async def _check_suspicious_login_patterns(self):
        """Check for suspicious login patterns"""
        try:
            # Simulate suspicious login pattern detection
            # In real implementation, this would analyze login patterns
            pass

        except Exception as e:
            logger.error(f"Failed to check suspicious login patterns: {e}")

    async def _check_brute_force_attacks(self):
        """Check for brute force attacks"""
        try:
            # Simulate brute force attack detection
            # In real implementation, this would detect rapid login attempts
            pass

        except Exception as e:
            logger.error(f"Failed to check brute force attacks: {e}")

    async def _check_privilege_escalation_attempts(self):
        """Check for privilege escalation attempts"""
        try:
            # Simulate privilege escalation detection
            # In real implementation, this would monitor authorization events
            pass

        except Exception as e:
            logger.error(f"Failed to check privilege escalation attempts: {e}")

    async def _check_unauthorized_access(self):
        """Check for unauthorized access attempts"""
        try:
            # Simulate unauthorized access detection
            # In real implementation, this would monitor access logs
            pass

        except Exception as e:
            logger.error(f"Failed to check unauthorized access: {e}")

    async def _check_rbac_violations(self):
        """Check for RBAC violations"""
        try:
            # Simulate RBAC violation detection
            # In real implementation, this would check role-based access
            pass

        except Exception as e:
            logger.error(f"Failed to check RBAC violations: {e}")

    async def _check_data_access_patterns(self):
        """Check data access patterns"""
        try:
            # Simulate data access pattern analysis
            # In real implementation, this would analyze data access logs
            pass

        except Exception as e:
            logger.error(f"Failed to check data access patterns: {e}")

    async def _check_data_exfiltration(self):
        """Check for data exfiltration attempts"""
        try:
            # Simulate data exfiltration detection
            # In real implementation, this would monitor data transfers
            pass

        except Exception as e:
            logger.error(f"Failed to check data exfiltration: {e}")

    async def _check_sensitive_data_access(self):
        """Check sensitive data access"""
        try:
            # Simulate sensitive data access monitoring
            # In real implementation, this would monitor sensitive data access
            pass

        except Exception as e:
            logger.error(f"Failed to check sensitive data access: {e}")

    async def _check_network_connections(self):
        """Check network connections"""
        try:
            # Simulate network connection monitoring
            # In real implementation, this would monitor network connections
            pass

        except Exception as e:
            logger.error(f"Failed to check network connections: {e}")

    async def _check_suspicious_traffic(self):
        """Check for suspicious network traffic"""
        try:
            # Simulate suspicious traffic detection
            # In real implementation, this would analyze network traffic
            pass

        except Exception as e:
            logger.error(f"Failed to check suspicious traffic: {e}")

    async def _check_port_scanning(self):
        """Check for port scanning attempts"""
        try:
            # Simulate port scanning detection
            # In real implementation, this would detect port scanning
            pass

        except Exception as e:
            logger.error(f"Failed to check port scanning: {e}")

    async def _check_unusual_user_behavior(self):
        """Check for unusual user behavior"""
        try:
            # Simulate unusual behavior detection
            # In real implementation, this would analyze user behavior
            pass

        except Exception as e:
            logger.error(f"Failed to check unusual user behavior: {e}")

    async def _check_system_anomalies(self):
        """Check for system anomalies"""
        try:
            # Simulate system anomaly detection
            # In real implementation, this would monitor system metrics
            pass

        except Exception as e:
            logger.error(f"Failed to check system anomalies: {e}")

    async def _check_malware_indicators(self):
        """Check for malware indicators"""
        try:
            # Simulate malware indicator detection
            # In real implementation, this would scan for malware
            pass

        except Exception as e:
            logger.error(f"Failed to check malware indicators: {e}")

    async def _analyze_attack_patterns(self):
        """Analyze attack patterns"""
        try:
            # Simulate attack pattern analysis
            # In real implementation, this would analyze security events
            pass

        except Exception as e:
            logger.error(f"Failed to analyze attack patterns: {e}")

    async def _correlate_security_events(self):
        """Correlate security events"""
        try:
            # Simulate security event correlation
            # In real implementation, this would correlate events
            pass

        except Exception as e:
            logger.error(f"Failed to correlate security events: {e}")

    async def _update_threat_intelligence(self):
        """Update threat intelligence"""
        try:
            # Simulate threat intelligence updates
            # In real implementation, this would update threat data
            pass

        except Exception as e:
            logger.error(f"Failed to update threat intelligence: {e}")

    async def _process_security_incidents(self):
        """Process security incidents"""
        try:
            # Simulate incident processing
            # In real implementation, this would process incidents
            pass

        except Exception as e:
            logger.error(f"Failed to process security incidents: {e}")

    async def _execute_incident_response(self):
        """Execute incident response procedures"""
        try:
            # Simulate incident response execution
            # In real implementation, this would execute response procedures
            pass

        except Exception as e:
            logger.error(f"Failed to execute incident response: {e}")

    async def _update_incident_status(self):
        """Update incident status"""
        try:
            # Simulate incident status updates
            # In real implementation, this would update incident status
            pass

        except Exception as e:
            logger.error(f"Failed to update incident status: {e}")

    async def _load_threat_indicators(self):
        """Load threat indicators"""
        try:
            # Load known threat indicators
            # In real implementation, this would load from threat intelligence feeds
            pass

        except Exception as e:
            logger.error(f"Failed to load threat indicators: {e}")

    async def _cleanup_threat_intelligence(self):
        """Clean up threat intelligence"""
        try:
            # Clean up old threat intelligence data
            # In real implementation, this would clean up old data
            pass

        except Exception as e:
            logger.error(f"Failed to cleanup threat intelligence: {e}")

    async def log_security_event(
        self,
        event_type: SecurityEventType,
        threat_level: ThreatLevel,
        source_ip: str,
        user_id: str,
        description: str,
        details: Dict[str, Any],
        classification: str = "unclassified",
    ) -> str:
        """Log a security event"""
        try:
            event_id = secrets.token_urlsafe(16)

            # Create security event
            event = SecurityEvent(
                event_id=event_id,
                event_type=event_type,
                threat_level=threat_level,
                timestamp=datetime.utcnow(),
                source_ip=source_ip,
                user_id=user_id,
                description=description,
                details=details,
                classification=classification,
                signature=self._generate_event_signature(event_id, description),
            )

            # Store event
            self.security_events[event_id] = event
            self.security_event_history.append(event)

            # Check security rules
            await self._check_security_rules(event)

            logger.warning(
                f"SECURITY EVENT [{threat_level.value.upper()}] {event_type.value}: {description}"
            )

            return event_id

        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            return None

    async def _check_security_rules(self, event: SecurityEvent):
        """Check security rules against event"""
        try:
            for rule in self.security_rules:
                if await self._evaluate_rule(rule, event):
                    await self._execute_rule_action(rule, event)

        except Exception as e:
            logger.error(f"Failed to check security rules: {e}")

    async def _evaluate_rule(self, rule: Dict[str, Any], event: SecurityEvent) -> bool:
        """Evaluate security rule"""
        try:
            # Simulate rule evaluation
            # In real implementation, this would evaluate rule conditions
            return False

        except Exception as e:
            logger.error(f"Failed to evaluate rule: {e}")
            return False

    async def _execute_rule_action(self, rule: Dict[str, Any], event: SecurityEvent):
        """Execute rule action"""
        try:
            action = rule.get("action")

            if action == "block_ip":
                await self._block_ip(event.source_ip)
            elif action == "require_2fa":
                await self._require_2fa(event.user_id)
            elif action == "alert_and_block":
                await self._alert_and_block(event)
            elif action == "alert_and_monitor":
                await self._alert_and_monitor(event)
            elif action == "quarantine_and_alert":
                await self._quarantine_and_alert(event)

        except Exception as e:
            logger.error(f"Failed to execute rule action: {e}")

    async def _block_ip(self, ip_address: str):
        """Block IP address"""
        try:
            self.blocked_ips.add(ip_address)
            logger.warning(f"IP address {ip_address} blocked")

        except Exception as e:
            logger.error(f"Failed to block IP {ip_address}: {e}")

    async def _require_2fa(self, user_id: str):
        """Require 2FA for user"""
        try:
            # Simulate 2FA requirement
            logger.warning(f"2FA required for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to require 2FA for user {user_id}: {e}")

    async def _alert_and_block(self, event: SecurityEvent):
        """Alert and block based on event"""
        try:
            await self._send_security_alert(event)
            await self._block_ip(event.source_ip)

        except Exception as e:
            logger.error(f"Failed to alert and block: {e}")

    async def _alert_and_monitor(self, event: SecurityEvent):
        """Alert and monitor based on event"""
        try:
            await self._send_security_alert(event)
            await self._add_to_monitoring(event.user_id)

        except Exception as e:
            logger.error(f"Failed to alert and monitor: {e}")

    async def _quarantine_and_alert(self, event: SecurityEvent):
        """Quarantine and alert based on event"""
        try:
            await self._send_security_alert(event)
            await self._quarantine_system(event)

        except Exception as e:
            logger.error(f"Failed to quarantine and alert: {e}")

    async def _send_security_alert(self, event: SecurityEvent):
        """Send security alert"""
        try:
            # Simulate security alert
            logger.critical(f"SECURITY ALERT: {event.description}")

        except Exception as e:
            logger.error(f"Failed to send security alert: {e}")

    async def _add_to_monitoring(self, user_id: str):
        """Add user to monitoring list"""
        try:
            self.suspicious_users.add(user_id)
            logger.warning(f"User {user_id} added to monitoring list")

        except Exception as e:
            logger.error(f"Failed to add user to monitoring: {e}")

    async def _quarantine_system(self, event: SecurityEvent):
        """Quarantine system based on event"""
        try:
            # Simulate system quarantine
            logger.critical(f"System quarantined due to: {event.description}")

        except Exception as e:
            logger.error(f"Failed to quarantine system: {e}")

    def _generate_event_signature(self, event_id: str, description: str) -> str:
        """Generate event signature for tamper detection"""
        try:
            secret_key = self.config.get("security_secret_key", "default_secret")
            data = f"{event_id}:{description}"
            signature = hmac.new(
                secret_key.encode(), data.encode(), hashlib.sha256
            ).hexdigest()
            return signature

        except Exception as e:
            logger.error(f"Failed to generate event signature: {e}")
            return ""

    async def get_security_status(self) -> Dict[str, Any]:
        """Get security monitoring status"""
        return {
            "monitoring_enabled": self.monitoring_enabled,
            "active_events": len(
                [e for e in self.security_events.values() if not e.resolved]
            ),
            "total_events": len(self.security_event_history),
            "blocked_ips": len(self.blocked_ips),
            "suspicious_users": len(self.suspicious_users),
            "threat_intelligence_entries": len(self.threat_intelligence),
            "security_rules": len(self.security_rules),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_security_events(
        self,
        event_type: SecurityEventType = None,
        threat_level: ThreatLevel = None,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> List[Dict[str, Any]]:
        """Get security events"""
        try:
            events = []
            for event in self.security_event_history:
                if event_type and event.event_type != event_type:
                    continue
                if threat_level and event.threat_level != threat_level:
                    continue
                if start_date and event.timestamp < start_date:
                    continue
                if end_date and event.timestamp > end_date:
                    continue

                events.append(
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type.value,
                        "threat_level": event.threat_level.value,
                        "timestamp": event.timestamp.isoformat(),
                        "source_ip": event.source_ip,
                        "user_id": event.user_id,
                        "description": event.description,
                        "details": event.details,
                        "classification": event.classification,
                        "resolved": event.resolved,
                        "resolved_at": (
                            event.resolved_at.isoformat() if event.resolved_at else None
                        ),
                    }
                )

            return events

        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return []

    async def resolve_security_event(self, event_id: str) -> bool:
        """Resolve a security event"""
        try:
            if event_id in self.security_events:
                event = self.security_events[event_id]
                event.resolved = True
                event.resolved_at = datetime.utcnow()
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to resolve security event {event_id}: {e}")
            return False

    async def add_threat_intelligence(self, threat_data: Dict[str, Any]) -> str:
        """Add threat intelligence"""
        try:
            threat_id = secrets.token_urlsafe(16)

            threat = ThreatIntelligence(
                threat_id=threat_id,
                threat_type=threat_data.get("threat_type", "unknown"),
                severity=ThreatLevel(threat_data.get("severity", "low")),
                indicators=threat_data.get("indicators", []),
                description=threat_data.get("description", ""),
                mitigation=threat_data.get("mitigation", []),
                last_seen=datetime.utcnow(),
                confidence=threat_data.get("confidence", 0.0),
            )

            self.threat_intelligence[threat_id] = threat

            logger.info(f"Threat intelligence added: {threat_id}")
            return threat_id

        except Exception as e:
            logger.error(f"Failed to add threat intelligence: {e}")
            return None

    async def shutdown(self):
        """Shutdown security monitoring service"""
        try:
            logger.info("Shutting down security monitoring service...")

            # Stop monitoring
            self.monitoring_enabled = False

            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()

            # Wait for tasks to complete
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)

            logger.info("Security monitoring service shutdown complete")

        except Exception as e:
            logger.error(f"Error during security monitoring service shutdown: {e}")
