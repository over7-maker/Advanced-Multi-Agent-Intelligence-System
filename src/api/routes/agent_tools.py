"""
Agent Tools Configuration API Routes
Endpoints for managing agent tool configuration and status
"""

import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.amas.security.audit.audit_logger import get_audit_logger
from src.amas.security.auth.jwt_middleware import auth_context

# WebSocket for real-time updates
try:
    from src.api.websocket import websocket_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    websocket_manager = None

logger = logging.getLogger(__name__)

router = APIRouter()


class ToolConfig(BaseModel):
    """Tool configuration model"""
    tool_name: str
    enabled: bool = True
    config: Dict[str, Any] = {}
    api_key: Optional[str] = None
    api_key_set: bool = False  # Whether API key is configured (without exposing value)


class ToolStatus(BaseModel):
    """Tool status model"""
    tool_name: str
    status: str  # "available", "unavailable", "error", "needs_config"
    last_checked: str
    error_message: Optional[str] = None
    requires_auth: bool = False
    requires_api_key: bool = False
    api_key_configured: bool = False
    service_url: Optional[str] = None
    service_available: bool = False


class AgentToolConfig(BaseModel):
    """Agent tool configuration"""
    agent_id: str
    tools: List[ToolConfig]
    tool_strategy: str = "comprehensive"  # comprehensive, efficient, reliable, cost_optimized
    max_tools: int = 5
    use_ai_synthesis: bool = True


class ToolStatusResponse(BaseModel):
    """Tool status response"""
    tool_name: str
    status: str
    last_checked: str
    error_message: Optional[str] = None
    requires_auth: bool
    requires_api_key: bool
    api_key_configured: bool
    service_url: Optional[str] = None
    service_available: bool


@router.get("/agents/{agent_id}/tools")
async def get_agent_tools(agent_id: str) -> Dict[str, Any]:
    """Get all tools available for an agent and their configuration"""
    logger.info(f"[API] get_agent_tools called for agent_id: {agent_id}")
    try:
        from src.amas.agents.tools import get_tool_registry
        from src.amas.agents.tools.tool_categories import TOOL_CATEGORY_MAP, ToolCategory
        
        logger.info("[API] Getting tool registry...")
        registry = get_tool_registry()
        all_tools = registry.list_tools()
        logger.info(f"[API] Found {len(all_tools)} tools in registry")
        
        # Get agent to determine which tools it can use
        from src.amas.api.main import get_amas_system
        logger.info("[API] Getting AMAS system...")
        amas = await get_amas_system()
        
        agent_tools = []
        agent_config = {}
        
        # Try to get agent from orchestrator
        if hasattr(amas, "orchestrator") and amas.orchestrator:
            logger.info(f"[API] Checking orchestrator for agent {agent_id}...")
            if hasattr(amas.orchestrator, 'agents') and agent_id in amas.orchestrator.agents:
                agent = amas.orchestrator.agents[agent_id]
                logger.info(f"[API] Found agent {agent_id} in orchestrator")
                # Get agent's tool configuration if available
                if hasattr(agent, 'tool_config'):
                    agent_config = agent.tool_config
                elif hasattr(agent, 'config'):
                    agent_config = getattr(agent.config, 'tools', {}) if hasattr(agent.config, 'tools') else {}
            else:
                logger.info(f"[API] Agent {agent_id} not found in orchestrator.agents")
        else:
            logger.info("[API] Orchestrator not available or has no agents attribute")
        
        # Build tool list with metadata
        logger.info("[API] Building tool list with metadata...")
        for tool_name in all_tools:
            tool = registry.get(tool_name)
            if not tool:
                logger.debug(f"[API] Tool {tool_name} not found in registry, skipping")
                continue
            
            tool_metadata = TOOL_CATEGORY_MAP.get(tool_name)
            if not tool_metadata:
                logger.debug(f"[API] No metadata for tool {tool_name}, skipping")
                continue
            
            # Check if tool requires auth/API key
            requires_auth = tool_metadata.requires_auth
            requires_api_key = requires_auth
            
            # Check API key status
            api_key_configured = False
            if requires_api_key:
                # Check environment variables for common API key patterns
                api_key_env_vars = [
                    f"{tool_name.upper()}_API_KEY",
                    f"{tool_name.upper().replace('-', '_')}_API_KEY",
                ]
                for env_var in api_key_env_vars:
                    if os.getenv(env_var):
                        api_key_configured = True
                        break
            
            # Get tool configuration from agent config
            tool_config = agent_config.get(tool_name, {})
            
            agent_tools.append({
                "tool_name": tool_name,
                "description": tool_metadata.description,
                "category": tool_metadata.category.value,
                "enabled": tool_config.get("enabled", True),
                "requires_auth": requires_auth,
                "requires_api_key": requires_api_key,
                "api_key_configured": api_key_configured,
                "config": tool_config.get("config", {}),
                "execution_mode": tool_metadata.execution_mode.value,
                "cost_tier": tool_metadata.cost_tier,
                "avg_execution_time": tool_metadata.avg_execution_time,
            })
        
        logger.info(f"[API] Returning {len(agent_tools)} tools for agent {agent_id}")
        result = {
            "agent_id": agent_id,
            "tools": agent_tools,
            "total": len(agent_tools),
            "enabled": len([t for t in agent_tools if t["enabled"]]),
        }
        logger.info(f"[API] Response prepared: {len(agent_tools)} tools, {result['enabled']} enabled")
        return result
    except Exception as e:
        logger.error(f"[API] Failed to get agent tools: {e}", exc_info=True)
        import traceback
        logger.error(f"[API] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent tools: {str(e)}")


