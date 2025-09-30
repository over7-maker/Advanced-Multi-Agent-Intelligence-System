"""
FastAPI Main Application for AMAS Intelligence System
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

# Import AMAS system
from ..main import AMASApplication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AMAS Intelligence System API",
    description="Advanced Multi-Agent Intelligence System API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global AMAS instance
amas_app = None

# Pydantic models
class TaskRequest(BaseModel):
    type: str
    description: str
    parameters: Dict[str, Any] = {}
    priority: int = 2

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class SystemStatus(BaseModel):
    status: str
    agents: int
    active_tasks: int
    total_tasks: int
    timestamp: str

class HealthCheck(BaseModel):
    status: str
    services: Dict[str, Any]
    timestamp: str

# Dependency to get AMAS system
async def get_amas_system():
    global amas_app
    if amas_app is None:
        raise HTTPException(status_code=503, detail="AMAS system not initialized")
    return amas_app

# Dependency to verify authentication
async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Mock authentication - in production, this would verify JWT tokens
    if credentials.credentials != "valid_token":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return {"user_id": "admin", "role": "admin"}

# Startup event
@app.on_event("startup")
async def startup_event():
    global amas_app
    try:
        logger.info("Initializing AMAS Intelligence System...")

        # Initialize AMAS application
        amas_app = AMASApplication()
        await amas_app.initialize()

        logger.info("AMAS Intelligence System initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize AMAS system: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    global amas_app
    if amas_app:
        await amas_app.shutdown()
        logger.info("AMAS Intelligence System shutdown complete")

# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Get system health status"""
    try:
        amas = await get_amas_system()

        # Get service health
        service_health = await amas.service_manager.health_check_all_services()

        return HealthCheck(
            status=service_health.get('overall_status', 'unknown'),
            services=service_health.get('services', {}),
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="unhealthy",
            services={"error": str(e)},
            timestamp=datetime.utcnow().isoformat()
        )

# System status endpoint
@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status"""
    try:
        amas = await get_amas_system()
        status = await amas.orchestrator.get_system_status()

        return SystemStatus(
            status=status.get('orchestrator_status', 'unknown'),
            agents=status.get('active_agents', 0),
            active_tasks=status.get('active_tasks', 0),
            total_tasks=status.get('total_tasks', 0),
            timestamp=status.get('timestamp', datetime.utcnow().isoformat())
        )

    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Submit task endpoint
@app.post("/tasks", response_model=TaskResponse)
async def submit_task(
    task_request: TaskRequest,
    background_tasks: BackgroundTasks,
    auth: dict = Depends(verify_auth)
):
    """Submit a new intelligence task"""
    try:
        amas = await get_amas_system()

        # Submit task
        task_id = await amas.orchestrator.submit_task(
            task_type=task_request.type,
            description=task_request.description,
            parameters=task_request.parameters,
            priority=task_request.priority
        )

        # Log audit event
        security_service = amas.service_manager.get_security_service()
        if security_service:
            await security_service.log_audit_event(
                event_type='task_submission',
                user_id=auth['user_id'],
                action='submit_task',
                details=f'Task submitted: {task_request.type}',
                classification='system'
            )

        return TaskResponse(
            task_id=task_id,
            status="submitted",
            message="Task submitted successfully"
        )

    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get task status endpoint
@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str, auth: dict = Depends(verify_auth)):
    """Get task status"""
    try:
        amas = await get_amas_system()

        # Get task status from orchestrator
        task_status = await amas.orchestrator.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")

        return task_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get agents endpoint
@app.get("/agents")
async def get_agents(auth: dict = Depends(verify_auth)):
    """Get list of agents"""
    try:
        amas = await get_amas_system()

        # Get agents from orchestrator
        agents = await amas.orchestrator.list_agents()
        return {'agents': agents}

    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get agent status endpoint
@app.get("/agents/{agent_id}")
async def get_agent_status(agent_id: str, auth: dict = Depends(verify_auth)):
    """Get specific agent status"""
    try:
        amas = await get_amas_system()

        # Get agent status from orchestrator
        agent_status = await amas.orchestrator.get_agent_status(agent_id)
        if not agent_status:
            raise HTTPException(status_code=404, detail="Agent not found")

        return agent_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Execute workflow endpoint
@app.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    parameters: Dict[str, Any],
    background_tasks: BackgroundTasks,
    auth: dict = Depends(verify_auth)
):
    """Execute a workflow"""
    try:
        amas = await get_amas_system()

        # Execute workflow
        result = await amas.orchestrator.execute_workflow(workflow_id, parameters)

        # Log audit event
        security_service = amas.service_manager.get_security_service()
        if security_service:
            await security_service.log_audit_event(
                event_type='workflow_execution',
                user_id=auth['user_id'],
                action='execute_workflow',
                details=f'Workflow executed: {workflow_id}',
                classification='system'
            )

        return result

    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get audit log endpoint
@app.get("/audit")
async def get_audit_log(
    user_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    auth: dict = Depends(verify_auth)
):
    """Get audit log"""
    try:
        amas = await get_amas_system()

        # Get audit log
        security_service = amas.service_manager.get_security_service()
        if not security_service:
            raise HTTPException(status_code=503, detail="Security service not available")
            
        audit_log = await security_service.get_audit_log(
            user_id=user_id,
            event_type=event_type
        )

        # Limit results
        audit_log = audit_log[:limit]

        return {'audit_log': audit_log}

    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AMAS Intelligence System API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
