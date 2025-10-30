"""
Comprehensive Session Management for AMAS
Implements session management with timeout, security controls, and enterprise features
"""

import asyncio
import hashlib
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    INVALID = "invalid"


class SessionType(Enum):
    """Session type enumeration"""
    WEB = "web"
    API = "api"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    CLI = "cli"


class SecurityEvent(Enum):
    """Security event types"""
    LOGIN = "login"
    LOGOUT = "logout"
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    SESSION_TERMINATED = "session_terminated"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MULTIPLE_LOGINS = "multiple_logins"
    IP_CHANGE = "ip_change"
    DEVICE_CHANGE = "device_change"


class Session:
    """Session model for comprehensive session management"""

    def __init__(self, session_id: str, user_id: str, session_type: str, **kwargs):
        self.session_id = session_id
        self.user_id = user_id
        self.session_type = session_type
        self.status = SessionStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.expires_at = kwargs.get("expires_at", datetime.utcnow() + timedelta(hours=8))
        self.ip_address = kwargs.get("ip_address", "")
        self.user_agent = kwargs.get("user_agent", "")
        self.device_id = kwargs.get("device_id")
        self.device_fingerprint = kwargs.get("device_fingerprint", "")
        self.location = kwargs.get("location", {})
        self.security_level = kwargs.get("security_level", "standard")
        self.mfa_verified = kwargs.get("mfa_verified", False)
        self.risk_score = kwargs.get("risk_score", 0)
        self.attributes = kwargs.get("attributes", {})
        self.metadata = kwargs.get("metadata", {})

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "session_type": self.session_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device_id": self.device_id,
            "device_fingerprint": self.device_fingerprint,
            "location": self.location,
            "security_level": self.security_level,
            "mfa_verified": self.mfa_verified,
            "risk_score": self.risk_score,
            "attributes": self.attributes,
            "metadata": self.metadata,
        }

    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at

    def is_active(self) -> bool:
        """Check if session is active"""
        return self.status == SessionStatus.ACTIVE and not self.is_expired()

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()

    def extend_session(self, additional_hours: int = 1):
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(hours=additional_hours)

    def terminate(self, reason: str = "user_logout"):
        """Terminate session"""
        self.status = SessionStatus.TERMINATED
        self.attributes["termination_reason"] = reason
        self.attributes["terminated_at"] = datetime.utcnow().isoformat()


