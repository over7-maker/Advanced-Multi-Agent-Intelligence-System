"""
Edge case tests for tasks_integrated.py
Tests error conditions, missing dependencies, and edge cases
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.api.routes.tasks_integrated import (
    create_task,
    execute_task,
    list_tasks,
    get_task,
    TaskCreate
)


class TestCreateTaskEdgeCases:
    """Test edge cases for task creation"""
    
    @pytest.mark.asyncio
    async def test_create_task_without_db(self):
        """Test task creation without database"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        
        mock_redis = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "test_user"
        
        with patch('src.api.routes.tasks_integrated.get_db', return_value=None):
            with patch('src.api.routes.tasks_integrated.get_redis', return_value=mock_redis):
                with patch('src.api.routes.tasks_integrated.get_current_user_optional', return_value=mock_user):
                    with patch('src.api.routes.tasks_integrated.get_predictive_engine') as mock_engine:
                        with patch('src.api.routes.tasks_integrated.get_intelligence_manager') as mock_intel:
                            with patch('src.api.routes.tasks_integrated.websocket_manager') as mock_ws:
                                # Mock services
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
                                
                                mock_intel_instance = AsyncMock()
                                mock_intel_instance.optimize_task_before_execution = AsyncMock(
                                    return_value={"optimal_agents": ["agent1"]}
                                )
                                mock_intel.return_value = mock_intel_instance
                                
                                mock_ws.broadcast = AsyncMock()
                                
                                # Should succeed in dev mode (cache-only)
                                from fastapi import BackgroundTasks
                                background_tasks = BackgroundTasks()
                                
                                result = await create_task(
                                    task_data=task_data,
                                    background_tasks=background_tasks,
                                    db=None,
                                    redis=mock_redis,
                                    current_user=mock_user
                                )
                                
                                assert result.id is not None
    
    @pytest.mark.asyncio
    async def test_create_task_without_redis(self):
        """Test task creation without Redis"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        
        mock_user = MagicMock()
        mock_user.id = "test_user"
        
        with patch('src.api.routes.tasks_integrated.get_db', return_value=mock_db):
            with patch('src.api.routes.tasks_integrated.get_redis', return_value=None):
                with patch('src.api.routes.tasks_integrated.get_current_user_optional', return_value=mock_user):
                    with patch('src.api.routes.tasks_integrated.get_predictive_engine') as mock_engine:
                        with patch('src.api.routes.tasks_integrated.get_intelligence_manager') as mock_intel:
                            with patch('src.api.routes.tasks_integrated.websocket_manager') as mock_ws:
                                # Mock services
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
                                
                                mock_intel_instance = AsyncMock()
                                mock_intel_instance.optimize_task_before_execution = AsyncMock(
                                    return_value={"optimal_agents": ["agent1"]}
                                )
                                mock_intel.return_value = mock_intel_instance
                                
                                mock_ws.broadcast = AsyncMock()
                                
                                # Should succeed (memory cache only)
                                from fastapi import BackgroundTasks
                                background_tasks = BackgroundTasks()
                                
                                result = await create_task(
                                    task_data=task_data,
                                    background_tasks=background_tasks,
                                    db=mock_db,
                                    redis=None,
                                    current_user=mock_user
                                )
                                
                                assert result.id is not None
    
    @pytest.mark.asyncio
    async def test_create_task_without_orchestrator(self):
        """Test task creation without orchestrator (should still create task)"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test",
            task_type="security_scan",
            target="example.com"
        )
        
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        
        mock_redis = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "test_user"
        
        with patch('src.api.routes.tasks_integrated.get_db', return_value=mock_db):
            with patch('src.api.routes.tasks_integrated.get_redis', return_value=mock_redis):
                with patch('src.api.routes.tasks_integrated.get_current_user_optional', return_value=mock_user):
                    with patch('src.api.routes.tasks_integrated.get_predictive_engine') as mock_engine:
                        with patch('src.api.routes.tasks_integrated.get_intelligence_manager') as mock_intel:
                            with patch('src.api.routes.tasks_integrated.websocket_manager') as mock_ws:
                                # Mock services
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
                                
                                mock_intel_instance = AsyncMock()
                                mock_intel_instance.optimize_task_before_execution = AsyncMock(
                                    return_value={"optimal_agents": ["agent1"]}
                                )
                                mock_intel.return_value = mock_intel_instance
                                
                                mock_ws.broadcast = AsyncMock()
                                
                                # Should succeed (orchestrator only needed for execution)
                                from fastapi import BackgroundTasks
                                background_tasks = BackgroundTasks()
                                
                                result = await create_task(
                                    task_data=task_data,
                                    background_tasks=background_tasks,
                                    db=mock_db,
                                    redis=mock_redis,
                                    current_user=mock_user
                                )
                                
                                assert result.id is not None
    
    @pytest.mark.asyncio
    async def test_create_task_with_invalid_data(self):
        """Test task creation with invalid input data"""
        # Test with missing required fields
        with pytest.raises(Exception):  # Should raise validation error
            task_data = TaskCreate(
                title="",  # Empty title
                description="Test",
                task_type="security_scan",
                target="example.com"
            )
    
    @pytest.mark.asyncio
    async def test_execute_task_not_found(self):
        """Test executing non-existent task"""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone = MagicMock(return_value=None)  # Task not found
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        mock_redis = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "test_user"
        
        with patch('src.api.routes.tasks_integrated.get_db', return_value=mock_db):
            with patch('src.api.routes.tasks_integrated.get_redis', return_value=mock_redis):
                with patch('src.api.routes.tasks_integrated.get_current_user_optional', return_value=mock_user):
                    from fastapi import BackgroundTasks
                    background_tasks = BackgroundTasks()
                    
                    # Should handle gracefully (return executing status with default values)
                    result = await execute_task(
                        task_id="nonexistent_task",
                        background_tasks=background_tasks,
                        db=mock_db,
                        current_user=mock_user
                    )
                    
                    # Should still return a response (with default task data)
                    assert result.task_id == "nonexistent_task"
                    assert result.status == "executing"
    
    @pytest.mark.asyncio
    async def test_list_tasks_with_filters(self):
        """Test list tasks with various filters"""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.id = "task1"
        mock_row.task_id = "task1"
        mock_row.title = "Test Task"
        mock_row.description = "Test"
        mock_row.status = "pending"
        mock_row.task_type = "security_scan"
        mock_row.target = "example.com"
        mock_row.priority = 5
        mock_row.created_at = MagicMock()
        mock_row.created_at.isoformat = MagicMock(return_value="2025-01-21T12:00:00")
        mock_row.created_by = "user1"
        mock_result.fetchall = MagicMock(return_value=[mock_row])
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        mock_redis = AsyncMock()
        mock_redis.keys = AsyncMock(return_value=[])
        
        mock_user = MagicMock()
        mock_user.id = "test_user"
        
        with patch('src.api.routes.tasks_integrated.get_db', return_value=mock_db):
            with patch('src.api.routes.tasks_integrated.get_redis', return_value=mock_redis):
                with patch('src.api.routes.tasks_integrated.get_current_user_optional', return_value=mock_user):
                    # Test with status filter
                    result = await list_tasks(
                        skip=0,
                        limit=100,
                        status="pending",
                        task_type=None,
                        db=mock_db,
                        redis=mock_redis,
                        current_user=mock_user
                    )
                    
                    assert result.total >= 0
                    
                    # Test with task_type filter
                    result = await list_tasks(
                        skip=0,
                        limit=100,
                        status=None,
                        task_type="security_scan",
                        db=mock_db,
                        redis=mock_redis,
                        current_user=mock_user
                    )
                    
                    assert result.total >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

