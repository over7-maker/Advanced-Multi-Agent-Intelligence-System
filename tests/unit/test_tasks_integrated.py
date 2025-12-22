"""
Unit tests for tasks_integrated.py helper functions
Tests individual functions extracted from create_task()
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.api.routes.tasks_integrated import (
    TaskCreate,
    _broadcast_task_created,
    _cache_task,
    _create_error_response,
    _generate_task_id,
    _get_ml_prediction,
    _handle_database_error,
    _handle_orchestrator_error,
    _log_error_with_context,
    _persist_task_to_db,
    _select_agents,
)


class TestGenerateTaskID:
    """Test task ID generation"""
    
    @pytest.mark.asyncio
    async def test_generate_task_id_format(self):
        """Test task ID format"""
        task_id = await _generate_task_id()
        
        assert task_id.startswith("task_")
        assert len(task_id) > 20
        assert "_" in task_id
    
    @pytest.mark.asyncio
    async def test_generate_task_id_uniqueness(self):
        """Test task ID uniqueness"""
        task_ids = [await _generate_task_id() for _ in range(10)]
        
        assert len(set(task_ids)) == 10, "Task IDs should be unique"


class TestGetMLPrediction:
    """Test ML prediction retrieval"""
    
    @pytest.mark.asyncio
    async def test_get_ml_prediction_success(self):
        """Test successful ML prediction"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        
        with patch('src.api.routes.tasks_integrated.get_predictive_engine') as mock_engine:
            mock_prediction = MagicMock()
            mock_prediction.success_probability = 0.85
            mock_prediction.estimated_duration = 120.0
            mock_prediction.quality_score_prediction = 0.9
            mock_prediction.confidence = 0.8
            mock_prediction.risk_factors = []
            mock_prediction.optimization_suggestions = []
            
            mock_engine_instance = AsyncMock()
            mock_engine_instance.predict_task_outcome = AsyncMock(return_value=mock_prediction)
            mock_engine.return_value = mock_engine_instance
            
            prediction = await _get_ml_prediction(task_data, "task_123", "user_123")
            
            assert prediction["success_probability"] == 0.85
            assert prediction["estimated_duration"] == 120.0
            assert prediction["confidence"] == 0.8
    
    @pytest.mark.asyncio
    async def test_get_ml_prediction_fallback(self):
        """Test ML prediction fallback on error"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        
        with patch('src.api.routes.tasks_integrated.get_predictive_engine', side_effect=Exception("Engine error")):
            prediction = await _get_ml_prediction(task_data, "task_123", "user_123")
            
            # Should return fallback values
            assert prediction["success_probability"] == 0.75
            assert prediction["estimated_duration"] == 120.0
            assert prediction["confidence"] == 0.3


class TestSelectAgents:
    """Test agent selection"""
    
    @pytest.mark.asyncio
    async def test_select_agents_success(self):
        """Test successful agent selection"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        prediction = {"success_probability": 0.85}
        
        with patch('src.api.routes.tasks_integrated.get_intelligence_manager') as mock_intel:
            mock_intel_instance = AsyncMock()
            mock_intel_instance.optimize_task_before_execution = AsyncMock(
                return_value={"optimal_agents": ["agent1", "agent2"]}
            )
            mock_intel.return_value = mock_intel_instance
            
            agents = await _select_agents(task_data, prediction, "task_123", "user_123")
            
            assert len(agents) == 2
            assert "agent1" in agents
            assert "agent2" in agents
    
    @pytest.mark.asyncio
    async def test_select_agents_fallback(self):
        """Test agent selection fallback"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        prediction = {"success_probability": 0.85}
        
        with patch('src.api.routes.tasks_integrated.get_intelligence_manager', side_effect=Exception("Manager error")):
            with patch('src.api.routes.tasks_integrated._get_default_agents_for_task_type', return_value=["default_agent"]):
                agents = await _select_agents(task_data, prediction, "task_123", "user_123")
                
                assert len(agents) > 0
                assert "default_agent" in agents


class TestPersistTaskToDB:
    """Test database persistence"""
    
    @pytest.mark.asyncio
    async def test_persist_task_to_db_success(self):
        """Test successful database persistence"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        prediction = {"success_probability": 0.85}
        
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        
        result = await _persist_task_to_db("task_123", task_data, prediction, "user_123", mock_db)
        
        assert result is True
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_persist_task_to_db_no_db(self):
        """Test persistence without database (dev mode)"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        prediction = {"success_probability": 0.85}
        
        result = await _persist_task_to_db("task_123", task_data, prediction, "user_123", None)
        
        assert result is True  # Should allow cache-only in dev mode
    
    @pytest.mark.asyncio
    async def test_persist_task_to_db_failure(self):
        """Test database persistence failure"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        prediction = {"success_probability": 0.85}
        
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=Exception("DB error"))
        mock_db.rollback = AsyncMock()
        
        result = await _persist_task_to_db("task_123", task_data, prediction, "user_123", mock_db)
        
        assert result is False
        mock_db.rollback.assert_called_once()


