"""
Multi-Tool Orchestrator
Main orchestrator that coordinates tool selection, execution, and result aggregation
"""

import logging
from typing import Dict, List, Optional, Any

from src.amas.agents.tools.intelligent_tool_selector import (
    get_intelligent_tool_selector,
    ToolRecommendation
)
from src.amas.agents.tools.multi_tool_executor import (
    get_multi_tool_executor,
    ExecutionStrategy,
    ToolExecutionResult
)
from src.amas.agents.tools.result_aggregator import (
    get_result_aggregator,
    AggregatedResult
)

logger = logging.getLogger(__name__)


class MultiToolOrchestrator:
    """
    Main orchestrator for multi-tool agent operations
    
    Coordinates:
    1. Intelligent tool selection
    2. Multi-tool execution
    3. Result aggregation and synthesis
    """
    
    def __init__(self):
        self.tool_selector = get_intelligent_tool_selector()
        self.tool_executor = get_multi_tool_executor()
        self.result_aggregator = get_result_aggregator()
        logger.info("MultiToolOrchestrator initialized")
    
    async def execute_multi_tool_task(
        self,
        task_type: str,
        task_description: str,
        parameters: Dict[str, Any],
        agent_type: Optional[str] = None,
        strategy: str = "comprehensive",
        max_tools: int = 5,
        use_ai_synthesis: bool = True
    ) -> Dict[str, Any]:
        """
        Complete multi-tool execution workflow
        
        Args:
            task_type: Type of task
            task_description: Task description
            parameters: Task parameters
            agent_type: Type of agent (for tool preferences)
            strategy: Tool selection strategy
            max_tools: Maximum number of tools to use
            use_ai_synthesis: Whether to use AI for result synthesis
            
        Returns:
            Complete result with aggregated findings
        """
        logger.info(
            f"Starting multi-tool task: {task_type} "
            f"(agent={agent_type}, strategy={strategy})"
        )
        
        # Step 1: Select tools intelligently
        recommendations = await self.tool_selector.select_tools(
            task_type=task_type,
            task_description=task_description,
            parameters=parameters,
            strategy=strategy,
            max_tools=max_tools,
            agent_type=agent_type
        )
        
        if not recommendations:
            logger.warning("No tools selected for task")
            return {
                "success": False,
                "error": "No suitable tools found for task",
                "tools_used": [],
                "result": {}
            }
        
        # Step 2: Execute tools
        execution_results = await self.tool_executor.execute_tools(
            recommendations=recommendations,
            context=parameters,
            strategy=None,  # Auto-detect
            timeout_per_tool=60.0,
            stop_on_error=False
        )
        
        # Step 3: Aggregate results
        aggregated = await self.result_aggregator.aggregate_results(
            tool_results=execution_results,
            task_description=task_description,
            use_ai_synthesis=use_ai_synthesis
        )
        
        # Step 4: Build final result
        successful_tools = [r.tool_name for r in execution_results if r.success]
        failed_tools = [r.tool_name for r in execution_results if not r.success]
        
        result = {
            "success": len(successful_tools) > 0,
            "tools_selected": [r.tool_name for r in recommendations],
            "tools_executed": [r.tool_name for r in execution_results],
            "tools_successful": successful_tools,
            "tools_failed": failed_tools,
            "primary_findings": aggregated.primary_findings,
            "supporting_evidence": aggregated.supporting_evidence,
            "confidence_scores": aggregated.confidence_scores,
            "synthesis": aggregated.synthesis,
            "conflicts": aggregated.conflicts,
            "metadata": {
                **aggregated.metadata,
                "selection_strategy": strategy,
                "total_tools_selected": len(recommendations),
                "total_tools_executed": len(execution_results),
                "success_rate": len(successful_tools) / len(execution_results) if execution_results else 0.0
            }
        }
        
        logger.info(
            f"Multi-tool task completed: "
            f"{len(successful_tools)}/{len(execution_results)} tools successful"
        )
        
        return result
    
    async def get_tool_recommendations(
        self,
        task_type: str,
        task_description: str,
        parameters: Dict[str, Any],
        agent_type: Optional[str] = None,
        strategy: str = "comprehensive",
        max_tools: int = 5
    ) -> List[ToolRecommendation]:
        """Get tool recommendations without executing"""
        return await self.tool_selector.select_tools(
            task_type=task_type,
            task_description=task_description,
            parameters=parameters,
            strategy=strategy,
            max_tools=max_tools,
            agent_type=agent_type
        )


# Global orchestrator instance
_orchestrator: Optional[MultiToolOrchestrator] = None


def get_multi_tool_orchestrator() -> MultiToolOrchestrator:
    """Get the global multi-tool orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiToolOrchestrator()
    return _orchestrator


__all__ = [
    'MultiToolOrchestrator',
    'get_multi_tool_orchestrator',
]

