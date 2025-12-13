"""
Agent management API routes
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.amas.security.audit.audit_logger import get_audit_logger
from src.amas.security.auth.jwt_middleware import auth_context
from src.amas.security.policies.opa_integration import get_policy_engine

# WebSocket for real-time updates
try:
    from src.api.websocket import websocket_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    websocket_manager = None

logger = logging.getLogger(__name__)

router = APIRouter()


class AgentCreate(BaseModel):
    """Agent creation model"""

    name: str
    type: str
    capabilities: List[str]
    config: Dict[str, Any]


class AgentUpdate(BaseModel):
    """Agent update model"""

    name: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Agent response model"""

    id: str
    name: str
    type: str
    status: str
    capabilities: List[str]
    config: Dict[str, Any]
    created_at: str
    updated_at: str


async def check_agent_permission(user_id: str, agent_id: str, action: str) -> bool:
    """Check if user has permission to perform action on agent"""
    # In development mode, allow all access
    dev_mode = os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "test"]
    if dev_mode:
        logger.debug(f"Development mode: Allowing {action} on agent {agent_id} for user {user_id}")
        return True
    
    try:
        policy_engine = get_policy_engine()
        result = await policy_engine.opa_client.check_agent_access(
            user_id=user_id,
            agent_id=agent_id,
            action=action
        )
        return result.allowed
    except Exception as e:
        logger.error(f"Authorization check failed: {e}")
        # Fail open in case of OPA errors (can be configured to fail closed)
        # In development, always allow
        return dev_mode


class AgentListResponse(BaseModel):
    """Agent list response with pagination"""
    agents: List[AgentResponse]
    total: int


