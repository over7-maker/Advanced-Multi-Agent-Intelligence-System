"""
Agent Tools Framework
Standardized tool interface for all agent tools
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AgentTool(ABC):
    """
    Base class for all agent tools
    
    All tools must implement this interface for consistency
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given parameters
        
        Args:
            params: Tool-specific parameters
            
        Returns:
            Dict with:
                - success: bool
                - result: Any (tool-specific result)
                - error: Optional[str] (if success is False)
                - metadata: Optional[Dict] (execution metadata)
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Validate tool parameters
        
        Override in subclasses for specific validation
        """
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for tool parameters
        
        Override in subclasses to provide parameter schema
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }


class ToolRegistry:
    """
    Registry for managing all available tools with category support
    """
    
    def __init__(self):
        self.tools: Dict[str, AgentTool] = {}
        self.logger = logging.getLogger(f"{__name__}.ToolRegistry")
    
    def register(self, tool: AgentTool, category: Optional[str] = None):
        """Register a tool with optional category"""
        if tool.name in self.tools:
            self.logger.warning(f"Tool {tool.name} already registered, overwriting")
        self.tools[tool.name] = tool
        
        # Set category attribute if provided
        if category:
            tool.category = category
        
        self.logger.info(f"Registered tool: {tool.name}" + (f" (category: {category})" if category else ""))
    
    def get(self, name: str) -> Optional[AgentTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
    
    def get_tools_by_category(self, category: str) -> List[AgentTool]:
        """Get tools by category"""
        from .tool_categories import ToolCategory, get_tools_by_category as get_tools_by_cat
        
        # Try to get from tool_categories first
        try:
            cat_enum = ToolCategory(category)
            tool_names = get_tools_by_cat(cat_enum)
            return [self.tools[name] for name in tool_names if name in self.tools]
        except (ValueError, KeyError):
            # Fallback to attribute-based lookup
            return [
                tool for tool in self.tools.values()
                if hasattr(tool, 'category') and tool.category == category
            ]
    
    def get_all_tools(self) -> List[AgentTool]:
        """Get all registered tools"""
        return list(self.tools.values())


# Global tool registry instance
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def register_tool(tool: AgentTool, category: Optional[str] = None):
    """Register a tool in the global registry with optional category"""
    registry = get_tool_registry()
    registry.register(tool, category)


__all__ = [
    'AgentTool',
    'ToolRegistry',
    'get_tool_registry',
    'register_tool',
    # Multi-tool orchestration
    'ToolCategory',
    'ExecutionMode',
    'ToolMetadata',
    'IntelligentToolSelector',
    'MultiToolExecutor',
    'ResultAggregator',
    'MultiToolOrchestrator',
    'ToolPerformanceTracker',
    'get_intelligent_tool_selector',
    'get_multi_tool_executor',
    'get_result_aggregator',
    'get_multi_tool_orchestrator',
    'get_tool_performance_tracker',
]

# Auto-import and register tools
try:
    from . import register_tools  # noqa: F401
except ImportError:
    pass  # Tools will be registered when imported

# Import multi-tool components (lazy import to avoid circular dependencies)
try:
    from .tool_categories import ToolCategory, ExecutionMode, ToolMetadata  # noqa: F401
    from .intelligent_tool_selector import IntelligentToolSelector, get_intelligent_tool_selector  # noqa: F401
    from .multi_tool_executor import MultiToolExecutor, get_multi_tool_executor  # noqa: F401
    from .result_aggregator import ResultAggregator, get_result_aggregator  # noqa: F401
    from .multi_tool_orchestrator import MultiToolOrchestrator, get_multi_tool_orchestrator  # noqa: F401
    from .tool_performance_tracker import ToolPerformanceTracker, get_tool_performance_tracker  # noqa: F401
except ImportError:
    pass  # Components will be imported when needed

