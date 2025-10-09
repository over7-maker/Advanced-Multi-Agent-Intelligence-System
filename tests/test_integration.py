#!/usr/bin/env python3
"""
AMAS Integration Tests
Comprehensive integration testing for the complete AMAS system
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import after path modification
from amas.config.settings import get_settings  # noqa: E402
from amas.core.self.orchestrator import IntelligenceOrchestrator  # noqa: E402


class TestAMASIntegration:
    """Integration tests for the complete AMAS system"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test"""
        # Mock environment variables
        self.env_patcher = patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_openai_key",
                "GEMINIAI_API_KEY": "test_gemini_key",
                "GROQAI_API_KEY": "test_groq_key",
            },
        )
        self.env_patcher.start()

        # Initialize test variables
        self.orchestrator = None
        self.provider_manager = None
        self.intelligence_manager = None

    def teardown_method(self):
        """Cleanup after each test"""
        self.env_patcher.stop()

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        assert self.orchestrator is not None
        assert len(self.orchestrator.agents) == 7
        assert self.orchestrator.task_queue is not None

    @pytest.mark.asyncio
    async def test_provider_manager_initialization(self):
        """Test provider manager initializes correctly"""
        assert self.provider_manager is not None
        assert len(self.provider_manager.providers) > 0
        assert len(self.provider_manager.provider_configs) > 0

    @pytest.mark.asyncio
    async def test_intelligence_manager_initialization(self):
        """Test intelligence manager initializes correctly"""
        assert self.intelligence_manager is not None
        assert self.intelligence_manager.collective_intelligence is not None
        assert self.intelligence_manager.personality_orchestrator is not None
        assert self.intelligence_manager.predictive_engine is not None

    @pytest.mark.asyncio
    async def test_task_execution_flow(self):
        """Test complete task execution flow"""
        # Mock the provider execution
        with patch.object(
            self.provider_manager, "get_best_provider"
        ) as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.infer.return_value = "Test response from AI"
            mock_get_provider.return_value = mock_provider

            # Execute a test task
            result = await self.orchestrator.execute_task(
                task_type="security_scan",
                target="example.com",
                parameters={"depth": "standard"},
            )

            # Verify result
            assert result is not None
            assert "task_id" in result
            assert result["status"] in ["completed", "failed"]
            assert "execution_time" in result

    @pytest.mark.asyncio
    async def test_system_status(self):
        """Test system status endpoint"""
        status = await self.orchestrator.get_system_status()
        assert status is not None
        assert "system_status" in status
        assert "agents" in status
        assert "providers" in status
        assert "tasks" in status
        assert "intelligence" in status

    @pytest.mark.asyncio
    async def test_agent_capabilities(self):
        """Test agent capabilities retrieval"""
        capabilities = await self.orchestrator.get_agent_capabilities()
        assert capabilities is not None
        assert len(capabilities) == 7

        # Check specific agents
        assert "security_expert" in capabilities
        assert "code_analysis" in capabilities
        assert "intelligence_gathering" in capabilities

        # Check agent structure
        for agent_id, agent_info in capabilities.items():
            assert "name" in agent_info
            assert "description" in agent_info
            assert "capabilities" in agent_info
            assert "status" in agent_info

    @pytest.mark.asyncio
    async def test_provider_status(self):
        """Test provider status retrieval"""
        status = self.provider_manager.get_provider_status()
        assert status is not None
        assert len(status) > 0

        # Check status structure
        for provider_name, provider_info in status.items():
            assert "status" in provider_info
            assert "available" in provider_info
            assert "priority" in provider_info

    @pytest.mark.asyncio
    async def test_intelligence_dashboard_data(self):
        """Test intelligence dashboard data retrieval"""
        data = await self.intelligence_manager.get_intelligence_dashboard_data()
        assert data is not None
        assert "collective_intelligence" in data
        assert "adaptive_personalities" in data
        assert "predictive_accuracy" in data
        assert "resource_predictions" in data

    @pytest.mark.asyncio
    async def test_task_optimization(self):
        """Test task optimization before execution"""
        task_data = {
            "task_type": "security_scan",
            "target": "example.com",
            "parameters": {"depth": "standard"},
            "user_id": "test_user",
        }

        optimization = await self.intelligence_manager.optimize_task_before_execution(
            task_data
        )
        assert optimization is not None
        assert "optimal_agents" in optimization
        assert "task_prediction" in optimization
        assert "optimization_recommendations" in optimization
        assert "personality_prompts" in optimization

    @pytest.mark.asyncio
    async def test_task_completion_processing(self):
        """Test task completion processing for learning"""
        task_data = {
            "task_id": "test_001",
            "task_type": "security_scan",
            "target": "example.com",
            "parameters": {"depth": "standard"},
            "agents_used": ["security_expert"],
            "execution_time": 120.5,
            "success_rate": 0.9,
            "solution_quality": 0.85,
            "error_patterns": [],
            "user_feedback": {"rating": 4, "comments": "Good work"},
        }

        # This should not raise an exception
        await self.intelligence_manager.process_task_completion(task_data)
        # Verify the task was processed (simplified check)
        assert True  # If we get here without exception, it worked

    def test_agent_prompt_creation(self):
        """Test agent prompt creation"""
        prompt = self.orchestrator._create_agent_prompt(
            task_type="security_scan",
            target="example.com",
            parameters={"depth": "standard"},
            agents=["security_expert", "intelligence_gathering"],
        )

        assert prompt is not None
        assert isinstance(prompt, str)
        assert "security_scan" in prompt
        assert "example.com" in prompt
        assert "Security Expert" in prompt
        assert "Intelligence Gathering" in prompt

    def test_agent_performance_analysis(self):
        """Test agent performance analysis"""
        analysis = self.orchestrator._analyze_agent_performance(
            agents=["security_expert"],
            response="This is a test response with analysis and recommendations",
        )

        assert analysis is not None
        assert "agents_used" in analysis
        assert "response_length" in analysis
        assert "has_recommendations" in analysis
        assert "has_analysis" in analysis
        assert "completeness_score" in analysis


class TestAMASEndToEnd:
    """End-to-end tests for AMAS system"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test"""
        self.env_patcher = patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_openai_key",
                "GEMINIAI_API_KEY": "test_gemini_key",
                "GROQAI_API_KEY": "test_groq_key",
            },
        )
        self.env_patcher.start()

    def teardown_method(self):
        """Cleanup after each test"""
        self.env_patcher.stop()

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete AMAS workflow from task creation to completion"""
        # Mock provider execution
        with patch.object(
            self.provider_manager, "get_best_provider"
        ) as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.infer.return_value = (
                "Comprehensive security analysis completed"
            )
            mock_get_provider.return_value = mock_provider

            # 1. Execute a task
            result = await self.orchestrator.execute_task(
                task_type="security_scan",
                target="example.com",
                parameters={"depth": "comprehensive"},
            )

            # 2. Verify task execution
            assert result["status"] == "completed"
            assert "security_expert" in result["agents_used"]

            # 3. Check system status
            status = await self.orchestrator.get_system_status()
            assert status["tasks"]["completed"] > 0

            # 4. Verify intelligence learning
            intelligence_data = (
                await self.intelligence_manager.get_intelligence_dashboard_data()
            )
            assert intelligence_data is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
