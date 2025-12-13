"""
Task management API routes - INTEGRATED VERSION
This file now uses the fully integrated tasks_integrated.py
"""

# Import the integrated version
from src.api.routes.tasks_integrated import (
    TaskCreate,
    TaskExecutionResponse,
    TaskProgressResponse,
    TaskResponse,
    router,
)

# Re-export for backward compatibility
__all__ = [
    "router",
    "TaskCreate",
    "TaskResponse",
    "TaskExecutionResponse",
    "TaskProgressResponse",
]
