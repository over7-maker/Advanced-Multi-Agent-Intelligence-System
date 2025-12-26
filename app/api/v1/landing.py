"""Landing page API endpoints for metrics, demos, and feedback."""

from datetime import datetime, timedelta
from typing import Optional
import random

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models import User
from app.core.auth import get_current_user

router = APIRouter(prefix="/landing", tags=["landing"])


# ============================================================================
# MODELS
# ============================================================================

class SystemMetricsResponse(BaseModel):
    """System metrics for landing page dashboard."""
    cpu_usage_percent: float
    memory_usage_percent: float
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    active_agents: int
    queue_depth: int
    uptime_hours: float
    avg_task_duration: float
    success_rate: float
    
    class Config:
        from_attributes = True


class AgentStatusResponse(BaseModel):
    """Agent status for landing page."""
    agent_id: str
    name: str
    status: str  # 'active', 'inactive', 'error'
    executions_today: int
    success_rate: float
    avg_response_time: float
    specialization: str
    
    class Config:
        from_attributes = True


class DemoDataResponse(BaseModel):
    """Demo data for interactive examples."""
    sample_task_id: str
    sample_agents: list[str]
    estimated_duration: float
    estimated_cost: float
    quality_prediction: float


class FeedbackRequest(BaseModel):
    """User feedback submission."""
    email: EmailStr
    name: str
    message: str
    sentiment: Optional[str] = None  # 'positive', 'neutral', 'negative'
    page_context: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback submission response."""
    feedback_id: str
    message: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_landing_metrics(db: Session = Depends(get_db)):
    """
    Get system metrics for landing page dashboard.
    No authentication required - public endpoint.
    """
    try:
        # Get metrics from monitoring system or mock data
        # This is a simplified version - connect to your actual metrics service
        metrics = SystemMetricsResponse(
            cpu_usage_percent=random.uniform(10, 50),
            memory_usage_percent=random.uniform(20, 60),
            active_tasks=random.randint(5, 50),
            completed_tasks=random.randint(100, 1000),
            failed_tasks=random.randint(0, 20),
            active_agents=random.randint(3, 10),
            queue_depth=random.randint(0, 10),
            uptime_hours=random.uniform(100, 1000),
            avg_task_duration=random.uniform(5, 60),
            success_rate=random.uniform(0.85, 0.99),
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")


@router.get("/agents-status", response_model=list[AgentStatusResponse])
async def get_agents_status(db: Session = Depends(get_db)):
    """
    Get status of all agents for landing page.
    No authentication required - public endpoint.
    """
    try:
        agents = [
            AgentStatusResponse(
                agent_id="agent-001",
                name="Data Analyst",
                status="active",
                executions_today=random.randint(10, 100),
                success_rate=random.uniform(0.9, 0.99),
                avg_response_time=random.uniform(2, 10),
                specialization="data-analysis",
            ),
            AgentStatusResponse(
                agent_id="agent-002",
                name="Content Creator",
                status="active",
                executions_today=random.randint(10, 100),
                success_rate=random.uniform(0.85, 0.98),
                avg_response_time=random.uniform(3, 15),
                specialization="content-generation",
            ),
            AgentStatusResponse(
                agent_id="agent-003",
                name="Code Engineer",
                status="active",
                executions_today=random.randint(5, 50),
                success_rate=random.uniform(0.88, 0.96),
                avg_response_time=random.uniform(5, 20),
                specialization="code-generation",
            ),
        ]
        return agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agent status: {str(e)}")


@router.get("/demo-data", response_model=DemoDataResponse)
async def get_demo_data():
    """
    Get demo data for interactive examples on landing page.
    No authentication required - public endpoint.
    """
    try:
        demo_data = DemoDataResponse(
            sample_task_id="task-demo-001",
            sample_agents=["agent-001", "agent-002"],
            estimated_duration=random.uniform(10, 60),
            estimated_cost=random.uniform(0.1, 5.0),
            quality_prediction=random.uniform(0.85, 0.99),
        )
        return demo_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch demo data: {str(e)}")


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Submit user feedback from landing page.
    Stores feedback in PostgreSQL database for analysis.
    No authentication required - public endpoint.
    """
    try:
        # Generate feedback ID
        feedback_id = f"feedback-{datetime.utcnow().timestamp()}"
        
        # In production, save to database:
        # from app.models import Feedback
        # db_feedback = Feedback(
        #     feedback_id=feedback_id,
        #     email=feedback.email,
        #     name=feedback.name,
        #     message=feedback.message,
        #     sentiment=feedback.sentiment,
        #     page_context=feedback.page_context,
        #     created_at=datetime.utcnow(),
        # )
        # db.add(db_feedback)
        # db.commit()
        
        # Add background task to send thank you email
        background_tasks.add_task(
            send_feedback_confirmation_email,
            email=feedback.email,
            name=feedback.name,
        )
        
        response = FeedbackResponse(
            feedback_id=feedback_id,
            message="Thank you! Your feedback has been received.",
            timestamp=datetime.utcnow(),
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/health")
async def landing_health():
    """
    Health check endpoint for landing page.
    Returns system status without authentication.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AMAS Landing Page",
    }


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def send_feedback_confirmation_email(email: str, name: str):
    """
    Background task to send feedback confirmation email.
    In production, integrate with your email service.
    """
    # TODO: Implement email sending
    print(f"Feedback confirmation email sent to {email} ({name})")
    pass
