"""
Test API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestAPIEndpoints:
    """Test API endpoint functionality"""
    
    def test_root_endpoint(self, async_test_client):
        """Test root endpoint"""
        response = async_test_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "AMAS - Advanced Multi-Agent Intelligence System"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    def test_health_endpoint(self, async_test_client):
        """Test health endpoint"""
        response = async_test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data
    
    def test_ready_endpoint(self, async_test_client):
        """Test ready endpoint"""
        response = async_test_client.get("/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
    
    def test_agents_list_endpoint(self, async_test_client):
        """Test agents list endpoint"""
        response = async_test_client.get("/api/v1/agents")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if data:  # If there are agents
            agent = data[0]
            assert "id" in agent
            assert "name" in agent
            assert "type" in agent
            assert "status" in agent
    
    def test_agents_create_endpoint(self, async_test_client):
        """Test agent creation endpoint"""
        agent_data = {
            "name": "Test Agent",
            "type": "research",
            "capabilities": ["web_search", "data_analysis"],
            "config": {"model": "gpt-4", "temperature": 0.7}
        }
        
        response = async_test_client.post("/api/v1/agents", json=agent_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == agent_data["name"]
        assert data["type"] == agent_data["type"]
        assert data["capabilities"] == agent_data["capabilities"]
    
    def test_tasks_list_endpoint(self, async_test_client):
        """Test tasks list endpoint"""
        response = async_test_client.get("/api/v1/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if data:  # If there are tasks
            task = data[0]
            assert "id" in task
            assert "agent_id" in task
            assert "description" in task
            assert "status" in task
    
    def test_tasks_create_endpoint(self, async_test_client):
        """Test task creation endpoint"""
        task_data = {
            "agent_id": "agent-1",
            "description": "Test task",
            "priority": "high",
            "config": {"timeout": 300}
        }
        
        response = async_test_client.post("/api/v1/tasks", json=task_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_id"] == task_data["agent_id"]
        assert data["description"] == task_data["description"]
        assert data["priority"] == task_data["priority"]
    
    def test_users_list_endpoint(self, async_test_client):
        """Test users list endpoint"""
        response = async_test_client.get("/api/v1/users")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if data:  # If there are users
            user = data[0]
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "role" in user
    
    def test_users_create_endpoint(self, async_test_client):
        """Test user creation endpoint"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "role": "user"
        }
        
        response = async_test_client.post("/api/v1/users", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["role"] == user_data["role"]
    
    def test_api_documentation_endpoint(self, async_test_client):
        """Test API documentation endpoint"""
        response = async_test_client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_endpoint(self, async_test_client):
        """Test ReDoc endpoint"""
        response = async_test_client.get("/redoc")
        assert response.status_code == 200
    
    def test_cors_headers(self, async_test_client):
        """Test CORS headers"""
        response = async_test_client.options("/api/v1/agents")
        assert response.status_code == 200
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_security_headers(self, async_test_client):
        """Test security headers"""
        response = async_test_client.get("/")
        assert response.status_code == 200
        
        # Check security headers
        assert response.headers.get("x-frame-options") == "DENY"
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-xss-protection") == "1; mode=block"
        assert "strict-transport-security" in response.headers.get("strict-transport-security", "").lower()
    
    def test_error_handling(self, async_test_client):
        """Test error handling"""
        # Test 404 error
        response = async_test_client.get("/nonexistent")
        assert response.status_code == 404
        
        # Test invalid JSON
        response = async_test_client.post("/api/v1/agents", data="invalid json")
        assert response.status_code == 422
    
    def test_pagination(self, async_test_client):
        """Test pagination parameters"""
        response = async_test_client.get("/api/v1/agents?skip=0&limit=10")
        assert response.status_code == 200
        
        response = async_test_client.get("/api/v1/agents?skip=10&limit=5")
        assert response.status_code == 200
    
    def test_filtering(self, async_test_client):
        """Test filtering parameters"""
        response = async_test_client.get("/api/v1/agents?status=active")
        assert response.status_code == 200
        
        response = async_test_client.get("/api/v1/tasks?agent_id=agent-1")
        assert response.status_code == 200
        
        response = async_test_client.get("/api/v1/users?role=admin")
        assert response.status_code == 200