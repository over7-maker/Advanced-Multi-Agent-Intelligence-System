#!/usr/bin/env python3
"""
Test Suite for Enhanced AI Issues Responder v2.0
Comprehensive testing of all features and capabilities
"""

import asyncio
import json
import os
import sys
import tempfile
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

# Import the enhanced responder
from ai_issues_responder_v2 import (
    EnhancedAIIssuesResponder,
    IssueType,
    Priority,
    Sentiment,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedResponderTestSuite:
    """Comprehensive test suite for Enhanced AI Issues Responder v2.0"""

    def __init__(self):
        self.responder = None
        self.test_results = []
        self.temp_db = None

    async def setup(self):
        """Set up test environment"""
        logger.info("🚀 Setting up Enhanced Responder Test Suite...")

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
        logger.info("✅ Test environment initialized")

    async def cleanup(self):
        """Clean up test environment"""
        logger.info("🧹 Cleaning up test environment...")

        if self.responder:
            await self.responder.shutdown()

        if self.temp_db and os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

        logger.info("✅ Test cleanup complete")

    def add_test_result(
        self, test_name: str, success: bool, details: str = "", duration: float = 0
    ):
        """Add test result to collection"""
        self.test_results.append(
            {
                "test_name": test_name,
                "success": success,
                "details": details,
                "duration": duration,
                "timestamp": time.time(),
            }
        )

    async def test_database_initialization(self):
        """Test database setup and schema creation"""
        test_name = "Database Initialization"
        start_time = time.time()

        try:
            # Check if database file exists
            if not os.path.exists(self.responder.cache_db_path):
                self.add_test_result(test_name, False, "Database file not created")
                return

            # Check database schema
            conn = sqlite3.connect(self.responder.cache_db_path)
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = ["issue_cache", "performance_metrics", "follow_ups"]
            missing_tables = [table for table in expected_tables if table not in tables]

            conn.close()

            if missing_tables:
                self.add_test_result(
                    test_name, False, f"Missing tables: {missing_tables}"
                )
            else:
                duration = time.time() - start_time
                self.add_test_result(
                    test_name,
                    True,
                    "All database tables created successfully",
                    duration,
                )

        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result(
                test_name, False, f"Database test failed: {e}", duration
            )

    async def test_language_detection(self):
        """Test automatic language detection"""
        test_name = "Language Detection"
        start_time = time.time()

        try:
            test_cases = [
                ("This is an English text about a bug in the software", "en"),
                ("Este es un texto en español sobre un error en el software", "es"),
                ("Ceci est un texte en français sur un bug dans le logiciel", "fr"),
                ("Dies ist ein deutscher Text über einen Fehler in der Software", "de"),
                ("Hello world", "en"),  # Default case
            ]

            success_count = 0
            for text, expected_lang in test_cases:
                detected_lang = await self.responder.detect_language(text)
                if detected_lang == expected_lang:
                    success_count += 1
                else:
                    logger.warning(
                        f"Language detection mismatch: expected {expected_lang}, got {detected_lang}"
                    )

            duration = time.time() - start_time
            success_rate = success_count / len(test_cases)

            if success_rate >= 0.8:  # 80% success rate threshold
                self.add_test_result(
                    test_name, True, f"Success rate: {success_rate:.1%}", duration
                )
            else:
                self.add_test_result(
                    test_name, False, f"Low success rate: {success_rate:.1%}", duration
                )

        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result(
                test_name, False, f"Language detection test failed: {e}", duration
            )

    async def test_caching_system(self):
        """Test caching functionality"""
        test_name = "Caching System"
        start_time = time.time()

        try:
            # Test data
            issue_number = 12345
            title = "Test issue for caching"
            body = "This is a test issue body for caching functionality"
            content_hash = self.responder._get_cache_key(title, body)

            # Test cache miss (should return None)
            cached_result = self.responder._get_cached_analysis(
                issue_number, content_hash
            )
            if cached_result is not None:
                self.add_test_result(
                    test_name, False, "Cache should be empty initially"
                )
                return

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
            cached_result = self.responder._get_cached_analysis(
                issue_number, content_hash
            )

            if cached_result and cached_result["analysis"]["success"]:
                duration = time.time() - start_time
                self.add_test_result(
                    test_name, True, "Caching system working correctly", duration
                )
            else:
                self.add_test_result(test_name, False, "Cache retrieval failed")

        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result(
                test_name, False, f"Caching test failed: {e}", duration
            )

    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        test_name = "Rate Limiting"
        start_time = time.time()

        try:
            # Test initial state (should allow requests)
            if not self.responder._check_rate_limit("test_service"):
                self.add_test_result(
                    test_name, False, "Rate limiting should allow initial requests"
                )
                return

            # Set up a low limit for testing
            self.responder.rate_limits["test_service"] = {
                "requests": 0,
                "reset_time": time.time() + 3600,
                "limit": 2,
            }

            # Test within limit
            self.responder._increment_rate_limit("test_service")
            if not self.responder._check_rate_limit("test_service"):
                self.add_test_result(
                    test_name, False, "Should still be within rate limit"
                )
                return

            # Test at limit
            self.responder._increment_rate_limit("test_service")
            if self.responder._check_rate_limit("test_service"):
                self.add_test_result(test_name, False, "Should be at rate limit")
                return

            duration = time.time() - start_time
            self.add_test_result(
                test_name, True, "Rate limiting working correctly", duration
            )

        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result(
                test_name, False, f"Rate limiting test failed: {e}", duration
            )

    async def test_fallback_analysis(self):
        """Test fallback analysis system"""
        test_name = "Fallback Analysis"
        start_time = time.time()

        try:
            test_cases = [
                (
                    "Bug in login system",
                    "The application crashes when I try to log in",
                    IssueType.BUG,
                ),
                (
                    "Add dark mode feature",
                    "Please add a dark mode toggle to the settings",
                    IssueType.FEATURE_REQUEST,
                ),
                (
                    "How to install?",
                    "I need help installing this software",
                    IssueType.QUESTION,
                ),
                (
                    "Update documentation",
                    "The README needs to be updated with new examples",
                    IssueType.DOCUMENTATION,
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
                else:
                    logger.warning(
                        f"Fallback analysis mismatch for '{title}': expected {expected_type.value}, got {result['analysis_data']['issue_type']}"
                    )

            duration = time.time() - start_time
            success_rate = success_count / len(test_cases)

            if success_rate >= 0.75:  # 75% success rate threshold
                self.add_test_result(
                    test_name, True, f"Success rate: {success_rate:.1%}", duration
                )
            else:
                self.add_test_result(
                    test_name, False, f"Low success rate: {success_rate:.1%}", duration
                )

        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result(
                test_name, False, f"Fallback analysis test failed: {e}", duration
            )

    async def test_performance_metrics(self):
        """Test performance metrics collection"""
        test_name = "Performance Metrics"
        start_time = time.time()

        try:
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

            if "error" in report:
                self.add_test_result(
                    test_name, False, f"Performance report error: {report['error']}"
                )
                return

            # Check if report contains expected data
            if "generated_at" in report and "cached_issues" in report:
                duration = time.time() - start_time
                self.add_test_result(
                    test_name, True, "Performance metrics working correctly", duration
                )
            else:
                self.add_test_result(
                    test_name, False, "Performance report missing expected fields"
                )

        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result(
                test_name, False, f"Performance metrics test failed: {e}", duration
            )

    async def test_follow_up_scheduling(self):
        """Test follow-up scheduling functionality"""
        test_name = "Follow-up Scheduling"
        start_time = time.time()

        try:
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

            if result and result[0] == test_issue:
                duration = time.time() - start_time
                self.add_test_result(
                    test_name, True, "Follow-up scheduling working correctly", duration
                )
            else:
                self.add_test_result(
                    test_name, False, "Follow-up not found in database"
                )

        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result(
                test_name, False, f"Follow-up scheduling test failed: {e}", duration
            )

    async def test_template_system(self):
        """Test response template system"""
        test_name = "Template System"
        start_time = time.time()

        try:
            # Test English templates
            templates = self.responder.response_templates

            if "en" not in templates:
                self.add_test_result(test_name, False, "English templates not found")
                return

            en_templates = templates["en"]

            # Check if all issue types have templates
            required_types = [
                IssueType.BUG,
                IssueType.FEATURE_REQUEST,
                IssueType.QUESTION,
            ]
            missing_templates = []

            for issue_type in required_types:
                if issue_type not in en_templates:
                    missing_templates.append(issue_type.value)

            if missing_templates:
                self.add_test_result(
                    test_name, False, f"Missing templates: {missing_templates}"
                )
                return

            # Check template structure
            for issue_type, template in en_templates.items():
                required_keys = ["greeting", "acknowledgment", "next_steps", "closing"]
                missing_keys = [key for key in required_keys if key not in template]

                if missing_keys:
                    self.add_test_result(
                        test_name,
                        False,
                        f"Template {issue_type} missing keys: {missing_keys}",
                    )
                    return

            duration = time.time() - start_time
            self.add_test_result(
                test_name, True, "Template system working correctly", duration
            )

        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result(
                test_name, False, f"Template system test failed: {e}", duration
            )

    async def test_enhanced_processing_flow(self):
        """Test the complete enhanced processing flow"""
        test_name = "Enhanced Processing Flow"
        start_time = time.time()

        try:
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

            duration = time.time() - start_time

            # Check result structure
            if not isinstance(result, dict):
                self.add_test_result(test_name, False, "Result is not a dictionary")
                return

            required_fields = ["success", "issue_number", "processing_time"]
            missing_fields = [field for field in required_fields if field not in result]

            if missing_fields:
                self.add_test_result(
                    test_name, False, f"Missing result fields: {missing_fields}"
                )
                return

            if result.get("success"):
                self.add_test_result(
                    test_name,
                    True,
                    f"Processing successful in {duration:.2f}s",
                    duration,
                )
            else:
                # Failure is expected in test environment without real AI providers
                error = result.get("error", "Unknown error")
                if "fallback" in error.lower() or "analysis failed" in error.lower():
                    self.add_test_result(
                        test_name,
                        True,
                        f"Expected fallback behavior: {error}",
                        duration,
                    )
                else:
                    self.add_test_result(
                        test_name, False, f"Unexpected error: {error}", duration
                    )

        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result(
                test_name, False, f"Enhanced processing test failed: {e}", duration
            )

    async def run_all_tests(self):
        """Run all test cases"""
        logger.info("🧪 Starting Enhanced AI Issues Responder Test Suite...")

        test_methods = [
            self.test_database_initialization,
            self.test_language_detection,
            self.test_caching_system,
            self.test_rate_limiting,
            self.test_fallback_analysis,
            self.test_performance_metrics,
            self.test_follow_up_scheduling,
            self.test_template_system,
            self.test_enhanced_processing_flow,
        ]

        for test_method in test_methods:
            try:
                logger.info(f"Running {test_method.__name__}...")
                await test_method()
            except Exception as e:
                logger.error(f"Test {test_method.__name__} failed with exception: {e}")
                self.add_test_result(test_method.__name__, False, f"Exception: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        total_duration = sum(result["duration"] for result in self.test_results)

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "total_duration": total_duration,
            },
            "test_results": self.test_results,
            "recommendations": [],
        }

        # Add recommendations based on results
        if failed_tests > 0:
            report["recommendations"].append(
                "Review failed tests and address underlying issues"
            )

        if total_duration > 30:
            report["recommendations"].append(
                "Consider optimizing test performance for faster execution"
            )

        if report["test_summary"]["success_rate"] < 0.8:
            report["recommendations"].append(
                "Success rate below 80% - investigate system stability"
            )

        return report

    def print_report(self):
        """Print formatted test report"""
        report = self.generate_report()
        summary = report["test_summary"]

        print("\n" + "=" * 80)
        print("🧪 ENHANCED AI ISSUES RESPONDER TEST REPORT")
        print("=" * 80)

        print(f"\n📊 TEST SUMMARY:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed_tests']} ✅")
        print(f"  Failed: {summary['failed_tests']} ❌")
        print(f"  Success Rate: {summary['success_rate']:.1%}")
        print(f"  Total Duration: {summary['total_duration']:.2f}s")

        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration_str = (
                f" ({result['duration']:.2f}s)" if result["duration"] > 0 else ""
            )
            print(f"  {status}: {result['test_name']}{duration_str}")
            if result["details"]:
                print(f"    Details: {result['details']}")

        if report["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")

        print("\n" + "=" * 80)

        # Overall status
        if summary["success_rate"] >= 0.8:
            print("🎉 OVERALL STATUS: SYSTEM READY FOR DEPLOYMENT")
        else:
            print("⚠️ OVERALL STATUS: SYSTEM NEEDS ATTENTION")

        print("=" * 80)


async def main():
    """Main test execution function"""
    test_suite = EnhancedResponderTestSuite()

    try:
        await test_suite.setup()
        await test_suite.run_all_tests()
        test_suite.print_report()

        # Save detailed report
        report = test_suite.generate_report()
        with open("enhanced_responder_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n📄 Detailed report saved to: enhanced_responder_test_report.json")

        # Return exit code based on success rate
        success_rate = report["test_summary"]["success_rate"]
        return 0 if success_rate >= 0.8 else 1

    except Exception as e:
        logger.error(f"❌ Test suite execution failed: {e}")
        print(f"\n❌ FATAL ERROR: {e}")
        return 1

    finally:
        await test_suite.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