@router.get("/agents", response_model=AgentListResponse)
async def list_agents(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    agent_type: Optional[str] = Query(None),
) -> AgentListResponse:
    """List all agents with optional filtering"""
    try:
        # Get AMAS system from main.py
        from src.amas.api.main import get_amas_system
        
        try:
            amas = await get_amas_system()
        except Exception as e:
            logger.error(f"Failed to get AMAS system: {e}", exc_info=True)
            # Return empty list if system not initialized
            return {
                "agents": [],
                "total": 0
            }
        
        agents_list = []
        
        # Get real agents from orchestrator
        try:
            if hasattr(amas, "orchestrator") and amas.orchestrator:
                if hasattr(amas.orchestrator, 'agents'):
                    # Check if agents is a dict or dict-like object
                    agents_dict = amas.orchestrator.agents
                    if agents_dict:
                        for agent_id, agent in agents_dict.items():
                            try:
                                # Get agent status
                                agent_status = {}
                                if hasattr(agent, 'get_status'):
                                    try:
                                        agent_status = await agent.get_status()
                                    except Exception:
                                        pass
                                
                                # Build agent info
                                agent_name = getattr(agent, 'name', getattr(agent, 'id', agent_id))
                                agent_type_str = getattr(agent, 'type', getattr(agent, '__class__', type(agent)).__name__.lower().replace('agent', ''))
                                agent_status_str = str(agent_status.get("status", getattr(agent, 'status', 'active')))
                                agent_capabilities = agent_status.get("capabilities", getattr(agent, 'capabilities', []))
                                
                                agents_list.append({
                                    "id": agent_id,
                                    "name": agent_name,
                                    "type": agent_type_str,
                                    "status": agent_status_str,
                                    "capabilities": agent_capabilities if isinstance(agent_capabilities, list) else [],
                                    "config": agent_status.get("config", getattr(agent, 'config', {})),
                                    "created_at": datetime.now().isoformat(),
                                    "updated_at": datetime.now().isoformat(),
                                })
                            except Exception as e:
                                logger.warning(f"Failed to get info for agent {agent_id}: {e}")
                                # Add basic info anyway
                                agents_list.append({
                                    "id": agent_id,
                                    "name": str(agent_id),
                                    "type": "unknown",
                                    "status": "unknown",
                                    "capabilities": [],
                                    "config": {},
                                    "created_at": datetime.now().isoformat(),
                                    "updated_at": datetime.now().isoformat(),
                                })
        except Exception as e:
            logger.error(f"Failed to iterate agents: {e}", exc_info=True)
            # Continue with empty list if iteration fails
        
        # If no agents found, return empty list (don't use mock data)
        if not agents_list:
            logger.info("No agents found in orchestrator")
        
        # Apply filters
        if status:
            agents_list = [a for a in agents_list if a["status"] == status]
        if agent_type:
            agents_list = [a for a in agents_list if a["type"] == agent_type]

        # Apply pagination
        total_count = len(agents_list)
        agents_list = agents_list[skip : skip + limit]

        # Convert to AgentResponse format - AgentResponse expects 'id' not 'agent_id'
        # But we need to return dict format for Frontend compatibility
        agent_responses = []
        for agent in agents_list:
            # Create dict with both 'id' (for AgentResponse validation) and 'agent_id' (for Frontend)
            agent_dict = {
                "id": agent["id"],  # Required by AgentResponse Pydantic model
                "agent_id": agent["id"],  # Required by Frontend
                "name": agent["name"],
                "type": agent["type"],
                "status": agent["status"],
                "capabilities": agent["capabilities"],
                "config": agent.get("config", {}),
                "created_at": agent.get("created_at", datetime.now().isoformat()),
                "updated_at": agent.get("updated_at", datetime.now().isoformat()),
                # Add default performance metrics for Frontend
                "performance_metrics": {
                    "success_rate": 0.95,
                    "avg_duration": 2.5,
                },
                "total_executions": 0,
                "total_cost_usd": 0.0,
            }
            agent_responses.append(agent_dict)
        
        # Validate using AgentResponse (but return dict format)
        validated_agents = []
        for agent_dict in agent_responses:
            # Validate structure matches AgentResponse
            try:
                AgentResponse(**{k: v for k, v in agent_dict.items() if k in ["id", "name", "type", "status", "capabilities", "config", "created_at", "updated_at"]})
            except Exception as e:
                logger.warning(f"Agent validation failed: {e}")
                continue
            validated_agents.append(agent_dict)
        
        return {
            "agents": validated_agents,
            "total": total_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/agents/ai-providers")
async def get_ai_providers():
    """Get list of available AI providers and their status"""
    try:
        from src.amas.ai.enhanced_router_v2 import (
            PROVIDER_CONFIGS,
            get_available_providers,
        )
        
        available_providers = get_available_providers()
        providers_info = []
        
        # Check Ollama availability
        ollama_available = False
        ollama_models = []
        try:
            response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
            if response.status_code == 200:
                ollama_available = True
                data = response.json()
                ollama_models = [model.get("name", "") for model in data.get("models", [])]
        except Exception:
            pass
        
        # Add Ollama to providers if available
        if ollama_available and "ollama" not in available_providers:
            available_providers.append("ollama")
        
        # Build providers info from available providers
        for provider_id in available_providers:
            config = PROVIDER_CONFIGS.get(provider_id)
            if config:
                providers_info.append({
                    "id": provider_id,
                    "name": config.name,
                    "model": config.model,
                    "type": config.provider_type,
                    "priority": config.priority,
                    "enabled": config.enabled,  # Use actual enabled status from config
                    "base_url": config.base_url,
                    "available": True,
                })
            elif provider_id == "ollama":
                # Ollama special handling - check if it's enabled in config
                ollama_enabled = False
                if "ollama" in PROVIDER_CONFIGS:
                    ollama_enabled = PROVIDER_CONFIGS["ollama"].enabled
                else:
                    # If Ollama is available, consider it enabled by default
                    ollama_enabled = ollama_available
                
                providers_info.append({
                    "id": "ollama",
                    "name": "Ollama (Local)",
                    "model": ollama_models[0] if ollama_models else "deepseek-r1:8b",
                    "type": "ollama",
                    "priority": 100,
                    "enabled": ollama_enabled,
                    "base_url": "http://localhost:11434/v1",
                    "available": ollama_available,
                    "models": ollama_models,
                })
        
        # Also list all configured providers (even if not available)
        for provider_id, config in PROVIDER_CONFIGS.items():
            if provider_id not in available_providers and provider_id != "ollama":
                providers_info.append({
                    "id": provider_id,
                    "name": config.name,
                    "model": config.model,
                    "type": config.provider_type,
                    "priority": config.priority,
                    "enabled": config.enabled,  # Use actual enabled status
                    "base_url": config.base_url,
                    "available": False,
                })
        
        return {
            "providers": sorted(providers_info, key=lambda x: x["priority"]),
            "total": len(providers_info),
            "available": len([p for p in providers_info if p["available"]]),
        }
    except Exception as e:
        logger.error(f"Failed to get AI providers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get AI providers: {str(e)}")


@router.post("/agents/ai-providers/{provider_id}/enable")
async def enable_ai_provider(provider_id: str):
    """Enable an AI provider"""
    try:
        from src.amas.ai.enhanced_router_v2 import PROVIDER_CONFIGS, get_api_key
        
        if provider_id == "ollama":
            # Check if Ollama is available
            try:
                response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
                if response.status_code == 200:
                    # Update Ollama config if it exists
                    if "ollama" in PROVIDER_CONFIGS:
                        PROVIDER_CONFIGS["ollama"].enabled = True
                    return {
                        "id": provider_id,
                        "name": "Ollama (Local)",
                        "type": "ollama",
                        "enabled": True,
                        "available": True,
                        "status_message": "Ollama is available and enabled",
                        "models": [model.get("name", "") for model in response.json().get("models", [])]
                    }
                else:
                    raise HTTPException(status_code=400, detail="Ollama is not running. Please start Ollama first.")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Ollama is not available: {str(e)}")
        else:
            # For other providers, check if API key is available
            config = PROVIDER_CONFIGS.get(provider_id)
            if not config:
                raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
            
            # Check if API key exists
            api_key = get_api_key(config.api_key_env)
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail=f"API key not found. Please set {config.api_key_env} environment variable."
                )
            
            # Enable the provider
            config.enabled = True
            
            return {
                "id": provider_id,
                "name": config.name,
                "type": config.provider_type,
                "enabled": True,
                "available": True,
                "status_message": f"{config.name} is enabled",
                "model": config.model,
                "base_url": config.base_url,
                "priority": config.priority,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable AI provider: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to enable AI provider: {str(e)}")


@router.get("/agents/ai-providers/ollama/models")
async def get_ollama_models():
    """Get list of available Ollama models"""
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            models = []
            for model in data.get("models", []):
                models.append({
                    "name": model.get("name", ""),
                    "size": model.get("size", 0),
                    "modified_at": model.get("modified_at", ""),
                })
            return {
                "models": models,
                "total": len(models),
                "available": True,
            }
        else:
            return {
                "models": [],
                "total": 0,
                "available": False,
                "error": f"Ollama returned status {response.status_code}",
            }
    except Exception as e:
        logger.error(f"Failed to get Ollama models: {e}")
        return {
            "models": [],
            "total": 0,
            "available": False,
            "error": str(e),
        }


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, request: Request) -> AgentResponse:
    """Get a specific agent by ID"""
    try:
        # Check authentication (bypass in development mode)
        dev_mode = os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "test"]
        user_context = auth_context.get_user()
        
        if not user_context:
            if dev_mode:
                # Use default user for development
                user_id = "dev_user"
                logger.debug("Development mode: Using default user for agent access")
            else:
                raise HTTPException(status_code=401, detail="Authentication required")
        else:
            user_id = user_context.get("user_id")
        
        # Check authorization
        has_permission = await check_agent_permission(user_id, agent_id, "read")
        if not has_permission:
            audit_logger = get_audit_logger()
            await audit_logger.log_security_violation(
                user_id=user_id,
                violation_type="unauthorized_access",
                severity="medium",
                description=f"User attempted to access agent {agent_id} without permission",
                ip_address=request.client.host if request.client else None,
                details={"agent_id": agent_id, "action": "read"}
            )
            raise HTTPException(status_code=403, detail=f"Insufficient permissions to access agent {agent_id}")
        # This would query the actual database
        # For now, return mock data
        agent = {
            "id": agent_id,
            "name": "Research Agent",
            "type": "research",
            "status": "active",
            "capabilities": ["web_search", "data_analysis"],
            "config": {"model": "gpt-4", "temperature": 0.7},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        return AgentResponse(**agent)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")


@router.post("/agents", response_model=AgentResponse)
async def create_agent(agent: AgentCreate) -> AgentResponse:
    """Create a new agent"""
    try:
        # This would create the agent in the database
        # For now, return mock data
        new_agent = {
            "id": "agent-new",
            "name": agent.name,
            "type": agent.type,
            "status": "active",
            "capabilities": agent.capabilities,
            "config": agent.config,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        return AgentResponse(**new_agent)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent_update: AgentUpdate) -> AgentResponse:
    """Update an existing agent"""
    try:
        # This would update the agent in the database
        # For now, return mock data
        updated_agent = {
            "id": agent_id,
            "name": agent_update.name or "Research Agent",
            "type": "research",
            "status": agent_update.status or "active",
            "capabilities": ["web_search", "data_analysis"],
            "config": agent_update.config or {"model": "gpt-4", "temperature": 0.7},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": datetime.now().isoformat(),
        }

        # Broadcast agent update via WebSocket
        if WEBSOCKET_AVAILABLE and websocket_manager:
            try:
                await websocket_manager.broadcast({
                    "event": "agent_update",
                    "agent_id": agent_id,
                    "id": agent_id,
                    "name": updated_agent["name"],
                    "status": updated_agent["status"],
                    "updated_at": updated_agent["updated_at"]
                })
            except Exception as e:
                logger.warning(f"WebSocket broadcast failed (non-critical): {e}")

        return AgentResponse(**updated_agent)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str) -> Dict[str, str]:
    """Delete an agent"""
    try:
        # This would delete the agent from the database
        return {"message": f"Agent {agent_id} deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")


