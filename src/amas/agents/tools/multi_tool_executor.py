"""
Multi-Tool Executor
Executes multiple tools in parallel, sequential, or hybrid modes with failover
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from src.amas.agents.tools import AgentTool, get_tool_registry
from src.amas.agents.tools.tool_categories import (
    ExecutionMode,
    get_tool_metadata,
    get_tool_failover_chain,
    get_tool_dependencies
)
from src.amas.agents.tools.tool_performance_tracker import get_tool_performance_tracker
from src.amas.agents.tools.intelligent_tool_selector import ToolRecommendation

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Tool execution strategy"""
    PARALLEL = "parallel"  # All tools execute simultaneously
    SEQUENTIAL = "sequential"  # Tools execute one after another
    HYBRID = "hybrid"  # Parallel groups with sequential dependencies
    ADAPTIVE = "adaptive"  # AI decides based on tool dependencies


@dataclass
class ToolExecutionResult:
    """Result of tool execution"""
    tool_name: str
    success: bool
    result: Any
    execution_time: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MultiToolExecutor:
    """Executes multiple tools with intelligent orchestration"""
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
        self.performance_tracker = get_tool_performance_tracker()
        logger.info("MultiToolExecutor initialized")
    
    async def execute_tools(
        self,
        recommendations: List[ToolRecommendation],
        context: Dict[str, Any],
        strategy: Optional[ExecutionStrategy] = None,
        timeout_per_tool: float = 60.0,
        stop_on_error: bool = False
    ) -> List[ToolExecutionResult]:
        """
        Execute multiple tools based on recommendations
        
        Args:
            recommendations: List of tool recommendations
            context: Context data to pass to tools
            strategy: Execution strategy (auto-detect if None)
            timeout_per_tool: Timeout per tool in seconds
            stop_on_error: Whether to stop on first error
            
        Returns:
            List of tool execution results
        """
        if not recommendations:
            logger.warning("No tool recommendations provided")
            return []
        
        logger.info(
            f"Executing {len(recommendations)} tools "
            f"(strategy={strategy or 'auto'})"
        )
        
        # Determine execution strategy
        if strategy is None:
            strategy = self._determine_strategy(recommendations)
        
        # Execute based on strategy
        if strategy == ExecutionStrategy.PARALLEL:
            results = await self._execute_parallel(
                recommendations, context, timeout_per_tool
            )
        elif strategy == ExecutionStrategy.SEQUENTIAL:
            results = await self._execute_sequential(
                recommendations, context, timeout_per_tool, stop_on_error
            )
        elif strategy == ExecutionStrategy.HYBRID:
            results = await self._execute_hybrid(
                recommendations, context, timeout_per_tool, stop_on_error
            )
        else:  # ADAPTIVE
            results = await self._execute_adaptive(
                recommendations, context, timeout_per_tool, stop_on_error
            )
        
        # Record performance metrics
        for result in results:
            await self.performance_tracker.record_execution(
                tool_name=result.tool_name,
                success=result.success,
                execution_time=result.execution_time,
                quality_score=self._calculate_quality_score(result)
            )
        
        logger.info(
            f"Tool execution completed: "
            f"{sum(1 for r in results if r.success)}/{len(results)} successful"
        )
        
        return results
    
    def _determine_strategy(
        self,
        recommendations: List[ToolRecommendation]
    ) -> ExecutionStrategy:
        """Determine optimal execution strategy"""
        # Check for dependencies
        has_dependencies = False
        for rec in recommendations:
            deps = get_tool_dependencies(rec.tool_name)
            if deps:
                has_dependencies = True
                break
        
        # Check execution modes
        execution_modes = {rec.execution_mode for rec in recommendations}
        
        if has_dependencies or "sequential" in execution_modes:
            # Use hybrid if some tools can run in parallel
            if len(execution_modes) > 1:
                return ExecutionStrategy.HYBRID
            return ExecutionStrategy.SEQUENTIAL
        
        if "parallel" in execution_modes or len(execution_modes) == 1:
            return ExecutionStrategy.PARALLEL
        
        return ExecutionStrategy.ADAPTIVE
    
    async def _execute_parallel(
        self,
        recommendations: List[ToolRecommendation],
        context: Dict[str, Any],
        timeout: float
    ) -> List[ToolExecutionResult]:
        """Execute all tools in parallel"""
        logger.info(f"Executing {len(recommendations)} tools in parallel")
        
        async def execute_single(rec: ToolRecommendation) -> ToolExecutionResult:
            return await self._execute_single_tool(rec, context, timeout)
        
        # Execute all tools concurrently
        tasks = [execute_single(rec) for rec in recommendations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ToolExecutionResult(
                    tool_name=recommendations[i].tool_name,
                    success=False,
                    result=None,
                    execution_time=0.0,
                    error=str(result)
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def _execute_sequential(
        self,
        recommendations: List[ToolRecommendation],
        context: Dict[str, Any],
        timeout: float,
        stop_on_error: bool
    ) -> List[ToolExecutionResult]:
        """Execute tools sequentially"""
        logger.info(f"Executing {len(recommendations)} tools sequentially")
        
        results = []
        current_context = context.copy()
        
        for rec in recommendations:
            result = await self._execute_single_tool(rec, current_context, timeout)
            results.append(result)
            
            # Update context with result for next tool
            if result.success and result.result:
                current_context[f"{result.tool_name}_result"] = result.result
                current_context["previous_tool"] = result.tool_name
            
            # Stop on error if requested
            if not result.success and stop_on_error:
                logger.warning(f"Tool {rec.tool_name} failed, stopping sequential execution")
                break
        
        return results
    
    async def _execute_hybrid(
        self,
        recommendations: List[ToolRecommendation],
        context: Dict[str, Any],
        timeout: float,
        stop_on_error: bool
    ) -> List[ToolExecutionResult]:
        """Execute tools in parallel groups with sequential dependencies"""
        logger.info(f"Executing {len(recommendations)} tools in hybrid mode")
        
        # Group tools by dependencies
        groups = self._group_by_dependencies(recommendations)
        
        results = []
        current_context = context.copy()
        
        # Execute groups sequentially, tools within group in parallel
        for group in groups:
            # Execute group in parallel
            group_results = await self._execute_parallel(group, current_context, timeout)
            results.extend(group_results)
            
            # Update context with group results
            for result in group_results:
                if result.success and result.result:
                    current_context[f"{result.tool_name}_result"] = result.result
            
            # Stop on error if requested
            if stop_on_error and any(not r.success for r in group_results):
                logger.warning("Group execution had failures, stopping")
                break
        
        return results
    
    async def _execute_adaptive(
        self,
        recommendations: List[ToolRecommendation],
        context: Dict[str, Any],
        timeout: float,
        stop_on_error: bool
    ) -> List[ToolExecutionResult]:
        """Adaptive execution - determine strategy dynamically"""
        # For now, use hybrid as default adaptive strategy
        return await self._execute_hybrid(recommendations, context, timeout, stop_on_error)
    
    def _group_by_dependencies(
        self,
        recommendations: List[ToolRecommendation]
    ) -> List[List[ToolRecommendation]]:
        """Group tools by dependency levels"""
        groups = []
        remaining = recommendations.copy()
        executed = set()
        
        while remaining:
            # Find tools with no unmet dependencies
            current_group = []
            for rec in remaining[:]:
                deps = get_tool_dependencies(rec.tool_name)
                if not deps or all(dep in executed for dep in deps):
                    current_group.append(rec)
                    remaining.remove(rec)
            
            if not current_group:
                # Circular dependency or missing dependency - execute remaining in parallel
                current_group = remaining
                remaining = []
            
            groups.append(current_group)
            executed.update(rec.tool_name for rec in current_group)
        
        return groups
    
    async def _execute_single_tool(
        self,
        recommendation: ToolRecommendation,
        context: Dict[str, Any],
        timeout: float
    ) -> ToolExecutionResult:
        """Execute a single tool with failover support"""
        tool_name = recommendation.tool_name
        start_time = time.time()
        
        try:
            # Get tool from registry
            tool = self.tool_registry.get(tool_name)
            if not tool:
                # Try failover chain
                return await self._execute_with_failover(
                    recommendation, context, timeout, start_time
                )
            
            # Execute tool with timeout
            result = await asyncio.wait_for(
                tool.execute(context),
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=result.get("success", False),
                result=result.get("result"),
                execution_time=execution_time,
                error=result.get("error"),
                metadata=result.get("metadata", {})
            )
        
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            logger.warning(f"Tool {tool_name} timed out after {timeout}s")
            
            # Try failover
            return await self._execute_with_failover(
                recommendation, context, timeout, start_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tool {tool_name} failed: {e}", exc_info=True)
            
            # Try failover
            return await self._execute_with_failover(
                recommendation, context, timeout, start_time
            )
    
    async def _execute_with_failover(
        self,
        recommendation: ToolRecommendation,
        context: Dict[str, Any],
        timeout: float,
        start_time: float
    ) -> ToolExecutionResult:
        """Execute failover chain if primary tool fails"""
        tool_name = recommendation.tool_name
        failover_chain = get_tool_failover_chain(tool_name)
        
        if not failover_chain:
            # No failover available
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                execution_time=time.time() - start_time,
                error=f"Tool {tool_name} failed and no failover available"
            )
        
        # Try failover tools
        for failover_name in failover_chain:
            logger.info(f"Trying failover tool: {failover_name} (original: {tool_name})")
            
            try:
                failover_tool = self.tool_registry.get(failover_name)
                if failover_tool:
                    result = await asyncio.wait_for(
                        failover_tool.execute(context),
                        timeout=timeout
                    )
                    
                    execution_time = time.time() - start_time
                    
                    return ToolExecutionResult(
                        tool_name=failover_name,
                        success=result.get("success", False),
                        result=result.get("result"),
                        execution_time=execution_time,
                        error=result.get("error"),
                        metadata={
                            **result.get("metadata", {}),
                            "failover_from": tool_name
                        }
                    )
            except Exception as e:
                logger.warning(f"Failover tool {failover_name} also failed: {e}")
                continue
        
        # All failovers exhausted
        return ToolExecutionResult(
            tool_name=tool_name,
            success=False,
            result=None,
            execution_time=time.time() - start_time,
            error=f"Tool {tool_name} and all failovers failed"
        )
    
    def _calculate_quality_score(self, result: ToolExecutionResult) -> float:
        """Calculate quality score for a tool result"""
        if not result.success:
            return 0.0
        
        score = 0.5  # Base score
        
        # Bonus for having result data
        if result.result:
            score += 0.3
        
        # Bonus for fast execution
        if result.execution_time < 5.0:
            score += 0.1
        elif result.execution_time > 30.0:
            score -= 0.1
        
        # Bonus for metadata
        if result.metadata:
            score += 0.1
        
        return min(1.0, max(0.0, score))


# Global executor instance
_executor: Optional[MultiToolExecutor] = None


def get_multi_tool_executor() -> MultiToolExecutor:
    """Get the global multi-tool executor"""
    global _executor
    if _executor is None:
        _executor = MultiToolExecutor()
    return _executor


__all__ = [
    'ExecutionStrategy',
    'ToolExecutionResult',
    'MultiToolExecutor',
    'get_multi_tool_executor',
]

