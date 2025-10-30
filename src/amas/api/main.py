"""
FastAPI Main Application for AMAS Intelligence System
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Import AMAS system
from ..main import AMASApplication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AMAS Intelligence System API",
    description="Advanced Multi-Agent Intelligence System API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Middleware to collect HTTP metrics"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate metrics
    duration = time.time() - start_time
    request_size = int(request.headers.get("content-length", 0))
    response_size = len(response.body) if hasattr(response, 'body') else 0
    
    # Record metrics if available
    try:
        from src.amas.services.prometheus_metrics_service import get_metrics_service
        metrics_service = get_metrics_service()
        metrics_service.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
            request_size=request_size,
            response_size=response_size
        )
    except ImportError:
        # Prometheus not available, skip metrics
        pass
    except Exception as e:
        logger.error(f"Failed to record metrics: {e}")
    
    return response

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
    if amas_app is None:
        raise HTTPException(status_code=503, detail="AMAS system not initialized")
    return amas_app


# Dependency to verify authentication
async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Mock authentication - in production, this would verify JWT tokens
    if credentials.credentials != "valid_token":
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return {"user_id": "admin", "role": "admin"}


# Startup event
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Initializing AMAS Intelligence System...")

        # Configuration
        config = {
            "llm_service_url": "http://localhost:11434",
            "vector_service_url": "http://localhost:8001",
            "graph_service_url": "bolt://localhost:7687",
            "postgres_host": "localhost",
            "postgres_port": 5432,
            "postgres_user": "amas",
            "postgres_password": "amas123",
            "postgres_db": "amas",
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_db": 0,
            "neo4j_username": "neo4j",
            "neo4j_password": "amas123",
            "neo4j_database": "neo4j",
            "jwt_secret": os.environ.get(
                "AMAS_JWT_SECRET", "amas_jwt_secret_key_2024_secure"
            ),
            "encryption_key": os.environ.get(
                "AMAS_ENCRYPTION_KEY", "amas_encryption_key_2024_secure_32_chars"
            ),
            "deepseek_api_key": os.environ.get("DEEPSEEK_API_KEY"),
            "glm_api_key": os.environ.get("GLM_API_KEY"),
            "grok_api_key": os.environ.get("GROK_API_KEY"),
            "n8n_url": os.environ.get("N8N_URL", "http://localhost:5678"),
            "n8n_api_key": os.environ.get("N8N_API_KEY"),
        }

        # Initialize AMAS system
        amas_system = AMASApplication(config)
        await amas_system.initialize()

        logger.info("AMAS Intelligence System initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize AMAS system: {e}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    if amas_app:
        await amas_app.shutdown()
        logger.info("AMAS Intelligence System shutdown complete")


# Enhanced health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Get comprehensive system health status"""
    try:
        # Use enhanced health check service if available
        try:
            from src.amas.services.health_check_service import check_health
            health_result = await check_health()
            
            return HealthCheck(
                status=health_result.get("status", "unknown"),
                services=health_result.get("checks", []),
                timestamp=health_result.get("timestamp", datetime.utcnow().isoformat()),
            )
        except ImportError:
            # Fallback to basic health check
            amas = await get_amas_system()
            service_health = await amas.service_manager.health_check_all_services()

            return HealthCheck(
                status=service_health.get("overall_status", "unknown"),
                services=service_health.get("services", {}),
                timestamp=datetime.utcnow().isoformat(),
            )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="unhealthy",
            services={"error": str(e)},
            timestamp=datetime.utcnow().isoformat(),
        )


# Readiness probe endpoint
@app.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe endpoint"""
    try:
        from src.amas.services.health_check_service import check_health
        health_result = await check_health()
        
        if health_result.get("status") == "healthy":
            return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        else:
            return {"status": "not_ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        return {"status": "not_ready", "error": str(e), "timestamp": datetime.utcnow().isoformat()}


# Liveness probe endpoint
@app.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe endpoint"""
    try:
        # Basic liveness check - just ensure the service is responding
        return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Liveness probe failed: {e}")
        return {"status": "not_alive", "error": str(e), "timestamp": datetime.utcnow().isoformat()}


