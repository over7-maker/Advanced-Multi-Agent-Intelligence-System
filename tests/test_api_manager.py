#!/usr/bin/env python3
"""
Comprehensive Test Suite for AMAS AI API Manager

This module provides comprehensive tests for the AI API Manager,
ensuring reliability, fallback mechanisms, and performance.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from amas.core.ai_api_manager import (  # noqa: E402
    AIAPIManager,
    APIConfig,
    APIHealth,
    APIType,
)
from amas.core.api_clients import (  # noqa: E402
    APIClientFactory,
    OpenAICompatibleClient,
)
from amas.core.api_integration import EnhancedOSINTAgent  # noqa: E402
from amas.core.enhanced_orchestrator import (  # noqa: E402
    EnhancedOrchestrator,
    TaskResult,
)


class TestAPIConfig:
    """Test API configuration"""

    def test_api_config_creation(self):
        """Test API configuration creation"""
        config = APIConfig(
            name="Test API",
            api_key="test_key",
            base_url="https://api.test.com/v1",
            model="test-model",
            api_type=APIType.OPENAI_COMPATIBLE,
            capabilities=["test"],
            priority=1,
        )

        assert config.name == "Test API"
        assert config.api_key == "test_key"
        assert config.base_url == "https://api.test.com/v1"
        assert config.model == "test-model"
        assert config.api_type == APIType.OPENAI_COMPATIBLE
        assert "test" in config.capabilities
        assert config.priority == 1


class TestAPIHealth:
    """Test API health tracking"""

    def test_api_health_initialization(self):
        """Test API health initialization"""
        health = APIHealth()

        assert health.is_healthy is True
        assert health.consecutive_failures == 0
        assert health.total_requests == 0
        assert health.successful_requests == 0
        assert health.error_rate == 0.0

    def test_api_health_update_success(self):
        """Test API health update on success"""
        health = APIHealth()

        # Simulate successful request
        health.last_success = datetime.now()
        health.consecutive_failures = 0
        health.total_requests = 1
        health.successful_requests = 1
        health.error_rate = 0.0

        assert health.is_healthy is True
        assert health.error_rate == 0.0

    def test_api_health_update_failure(self):
        """Test API health update on failure"""
        health = APIHealth()

        # Simulate failed request
        health.last_failure = datetime.now()
        health.consecutive_failures = 1
        health.total_requests = 1
        health.successful_requests = 0
        health.error_rate = 1.0

        assert health.consecutive_failures == 1
        assert health.error_rate == 1.0


class TestAIAPIManager:
    """Test AI API Manager"""

    @pytest.fixture
    def api_manager(self):
        """Create API manager instance for testing"""
        return AIAPIManager()

    def test_api_manager_initialization(self, api_manager):
        """Test API manager initialization"""
        assert api_manager is not None
        assert hasattr(api_manager, "apis")
        assert hasattr(api_manager, "health_status")

    def test_setup_apis(self, api_manager):
        """Test API setup"""
        # Mock environment variables
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "test_deepseek_key",
                "CODESTRAL_API_KEY": "test_codestral_key",
                "GROK_API_KEY": "test_grok_key",
            },
        ):
            api_manager._setup_apis()

            # Check if APIs were configured
            assert len(api_manager.apis) > 0
            assert (
                "deepseek" in api_manager.apis
                or "codestral" in api_manager.apis
            )

    def test_get_available_apis(self, api_manager):
        """Test getting available APIs"""
        # Mock some APIs
        api_manager.apis = {
            "api1": Mock(priority=1, capabilities=["test"]),
            "api2": Mock(priority=2, capabilities=["test"]),
        }
        api_manager.health_status = {
            "api1": APIHealth(is_healthy=True),
            "api2": APIHealth(is_healthy=False),
        }

        available = api_manager.get_available_apis()
        assert "api1" in available
        assert "api2" not in available

    def test_get_available_apis_with_task_type(self, api_manager):
        """Test getting available APIs filtered by task type"""
        # Mock APIs with different capabilities
        api_manager.apis = {
            "api1": Mock(priority=1, capabilities=["osint", "analysis"]),
            "api2": Mock(priority=2, capabilities=["code_analysis"]),
        }
        api_manager.health_status = {
            "api1": APIHealth(is_healthy=True),
            "api2": APIHealth(is_healthy=True),
        }

        available = api_manager.get_available_apis("osint")
        assert "api1" in available
        assert "api2" not in available


class TestAPIClients:
    """Test API clients"""

    def test_openai_compatible_client_creation(self):
        """Test OpenAI compatible client creation"""
        client = OpenAICompatibleClient(
            api_key="test_key",
            base_url="https://api.test.com/v1",
            model="test-model",
        )

        assert client.api_key == "test_key"
        assert client.base_url == "https://api.test.com/v1"
        assert client.model == "test-model"

    def test_api_client_factory(self):
        """Test API client factory"""
        client = APIClientFactory.create_client(
            api_name="deepseek",
            api_key="test_key",
            base_url="https://api.test.com/v1",
            model="test-model",
        )

        assert client is not None
        assert hasattr(client, "generate")


class TestEnhancedOrchestrator:
    """Test Enhanced Orchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        return EnhancedOrchestrator()

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator is not None
        assert hasattr(orchestrator, "api_manager")
        assert hasattr(orchestrator, "agent_capabilities")

    def test_agent_capabilities_setup(self, orchestrator):
        """Test agent capabilities setup"""
        assert "osint_agent" in orchestrator.agent_capabilities
        assert "analysis_agent" in orchestrator.agent_capabilities
        assert "code_agent" in orchestrator.agent_capabilities

    def test_determine_agent_type(self, orchestrator):
        """Test agent type determination"""
        assert orchestrator._determine_agent_type("osint") == "osint_agent"
        assert orchestrator._determine_agent_type("analysis") == "analysis_agent"
        assert (
            orchestrator._determine_agent_type("code_analysis")
            == "code_agent"
        )
        assert orchestrator._determine_agent_type("unknown") == "general_agent"

    def test_get_system_prompt(self, orchestrator):
        """Test system prompt generation"""
        osint_prompt = orchestrator._get_system_prompt(
            "osint_agent", "osint"
        )
        assert "OSINT" in osint_prompt
        assert "intelligence" in osint_prompt

        analysis_prompt = orchestrator._get_system_prompt(
            "analysis_agent", "analysis"
        )
        assert "analysis" in analysis_prompt
        assert "pattern" in analysis_prompt


