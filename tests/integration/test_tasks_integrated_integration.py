"""
Integration tests for tasks_integrated.py
Tests complete task lifecycle and integration with other components
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.api.routes.tasks_integrated import (
    create_task,
    execute_task,
    list_tasks,
    get_task,
    TaskCreate
)


class TestCreateTaskFullFlow:
    """Test complete task creation flow"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_task_full_flow(self):
        """Test complete task creation with all components"""
        task_data = TaskCreate(
            title="Integration Test Task",
            description="Test full flow",
            task_type="security_scan",
            target="example.com",
            priority=5
        )
        
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock()
        
        mock_user = MagicMock()
        mock_user.id = "test_user"
        mock_user.username = "testuser"
        
        with patch('src.api.routes.tasks_integrated.get_db', return_value=mock_db):
            with patch('src.api.routes.tasks_integrated.get_redis', return_value=mock_redis):
                with patch('src.api.routes.tasks_integrated.get_current_user_optional', return_value=mock_user):
                    with patch('src.api.routes.tasks_integrated.get_predictive_engine') as mock_engine:
                        with patch('src.api.routes.tasks_integrated.get_intelligence_manager') as mock_intel:
                            with patch('src.api.routes.tasks_integrated.websocket_manager') as mock_ws:
                                # Mock prediction
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
                                
                                # Mock intelligence manager
                                mock_intel_instance = AsyncMock()
                                mock_intel_instance.optimize_task_before_execution = AsyncMock(
                                    return_value={"optimal_agents": ["agent1", "agent2"]}
                                )
                                mock_intel.return_value = mock_intel_instance
                                
                                # Mock WebSocket
                                mock_ws.broadcast = AsyncMock()
                                
                                # Execute
                                from fastapi import BackgroundTasks
                                background_tasks = BackgroundTasks()
                                
                                result = await create_task(
                                    task_data=task_data,
                                    background_tasks=background_tasks,
                                    db=mock_db,
                                    redis=mock_redis,
                                    current_user=mock_user
                                )
                                
                                # Verify result
                                assert result.id is not None
                                assert result.title == "Integration Test Task"
                                assert result.status == "pending"
                                assert result.task_type == "security_scan"
                                assert result.created_by == "test_user"
                                
                                # Verify database was called
                                mock_db.execute.assert_called()
                                mock_db.commit.assert_called()
                                
                                # Verify WebSocket broadcast
                                mock_ws.broadcast.assert_called()


class TestExecuteTaskFullFlow:
    """Test complete task execution flow"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_execute_task_full_flow(self):
        """Test complete task execution with orchestrator"""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.task_id = "task_123"
        mock_row.title = "Test Task"
        mock_row.description = "Test"
        mock_row.task_type = "security_scan"
        mock_row.target = "example.com"
        mock_row.parameters = "{}"
        mock_row.status = "pending"
        mock_row.priority = 5
        mock_row.execution_metadata = '{"prediction": {"estimated_duration": 120.0}}'
        mock_result.fetchone = MagicMock(return_value=mock_row)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        
        mock_redis = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = "test_user"
        
        with patch('src.api.routes.tasks_integrated.get_db', return_value=mock_db):
            with patch('src.api.routes.tasks_integrated.get_redis', return_value=mock_redis):
                with patch('src.api.routes.tasks_integrated.get_current_user_optional', return_value=mock_user):
                    with patch('src.api.routes.tasks_integrated.get_orchestrator_instance') as mock_orch:
                        with patch('src.api.routes.tasks_integrated.websocket_manager') as mock_ws:
                            # Mock orchestrator
                            mock_orch_instance = AsyncMock()
                            mock_orch_instance.execute_task = AsyncMock(return_value={
                                "success": True,
                                "output": {"agent_results": {"agent1": {"status": "complete"}}},
                                "quality_score": 0.9
                            })
                            mock_orch.return_value = mock_orch_instance
                            
                            # Mock WebSocket
                            mock_ws.broadcast = AsyncMock()
                            
                            # Execute
                            from fastapi import BackgroundTasks
                            background_tasks = BackgroundTasks()
                            
                            result = await execute_task(
                                task_id="task_123",
                                background_tasks=background_tasks,
                                db=mock_db,
                                current_user=mock_user
                            )
                            
                            # Verify result
                            assert result.task_id == "task_123"
                            assert result.status == "executing"
                            
                            # Note: orchestrator.execute_task is called in a background task,
                            # so we can't verify it was called immediately. The test verifies
                            # that the task execution endpoint returns the correct response.
                            # The actual orchestrator execution happens asynchronously.


class TestTaskLifecycle:
    """Integration contract: module exports remain stable (CAP-03)."""

    def test_tasks_integrated_core_exports(self):
        from src.api.routes import tasks_integrated as ti

        assert callable(ti.create_task)
        assert callable(ti.get_task)
        assert callable(ti.list_tasks)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])

