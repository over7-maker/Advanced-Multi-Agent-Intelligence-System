from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from amas.common.models import AgentStatus, OrchestratorTask, TaskPriority, TaskStatus
from amas.core.message_bus import MessageBus
from amas.services.universal_ai_manager import (
    UniversalAIManager,
    get_universal_ai_manager,
)

logger = logging.getLogger(__name__)


class IntelligenceAgent(ABC):
    """
    Base class for all intelligent agents in the AMAS system.

    Defines the common interface and core functionalities for agents,
    including interaction with the Universal AI Manager, task processing,
    and state management. Also includes basic learning and adaptation mechanisms.
    """

    def __init__(
        self,
        agent_id: str,
        config: Dict[str, Any],
        orchestrator: Any,
        message_bus: MessageBus,
    ):
        self.agent_id = agent_id
        self.config = config
        self.orchestrator = orchestrator
        self.message_bus = message_bus
        self.universal_ai_manager: UniversalAIManager = get_universal_ai_manager()
        self.status: str = "idle"
        self.current_task: Optional[OrchestratorTask] = None
        self.last_active: datetime = datetime.now()
        self.metrics: Dict[str, Any] = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_processing_time": 0.0,
            "ai_requests_made": 0,
            "tokens_used": 0,
            "success_rate": 1.0,  # Initial success rate
            "average_response_time": 0.0,
        }
        # Adaptation parameters
        self.llm_temperature: float = config.get("initial_llm_temperature", 0.7)
        self.llm_max_tokens: int = config.get("initial_llm_max_tokens", 1000)

        logger.info(
            f'Agent {self.agent_id} initialized with config: {self.config.get("name", "Unnamed Agent")}'
        )

    @abstractmethod
    async def execute_task(self, task: OrchestratorTask) -> Dict[str, Any]:
        """
        Abstract method to be implemented by concrete agent classes.
        This method defines the core logic for how an agent processes a task.
        """
        pass

    async def process_task(self, task: OrchestratorTask):
        """
        Handles the lifecycle of a task for the agent.
        Updates agent status, calls execute_task, and updates metrics.
        Sends task updates to the orchestrator via the message bus.
        """
        self.status = "processing"
        self.current_task = task
        self.last_active = datetime.now()
        start_time = time.time()
        task_result = {"success": False, "message": "Task processing failed."}
        error_message = None

        try:
            logger.info(
                f"Agent {self.agent_id} starting task {task.id}: {task.description}"
            )
            # Notify orchestrator that task is in progress
            await self.message_bus.publish(
                "orchestrator_updates",
                {
                    "sender_id": self.agent_id,
                    "type": "task_update",
                    "task_id": task.id,
                    "payload": {"status": TaskStatus.IN_PROGRESS.value},
                },
            )

            task_result = await self.execute_task(task)
            self.metrics["tasks_completed"] += 1
            self.status = "idle"
            logger.info(f"Agent {self.agent_id} completed task {task.id}.")
            # Notify orchestrator of completion
            await self.message_bus.publish(
                "orchestrator_updates",
                {
                    "sender_id": self.agent_id,
                    "type": "task_update",
                    "task_id": task.id,
                    "payload": {
                        "status": TaskStatus.COMPLETED.value,
                        "result": task_result,
                    },
                },
            )
            # Provide feedback for learning
            await self._provide_feedback(task.id, True, task_result)

        except Exception as e:
            logger.error(f"Agent {self.agent_id} failed to process task {task.id}: {e}")
            self.metrics["tasks_failed"] += 1
            self.status = "error"
            error_message = str(e)
            task_result["message"] = f"Task processing failed: {error_message}"
            # Notify orchestrator of failure
            await self.message_bus.publish(
                "orchestrator_updates",
                {
                    "sender_id": self.agent_id,
                    "type": "task_update",
                    "task_id": task.id,
                    "payload": {
                        "status": TaskStatus.FAILED.value,
                        "error": error_message,
                        "result": task_result,
                    },
                },
            )
            # Provide feedback for learning
            await self._provide_feedback(task.id, False, {"error": error_message})

        finally:
            end_time = time.time()
            duration = end_time - start_time
            self.metrics["total_processing_time"] += duration
            self.metrics["average_response_time"] = (
                (
                    self.metrics["average_response_time"]
                    * (
                        self.metrics["tasks_completed"]
                        + self.metrics["tasks_failed"]
                        - 1
                    )
                    + duration
                )
                / (self.metrics["tasks_completed"] + self.metrics["tasks_failed"])
                if (self.metrics["tasks_completed"] + self.metrics["tasks_failed"]) > 0
                else 0.0
            )
            self.metrics["success_rate"] = (
                self.metrics["tasks_completed"]
                / (self.metrics["tasks_completed"] + self.metrics["tasks_failed"])
                if (self.metrics["tasks_completed"] + self.metrics["tasks_failed"]) > 0
                else 1.0
            )
            self.current_task = None

    async def get_status(self) -> Dict[str, Any]:
        """
        Returns the current status and metrics of the agent.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.config.get("name", "Unnamed Agent"),
            "status": self.status,
            "last_active": self.last_active.isoformat(),
            "current_task": self.current_task.id if self.current_task else None,
            "metrics": self.metrics,
            "llm_parameters": {
                "temperature": self.llm_temperature,
                "max_tokens": self.llm_max_tokens,
            },
            "ai_manager_health": (
                await self.universal_ai_manager.get_status()
                if self.universal_ai_manager
                else "N/A"
            ),
        }

    async def _call_ai_manager(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Helper method to call the Universal AI Manager and update agent metrics.
        Uses agent's adaptive LLM parameters.
        """
        self.metrics["ai_requests_made"] += 1
        # Override kwargs with adaptive parameters if not explicitly provided
        kwargs.setdefault("temperature", self.llm_temperature)
        kwargs.setdefault("max_tokens", self.llm_max_tokens)

        response = await self.universal_ai_manager.generate_response(
            prompt, system_prompt, **kwargs
        )
        if response["success"]:
            self.metrics["tokens_used"] += response.get("tokens_used", 0)
        return response

    async def update_config(self, new_config: Dict[str, Any]):
        """
        Updates the agent's configuration.
        """
        self.config.update(new_config)
        self.llm_temperature = new_config.get(
            "initial_llm_temperature", self.llm_temperature
        )
        self.llm_max_tokens = new_config.get(
            "initial_llm_max_tokens", self.llm_max_tokens
        )
        logger.info(f"Agent {self.agent_id} configuration updated.")

    async def start(self):
        """
        Starts the agent, subscribing it to relevant message bus topics.
        """
        await self.message_bus.subscribe(
            f"agent_tasks_{self.agent_id}", self._handle_incoming_message
        )
        logger.info(f"Agent {self.agent_id} started and subscribed to its task queue.")

    async def stop(self):
        """
        Stops the agent, unsubscribing it from the message bus.
        """
        await self.message_bus.unsubscribe(
            f"agent_tasks_{self.agent_id}", self._handle_incoming_message
        )
        logger.info(f"Agent {self.agent_id} stopped and unsubscribed from MessageBus.")

    async def _handle_incoming_message(self, message: Dict[str, Any]):
        """
        Handles messages received directly by this agent.
        """
        message_type = message.get("type")
        payload = message.get("payload")

        if message_type == "assign_task":
            task = OrchestratorTask(**payload["task_data"])
            asyncio.create_task(self.process_task(task))
        elif message_type == "update_config":
            await self.update_config(payload["new_config"])
        else:
            logger.warning(
                f"Agent {self.agent_id} received unhandled message type: {message_type}"
            )

    async def _provide_feedback(
        self, task_id: str, success: bool, details: Dict[str, Any]
    ):
        """
        Sends feedback about task execution to the orchestrator for learning.
        """
        feedback_message = {
            "sender_id": self.agent_id,
            "type": "task_feedback",
            "task_id": task_id,
            "payload": {
                "success": success,
                "details": details,
                "metrics": self.metrics,
            },
        }
        await self.message_bus.publish("orchestrator_feedback", feedback_message)
        logger.debug(
            f"Agent {self.agent_id} sent feedback for task {task_id}: success={success}"
        )

    async def adapt_parameters(
        self, success_rate_threshold: float = 0.8, adjustment_factor: float = 0.1
    ):
        """
        Adapts LLM parameters based on recent performance.
        This is a simple heuristic; more advanced RL could be integrated here.
        """
        if self.metrics["success_rate"] < success_rate_threshold:
            logger.warning(
                f'Agent {self.agent_id} success rate ({self.metrics["success_rate"]:.2f}) below threshold. Adapting parameters.'
            )
            # If success rate is low, try to make LLM more deterministic (lower temperature)
            self.llm_temperature = max(0.1, self.llm_temperature - adjustment_factor)
            # And potentially allow more tokens for more detailed responses
            self.llm_max_tokens = min(
                4000, self.llm_max_tokens + 200
            )  # Cap at 4000 for example
            logger.info(
                f"Agent {self.agent_id} adapted: new temperature={self.llm_temperature:.2f}, max_tokens={self.llm_max_tokens}"
            )
        elif (
            self.metrics["success_rate"] > (success_rate_threshold + 0.1)
            and self.llm_temperature < 1.0
        ):
            logger.info(
                f'Agent {self.agent_id} success rate ({self.metrics["success_rate"]:.2f}) is high. Increasing temperature slightly.'
            )
            # If success rate is high, allow LLM to be more creative (higher temperature)
            self.llm_temperature = min(
                1.0, self.llm_temperature + adjustment_factor / 2
            )
            logger.info(
                f"Agent {self.agent_id} adapted: new temperature={self.llm_temperature:.2f}"
            )
