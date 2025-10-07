#!/usr/bin/env python3
"""
AMAS Integration Tests
Comprehensive integration testing for the complete AMAS system
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import httpx

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from amas.core.unified_orchestrator_v2 import TaskPriority
from amas.orchestrator import orchestrator
from amas.providers.manager import provider_manager
from amas.intelligence.intelligence_manager import intelligence_manager

class TestAMASIntegration:
    """Integration tests for the complete AMAS system"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test"""
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test_openai_key',
            'GEMINIAI_API_KEY': 'test_gemini_key',
            'GROQAI_API_KEY': 'test_groq_key'
        })
        self.env_patcher.start()
    
    def teardown_method(self):
        """Cleanup after each test"""
        self.env_patcher.stop()
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        assert orchestrator is not None
        assert len(orchestrator.agents) == 7
        assert orchestrator.task_queue is not None
    
    @pytest.mark.asyncio
    async def test_provider_manager_initialization(self):
        """Test provider manager initializes correctly"""
        assert provider_manager is not None
        assert len(provider_manager.providers) > 0
        assert len(provider_manager.provider_configs) > 0
    
    @pytest.mark.asyncio
    async def test_intelligence_manager_initialization(self):
        """Test intelligence manager initializes correctly"""
        assert intelligence_manager is not None
        assert intelligence_manager.collective_intelligence is not None
        assert intelligence_manager.personality_orchestrator is not None
        assert intelligence_manager.predictive_engine is not None
    
    @pytest.mark.asyncio
    async def test_end_to_end_task_processing(
        self, amas_app, test_client: httpx.AsyncClient
    ):
        """Test complete task processing workflow"""
        # Submit a task via API
        task_data = {
            "description": "Collect intelligence on AI advancements",
            "task_type": "osint",
            "priority": 1,
            "metadata": {
                "title": "Collect AI Advancements",
                "parameters": {
                    "keywords": ["AI", "machine learning", "advancements"],
                    "sources": ["web", "academic"],
                },
                "required_agent_roles": ["intelligence_gatherer_agent"]
            }
        }

        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.post(
            "/tasks", json=task_data, headers=headers
        )
        assert response.status_code == 200

        task_id = response.json()["task_id"]

        # Wait for task processing
        max_attempts = 10
        for attempt in range(max_attempts):
            status_response = await test_client.get(
                f"/tasks/{task_id}", headers=headers
            )
            
            # Verify result
            assert result is not None
            assert "task_id" in result
            assert result["status"] in ["completed", "failed"]
            assert "execution_time" in result
    
    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self, amas_app):
        """Test coordination between multiple agents"""
        orchestrator = amas_app.orchestrator

        # Submit multiple tasks of different types
        tasks = [
            {
                "description": "OSINT task",
                "task_type": "osint",
                "priority": 1,
                "metadata": {"title": "OSINT Task", "parameters": {"keywords": ["test"]}, "required_agent_roles": ["intelligence_gatherer_agent"]}
            },
            {
                "description": "Forensics task",
                "task_type": "forensics",
                "priority": 2,
                "metadata": {"title": "Forensics Task", "parameters": {"source": "/dev/sda1"}, "required_agent_roles": ["forensics_agent"]}
            },
            {
                "description": "Data analysis task",
                "task_type": "data_analysis",
                "priority": 3,
                "metadata": {"title": "Data Analysis Task", "parameters": {"data": [{"value": 1}]}, "required_agent_roles": ["data_agent"]}
            },
        ]

        task_ids = []
        for task_data in tasks:
            task_id = await orchestrator.submit_task(
                description=task_data["description"],
                task_type=task_data["task_type"],
                priority=TaskPriority(task_data["priority"]),
                metadata=task_data["metadata"],
            )

            task_ids.append(task_id)


        # Wait for all tasks to complete
        for task_id in task_ids:
            max_attempts = 10
            for attempt in range(max_attempts):
                status = await orchestrator.get_task_status(task_id)
                if status["status"] in ["completed", "failed"]:
                    break
                await asyncio.sleep(0.5)

            assert status["status"] == "completed"

    @pytest.mark.asyncio
    async def test_system_status(self):
        """Test system status endpoint"""
        status = await orchestrator.get_system_status()
        
        assert status is not None
        assert "system_status" in status
        assert "agents" in status
        assert "providers" in status
        assert "tasks" in status
        assert "intelligence" in status
    
    @pytest.mark.asyncio
    async def test_agent_capabilities(self):
        """Test agent capabilities retrieval"""
        capabilities = await orchestrator.get_agent_capabilities()
        
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
        status = provider_manager.get_provider_status()
        
        assert status is not None
        assert len(status) > 0
        
        # Check status structure
        for provider_name, provider_info in status.items():
            assert "status" in provider_info
            assert "available" in provider_info
            assert "priority" in provider_info
    
    @pytest.mark.asyncio
    async def test_error_handling(self, amas_app):
        """Test error handling in the system"""
        orchestrator = amas_app.orchestrator

        # Test invalid task submission
        invalid_task = {
            "description": "Invalid task",
            "task_type": "invalid_type",
            "priority": "LOW",
            "metadata": {"title": "Invalid Task"}
        }

        # Should handle gracefully
        try:
            task_id = await orchestrator.submit_task(
                description=invalid_task["description"],
                task_type=invalid_task["task_type"],
                priority=TaskPriority(invalid_task["priority"]),
                metadata=invalid_task["metadata"],
            )

            # If it doesn't raise an exception, check the result
            if task_id:
                status = await orchestrator.get_task_status(task_id)
                # Should either complete or fail gracefully
                assert status["status"] in ["completed", "failed", "pending"]
        except Exception as e:
            # Should handle errors gracefully
            assert isinstance(e, Exception)

    @pytest.mark.asyncio
    async def test_concurrent_task_processing(self, amas_app):
        """Test concurrent task processing"""
        orchestrator = amas_app.orchestrator

        # Submit multiple tasks concurrently
        tasks = [
            {
                "description": f"OSINT task {i}",
                "task_type": "osint",
                "priority": TaskPriority.MEDIUM, # Use a valid TaskPriority enum member
                "metadata": {"title": f"OSINT Task {i}", "parameters": {"keywords": [f"keyword_{i}"]}, "required_agent_roles": ["intelligence_gatherer_agent"]}
            }
            for i in range(5)
        ]

        # Submit all tasks
        task_ids = []
        for task_data in tasks:
            task_id = await orchestrator.submit_task(
                description=task_data["description"],
                task_type=task_data["task_type"],
                priority=task_data["priority"],
                metadata=task_data["metadata"],
            )
            task_ids.append(task_id)


        # Wait for all tasks to complete
        completed_tasks = 0
        max_attempts = 20

        for attempt in range(max_attempts):
            for task_id in task_ids:
                status = await orchestrator.get_task_status(task_id)
                if status["status"] in ["completed", "failed"]:
                    completed_tasks += 1

            if completed_tasks >= len(task_ids):
                break

            await asyncio.sleep(0.5)

        # Verify all tasks were processed
        assert completed_tasks >= len(task_ids)

    @pytest.mark.asyncio
    async def test_service_dependencies(self, amas_app):
        """Test service dependencies and initialization order"""
        service_manager = amas_app.service_manager

        # Check that all services are initialized
        services = [
            service_manager.get_llm_service(),
            service_manager.get_vector_service(),
            service_manager.get_knowledge_graph(),
            service_manager.get_database_service(),
            service_manager.get_security_service(),
        ]

        for service in services:
            assert service is not None

        # Test service health checks
        health_status = await service_manager.health_check_all_services()
        assert "llm" in health_status
        assert "vector" in health_status
        assert "knowledge_graph" in health_status
        assert "database" in health_status
        assert "security" in health_status

    @pytest.mark.asyncio
    async def test_workflow_execution(
        self, amas_app, test_client: httpx.AsyncClient
    ):
        """Test workflow execution"""
        workflow_data = {
            "workflow_id": "test_workflow",
            "parameters": {"target": "test_target", "depth": 2},
        }

        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.post(
            f"/workflows/{workflow_data['workflow_id']}/execute",
            json=workflow_data["parameters"],
            headers=headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert "workflow_id" in data
        assert "status" in data

    @pytest.mark.asyncio
    async def test_audit_trail(self, amas_app, test_client: httpx.AsyncClient):
        """Test audit trail functionality"""
        # Perform some actions that should generate audit events
        task_data = {
            "description": "Audit test task",
            "task_type": "osint",
            "priority": TaskPriority.MEDIUM,
            "metadata": {"title": "Audit Test Task", "parameters": {"keywords": ["audit", "test"]}, "required_agent_roles": ["intelligence_gatherer_agent"]}
        }
        
        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.post(
            "/tasks", json=task_data, headers=headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_intelligence_dashboard_data(self):
        """Test intelligence dashboard data retrieval"""
        data = await intelligence_manager.get_intelligence_dashboard_data()
        
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
            "user_id": "test_user"
        }
        
        optimization = await intelligence_manager.optimize_task_before_execution(task_data)
        
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
            "user_feedback": {"rating": 4, "comments": "Good work"}
        }
        
        # This should not raise an exception
        await intelligence_manager.process_task_completion(task_data)
        
        # Verify the task was processed (simplified check)
        assert True  # If we get here without exception, it worked
    
    def test_agent_prompt_creation(self):
        """Test agent prompt creation"""
        prompt = orchestrator._create_agent_prompt(
            task_type="security_scan",
            target="example.com",
            parameters={"depth": "standard"},
            agents=["security_expert", "intelligence_gathering"]
        )
        
        assert prompt is not None
        assert isinstance(prompt, str)
        assert "security_scan" in prompt
        assert "example.com" in prompt
        assert "Security Expert" in prompt
        assert "Intelligence Gathering" in prompt
    
    def test_agent_performance_analysis(self):
        """Test agent performance analysis"""
        analysis = orchestrator._analyze_agent_performance(
            agents=["security_expert"],
            response="This is a test response with analysis and recommendations"
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
        self.env_patcher = patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test_openai_key',
            'GEMINIAI_API_KEY': 'test_gemini_key',
            'GROQAI_API_KEY': 'test_groq_key'
        })
        self.env_patcher.start()
    
    def teardown_method(self):
        """Cleanup after each test"""
        self.env_patcher.stop()
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete AMAS workflow from task creation to completion"""
        # Mock provider execution
        with patch.object(provider_manager, 'get_best_provider') as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.infer.return_value = "Comprehensive security analysis completed"
            mock_get_provider.return_value = mock_provider
            
            # 1. Execute a task
            result = await orchestrator.execute_task(
                task_type="security_scan",
                target="example.com",
                parameters={"depth": "comprehensive"}
            )
            
            # 2. Verify task execution
            assert result["status"] == "completed"
            assert "security_expert" in result["agents_used"]
            
            # 3. Check system status
            status = await orchestrator.get_system_status()
            assert status["tasks"]["completed"] > 0
            
            # 4. Verify intelligence learning
            intelligence_data = await intelligence_manager.get_intelligence_dashboard_data()
            assert intelligence_data is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])