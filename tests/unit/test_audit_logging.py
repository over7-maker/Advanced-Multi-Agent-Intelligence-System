"""
Unit tests for audit logging and PII redaction
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.amas.security.audit.audit_logger import (
    AuditLogger,
    AuditEvent,
    AuditEventType,
    AuditStatus,
    PIIRedactor,
)


@pytest.fixture
def audit_logger(tmp_path):
    """Create audit logger instance for testing"""
    log_file = tmp_path / "audit.jsonl"
    return AuditLogger(
        log_file=str(log_file),
        buffer_size=10,
        flush_interval=1,
        enable_redaction=True
    )


@pytest.fixture
def pii_redactor():
    """Create PII redactor instance"""
    return PIIRedactor()


class TestPIIRedactor:
    """Test PII redaction functionality"""
    
    def test_redact_email(self, pii_redactor):
        """Test email redaction"""
        text = "Contact us at user@example.com for support"
        redacted, found = pii_redactor.redact_text(text)
        
        assert found is True
        assert "user@example.com" not in redacted
        assert "[EMAIL_REDACTED]" in redacted
    
    def test_redact_ssn(self, pii_redactor):
        """Test SSN redaction"""
        text = "SSN: 123-45-6789"
        redacted, found = pii_redactor.redact_text(text)
        
        assert found is True
        assert "123-45-6789" not in redacted
        assert "[SSN_REDACTED]" in redacted
    
    def test_redact_api_key(self, pii_redactor):
        """Test API key redaction"""
        text = "API key: sk-1234567890abcdef1234567890abcdef1234567890abcdef"
        redacted, found = pii_redactor.redact_text(text)
        
        assert found is True
        assert "sk-" not in redacted or "[API_KEY_REDACTED]" in redacted
    
    def test_redact_dict(self, pii_redactor):
        """Test redaction in dictionary"""
        data = {
            "user_id": "123",
            "email": "user@example.com",
            "password": "secret123",
            "api_key": "sk-abcdef123456"
        }
        
        redacted, found = pii_redactor.redact_dict(data)
        
        assert found is True
        assert redacted["password"] == "[REDACTED]"
        assert "[EMAIL_REDACTED]" in redacted["email"] or redacted["email"] == "[REDACTED]"
    
    def test_no_pii_no_redaction(self, pii_redactor):
        """Test that non-PII text is not redacted"""
        text = "This is a normal message without sensitive data"
        redacted, found = pii_redactor.redact_text(text)
        
        assert found is False
        assert redacted == text


class TestAuditLogger:
    """Test audit logger functionality"""
    
    @pytest.mark.asyncio
    async def test_log_event(self, audit_logger):
        """Test logging an audit event"""
        event = AuditEvent(
            event_id="test-event-123",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=AuditEventType.AUTHENTICATION,
            status=AuditStatus.SUCCESS,
            user_id="test-user",
            action="login",
            details={"method": "jwt"}
        )
        
        await audit_logger.log_event(event)
        
        # Flush buffer to ensure event is written
        await audit_logger.flush_buffer()
        
        # Check that log file exists and contains event
        log_file = Path(audit_logger.log_file)
        assert log_file.exists()
        
        # Read and verify log entry
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            log_entry = json.loads(lines[-1])
            assert log_entry["event_id"] == "test-event-123"
            assert log_entry["user_id"] == "test-user"
    
    @pytest.mark.asyncio
    async def test_log_authentication(self, audit_logger):
        """Test logging authentication event"""
        await audit_logger.log_authentication(
            user_id="test-user",
            status=AuditStatus.SUCCESS,
            method="jwt",
            ip_address="192.168.1.1"
        )
        
        await audit_logger.flush_buffer()
        
        # Verify event was logged
        log_file = Path(audit_logger.log_file)
        assert log_file.exists()
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            log_entry = json.loads(lines[-1])
            assert log_entry["event_type"] == "authentication"
            assert log_entry["user_id"] == "test-user"
            assert log_entry["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_log_agent_execution(self, audit_logger):
        """Test logging agent execution event"""
        await audit_logger.log_agent_execution(
            user_id="test-user",
            agent_id="agent-123",
            action="execute",
            status=AuditStatus.SUCCESS,
            duration_ms=150.5,
            tokens_used=1000,
            cost_usd=0.02
        )
        
        await audit_logger.flush_buffer()
        
        # Verify event was logged
        log_file = Path(audit_logger.log_file)
        with open(log_file, 'r') as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1])
            assert log_entry["event_type"] == "agent_execution"
            assert log_entry["agent_id"] == "agent-123"
            assert log_entry["duration_ms"] == 150.5
            assert log_entry["tokens_used"] == 1000
    
    @pytest.mark.asyncio
    async def test_log_security_violation(self, audit_logger):
        """Test logging security violation"""
        await audit_logger.log_security_violation(
            user_id="test-user",
            violation_type="unauthorized_access",
            severity="high",
            description="User attempted unauthorized access",
            ip_address="192.168.1.1"
        )
        
        await audit_logger.flush_buffer()
        
        # Verify event was logged
        log_file = Path(audit_logger.log_file)
        with open(log_file, 'r') as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1])
            assert log_entry["event_type"] == "security_violation"
            assert log_entry["status"] == "blocked"
            assert log_entry["risk_score"] == 1.0  # High severity
            assert "unauthorized_access" in log_entry["details"]["violation_type"]
    
    @pytest.mark.asyncio
    async def test_pii_redaction_in_logs(self, audit_logger):
        """Test that PII is automatically redacted in audit logs"""
        event = AuditEvent(
            event_id="test-event",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=AuditEventType.DATA_ACCESS,
            status=AuditStatus.SUCCESS,
            user_id="test-user",
            details={
                "email": "user@example.com",
                "ssn": "123-45-6789",
                "api_key": "sk-abcdef123456"
            }
        )
        
        await audit_logger.log_event(event)
        await audit_logger.flush_buffer()
        
        # Check that PII was redacted
        log_file = Path(audit_logger.log_file)
        with open(log_file, 'r') as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1])
            details = log_entry["details"]
            
            # PII should be redacted
            assert "user@example.com" not in json.dumps(log_entry)
            assert "123-45-6789" not in json.dumps(log_entry)
            assert log_entry["pii_detected"] is True
    
    @pytest.mark.asyncio
    async def test_buffer_flush(self, audit_logger):
        """Test that buffer flushes when full"""
        # Add multiple events to fill buffer
        for i in range(15):  # More than buffer_size of 10
            event = AuditEvent(
                event_id=f"event-{i}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=AuditEventType.SYSTEM_EVENT,
                status=AuditStatus.SUCCESS,
                user_id="test-user"
            )
            await audit_logger.log_event(event)
        
        # Wait for flush
        await asyncio.sleep(2)
        
        # Verify events were written
        log_file = Path(audit_logger.log_file)
        assert log_file.exists()
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # Should have at least buffer_size events written
            assert len(lines) >= 10
    
    @pytest.mark.asyncio
    async def test_audit_context_manager(self, audit_logger):
        """Test audit context manager"""
        user_id = "test-user"
        
        async with audit_logger.audit_context(
            user_id=user_id,
            operation="test_operation",
            resource_type="test_resource",
            resource_id="test-id"
        ):
            # Simulate operation
            await asyncio.sleep(0.1)
        
        await audit_logger.flush_buffer()
        
        # Verify event was logged
        log_file = Path(audit_logger.log_file)
        with open(log_file, 'r') as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1])
            assert log_entry["user_id"] == user_id
            assert log_entry["action"] == "test_operation"
            assert log_entry["duration_ms"] is not None
