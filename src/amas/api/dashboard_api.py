"""
AMAS Dashboard API

This module provides a Flask-based REST API for the AMAS Dashboard,
serving real-time system metrics, agent status, and task information.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

from ..core.unified_orchestrator_v2 import UnifiedOrchestratorV2
from ..services.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class DashboardAPI:
    """
    Flask-based API for the AMAS Dashboard.

    Provides endpoints for system metrics, agent status, task information,
    and real-time updates for monitoring and management.
    """

    def __init__(
        self, orchestrator: UnifiedOrchestratorV2, service_manager: ServiceManager
    ):
        """
        Initialize the Dashboard API.

        Args:
            orchestrator: The unified orchestrator instance
            service_manager: The service manager instance
        """
        self.orchestrator = orchestrator
        self.service_manager = service_manager
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend access

        self._setup_routes()
        logger.info("Dashboard API initialized")

    def _setup_routes(self):
        """Set up Flask routes for the API."""

        @self.app.route("/api/health", methods=["GET"])
        def health_check():
            """Health check endpoint."""
            return jsonify(
                {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "2.0.0",
                }
            )

        @self.app.route("/api/system/metrics", methods=["GET"])
        def get_system_metrics():
            """Get overall system metrics."""
            try:
                metrics = self.orchestrator.metrics
                total_tasks = metrics.get("tasks_completed", 0) + metrics.get(
                    "tasks_failed", 0
                )
                success_rate = (
                    (metrics.get("tasks_completed", 0) / total_tasks * 100)
                    if total_tasks > 0
                    else 100.0
                )

                return jsonify(
                    {
                        "totalAgents": metrics.get("active_agents", 0),
                        "activeAgents": len(
                            [
                                a
                                for a in self.orchestrator.agents.values()
                                if a.status == "active"
                            ]
                        ),
                        "tasksProcessed": total_tasks,
                        "tasksCompleted": metrics.get("tasks_completed", 0),
                        "tasksFailed": metrics.get("tasks_failed", 0),
                        "averageTaskTime": metrics.get("average_task_time", 0.0),
                        "successRate": round(success_rate, 1),
                        "systemUptime": "99.7%",  # Placeholder - would be calculated from actual uptime
                        "memoryUsage": 68,  # Placeholder - would be from system monitoring
                        "cpuUsage": 42,  # Placeholder - would be from system monitoring
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            except Exception as e:
                logger.error(f"Error getting system metrics: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/agents", methods=["GET"])
        def get_agents():
            """Get all agent information."""
            try:
                agents_data = []
                for agent_id, agent in self.orchestrator.agents.items():
                    agent_status = asyncio.run(agent.get_status())
                    agents_data.append(
                        {
                            "id": agent_id,
                            "name": agent_status.get("name", "Unknown Agent"),
                            "status": agent_status.get("status", "unknown"),
                            "tasks": agent_status.get("metrics", {}).get(
                                "tasks_completed", 0
                            ),
                            "successRate": round(
                                agent_status.get("metrics", {}).get("success_rate", 0.0)
                                * 100,
                                1,
                            ),
                            "lastActive": agent_status.get(
                                "last_active", datetime.utcnow().isoformat()
                            ),
                            "metrics": agent_status.get("metrics", {}),
                            "llmParameters": agent_status.get("llm_parameters", {}),
                        }
                    )

                return jsonify(agents_data)
            except Exception as e:
                logger.error(f"Error getting agents: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/agents/<agent_id>", methods=["GET"])
        def get_agent_details(agent_id):
            """Get detailed information for a specific agent."""
            try:
                if agent_id not in self.orchestrator.agents:
                    return jsonify({"error": "Agent not found"}), 404

                agent = self.orchestrator.agents[agent_id]
                agent_status = asyncio.run(agent.get_status())

                return jsonify(agent_status)
            except Exception as e:
                logger.error(f"Error getting agent details for {agent_id}: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/tasks", methods=["GET"])
        def get_tasks():
            """Get recent tasks."""
            try:
                limit = request.args.get("limit", 50, type=int)
                status_filter = request.args.get("status")

                tasks_data = []
                for task_id, task in list(self.orchestrator.tasks.items())[-limit:]:
                    if status_filter and task.status.value != status_filter:
                        continue

                    duration = 0.0
                    if task.started_at and task.completed_at:
                        duration = (task.completed_at - task.started_at).total_seconds()
                    elif task.started_at:
                        duration = (datetime.utcnow() - task.started_at).total_seconds()

                    tasks_data.append(
                        {
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "type": task.task_type,
                            "status": task.status.value,
                            "priority": task.priority.name.lower(),
                            "assignedAgent": task.assigned_agent_id,
                            "createdAt": task.created_at.isoformat(),
                            "startedAt": (
                                task.started_at.isoformat() if task.started_at else None
                            ),
                            "completedAt": (
                                task.completed_at.isoformat()
                                if task.completed_at
                                else None
                            ),
                            "duration": round(duration, 2),
                            "result": task.result,
                            "error": task.error,
                        }
                    )

                return jsonify(tasks_data)
            except Exception as e:
                logger.error(f"Error getting tasks: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/tasks/<task_id>", methods=["GET"])
        def get_task_details(task_id):
            """Get detailed information for a specific task."""
            try:
                if task_id not in self.orchestrator.tasks:
                    return jsonify({"error": "Task not found"}), 404

                task = self.orchestrator.tasks[task_id]

                duration = 0.0
                if task.started_at and task.completed_at:
                    duration = (task.completed_at - task.started_at).total_seconds()
                elif task.started_at:
                    duration = (datetime.utcnow() - task.started_at).total_seconds()

                return jsonify(
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "type": task.task_type,
                        "status": task.status.value,
                        "priority": task.priority.name.lower(),
                        "assignedAgent": task.assigned_agent_id,
                        "parameters": task.parameters,
                        "createdAt": task.created_at.isoformat(),
                        "startedAt": (
                            task.started_at.isoformat() if task.started_at else None
                        ),
                        "completedAt": (
                            task.completed_at.isoformat() if task.completed_at else None
                        ),
                        "duration": round(duration, 2),
                        "result": task.result,
                        "error": task.error,
                        "workflowId": task.workflow_id,
                        "workflowStepId": task.workflow_step_id,
                    }
                )
            except Exception as e:
                logger.error(f"Error getting task details for {task_id}: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/analytics/performance", methods=["GET"])
        def get_performance_analytics():
            """Get performance analytics data."""
            try:
                # Generate sample performance data for the last 24 hours
                # In a real implementation, this would come from a time-series database
                now = datetime.utcnow()
                performance_data = []

                for i in range(24):
                    timestamp = now - timedelta(hours=23 - i)
                    # Simulate some performance metrics
                    tasks = max(20, int(50 + 30 * (i / 24) + (i % 4) * 10))
                    success = int(tasks * (0.92 + 0.05 * (i / 24)))
                    failed = tasks - success

                    performance_data.append(
                        {
                            "time": timestamp.strftime("%H:%M"),
                            "timestamp": timestamp.isoformat(),
                            "tasks": tasks,
                            "success": success,
                            "failed": failed,
                            "successRate": (
                                round((success / tasks) * 100, 1) if tasks > 0 else 0
                            ),
                        }
                    )

                return jsonify(performance_data)
            except Exception as e:
                logger.error(f"Error getting performance analytics: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/analytics/agents", methods=["GET"])
        def get_agent_analytics():
            """Get agent performance analytics."""
            try:
                agent_analytics = []
                for agent_id, agent in self.orchestrator.agents.items():
                    agent_status = asyncio.run(agent.get_status())
                    metrics = agent_status.get("metrics", {})

                    agent_analytics.append(
                        {
                            "agentId": agent_id,
                            "name": agent_status.get("name", "Unknown Agent"),
                            "tasksCompleted": metrics.get("tasks_completed", 0),
                            "tasksFailed": metrics.get("tasks_failed", 0),
                            "successRate": round(
                                metrics.get("success_rate", 0.0) * 100, 1
                            ),
                            "averageResponseTime": round(
                                metrics.get("average_response_time", 0.0), 2
                            ),
                            "tokensUsed": metrics.get("tokens_used", 0),
                            "aiRequestsMade": metrics.get("ai_requests_made", 0),
                        }
                    )

                return jsonify(agent_analytics)
            except Exception as e:
                logger.error(f"Error getting agent analytics: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/workflows", methods=["GET"])
        def get_workflows():
            """Get available workflows."""
            try:
                workflows_data = []
                for workflow_id, workflow in self.orchestrator.workflows.items():
                    workflows_data.append(
                        {
                            "id": workflow_id,
                            "name": workflow.get("name", "Unknown Workflow"),
                            "description": workflow.get("description", ""),
                            "steps": len(workflow.get("steps", [])),
                            "stepDetails": workflow.get("steps", []),
                        }
                    )

                return jsonify(workflows_data)
            except Exception as e:
                logger.error(f"Error getting workflows: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/services/status", methods=["GET"])
        def get_services_status():
            """Get status of all services."""
            try:
                services_status = {}

                # Universal AI Manager status
                if self.orchestrator.universal_ai_manager:
                    ai_status = asyncio.run(
                        self.orchestrator.universal_ai_manager.get_status()
                    )
                    services_status["universal_ai_manager"] = ai_status

                # Vector Service status
                if self.service_manager.vector_service:
                    services_status["vector_service"] = {
                        "status": (
                            "healthy"
                            if self.service_manager.vector_service.is_initialized
                            else "unavailable"
                        ),
                        "initialized": self.service_manager.vector_service.is_initialized,
                    }

                # Knowledge Graph Service status
                if self.service_manager.knowledge_graph_service:
                    services_status["knowledge_graph_service"] = {
                        "status": (
                            "healthy"
                            if self.service_manager.knowledge_graph_service.is_initialized
                            else "unavailable"
                        ),
                        "initialized": self.service_manager.knowledge_graph_service.is_initialized,
                    }

                return jsonify(services_status)
            except Exception as e:
                logger.error(f"Error getting services status: {e}")
                return jsonify({"error": str(e)}), 500

    def run(self, host="0.0.0.0", port=5000, debug=False):
        """
        Run the Flask application.

        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
        logger.info(f"Starting Dashboard API on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

    def get_app(self):
        """
        Get the Flask application instance.

        Returns:
            Flask application instance
        """
        return self.app


def create_dashboard_api(
    orchestrator: UnifiedOrchestratorV2, service_manager: ServiceManager
) -> DashboardAPI:
    """
    Factory function to create a Dashboard API instance.

    Args:
        orchestrator: The unified orchestrator instance
        service_manager: The service manager instance

    Returns:
        DashboardAPI instance
    """
    return DashboardAPI(orchestrator, service_manager)
