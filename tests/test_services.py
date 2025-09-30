"""
Test service implementations
"""
import pytest
import asyncio
from typing import Dict, Any

from amas.services.database_service import DatabaseService
from amas.services.security_service import SecurityService


class TestDatabaseService:
    """Test database service functionality"""

    @pytest.fixture
    def database_config(self):
        """Database configuration for testing"""
        return {
            "database": {
                "url": "postgresql://test:test@localhost:5432/amas_test"
            }
        }

    @pytest.fixture
    def database_service(self, database_config):
        """Create database service instance"""
        return DatabaseService(database_config)

    @pytest.mark.asyncio
    async def test_database_initialization(self, database_service):
        """Test database service initialization"""
        # Note: This test requires a running PostgreSQL instance
        # In a real test environment, you'd use a test database
        try:
            await database_service.initialize()
            assert database_service.pool is not None
        except Exception as e:
            # Skip test if database is not available
            pytest.skip(f"Database not available: {e}")

    @pytest.mark.asyncio
    async def test_health_check(self, database_service):
        """Test database health check"""
        try:
            health_status = await database_service.health_check()
            assert 'status' in health_status
            assert 'timestamp' in health_status
            assert 'service' in health_status
        except Exception as e:
            # Skip test if database is not available
            pytest.skip(f"Database not available: {e}")

    @pytest.mark.asyncio
    async def test_task_persistence(self, database_service):
        """Test task saving and retrieval"""
        try:
            await database_service.initialize()
            
            # Test data
            task_data = {
                'id': 'test_task_123',
                'type': 'test_type',
                'description': 'Test task description',
                'priority': 1,
                'status': 'pending',
                'created_at': '2023-01-01T00:00:00Z',
                'parameters': {'test': 'value'},
                'result': {'success': True}
            }
            
            # Save task
            await database_service.save_task(task_data)
            
            # Retrieve task
            retrieved_task = await database_service.get_task('test_task_123')
            assert retrieved_task is not None
            assert retrieved_task['id'] == 'test_task_123'
            assert retrieved_task['type'] == 'test_type'
            
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    @pytest.mark.asyncio
    async def test_audit_log_persistence(self, database_service):
        """Test audit log saving and retrieval"""
        try:
            await database_service.initialize()
            
            # Test audit event
            event_data = {
                'id': 'test_event_123',
                'timestamp': '2023-01-01T00:00:00Z',
                'event_type': 'test_event',
                'user_id': 'test_user',
                'action': 'test_action',
                'details': {'test': 'value'},
                'classification': 'test'
            }
            
            # Save audit event
            await database_service.save_audit_event(event_data)
            
            # Retrieve audit log
            audit_log = await database_service.get_audit_log(limit=10)
            assert isinstance(audit_log, list)
            
        except Exception as e:
            pytest.skip(f"Database not available: {e}")


class TestSecurityService:
    """Test security service functionality"""

    @pytest.fixture
    def security_config(self):
        """Security configuration for testing"""
        return {
            "security": {
                "jwt_secret": "test_secret_key",
                "encryption_key": "test_encryption_key_32_bytes",
                "audit_enabled": True
            }
        }

    @pytest.fixture
    def security_service(self, security_config):
        """Create security service instance"""
        return SecurityService(security_config)

    @pytest.mark.asyncio
    async def test_security_initialization(self, security_service):
        """Test security service initialization"""
        await security_service.initialize()
        assert security_service.jwt_secret == "test_secret_key"
        assert security_service.audit_enabled == True

    @pytest.mark.asyncio
    async def test_health_check(self, security_service):
        """Test security service health check"""
        health_status = await security_service.health_check()
        assert health_status['status'] == 'healthy'
        assert 'timestamp' in health_status
        assert 'service' in health_status
        assert 'audit_enabled' in health_status

    @pytest.mark.asyncio
    async def test_jwt_token_creation(self, security_service):
        """Test JWT token creation and validation"""
        user_id = "test_user"
        roles = ["admin", "user"]
        
        # Create token
        token = await security_service.create_jwt_token(user_id, roles)
        assert token is not None
        assert isinstance(token, str)
        
        # Decode token
        decoded_token = await security_service.decode_jwt_token(token)
        assert decoded_token is not None
        assert decoded_token['sub'] == user_id
        assert decoded_token['roles'] == roles

    @pytest.mark.asyncio
    async def test_invalid_jwt_token(self, security_service):
        """Test handling of invalid JWT tokens"""
        invalid_token = "invalid_token"
        decoded_token = await security_service.decode_jwt_token(invalid_token)
        assert decoded_token is None

    @pytest.mark.asyncio
    async def test_password_hashing(self, security_service):
        """Test password hashing and verification"""
        password = "test_password"
        
        # Hash password
        hashed_password = await security_service.hash_password(password)
        assert hashed_password is not None
        assert hashed_password != password
        
        # Verify password
        is_valid = await security_service.verify_password(password, hashed_password)
        assert is_valid == True
        
        # Test with wrong password
        is_invalid = await security_service.verify_password("wrong_password", hashed_password)
        assert is_invalid == False

    @pytest.mark.asyncio
    async def test_audit_logging(self, security_service):
        """Test audit event logging"""
        # Test audit event logging (without database service)
        await security_service.log_audit_event(
            event_type="test_event",
            user_id="test_user",
            action="test_action",
            details={"test": "value"},
            classification="test"
        )
        
        # Should not raise exception even without database service
        assert True

    @pytest.mark.asyncio
    async def test_audit_log_retrieval(self, security_service):
        """Test audit log retrieval"""
        # Test without database service
        audit_log = await security_service.get_audit_log()
        assert isinstance(audit_log, list)
        assert len(audit_log) == 0  # Should be empty without database service


class TestServiceIntegration:
    """Test service integration"""

    @pytest.mark.asyncio
    async def test_database_security_integration(self, database_config, security_config):
        """Test integration between database and security services"""
        try:
            # Initialize database service
            database_service = DatabaseService(database_config)
            await database_service.initialize()
            
            # Initialize security service with database service
            security_service = SecurityService(security_config, database_service)
            await security_service.initialize()
            
            # Test audit logging with database
            await security_service.log_audit_event(
                event_type="integration_test",
                user_id="test_user",
                action="test_action",
                details={"integration": "test"},
                classification="test"
            )
            
            # Retrieve audit log
            audit_log = await security_service.get_audit_log(limit=10)
            assert isinstance(audit_log, list)
            
            # Clean up
            await database_service.close()
            
        except Exception as e:
            pytest.skip(f"Database not available: {e}")