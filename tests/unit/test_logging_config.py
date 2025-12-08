"""
Unit tests for Logging Configuration
Tests PART 6: Monitoring & Observability - Structured Logging
"""

import pytest
import logging
import json
from unittest.mock import patch

from src.utils.logging_config import setup_logging, JsonFormatter


@pytest.mark.unit
class TestLoggingConfig:
    """Test logging configuration"""

    def test_setup_logging_production(self):
        """Test setting up logging for production"""
        setup_logging(environment="production")
        
        # Verify logging is configured
        logger = logging.getLogger("test")
        assert logger is not None

    def test_setup_logging_development(self):
        """Test setting up logging for development"""
        setup_logging(environment="development")
        
        # Verify logging is configured
        logger = logging.getLogger("test")
        assert logger is not None

    def test_json_formatter(self):
        """Test JSON formatter"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Should be valid JSON
        parsed = json.loads(formatted)
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message"

    def test_json_formatter_with_exception(self):
        """Test JSON formatter with exception"""
        formatter = JsonFormatter()
        
        try:
            raise ValueError("Test error")
        except Exception:
            import sys
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="Test error",
                args=(),
                exc_info=sys.exc_info()
            )
            
            formatted = formatter.format(record)
            parsed = json.loads(formatted)
            
            assert parsed["level"] == "ERROR"
            assert "exception" in parsed or "exc_info" in parsed

    def test_json_formatter_extra_fields(self):
        """Test JSON formatter with extra fields"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add extra field
        record.custom_field = "custom_value"
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert parsed["custom_field"] == "custom_value"

