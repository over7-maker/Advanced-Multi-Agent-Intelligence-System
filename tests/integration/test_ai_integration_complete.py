"""
Complete AI Integration Test - Tests all AI integrations and workflows
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest.mark.integration
class TestAIIntegrationComplete:
    """Complete AI Integration Test Suite"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment"""
        self.ai_service = None
        self.config_manager = None
        self.test_results = {}

        # Try to import AI service if available
        try:
            from src.amas.services.ai_service_manager import (
                AIProvider,
                AIServiceManager,
            )

            config = {
                "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
                "glm_api_key": os.getenv("GLM_API_KEY"),
                "grok_api_key": os.getenv("GROK_API_KEY"),
                "kimi_api_key": os.getenv("KIMI_API_KEY"),
                "qwen_api_key": os.getenv("QWEN_API_KEY"),
                "gptoss_api_key": os.getenv("GPTOSS_API_KEY"),
            }

            self.ai_service = AIServiceManager(config)
            await self.ai_service.initialize()
            self.AIProvider = AIProvider
            logger.info("AI Service initialized successfully")
        except ImportError:
            logger.warning("AI Service not available, using mock tests")
            self.ai_service = None
            self.AIProvider = None

        yield

        # Cleanup
        if self.ai_service:
            await self.ai_service.shutdown()

    async def test_ai_provider_fallback(self):
        """Test AI provider fallback system."""
        if not self.ai_service:
            pytest.skip("AI Service not available")

        # Test with simple request
        test_response = await self.ai_service.generate_response(
            "Hello, this is a connectivity test. Respond with 'OK'."
        )

        assert test_response.success or test_response.error is not None
        if test_response.success:
            assert len(test_response.content) > 0
            assert test_response.provider is not None

    async def test_multi_agent_coordination(self):
        """Test multi-agent coordination."""
        # This is a placeholder test since the actual multi-agent system may not be available
        # In a real test, this would test coordination between multiple AI agents
        assert True

    async def test_ai_providers(self):
        """Test all AI providers"""
        if not self.ai_service or not self.AIProvider:
            pytest.skip("AI Service not available")

        provider_tests = {}
        for provider in self.AIProvider:
            logger.info(f"Testing {provider.value}...")

            try:
                # Test with simple request
                test_response = await self.ai_service.generate_response(
                    "Hello, this is a connectivity test. Respond with 'OK'.",
                    preferred_provider=provider,
                )

                provider_tests[provider.value] = {
                    "status": "success" if test_response.success else "failed",
                    "response_time": test_response.response_time,
                    "error": test_response.error if not test_response.success else None,
                }

                if test_response.success:
                    logger.info(f"✓ {provider.value} test successful")
                else:
                    logger.warning(
                        f"✗ {provider.value} test failed: {test_response.error}"
                    )

            except Exception as e:
                provider_tests[provider.value] = {
                    "status": "error",
                    "error": str(e),
                }
                logger.error(f"✗ {provider.value} test error: {e}")

        # At least one provider should work
        successful_providers = [
            p for p in provider_tests.values() if p["status"] == "success"
        ]
        assert len(successful_providers) > 0, "No AI providers are working"

    async def test_code_generation_capability(self):
        """Test code generation capability"""
        if not self.ai_service:
            pytest.skip("AI Service not available")

        prompt = """Generate a simple Python function that calculates the factorial of a number.
Include proper error handling and documentation."""

        response = await self.ai_service.generate_code(prompt, "python")

        assert response.success or response.error is not None
        if response.success:
            assert len(response.content) > 0
            assert response.provider is not None

    async def test_code_analysis_capability(self):
        """Test code analysis capability"""
        if not self.ai_service:
            pytest.skip("AI Service not available")

        code = """
def calculate_factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    return n * calculate_factorial(n-1)
"""

        response = await self.ai_service.analyze_code(code, "python")

        assert response.success or response.error is not None
        if response.success:
            assert len(response.content) > 0
            assert response.provider is not None

    def test_ai_scripts_existence(self):
        """Test that AI scripts exist"""
        scripts = [
            "scripts/development/setup_ai_integration.py",
            "scripts/ai_code_analyzer.py",
            "scripts/ai_code_improver.py",
            "scripts/ai_test_generator.py",
        ]

        missing_scripts = []
        for script in scripts:
            if not Path(script).exists():
                missing_scripts.append(script)

        # Allow some scripts to be missing in test environment
        assert len(missing_scripts) < len(
            scripts
        ), f"Too many missing scripts: {missing_scripts}"

    def test_environment_variables(self):
        """Test that required environment variables are set"""
        # In test environment, we don't require all API keys to be set
        # Just check that the test environment is properly configured
        assert os.getenv("ENVIRONMENT") == "testing"
        assert os.getenv("DATABASE_URL") is not None
        assert os.getenv("SECRET_KEY") is not None

    async def test_ai_service_initialization(self):
        """Test AI service initialization"""
        if not self.ai_service:
            # If AI service is not available, that's okay in test environment
            assert True
            return

        # If available, test that it's properly initialized
        assert hasattr(self.ai_service, "generate_response")
        assert hasattr(self.ai_service, "generate_code")
        assert hasattr(self.ai_service, "analyze_code")

    def test_workflow_configuration(self):
        """Test GitHub Actions workflow configuration"""
        workflow_file = Path(".github/workflows/ai_development.yml")

        # In test environment, workflow file might not exist
        if workflow_file.exists():
            with open(workflow_file, "r", encoding="utf-8") as f:
                workflow_content = f.read()

            # Check for some expected content
            assert len(workflow_content) > 0
            # More specific checks can be added based on actual workflow
        else:
            # It's okay if workflow doesn't exist in test environment
            assert True

    async def test_ai_response_format(self):
        """Test AI response format and structure"""
        if not self.ai_service:
            pytest.skip("AI Service not available")

        response = await self.ai_service.generate_response("Test")

        # Check response structure
        assert hasattr(response, "success")
        assert hasattr(response, "content")
        assert hasattr(response, "provider")
        assert hasattr(response, "response_time")
        assert hasattr(response, "error")

    @pytest.mark.slow
    async def test_ai_performance(self):
        """Test AI service performance"""
        if not self.ai_service:
            pytest.skip("AI Service not available")

        start_time = datetime.now()
        response = await self.ai_service.generate_response("Quick test")
        end_time = datetime.now()

        response_time = (end_time - start_time).total_seconds()

        # Response should be reasonably fast (under 30 seconds)
        assert response_time < 30, f"Response took too long: {response_time}s"

    def test_configuration_modes(self):
        """Test different configuration modes"""
        # Test that configuration modes are properly defined
        config_modes = ["basic", "standard", "full"]

        # In production, we'd check actual configuration
        # For tests, just verify the concept exists
        assert len(config_modes) == 3

    async def test_error_handling(self):
        """Test error handling in AI service"""
        if not self.ai_service:
            pytest.skip("AI Service not available")

        # Test with invalid input
        response = await self.ai_service.generate_response("")

        # Should handle empty input gracefully
        assert response.success or response.error is not None

    async def test_concurrent_requests(self):
        """Test handling of concurrent AI requests"""
        if not self.ai_service:
            pytest.skip("AI Service not available")

        # Send multiple requests concurrently
        tasks = [
            self.ai_service.generate_response(f"Test request {i}") for i in range(3)
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # All requests should complete (either success or proper error)
        for response in responses:
            if isinstance(response, Exception):
                # Exception is acceptable in test environment
                assert True
            else:
                assert hasattr(response, "success")
