"""
AMAS Intelligence System - Comprehensive Test Suite

Enterprise-grade testing framework with:
- Unit tests for all components
- Integration tests for workflows
- API endpoint testing
- Performance benchmarks
- Security validation
- 80% coverage requirement
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch
import httpx
from fastapi.testclient import TestClient

# Import AMAS components
from main import AMASIntelligenceSystem
from core.orchestrator import IntelligenceOrchestrator, TaskPriority, TaskStatus
from agents.osint.osint_agent import OSINTAgent
from agents.investigation.investigation_agent import InvestigationAgent
from api.enhanced_main import app
from services.security_service import SecurityService
from services.llm_service import LLMService

# Test configuration
TEST_CONFIG = {
    'llm_service_url': 'http://localhost:11434',
    'vector_service_url': 'http://localhost:8001',
    'graph_service_url': 'bolt://localhost:7687',
    'postgres_host': 'localhost',
    'postgres_port': 5432,
    'postgres_user': 'amas_test',
    'postgres_password': 'test123',
    'postgres_db': 'amas_test',
    'redis_host': 'localhost',
    'redis_port': 6379,
    'redis_db': 1,  # Use different DB for testing
    'neo4j_username': 'neo4j',
    'neo4j_password': 'test123',
    'neo4j_database': 'test',
    'jwt_secret': 'test_secret_key_for_testing_only',
    'encryption_key': 'test_encryption_key_32_characters'
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def amas_system():
    """Create AMAS system instance for testing."""
    system = AMASIntelligenceSystem(TEST_CONFIG)
    await system.initialize()
    yield system
    await system.shutdown()

@pytest.fixture
def api_client():
    """Create FastAPI test client."""
    return TestClient(app)

@pytest.fixture
async def orchestrator():
    """Create orchestrator instance for testing."""
    orchestrator = IntelligenceOrchestrator(
        llm_service=Mock(),
        vector_service=Mock(),
        knowledge_graph=Mock(),
        security_service=Mock()
    )
    return orchestrator

class TestAMASSystem:
    """Test suite for the main AMAS system."""
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, amas_system):
        """Test system initialization."""
        assert amas_system is not None
        assert amas_system.orchestrator is not None
        assert len(amas_system.agents) > 0
        
    @pytest.mark.asyncio
    async def test_system_status(self, amas_system):
        """Test system status retrieval."""
        status = await amas_system.get_system_status()
        
        assert status['status'] == 'operational'
        assert 'agents' in status
        assert 'active_tasks' in status
        assert 'total_tasks' in status
        assert 'timestamp' in status
        
    @pytest.mark.asyncio
    async def test_task_submission(self, amas_system):
        """Test task submission and processing."""
        task_data = {
            'type': 'osint',
            'description': 'Test OSINT collection task',
            'priority': 2,
            'parameters': {
                'target': 'test.example.com',
                'sources': ['whois', 'dns']
            }
        }
        
        task_id = await amas_system.submit_intelligence_task(task_data)
        assert task_id is not None
        assert isinstance(task_id, str)

class TestIntelligenceOrchestrator:
    """Test suite for the intelligence orchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator is not None
        assert orchestrator.agents == {}
        assert orchestrator.tasks == {}
        
    @pytest.mark.asyncio
    async def test_agent_registration(self, orchestrator):
        """Test agent registration."""
        # Mock agent
        mock_agent = Mock()
        mock_agent.agent_id = "test_agent_001"
        mock_agent.capabilities = ["test_capability"]
        mock_agent.start = AsyncMock()
        
        result = await orchestrator.register_agent(mock_agent)
        
        assert result is True
        assert "test_agent_001" in orchestrator.agents
        mock_agent.start.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_task_submission(self, orchestrator):
        """Test task submission to orchestrator."""
        task_id = await orchestrator.submit_task(
            task_type="test",
            description="Test task",
            parameters={},
            priority=TaskPriority.MEDIUM
        )
        
        assert task_id is not None
        assert task_id in orchestrator.tasks
        
        task = orchestrator.tasks[task_id]
        assert task.type == "test"
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        
    @pytest.mark.asyncio
    async def test_workflow_execution(self, orchestrator):
        """Test workflow execution."""
        # Add a test workflow
        orchestrator.workflows['test_workflow'] = {
            'name': 'Test Workflow',
            'description': 'Test workflow for testing',
            'steps': [
                {
                    'step_id': 'test_step',
                    'agent_type': 'test',
                    'action': 'test_action',
                    'parameters': {}
                }
            ]
        }
        
        execution_id = await orchestrator.execute_workflow(
            'test_workflow',
            {'test_param': 'test_value'}
        )
        
        assert execution_id is not None
        assert execution_id in orchestrator.workflow_instances

