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
from main import AMASIntelligenceSystem

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
amas_system = None

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
    global amas_system
    if amas_system is None:
        raise HTTPException(status_code=503, detail="AMAS system not initialized")
    return amas_system

# Dependency to verify authentication
async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Mock authentication - in production, this would verify JWT tokens
    if credentials.credentials != "valid_token":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return {"user_id": "admin", "role": "admin"}

# Startup event
@app.on_event("startup")
async def startup_event():
    global amas_system
    try:
        logger.info("Initializing AMAS Intelligence System...")
        
        # Configuration
        config = {
            'llm_service_url': 'http://localhost:11434',
            'vector_service_url': 'http://localhost:8001',
            'graph_service_url': 'bolt://localhost:7687',
            'postgres_host': 'localhost',
            'postgres_port': 5432,
            'postgres_user': 'amas',
            'postgres_password': 'amas123',
            'postgres_db': 'amas',
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 0,
            'neo4j_username': 'neo4j',
            'neo4j_password': 'amas123',
            'neo4j_database': 'neo4j',
            'jwt_secret': 'amas_jwt_secret_key_2024_secure',
            'encryption_key': 'amas_encryption_key_2024_secure_32_chars',
            'deepseek_api_key': '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',
            'glm_api_key': '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',
            'grok_api_key': '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',
            'n8n_url': 'http://localhost:5678',
            'n8n_api_key': 'your_n8n_api_key_here'
        }
        
        # Initialize AMAS system
        amas_system = AMASIntelligenceSystem(config)
        await amas_system.initialize()
        
        logger.info("AMAS Intelligence System initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize AMAS system: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    global amas_system
    if amas_system:
        await amas_system.shutdown()
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
        status = await amas.get_system_status()
        
        return SystemStatus(
            status=status.get('status', 'unknown'),
            agents=status.get('agents', 0),
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
        task_id = await amas.submit_intelligence_task({
            'type': task_request.type,
            'description': task_request.description,
            'parameters': task_request.parameters,
            'priority': task_request.priority
        })
        
        # Log audit event
        await amas.security_service.log_audit_event(
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
        
        # Get task from database
        task = await amas.database_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            'task_id': task_id,
            'status': task.get('status', 'unknown'),
            'type': task.get('task_type', 'unknown'),
            'description': task.get('description', ''),
            'created_at': task.get('created_at', ''),
            'started_at': task.get('started_at', ''),
            'completed_at': task.get('completed_at', ''),
            'result': task.get('result', {}),
            'error': task.get('error', '')
        }
        
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
        
        agents = []
        for agent_id, agent in amas.agents.items():
            agent_status = await agent.get_status()
            agents.append({
                'agent_id': agent_id,
                'name': agent_status.get('name', ''),
                'status': agent_status.get('status', 'unknown'),
                'capabilities': agent_status.get('capabilities', []),
                'last_activity': agent_status.get('last_activity', ''),
                'metrics': agent_status.get('metrics', {})
            })
        
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
        
        if agent_id not in amas.agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent = amas.agents[agent_id]
        status = await agent.get_status()
        
        return status
        
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
        result = await amas.execute_intelligence_workflow(workflow_id, parameters)
        
        # Log audit event
        await amas.security_service.log_audit_event(
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
        audit_log = await amas.security_service.get_audit_log(
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