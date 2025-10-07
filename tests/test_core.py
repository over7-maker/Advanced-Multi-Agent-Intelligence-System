"""
Test core AMAS functionality
"""

from typing import Any, Dict

import pytest

from amas.common.models import TaskPriority
from amas.main import AMASApplication


class TestAMASApplication:
    """Test AMAS application initialization and basic functionality"""

    @pytest.mark.asyncio
    async def test_application_initialization(self, amas_app: AMASApplication):
        """Test that AMAS application initializes correctly"""
        assert amas_app is not None
        assert amas_app.service_manager is not None
        assert amas_app.orchestrator is not None

    @pytest.mark.asyncio
    async def test_service_manager_initialization(
        self, amas_app: AMASApplication
    ):
        """Test that service manager initializes all services"""
        service_manager = amas_app.service_manager

        # Check that all services are initialized
        assert service_manager.llm_service is not None
        assert service_manager.vector_service is not None
        assert service_manager.knowledge_graph is not None
        assert service_manager.database_service is not None
        assert service_manager.security_service is not None

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(
        self, amas_app: AMASApplication
    ):
        """Test that orchestrator initializes with agents"""
        orchestrator = amas_app.orchestrator

        # Check that agents are registered
        agents = await orchestrator.list_agents()
        assert len(agents) > 0

        # Check for specific agent types
        agent_names = [agent["name"] for agent in agents]
        expected_agents = [
            "OSINT Agent",
            "Investigation Agent",
            "Forensics Agent",
            "Data Analysis Agent",
            "Reverse Engineering Agent",
            "Metadata Agent",
            "Reporting Agent",
            "Technology Monitor Agent",
        ]

        for expected_agent in expected_agents:
            assert expected_agent in agent_names

    @pytest.mark.asyncio
    async def test_health_check(self, amas_app: AMASApplication):
        """Test system health check"""
        health_status = await amas_app.health_check()

        assert health_status["status"] == "healthy"
        assert "services" in health_status
        assert "timestamp" in health_status

    @pytest.mark.asyncio
    async def test_system_status(self, amas_app: AMASApplication):
        """Test system status retrieval"""
        status = await amas_app.orchestrator.get_system_status()

        assert "orchestrator_status" in status
        assert "active_agents" in status
        assert status["orchestrator_status"] == "active"


class TestOrchestrator:
    """Test orchestrator functionality"""

    @pytest.mark.asyncio
    async def test_task_submission(
        self, amas_app: AMASApplication, sample_task: Dict[str, Any]
    ):
        """Test task submission to orchestrator"""
        orchestrator = amas_app.orchestrator

        task_id = await orchestrator.submit_task(
            description=sample_task["description"],
            task_type=sample_task["task_type"],
            priority=TaskPriority(sample_task["priority"]),
            metadata=sample_task["metadata"],
        )


        assert task_id is not None
        assert isinstance(task_id, str)

    @pytest.mark.asyncio
    async def test_task_status(
        self, amas_app: AMASApplication, sample_task: Dict[str, Any]
    ):
        """Test task status retrieval"""
        orchestrator = amas_app.orchestrator
        # Submit a task
        task_id = await orchestrator.submit_task(
            description=sample_task["description"],
            task_type=sample_task["task_type"],
            priority=TaskPriority(sample_task["priority"]),
            metadata=sample_task["metadata"],
        )



        # Get task status
        status = await orchestrator.get_task_status(task_id)
        assert status is not None
        assert "task_id" in status
        assert "status" in status
        assert status["task_id"] == task_id

    @pytest.mark.asyncio
    async def test_agent_listing(self, amas_app: AMASApplication):
        """Test agent listing"""
        orchestrator = amas_app.orchestrator

        agents = await orchestrator.list_agents()
        assert isinstance(agents, list)
        assert len(agents) > 0

        # Check agent structure
        for agent in agents:
            assert "agent_id" in agent
            assert "name" in agent
            assert "capabilities" in agent
            assert "status" in agent

    @pytest.mark.asyncio
    async def test_agent_status(self, amas_app: AMASApplication):
        """Test individual agent status"""
        orchestrator = amas_app.orchestrator

        # Get first agent
        agents = await orchestrator.list_agents()
        first_agent = agents[0]
        agent_id = first_agent["agent_id"]

        # Get agent status
        status = await orchestrator.get_agent_status(agent_id)
        assert status is not None
        assert "agent_id" in status
        assert "status" in status


class TestServiceManager:
    """Test service manager functionality"""

    @pytest.mark.asyncio
    async def test_service_health_checks(self, amas_app: AMASApplication):
        """Test health checks for all services"""
        service_manager = amas_app.service_manager

        health_status = await service_manager.health_check_all_services()

        assert "llm" in health_status
        assert "vector" in health_status
        assert "knowledge_graph" in health_status
        assert "database" in health_status
        assert "security" in health_status

    @pytest.mark.asyncio
    async def test_service_getters(self, amas_app: AMASApplication):
        """Test service getter methods"""
        service_manager = amas_app.service_manager

        # Test all getter methods
        llm_service = service_manager.get_llm_service()
        vector_service = service_manager.get_vector_service()
        knowledge_graph = service_manager.get_knowledge_graph()
        database_service = service_manager.get_database_service()
        security_service = service_manager.get_security_service()

        assert llm_service is not None
        assert vector_service is not None
        assert knowledge_graph is not None
        assert database_service is not None
        assert security_service is not None
