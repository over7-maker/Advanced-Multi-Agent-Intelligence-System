"""
AMAS Intelligence System - Main Application

This is the main FastAPI application for the AMAS Intelligence System,
providing REST API endpoints for intelligence operations.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

from core.orchestrator import IntelligenceOrchestrator, TaskPriority
from core.agentic_rag import AgenticRAG
from core.prompt_maker import PromptMaker
from services.n8n_integration import N8NIntegration
from services.llm_service import LLMService
from services.vector_service import VectorService
from services.knowledge_graph import KnowledgeGraphService
from services.security_service import SecurityService


# Pydantic Models
class TaskRequest(BaseModel):
    task_type: str = Field(..., description="Type of task (osint, investigation, forensics, etc.)")
    description: str = Field(..., description="Task description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    priority: str = Field(default="medium", description="Task priority (low, medium, high, critical)")
    workflow_id: Optional[str] = Field(None, description="Optional workflow ID")

class WorkflowRequest(BaseModel):
    workflow_id: str = Field(..., description="Workflow ID to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Workflow parameters")

class AgentStatusResponse(BaseModel):
    agent_id: str
    name: str
    status: str
    capabilities: List[str]
    metrics: Dict[str, Any]
    last_activity: str

class TaskStatusResponse(BaseModel):
    task_id: str
    type: str
    description: str
    status: str
    priority: str
    assigned_agent: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]

class SystemStatusResponse(BaseModel):
    orchestrator_status: str
    active_agents: int
    active_tasks: int
    total_tasks: int
    metrics: Dict[str, Any]
    timestamp: str


# Global variables
orchestrator: Optional[IntelligenceOrchestrator] = None
agentic_rag: Optional[AgenticRAG] = None
prompt_maker: Optional[PromptMaker] = None
n8n_integration: Optional[N8NIntegration] = None
security_service: Optional[SecurityService] = None

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator, agentic_rag, prompt_maker, n8n_integration, security_service
    
    # Startup
    logging.info("Starting AMAS Intelligence System...")
    
    try:
        # Initialize services
        llm_service = LLMService(
            host=os.getenv("AMAS_LLM_HOST", "localhost:11434"),
            api_key=os.getenv("AMAS_LLM_API_KEY")
        )
        
        vector_service = VectorService(
            host=os.getenv("AMAS_VECTOR_HOST", "localhost:8001"),
            api_key=os.getenv("AMAS_VECTOR_API_KEY")
        )
        
        knowledge_graph = KnowledgeGraphService(
            host=os.getenv("AMAS_GRAPH_HOST", "localhost:7474"),
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password")
        )
        
        security_service = SecurityService(
            jwt_secret=os.getenv("AMAS_JWT_SECRET", "your-secret-key"),
            encryption_key=os.getenv("AMAS_ENCRYPTION_KEY", "your-encryption-key")
        )
        
        # Initialize core components
        orchestrator = IntelligenceOrchestrator(
            llm_service=llm_service,
            vector_service=vector_service,
            knowledge_graph=knowledge_graph,
            security_service=security_service
        )
        
        agentic_rag = AgenticRAG(
            vector_service=vector_service,
            knowledge_graph=knowledge_graph,
            llm_service=llm_service,
            orchestrator=orchestrator
        )
        
        prompt_maker = PromptMaker(
            llm_service=llm_service,
            vector_service=vector_service
        )
        
        n8n_integration = N8NIntegration(
            n8n_url=os.getenv("N8N_URL", "http://localhost:5678"),
            username=os.getenv("N8N_USERNAME", "admin"),
            password=os.getenv("N8N_PASSWORD", "admin")
        )
        
        # Start services
        await orchestrator.start()
        await agentic_rag.start()
        await prompt_maker.start()
        await n8n_integration.authenticate()
        
        logging.info("AMAS Intelligence System started successfully")
        
    except Exception as e:
        logging.error(f"Failed to start AMAS Intelligence System: {e}")
        raise
    
    yield
    
    # Shutdown
    logging.info("Shutting down AMAS Intelligence System...")
    
    try:
        if orchestrator:
            await orchestrator.stop()
        if agentic_rag:
            await agentic_rag.stop()
        if prompt_maker:
            await prompt_maker.stop()
        if n8n_integration:
            await n8n_integration.disconnect()
        
        logging.info("AMAS Intelligence System shut down successfully")
        
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="AMAS Intelligence System",
    description="Advanced Multi-Agent AI System for Intelligence Operations",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token."""
    if not security_service:
        raise HTTPException(status_code=500, detail="Security service not initialized")
    
    try:
        user = await security_service.verify_token(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# Task Management Endpoints
@app.post("/api/tasks/submit", response_model=Dict[str, str])
async def submit_task(
    task_request: TaskRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Submit a new intelligence task."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        # Convert priority string to enum
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL
        }
        priority = priority_map.get(task_request.priority, TaskPriority.MEDIUM)
        
        # Submit task
        task_id = await orchestrator.submit_task(
            task_type=task_request.task_type,
            description=task_request.description,
            parameters=task_request.parameters,
            priority=priority,
            workflow_id=task_request.workflow_id
        )
        
        return {"task_id": task_id, "status": "submitted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get task status."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        task_status = await orchestrator.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskStatusResponse(**task_status)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks", response_model=List[TaskStatusResponse])
async def get_tasks(
    status: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get list of tasks."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        # This would need to be implemented in the orchestrator
        # For now, return empty list
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Agent Management Endpoints
@app.get("/api/agents", response_model=List[AgentStatusResponse])
async def get_agents(current_user: dict = Depends(get_current_user)):
    """Get list of agents."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        agents = []
        for agent_id in orchestrator.agents:
            agent_status = await orchestrator.get_agent_status(agent_id)
            if agent_status:
                agents.append(AgentStatusResponse(**agent_status))
        
        return agents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_id}", response_model=AgentStatusResponse)
async def get_agent_status(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get agent status."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        agent_status = await orchestrator.get_agent_status(agent_id)
        if not agent_status:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentStatusResponse(**agent_status)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# System Status Endpoints
@app.get("/api/status", response_model=SystemStatusResponse)
async def get_system_status(current_user: dict = Depends(get_current_user)):
    """Get system status."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        system_status = await orchestrator.get_system_status()
        return SystemStatusResponse(**system_status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Workflow Management Endpoints
@app.post("/api/workflows/execute", response_model=Dict[str, str])
async def execute_workflow(
    workflow_request: WorkflowRequest,
    current_user: dict = Depends(get_current_user)
):
    """Execute a workflow."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        execution_id = await orchestrator.execute_workflow(
            workflow_id=workflow_request.workflow_id,
            parameters=workflow_request.parameters
        )
        
        return {"execution_id": execution_id, "status": "started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflows", response_model=List[Dict[str, Any]])
async def get_workflows(current_user: dict = Depends(get_current_user)):
    """Get list of workflows."""
    if not n8n_integration:
        raise HTTPException(status_code=500, detail="n8n integration not initialized")
    
    try:
        workflows = await n8n_integration.get_workflows()
        return workflows
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Intelligence-specific Endpoints
@app.post("/api/intelligence/osint/collect")
async def collect_osint(
    sources: List[str],
    keywords: List[str],
    filters: Dict[str, Any] = None,
    current_user: dict = Depends(get_current_user)
):
    """Collect OSINT data."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        task_id = await orchestrator.submit_task(
            task_type="osint",
            description="OSINT data collection",
            parameters={
                "sources": sources,
                "keywords": keywords,
                "filters": filters or {}
            },
            priority=TaskPriority.MEDIUM
        )
        
        return {"task_id": task_id, "status": "submitted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/intelligence/investigation/analyze")
async def analyze_entities(
    entities: List[str],
    analysis_type: str = "comprehensive",
    depth: str = "medium",
    current_user: dict = Depends(get_current_user)
):
    """Analyze entities for investigation."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        task_id = await orchestrator.submit_task(
            task_type="investigation",
            description="Entity investigation",
            parameters={
                "entities": entities,
                "investigation_type": analysis_type,
                "depth": depth
            },
            priority=TaskPriority.HIGH
        )
        
        return {"task_id": task_id, "status": "submitted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/intelligence/forensics/acquire")
async def acquire_evidence(
    source: str,
    acquisition_type: str = "forensic",
    current_user: dict = Depends(get_current_user)
):
    """Acquire digital evidence."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        task_id = await orchestrator.submit_task(
            task_type="forensics",
            description="Evidence acquisition",
            parameters={
                "source": source,
                "acquisition_type": acquisition_type
            },
            priority=TaskPriority.HIGH
        )
        
        return {"task_id": task_id, "status": "submitted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Data Management Endpoints
@app.post("/api/data/store")
async def store_data(
    data: Dict[str, Any],
    data_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Store intelligence data."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        # This would need to be implemented in the orchestrator
        # For now, return success
        return {"status": "stored", "data_type": data_type}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/search")
async def search_data(
    query: str,
    data_type: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Search intelligence data."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        # This would need to be implemented in the orchestrator
        # For now, return empty results
        return {"results": [], "query": query, "limit": limit}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Metrics and Monitoring Endpoints
@app.get("/api/metrics")
async def get_metrics(current_user: dict = Depends(get_current_user)):
    """Get system metrics."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        system_status = await orchestrator.get_system_status()
        return system_status.get("metrics", {})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4
    )