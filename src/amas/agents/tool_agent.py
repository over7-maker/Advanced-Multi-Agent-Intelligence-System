import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from amas.agents.base.intelligence_agent import IntelligenceAgent
from amas.core.message_bus import MessageBus
from amas.core.unified_orchestrator_v2 import OrchestratorTask, UnifiedOrchestratorV2

logger = logging.getLogger(__name__)


class ToolAgent(IntelligenceAgent):
    """
    A specialized agent capable of executing external tools or functions.

    This agent acts as an interface to various external capabilities,
    allowing the AMAS system to interact with the outside world.
    """

    def __init__(
        self,
        agent_id: str,
        config: Dict[str, Any],
        orchestrator: UnifiedOrchestratorV2,
        message_bus: MessageBus,
    ):
        super().__init__(agent_id, config, orchestrator, message_bus)
        self.name = config.get("name", "Tool Agent")
        self.capabilities = config.get("capabilities", ["tool_execution"])
        self.available_tools: Dict[str, Callable] = {}
        self._load_tools(config.get("tools", []))
        logger.info(
            f"ToolAgent {self.agent_id} initialized with tools: {list(self.available_tools.keys())}"
        )

    def _load_tools(self, tool_configs: List[Dict[str, Any]]):
        """
        Loads tools based on configuration. This is a placeholder for dynamic tool loading.
        In a real system, this would involve importing modules or registering functions.
        """
        for tool_config in tool_configs:
            tool_name = tool_config.get("name")
            tool_function_path = tool_config.get("function_path")
            if tool_name and tool_function_path:
                # Simulate loading a tool function
                # In a real scenario, you'd use importlib to load the actual function
                self.available_tools[tool_name] = self._simulate_tool_function(
                    tool_name, tool_config
                )
                logger.info(f"Loaded simulated tool: {tool_name}")
            else:
                logger.warning(f"Invalid tool configuration: {tool_config}")

    def _simulate_tool_function(self, tool_name: str, tool_config: Dict[str, Any]):
        """
        A placeholder for a tool function. In reality, this would be the actual tool logic.
        """

        async def simulated_tool(*args, **kwargs):
            logger.info(
                f"Executing simulated tool '{tool_name}' with args: {args}, kwargs: {kwargs}"
            )
            await asyncio.sleep(1)  # Simulate work
            return {
                "tool_name": tool_name,
                "status": "success",
                "output": f"Executed {tool_name} with {kwargs}",
            }

        return simulated_tool

    async def execute_task(self, task: OrchestratorTask) -> Dict[str, Any]:
        """
        Executes a tool based on the task parameters.
        Expected task parameters: {"tool_name": "tool_id", "tool_args": {...}}
        """
        tool_name = task.parameters.get("tool_name")
        tool_args = task.parameters.get("tool_args", {})

        if not tool_name:
            raise ValueError("ToolAgent requires 'tool_name' in task parameters.")

        tool_function = self.available_tools.get(tool_name)
        if not tool_function:
            raise ValueError(f"Tool '{tool_name}' not found or not available.")

        try:
            logger.info(
                f"ToolAgent {self.agent_id} executing tool '{tool_name}' for task {task.id}"
            )
            result = await tool_function(**tool_args)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed for task {task.id}: {e}")
            return {"success": False, "error": str(e)}

    async def add_tool(
        self,
        tool_name: str,
        tool_function: Callable,
        tool_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Dynamically adds a tool to the agent.
        """
        self.available_tools[tool_name] = tool_function
        if tool_config:
            self.config.setdefault("tools", []).append(tool_config)
        logger.info(f"Tool '{tool_name}' added to ToolAgent {self.agent_id}.")

    async def remove_tool(self, tool_name: str):
        """
        Removes a tool from the agent.
        """
        if tool_name in self.available_tools:
            del self.available_tools[tool_name]
            self.config["tools"] = [
                t for t in self.config.get("tools", []) if t.get("name") != tool_name
            ]
            logger.info(f"Tool '{tool_name}' removed from ToolAgent {self.agent_id}.")
        else:
            logger.warning(
                f"Attempted to remove non-existent tool '{tool_name}' from ToolAgent {self.agent_id}."
            )
