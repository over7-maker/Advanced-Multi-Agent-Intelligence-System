"""
Test API endpoints
"""
import pytest
import asyncio
import httpx
from typing import Dict, Any


class TestAPIEndpoints:
    """Test FastAPI endpoints"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, test_client: httpx.AsyncClient):
        """Test health check endpoint"""
        response = await test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

    @pytest.mark.asyncio
    async def test_system_status_endpoint(self, test_client: httpx.AsyncClient):
        """Test system status endpoint"""
        response = await test_client.get("/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'active'
        assert 'orchestrator_status' in data
        assert 'active_agents' in data

    @pytest.mark.asyncio
    async def test_submit_task_endpoint(self, test_client: httpx.AsyncClient, sample_task: Dict[str, Any]):
        """Test task submission endpoint"""
        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.post("/tasks", json=sample_task, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert 'task_id' in data
        assert 'status' in data

    @pytest.mark.asyncio
    async def test_get_task_status_endpoint(self, test_client: httpx.AsyncClient, sample_task: Dict[str, Any]):
        """Test get task status endpoint"""
        headers = {"Authorization": "Bearer valid_token"}
        
        # First submit a task
        submit_response = await test_client.post("/tasks", json=sample_task, headers=headers)
        task_id = submit_response.json()['task_id']
        
        # Then get task status
        response = await test_client.get(f"/tasks/{task_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data['task_id'] == task_id
        assert 'status' in data

    @pytest.mark.asyncio
    async def test_get_agents_endpoint(self, test_client: httpx.AsyncClient):
        """Test get agents endpoint"""
        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.get("/agents", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert 'agents' in data
        assert isinstance(data['agents'], list)
        assert len(data['agents']) > 0

    @pytest.mark.asyncio
    async def test_get_agent_status_endpoint(self, test_client: httpx.AsyncClient):
        """Test get agent status endpoint"""
        headers = {"Authorization": "Bearer valid_token"}
        
        # First get agents list
        agents_response = await test_client.get("/agents", headers=headers)
        agents = agents_response.json()['agents']
        agent_id = agents[0]['agent_id']
        
        # Then get specific agent status
        response = await test_client.get(f"/agents/{agent_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data['agent_id'] == agent_id
        assert 'status' in data

    @pytest.mark.asyncio
    async def test_execute_workflow_endpoint(self, test_client: httpx.AsyncClient, sample_workflow: Dict[str, Any]):
        """Test execute workflow endpoint"""
        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.post(
            f"/workflows/{sample_workflow['workflow_id']}/execute",
            json=sample_workflow['parameters'],
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'workflow_id' in data
        assert 'status' in data

    @pytest.mark.asyncio
    async def test_get_audit_log_endpoint(self, test_client: httpx.AsyncClient):
        """Test get audit log endpoint"""
        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.get("/audit", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert 'audit_log' in data
        assert isinstance(data['audit_log'], list)

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, test_client: httpx.AsyncClient, sample_task: Dict[str, Any]):
        """Test that unauthorized requests are rejected"""
        # Test without authorization header
        response = await test_client.post("/tasks", json=sample_task)
        assert response.status_code == 401
        
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = await test_client.post("/tasks", json=sample_task, headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_task_data(self, test_client: httpx.AsyncClient):
        """Test handling of invalid task data"""
        headers = {"Authorization": "Bearer valid_token"}
        invalid_task = {
            "type": "invalid_type",
            "description": "Invalid task"
            # Missing required fields
        }
        
        response = await test_client.post("/tasks", json=invalid_task, headers=headers)
        # Should handle gracefully (either 400 or process with defaults)
        assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_nonexistent_task(self, test_client: httpx.AsyncClient):
        """Test getting status of non-existent task"""
        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.get("/tasks/nonexistent_task_id", headers=headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_nonexistent_agent(self, test_client: httpx.AsyncClient):
        """Test getting status of non-existent agent"""
        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.get("/agents/nonexistent_agent_id", headers=headers)
        assert response.status_code == 404