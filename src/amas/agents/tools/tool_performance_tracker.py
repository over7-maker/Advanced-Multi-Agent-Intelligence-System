"""
Tool Performance Tracker
Tracks execution metrics for all tools to enable intelligent selection
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ToolExecutionRecord:
    """Record of a single tool execution"""
    tool_name: str
    success: bool
    execution_time: float
    cost_usd: float = 0.0
    quality_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    result_size: int = 0  # Size of result in bytes


@dataclass
class ToolPerformanceMetrics:
    """Aggregated performance metrics for a tool"""
    tool_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time: float = 0.0
    total_cost_usd: float = 0.0
    total_quality_score: float = 0.0
    last_execution: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions
    
    @property
    def avg_execution_time(self) -> float:
        """Calculate average execution time"""
        if self.total_executions == 0:
            return 0.0
        return self.total_execution_time / self.total_executions
    
    @property
    def avg_cost(self) -> float:
        """Calculate average cost per execution"""
        if self.total_executions == 0:
            return 0.0
        return self.total_cost_usd / self.total_executions
    
    @property
    def avg_quality_score(self) -> float:
        """Calculate average quality score"""
        if self.successful_executions == 0:
            return 0.0
        return self.total_quality_score / self.successful_executions
    
    @property
    def reliability_score(self) -> float:
        """Calculate reliability score (0-1)"""
        # Combine success rate, recency, and consistency
        recency_bonus = 0.0
        if self.last_success:
            days_since_success = (datetime.now() - self.last_success).days
            if days_since_success < 7:
                recency_bonus = 0.1
            elif days_since_success < 30:
                recency_bonus = 0.05
        
        base_score = self.success_rate
        return min(1.0, base_score + recency_bonus)


class ToolPerformanceTracker:
    """Tracks and analyzes tool performance metrics"""
    
    def __init__(self, retention_days: int = 90):
        self.retention_days = retention_days
        self.execution_history: List[ToolExecutionRecord] = []
        self.metrics_cache: Dict[str, ToolPerformanceMetrics] = {}
        self.lock = asyncio.Lock()
        logger.info(f"ToolPerformanceTracker initialized (retention: {retention_days} days)")
    
    async def record_execution(
        self,
        tool_name: str,
        success: bool,
        execution_time: float,
        cost_usd: float = 0.0,
        quality_score: float = 0.0,
        error_message: Optional[str] = None,
        result_size: int = 0
    ):
        """Record a tool execution"""
        async with self.lock:
            record = ToolExecutionRecord(
                tool_name=tool_name,
                success=success,
                execution_time=execution_time,
                cost_usd=cost_usd,
                quality_score=quality_score,
                error_message=error_message,
                result_size=result_size
            )
            
            self.execution_history.append(record)
            
            # Update metrics cache
            if tool_name not in self.metrics_cache:
                self.metrics_cache[tool_name] = ToolPerformanceMetrics(tool_name=tool_name)
            
            metrics = self.metrics_cache[tool_name]
            metrics.total_executions += 1
            metrics.total_execution_time += execution_time
            metrics.total_cost_usd += cost_usd
            metrics.last_execution = record.timestamp
            
            if success:
                metrics.successful_executions += 1
                metrics.total_quality_score += quality_score
                metrics.last_success = record.timestamp
            else:
                metrics.failed_executions += 1
                metrics.last_failure = record.timestamp
            
            logger.debug(
                f"Recorded execution: {tool_name} - "
                f"success={success}, time={execution_time:.2f}s, "
                f"cost=${cost_usd:.4f}, quality={quality_score:.2f}"
            )
            
            # Cleanup old records periodically
            if len(self.execution_history) % 100 == 0:
                await self._cleanup_old_records()
    
    async def get_metrics(self, tool_name: str) -> Optional[ToolPerformanceMetrics]:
        """Get performance metrics for a tool"""
        async with self.lock:
            return self.metrics_cache.get(tool_name)
    
    async def get_all_metrics(self) -> Dict[str, ToolPerformanceMetrics]:
        """Get metrics for all tools"""
        async with self.lock:
            return self.metrics_cache.copy()
    
    async def get_top_tools(
        self,
        category: Optional[str] = None,
        min_executions: int = 5,
        sort_by: str = "reliability"
    ) -> List[ToolPerformanceMetrics]:
        """Get top performing tools"""
        async with self.lock:
            metrics_list = list(self.metrics_cache.values())
            
            # Filter by category if specified
            if category:
                from .tool_categories import get_tools_by_category, ToolCategory
                try:
                    cat_enum = ToolCategory(category)
                    category_tools = get_tools_by_category(cat_enum)
                    metrics_list = [
                        m for m in metrics_list
                        if m.tool_name in category_tools
                    ]
                except ValueError:
                    logger.warning(f"Invalid category: {category}")
            
            # Filter by minimum executions
            metrics_list = [
                m for m in metrics_list
                if m.total_executions >= min_executions
            ]
            
            # Sort
            if sort_by == "reliability":
                metrics_list.sort(key=lambda m: m.reliability_score, reverse=True)
            elif sort_by == "success_rate":
                metrics_list.sort(key=lambda m: m.success_rate, reverse=True)
            elif sort_by == "speed":
                metrics_list.sort(key=lambda m: m.avg_execution_time)
            elif sort_by == "cost":
                metrics_list.sort(key=lambda m: m.avg_cost)
            elif sort_by == "quality":
                metrics_list.sort(key=lambda m: m.avg_quality_score, reverse=True)
            
            return metrics_list
    
    async def get_tool_rankings(
        self,
        category: Optional[str] = None
    ) -> Dict[str, int]:
        """Get tool rankings (1 = best)"""
        top_tools = await self.get_top_tools(category=category, sort_by="reliability")
        return {
            tool.tool_name: rank + 1
            for rank, tool in enumerate(top_tools)
        }
    
    async def _cleanup_old_records(self):
        """Remove records older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        # Remove old records
        self.execution_history = [
            r for r in self.execution_history
            if r.timestamp > cutoff_date
        ]
        
        # Recalculate metrics from remaining records
        self.metrics_cache.clear()
        for record in self.execution_history:
            if record.tool_name not in self.metrics_cache:
                self.metrics_cache[record.tool_name] = ToolPerformanceMetrics(
                    tool_name=record.tool_name
                )
            
            metrics = self.metrics_cache[record.tool_name]
            metrics.total_executions += 1
            metrics.total_execution_time += record.execution_time
            metrics.total_cost_usd += record.cost_usd
            
            if record.success:
                metrics.successful_executions += 1
                metrics.total_quality_score += record.quality_score
                if not metrics.last_success or record.timestamp > metrics.last_success:
                    metrics.last_success = record.timestamp
            else:
                metrics.failed_executions += 1
                if not metrics.last_failure or record.timestamp > metrics.last_failure:
                    metrics.last_failure = record.timestamp
            
            if not metrics.last_execution or record.timestamp > metrics.last_execution:
                metrics.last_execution = record.timestamp
        
        logger.info(f"Cleaned up old records, {len(self.execution_history)} records remaining")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        async with self.lock:
            total_tools = len(self.metrics_cache)
            total_executions = sum(m.total_executions for m in self.metrics_cache.values())
            total_successful = sum(m.successful_executions for m in self.metrics_cache.values())
            total_failed = sum(m.failed_executions for m in self.metrics_cache.values())
            
            return {
                "total_tools_tracked": total_tools,
                "total_executions": total_executions,
                "total_successful": total_successful,
                "total_failed": total_failed,
                "overall_success_rate": total_successful / total_executions if total_executions > 0 else 0.0,
                "average_execution_time": sum(m.avg_execution_time for m in self.metrics_cache.values()) / total_tools if total_tools > 0 else 0.0,
                "total_cost_usd": sum(m.total_cost_usd for m in self.metrics_cache.values()),
            }


# Global tracker instance
_tracker: Optional[ToolPerformanceTracker] = None


def get_tool_performance_tracker() -> ToolPerformanceTracker:
    """Get the global tool performance tracker"""
    global _tracker
    if _tracker is None:
        _tracker = ToolPerformanceTracker()
    return _tracker


__all__ = [
    'ToolExecutionRecord',
    'ToolPerformanceMetrics',
    'ToolPerformanceTracker',
    'get_tool_performance_tracker',
]

