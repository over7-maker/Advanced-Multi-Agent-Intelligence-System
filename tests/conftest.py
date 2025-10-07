
import pytest
import asyncio
from unittest.mock import AsyncMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from amas.core.message_bus import MessageBus
from amas.core.unified_orchestrator_v2 import UnifiedOrchestratorV2
from amas.services.service_manager import ServiceManager
from amas.services.universal_ai_manager import UniversalAIManager
from amas.agents.base.intelligence_agent import IntelligenceAgent
from amas.agents.rag_agent import RAGAgent
from amas.agents.tool_agent import ToolAgent
from amas.agents.planning_agent import PlanningAgent
from amas.agents.code_agent import CodeAgent
from amas.agents.data_agent import DataAgent
from amas.core.unified_orchestrator_v2 import OrchestratorTask, TaskStatus
from amas.common.models import TaskPriority

@pytest.fixture(scope="session")
def event_loop():
    """Provide an event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_message_bus():
    """Mock MessageBus instance."""
    mock_bus = AsyncMock(spec=MessageBus)
    mock_bus.publish.return_value = None
    mock_bus.subscribe.return_value = None
    mock_bus.unregister_agent.return_value = None
    mock_bus.register_agent.return_value = None
    mock_bus.send_direct_message.return_value = None
    return mock_bus

@pytest.fixture
def mock_universal_ai_manager():
    """Mock UniversalAIManager instance."""
    mock_manager = AsyncMock(spec=UniversalAIManager)
    mock_manager.initialize = AsyncMock()
    mock_manager.generate_response.return_value = {"success": True, "content": "Mocked AI response", "tokens_used": 10}
    mock_manager.get_status.return_value = {"status": "healthy"}
    return mock_manager

@pytest.fixture
def mock_vector_service():
    """
    Mock VectorService instance.
    """
    mock_service = AsyncMock()
    mock_service.is_initialized = True
    mock_service.semantic_search.return_value = []
    mock_service.keyword_search.return_value = []
    mock_service.hybrid_search.return_value = []
    return mock_service

@pytest.fixture
def mock_knowledge_graph_service():
    """
    Mock KnowledgeGraphService instance.
    """
    mock_service = AsyncMock()
    mock_service.is_initialized = True
    mock_service.query_graph.return_value = []
    return mock_service

@pytest.fixture
def mock_service_manager(mock_vector_service, mock_knowledge_graph_service):
    """
    Mock ServiceManager instance.
    """
    mock_manager = AsyncMock(spec=ServiceManager)
    mock_manager.initialize = AsyncMock()
    mock_manager.initialize.return_value = None
    mock_manager.shutdown.return_value = None
    mock_manager.get_vector_service.return_value = mock_vector_service
    mock_manager.get_knowledge_graph_service.return_value = mock_knowledge_graph_service
    return mock_manager

@pytest.fixture
async def mock_orchestrator(mock_universal_ai_manager, mock_service_manager, mock_message_bus):



    """
    Mock UnifiedOrchestratorV2 instance with mocked dependencies.
    """
    orchestrator = UnifiedOrchestratorV2(
        universal_ai_manager=mock_universal_ai_manager,
        vector_service=mock_service_manager.get_vector_service(),
        knowledge_graph=mock_service_manager.get_knowledge_graph_service(),
    )
    orchestrator.message_bus = mock_message_bus
    orchestrator._subscribe_to_feedback = AsyncMock(return_value=None) # Mock this to prevent actual subscription during tests
    return orchestrator

@pytest.fixture
def agent_config():
    """Default agent configuration."""
    return {
        "name": "Test Agent",
        "capabilities": ["test_capability"],
        "initial_llm_temperature": 0.7,
        "initial_llm_max_tokens": 1000
    }

@pytest.fixture
def mock_task():
    """Mock OrchestratorTask instance."""
    return OrchestratorTask(
        id="test_task_123",
        description="A task for testing purposes.",
        task_type="general",
        priority=TaskPriority.MEDIUM,
        metadata={"title": "Test Task", "parameters": {"input": "sample data"}}
    )


@pytest.fixture
async def rag_agent(mock_orchestrator, mock_message_bus, agent_config):
    orchestrator = await mock_orchestrator
    """RAGAgent instance for testing."""
    agent = RAGAgent("rag_agent_001", agent_config, orchestrator, mock_message_bus)

    return agent

@pytest.fixture
async def tool_agent(mock_orchestrator, mock_message_bus, agent_config):
    orchestrator = await mock_orchestrator
    """ToolAgent instance for testing."""
    agent = ToolAgent("tool_agent_001", agent_config, orchestrator, mock_message_bus)

    return agent

@pytest.fixture
async def planning_agent(mock_orchestrator, mock_message_bus, agent_config):
    orchestrator = await mock_orchestrator
    """PlanningAgent instance for testing."""
    agent = PlanningAgent("planning_agent_001", agent_config, orchestrator, mock_message_bus)

    return agent

@pytest.fixture
async def code_agent(mock_orchestrator, mock_message_bus, agent_config):
    orchestrator = await mock_orchestrator
    """CodeAgent instance for testing."""
    agent = CodeAgent("code_agent_001", agent_config, orchestrator, mock_message_bus)
    return agent

@pytest.fixture
async def data_agent(mock_orchestrator, mock_message_bus, agent_config):
    orchestrator = await mock_orchestrator
    """DataAgent instance for testing."""
    agent = DataAgent("data_agent_001", agent_config, orchestrator, mock_message_bus)

    return agent



@pytest.fixture
def sample_task():
    """Sample task data for API tests."""
    return {
        "description": "Analyze sales data for Q3",
        "task_type": "data_analysis",
        "priority": "HIGH",
        "metadata": {
            "title": "Sales Data Analysis",
            "required_agent_roles": ["data_agent"],
            "parameters": {"quarter": "Q3", "year": 2025}
        }
    }

@pytest.fixture
def sample_workflow():
    """Sample workflow data for API tests."""
    return {
        "workflow_id": "test_workflow_1",
        "parameters": {"input_data": "some_data", "analysis_type": "financial"}
    }

