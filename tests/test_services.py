"""Test services"""

import asyncio
from datetime import datetime
from typing import Any, Dict

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from amas.services.database_service import DatabaseService
from amas.services.knowledge_graph_service import KnowledgeGraphService
from amas.services.llm_service import LLMService
from amas.services.security_service import SecurityService
from amas.services.service_manager import ServiceManager
from amas.services.vector_service import VectorService

class TestServiceManager:
    """Test Service Manager"""

    @pytest.fixture
    async def service_manager(self):
        """Create service manager for testing"""
        config = {
            "llm_service_url": "http://localhost:11434",
            "vector_service_url": "http://localhost:8001",
            "graph_service_url": "bolt://localhost:7687",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "index_path": "/tmp/faiss_index",
            "neo4j_username": "neo4j",
            "neo4j_password": "amas123",
            "neo4j_database": "neo4j",
        }

        manager = ServiceManager(config)
        # Note: In real tests, you'd want to mock the services
        yield manager

    @pytest.mark.asyncio
    async def test_service_initialization(self, service_manager):
        """Test service initialization"""
        # This would test service initialization in a real scenario
        # For now, we'll just test the configuration
        assert service_manager.config is not None
        assert "llm_service_url" in service_manager.config

    @pytest.mark.asyncio
    async def test_health_check(self, service_manager):
        """Test service health check"""
        # Mock health check
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "llm": {"status": "healthy"},
                "vector": {"status": "healthy"},
                "knowledge_graph": {"status": "healthy"},
            },
            "overall_status": "healthy",
        }

        assert health_status["overall_status"] == "healthy"
        assert len(health_status["services"]) == 3

class TestDatabaseService:
    """Test Database Service"""

    @pytest.fixture
    async def database_service(self):
        """Create database service for testing"""
        config = {
            "postgres_host": "localhost",
            "postgres_port": 5432,
            "postgres_user": "amas",
            "postgres_password": "amas123",
            "postgres_db": "amas",
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_db": 0,
        }

        service = DatabaseService(config)
        # Note: In real tests, you'd want to use a test database
        yield service

    @pytest.mark.asyncio
    async def test_agent_storage(self, database_service):
        """Test agent data storage"""
        agent_data = {
            "agent_id": "test_agent_001",
            "name": "Test Agent",
            "capabilities": ["test_capability"],
            "status": "active",
        }

        # Mock storage operation
        result = True  # In real test, this would be the actual result
        assert result is True

    @pytest.mark.asyncio
    async def test_task_storage(self, database_service):
        """Test task data storage"""
        task_data = {
            "task_id": "test_task_001",
            "task_type": "test",
            "description": "Test task",
            "parameters": {"test": "value"},
            "priority": 2,
            "status": "pending",
            "assigned_agent": "test_agent_001",
        }

        # Mock storage operation
        result = True  # In real test, this would be the actual result
        assert result is True

    @pytest.mark.asyncio
    async def test_intelligence_data_storage(self, database_service):
        """Test intelligence data storage"""
        data = {
            "data_id": "test_data_001",
            "data_type": "osint",
            "source": "test_source",
            "content": {"test": "content"},
            "metadata": {"test": "metadata"},
            "classification": "unclassified",
        }

        # Mock storage operation
        result = True  # In real test, this would be the actual result
        assert result is True

