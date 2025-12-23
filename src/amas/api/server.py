#!/usr/bin/env python3
"""
AMAS API Server
FastAPI-based REST API for AMAS system
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import managers with graceful fallback
# These will be imported in startup_event if available
orchestrator = None  # Will be initialized in startup
intelligence_manager = None  # Will be initialized in startup
provider_manager = None  # Will be initialized in startup

# Create FastAPI app
app = FastAPI(
    title="AMAS API",
    description="Advanced Multi-Agent Intelligence System API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class TaskRequest(BaseModel):
    task_type: str
    target: str
    parameters: Optional[Dict[str, Any]] = {}
    user_id: Optional[str] = "api_user"


class TaskResponse(BaseModel):
    task_id: str
    status: str
    execution_time: float
    agents_used: List[str]
    result: Dict[str, Any]


class SystemStatus(BaseModel):
    system_status: str
    agents: Dict[str, int]
    providers: Dict[str, Any]
    tasks: Dict[str, int]
    intelligence: Dict[str, Any]
    timestamp: str


# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with system information"""
    return """
    <html>
        <head>
            <title>AMAS - Advanced Multi-Agent Intelligence System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #2c3e50; }
                .status { color: #27ae60; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1 class="header">🚀 AMAS - Advanced Multi-Agent Intelligence System</h1>
            <p class="status">✅ System is running</p>
            <p>API Documentation: <a href="/api/docs">/api/docs</a></p>
            <p>Dashboard: <a href="/dashboard">/dashboard</a></p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Get comprehensive system status"""
    try:
        if orchestrator:
            status = await orchestrator.get_system_status()
            return SystemStatus(**status)
        else:
            return SystemStatus(
                system_status="initializing",
                agents={},
                providers={},
                tasks={},
                intelligence={},
                timestamp=datetime.now().isoformat()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents")
async def get_agents():
    """Get all available agents and their capabilities"""
    try:
        if orchestrator:
            # Get agents from orchestrator
            agents_list = []
            for agent_id, agent in orchestrator.agents.items():
                agent_info = {
                    "agent_id": agent_id,
                    "name": getattr(agent, 'name', getattr(agent, 'id', agent_id)),
                    "type": getattr(agent, 'type', 'unknown'),
                    "capabilities": getattr(agent, 'capabilities', []),
                    "status": str(getattr(agent, 'status', 'unknown')),
                }
                agents_list.append(agent_info)
            return {"agents": agents_list}
        else:
            return {"agents": [], "message": "Orchestrator not initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/providers")
async def get_providers():
    """Get AI provider status"""
    try:
        if provider_manager:
            status = provider_manager.get_provider_status()
            return {"providers": status}
        else:
            from src.amas.ai.enhanced_router_v2 import get_available_providers
            providers = get_available_providers()
            return {"providers": providers, "message": "Using enhanced router"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tasks", response_model=TaskResponse)
async def execute_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Execute a new task"""
    try:
        if orchestrator:
            import uuid
            task_id = str(uuid.uuid4())
            result = await orchestrator.execute_task(
                task_id=task_id,
                task_type=task_request.task_type,
                target=task_request.target,
                parameters=task_request.parameters or {},
            )
            return TaskResponse(**result)
        else:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific task"""
    # This would be implemented with proper task tracking
    return {
        "task_id": task_id,
        "status": "completed",
        "message": "Task tracking not implemented yet",
    }


@app.get("/api/intelligence")
async def get_intelligence_status():
    """Get intelligence system status"""
    try:
        if intelligence_manager:
            data = await intelligence_manager.get_intelligence_dashboard_data()
            return data
        else:
            return {"status": "not_initialized", "message": "Intelligence manager not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/intelligence/learn")
async def trigger_learning():
    """Trigger collective learning cycle"""
    try:
        # This would trigger the learning cycle
        return {"message": "Learning cycle triggered", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files for dashboard
try:
    app.mount(
        "/dashboard", StaticFiles(directory="frontend/dist", html=True), name="dashboard"
    )
except Exception:
    # If build directory doesn't exist, create a simple dashboard
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        return """
        <html>
            <head><title>AMAS Dashboard</title></head>
            <body>
                <h1>AMAS Dashboard</h1>
                <p>React dashboard not built yet. Run: cd frontend && npm install && npm run build</p>
            </body>
        </html>
        """


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize AMAS on startup"""
    logging.info("🚀 Starting AMAS API Server...")

    # Initialize orchestrator and intelligence manager if available
    global orchestrator, intelligence_manager, provider_manager
    try:
        from ..core.unified_intelligence_orchestrator import (
            UnifiedIntelligenceOrchestrator,
        )
        orchestrator = UnifiedIntelligenceOrchestrator()
        # UnifiedIntelligenceOrchestrator doesn't have initialize() - it initializes in __init__
        # await orchestrator.initialize()  # Not needed
        logging.info("✅ Orchestrator initialized")
    except Exception as e:
        logging.warning(f"Could not initialize orchestrator: {e}")
    
    try:
        from ..intelligence.intelligence_manager import AMASIntelligenceManager
        intelligence_manager = AMASIntelligenceManager()
        if hasattr(intelligence_manager, 'start_intelligence_systems'):
            await intelligence_manager.start_intelligence_systems()
        logging.info("✅ Intelligence manager initialized")
    except Exception as e:
        logging.warning(f"Could not initialize intelligence manager: {e}")

    logging.info("✅ AMAS API Server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logging.info("👋 Shutting down AMAS API Server...")


# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