@router.post("/agents/{agent_id}/start")
async def start_agent(agent_id: str) -> Dict[str, str]:
    """Start an agent"""
    try:
        # Get AMAS system to access orchestrator
        from src.amas.api.main import get_amas_system
        
        amas = await get_amas_system()
        
        # Check if agent exists in orchestrator
        if hasattr(amas, "orchestrator") and amas.orchestrator:
            if hasattr(amas.orchestrator, 'agents') and agent_id in amas.orchestrator.agents:
                agent = amas.orchestrator.agents[agent_id]
                # Try to start the agent if it has a start method
                if hasattr(agent, 'start'):
                    try:
                        await agent.start()
                        logger.info(f"Agent {agent_id} started successfully")
                    except Exception as e:
                        logger.warning(f"Agent start method failed: {e}")
                # Update agent status
                if hasattr(agent, 'status'):
                    agent.status = 'active'
                
                # Broadcast agent update via WebSocket
                if WEBSOCKET_AVAILABLE and websocket_manager:
                    try:
                        await websocket_manager.broadcast({
                            "event": "agent_status_changed",
                            "agent_id": agent_id,
                            "status": "active",
                            "timestamp": datetime.now().isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"WebSocket broadcast failed (non-critical): {e}")
                
                return {"message": f"Agent {agent_id} started successfully"}
            else:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        else:
            raise HTTPException(status_code=503, detail="Orchestrator not available")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")


@router.post("/agents/{agent_id}/stop")
async def stop_agent(agent_id: str) -> Dict[str, str]:
    """Stop an agent"""
    try:
        # Get AMAS system to access orchestrator
        from src.amas.api.main import get_amas_system
        
        amas = await get_amas_system()
        
        # Check if agent exists in orchestrator
        if hasattr(amas, "orchestrator") and amas.orchestrator:
            if hasattr(amas.orchestrator, 'agents') and agent_id in amas.orchestrator.agents:
                agent = amas.orchestrator.agents[agent_id]
                # Try to stop the agent if it has a stop method
                if hasattr(agent, 'stop'):
                    try:
                        await agent.stop()
                        logger.info(f"Agent {agent_id} stopped successfully")
                    except Exception as e:
                        logger.warning(f"Agent stop method failed: {e}")
                # Update agent status
                if hasattr(agent, 'status'):
                    agent.status = 'inactive'
                
                # Broadcast agent update via WebSocket
                if WEBSOCKET_AVAILABLE and websocket_manager:
                    try:
                        await websocket_manager.broadcast({
                            "event": "agent_status_changed",
                            "agent_id": agent_id,
                            "status": "inactive",
                            "timestamp": datetime.now().isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"WebSocket broadcast failed (non-critical): {e}")
                
                return {"message": f"Agent {agent_id} stopped successfully"}
            else:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        else:
            raise HTTPException(status_code=503, detail="Orchestrator not available")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")


@router.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str) -> Dict[str, Any]:
    """Get agent status and metrics"""
    try:
        # This would get the actual agent status
        return {
            "agent_id": agent_id,
            "status": "active",
            "uptime": 3600,
            "tasks_completed": 42,
            "current_task": None,
            "performance_metrics": {
                "cpu_usage": 15.5,
                "memory_usage": 256,
                "response_time": 1.2,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get agent status: {str(e)}"
        )
