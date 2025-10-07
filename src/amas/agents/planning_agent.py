import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from amas.agents.base.intelligence_agent import IntelligenceAgent
from amas.core.message_bus import MessageBus
from amas.core.unified_orchestrator_v2 import (
    OrchestratorTask,
    TaskPriority,
    TaskStatus,
    UnifiedOrchestratorV2,
)

logger = logging.getLogger(__name__)


class PlanningAgent(IntelligenceAgent):
    """
    A specialized agent responsible for generating, refining, and optimizing task plans.

    This agent breaks down complex goals into actionable sub-tasks, assigns priorities,
    and can adapt plans based on execution feedback.
    """

    def __init__(
        self,
        agent_id: str,
        config: Dict[str, Any],
        orchestrator: UnifiedOrchestratorV2,
        message_bus: MessageBus,
    ):
        super().__init__(agent_id, config, orchestrator, message_bus)
        self.name = config.get("name", "Planning Agent")
        self.capabilities = config.get(
            "capabilities", ["task_planning", "plan_refinement", "resource_allocation"]
        )
        logger.info(
            f"PlanningAgent {self.agent_id} initialized with capabilities: {self.capabilities}"
        )

    async def execute_task(self, task: OrchestratorTask) -> Dict[str, Any]:
        """
        Executes a planning task.
        Expected task parameters: {"goal": "...", "context": {...}, "existing_plan": [...]}
        """
        goal = task.parameters.get("goal")
        context = task.parameters.get("context", {})
        existing_plan = task.parameters.get("existing_plan", [])

        if not goal:
            raise ValueError("PlanningAgent requires a 'goal' in task parameters.")

        try:
            if existing_plan:
                logger.info(
                    f"PlanningAgent {self.agent_id} refining existing plan for goal: {goal}"
                )
                new_plan = await self._refine_plan(goal, context, existing_plan)
            else:
                logger.info(
                    f"PlanningAgent {self.agent_id} generating new plan for goal: {goal}"
                )
                new_plan = await self._generate_plan(goal, context)

            return {"success": True, "plan": new_plan}
        except Exception as e:
            logger.error(
                f"PlanningAgent {self.agent_id} failed to execute task {task.id}: {e}"
            )
            return {"success": False, "error": str(e)}

    async def _generate_plan(
        self, goal: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generates a new task plan using the Universal AI Manager.
        """
        prompt = f"""
As a highly capable AI planning system, your task is to break down the following complex goal into a series of discrete, actionable sub-tasks. Each sub-task should be clearly defined, have a logical order, and specify the type of agent best suited to execute it.

Goal: {goal}

Context: {json.dumps(context, indent=2)}

Output the plan as a JSON array of objects. Each object should have the following structure:
{{
    "task_id": "unique_id_for_task",
    "description": "A clear description of the sub-task.",
    "agent_type": "The type of agent best suited for this task (e.g., 'RAGAgent', 'ToolAgent', 'CodeAgent', 'DataAgent', 'CreativeAgent').",
    "priority": "High|Medium|Low",
    "dependencies": ["task_id_1", "task_id_2"], 
    "parameters": {{}} 
}}

Ensure the plan is comprehensive, logical, and covers all aspects of achieving the goal. Focus on creating a robust and efficient sequence of operations.
"""

        response = await self._call_ai_manager(
            prompt=prompt, max_tokens=2000, temperature=0.7, task_type="plan_generation"
        )

        if response["success"]:
            try:
                plan = json.loads(response["content"])
                return plan
            except json.JSONDecodeError:
                logger.error(
                    f"Failed to parse AI manager response for plan generation: {response['content']}"
                )
                return []
        else:
            logger.error(f"AI manager failed for plan generation: {response['error']}")
            return []

    async def _refine_plan(
        self, goal: str, context: Dict[str, Any], existing_plan: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Refines an existing task plan using the Universal AI Manager.
        """
        prompt = f"""
As a highly capable AI planning system, your task is to review and refine the following existing plan to achieve the given goal. The plan should be optimized for efficiency, logical flow, and robustness. Adjust task descriptions, agent assignments, priorities, and dependencies as necessary. You may add, remove, or modify tasks.

Goal: {goal}

Context: {json.dumps(context, indent=2)}

Existing Plan: {json.dumps(existing_plan, indent=2)}

Output the refined plan as a JSON array of objects. Each object should have the following structure:
{{
    "task_id": "unique_id_for_task",
    "description": "A clear description of the sub-task.",
    "agent_type": "The type of agent best suited for this task (e.g., 'RAGAgent', 'ToolAgent', 'CodeAgent', 'DataAgent', 'CreativeAgent').",
    "priority": "High|Medium|Low",
    "dependencies": ["task_id_1", "task_id_2"], 
    "parameters": {{}} 
}}

Ensure the refined plan is comprehensive, logical, and covers all aspects of achieving the goal. Focus on creating a robust and efficient sequence of operations.
"""

        response = await self._call_ai_manager(
            prompt=prompt, max_tokens=2000, temperature=0.7, task_type="plan_refinement"
        )

        if response["success"]:
            try:
                refined_plan = json.loads(response["content"])
                return refined_plan
            except json.JSONDecodeError:
                logger.error(
                    f"Failed to parse AI manager response for plan refinement: {response['content']}"
                )
                return existing_plan
        else:
            logger.error(f"AI manager failed for plan refinement: {response['error']}")
            return existing_plan
