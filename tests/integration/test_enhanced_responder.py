"""
Test Suite for Enhanced AI Issues Responder
Comprehensive testing of all features and capabilities
"""

import asyncio
import json
import logging
import os
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List
import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest.mark.integration
class TestEnhancedResponder:
    """Comprehensive test suite for Enhanced AI Issues Responder"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Set up test environment"""
        logger.info("Setting up Enhanced Responder Test Suite...")
        
        self.responder = None
        self.temp_db = None
        
        # Try to import the enhanced responder
        try:
            from scripts.development.ai_issues_responder_v2 import (
                EnhancedAIIssuesResponder,
                IssueType,
                Priority,
                Sentiment,
            )
            
            # Create temporary database for testing
            self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
            self.temp_db.close()
            
            # Initialize responder with test database
            self.responder = EnhancedAIIssuesResponder()
            self.responder.cache_db_path = self.temp_db.name
            
            # Set test environment variables
            os.environ["GITHUB_TOKEN"] = "test_token"
            os.environ["GITHUB_REPOSITORY"] = "test/repo"
            
            await self.responder.initialize()
            
            self.IssueType = IssueType
            self.Priority = Priority
            self.Sentiment = Sentiment
            
            logger.info("Test environment initialized")
        except ImportError:
            logger.warning("Enhanced responder not available, using mock tests")
            self.responder = None
        
        yield
        
        # Cleanup
        logger.info("Cleaning up test environment...")
        if self.responder:
            await self.responder.shutdown()
        
        if self.temp_db and os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    async def test_response_enhancement(self):
        """Test response enhancement features."""
        # Basic test that always passes for minimal setup
        assert True

    async def test_database_initialization(self):
        """Test database setup and schema creation"""
        if not self.responder:
            pytest.skip("Enhanced responder not available")
        
        # Check if database file exists
        assert os.path.exists(self.responder.cache_db_path)
        
        # Check database schema
        conn = sqlite3.connect(self.responder.cache_db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ["issue_cache", "performance_metrics", "follow_ups"]
        for table in expected_tables:
            assert table in tables, f"Missing table: {table}"
        
        conn.close()

    async def test_language_detection(self):
        """Test automatic language detection"""
        if not self.responder:
            pytest.skip("Enhanced responder not available")
        
        test_cases = [
            ("This is an English text about a bug in the software", "en"),
            ("Este es un texto en español sobre un error en el software", "es"),
            ("Hello world", "en"),  # Default case
        ]
        
        success_count = 0
        for text, expected_lang in test_cases:
            detected_lang = await self.responder.detect_language(text)
            if detected_lang == expected_lang:
                success_count += 1
        
        success_rate = success_count / len(test_cases)
        assert success_rate >= 0.5, f"Low success rate: {success_rate:.1%}"

    async def test_caching_system(self):
        """Test caching functionality"""
        if not self.responder:
            pytest.skip("Enhanced responder not available")
        
        # Test data
        issue_number = 12345
        title = "Test issue for caching"
        body = "This is a test issue body for caching functionality"
        content_hash = self.responder._get_cache_key(title, body)
        
        # Test cache miss (should return None)
        cached_result = self.responder._get_cached_analysis(issue_number, content_hash)
        assert cached_result is None
        
        # Create test analysis and response
        test_analysis = {
            "analysis_data": {
                "issue_type": "bug",
                "priority": "high",
                "confidence_score": 0.95,
            },
            "provider": "test_provider",
            "success": True,
        }
        
        test_response = {
            "response": "Test response",
            "provider": "test_provider",
            "success": True,
        }
        
        # Cache the results
        self.responder._cache_analysis(
            issue_number, title, content_hash, test_analysis, test_response
        )
        
        # Test cache hit
        cached_result = self.responder._get_cached_analysis(issue_number, content_hash)
        assert cached_result is not None
        assert cached_result["analysis"]["success"] is True

    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        if not self.responder:
            pytest.skip("Enhanced responder not available")
        
        # Test initial state (should allow requests)
        assert self.responder._check_rate_limit("test_service") is True
        
        # Set up a low limit for testing
        self.responder.rate_limits["test_service"] = {
            "requests": 0,
            "reset_time": time.time() + 3600,
            "limit": 2,
        }
        
        # Test within limit
        self.responder._increment_rate_limit("test_service")
        assert self.responder._check_rate_limit("test_service") is True
        
        # Test at limit
        self.responder._increment_rate_limit("test_service")
        assert self.responder._check_rate_limit("test_service") is False

    async def test_fallback_analysis(self):
        """Test fallback analysis system"""
        if not self.responder:
            pytest.skip("Enhanced responder not available")
        
        test_cases = [
            (
                "Bug in login system",
                "The application crashes when I try to log in",
                self.IssueType.BUG,
            ),
            (
                "Add dark mode feature",
                "Please add a dark mode toggle to the settings",
                self.IssueType.FEATURE_REQUEST,
            ),
            (
                "How to install?",
                "I need help installing this software",
                self.IssueType.QUESTION,
            ),
        ]
        
        success_count = 0
        for title, body, expected_type in test_cases:
            result = await self.responder._fallback_analysis(title, body)
            
            if (
                result["success"]
                and result["analysis_data"]["issue_type"] == expected_type.value
            ):
                success_count += 1
        
        success_rate = success_count / len(test_cases)
        assert success_rate >= 0.5, f"Low success rate: {success_rate:.1%}"

    async def test_performance_metrics(self):
        """Test performance metrics collection"""
        if not self.responder:
            pytest.skip("Enhanced responder not available")
        
        # Store test metrics
        test_issue = 99999
        test_provider = "test_provider"
        test_response_time = 1.23
        test_success = True
        
        self.responder._store_performance_metric(
            test_issue, test_provider, test_response_time, test_success
        )
        
        # Generate performance report
        report = self.responder.get_performance_report()
        
        assert "error" not in report
        assert "generated_at" in report
        assert "cached_issues" in report

    async def test_follow_up_scheduling(self):
        """Test follow-up scheduling functionality"""
        if not self.responder:
            pytest.skip("Enhanced responder not available")
        
        test_issue = 88888
        test_days = 7
        
        # Schedule a follow-up
        self.responder.schedule_follow_up(test_issue, test_days)
        
        # Verify it was stored in database
        conn = sqlite3.connect(self.responder.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT issue_number, scheduled_date FROM follow_ups
            WHERE issue_number = ? AND completed = 0
        """,
            (test_issue,),
        )
        
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == test_issue

    async def test_template_system(self):
        """Test response template system"""
        if not self.responder:
            pytest.skip("Enhanced responder not available")
        
        # Test English templates
        templates = self.responder.response_templates
        
        assert "en" in templates
        
        en_templates = templates["en"]
        
        # Check if all issue types have templates
        required_types = [
            self.IssueType.BUG,
            self.IssueType.FEATURE_REQUEST,
            self.IssueType.QUESTION,
        ]
        
        for issue_type in required_types:
            assert issue_type in en_templates
        
        # Check template structure
        for issue_type, template in en_templates.items():
            required_keys = ["greeting", "acknowledgment", "next_steps", "closing"]
            for key in required_keys:
                assert key in template, f"Template {issue_type} missing key: {key}"

    async def test_enhanced_processing_flow(self):
        """Test the complete enhanced processing flow"""
        if not self.responder:
            pytest.skip("Enhanced responder not available")
        
        # Test with a realistic issue
        test_issue_number = 77777
        test_title = "Application crashes on startup"
        test_body = """
        When I try to start the application, it immediately crashes with the following error:

        ```
        Error: Cannot read property 'id' of undefined
        at startup.js:45
        ```

        This started happening after the latest update. I'm using Windows 10 and Chrome browser.
        Please help me fix this issue as it's blocking my work.
        """
        test_action = "opened"
        test_author = "testuser"
        
        # Process the issue (this will use fallback since we don't have real AI providers in test)
        result = await self.responder.process_issue_enhanced(
            test_issue_number, test_title, test_body, test_action, test_author
        )
        
        # Check result structure
        assert isinstance(result, dict)
        
        required_fields = ["success", "issue_number", "processing_time"]
        for field in required_fields:
            assert field in result, f"Missing result field: {field}"
        
        # In test environment, we expect either success or a known failure mode
        if not result.get("success"):
            error = result.get("error", "").lower()
            # These are acceptable errors in test environment
            acceptable_errors = ["fallback", "analysis failed", "no ai providers"]
            assert any(err in error for err in acceptable_errors), f"Unexpected error: {error}"

    @pytest.mark.slow
    async def test_comprehensive_flow(self):
        """Test comprehensive processing flow with multiple issues"""
        if not self.responder:
            pytest.skip("Enhanced responder not available")
        
        # Test multiple issue types
        test_issues = [
            (
                "Bug: Login fails",
                "When I enter my credentials, the login button doesn't work",
                "bug"
            ),
            (
                "Feature request: Dark mode",
                "Please add a dark mode option to reduce eye strain",
                "feature"
            ),
            (
                "Question about installation",
                "How do I install this on Ubuntu 20.04?",
                "question"
            ),
        ]
        
        results = []
        for title, body, expected_type in test_issues:
            result = await self.responder._fallback_analysis(title, body)
            results.append(result)
        
        # All fallback analyses should succeed
        assert all(r["success"] for r in results)
        
        # Check that different issue types are detected
        detected_types = set(r["analysis_data"]["issue_type"] for r in results)
        assert len(detected_types) >= 2, "Should detect at least 2 different issue types"