#!/usr/bin/env python3
"""
AMAS API Server
FastAPI-based REST API for AMAS system
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime

from ..orchestrator import orchestrator
from ..providers.manager import provider_manager
from ..intelligence.intelligence_manager import intelligence_manager

# Create FastAPI app
app = FastAPI(
    title="AMAS API",
    description="Advanced Multi-Agent Intelligence System API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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
        status = await orchestrator.get_system_status()
        return SystemStatus(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
async def get_agents():
    """Get all available agents and their capabilities"""
    try:
        capabilities = await orchestrator.get_agent_capabilities()
        return {"agents": capabilities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/providers")
async def get_providers():
    """Get AI provider status"""
    try:
        status = provider_manager.get_provider_status()
        return {"providers": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks", response_model=TaskResponse)
async def execute_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Execute a new task"""
    try:
        result = await orchestrator.execute_task(
            task_type=task_request.task_type,
            target=task_request.target,
            parameters=task_request.parameters,
            user_id=task_request.user_id
        )
        return TaskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific task"""
    # This would be implemented with proper task tracking
    return {"task_id": task_id, "status": "completed", "message": "Task tracking not implemented yet"}

@app.get("/api/intelligence")
async def get_intelligence_status():
    """Get intelligence system status"""
    try:
        data = await intelligence_manager.get_intelligence_dashboard_data()
        return data
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
    app.mount("/dashboard", StaticFiles(directory="web/build", html=True), name="dashboard")
except:
    # If build directory doesn't exist, create a simple dashboard
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        return """
        <html>
            <head><title>AMAS Dashboard</title></head>
            <body>
                <h1>AMAS Dashboard</h1>
                <p>React dashboard not built yet. Run: cd web && npm install && npm run build</p>
            </body>
        </html>
        """

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize AMAS on startup"""
    logging.info("🚀 Starting AMAS API Server...")
    
    # Start intelligence systems
    await intelligence_manager.start_intelligence_systems()
    
    logging.info("✅ AMAS API Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logging.info("👋 Shutting down AMAS API Server...")

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)