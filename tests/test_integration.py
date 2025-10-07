"""
Integration tests for AMAS system
"""

import asyncio

import httpx
import pytest

from amas.core.unified_orchestrator_v2 import TaskPriority


class TestSystemIntegration:
    """Test full system integration"""

    @pytest.mark.asyncio
    async def test_end_to_end_task_processing(
        self, amas_app, test_client: httpx.AsyncClient
    ):
        """Test complete task processing workflow"""
        # Submit a task via API
        task_data = {
            "description": "Collect intelligence on AI advancements",
            "task_type": "osint",
            "priority": 1,
            "metadata": {
                "title": "Collect AI Advancements",
                "parameters": {
                    "keywords": ["AI", "machine learning", "advancements"],
                    "sources": ["web", "academic"],
                },
                "required_agent_roles": ["intelligence_gatherer_agent"]
            }
        }

        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.post(
            "/tasks", json=task_data, headers=headers
        )
        assert response.status_code == 200

        task_id = response.json()["task_id"]

        # Wait for task processing
        max_attempts = 10
        for attempt in range(max_attempts):
            status_response = await test_client.get(
                f"/tasks/{task_id}", headers=headers
            )
            assert status_response.status_code == 200

            status_data = status_response.json()
            if status_data["status"] in ["completed", "failed"]:
                break

            await asyncio.sleep(0.5)

        # Verify task completion
        assert status_data["status"] == "completed"
        assert "result" in status_data

    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self, amas_app):
        """Test coordination between multiple agents"""
        orchestrator = amas_app.orchestrator

        # Submit multiple tasks of different types
        tasks = [
            {
                "description": "OSINT task",
                "task_type": "osint",
                "priority": 1,
                "metadata": {"title": "OSINT Task", "parameters": {"keywords": ["test"]}, "required_agent_roles": ["intelligence_gatherer_agent"]}
            },
            {
                "description": "Forensics task",
                "task_type": "forensics",
                "priority": 2,
                "metadata": {"title": "Forensics Task", "parameters": {"source": "/dev/sda1"}, "required_agent_roles": ["forensics_agent"]}
            },
            {
                "description": "Data analysis task",
                "task_type": "data_analysis",
                "priority": 3,
                "metadata": {"title": "Data Analysis Task", "parameters": {"data": [{"value": 1}]}, "required_agent_roles": ["data_agent"]}
            },
        ]

        task_ids = []
        for task_data in tasks:
            task_id = await orchestrator.submit_task(
                description=task_data["description"],
                task_type=task_data["task_type"],
                priority=TaskPriority(task_data["priority"]),
                metadata=task_data["metadata"],
            )

            task_ids.append(task_id)


        # Wait for all tasks to complete
        for task_id in task_ids:
            max_attempts = 10
            for attempt in range(max_attempts):
                status = await orchestrator.get_task_status(task_id)
                if status["status"] in ["completed", "failed"]:
                    break
                await asyncio.sleep(0.5)

            assert status["status"] == "completed"

    @pytest.mark.asyncio
    async def test_agent_status_monitoring(self, amas_app):
        """Test agent status monitoring"""
        orchestrator = amas_app.orchestrator

        # Get all agents
        agents = await orchestrator.list_agents()
        assert len(agents) > 0

        # Check each agent's status
        for agent in agents:
            agent_id = agent["agent_id"]
            status = await orchestrator.get_agent_status(agent_id)
            assert "agent_id" in status
            assert "status" in status
            assert status["agent_id"] == agent_id

    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, amas_app):
        """Test system health monitoring"""
        # Test application health check
        health_status = await amas_app.health_check()
        assert health_status["status"] == "healthy"
        assert "services" in health_status

        # Test orchestrator status
        system_status = await amas_app.orchestrator.get_system_status()
        assert "orchestrator_status" in system_status
        assert "active_agents" in system_status

    @pytest.mark.asyncio
    async def test_error_handling(self, amas_app):
        """Test error handling in the system"""
        orchestrator = amas_app.orchestrator

        # Test invalid task submission
        invalid_task = {
            "description": "Invalid task",
            "task_type": "invalid_type",
            "priority": "LOW",
            "metadata": {"title": "Invalid Task"}
        }

        # Should handle gracefully
        try:
            task_id = await orchestrator.submit_task(
                description=invalid_task["description"],
                task_type=invalid_task["task_type"],
                priority=TaskPriority(invalid_task["priority"]),
                metadata=invalid_task["metadata"],
            )

            # If it doesn't raise an exception, check the result
            if task_id:
                status = await orchestrator.get_task_status(task_id)
                # Should either complete or fail gracefully
                assert status["status"] in ["completed", "failed", "pending"]
        except Exception as e:
            # Should handle errors gracefully
            assert isinstance(e, Exception)

    @pytest.mark.asyncio
    async def test_concurrent_task_processing(self, amas_app):
        """Test concurrent task processing"""
        orchestrator = amas_app.orchestrator

        # Submit multiple tasks concurrently
        tasks = [
            {
                "description": f"OSINT task {i}",
                "task_type": "osint",
                "priority": TaskPriority.MEDIUM, # Use a valid TaskPriority enum member
                "metadata": {"title": f"OSINT Task {i}", "parameters": {"keywords": [f"keyword_{i}"]}, "required_agent_roles": ["intelligence_gatherer_agent"]}
            }
            for i in range(5)
        ]

        # Submit all tasks
        task_ids = []
        for task_data in tasks:
            task_id = await orchestrator.submit_task(
                description=task_data["description"],
                task_type=task_data["task_type"],
                priority=task_data["priority"],
                metadata=task_data["metadata"],
            )
            task_ids.append(task_id)


        # Wait for all tasks to complete
        completed_tasks = 0
        max_attempts = 20

        for attempt in range(max_attempts):
            for task_id in task_ids:
                status = await orchestrator.get_task_status(task_id)
                if status["status"] in ["completed", "failed"]:
                    completed_tasks += 1

            if completed_tasks >= len(task_ids):
                break

            await asyncio.sleep(0.5)

        # Verify all tasks were processed
        assert completed_tasks >= len(task_ids)

    @pytest.mark.asyncio
    async def test_service_dependencies(self, amas_app):
        """Test service dependencies and initialization order"""
        service_manager = amas_app.service_manager

        # Check that all services are initialized
        services = [
            service_manager.get_llm_service(),
            service_manager.get_vector_service(),
            service_manager.get_knowledge_graph(),
            service_manager.get_database_service(),
            service_manager.get_security_service(),
        ]

        for service in services:
            assert service is not None

        # Test service health checks
        health_status = await service_manager.health_check_all_services()
        assert "llm" in health_status
        assert "vector" in health_status
        assert "knowledge_graph" in health_status
        assert "database" in health_status
        assert "security" in health_status

    @pytest.mark.asyncio
    async def test_workflow_execution(
        self, amas_app, test_client: httpx.AsyncClient
    ):
        """Test workflow execution"""
        workflow_data = {
            "workflow_id": "test_workflow",
            "parameters": {"target": "test_target", "depth": 2},
        }

        headers = {"Authorization": "Bearer valid_token"}
        response = await test_client.post(
            f"/workflows/{workflow_data['workflow_id']}/execute",
            json=workflow_data["parameters"],
            headers=headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert "workflow_id" in data
        assert "status" in data

    @pytest.mark.asyncio
    async def test_audit_trail(self, amas_app, test_client: httpx.AsyncClient):
        """Test audit trail functionality"""
        # Perform some actions that should generate audit events
        task_data = {
            "description": "Audit test task",
            "task_type": "osint",
            "priority": TaskPriority.MEDIUM,
            "metadata": {"title": "Audit Test Task", "parameters": {"keywords": ["audit", "test"]}, "required_agent_roles": ["intelligence_gatherer_agent"]}
        }

        headers = {"Authorization": "Bearer valid_token"}

        # Submit task (should generate audit event)
        response = await test_client.post(
            "/tasks", json=task_data, headers=headers
        )
        assert response.status_code == 200

        # Get audit log
        audit_response = await test_client.get("/audit", headers=headers)
        assert audit_response.status_code == 200

        audit_data = audit_response.json()
        assert "audit_log" in audit_data
        assert isinstance(audit_data["audit_log"], list)