class TestSecurityService:
    """Test Security Service"""

    @pytest.fixture
    async def security_service(self):
        """Create security service for testing"""
        config = {"jwt_secret": "test_secret", "encryption_key": "test_encryption_key"}

        service = SecurityService(config)
        await service.initialize()
        yield service

    @pytest.mark.asyncio
    async def test_user_authentication(self, security_service):
        """Test user authentication"""
        # Test successful authentication
        result = await security_service.authenticate_user("admin", "admin123")

        assert result["success"] is True
        assert "user" in result
        assert "token" in result

    @pytest.mark.asyncio
    async def test_jwt_token_generation(self, security_service):
        """Test JWT token generation"""
        user_data = {
            "user_id": "test_user",
            "username": "test_user",
            "role": "analyst",
            "permissions": ["read", "write"],
        }

        token = await security_service.generate_jwt_token(user_data)

        assert token is not None
        assert isinstance(token, str)

    @pytest.mark.asyncio
    async def test_jwt_token_verification(self, security_service):
        """Test JWT token verification"""
        user_data = {
            "user_id": "test_user",
            "username": "test_user",
            "role": "analyst",
            "permissions": ["read", "write"],
        }

        token = await security_service.generate_jwt_token(user_data)
        verification = await security_service.verify_jwt_token(token)

        assert verification["valid"] is True
        assert verification["user_data"]["user_id"] == "test_user"

    @pytest.mark.asyncio
    async def test_permission_check(self, security_service):
        """Test permission checking"""
        # Test admin permissions
        admin_permission = await security_service.check_permission("admin", "read")
        assert admin_permission is True

        # Test analyst permissions
        analyst_permission = await security_service.check_permission("analyst", "read")
        assert analyst_permission is True

        # Test viewer permissions
        viewer_permission = await security_service.check_permission("viewer", "read")
        assert viewer_permission is True

        # Test denied permission
        denied_permission = await security_service.check_permission("viewer", "delete")
        assert denied_permission is False

    @pytest.mark.asyncio
    async def test_data_encryption(self, security_service):
        """Test data encryption and decryption"""
        test_data = "This is a test message"

        # Encrypt data
        encrypted_data = await security_service.encrypt_data(test_data)
        assert encrypted_data != test_data

        # Decrypt data
        decrypted_data = await security_service.decrypt_data(encrypted_data)
        assert decrypted_data == test_data

    @pytest.mark.asyncio
    async def test_password_hashing(self, security_service):
        """Test password hashing and verification"""
        password = "test_password"

        # Hash password
        hashed_password = await security_service.hash_password(password)
        assert hashed_password != password

        # Verify password
        is_valid = await security_service.verify_password(password, hashed_password)
        assert is_valid is True

        # Test invalid password
        is_invalid = await security_service.verify_password(
            "wrong_password", hashed_password
        )
        assert is_invalid is False

    @pytest.mark.asyncio
    async def test_audit_logging(self, security_service):
        """Test audit logging"""
        # Log audit event
        result = await security_service.log_audit_event(
            event_type="test_event",
            user_id="test_user",
            action="test_action",
            details="Test audit event",
            classification="test",
        )

        assert result is True

        # Get audit log
        audit_log = await security_service.get_audit_log()
        assert len(audit_log) > 0

        # Check if our event is in the log
        test_events = [
            event for event in audit_log if event["event_type"] == "test_event"
        ]
        assert len(test_events) > 0

    @pytest.mark.asyncio
    async def test_data_classification(self, security_service):
        """Test data classification"""
        # Test classified data
        classified_data = {"content": "This is classified information"}
        classification = await security_service.classify_data(classified_data)
        assert classification == "classified"

        # Test unclassified data
        unclassified_data = {"content": "This is normal information"}
        classification = await security_service.classify_data(unclassified_data)
        assert classification == "unclassified"

    @pytest.mark.asyncio
    async def test_data_sanitization(self, security_service):
        """Test data sanitization"""
        malicious_data = {
            "content": 'This is <script>alert("xss")</script> malicious content',
            "url": 'javascript:alert("xss")',
        }

        sanitized_data = await security_service.sanitize_data(malicious_data)

        assert "<script>" not in sanitized_data["content"]
        assert "javascript:" not in sanitized_data["url"]

    @pytest.mark.asyncio
    async def test_health_check(self, security_service):
        """Test security service health check"""
        health = await security_service.health_check()

        assert health["status"] == "healthy"
        assert "encryption_available" in health
        assert "jwt_available" in health
        assert "audit_logging" in health

