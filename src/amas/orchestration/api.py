"""
REST API Integration for Orchestration System

Provides HTTP endpoints for interacting with the orchestration system.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json

from .task_decomposer import get_task_decomposer
from .agent_hierarchy import get_hierarchy_manager
from .agent_communication import get_communication_bus
from .workflow_executor import get_workflow_executor
from .health import get_health_checker
from .utils import get_metrics_collector
from .config import get_config

logger = logging.getLogger(__name__)

class OrchestrationAPI:
    """
    REST API wrapper for orchestration system.
    
    This class provides HTTP-like interface methods that can be integrated
    with web frameworks like FastAPI, Flask, or used directly.
    """
    
    def __init__(self):
        self.task_decomposer = get_task_decomposer()
        self.hierarchy_manager = get_hierarchy_manager()
        self.communication_bus = get_communication_bus()
        self.workflow_executor = get_workflow_executor()
        self.health_checker = get_health_checker()
        self.metrics_collector = get_metrics_collector()
        self.config = get_config()
    
    async def create_workflow(self, user_request: str, user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create and execute a new workflow from user request.
        
        Args:
            user_request: Natural language description of the task
            user_preferences: Optional user preferences (priority, deadline, etc.)
            
        Returns:
            Dictionary with workflow execution ID and initial status
        """
        try:
            execution_id = await self.workflow_executor.execute_workflow(
                user_request,
                user_preferences or {}
            )
            
            status = self.workflow_executor.get_execution_status(execution_id)
            
            return {
                "success": True,
                "execution_id": execution_id,
                "status": status,
                "message": "Workflow execution started successfully"
            }
        except Exception as e:
            logger.error(f"Error creating workflow: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create workflow"
            }
    
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get current status of a workflow execution.
        
        Args:
            execution_id: Execution ID of the workflow
            
        Returns:
            Dictionary with workflow status and progress
        """
        status = self.workflow_executor.get_execution_status(execution_id)
        
        if not status:
            return {
                "success": False,
                "error": "Workflow not found",
                "execution_id": execution_id
            }
        
        return {
            "success": True,
            "execution_id": execution_id,
            "status": status
        }
    
    async def get_hierarchy_status(self) -> Dict[str, Any]:
        """
        Get current status of the agent hierarchy.
        
        Returns:
            Dictionary with hierarchy status and agent information
        """
        try:
            status = self.hierarchy_manager.get_hierarchy_status()
            return {
                "success": True,
                "hierarchy": status,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting hierarchy status: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_communication_metrics(self) -> Dict[str, Any]:
        """
        Get communication system metrics.
        
        Returns:
            Dictionary with communication metrics
        """
        try:
            metrics = await self.communication_bus.get_communication_metrics()
            return {
                "success": True,
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting communication metrics: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of the orchestration system.
        
        Returns:
            Dictionary with health status of all components
        """
        try:
            health = await self.health_checker.check_all()
            return {
                "success": True,
                "health": health
            }
        except Exception as e:
            logger.error(f"Error getting health status: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "overall_status": "unknown"
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get system-wide metrics.
        
        Returns:
            Dictionary with operation metrics
        """
        try:
            metrics = self.metrics_collector.get_metrics()
            return {
                "success": True,
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def decompose_task(self, user_request: str) -> Dict[str, Any]:
        """
        Decompose a task without executing it.
        
        Args:
            user_request: Natural language description of the task
            
        Returns:
            Dictionary with workflow plan (not executed)
        """
        try:
            workflow_plan = await self.task_decomposer.decompose_task(user_request)
            serialized = self.task_decomposer.serialize_workflow(workflow_plan)
            
            return {
                "success": True,
                "workflow_plan": serialized,
                "message": "Task decomposed successfully"
            }
        except Exception as e:
            logger.error(f"Error decomposing task: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to decompose task"
            }
    
    async def get_configuration(self) -> Dict[str, Any]:
        """
        Get current orchestration configuration.
        
        Returns:
            Dictionary with current configuration
        """
        try:
            config_dict = self.config.to_dict()
            return {
                "success": True,
                "configuration": config_dict,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting configuration: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_api_documentation(self) -> Dict[str, Any]:
        """
        Get API documentation with available endpoints.
        
        Returns:
            Dictionary with API endpoint documentation
        """
        return {
            "api_version": "1.0.0",
            "endpoints": {
                "POST /workflows": {
                    "description": "Create and execute a new workflow",
                    "parameters": {
                        "user_request": "string (required) - Task description",
                        "user_preferences": "object (optional) - User preferences"
                    },
                    "returns": "Workflow execution ID and status"
                },
                "GET /workflows/{execution_id}": {
                    "description": "Get workflow execution status",
                    "parameters": {
                        "execution_id": "string (required) - Execution ID"
                    },
                    "returns": "Workflow status and progress"
                },
                "GET /hierarchy": {
                    "description": "Get agent hierarchy status",
                    "returns": "Hierarchy status and agent information"
                },
                "GET /communication/metrics": {
                    "description": "Get communication system metrics",
                    "returns": "Communication metrics and statistics"
                },
                "GET /health": {
                    "description": "Get system health status",
                    "returns": "Health status of all components"
                },
                "GET /metrics": {
                    "description": "Get system-wide metrics",
                    "returns": "Operation metrics and statistics"
                },
                "POST /decompose": {
                    "description": "Decompose task without execution",
                    "parameters": {
                        "user_request": "string (required) - Task description"
                    },
                    "returns": "Workflow plan (not executed)"
                },
                "GET /config": {
                    "description": "Get current configuration",
                    "returns": "Orchestration configuration"
                }
            }
        }

# Global API instance
_global_api: Optional[OrchestrationAPI] = None

def get_api() -> OrchestrationAPI:
    """Get global orchestration API instance"""
    global _global_api
    if _global_api is None:
        _global_api = OrchestrationAPI()
    return _global_api
