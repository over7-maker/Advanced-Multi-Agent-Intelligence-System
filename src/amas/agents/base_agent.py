"""
Base Agent Class - Foundation for all specialized agents
Implements PART_3 requirements with AI router integration
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from src.amas.ai.enhanced_router_class import AIResponse, get_ai_router
from src.amas.agents.tools import get_tool_registry, AgentTool
from src.amas.agents.memory import get_agent_memory
from src.amas.agents.communication import (
    get_communication_protocol,
    get_event_bus,
    get_shared_context,
    AgentMessage,
    MessagePriority,
)

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all specialized agents
    
    ✅ Standardized interface
    ✅ AI provider integration via router
    ✅ Tool execution
    ✅ Memory integration
    ✅ Error handling
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        system_prompt: str,
        tools: Optional[List[Any]] = None,
        model_preference: Optional[str] = None,  # None = use local models first
        strategy: str = "quality_first"
    ):
        self.id = agent_id
        self.name = name
        self.type = agent_type
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model_preference = model_preference
        self.strategy = strategy
        
        # Get AI router
        self.ai_router = get_ai_router()
        
        # Get tool registry
        self.tool_registry = get_tool_registry()
        
        # Get agent memory
        self.memory = get_agent_memory(agent_id)
        
        # Communication capabilities
        self.communication = get_communication_protocol(agent_id)
        self.event_bus = get_event_bus()
        self.shared_context = get_shared_context(agent_id)
        
        # Event handlers
        self.event_handlers = {}
        
        # Tool usage tracking
        self.tool_usage_count = {}
        self.tool_success_count = {}
        
        # Performance tracking
        self.expertise_score = 0.90  # Default
        self.executions = 0
        self.successes = 0
        self.total_duration = 0.0
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any],
        use_react: bool = False,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Execute agent task
        
        Args:
            task_id: Task identifier
            target: Target of the task
            parameters: Task parameters
            use_react: Whether to use ReAct pattern (multi-step reasoning)
            max_iterations: Maximum iterations for ReAct pattern
            
        Returns:
            Dict with result, success, duration, etc.
        """
        
        # Use ReAct pattern if requested
        if use_react:
            return await self.execute_with_react(task_id, target, parameters, max_iterations)
        
        execution_start = time.time()
        
        try:
            # STEP 0: Load relevant memory
            similar_tasks = await self.memory.retrieve_similar_tasks({
                "task_type": self.type,
                "target": target,
                "parameters": parameters
            }, limit=3)
            
            # Get learned patterns
            patterns = await self.memory.get_learned_patterns(self.type)
            
            # Enhance parameters with memory context
            enhanced_parameters = parameters.copy()
            if similar_tasks:
                enhanced_parameters["_similar_tasks"] = similar_tasks[:2]  # Include top 2 similar
            if patterns:
                enhanced_parameters["_learned_patterns"] = patterns
            
            # STEP 1: Prepare prompt (with memory context)
            prompt = await self._prepare_prompt(target, enhanced_parameters)
            
            # STEP 2: Call AI via router (WITH FALLBACK)
            logger.info(f"Agent {self.name}: Calling AI with strategy '{self.strategy}'")
            
            # Use local models first if no preference specified
            model_pref = self.model_preference
            if not model_pref or model_pref == "gpt-4-turbo-preview":
                # Check for local models first
                from src.amas.ai.enhanced_router_v2 import get_available_providers
                available = get_available_providers()
                if "ollama" in available:
                    model_pref = None  # Let router choose best local model
            
            ai_response: AIResponse = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=model_pref,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"Agent {self.name}: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 3: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 4: Execute tools if needed (multi-tool orchestration enabled by default)
            # Check if tools should be used (explicit flag or if agent has tools registered)
            should_use_tools = (
                parsed_result.get("requires_tools", False) or
                (self.tools and parameters.get("use_multi_tool", True))
            )
            
            if should_use_tools:
                # Enhance parsed_result with task context for multi-tool orchestration
                parsed_result["task_type"] = self.type
                parsed_result["description"] = target
                parsed_result["use_multi_tool"] = parameters.get("use_multi_tool", True)
                parsed_result["tool_strategy"] = parameters.get("tool_strategy", "comprehensive")
                parsed_result["max_tools"] = parameters.get("max_tools", 5)
                parsed_result["requires_tools"] = True  # Ensure tools are executed
                
                tool_results = await self._execute_tools(parsed_result)
                parsed_result["tool_results"] = tool_results
                
                # If multi-tool orchestration was used, merge aggregated results
                if tool_results and any(r.get("metadata", {}).get("multi_tool") for r in tool_results):
                    aggregated = next(
                        (r for r in tool_results if r.get("tool") == "aggregated"),
                        None
                    )
                    if aggregated and aggregated.get("result"):
                        # Merge aggregated findings into parsed_result
                        parsed_result.update(aggregated["result"].get("primary_findings", {}))
                        if aggregated["result"].get("synthesis"):
                            parsed_result["synthesis"] = aggregated["result"]["synthesis"]
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            # Store in memory for learning
            result_dict = {
                "success": True,
                "agent_id": self.id,
                "agent_name": self.name,
                "result": parsed_result,
                "duration": execution_duration,
                "quality_score": parsed_result.get("quality_score", 0.8),
                "ai_provider": ai_response.provider,
                "ai_model": ai_response.model,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "fallback_used": ai_response.fallback_used
            }
            
            # Store execution in memory
            await self.memory.store_execution(
                task_id=task_id,
                result=result_dict,
                context={
                    "target": target,
                    "parameters": parameters,
                    "task_type": self.type,
                    "tools_used": [t.name for t in self._select_tools(parsed_result)]
                }
            )
            
            return result_dict
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            
            logger.error(f"Agent {self.name} execution failed: {e}", exc_info=True)
            
            self.executions += 1
            self.total_duration += execution_duration
            
            return {
                "success": False,
                "agent_id": self.id,
                "agent_name": self.name,
                "error": str(e),
                "duration": execution_duration
            }
    
    async def execute_with_react(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any],
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Execute task using ReAct (Reasoning-Acting-Observing) pattern
        
        Args:
            task_id: Task identifier
            target: Target of the task
            parameters: Task parameters
            max_iterations: Maximum number of ReAct iterations
            
        Returns:
            Dict with result, success, duration, reasoning trace, etc.
        """
        execution_start = time.time()
        reasoning_trace = []
        context = {
            "task_id": task_id,
            "target": target,
            "parameters": parameters,
            "iteration": 0
        }
        
        try:
            logger.info(f"Agent {self.name}: Starting ReAct execution for task {task_id}")
            
            for iteration in range(max_iterations):
                context["iteration"] = iteration
                
                # THINK: Reason about what to do next
                logger.debug(f"Agent {self.name}: [Iteration {iteration}] Thinking...")
                reasoning = await self._think(context)
                reasoning_trace.append({
                    "iteration": iteration,
                    "step": "think",
                    "reasoning": reasoning
                })
                
                # ACT: Execute selected action/tool
                logger.debug(f"Agent {self.name}: [Iteration {iteration}] Acting...")
                action_result = await self._act(reasoning, context)
                reasoning_trace.append({
                    "iteration": iteration,
                    "step": "act",
                    "action_result": action_result
                })
                
                # OBSERVE: Analyze results
                logger.debug(f"Agent {self.name}: [Iteration {iteration}] Observing...")
                observation = await self._observe(action_result, context)
                reasoning_trace.append({
                    "iteration": iteration,
                    "step": "observe",
                    "observation": observation
                })
                
                # Update context with observation
                context.update(observation.get("context_updates", {}))
                
                # Check if task is complete
                if self._is_complete(context, observation):
                    logger.info(f"Agent {self.name}: Task {task_id} completed after {iteration + 1} iterations")
                    break
            
            execution_duration = time.time() - execution_start
            
            # Final result aggregation
            final_result = await self._aggregate_react_results(reasoning_trace, context)
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": True,
                "agent_id": self.id,
                "agent_name": self.name,
                "result": final_result,
                "duration": execution_duration,
                "reasoning_trace": reasoning_trace,
                "iterations": len(reasoning_trace) // 3,  # Each iteration has think, act, observe
                "react_pattern": True
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            
            logger.error(f"Agent {self.name} ReAct execution failed: {e}", exc_info=True)
            
            self.executions += 1
            self.total_duration += execution_duration
            
            return {
                "success": False,
                "agent_id": self.id,
                "agent_name": self.name,
                "error": str(e),
                "duration": execution_duration,
                "reasoning_trace": reasoning_trace,
                "react_pattern": True
            }
    
    async def _think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Think: Generate reasoning about next steps
        
        Override in subclasses for agent-specific reasoning
        """
        # Default: Use AI to generate reasoning
        try:
            reasoning_prompt = f"""Based on the current context, what should I do next?

Context:
- Task ID: {context.get('task_id')}
- Target: {context.get('target')}
- Parameters: {context.get('parameters')}
- Iteration: {context.get('iteration')}

Available tools: {', '.join([t.name for t in self._select_tools(context)]) if self._select_tools(context) else 'None'}

Think about:
1. What information do I need?
2. What tools should I use?
3. What is my next action?

Respond in JSON format:
{{
    "analysis": "Your analysis",
    "next_action": "action_name",
    "tool_to_use": "tool_name or null",
    "reasoning": "Why this action"
}}"""
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=reasoning_prompt,
                model_preference=self.model_preference,
                max_tokens=1000,
                temperature=0.7,
                system_prompt=f"{self.system_prompt}\n\nYou are reasoning about the next step in a multi-step task.",
                strategy=self.strategy
            )
            
            # Parse reasoning
            try:
                import json
                reasoning = json.loads(ai_response.content)
            except Exception:
                reasoning = {
                    "analysis": ai_response.content,
                    "next_action": "collect_data",
                    "tool_to_use": None,
                    "reasoning": "Default reasoning"
                }
            
            return reasoning
        
        except Exception as e:
            logger.warning(f"Agent {self.name}: Reasoning failed, using default: {e}")
            return {
                "analysis": "Default reasoning",
                "next_action": "collect_data",
                "tool_to_use": None,
                "reasoning": "Fallback reasoning"
            }
    
    async def _act(self, reasoning: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Act: Execute selected action/tool
        
        Override in subclasses for agent-specific actions
        """
        next_action = reasoning.get("next_action", "collect_data")
        tool_to_use = reasoning.get("tool_to_use")
        
        result = {
            "action": next_action,
            "success": False,
            "result": None,
            "error": None
        }
        
        # If tool is specified, use it
        if tool_to_use:
            tools = self._select_tools(context)
            selected_tool = next((t for t in tools if t.name == tool_to_use), None)
            
            if selected_tool:
                try:
                    tool_result = await selected_tool.execute(context)
                    result["success"] = tool_result.get("success", False)
                    result["result"] = tool_result.get("result")
                    result["error"] = tool_result.get("error")
                except Exception as e:
                    result["error"] = str(e)
                    logger.error(f"Agent {self.name}: Tool {tool_to_use} execution failed: {e}")
        else:
            # Default action: prepare prompt and call AI
            try:
                prompt = await self._prepare_prompt(context.get("target", ""), context.get("parameters", {}))
                ai_response = await self.ai_router.generate_with_fallback(
                    prompt=prompt,
                    model_preference=self.model_preference,
                    max_tokens=2000,
                    temperature=0.3,
                    system_prompt=self.system_prompt,
                    strategy=self.strategy
                )
                result["success"] = True
                result["result"] = ai_response.content
            except Exception as e:
                result["error"] = str(e)
                logger.error(f"Agent {self.name}: Action {next_action} failed: {e}")
        
        return result
    
    async def _observe(self, action_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Observe: Analyze action results
        
        Override in subclasses for agent-specific observation
        """
        observation = {
            "action_success": action_result.get("success", False),
            "has_result": action_result.get("result") is not None,
            "context_updates": {}
        }
        
        # Update context with action results
        if action_result.get("success") and action_result.get("result"):
            observation["context_updates"][f"{action_result.get('action')}_result"] = action_result["result"]
        
        # Analyze if we have enough information
        if action_result.get("success"):
            observation["has_sufficient_data"] = True
        else:
            observation["has_sufficient_data"] = False
            observation["needs_more_data"] = True
        
        return observation
    
    def _is_complete(self, context: Dict[str, Any], observation: Dict[str, Any]) -> bool:
        """
        Check if task is complete
        
        Override in subclasses for agent-specific completion logic
        """
        # Default: Complete if we have successful results and sufficient data
        return (
            observation.get("action_success", False) and
            observation.get("has_sufficient_data", False) and
            context.get("iteration", 0) > 0  # At least one iteration completed
        )
    
    async def _aggregate_react_results(
        self,
        reasoning_trace: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aggregate results from ReAct execution
        
        Override in subclasses for agent-specific aggregation
        """
        # Collect all successful action results
        all_results = []
        for trace_entry in reasoning_trace:
            if trace_entry.get("step") == "act":
                action_result = trace_entry.get("action_result", {})
                if action_result.get("success"):
                    all_results.append(action_result.get("result"))
        
        # Parse final result if available
        final_result = None
        if all_results:
            # Use the last successful result
            final_result_data = all_results[-1]
            if isinstance(final_result_data, str):
                # Try to parse as JSON
                try:
                    import json
                    final_result = json.loads(final_result_data)
                except Exception:
                    final_result = {"raw_result": final_result_data}
            else:
                final_result = final_result_data
        
        return {
            "final_result": final_result,
            "all_results": all_results,
            "reasoning_steps": len(reasoning_trace),
            "success": bool(final_result)
        }
    
    @abstractmethod
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Prepare agent-specific prompt
        
        Override in subclasses
        """
        pass
    
    @abstractmethod
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response
        
        Override in subclasses
        """
        pass
    
    def _select_tools(self, task_context: Dict[str, Any]) -> List[AgentTool]:
        """
        Select appropriate tools for the task
        
        Enhanced with multi-tool orchestration support.
        Override in subclasses for agent-specific tool selection logic.
        """
        # Check if multi-tool orchestration is enabled
        use_multi_tool = task_context.get("use_multi_tool", True)
        
        if not use_multi_tool:
            # Fallback to legacy tool selection
            return self._select_tools_legacy(task_context)
        
        # Multi-tool selection will be handled by _execute_tools_multi_tool
        # Return empty list here - tools will be selected intelligently during execution
        return []
    
    def _select_tools_legacy(self, task_context: Dict[str, Any]) -> List[AgentTool]:
        """Legacy tool selection for backward compatibility"""
        selected_tools = []
        
        # First, check agent's own tools
        for tool in self.tools:
            if isinstance(tool, AgentTool):
                selected_tools.append(tool)
            elif isinstance(tool, str):
                # Tool name - look it up in registry
                registry_tool = self.tool_registry.get(tool)
                if registry_tool:
                    selected_tools.append(registry_tool)
        
        # Also check if AI suggested tools
        suggested_tools = task_context.get("suggested_tools", [])
        for tool_name in suggested_tools:
            if isinstance(tool_name, str):
                registry_tool = self.tool_registry.get(tool_name)
                if registry_tool and registry_tool not in selected_tools:
                    selected_tools.append(registry_tool)
        
        return selected_tools
    
    async def _execute_tool_chain(
        self,
        tools: List[AgentTool],
        context: Dict[str, Any],
        stop_on_error: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute a chain of tools sequentially
        
        Args:
            tools: List of tools to execute
            context: Context data to pass to tools
            stop_on_error: Whether to stop execution on first error
            
        Returns:
            List of tool execution results
        """
        tool_results = []
        
        for tool in tools:
            try:
                # Validate tool parameters if tool supports it
                if hasattr(tool, 'validate_params'):
                    if not tool.validate_params(context):
                        error_msg = f"Invalid parameters for tool {tool.name}"
                        logger.warning(f"Agent {self.name}: {error_msg}")
                        tool_results.append({
                            "tool": tool.name,
                            "success": False,
                            "error": error_msg
                        })
                        if stop_on_error:
                            break
                        continue
                
                # Execute tool
                logger.info(f"Agent {self.name}: Executing tool {tool.name}")
                result = await tool.execute(context)
                
                # Track tool usage
                self.tool_usage_count[tool.name] = self.tool_usage_count.get(tool.name, 0) + 1
                if result.get("success"):
                    self.tool_success_count[tool.name] = self.tool_success_count.get(tool.name, 0) + 1
                
                tool_results.append({
                    "tool": tool.name,
                    "success": result.get("success", False),
                    "result": result.get("result"),
                    "error": result.get("error"),
                    "metadata": result.get("metadata", {})
                })
                
                # Update context with tool results for next tools
                if result.get("success") and result.get("result"):
                    context[f"{tool.name}_result"] = result["result"]
                
                # Stop on error if requested
                if stop_on_error and not result.get("success"):
                    logger.warning(f"Agent {self.name}: Tool {tool.name} failed, stopping chain")
                    break
                
            except Exception as e:
                logger.error(f"Agent {self.name}: Tool {tool.name} execution failed: {e}", exc_info=True)
                tool_results.append({
                    "tool": tool.name,
                    "success": False,
                    "error": str(e)
                })
                if stop_on_error:
                    break
        
        return tool_results
    
    async def _execute_tools(self, parsed_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute tools if agent has them
        
        Enhanced with multi-tool orchestration support
        """
        # Check if multi-tool orchestration is enabled
        use_multi_tool = parsed_result.get("use_multi_tool", True)
        task_type = parsed_result.get("task_type", self.type)
        task_description = parsed_result.get("description", parsed_result.get("target", ""))
        
        if use_multi_tool:
            # Use multi-tool orchestration
            return await self._execute_tools_multi_tool(
                task_type=task_type,
                task_description=task_description,
                parameters=parsed_result
            )
        
        # Legacy single-tool execution
        return await self._execute_tools_legacy(parsed_result)
    
    async def _execute_tools_multi_tool(
        self,
        task_type: str,
        task_description: str,
        parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute tools using multi-tool orchestration"""
        try:
            from src.amas.agents.tools.multi_tool_orchestrator import get_multi_tool_orchestrator
            
            orchestrator = get_multi_tool_orchestrator()
            
            # Execute multi-tool task
            result = await orchestrator.execute_multi_tool_task(
                task_type=task_type,
                task_description=task_description or parameters.get("target", ""),
                parameters=parameters,
                agent_type=self.type,
                strategy=parameters.get("tool_strategy", "comprehensive"),
                max_tools=parameters.get("max_tools", 5),
                use_ai_synthesis=parameters.get("use_ai_synthesis", True)
            )
            
            # Convert to legacy format for compatibility
            tool_results = []
            
            # Add individual tool results
            for tool_name in result.get("tools_executed", []):
                tool_results.append({
                    "tool": tool_name,
                    "success": tool_name in result.get("tools_successful", []),
                    "result": result.get("supporting_evidence", {}).get(tool_name),
                    "confidence": result.get("confidence_scores", {}).get(tool_name, 0.5),
                    "metadata": {
                        "multi_tool": True,
                        "aggregated": False
                    }
                })
            
            # Add aggregated result if available
            if result.get("primary_findings") or result.get("synthesis"):
                tool_results.append({
                    "tool": "aggregated",
                    "success": result.get("success", False),
                    "result": {
                        "primary_findings": result.get("primary_findings", {}),
                        "synthesis": result.get("synthesis"),
                        "confidence_scores": result.get("confidence_scores", {}),
                        "conflicts": result.get("conflicts", []),
                        "tools_used": result.get("tools_successful", [])
                    },
                    "metadata": {
                        "multi_tool": True,
                        "aggregated": True,
                        **result.get("metadata", {})
                    }
                })
            
            # If no tools were executed, return empty list (not an error)
            if not tool_results:
                logger.info("No tools were selected/executed for this task")
            
            return tool_results
        
        except ImportError as e:
            logger.warning(f"Multi-tool orchestrator not available: {e}, falling back to legacy execution")
            return await self._execute_tools_legacy(parameters)
        except Exception as e:
            logger.error(f"Multi-tool execution failed: {e}", exc_info=True)
            # Don't fail completely - return empty results
            return []
    
    async def _execute_tools_legacy(self, parsed_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Legacy tool execution for backward compatibility"""
        # Select tools based on task context
        selected_tools = self._select_tools_legacy(parsed_result)
        
        if not selected_tools:
            # Fallback to old behavior for backward compatibility
            tool_results = []
            
            for tool in self.tools:
                try:
                    if hasattr(tool, 'execute'):
                        result = await tool.execute(parsed_result)
                    else:
                        result = tool(parsed_result)
                    
                    tool_results.append({
                        "tool": getattr(tool, 'name', str(tool)),
                        "success": True,
                        "result": result
                    })
                except Exception as e:
                    tool_results.append({
                        "tool": getattr(tool, 'name', str(tool)),
                        "success": False,
                        "error": str(e)
                    })
            
            return tool_results
        
        # Execute tool chain
        return await self._execute_tool_chain(selected_tools, parsed_result)
    
    # ==================== Communication Methods ====================
    
    async def send_to_agent(
        self,
        agent_id: str,
        message: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> bool:
        """
        Send a message to another agent
        
        Args:
            agent_id: ID of recipient agent
            message: Message payload
            priority: Message priority
            
        Returns:
            True if sent successfully
        """
        try:
            from src.amas.agents.communication.message import create_request_message
            
            agent_message = create_request_message(
                sender=self.id,
                receiver=agent_id,
                payload=message,
                priority=priority,
            )
            
            return await self.communication.send_message(agent_id, agent_message)
            
        except Exception as e:
            logger.error(f"Failed to send message to {agent_id}: {e}")
            return False
    
    async def broadcast_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> None:
        """
        Broadcast an event to all agents
        
        Args:
            event_type: Type of event
            data: Event data
            priority: Event priority
        """
        try:
            await self.event_bus.publish(
                event_type=event_type,
                data=data,
                sender=self.id,
                priority=priority,
            )
            logger.debug(f"Event {event_type} broadcast by {self.id}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast event {event_type}: {e}")
    
    async def request_from_agent(
        self,
        agent_id: str,
        payload: Dict[str, Any],
        timeout: float = 30.0,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a request to another agent and wait for response
        
        Args:
            agent_id: ID of recipient agent
            payload: Request payload
            timeout: Timeout in seconds
            priority: Message priority
            
        Returns:
            Response payload or None if timeout
        """
        try:
            response = await self.communication.request(
                to_agent=agent_id,
                payload=payload,
                timeout=timeout,
                priority=priority,
            )
            
            if response:
                logger.debug(f"Received response from {agent_id}")
            else:
                logger.warning(f"Request to {agent_id} timed out")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to request from {agent_id}: {e}")
            return None
    
    async def subscribe_to_event(
        self,
        event_type: str,
        handler,
    ) -> None:
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async function to call when event occurs
        """
        try:
            self.event_bus.subscribe(event_type, handler)
            self.event_handlers[event_type] = handler
            logger.debug(f"Agent {self.id} subscribed to event: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to event {event_type}: {e}")
    
    async def share_context(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Share a value in shared context
        
        Args:
            key: Context key
            value: Value to share
            ttl: Time-to-live in seconds
            
        Returns:
            True if successful
        """
        try:
            return await self.shared_context.set(
                key=key,
                value=value,
                ttl=ttl,
                updated_by=self.id,
            )
            
        except Exception as e:
            logger.error(f"Failed to share context {key}: {e}")
            return False
    
    async def get_shared_context(self, key: str, default: Any = None) -> Any:
        """
        Get a value from shared context
        
        Args:
            key: Context key
            default: Default value if not found
            
        Returns:
            Value or default
        """
        try:
            return await self.shared_context.get(key, default)
            
        except Exception as e:
            logger.error(f"Failed to get shared context {key}: {e}")
            return default
    
    async def notify_progress(
        self,
        progress: float,
        message: str,
    ) -> None:
        """
        Notify progress of current task
        
        Args:
            progress: Progress percentage (0.0 to 1.0)
            message: Progress message
        """
        try:
            await self.broadcast_event(
                event_type="agent_progress",
                data={
                    "agent_id": self.id,
                    "agent_name": self.name,
                    "progress": progress,
                    "message": message,
                },
                priority=MessagePriority.LOW,
            )
            
        except Exception as e:
            logger.error(f"Failed to notify progress: {e}")
    
    async def receive_messages(self) -> List[AgentMessage]:
        """
        Receive pending messages from queue
        
        Returns:
            List of received messages
        """
        try:
            return await self.communication.receive_messages()
            
        except Exception as e:
            logger.error(f"Failed to receive messages: {e}")
            return []
    
    async def initialize_communication(self) -> None:
        """Initialize communication components"""
        try:
            await self.communication.initialize()
            await self.event_bus.initialize()
            await self.shared_context.initialize()
            logger.info(f"Communication initialized for agent {self.id}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize communication for {self.id}: {e}")

