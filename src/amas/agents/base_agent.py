"""
Base Agent Class - Foundation for all specialized agents
Implements PART_3 requirements with AI router integration
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.amas.ai.enhanced_router_class import AIResponse, get_ai_router

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
        tools: List[Any] = None,
        model_preference: str = "gpt-4-turbo-preview",
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
        
        # Performance tracking
        self.expertise_score = 0.90  # Default
        self.executions = 0
        self.successes = 0
        self.total_duration = 0.0
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute agent task
        
        Returns:
            Dict with result, success, duration, etc.
        """
        
        execution_start = time.time()
        
        try:
            # STEP 1: Prepare prompt
            prompt = await self._prepare_prompt(target, parameters)
            
            # STEP 2: Call AI via router (WITH FALLBACK)
            logger.info(f"Agent {self.name}: Calling AI with strategy '{self.strategy}'")
            
            ai_response: AIResponse = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"Agent {self.name}: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 3: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 4: Execute tools if needed
            if self.tools and parsed_result.get("requires_tools"):
                tool_results = await self._execute_tools(parsed_result)
                parsed_result["tool_results"] = tool_results
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": True,
                "agent_id": self.id,
                "agent_name": self.name,
                "result": parsed_result,
                "duration": execution_duration,
                "ai_provider": ai_response.provider,
                "ai_model": ai_response.model,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "fallback_used": ai_response.fallback_used
            }
        
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
    
    async def _execute_tools(self, parsed_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute tools if agent has them"""
        
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