class TestEnhancedAgents:
    """Test Enhanced Agents"""

    def test_enhanced_osint_agent_creation(self):
        """Test enhanced OSINT agent creation"""
        agent = EnhancedOSINTAgent()

        assert agent.agent_id == "osint_001"
        assert agent.name == "Enhanced OSINT Agent"
        assert "osint_collection" in agent.capabilities

    # def test_enhanced_investigation_agent_creation(self):
    #     """Test enhanced investigation agent creation"""
    #     agent = EnhancedInvestigationAgent()
    #
    #     assert agent.agent_id == "investigation_001"
    #     assert agent.name == "Enhanced Investigation Agent"
    #     assert "investigation" in agent.capabilities
    #
    # def test_enhanced_forensics_agent_creation(self):
    #     """Test enhanced forensics agent creation"""
    #     agent = EnhancedForensicsAgent()
    #
    #     assert agent.agent_id == "forensics_001"
    #     assert agent.name == "Enhanced Forensics Agent"
    #     assert "digital_forensics" in agent.capabilities
    #
    # def test_enhanced_reporting_agent_creation(self):
    #     """Test enhanced reporting agent creation"""
    #     agent = EnhancedReportingAgent()
    #
    #     assert agent.agent_id == "reporting_001"
    #     assert agent.name == "Enhanced Reporting Agent"
    #     assert "report_generation" in agent.capabilities


class TestIntegration:
    """Test integration between components"""

    @pytest.mark.asyncio
    async def test_api_manager_integration(self):
        """Test API manager integration"""
        # Mock environment variables
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "test_deepseek_key",
                "CODESTRAL_API_KEY": "test_codestral_key",
            },
        ):
            api_manager = AIAPIManager()

            # Test health status
            health = api_manager.get_health_status()
            assert "total_apis" in health
            assert "healthy_apis" in health

    @pytest.mark.asyncio
    async def test_orchestrator_integration(self):
        """Test orchestrator integration"""
        orchestrator = EnhancedOrchestrator()

        # Test performance stats
        stats = orchestrator.get_performance_stats()
        assert "total_tasks" in stats
        assert "success_rate" in stats