@router.get("/agents/{agent_id}/tools/{tool_name}/status")
async def get_tool_status(agent_id: str, tool_name: str) -> ToolStatusResponse:
    """Get status of a specific tool for an agent"""
    try:
        from src.amas.agents.tools import get_tool_registry
        from src.amas.agents.tools.tool_categories import TOOL_CATEGORY_MAP
        
        registry = get_tool_registry()
        tool = registry.get(tool_name)
        
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
        
        tool_metadata = TOOL_CATEGORY_MAP.get(tool_name)
        if not tool_metadata:
            raise HTTPException(status_code=404, detail=f"Tool metadata for {tool_name} not found")
        
        # Check tool status
        status = "available"
        error_message = None
        service_available = False
        service_url = None
        
        requires_auth = tool_metadata.requires_auth
        requires_api_key = requires_auth
        
        # Check API key
        api_key_configured = False
        if requires_api_key:
            api_key_env_vars = [
                f"{tool_name.upper()}_API_KEY",
                f"{tool_name.upper().replace('-', '_')}_API_KEY",
            ]
            for env_var in api_key_env_vars:
                if os.getenv(env_var):
                    api_key_configured = True
                    break
            
            if not api_key_configured:
                status = "needs_config"
                error_message = f"API key not configured. Set one of: {', '.join(api_key_env_vars)}"
        
        # Check service availability for tools that require external services
        if tool_name in ["agenticseek", "robin", "prometheus", "grafana", "loki", "jaeger"]:
            service_urls = {
                "agenticseek": os.getenv("AGENTICSEEK_URL", "http://localhost:8000"),
                "robin": os.getenv("ROBIN_URL", "http://localhost:8002"),
                "prometheus": os.getenv("PROMETHEUS_URL", "http://localhost:9090"),
                "grafana": os.getenv("GRAFANA_URL", "http://localhost:3000"),
                "loki": os.getenv("LOKI_URL", "http://localhost:3100"),
                "jaeger": os.getenv("JAEGER_URL", "http://localhost:16686"),
            }
            
            service_url = service_urls.get(tool_name)
            if service_url:
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{service_url}/health" if tool_name != "prometheus" else f"{service_url}/-/healthy",
                            timeout=aiohttp.ClientTimeout(total=2)
                        ) as response:
                            service_available = response.status == 200
                            if not service_available:
                                status = "unavailable"
                                error_message = f"Service at {service_url} is not responding"
                except Exception as e:
                    service_available = False
                    status = "unavailable"
                    error_message = f"Service check failed: {str(e)}"
        
        return ToolStatusResponse(
            tool_name=tool_name,
            status=status,
            last_checked=datetime.now().isoformat(),
            error_message=error_message,
            requires_auth=requires_auth,
            requires_api_key=requires_api_key,
            api_key_configured=api_key_configured,
            service_url=service_url,
            service_available=service_available,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get tool status: {str(e)}")


@router.get("/agents/{agent_id}/tools/status")
async def get_all_tools_status(agent_id: str) -> Dict[str, Any]:
    """Get status of all tools for an agent"""
    try:
        from src.amas.agents.tools import get_tool_registry
        from src.amas.agents.tools.tool_categories import TOOL_CATEGORY_MAP
        
        registry = get_tool_registry()
        all_tools = registry.list_tools()
        
        tool_statuses = []
        for tool_name in all_tools:
            try:
                tool = registry.get(tool_name)
                if not tool:
                    continue
                
                tool_metadata = TOOL_CATEGORY_MAP.get(tool_name)
                if not tool_metadata:
                    continue
                
                # Check tool status
                status = "available"
                error_message = None
                service_available = False
                service_url = None
                
                requires_auth = tool_metadata.requires_auth
                requires_api_key = requires_auth
                
                # Check API key
                api_key_configured = False
                if requires_api_key:
                    api_key_env_vars = [
                        f"{tool_name.upper()}_API_KEY",
                        f"{tool_name.upper().replace('-', '_')}_API_KEY",
                    ]
                    for env_var in api_key_env_vars:
                        if os.getenv(env_var):
                            api_key_configured = True
                            break
                    
                    if not api_key_configured:
                        status = "needs_config"
                        error_message = f"API key not configured. Set one of: {', '.join(api_key_env_vars)}"
                
                # Check service availability for tools that require external services
                if tool_name in ["agenticseek", "robin", "prometheus", "grafana", "loki", "jaeger", "pyroscope", "owasp_zap"]:
                    service_urls = {
                        "agenticseek": os.getenv("AGENTICSEEK_URL", "http://localhost:8000"),
                        "robin": os.getenv("ROBIN_URL", "http://localhost:8002"),
                        "prometheus": os.getenv("PROMETHEUS_URL", "http://localhost:9090"),
                        "grafana": os.getenv("GRAFANA_URL", "http://localhost:3000"),
                        "loki": os.getenv("LOKI_URL", "http://localhost:3100"),
                        "jaeger": os.getenv("JAEGER_URL", "http://localhost:16686"),
                        "pyroscope": os.getenv("PYROSCOPE_URL", "http://localhost:4040"),
                        "owasp_zap": os.getenv("OWASP_ZAP_URL", "http://localhost:8080"),
                    }
                    
                    service_url = service_urls.get(tool_name)
                    if service_url:
                        try:
                            import aiohttp
                            async with aiohttp.ClientSession() as session:
                                async with session.get(
                                    f"{service_url}/health" if tool_name != "prometheus" else f"{service_url}/-/healthy",
                                    timeout=aiohttp.ClientTimeout(total=2)
                                ) as response:
                                    service_available = response.status == 200
                                    if not service_available:
                                        status = "unavailable"
                                        error_message = f"Service at {service_url} is not responding"
                        except Exception as e:
                            service_available = False
                            status = "unavailable"
                            error_message = f"Service check failed: {str(e)}"
                
                tool_statuses.append({
                    "tool_name": tool_name,
                    "status": status,
                    "last_checked": datetime.now().isoformat(),
                    "error_message": error_message,
                    "requires_auth": requires_auth,
                    "requires_api_key": requires_api_key,
                    "api_key_configured": api_key_configured,
                    "service_url": service_url,
                    "service_available": service_available,
                })
            except Exception as e:
                logger.warning(f"Failed to get status for tool {tool_name}: {e}")
                tool_statuses.append({
                    "tool_name": tool_name,
                    "status": "error",
                    "error_message": str(e),
                    "last_checked": datetime.now().isoformat(),
                    "requires_auth": False,
                    "requires_api_key": False,
                    "api_key_configured": False,
                    "service_available": False,
                })
        
        return {
            "agent_id": agent_id,
            "tools": tool_statuses,
            "total": len(tool_statuses),
            "available": len([t for t in tool_statuses if t.get("status") == "available"]),
            "needs_config": len([t for t in tool_statuses if t.get("status") == "needs_config"]),
            "unavailable": len([t for t in tool_statuses if t.get("status") == "unavailable"]),
        }
    except Exception as e:
        logger.error(f"Failed to get all tools status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get all tools status: {str(e)}")


@router.put("/agents/{agent_id}/tools/{tool_name}/config")
async def update_tool_config(
    agent_id: str,
    tool_name: str,
    config: ToolConfig
) -> Dict[str, Any]:
    """Update configuration for a specific tool"""
    try:
        from src.amas.api.main import get_amas_system
        
        amas = await get_amas_system()
        
        # Get agent
        if not (hasattr(amas, "orchestrator") and amas.orchestrator):
            raise HTTPException(status_code=503, detail="Orchestrator not available")
        
        if not (hasattr(amas.orchestrator, 'agents') and agent_id in amas.orchestrator.agents):
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = amas.orchestrator.agents[agent_id]
        
        # Update tool configuration
        if not hasattr(agent, 'tool_config'):
            agent.tool_config = {}
        
        agent.tool_config[tool_name] = {
            "enabled": config.enabled,
            "config": config.config,
        }
        
        # If API key provided, store it (in production, use secure storage)
        if config.api_key:
            # In production, encrypt and store in secure vault
            # For now, just log that it was set
            logger.info(f"API key configured for tool {tool_name} on agent {agent_id}")
            agent.tool_config[tool_name]["api_key_set"] = True
        
        # Broadcast update via WebSocket
        if WEBSOCKET_AVAILABLE and websocket_manager:
            try:
                await websocket_manager.broadcast({
                    "event": "tool_config_updated",
                    "agent_id": agent_id,
                    "tool_name": tool_name,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"WebSocket broadcast failed (non-critical): {e}")
        
        return {
            "agent_id": agent_id,
            "tool_name": tool_name,
            "config": agent.tool_config[tool_name],
            "message": "Tool configuration updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update tool config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update tool config: {str(e)}")


@router.put("/agents/{agent_id}/tools/config")
async def update_agent_tools_config(
    agent_id: str,
    config: AgentToolConfig
) -> Dict[str, Any]:
    """Update configuration for all tools of an agent"""
    try:
        from src.amas.api.main import get_amas_system
        
        amas = await get_amas_system()
        
        # Get agent
        if not (hasattr(amas, "orchestrator") and amas.orchestrator):
            raise HTTPException(status_code=503, detail="Orchestrator not available")
        
        if not (hasattr(amas.orchestrator, 'agents') and agent_id in amas.orchestrator.agents):
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = amas.orchestrator.agents[agent_id]
        
        # Initialize tool_config if not exists
        if not hasattr(agent, 'tool_config'):
            agent.tool_config = {}
        
        # Update all tool configurations
        for tool_config in config.tools:
            agent.tool_config[tool_config.tool_name] = {
                "enabled": tool_config.enabled,
                "config": tool_config.config,
            }
            
            if tool_config.api_key:
                logger.info(f"API key configured for tool {tool_config.tool_name} on agent {agent_id}")
                agent.tool_config[tool_config.tool_name]["api_key_set"] = True
        
        # Update agent-level tool settings
        if not hasattr(agent, 'tool_settings'):
            agent.tool_settings = {}
        
        agent.tool_settings = {
            "tool_strategy": config.tool_strategy,
            "max_tools": config.max_tools,
            "use_ai_synthesis": config.use_ai_synthesis,
        }
        
        # Broadcast update via WebSocket
        if WEBSOCKET_AVAILABLE and websocket_manager:
            try:
                await websocket_manager.broadcast({
                    "event": "agent_tools_config_updated",
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"WebSocket broadcast failed (non-critical): {e}")
        
        return {
            "agent_id": agent_id,
            "message": "Agent tools configuration updated successfully",
            "tools_configured": len(config.tools),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent tools config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update agent tools config: {str(e)}")


@router.post("/agents/{agent_id}/tools/{tool_name}/test")
async def test_tool(agent_id: str, tool_name: str) -> Dict[str, Any]:
    """Test a tool to verify it's working"""
    try:
        from src.amas.agents.tools import get_tool_registry
        
        registry = get_tool_registry()
        tool = registry.get(tool_name)
        
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
        
        # Try to execute tool with minimal test parameters
        test_params = {}
        if hasattr(tool, 'get_schema'):
            schema = tool.get_schema()
            # Try to create minimal valid parameters from schema
            props = schema.get("properties", {})
            for prop_name, prop_def in props.items():
                if "default" in prop_def:
                    test_params[prop_name] = prop_def["default"]
                elif prop_def.get("type") == "string":
                    test_params[prop_name] = "test"
                elif prop_def.get("type") == "integer":
                    test_params[prop_name] = 1
                elif prop_def.get("type") == "boolean":
                    test_params[prop_name] = False
        
        # Execute tool
        try:
            result = await tool.execute(test_params)
            success = result.get("success", False)
            
            return {
                "tool_name": tool_name,
                "success": success,
                "message": "Tool test completed",
                "result": result if success else None,
                "error": result.get("error") if not success else None,
                "tested_at": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "tool_name": tool_name,
                "success": False,
                "message": "Tool test failed",
                "error": str(e),
                "tested_at": datetime.now().isoformat(),
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test tool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to test tool: {str(e)}")

