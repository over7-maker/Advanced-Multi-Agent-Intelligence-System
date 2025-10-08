"""
n8n Integration Service

This module provides integration with n8n workflow automation platform
for advanced intelligence workflow orchestration.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests


class N8NIntegration:
    """
    n8n workflow integration service.

    This service provides integration with n8n for advanced workflow
    orchestration in intelligence operations.
    """

    def __init__(
        self,
        n8n_url: str = "http://localhost:5678",
        n8n_api_key: Optional[str] = None,
        username: str = "admin",
        password: str = "admin",
    ):
        """
        Initialize n8n integration.

        Args:
            n8n_url: n8n instance URL
            n8n_api_key: n8n API key (if available)
            username: n8n username
            password: n8n password
        """
        self.n8n_url = n8n_url.rstrip("/")
        self.n8n_api_key = n8n_api_key
        self.username = username
        self.password = password

        # Authentication
        self.auth_token = None
        self.session = requests.Session()

        # Workflow templates
        self.workflow_templates = {}

        # Performance metrics
        self.metrics = {
            "workflows_executed": 0,
            "workflows_failed": 0,
            "average_execution_time": 0.0,
            "active_workflows": 0,
        }

        # Logging
        self.logger = logging.getLogger("amas.n8n_integration")

        # Initialize workflow templates
        self._initialize_workflow_templates()

    def _initialize_workflow_templates(self):
        """Initialize intelligence workflow templates."""
        try:
            # OSINT Monitoring Workflow
            self.workflow_templates["osint_monitoring"] = {
                "name": "OSINT Monitoring Workflow",
                "description": "Continuous OSINT source monitoring",
                "nodes": [
                    {
                        "name": "Schedule Trigger",
                        "type": "n8n-nodes-base.scheduleTrigger",
                        "parameters": {
                            "rule": {"interval": [{"field": "minutes", "value": 30}]}
                        },
                    },
                    {
                        "name": "OSINT Collection",
                        "type": "n8n-nodes-base.httpRequest",
                        "parameters": {
                            "url": "http://amas-api:8000/api/agents/osint/collect",
                            "method": "POST",
                            "body": {
                                "sources": "{{ $json.sources }}",
                                "keywords": "{{ $json.keywords }}",
                                "filters": "{{ $json.filters }}",
                            },
                        },
                    },
                    {
                        "name": "Data Processing",
                        "type": "n8n-nodes-base.function",
                        "parameters": {
                            "functionCode": """
// Process collected OSINT data
const items = $input.all();
const processedItems = [];

for (const item of items) {
    const data = item.json;

    // Filter relevant content
    if (data.relevance_score > 0.7) {
        processedItems.push({
            source: data.source,
            content: data.content,
            entities: data.entities,
            timestamp: data.timestamp
        });
    }
}