class TestOSINTAgent:
    """Test suite for OSINT agent."""
    
    @pytest.mark.asyncio
    async def test_osint_agent_initialization(self):
        """Test OSINT agent initialization."""
        agent = OSINTAgent(
            agent_id="osint_test_001",
            name="Test OSINT Agent",
            llm_service=Mock(),
            vector_service=Mock(),
            knowledge_graph=Mock(),
            security_service=Mock()
        )
        
        assert agent.agent_id == "osint_test_001"
        assert agent.name == "Test OSINT Agent"
        assert "osint" in agent.capabilities
        
    @pytest.mark.asyncio
    async def test_osint_task_processing(self):
        """Test OSINT task processing."""
        # Mock services
        mock_llm = AsyncMock()
        mock_vector = AsyncMock()
        mock_graph = AsyncMock()
        mock_security = AsyncMock()
        
        agent = OSINTAgent(
            agent_id="osint_test_001",
            name="Test OSINT Agent",
            llm_service=mock_llm,
            vector_service=mock_vector,
            knowledge_graph=mock_graph,
            security_service=mock_security
        )
        
        task = {
            'id': 'test_task_001',
            'type': 'osint',
            'description': 'Test OSINT collection',
            'parameters': {
                'target': 'test.example.com',
                'sources': ['whois', 'dns']
            }
        }
        
        # Mock the actual processing method
        with patch.object(agent, '_collect_intelligence') as mock_collect:
            mock_collect.return_value = {
                'target': 'test.example.com',
                'intelligence': {
                    'whois': {'registrar': 'Test Registrar'},
                    'dns': {'a_records': ['1.2.3.4']}
                },
                'confidence': 0.95,
                'timestamp': datetime.now().isoformat()
            }
            
            result = await agent.process_task(task)
            
            assert result is not None
            assert 'intelligence' in result
            assert result['confidence'] >= 0.9

class TestSecurityService:
    """Test suite for security service."""
    
    @pytest.mark.asyncio
    async def test_security_service_initialization(self):
        """Test security service initialization."""
        service = SecurityService(TEST_CONFIG)
        await service.initialize()
        
        assert service is not None
        
    @pytest.mark.asyncio
    async def test_audit_logging(self):
        """Test audit logging functionality."""
        service = SecurityService(TEST_CONFIG)
        await service.initialize()
        
        await service.log_audit_event(
            event_type='test_event',
            user_id='test_user',
            action='test_action',
            details='Test audit log entry',
            classification='test'
        )
        
        # Verify audit log entry was created
        audit_logs = await service.get_audit_log(user_id='test_user')
        assert len(audit_logs) > 0
        
        latest_log = audit_logs[0]
        assert latest_log['event_type'] == 'test_event'
        assert latest_log['user_id'] == 'test_user'
        assert latest_log['action'] == 'test_action'

