#!/usr/bin/env python3
"""
Agent-1: Workflow Orchestrator
Intelligent workflow routing and scheduling for optimal performance
"""

import json
from pathlib import Path
from typing import Any, Dict

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.amas.agents.base_agent import BaseAgent


class WorkflowOrchestratorAgent(BaseAgent):
    """Agent-1: Intelligent workflow routing and scheduling"""
    
    def __init__(self, orchestrator=None):
        super().__init__("workflow_orchestrator", orchestrator)
        self.workflow_registry = {}
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize workflow registry"""
        # Load workflow configurations
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.yml"):
                if workflow_file.name.startswith("00-"):
                    continue  # Skip orchestrator workflows
                self.workflow_registry[workflow_file.stem] = {
                    "path": str(workflow_file),
                    "name": workflow_file.stem
                }
        
        return {
            "success": True,
            "workflows_registered": len(self.workflow_registry),
            "message": f"Registered {len(self.workflow_registry)} workflows"
        }
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intelligent workflow routing"""
        task_type = context.get("task_type", "general")
        task_data = context.get("task_data", {})
        
        # Use AI to determine optimal workflow routing
        system_message = """You are a workflow orchestration expert. Analyze the task and recommend the best workflow routing strategy.
Consider: task complexity, resource requirements, dependencies, and current system load."""
        
        user_prompt = f"""Task Type: {task_type}
Task Data: {json.dumps(task_data, indent=2)}
Available Workflows: {', '.join(self.workflow_registry.keys())}

Recommend:
1. Which workflow(s) should handle this task?
2. Execution order (parallel vs sequential)?
3. Priority level?
4. Estimated execution time?"""
        
        ai_result = await self._call_ai(
            task_type="pr_analysis",
            system_message=system_message,
            user_prompt=user_prompt
        )
        
        if not ai_result.get("success"):
            return {
                "success": False,
                "error": "AI routing failed",
                "fallback": "default_sequential"
            }
        
        # Parse AI recommendation
        recommendation = ai_result.get("response", "")
        
        return {
            "success": True,
            "recommendation": recommendation,
            "workflows_available": len(self.workflow_registry),
            "routing_strategy": "ai_optimized"
        }