class SessionManager:
    """Comprehensive session management system"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sessions = {}  # In production, use database
        self.session_history = []
        self.security_events = []
        self.max_sessions_per_user = config.get("max_sessions_per_user", 5)
        self.session_timeout = config.get("session_timeout", 8 * 3600)  # 8 hours
        self.idle_timeout = config.get("idle_timeout", 2 * 3600)  # 2 hours
        self.absolute_timeout = config.get("absolute_timeout", 24 * 3600)  # 24 hours
        self.risk_threshold = config.get("risk_threshold", 70)
        self.suspicious_activity_threshold = config.get("suspicious_activity_threshold", 3)

    async def create_session(
        self,
        user_id: str,
        session_type: str,
        ip_address: str,
        user_agent: str,
        device_id: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None,
        security_level: str = "standard",
        mfa_verified: bool = False,
        **kwargs
    ) -> Session:
        """Create a new session"""
        try:
            # Check for existing sessions
            await self._cleanup_expired_sessions()
            await self._enforce_session_limits(user_id)

            # Generate session ID
            session_id = await self._generate_session_id()

            # Calculate risk score
            risk_score = await self._calculate_risk_score(
                user_id, ip_address, user_agent, device_id, location
            )

            # Determine session expiration
            expires_at = await self._calculate_session_expiration(
                security_level, mfa_verified, risk_score
            )

            # Create session
            session = Session(
                session_id=session_id,
                user_id=user_id,
                session_type=session_type,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent,
                device_id=device_id,
                device_fingerprint=device_fingerprint,
                location=location or {},
                security_level=security_level,
                mfa_verified=mfa_verified,
                risk_score=risk_score,
                **kwargs
            )

            # Store session
            self.sessions[session_id] = session

            # Log security event
            await self._log_security_event(
                SecurityEvent.SESSION_CREATED,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                details={"session_type": session_type, "risk_score": risk_score}
            )

            logger.info(f"Created session {session_id} for user {user_id}")
            return session

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise

    async def validate_session(self, session_id: str, ip_address: str = None) -> Optional[Session]:
        """Validate and return session if valid"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return None

            # Check if session is expired
            if session.is_expired():
                await self._terminate_session(session_id, "expired")
                return None

            # Check if session is active
            if not session.is_active():
                return None

            # Validate IP address if provided
            if ip_address and session.ip_address != ip_address:
                await self._handle_ip_change(session, ip_address)
                # Don't terminate session immediately, but log the event

            # Update last activity
            session.update_activity()

            # Check for suspicious activity
            await self._check_suspicious_activity(session)

            return session

        except Exception as e:
            logger.error(f"Failed to validate session: {e}")
            return None

    async def terminate_session(self, session_id: str, reason: str = "user_logout") -> bool:
        """Terminate a session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return False

            await self._terminate_session(session_id, reason)
            return True

        except Exception as e:
            logger.error(f"Failed to terminate session: {e}")
            return False

    async def terminate_user_sessions(self, user_id: str, reason: str = "user_logout") -> int:
        """Terminate all sessions for a user"""
        try:
            terminated_count = 0
            sessions_to_terminate = [
                session_id for session_id, session in self.sessions.items()
                if session.user_id == user_id and session.is_active()
            ]

            for session_id in sessions_to_terminate:
                await self._terminate_session(session_id, reason)
                terminated_count += 1

            logger.info(f"Terminated {terminated_count} sessions for user {user_id}")
            return terminated_count

        except Exception as e:
            logger.error(f"Failed to terminate user sessions: {e}")
            return 0

    async def extend_session(self, session_id: str, additional_hours: int = 1) -> bool:
        """Extend session expiration"""
        try:
            session = self.sessions.get(session_id)
            if not session or not session.is_active():
                return False

            session.extend_session(additional_hours)

            # Log security event
            await self._log_security_event(
                SecurityEvent.SESSION_CREATED,  # Reuse event type for extension
                user_id=session.user_id,
                session_id=session_id,
                details={"action": "extended", "additional_hours": additional_hours}
            )

            logger.info(f"Extended session {session_id} by {additional_hours} hours")
            return True

        except Exception as e:
            logger.error(f"Failed to extend session: {e}")
            return False

    async def get_user_sessions(self, user_id: str) -> List[Session]:
        """Get all active sessions for a user"""
        try:
            await self._cleanup_expired_sessions()
            return [
                session for session in self.sessions.values()
                if session.user_id == user_id and session.is_active()
            ]
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []

    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            await self._cleanup_expired_sessions()
            
            total_sessions = len(self.sessions)
            active_sessions = len([s for s in self.sessions.values() if s.is_active()])
            expired_sessions = len([s for s in self.sessions.values() if s.is_expired()])
            
            # Group by session type
            session_types = {}
            for session in self.sessions.values():
                session_type = session.session_type
                if session_type not in session_types:
                    session_types[session_type] = 0
                session_types[session_type] += 1

            # Group by security level
            security_levels = {}
            for session in self.sessions.values():
                security_level = session.security_level
                if security_level not in security_levels:
                    security_levels[security_level] = 0
                security_levels[security_level] += 1

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "expired_sessions": expired_sessions,
                "session_types": session_types,
                "security_levels": security_levels,
                "last_cleanup": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get session statistics: {e}")
            return {}

    async def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        return f"sess_{secrets.token_urlsafe(32)}"

    async def _calculate_risk_score(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str,
        device_id: Optional[str],
        location: Optional[Dict[str, Any]]
    ) -> int:
        """Calculate risk score for session"""
        risk_score = 0

        # Check for multiple sessions from different IPs
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id and s.is_active()]
        unique_ips = set(s.ip_address for s in user_sessions)
        if len(unique_ips) > 1:
            risk_score += 30

        # Check for suspicious user agent
        if "bot" in user_agent.lower() or "crawler" in user_agent.lower():
            risk_score += 40

        # Check for location anomalies (simplified)
        if location and location.get("country") == "unknown":
            risk_score += 20

        # Check for device changes
        if device_id:
            user_devices = set(s.device_id for s in user_sessions if s.device_id)
            if len(user_devices) > 2:
                risk_score += 25

        return min(risk_score, 100)

    async def _calculate_session_expiration(
        self, security_level: str, mfa_verified: bool, risk_score: int
    ) -> datetime:
        """Calculate session expiration based on security factors"""
        base_hours = self.session_timeout / 3600

        # Adjust based on security level
        if security_level == "high":
            base_hours = min(base_hours, 4)  # Max 4 hours for high security
        elif security_level == "low":
            base_hours = min(base_hours * 1.5, 12)  # Up to 12 hours for low security

        # Adjust based on MFA verification
        if mfa_verified:
            base_hours = min(base_hours * 1.2, 8)  # 20% longer with MFA

        # Adjust based on risk score
        if risk_score > self.risk_threshold:
            base_hours = min(base_hours * 0.5, 2)  # Reduce to max 2 hours for high risk

        return datetime.utcnow() + timedelta(hours=base_hours)

    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            expired_sessions = []
            for session_id, session in self.sessions.items():
                if session.is_expired():
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                await self._terminate_session(session_id, "expired")

            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")

    async def _enforce_session_limits(self, user_id: str):
        """Enforce maximum sessions per user"""
        try:
            user_sessions = [s for s in self.sessions.values() if s.user_id == user_id and s.is_active()]
            
            if len(user_sessions) >= self.max_sessions_per_user:
                # Terminate oldest session
                oldest_session = min(user_sessions, key=lambda s: s.created_at)
                await self._terminate_session(oldest_session.session_id, "session_limit_exceeded")

        except Exception as e:
            logger.error(f"Failed to enforce session limits: {e}")

    async def _terminate_session(self, session_id: str, reason: str):
        """Terminate a session and log the event"""
        try:
            session = self.sessions.get(session_id)
            if session:
                session.terminate(reason)
                
                # Move to history
                self.session_history.append(session.to_dict())
                
                # Log security event
                await self._log_security_event(
                    SecurityEvent.SESSION_TERMINATED,
                    user_id=session.user_id,
                    session_id=session_id,
                    details={"reason": reason}
                )

                # Remove from active sessions
                del self.sessions[session_id]

        except Exception as e:
            logger.error(f"Failed to terminate session: {e}")

    async def _handle_ip_change(self, session: Session, new_ip: str):
        """Handle IP address change during session"""
        try:
            old_ip = session.ip_address
            session.ip_address = new_ip

            # Log security event
            await self._log_security_event(
                SecurityEvent.IP_CHANGE,
                user_id=session.user_id,
                session_id=session.session_id,
                ip_address=new_ip,
                details={"old_ip": old_ip, "new_ip": new_ip}
            )

            # Increase risk score
            session.risk_score = min(session.risk_score + 20, 100)

            logger.warning(f"IP change detected for session {session.session_id}: {old_ip} -> {new_ip}")

        except Exception as e:
            logger.error(f"Failed to handle IP change: {e}")

    async def _check_suspicious_activity(self, session: Session):
        """Check for suspicious activity patterns"""
        try:
            # Check for rapid session creation
            recent_sessions = [
                s for s in self.session_history
                if s["user_id"] == session.user_id and
                datetime.fromisoformat(s["created_at"]) > datetime.utcnow() - timedelta(minutes=10)
            ]

            if len(recent_sessions) > self.suspicious_activity_threshold:
                await self._log_security_event(
                    SecurityEvent.SUSPICIOUS_ACTIVITY,
                    user_id=session.user_id,
                    session_id=session.session_id,
                    details={"activity": "rapid_session_creation", "count": len(recent_sessions)}
                )

                # Increase risk score
                session.risk_score = min(session.risk_score + 30, 100)

        except Exception as e:
            logger.error(f"Failed to check suspicious activity: {e}")

    async def _log_security_event(
        self,
        event_type: SecurityEvent,
        user_id: str = None,
        session_id: str = None,
        ip_address: str = None,
        details: Dict[str, Any] = None
    ):
        """Log security event"""
        try:
            event = {
                "event_type": event_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "session_id": session_id,
                "ip_address": ip_address,
                "details": details or {},
            }

            self.security_events.append(event)

            # In production, also send to security monitoring system
            logger.info(f"Security event: {event_type.value} for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    async def get_security_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get security events with filters"""
        try:
            filtered_events = []

            for event in self.security_events:
                if user_id and event.get("user_id") != user_id:
                    continue
                if event_type and event.get("event_type") != event_type:
                    continue

                filtered_events.append(event)

            # Sort by timestamp (newest first)
            filtered_events.sort(key=lambda x: x["timestamp"], reverse=True)

            return filtered_events[:limit]

        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return []

    async def get_session_analytics(self) -> Dict[str, Any]:
        """Get session analytics and insights"""
        try:
            await self._cleanup_expired_sessions()

            # Calculate metrics
            total_sessions = len(self.sessions)
            active_sessions = len([s for s in self.sessions.values() if s.is_active()])
            
            # Average session duration
            completed_sessions = [
                s for s in self.session_history
                if s["status"] == SessionStatus.TERMINATED.value
            ]
            
            avg_duration = 0
            if completed_sessions:
                durations = []
                for session in completed_sessions:
                    created = datetime.fromisoformat(session["created_at"])
                    terminated = datetime.fromisoformat(session.get("terminated_at", session["created_at"]))
                    duration = (terminated - created).total_seconds() / 3600  # hours
                    durations.append(duration)
                avg_duration = sum(durations) / len(durations)

            # Risk score distribution
            risk_scores = [s.risk_score for s in self.sessions.values() if s.is_active()]
            high_risk_sessions = len([score for score in risk_scores if score > self.risk_threshold])

            # Security events in last 24 hours
            recent_events = [
                e for e in self.security_events
                if datetime.fromisoformat(e["timestamp"]) > datetime.utcnow() - timedelta(hours=24)
            ]

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "average_session_duration_hours": round(avg_duration, 2),
                "high_risk_sessions": high_risk_sessions,
                "security_events_24h": len(recent_events),
                "risk_score_average": round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else 0,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get session analytics: {e}")
            return {}
