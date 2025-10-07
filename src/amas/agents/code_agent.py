import asyncio
import logging
import json
from typing import Any, Dict, List, Optional

from amas.agents.base.intelligence_agent import IntelligenceAgent
from amas.core.unified_orchestrator_v2 import UnifiedOrchestratorV2, OrchestratorTask
from amas.core.message_bus import MessageBus

logger = logging.getLogger(__name__)

class CodeAgent(IntelligenceAgent):
    """
    A specialized agent capable of writing, debugging, and executing code.

    This agent can generate code snippets, run them in a sandboxed environment,
    and debug issues based on execution results.
    """

    def __init__(
        self,
        agent_id: str,
        config: Dict[str, Any],
        orchestrator: UnifiedOrchestratorV2,
        message_bus: MessageBus,
    ):
        super().__init__(agent_id, config, orchestrator, message_bus)

        self.name = config.get("name", "Code Agent")
        self.capabilities = config.get("capabilities", ["code_generation", "code_execution", "code_debugging"])
        logger.info(f"CodeAgent {self.agent_id} initialized with capabilities: {self.capabilities}")

    async def execute_task(self, task: OrchestratorTask) -> Dict[str, Any]:
        """
        Executes a code-related task.
        Expected task parameters: {"code_task_type": "generate|execute|debug", "details": {...}}
        """
        code_task_type = task.parameters.get("code_task_type")
        details = task.parameters.get("details", {})

        if not code_task_type:
            raise ValueError("CodeAgent requires a 'code_task_type' in task parameters.")

        try:
            if code_task_type == "generate":
                result = await self._generate_code(details)
            elif code_task_type == "execute":
                result = await self._execute_code(details)
            elif code_task_type == "debug":
                result = await self._debug_code(details)
            else:
                raise ValueError(f"Unknown code_task_type: {code_task_type}")
            
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"CodeAgent {self.agent_id} failed to execute task {task.id}: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_code(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates code based on a prompt and context using the Universal AI Manager.
        """
        prompt = details.get("prompt")
        language = details.get("language", "python")
        context = details.get("context", {})

        if not prompt:
            raise ValueError("Code generation requires a 'prompt'.")

        llm_prompt = f"""
Generate {language} code based on the following requirements and context:

Requirements: {prompt}

Context: {json.dumps(context, indent=2)}

Provide only the code, enclosed in triple backticks, without any additional explanations.
"""
        response = await self._call_ai_manager(
            prompt=llm_prompt, max_tokens=2000, temperature=0.7, task_type="code_generation"
        )

        if response["success"]:
            code_content = response["content"].strip()
            # Extract code block if present
            if code_content.startswith("```") and code_content.endswith("```"):
                code_content = code_content.split("\n", 1)[1].rsplit("\n", 1)[0]
            return {"generated_code": code_content, "language": language}
        else:
            raise Exception(f"AI manager failed to generate code: {response['error']}")

    async def _execute_code(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes provided code in a sandboxed environment.
        This is a placeholder for actual sandbox execution.
        """
        code = details.get("code")
        language = details.get("language", "python")
        timeout = details.get("timeout", 30)

        if not code:
            raise ValueError("Code execution requires 'code'.")

        logger.info(f"Simulating execution of {language} code:\n{code[:100]}...")
        await asyncio.sleep(2) # Simulate execution time

        # In a real system, this would involve a secure sandbox execution environment
        # For now, we simulate success/failure based on a simple check or random chance
        if "raise Exception" in code:
            return {"stdout": "", "stderr": "Simulated error during execution.", "exit_code": 1}
        else:
            return {"stdout": "Simulated code execution successful.", "stderr": "", "exit_code": 0}

    async def _debug_code(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Debugs code based on provided code, error, and context using the Universal AI Manager.
        """
        code = details.get("code")
        error_message = details.get("error_message")
        context = details.get("context", {})
        language = details.get("language", "python")

        if not code or not error_message:
            raise ValueError("Code debugging requires 'code' and 'error_message'.")

        llm_prompt = f"""
Analyze the following {language} code and error message to identify the bug and suggest a fix.

Code:
``` {language}
{code}
```

Error Message:
{error_message}

Context: {json.dumps(context, indent=2)}

Provide a detailed explanation of the bug, the proposed fix, and the corrected code. Output in JSON format with keys: "explanation", "proposed_fix", "corrected_code".
"""
        response = await self._call_ai_manager(
            prompt=llm_prompt, max_tokens=1500, temperature=0.5, task_type="code_debugging"
        )

        if response["success"]:
            try:
                debug_info = json.loads(response["content"])
                return debug_info
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI manager response for code debugging: {response['content']}")
                return {"explanation": "Failed to parse debug info.", "proposed_fix": "", "corrected_code": code}
        else:
            raise Exception(f"AI manager failed to debug code: {response['error']}")