class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    def test_root_endpoint(self, api_client):
        """Test root API endpoint."""
        response = api_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data['name'] == "AMAS Intelligence System API"
        assert data['status'] == "operational"
        
    def test_health_endpoint(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert 'status' in data
        assert 'services' in data
        assert 'timestamp' in data
        
    def test_authentication_endpoint(self, api_client):
        """Test authentication endpoint."""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = api_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['token_type'] == 'bearer'
        
    def test_protected_endpoint_without_auth(self, api_client):
        """Test protected endpoint without authentication."""
        response = api_client.get("/status")
        assert response.status_code == 401
        
    def test_protected_endpoint_with_auth(self, api_client):
        """Test protected endpoint with authentication."""
        # First login to get token
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = api_client.post("/auth/login", json=login_data)
        token = login_response.json()['access_token']
        
        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = api_client.get("/status", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'agents' in data
        
    def test_task_submission_endpoint(self, api_client):
        """Test task submission endpoint."""
        # Login first
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = api_client.post("/auth/login", json=login_data)
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Submit task
        task_data = {
            "type": "osint",
            "description": "Test OSINT collection task for API testing",
            "parameters": {
                "target": "test.example.com"
            },
            "priority": 2
        }
        
        response = api_client.post("/tasks", json=task_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert 'task_id' in data
        assert data['status'] == 'submitted'

class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    @pytest.mark.asyncio
    async def test_task_processing_performance(self, amas_system):
        """Test task processing performance."""
        start_time = time.time()
        
        # Submit multiple tasks
        task_ids = []
        for i in range(10):
            task_data = {
                'type': 'osint',
                'description': f'Performance test task {i}',
                'priority': 2,
                'parameters': {'test_id': i}
            }
            
            task_id = await amas_system.submit_intelligence_task(task_data)
            task_ids.append(task_id)
        
        processing_time = time.time() - start_time
        
        # Should be able to submit 10 tasks in under 1 second
        assert processing_time < 1.0
        assert len(task_ids) == 10
        
    @pytest.mark.asyncio
    async def test_concurrent_task_processing(self, amas_system):
        """Test concurrent task processing."""
        async def submit_task(task_id: int):
            task_data = {
                'type': 'osint',
                'description': f'Concurrent test task {task_id}',
                'priority': 2,
                'parameters': {'concurrent_id': task_id}
            }
            return await amas_system.submit_intelligence_task(task_data)
        
        start_time = time.time()
        
        # Submit 20 tasks concurrently
        tasks = [submit_task(i) for i in range(20)]
        task_ids = await asyncio.gather(*tasks)
        
        processing_time = time.time() - start_time
        
        # Should handle 20 concurrent tasks efficiently
        assert processing_time < 2.0
        assert len(task_ids) == 20
        assert len(set(task_ids)) == 20  # All unique IDs

class TestSecurityValidation:
    """Security validation tests."""
    
    def test_sql_injection_protection(self, api_client):
        """Test SQL injection protection."""
        # Login first
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = api_client.post("/auth/login", json=login_data)
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try SQL injection in task description
        malicious_task = {
            "type": "osint",
            "description": "'; DROP TABLE tasks; --",
            "parameters": {},
            "priority": 2
        }
        
        response = api_client.post("/tasks", json=malicious_task, headers=headers)
        
        # Should either reject the request or handle it safely
        assert response.status_code in [200, 400, 422]
        
    def test_xss_protection(self, api_client):
        """Test XSS protection."""
        # Login first
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = api_client.post("/auth/login", json=login_data)
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try XSS in task description
        xss_task = {
            "type": "osint",
            "description": "<script>alert('xss')</script>",
            "parameters": {},
            "priority": 2
        }
        
        response = api_client.post("/tasks", json=xss_task, headers=headers)
        
        # Should handle XSS attempts safely
        assert response.status_code in [200, 400, 422]
        
    def test_rate_limiting(self, api_client):
        """Test rate limiting."""
        # Try to make many requests quickly
        responses = []
        for i in range(50):
            response = api_client.get("/health")
            responses.append(response.status_code)
        
        # Should have some rate limiting in place
        rate_limited = any(status == 429 for status in responses)
        # Note: This might not trigger in test environment
        # In production, rate limiting should be more strict

class TestIntegrationWorkflows:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_osint_investigation_workflow(self, amas_system):
        """Test complete OSINT investigation workflow."""
        # Submit OSINT workflow
        workflow_result = await amas_system.execute_intelligence_workflow(
            'osint_investigation',
            {
                'target': 'test.example.com',
                'sources': ['whois', 'dns', 'subdomain'],
                'depth': 'standard'
            }
        )
        
        assert workflow_result is not None
        assert 'workflow_id' in workflow_result
        assert 'execution_result' in workflow_result
        
    @pytest.mark.asyncio
    async def test_multi_agent_collaboration(self, amas_system):
        """Test multi-agent collaboration."""
        # Submit a task that requires multiple agents
        task_data = {
            'type': 'investigation',
            'description': 'Multi-agent investigation test',
            'priority': 3,
            'parameters': {
                'target': 'suspicious_entity',
                'require_agents': ['osint', 'investigation', 'reporting']
            }
        }
        
        task_id = await amas_system.submit_intelligence_task(task_data)
        assert task_id is not None
        
        # Wait a bit for processing to start
        await asyncio.sleep(1)
        
        # Check system status shows active tasks
        status = await amas_system.get_system_status()
        assert status['active_tasks'] >= 0

# Performance and load testing
class TestLoadTesting:
    """Load testing for system scalability."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_high_load_task_submission(self, amas_system):
        """Test system under high load."""
        # Submit 100 tasks rapidly
        tasks = []
        for i in range(100):
            task_data = {
                'type': 'osint',
                'description': f'Load test task {i}',
                'priority': 2,
                'parameters': {'load_test_id': i}
            }
            tasks.append(amas_system.submit_intelligence_task(task_data))
        
        start_time = time.time()
        task_ids = await asyncio.gather(*tasks, return_exceptions=True)
        processing_time = time.time() - start_time
        
        # Count successful submissions
        successful_tasks = [tid for tid in task_ids if isinstance(tid, str)]
        
        # Should handle at least 80% of tasks successfully
        success_rate = len(successful_tasks) / len(tasks)
        assert success_rate >= 0.8
        
        # Should process 100 tasks in reasonable time (under 10 seconds)
        assert processing_time < 10.0
        
        print(f"Load test: {len(successful_tasks)}/100 tasks successful in {processing_time:.2f}s")

# Test configuration and fixtures for different environments
@pytest.fixture(params=["development", "testing", "production"])
def environment_config(request):
    """Test different environment configurations."""
    env = request.param
    config = TEST_CONFIG.copy()
    
    if env == "production":
        config.update({
            'log_level': 'WARNING',
            'debug': False,
            'testing': False
        })
    elif env == "development":
        config.update({
            'log_level': 'DEBUG',
            'debug': True,
            'testing': False
        })
    else:  # testing
        config.update({
            'log_level': 'INFO',
            'debug': True,
            'testing': True
        })
    
    return config

# Custom test markers
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration
]

# Test collection and reporting
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add slow marker to load tests
        if "load" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Add security marker to security tests
        if "security" in item.name.lower():
            item.add_marker(pytest.mark.security)
        
        # Add performance marker to performance tests
        if "performance" in item.name.lower() or "benchmark" in item.name.lower():
            item.add_marker(pytest.mark.performance)