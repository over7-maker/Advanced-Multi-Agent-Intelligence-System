"""
Agent management API routes
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from src.config.settings import get_settings
from src.amas.security.policies.opa_integration import get_policy_engine, PolicyDecision
from src.amas.security.auth.jwt_middleware import auth_context
from src.amas.security.audit.audit_logger import get_audit_logger, AuditEventType, AuditStatus

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
        return False


@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    agent_type: Optional[str] = Query(None),
) -> List[AgentResponse]:
    """List all agents with optional filtering"""
    try:
        # Check authentication
        user_context = auth_context.get_user()
        if not user_context:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = user_context.get("user_id")
        
        # Check authorization - user needs 'read' permission
        # For listing, we check general agent access
        has_permission = await check_agent_permission(user_id, "*", "read")
        if not has_permission:
            audit_logger = get_audit_logger()
            await audit_logger.log_security_violation(
                user_id=user_id,
                violation_type="unauthorized_access",
                severity="medium",
                description=f"User attempted to list agents without permission",
                ip_address=request.client.host if request.client else None,
                details={"action": "list_agents"}
            )
            raise HTTPException(status_code=403, detail="Insufficient permissions to list agents")
        
        # Log successful access
        audit_logger = get_audit_logger()
        await audit_logger.log_data_access(
            user_id=user_id,
            resource_type="agent",
            resource_id="*",
            operation="list",
            status=AuditStatus.SUCCESS,
            trace_id=request.headers.get("X-Trace-ID")
        )
        # This would query the actual database
        # For now, return mock data
        agents = [
            {
                "id": "agent-1",
                "name": "Research Agent",
                "type": "research",
                "status": "active",
                "capabilities": ["web_search", "data_analysis"],
                "config": {"model": "gpt-4", "temperature": 0.7},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "agent-2",
                "name": "Analysis Agent",
                "type": "analysis",
                "status": "active",
                "capabilities": ["data_processing", "visualization"],
                "config": {"model": "gpt-3.5-turbo", "temperature": 0.5},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        ]

        # Apply filters
        if status:
            agents = [a for a in agents if a["status"] == status]
        if agent_type:
            agents = [a for a in agents if a["type"] == agent_type]

        # Apply pagination
        agents = agents[skip : skip + limit]

        return [AgentResponse(**agent) for agent in agents]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, request: Request) -> AgentResponse:
    """Get a specific agent by ID"""
    try:
        # Check authentication
        user_context = auth_context.get_user()
        if not user_context:
            raise HTTPException(status_code=401, detail="Authentication required")
        
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
            "updated_at": "2024-01-01T00:00:00Z",
        }

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
        # This would start the agent
        return {"message": f"Agent {agent_id} started successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")


@router.post("/agents/{agent_id}/stop")
async def stop_agent(agent_id: str) -> Dict[str, str]:
    """Stop an agent"""
    try:
        # This would stop the agent
        return {"message": f"Agent {agent_id} stopped successfully"}

    except Exception as e:
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