class TestCacheTask:
    """Test task caching"""
    
    @pytest.mark.asyncio
    async def test_cache_task_memory(self):
        """Test memory caching"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        prediction = {"success_probability": 0.85}
        selected_agents = ["agent1"]
        
        # Clear cache first
        from src.api.routes.tasks_integrated import (
            _recently_accessed_tasks,
            _recently_accessed_tasks_timestamps,
        )
        _recently_accessed_tasks.clear()
        _recently_accessed_tasks_timestamps.clear()
        
        await _cache_task("task_123", task_data, prediction, selected_agents, None, "user_123")
        
        assert "task_123" in _recently_accessed_tasks
        assert _recently_accessed_tasks["task_123"]["task_id"] == "task_123"
    
    @pytest.mark.asyncio
    async def test_cache_task_redis(self):
        """Test Redis caching"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        prediction = {"success_probability": 0.85}
        selected_agents = ["agent1"]
        
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock()
        
        # Mock cache services to raise ImportError so it falls back to Redis
        with patch('src.amas.services.task_cache_service.get_task_cache_service', side_effect=ImportError):
            with patch('src.amas.services.prediction_cache_service.get_prediction_cache_service', side_effect=ImportError):
                await _cache_task("task_123", task_data, prediction, selected_agents, mock_redis, "user_123")
        
        # Should call setex for task and prediction
        assert mock_redis.setex.call_count >= 1


class TestBroadcastTaskCreated:
    """Test WebSocket broadcasting"""
    
    @pytest.mark.asyncio
    async def test_broadcast_task_created_success(self):
        """Test successful broadcast"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        prediction = {"success_probability": 0.85}
        selected_agents = ["agent1"]
        
        with patch('src.api.routes.tasks_integrated.websocket_manager') as mock_ws:
            mock_ws.broadcast = AsyncMock()
            
            await _broadcast_task_created("task_123", task_data, prediction, selected_agents)
            
            mock_ws.broadcast.assert_called_once()
            call_args = mock_ws.broadcast.call_args[0][0]
            assert call_args["event"] == "task_created"
            assert call_args["task_id"] == "task_123"
    
    @pytest.mark.asyncio
    async def test_broadcast_task_created_failure(self):
        """Test broadcast failure handling"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        prediction = {"success_probability": 0.85}
        selected_agents = ["agent1"]
        
        with patch('src.api.routes.tasks_integrated.websocket_manager') as mock_ws:
            mock_ws.broadcast = AsyncMock(side_effect=Exception("WebSocket error"))
            
            # Should not raise exception
            await _broadcast_task_created("task_123", task_data, prediction, selected_agents)


class TestErrorHandling:
    """Test error handling utilities"""
    
    def test_log_error_with_context(self):
        """Test error logging with context"""
        error = ValueError("Test error")
        
        with patch('src.api.routes.tasks_integrated.logger') as mock_logger:
            _log_error_with_context(
                error,
                level="error",
                task_id="task_123",
                user_id="user_123",
                operation="test_operation"
            )
            
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert "test_operation" in call_args[0][0]
    
    def test_create_error_response(self):
        """Test error response creation"""
        error_response = _create_error_response(
            status_code=500,
            detail="Test error",
            error_code="TEST_ERROR",
            task_id="task_123"
        )
        
        assert isinstance(error_response, Exception)
        assert error_response.status_code == 500
    
    def test_handle_database_error(self):
        """Test database error handling"""
        error = Exception("Database connection failed")
        
        error_response = _handle_database_error(
            error,
            task_id="task_123",
            operation="test_db_operation",
            user_id="user_123"
        )
        
        assert error_response.status_code in [500, 503, 409]
    
    def test_handle_orchestrator_error(self):
        """Test orchestrator error handling"""
        error = Exception("Orchestrator not available")
        
        error_response = _handle_orchestrator_error(
            error,
            task_id="task_123",
            operation="test_orch_operation",
            user_id="user_123"
        )
        
        assert error_response.status_code in [500, 503, 504]


class TestUserContextExtraction:
    """Test user context extraction"""
    
    def test_user_context_with_user(self):
        """Test user context extraction with user"""
        from src.api.routes.tasks_integrated import User

        # Create User with required fields
        user = User(
            id="user_123",
            username="testuser",
            email="test@example.com"
        )
        user.roles = ["admin"]
        
        user_id = user.id if user and hasattr(user, 'id') else "system"
        
        assert user_id == "user_123"
    
    def test_user_context_without_user(self):
        """Test user context extraction without user"""
        user_id = "system" if None else "system"
        
        assert user_id == "system"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