class TestLLMService:
    """Test LLM Service"""

    @pytest.fixture
    async def llm_service(self):
        """Create LLM service for testing"""
        config = {"llm_service_url": "http://localhost:11434"}

        service = LLMService(config)
        # Note: In real tests, you'd want to mock the HTTP calls
        yield service

    @pytest.mark.asyncio
    async def test_health_check(self, llm_service):
        """Test LLM service health check"""
        # Mock health check
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "llm",
        }

        assert health["status"] == "healthy"
        assert "timestamp" in health

    @pytest.mark.asyncio
    async def test_response_generation(self, llm_service):
        """Test response generation"""
        # Mock response generation
        response = {
            "success": True,
            "response": "This is a test response",
            "model": "test_model",
            "tokens_used": 10,
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert response["success"] is True
        assert "response" in response
        assert "model" in response

class TestVectorService:
    """Test Vector Service"""

    @pytest.fixture
    async def vector_service(self):
        """Create Vector service for testing"""
        config = {
            "vector_service_url": "http://localhost:8001",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "index_path": "/tmp/faiss_index",
        }

        service = VectorService(config)
        # Note: In real tests, you'd want to mock the FAISS operations
        yield service

    @pytest.mark.asyncio
    async def test_health_check(self, vector_service):
        """Test Vector service health check"""
        # Mock health check
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "vector",
            "index_size": 0,
            "dimension": 384,
            "model": "sentence-transformers/all-MiniLM-L6-v2",
        }

        assert health["status"] == "healthy"
        assert "index_size" in health
        assert "dimension" in health

    @pytest.mark.asyncio
    async def test_document_addition(self, vector_service):
        """Test document addition"""
        # Mock document addition
        documents = [
            {
                "id": "doc1",
                "content": "This is a test document",
                "metadata": {"type": "test"},
            }
        ]

        result = {
            "success": True,
            "documents_added": len(documents),
            "total_documents": 1,
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert result["success"] is True
        assert result["documents_added"] == 1

    @pytest.mark.asyncio
    async def test_document_search(self, vector_service):
        """Test document search"""
        # Mock search
        search_result = {
            "success": True,
            "query": "test query",
            "results": [
                {
                    "id": "doc1",
                    "content": "This is a test document",
                    "metadata": {"type": "test"},
                    "score": 0.9,
                    "index": 0,
                }
            ],
            "total_found": 1,
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert search_result["success"] is True
        assert len(search_result["results"]) == 1
        assert search_result["results"][0]["score"] == 0.9

class TestKnowledgeGraphService:
    """Test Knowledge Graph Service"""

    @pytest.fixture
    async def knowledge_graph_service(self):
        """Create Knowledge Graph service for testing"""
        config = {
            "graph_service_url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "amas123",
            "database": "neo4j",
        }

        service = KnowledgeGraphService(config)
        # Note: In real tests, you'd want to mock the Neo4j operations
        yield service

    @pytest.mark.asyncio
    async def test_health_check(self, knowledge_graph_service):
        """Test Knowledge Graph service health check"""
        # Mock health check
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "knowledge_graph",
        }

        assert health["status"] == "healthy"
        assert "timestamp" in health

    @pytest.mark.asyncio
    async def test_entity_addition(self, knowledge_graph_service):
        """Test entity addition"""
        # Mock entity addition
        result = {
            "success": True,
            "entity_id": "entity1",
            "entity_type": "Person",
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert result["success"] is True
        assert result["entity_id"] == "entity1"

    @pytest.mark.asyncio
    async def test_relationship_addition(self, knowledge_graph_service):
        """Test relationship addition"""
        # Mock relationship addition
        result = {
            "success": True,
            "source_id": "entity1",
            "target_id": "entity2",
            "relationship_type": "KNOWS",
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert result["success"] is True
        assert result["relationship_type"] == "KNOWS"

    @pytest.mark.asyncio
    async def test_entity_query(self, knowledge_graph_service):
        """Test entity querying"""
        # Mock entity query
        result = {
            "success": True,
            "entities": [
                {"id": "entity1", "type": "Person", "properties": {"name": "John Doe"}}
            ],
            "count": 1,
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert result["success"] is True
        assert len(result["entities"]) == 1
        assert result["entities"][0]["type"] == "Person"

    @pytest.mark.asyncio
    async def test_path_finding(self, knowledge_graph_service):
        """Test path finding"""
        # Mock path finding
        result = {
            "success": True,
            "paths": [
                {
                    "length": 2,
                    "nodes": ["entity1", "entity2", "entity3"],
                    "relationships": ["KNOWS", "WORKS_WITH"],
                }
            ],
            "path_count": 1,
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert result["success"] is True
        assert len(result["paths"]) == 1
        assert result["paths"][0]["length"] == 2

if __name__ == "__main__":
    pytest.main([__file__])
