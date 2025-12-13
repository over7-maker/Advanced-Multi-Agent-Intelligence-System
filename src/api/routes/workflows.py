"""
Workflow management API routes
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class WorkflowCreate(BaseModel):
    """Workflow creation model"""

    template_id: Optional[str] = None
    task_template: str
    team_composition: Dict[str, Any]
    complexity: str = "moderate"
    config: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    """Workflow response model"""

    id: str
    template_id: Optional[str]
    task_template: str
    status: str
    progress: float
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response model"""

    id: str
    execution_id: str
    workflow_id: str
    status: str
    progress: float
    tasks_completed: int
    tasks_in_progress: int
    tasks_pending: int
    estimated_hours: float
    health: str
    current_phase: str
    started_at: str
    completed_at: Optional[str] = None


@router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
) -> List[WorkflowResponse]:
    """List all workflows"""
    try:
        # Mock data for now - replace with actual database query
        workflows = [
            {
                "id": "workflow_001",
                "template_id": "template_market_research",
                "task_template": "Conduct market research",
                "status": "executing",
                "progress": 75.0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "started_at": datetime.now().isoformat(),
            },
        ]

        if status:
            workflows = [w for w in workflows if w["status"] == status]

        workflows = workflows[skip : skip + limit]

        return [WorkflowResponse(**workflow) for workflow in workflows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str) -> WorkflowResponse:
    """Get a specific workflow by ID"""
    try:
        workflow = {
            "id": workflow_id,
            "template_id": "template_market_research",
            "task_template": "Conduct market research",
            "status": "executing",
            "progress": 75.0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "started_at": datetime.now().isoformat(),
        }

        return WorkflowResponse(**workflow)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow: {str(e)}")


@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(workflow: WorkflowCreate) -> WorkflowResponse:
    """Create a new workflow"""
    try:
        new_workflow = {
            "id": f"workflow_{datetime.now().timestamp()}",
            "template_id": workflow.template_id,
            "task_template": workflow.task_template,
            "status": "pending",
            "progress": 0.0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "started_at": None,
        }

        return WorkflowResponse(**new_workflow)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")


@router.get("/workflows/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_workflow_execution(execution_id: str) -> WorkflowExecutionResponse:
    """Get workflow execution details"""
    try:
        execution = {
            "id": execution_id,
            "execution_id": execution_id,
            "workflow_id": "workflow_001",
            "status": "executing",
            "progress": 75.0,
            "tasks_completed": 6,
            "tasks_in_progress": 2,
            "tasks_pending": 0,
            "estimated_hours": 0.5,
            "health": "healthy",
            "current_phase": "content_creation_and_formatting",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
        }

        return WorkflowExecutionResponse(**execution)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get workflow execution: {str(e)}"
        )


@router.get("/workflows/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
async def list_workflow_executions(workflow_id: str) -> List[WorkflowExecutionResponse]:
    """List executions for a workflow"""
    try:
        executions = [
            {
                "id": "exec_001",
                "execution_id": "exec_001",
                "workflow_id": workflow_id,
                "status": "executing",
                "progress": 75.0,
                "tasks_completed": 6,
                "tasks_in_progress": 2,
                "tasks_pending": 0,
                "estimated_hours": 0.5,
                "health": "healthy",
                "current_phase": "content_creation_and_formatting",
                "started_at": datetime.now().isoformat(),
                "completed_at": None,
            },
        ]

        return [WorkflowExecutionResponse(**exec) for exec in executions]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list workflow executions: {str(e)}"
        )