return processedItems;
"""
                        },
                    },
                    {
                        "name": "Store Results",
                        "type": "n8n-nodes-base.httpRequest",
                        "parameters": {
                            "url": "http://amas-api:8000/api/data/store",
                            "method": "POST",
                            "body": {"data": "{{ $json }}", "type": "osint"},
                        },
                    },
                ],
            }

            # Investigation Workflow
            self.workflow_templates["investigation"] = {
                "name": "Investigation Workflow",
                "description": "Multi-step investigation process",
                "nodes": [
                    {
                        "name": "Manual Trigger",
                        "type": "n8n-nodes-base.manualTrigger",
                        "parameters": {},
                    },
                    {
                        "name": "Entity Analysis",
                        "type": "n8n-nodes-base.httpRequest",
                        "parameters": {
                            "url": "http://amas-api:8000/api/agents/investigation/analyze",
                            "method": "POST",
                            "body": {
                                "entities": "{{ $json.entities }}",
                                "analysis_type": "deep",
                            },
                        },
                    },
                    {
                        "name": "Link Analysis",
                        "type": "n8n-nodes-base.httpRequest",
                        "parameters": {
                            "url": "http://amas-api:8000/api/agents/investigation/links",
                            "method": "POST",
                            "body": {
                                "entities": "{{ $json.entities }}",
                                "depth": "deep",
                            },
                        },
                    },
                    {
                        "name": "Generate Report",
                        "type": "n8n-nodes-base.httpRequest",
                        "parameters": {
                            "url": "http://amas-api:8000/api/agents/reporting/generate",
                            "method": "POST",
                            "body": {
                                "report_type": "investigation",
                                "data": "{{ $json }}",
                            },
                        },
                    },
                ],
            }

            # Threat Intelligence Workflow
            self.workflow_templates["threat_intelligence"] = {
                "name": "Threat Intelligence Workflow",
                "description": "Threat intelligence collection and analysis",
                "nodes": [
                    {
                        "name": "Schedule Trigger",
                        "type": "n8n-nodes-base.scheduleTrigger",
                        "parameters": {
                            "rule": {"interval": [{"field": "hours", "value": 6}]}
                        },
                    },
                    {
                        "name": "OSINT Collection",
                        "type": "n8n-nodes-base.httpRequest",
                        "parameters": {
                            "url": "http://amas-api:8000/api/agents/osint/collect",
                            "method": "POST",
                            "body": {
                                "sources": "{{ $json.threat_sources }}",
                                "keywords": "{{ $json.threat_keywords }}",
                                "filters": "{{ $json.filters }}",
                            },
                        },
                    },
                    {
                        "name": "Threat Analysis",
                        "type": "n8n-nodes-base.httpRequest",
                        "parameters": {
                            "url": "http://amas-api:8000/api/agents/data_analysis/threats",
                            "method": "POST",
                            "body": {
                                "data": "{{ $json }}",
                                "analysis_type": "threat_assessment",
                            },
                        },
                    },
                    {
                        "name": "Alert Generation",
                        "type": "n8n-nodes-base.httpRequest",
                        "parameters": {
                            "url": "http://amas-api:8000/api/alerts/create",
                            "method": "POST",
                            "body": {
                                "alert_type": "threat_intelligence",
                                "severity": "{{ $json.severity }}",
                                "content": "{{ $json.analysis }}",
                            },
                        },
                    },
                ],
            }

            self.logger.info("Workflow templates initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize workflow templates: {e}")
            raise

    async def authenticate(self) -> bool:
        """
        Authenticate with n8n instance.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            if self.n8n_api_key:
                # Use API key authentication
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.n8n_api_key}"}
                )
                self.auth_token = self.n8n_api_key
            else:
                # Use username/password authentication
                auth_url = f"{self.n8n_url}/api/auth/login"
                auth_data = {"email": self.username, "password": self.password}

                response = self.session.post(auth_url, json=auth_data)
                response.raise_for_status()

                auth_result = response.json()
                self.auth_token = auth_result.get("token")

                if self.auth_token:
                    self.session.headers.update(
                        {"Authorization": f"Bearer {self.auth_token}"}
                    )

            # Test authentication
            test_url = f"{self.n8n_url}/api/workflows"
            response = self.session.get(test_url)
            response.raise_for_status()

            self.logger.info("n8n authentication successful")
            return True

        except Exception as e:
            self.logger.error(f"n8n authentication failed: {e}")
            return False

    async def create_workflow(
        self,
        workflow_name: str,
        workflow_template: str,
        parameters: Dict[str, Any] = None,
    ) -> Optional[str]:
        """
        Create a new workflow in n8n.

        Args:
            workflow_name: Name for the workflow
            workflow_template: Template to use
            parameters: Parameters to customize the workflow

        Returns:
            Workflow ID if created successfully, None otherwise
        """
        try:
            if not await self.authenticate():
                return None

            if workflow_template not in self.workflow_templates:
                self.logger.error(f"Workflow template {workflow_template} not found")
                return None

            template = self.workflow_templates[workflow_template]

            # Customize workflow with parameters
            workflow_data = self._customize_workflow(template, parameters or {})

            # Create workflow
            create_url = f"{self.n8n_url}/api/workflows"
            workflow_payload = {
                "name": workflow_name,
                "nodes": workflow_data["nodes"],
                "connections": self._generate_connections(workflow_data["nodes"]),
                "active": True,
                "settings": {"executionOrder": "v1"},
            }

            response = self.session.post(create_url, json=workflow_payload)
            response.raise_for_status()

            workflow_result = response.json()
            workflow_id = workflow_result.get("id")

            self.logger.info(f"Workflow {workflow_name} created with ID {workflow_id}")
            return workflow_id

        except Exception as e:
            self.logger.error(f"Failed to create workflow {workflow_name}: {e}")
            return None

    def _customize_workflow(
        self, template: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customize workflow template with parameters."""
        try:
            customized_workflow = template.copy()

            # Apply parameter customizations
            for node in customized_workflow["nodes"]:
                if "parameters" in node:
                    # Customize node parameters based on template
                    if "url" in node["parameters"]:
                        # Replace placeholder URLs with actual endpoints
                        node["parameters"]["url"] = node["parameters"]["url"].replace(
                            "{{ $json.sources }}", str(parameters.get("sources", []))
                        )

                    if "body" in node["parameters"]:
                        # Customize request body
                        body = node["parameters"]["body"]
                        if isinstance(body, dict):
                            for key, value in body.items():
                                if isinstance(value, str) and "{{ $json." in value:
                                    # Replace template variables
                                    var_name = value.replace("{{ $json.", "").replace(
                                        " }}", ""
                                    )
                                    if var_name in parameters:
                                        node["parameters"]["body"][key] = parameters[
                                            var_name
                                        ]

            return customized_workflow

        except Exception as e:
            self.logger.error(f"Workflow customization failed: {e}")
            return template

    def _generate_connections(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate connections between workflow nodes."""
        try:
            connections = {}

            for i, node in enumerate(nodes):
                node_name = node["name"]

                if i < len(nodes) - 1:
                    next_node = nodes[i + 1]["name"]
                    connections[node_name] = {
                        "main": [
                            [{"node": next_node, "type": "main", "index": 0}],
                        ]
                    }

            return connections

        except Exception as e:
            self.logger.error(f"Connection generation failed: {e}")
            return {}

    async def execute_workflow(
        self, workflow_id: str, input_data: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Execute a workflow.

        Args:
            workflow_id: ID of the workflow to execute
            input_data: Input data for the workflow

        Returns:
            Execution ID if started successfully, None otherwise
        """
        try:
            if not await self.authenticate():
                return None

            # Start workflow execution
            execute_url = f"{self.n8n_url}/api/workflows/{workflow_id}/execute"
            execute_payload = {"data": input_data or {}, "mode": "trigger"}

            response = self.session.post(execute_url, json=execute_payload)
            response.raise_for_status()

            execution_result = response.json()
            execution_id = execution_result.get("executionId")

            if execution_id:
                self.metrics["workflows_executed"] += 1
                self.metrics["active_workflows"] += 1

                # Start monitoring execution
                asyncio.create_task(self._monitor_execution(workflow_id, execution_id))

            self.logger.info(
                f"Workflow {workflow_id} execution started: {execution_id}"
            )
            return execution_id

        except Exception as e:
            self.logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            self.metrics["workflows_failed"] += 1
            return None

    async def _monitor_execution(self, workflow_id: str, execution_id: str):
        """Monitor workflow execution status."""
        try:
            while True:
                # Check execution status
                status_url = f"{self.n8n_url}/api/executions/{execution_id}"
                response = self.session.get(status_url)

                if response.status_code == 200:
                    execution_data = response.json()
                    status = execution_data.get("status")

                    if status in ["success", "error", "cancelled"]:
                        # Execution completed
                        self.metrics["active_workflows"] = max(
                            0, self.metrics["active_workflows"] - 1
                        )

                        if status == "success":
                            self.logger.info(
                                f"Workflow {workflow_id} execution completed successfully"
                            )
                        else:
                            self.logger.warning(
                                f"Workflow {workflow_id} execution failed with status: {status}"
                            )

                        break

                # Wait before next check
                await asyncio.sleep(5)

        except Exception as e:
            self.logger.error(
                f"Execution monitoring failed for workflow {workflow_id}: {e}"
            )
            self.metrics["active_workflows"] = max(
                0, self.metrics["active_workflows"] - 1
            )

    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow status.

        Args:
            workflow_id: ID of the workflow

        Returns:
            Workflow status information or None if not found
        """
        try:
            if not await self.authenticate():
                return None

            # Get workflow details
            workflow_url = f"{self.n8n_url}/api/workflows/{workflow_id}"
            response = self.session.get(workflow_url)
            response.raise_for_status()

            workflow_data = response.json()

            # Get execution history
            executions_url = f"{self.n8n_url}/api/executions"
            params = {"workflowId": workflow_id, "limit": 10}
            response = self.session.get(executions_url, params=params)
            response.raise_for_status()

            executions_data = response.json()

            return {
                "workflow_id": workflow_id,
                "name": workflow_data.get("name"),
                "active": workflow_data.get("active", False),
                "created_at": workflow_data.get("createdAt"),
                "updated_at": workflow_data.get("updatedAt"),
                "recent_executions": executions_data.get("data", []),
                "status": "active" if workflow_data.get("active") else "inactive",
            }

        except Exception as e:
            self.logger.error(f"Failed to get workflow status {workflow_id}: {e}")
            return None

    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution status.

        Args:
            execution_id: ID of the execution

        Returns:
            Execution status information or None if not found
        """
        try:
            if not await self.authenticate():
                return None

            # Get execution details
            execution_url = f"{self.n8n_url}/api/executions/{execution_id}"
            response = self.session.get(execution_url)
            response.raise_for_status()

            execution_data = response.json()

            return {
                "execution_id": execution_id,
                "workflow_id": execution_data.get("workflowId"),
                "status": execution_data.get("status"),
                "started_at": execution_data.get("startedAt"),
                "finished_at": execution_data.get("finishedAt"),
                "data": execution_data.get("data"),
                "error": execution_data.get("error"),
            }

        except Exception as e:
            self.logger.error(f"Failed to get execution status {execution_id}: {e}")
            return None

    async def stop_workflow(self, workflow_id: str) -> bool:
        """
        Stop a workflow.

        Args:
            workflow_id: ID of the workflow to stop

        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            if not await self.authenticate():
                return False

            # Deactivate workflow
            update_url = f"{self.n8n_url}/api/workflows/{workflow_id}"
            update_payload = {"active": False}

            response = self.session.patch(update_url, json=update_payload)
            response.raise_for_status()

            self.logger.info(f"Workflow {workflow_id} stopped")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop workflow {workflow_id}: {e}")
            return False

    async def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.

        Args:
            workflow_id: ID of the workflow to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if not await self.authenticate():
                return False

            # Delete workflow
            delete_url = f"{self.n8n_url}/api/workflows/{workflow_id}"
            response = self.session.delete(delete_url)
            response.raise_for_status()

            self.logger.info(f"Workflow {workflow_id} deleted")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            return False

    async def get_workflows(self) -> List[Dict[str, Any]]:
        """
        Get all workflows.

        Returns:
            List of workflow information
        """
        try:
            if not await self.authenticate():
                return []

            # Get workflows
            workflows_url = f"{self.n8n_url}/api/workflows"
            response = self.session.get(workflows_url)
            response.raise_for_status()

            workflows_data = response.json()
            return workflows_data.get("data", [])

        except Exception as e:
            self.logger.error(f"Failed to get workflows: {e}")
            return []

    async def get_metrics(self) -> Dict[str, Any]:
        """Get integration metrics."""
        return {
            "metrics": self.metrics,
            "n8n_url": self.n8n_url,
            "authenticated": self.auth_token is not None,
            "timestamp": datetime.utcnow().isoformat(),
        }
