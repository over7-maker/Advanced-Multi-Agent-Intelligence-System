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
    Registry for managing all available tools
    """
    
    def __init__(self):
        self.tools: Dict[str, AgentTool] = {}
        self.logger = logging.getLogger(f"{__name__}.ToolRegistry")
    
    def register(self, tool: AgentTool):
        """Register a tool"""
        if tool.name in self.tools:
            self.logger.warning(f"Tool {tool.name} already registered, overwriting")
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get(self, name: str) -> Optional[AgentTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
    
    def get_tools_by_category(self, category: str) -> List[AgentTool]:
        """Get tools by category (if tools have category attribute)"""
        return [
            tool for tool in self.tools.values()
            if hasattr(tool, 'category') and tool.category == category
        ]


# Global tool registry instance
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def register_tool(tool: AgentTool):
    """Register a tool in the global registry"""
    registry = get_tool_registry()
    registry.register(tool)


__all__ = [
    'AgentTool',
    'ToolRegistry',
    'get_tool_registry',
    'register_tool'
]

# Auto-import and register tools
try:
    from . import register_tools  # noqa: F401
except ImportError:
    pass  # Tools will be registered when imported