# Detailed health check endpoint
@app.get("/health/detailed")
async def detailed_health_check():
    """Get detailed health information including metrics"""
    try:
        from src.amas.services.health_check_service import check_health
        health_result = await check_health()
        
        # Add additional system information
        import psutil
        process = psutil.Process()
        
        detailed_info = {
            **health_result,
            "system": {
                "process": {
                    "pid": process.pid,
                    "memory_mb": process.memory_info().rss / (1024 * 1024),
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads(),
                },
                "uptime_seconds": time.time() - process.create_time(),
            }
        }
        
        return detailed_info
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


# System status endpoint
@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status"""
    try:
        amas = await get_amas_system()
        status = await amas.orchestrator.get_system_status()

        return SystemStatus(
            status=status.get("status", "unknown"),
            agents=status.get("agents", 0),
            active_tasks=status.get("active_tasks", 0),
            total_tasks=status.get("total_tasks", 0),
            timestamp=status.get("timestamp", datetime.utcnow().isoformat()),
        )

    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Submit task endpoint
@app.post("/tasks", response_model=TaskResponse)
async def submit_task(
    task_request: TaskRequest,
    background_tasks: BackgroundTasks,
    auth: dict = Depends(verify_auth),
):
    """Submit a new intelligence task"""
    try:
        amas = await get_amas_system()

        # Submit task
        task_id = await amas.submit_task(
            {
                "type": task_request.type,
                "description": task_request.description,
                "parameters": task_request.parameters,
                "priority": task_request.priority,
            }
        )

        # Log audit event
        await amas.security_service.log_audit_event(
            event_type="task_submission",
            user_id=auth["user_id"],
            action="submit_task",
            details=f"Task submitted: {task_request.type}",
            classification="system",
        )

        # Log audit event
        security_service = amas.service_manager.get_security_service()
        if security_service:
            await security_service.log_audit_event(
                event_type="task_submission",
                user_id=auth["user_id"],
                action="submit_task",
                details=f"Task submitted: {task_request.type}",
                classification="system",
            )

        return TaskResponse(
            task_id=task_id, status="submitted", message="Task submitted successfully"
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

        # Get task result
        task_result = await amas.get_task_result(task_id)
        if "error" in task_result:
            raise HTTPException(status_code=404, detail=task_result["error"])

        return task_result

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
        if hasattr(amas, "orchestrator") and amas.orchestrator:
            for agent_id, agent in amas.orchestrator.agents.items():
                agent_status = await agent.get_status()
                agents.append(
                    {
                        "agent_id": agent_id,
                        "name": agent_status.get("name", ""),
                        "status": agent_status.get("status", "unknown"),
                        "capabilities": agent_status.get("capabilities", []),
                        "last_activity": agent_status.get("last_activity", ""),
                        "metrics": agent_status.get("metrics", {}),
                    }
                )

        return {"agents": agents}

    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get agent status endpoint
@app.get("/agents/{agent_id}")
async def get_agent_status(agent_id: str, auth: dict = Depends(verify_auth)):
    """Get specific agent status"""
    try:
        amas = await get_amas_system()

        if not hasattr(amas, "orchestrator") or not amas.orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not available")

        if agent_id not in amas.orchestrator.agents:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = amas.orchestrator.agents[agent_id]
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
    auth: dict = Depends(verify_auth),
):
    """Execute a workflow"""
    try:
        amas = await get_amas_system()

        # Execute workflow
        result = await amas.orchestrator.execute_workflow(workflow_id, parameters)

        # Log audit event
        await amas.security_service.log_audit_event(
            event_type="workflow_execution",
            user_id=auth["user_id"],
            action="execute_workflow",
            details=f"Workflow executed: {workflow_id}",
            classification="system",
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
    auth: dict = Depends(verify_auth),
):
    """Get audit log"""
    try:
        amas = await get_amas_system()

        # Get audit log
        audit_log = await amas.security_service.get_audit_log(
            user_id=user_id, event_type=event_type
        )

        # Limit results
        audit_log = audit_log[:limit]

        return {"audit_log": audit_log}

    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        from src.amas.services.prometheus_metrics_service import get_metrics_service
        metrics_service = get_metrics_service()
        metrics_data = metrics_service.get_metrics()
        
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(metrics_data, media_type="text/plain")
    except ImportError:
        return {"error": "Prometheus metrics not available"}
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return {"error": str(e)}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AMAS Intelligence System API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