class TestErrorHandling:
    """Test error handling and fallback mechanisms"""

    @pytest.mark.asyncio
    async def test_api_failure_handling(self):
        """Test API failure handling"""
        api_manager = AIAPIManager()

        # Mock all APIs as unhealthy
        for api_name in api_manager.health_status:
            api_manager.health_status[api_name].is_healthy = False

        # Test getting available APIs
        available = api_manager.get_available_apis()
        assert len(available) == 0

    @pytest.mark.asyncio
    async def test_task_execution_failure(self):
        """Test task execution failure handling"""
        orchestrator = EnhancedOrchestrator()

        # Mock API manager to always fail
        with patch.object(
            orchestrator.api_manager, "generate_response"
        ) as mock_generate:
            mock_generate.side_effect = Exception("API failure")

            result = await orchestrator.execute_task(
                task_id="test_001", task_type="analysis", prompt="Test prompt"
            )

            assert result.success is False
            assert result.error is not None


class TestPerformance:
    """Test performance and optimization"""

    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self):
        """Test concurrent task execution"""
        orchestrator = EnhancedOrchestrator()

        # Create multiple tasks
        tasks = [
            {
                "task_id": f"test_{i}",
                "task_type": "analysis",
                "prompt": f"Test prompt {i}",
                "agent_type": "analysis_agent",
            }
            for i in range(5)
        ]

        # Mock API manager to return successful responses
        with patch.object(
            orchestrator.api_manager, "generate_response"
        ) as mock_generate:
            mock_generate.return_value = {
                "content": "Test response",
                "api_used": "test_api",
            }

            results = await orchestrator.execute_parallel_tasks(
                tasks, max_concurrent=3
            )

            assert len(results) == 5
            assert all(result.success for result in results)

    def test_health_monitoring(self):
        """Test health monitoring functionality"""
        api_manager = AIAPIManager()

        # Test health status
        health = api_manager.get_health_status()
        assert isinstance(health, dict)
        assert "total_apis" in health
        assert "healthy_apis" in health
        assert "unhealthy_apis" in health


class TestConfiguration:
    """Test configuration and setup"""

    def test_environment_variable_handling(self):
        """Test environment variable handling"""
        # Test with no environment variables
        with patch.dict(os.environ, {}, clear=True):
            api_manager = AIAPIManager()
            assert len(api_manager.apis) == 0

        # Test with some environment variables
        with patch.dict(
            os.environ,
            {"DEEPSEEK_API_KEY": "test_key", "CODESTRAL_API_KEY": "test_key"},
        ):
            api_manager = AIAPIManager()
            assert len(api_manager.apis) > 0

    def test_api_priority_ordering(self):
        """Test API priority ordering"""
        api_manager = AIAPIManager()

        # Mock APIs with different priorities
        api_manager.apis = {
            "api1": Mock(priority=3, capabilities=["test"]),
            "api2": Mock(priority=1, capabilities=["test"]),
            "api3": Mock(priority=2, capabilities=["test"]),
        }
        api_manager.health_status = {
            "api1": APIHealth(is_healthy=True),
            "api2": APIHealth(is_healthy=True),
            "api3": APIHealth(is_healthy=True),
        }

        available = api_manager.get_available_apis()
        assert available[0] == "api2"  # Highest priority
        assert available[1] == "api3"
        assert available[2] == "api1"

# Integration tests
class TestEndToEnd:
    """End-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete workflow from task submission to completion"""
        # This would test the complete workflow
        # For now, just test that components can be instantiated
        api_manager = AIAPIManager()
        orchestrator = EnhancedOrchestrator()

        assert api_manager is not None
        assert orchestrator is not None

    @pytest.mark.asyncio
    async def test_fallback_mechanism(self):
        """Test fallback mechanism"""
        orchestrator = EnhancedOrchestrator()

        # Mock first API to fail, second to succeed
        with patch.object(
            orchestrator.api_manager, "generate_response"
        ) as mock_generate:
            mock_generate.side_effect = [
                Exception("First API failed"),
                {"content": "Success response", "api_used": "backup_api"},
            ]

            result = await orchestrator.execute_task(
                task_id="test_001", task_type="analysis", prompt="Test prompt"
            )

            # Should succeed with fallback
            assert result.success is True
            assert result.api_used == "backup_api"

# Utility functions for testing
def create_mock_api_response(
    content: str = "Test response", api_used: str = "test_api"
) -> Dict[str, Any]:
    """Create mock API response for testing"""
    return {
        "content": content,
        "api_used": api_used,
        "model": "test-model",
        "timestamp": datetime.now().isoformat(),
    }

def create_mock_task_result(
    success: bool = True, error: str = None
) -> TaskResult:
    """Create mock task result for testing"""
    return TaskResult(
        task_id="test_001",
        task_type="analysis",
        success=success,
        result=create_mock_api_response() if success else None,
        error=error,
        api_used="test_api" if success else None,
        execution_time=1.0,
        timestamp=datetime.now().isoformat(),
    )

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
