"""
Task management API routes - FULLY INTEGRATED
Integrates orchestrator, ML predictions, agents, WebSocket, and database
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.amas.core.unified_intelligence_orchestrator import (
    UnifiedIntelligenceOrchestrator,
    get_unified_orchestrator,
)
from src.amas.intelligence.intelligence_manager import AMASIntelligenceManager
from src.amas.intelligence.predictive_engine import PredictiveIntelligenceEngine
from src.api.websocket import websocket_manager

# Metrics and tracing services
try:
    from src.amas.services.prometheus_metrics_service import get_metrics_service
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    def get_metrics_service():
        return None

try:
    from src.amas.services.tracing_service import get_tracing_service
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False
    def get_tracing_service():
        return None

# Authentication support (optional - allows unauthenticated access in dev)
try:
    from src.amas.security.enhanced_auth import (
        User,
        get_current_user,
        get_current_user_optional,
    )
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    # Fallback for development
    class User:
        def __init__(self):
            self.id = "system"
            self.username = "system"
            self.email = "system@amas.local"
            self.is_active = True
            self.roles = []
    
    async def get_current_user() -> User:
        return User()
    
    async def get_current_user_optional() -> Optional[User]:
        return User()

# In-memory cache for recently accessed tasks (cache layer, not primary storage)
# Used as a read-through cache after database persistence
# This allows fast retrieval of recently accessed tasks
_recently_accessed_tasks: Dict[str, Dict[str, Any]] = {}
_recently_accessed_tasks_timestamps: Dict[str, float] = {}
_CACHE_TTL_SECONDS = 300  # 5 minutes cache TTL

# Cleanup old cache entries periodically
async def _cleanup_old_cache():
    """Remove cache entries older than TTL"""
    import time
    current_time = time.time()
    expired_tasks = [
        task_id for task_id, timestamp in _recently_accessed_tasks_timestamps.items()
        if current_time - timestamp > _CACHE_TTL_SECONDS
    ]
    for task_id in expired_tasks:
        _recently_accessed_tasks.pop(task_id, None)
        _recently_accessed_tasks_timestamps.pop(task_id, None)

# Tracing support (optional)
try:
    from src.amas.services.tracing_service import get_tracing_service
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False


# Database dependency (optional)
async def get_db():
    """Get database session (optional)
    
    In test/development environments, returns None when the database
    is not initialized so API routes can still be exercised.
    """
    try:
        from src.database.connection import get_session
        async for session in get_session():
            return session
    except Exception as e:
        logger.debug(f"Database not available (expected in dev): {e}")
        return None

# Redis dependency (optional)
async def get_redis():
    """Get Redis client (optional)"""
    redis_client = None
    try:
        from src.cache.redis import get_redis_client
        redis_client = get_redis_client()
    except HTTPException as http_exc:
        # For HTTP exceptions (like 403), log and yield None since Redis is optional
        logger.warning(f"Redis not available (auth error): {http_exc.detail}")
        redis_client = None
    except Exception as e:
        logger.warning(f"Redis not available: {e}")
        redis_client = None
    try:
        yield redis_client
    finally:
        # Generator cleanup - ensure we always complete
        pass

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# Error Handling Utilities - Standardized Error Handling with Structured Logging
# ============================================================================

class ErrorContext:
    """Context manager for error handling with structured logging"""
    
    def __init__(self, task_id: Optional[str] = None, user_id: Optional[str] = None, 
                 operation: Optional[str] = None, **extra_context):
        self.task_id = task_id
        self.user_id = user_id
        self.operation = operation
        self.extra_context = extra_context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging"""
        context = {}
        if self.task_id:
            context["task_id"] = self.task_id
        if self.user_id:
            context["user_id"] = self.user_id
        if self.operation:
            context["operation"] = self.operation
        context.update(self.extra_context)
        return context


def _log_error_with_context(
    error: Exception,
    level: str = "error",
    task_id: Optional[str] = None,
    user_id: Optional[str] = None,
    operation: Optional[str] = None,
    **extra_context
) -> None:
    """
    Standardized error logging with context
    
    Args:
        error: Exception to log
        level: Log level (error, warning, debug, info)
        task_id: Task ID if applicable
        user_id: User ID if applicable
        operation: Operation name
        **extra_context: Additional context fields
    """
    context = ErrorContext(task_id=task_id, user_id=user_id, operation=operation, **extra_context)
    context_dict = context.to_dict()
    
    # Add exception info
    context_dict["error_type"] = type(error).__name__
    context_dict["error_message"] = str(error)
    
    # Use structured logging with context
    log_message = f"Error in {operation or 'unknown operation'}: {str(error)}"
    
    if level == "error":
        logger.error(log_message, extra=context_dict, exc_info=True)
    elif level == "warning":
        logger.warning(log_message, extra=context_dict)
    elif level == "debug":
        logger.debug(log_message, extra=context_dict)
    else:
        logger.info(log_message, extra=context_dict)


def _create_error_response(
    status_code: int,
    detail: str,
    error_code: Optional[str] = None,
    task_id: Optional[str] = None,
    **extra_fields
) -> HTTPException:
    """
    Create consistent error response
    
    Args:
        status_code: HTTP status code
        detail: Error detail message
        error_code: Optional error code for client handling
        task_id: Task ID if applicable
        **extra_fields: Additional fields to include in error response
    
    Returns:
        HTTPException with consistent format
    """
    error_data = {
        "detail": detail,
        "status_code": status_code
    }
    
    if error_code:
        error_data["error_code"] = error_code
    if task_id:
        error_data["task_id"] = task_id
    error_data.update(extra_fields)
    
    return HTTPException(status_code=status_code, detail=error_data)


def _handle_database_error(
    error: Exception,
    task_id: Optional[str] = None,
    operation: Optional[str] = None,
    user_id: Optional[str] = None
) -> HTTPException:
    """
    Handle database-specific errors with appropriate logging and response
    
    Args:
        error: Database error exception
        task_id: Task ID if applicable
        operation: Operation name
        user_id: User ID if applicable
    
    Returns:
        HTTPException with appropriate status code
    """
    error_type = type(error).__name__
    
    # Log with context
    _log_error_with_context(
        error,
        level="error",
        task_id=task_id,
        user_id=user_id,
        operation=operation or "database_operation",
        error_type=error_type
    )
    
    # Determine appropriate status code and message
    if "connection" in str(error).lower() or "timeout" in str(error).lower():
        return _create_error_response(
            status_code=503,
            detail="Database connection unavailable. Please try again later.",
            error_code="DB_CONNECTION_ERROR",
            task_id=task_id
        )
    elif "constraint" in str(error).lower() or "unique" in str(error).lower():
        return _create_error_response(
            status_code=409,
            detail="Database constraint violation. The resource may already exist.",
            error_code="DB_CONSTRAINT_ERROR",
            task_id=task_id
        )
    else:
        return _create_error_response(
            status_code=500,
            detail="Database operation failed. Please contact support if the issue persists.",
            error_code="DB_ERROR",
            task_id=task_id
        )


def _handle_orchestrator_error(
    error: Exception,
    task_id: Optional[str] = None,
    operation: Optional[str] = None,
    user_id: Optional[str] = None
) -> HTTPException:
    """
    Handle orchestrator-specific errors with appropriate logging and response
    
    Args:
        error: Orchestrator error exception
        task_id: Task ID if applicable
        operation: Operation name
        user_id: User ID if applicable
    
    Returns:
        HTTPException with appropriate status code
    """
    error_type = type(error).__name__
    
    # Log with context
    _log_error_with_context(
        error,
        level="error",
        task_id=task_id,
        user_id=user_id,
        operation=operation or "orchestrator_operation",
        error_type=error_type
    )
    
    # Determine appropriate status code and message
    if "not available" in str(error).lower() or "not initialized" in str(error).lower():
        return _create_error_response(
            status_code=503,
            detail="Orchestrator service unavailable. Please try again later.",
            error_code="ORCHESTRATOR_UNAVAILABLE",
            task_id=task_id
        )
    elif "timeout" in str(error).lower():
        return _create_error_response(
            status_code=504,
            detail="Orchestrator operation timed out. The task may still be processing.",
            error_code="ORCHESTRATOR_TIMEOUT",
            task_id=task_id
        )
    else:
        return _create_error_response(
            status_code=500,
            detail="Orchestrator operation failed. Please contact support if the issue persists.",
            error_code="ORCHESTRATOR_ERROR",
            task_id=task_id
        )

# Initialize core systems (singleton pattern)
_orchestrator: Optional[UnifiedIntelligenceOrchestrator] = None
_intelligence_manager: Optional[AMASIntelligenceManager] = None
_predictive_engine: Optional[PredictiveIntelligenceEngine] = None


def get_orchestrator_instance() -> UnifiedIntelligenceOrchestrator:
    """Get orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        try:
            _orchestrator = get_unified_orchestrator()
        except Exception as e:
            raise _handle_orchestrator_error(e, operation="get_orchestrator_instance")
    return _orchestrator


def get_intelligence_manager() -> AMASIntelligenceManager:
    """Get intelligence manager instance"""
    global _intelligence_manager
    if _intelligence_manager is None:
        try:
            _intelligence_manager = AMASIntelligenceManager()
        except Exception as e:
            _log_error_with_context(e, level="error", operation="get_intelligence_manager")
            raise _create_error_response(
                status_code=500,
                detail="Intelligence manager not available",
                error_code="INTELLIGENCE_MANAGER_UNAVAILABLE"
            )
    return _intelligence_manager


def get_predictive_engine() -> PredictiveIntelligenceEngine:
    """Get predictive engine instance"""
    global _predictive_engine
    if _predictive_engine is None:
        try:
            _predictive_engine = PredictiveIntelligenceEngine()
        except Exception as e:
            _log_error_with_context(e, level="error", operation="get_predictive_engine")
            raise _create_error_response(
                status_code=500,
                detail="Predictive engine not available",
                error_code="PREDICTIVE_ENGINE_UNAVAILABLE"
            )
    return _predictive_engine


# ============================================================================
# Helper Functions for Task Creation - Refactored from create_task()
# ============================================================================

async def _generate_task_id() -> str:
    """Generate unique task ID"""
    return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


async def _get_ml_prediction(
    task_data: 'TaskCreate',
    task_id: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get ML prediction for task
    
    Args:
        task_data: Task creation data
        task_id: Generated task ID
        user_id: User ID for logging
    
    Returns:
        Prediction dictionary with success_probability, estimated_duration, etc.
    """
    try:
        predictive_engine = get_predictive_engine()
        
        # Get initial agent suggestions (will be refined)
        initial_agents = task_data.required_capabilities or []
        
        prediction_result = await predictive_engine.predict_task_outcome(
            task_type=task_data.task_type,
            target=task_data.target,
            parameters=task_data.parameters or {},
            agents_planned=initial_agents
        )
        
        prediction = {
            "success_probability": prediction_result.success_probability,
            "estimated_duration": prediction_result.estimated_duration,
            "quality_score_prediction": prediction_result.quality_score_prediction,
            "confidence": prediction_result.confidence,
            "risk_factors": prediction_result.risk_factors,
            "optimization_suggestions": prediction_result.optimization_suggestions
        }
        
        logger.info(f"Task {task_id} prediction: "
                   f"success_prob={prediction['success_probability']:.2f}, "
                   f"duration={prediction['estimated_duration']:.1f}s",
                   extra={"task_id": task_id, "operation": "ml_prediction"})
        return prediction
    except Exception as e:
        _log_error_with_context(
            e,
            level="warning",
            task_id=task_id,
            operation="get_ml_prediction",
            user_id=user_id
        )
        # Fallback to defaults
        return {
            "success_probability": 0.75,
            "estimated_duration": 120.0,
            "confidence": 0.3
        }


async def _select_agents(
    task_data: 'TaskCreate',
    prediction: Dict[str, Any],
    task_id: str,
    user_id: Optional[str] = None
) -> List[str]:
    """
    Select optimal agents for task
    
    Args:
        task_data: Task creation data
        prediction: ML prediction results
        task_id: Task ID for logging
        user_id: User ID for logging
    
    Returns:
        List of selected agent IDs
    """
    try:
        intelligence_manager = get_intelligence_manager()
        
        # Use intelligence manager to optimize task
        optimized_task = await intelligence_manager.optimize_task_before_execution({
            "task_type": task_data.task_type,
            "target": task_data.target,
            "parameters": task_data.parameters or {},
            "required_capabilities": task_data.required_capabilities or []
        })
        
        selected_agents = optimized_task.get("optimal_agents", [])
        
        logger.info(f"Task {task_id} agents selected: {selected_agents}",
                   extra={"task_id": task_id, "operation": "agent_selection", "agents": selected_agents})
        return selected_agents
    except Exception as e:
        _log_error_with_context(
            e,
            level="warning",
            task_id=task_id,
            operation="select_agents",
            user_id=user_id
        )
        # Fallback to default agents based on task type
        return _get_default_agents_for_task_type(task_data.task_type)


async def _persist_task_to_db(
    task_id: str,
    task_data: 'TaskCreate',
    prediction: Dict[str, Any],
    user_id: str,
    db: Optional[AsyncSession]
) -> bool:
    """
    Persist task to database (primary storage)
    
    Args:
        task_id: Task ID
        task_data: Task creation data
        prediction: ML prediction results
        user_id: User ID
        db: Database session
    
    Returns:
        True if persisted successfully, False otherwise
    """
    if db is None:
        logger.debug("Database not available, using cache only (dev mode)",
                    extra={"task_id": task_id, "operation": "persist_task"})
        return True  # In dev mode without DB, allow cache-only storage
    
    try:
        await db.execute(
            text("""
            INSERT INTO tasks (task_id, title, description, task_type, target, 
            parameters, status, priority, execution_metadata, created_at, created_by) 
            VALUES (:task_id, :title, :description, :task_type, :target, 
            :parameters, :status, :priority, :execution_metadata, :created_at, :created_by)
            """),
            {
                "task_id": task_id,
                "title": task_data.title,
                "description": task_data.description,
                "task_type": task_data.task_type,
                "target": task_data.target,
                "parameters": json.dumps(task_data.parameters or {}),
                "status": "pending",
                "priority": task_data.priority or 5,
                "execution_metadata": json.dumps(prediction),
                "created_at": datetime.now(),
                "created_by": user_id
            }
        )
        await db.commit()
        logger.info(f"Task {task_id} persisted to database by user {user_id}",
                   extra={"task_id": task_id, "user_id": user_id, "operation": "persist_task"})
        return True
    except Exception as db_error:
        _log_error_with_context(
            db_error,
            level="warning",
            task_id=task_id,
            user_id=user_id,
            operation="persist_task_to_db"
        )
        await db.rollback()
        return False


async def _cache_task(
    task_id: str,
    task_data: 'TaskCreate',
    prediction: Dict[str, Any],
    selected_agents: List[str],
    redis: Optional[Any],
    user_id: Optional[str] = None
) -> None:
    """
    Cache task in memory and Redis (secondary cache layer)
    
    Args:
        task_id: Task ID
        task_data: Task creation data
        prediction: ML prediction results
        selected_agents: Selected agents
        redis: Redis client
        user_id: User ID for logging
    """
    # Cache in memory
    task_record = {
        "id": task_id,
        "task_id": task_id,
        "title": task_data.title,
        "description": task_data.description,
        "status": "pending",
        "task_type": task_data.task_type,
        "target": task_data.target,
        "priority": task_data.priority or 5,
        "created_at": datetime.now().isoformat(),
        "created_by": user_id or "system",
        "parameters": task_data.parameters or {},
        "execution_metadata": prediction,
    }
    _recently_accessed_tasks[task_id] = task_record
    _recently_accessed_tasks_timestamps[task_id] = time.time()
    logger.debug(f"Task {task_id} cached in memory (5 min TTL)",
                extra={"task_id": task_id, "operation": "cache_memory"})
    
    # Try to cache using cache services
    try:
        from src.amas.services.prediction_cache_service import (
            get_prediction_cache_service,
        )
        from src.amas.services.task_cache_service import get_task_cache_service
        
        task_cache_service = get_task_cache_service()
        prediction_cache_service = get_prediction_cache_service()
        
        task_record_cache = {
            "task_id": task_id,
            "title": task_data.title,
            "description": task_data.description,
            "task_type": task_data.task_type,
            "target": task_data.target,
            "parameters": task_data.parameters,
            "status": "pending",
            "priority": task_data.priority or 5,
            "prediction": prediction,
            "assigned_agents": selected_agents,
            "created_at": datetime.now().isoformat()
        }
        
        # Cache task using TaskCacheService
        try:
            await task_cache_service.update_task(task_id, task_record_cache)
        except Exception as cache_error:
            _log_error_with_context(
                cache_error,
                level="debug",
                task_id=task_id,
                operation="cache_task_update"
            )
        
        # Cache prediction using PredictionCacheService
        if prediction:
            try:
                await prediction_cache_service.cache_prediction(
                    {
                        "task_type": task_data.task_type,
                        "target": task_data.target,
                        "parameters": task_data.parameters or {}
                    },
                    prediction
                )
            except Exception as pred_cache_error:
                _log_error_with_context(
                    pred_cache_error,
                    level="debug",
                    task_id=task_id,
                    operation="cache_prediction"
                )
        logger.info(f"Task {task_id} cached using cache services",
                   extra={"task_id": task_id, "operation": "cache_task"})
    except ImportError:
        # Fallback to direct Redis caching if cache services not available
        try:
            if redis is not None:
                task_record_redis = {
                    "task_id": task_id,
                    "title": task_data.title,
                    "description": task_data.description,
                    "task_type": task_data.task_type,
                    "target": task_data.target,
                    "parameters": task_data.parameters,
                    "status": "pending",
                    "priority": task_data.priority or 5,
                    "prediction": prediction,
                    "assigned_agents": selected_agents,
                    "created_at": datetime.now().isoformat()
                }
                # PART_4: Task cache with 5 min TTL (300 seconds)
                await redis.setex(
                    f"task:{task_id}",
                    300,  # 5 minutes per PART_4 requirements
                    json.dumps(task_record_redis)
                )
                
                # Also cache prediction separately with 1 hour TTL (PART_4: ML predictions cache)
                await redis.setex(
                    f"prediction:{task_id}",
                    3600,  # 1 hour per PART_4 requirements
                    json.dumps(prediction)
                )
                logger.info(f"Task {task_id} cached in Redis (5 min TTL)",
                           extra={"task_id": task_id, "operation": "cache_redis"})
        except Exception as e:
            _log_error_with_context(
                e,
                level="debug",
                task_id=task_id,
                operation="cache_redis_set"
            )


async def _broadcast_task_created(
    task_id: str,
    task_data: 'TaskCreate',
    prediction: Dict[str, Any],
    selected_agents: List[str]
) -> None:
    """
    Broadcast task created event via WebSocket
    
    Args:
        task_id: Task ID
        task_data: Task creation data
        prediction: ML prediction results
        selected_agents: Selected agents
    """
    try:
        await websocket_manager.broadcast({
            "event": "task_created",
            "task_id": task_id,
            "title": task_data.title,
            "task_type": task_data.task_type,
            "prediction": prediction,
            "agents": [{"id": agent_id, "name": agent_id} for agent_id in selected_agents]
        })
    except Exception as e:
        _log_error_with_context(
            e,
            level="debug",
            task_id=task_id,
            operation="websocket_broadcast"
        )


def _schedule_auto_execution(
    task_id: str,
    task_data: 'TaskCreate',
    selected_agents: List[str],
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = None
) -> None:
    """
    Schedule auto-execution if task type requires it
    
    Args:
        task_id: Task ID
        task_data: Task creation data
        selected_agents: Selected agents
        background_tasks: Background tasks manager
        user_id: User ID for logging
    """
    # Auto-execute tasks that don't require manual approval
    auto_execute_task_types = [
        "security_scan", "intelligence_gathering", "osint_investigation",
        "performance_analysis", "monitoring", "data_analysis"
    ]
    
    if task_data.task_type in auto_execute_task_types:
        # Schedule background execution
        async def auto_execute_task():
            """Auto-execute task after creation with full event broadcasting"""
            try:
                # Wait a bit to ensure task is fully created
                await asyncio.sleep(0.5)
                
                # Broadcast task execution started
                await websocket_manager.broadcast({
                    "event": "task_execution_started",
                    "task_id": task_id,
                    "status": "executing",
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update task status in cache
                if task_id in _recently_accessed_tasks:
                    _recently_accessed_tasks[task_id]["status"] = "executing"
                    _recently_accessed_tasks_timestamps[task_id] = time.time()
                
                # Progress callback to broadcast events
                async def progress_callback(progress_data: Dict[str, Any]):
                    """Broadcast progress updates"""
                    try:
                        await websocket_manager.broadcast({
                            "event": "task_progress",
                            "task_id": task_id,
                            "progress": progress_data.get("percentage", 0),
                            "current_step": progress_data.get("current_step", ""),
                            "agent_activity": progress_data.get("agent_activity", {}),
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Broadcast agent activity events
                        agent_activity = progress_data.get("agent_activity", {})
                        for agent_id, activity in agent_activity.items():
                            if activity.get("status") == "complete":
                                await websocket_manager.broadcast({
                                    "event": "agent_completed",
                                    "task_id": task_id,
                                    "agent_id": agent_id,
                                    "agent_name": agent_id,
                                    "duration": activity.get("duration", 0),
                                    "timestamp": datetime.now().isoformat()
                                })
                    except Exception as e:
                        _log_error_with_context(
                            e,
                            level="debug",
                            task_id=task_id,
                            operation="progress_callback"
                        )
                
                # Get orchestrator and execute
                orchestrator = get_orchestrator_instance()
                
                # Broadcast agent started events
                for agent_id in selected_agents:
                    await websocket_manager.broadcast({
                        "event": "agent_started",
                        "task_id": task_id,
                        "agent_id": agent_id,
                        "agent_name": agent_id,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Execute via orchestrator with progress callback
                logger.info(f"Starting AI-powered execution for task {task_id} with agents: {selected_agents}",
                           extra={"task_id": task_id, "operation": "auto_execute_start", "agents": selected_agents})
                result = await orchestrator.execute_task(
                    task_id=task_id,
                    task_type=task_data.task_type,
                    target=task_data.target,
                    parameters=task_data.parameters or {},
                    assigned_agents=selected_agents,
                    user_context={"user_id": user_id} if user_id else {},
                    progress_callback=progress_callback
                )
                
                logger.info(f"Task {task_id} execution completed. Result: {result.get('success', False)}",
                           extra={"task_id": task_id, "operation": "auto_execute_complete", "success": result.get('success', False)})
                
                # Update task status and result in cache
                if task_id in _recently_accessed_tasks:
                    has_agent_results = (
                        result and 
                        result.get("output") and 
                        result.get("output", {}).get("agent_results")
                    )
                    
                    is_successful = result and result.get("success", False)
                    has_valuable_outputs = has_agent_results and (
                        result.get("quality_score", 0.0) > 0.0 or
                        result.get("output", {}).get("agent_results", {})
                    )
                    
                    if is_successful or has_valuable_outputs:
                        _recently_accessed_tasks[task_id]["status"] = "completed"
                        _recently_accessed_tasks[task_id]["result"] = result
                        _recently_accessed_tasks[task_id]["output"] = result.get("output", {})
                        _recently_accessed_tasks[task_id]["summary"] = result.get("summary", "") or result.get("insights", {}).get("summary", "")
                        _recently_accessed_tasks[task_id]["quality_score"] = result.get("quality_score", 0.0)
                        _recently_accessed_tasks[task_id]["execution_time"] = result.get("execution_time", 0.0)
                        _recently_accessed_tasks[task_id]["total_cost_usd"] = result.get("output", {}).get("total_cost_usd", 0.0)
                        _recently_accessed_tasks[task_id]["agent_results"] = result.get("output", {}).get("agent_results", {})
                        _recently_accessed_tasks_timestamps[task_id] = time.time()
                        logger.info(f"Task {task_id} results saved to cache: quality_score={result.get('quality_score', 0.0)}, agents={list(result.get('output', {}).get('agent_results', {}).keys())}",
                                   extra={"task_id": task_id, "operation": "auto_execute_save_results"})
                    else:
                        _recently_accessed_tasks[task_id]["status"] = "failed"
                        _recently_accessed_tasks[task_id]["error"] = result.get("error", "Execution failed") if result else "Unknown error"
                        _recently_accessed_tasks_timestamps[task_id] = time.time()
                        if result:
                            _recently_accessed_tasks[task_id]["result"] = result
                            _recently_accessed_tasks[task_id]["output"] = result.get("output", {})
                            _recently_accessed_tasks_timestamps[task_id] = time.time()
                
                # Broadcast completion
                has_agent_results = (
                    result and 
                    result.get("output") and 
                    result.get("output", {}).get("agent_results")
                )
                final_status = "completed" if (
                    (result and result.get("success", False)) or 
                    (has_agent_results and result.get("quality_score", 0.0) > 0.0)
                ) else "failed"
                
                await websocket_manager.broadcast({
                    "event": "task_completed",
                    "task_id": task_id,
                    "status": final_status,
                    "result": result,
                    "output": result.get("output", {}) if result else {},
                    "agent_results": result.get("output", {}).get("agent_results", {}) if result else {},
                    "summary": result.get("summary", "") or (result.get("insights", {}).get("summary", "") if result else ""),
                    "quality_score": result.get("quality_score", 0.0) if result else 0.0,
                    "execution_time": result.get("execution_time", 0.0) if result else 0.0,
                    "total_cost_usd": result.get("output", {}).get("total_cost_usd", 0.0) if result else 0.0,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Task {task_id} auto-executed successfully with AI agents",
                           extra={"task_id": task_id, "operation": "auto_execute_task"})
            except Exception as e:
                _log_error_with_context(
                    e,
                    level="error",
                    task_id=task_id,
                    operation="auto_execute_task"
                )
                # Update status to failed
                if task_id in _recently_accessed_tasks:
                    _recently_accessed_tasks[task_id]["status"] = "failed"
                    _recently_accessed_tasks[task_id]["error"] = str(e)
                    _recently_accessed_tasks_timestamps[task_id] = time.time()
                
                # Broadcast failure
                await websocket_manager.broadcast({
                    "event": "task_failed",
                    "task_id": task_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # Schedule auto-execution
        background_tasks.add_task(auto_execute_task)
        logger.info(f"Task {task_id} scheduled for auto-execution",
                   extra={"task_id": task_id, "operation": "schedule_auto_execution"})


# Pydantic Models
class TaskCreate(BaseModel):
    """Task creation model with full integration support"""
    title: str = Field(..., min_length=1, description="Task title (required, non-empty)")
    # Limit description size to prevent abuse and ensure security tests pass
    description: str = Field(..., max_length=10000, min_length=1, description="Task description (required, non-empty)")
    task_type: str  # security_scan, code_analysis, intelligence_gathering, etc.
    target: str  # URL, repo, system, etc.
    parameters: Optional[Dict[str, Any]] = None
    priority: Optional[int] = Field(5, ge=1, le=10)  # 1-10, default 5
    required_capabilities: Optional[List[str]] = None


class TaskResponse(BaseModel):
    """
    Task response model with prediction data and execution results
    
    Example:
        ```json
        {
            "id": "task_20250121_120000_abc12345",
            "title": "Security Scan",
            "description": "Scan example.com",
            "status": "completed",
            "task_type": "security_scan",
            "target": "example.com",
            "priority": 5,
            "prediction": {
                "success_probability": 0.85,
                "estimated_duration": 120.0
            },
            "assigned_agents": ["security_expert"],
            "created_at": "2025-01-21T12:00:00",
            "created_by": "user_123",
            "result": {
                "success": true,
                "quality_score": 0.9
            },
            "summary": "Scan completed successfully",
            "quality_score": 0.9
        }
        ```
    """
    id: str = Field(..., description="Task ID", example="task_20250121_120000_abc12345")
    title: str = Field(..., description="Task title", example="Security Scan")
    description: str = Field(..., description="Task description", example="Scan example.com for vulnerabilities")
    status: str = Field(..., description="Task status", example="pending", enum=["pending", "executing", "completed", "failed"])
    task_type: str = Field(..., description="Task type", example="security_scan")
    target: str = Field(..., description="Task target", example="example.com")
    priority: int = Field(..., description="Task priority (1-10)", example=5, ge=1, le=10)
    prediction: Optional[Dict[str, Any]] = Field(None, description="ML prediction results")
    assigned_agents: Optional[List[str]] = Field(None, description="Assigned agent IDs", example=["security_expert", "osint_001"])
    created_at: str = Field(..., description="Task creation timestamp (ISO format)", example="2025-01-21T12:00:00")
    created_by: Optional[str] = Field(None, description="User ID who created the task", example="user_123")
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution results (available after execution)")
    summary: Optional[str] = Field(None, description="Task summary (available after execution)")
    quality_score: Optional[float] = Field(None, description="Task quality score (0.0-1.0, available after execution)", ge=0.0, le=1.0)
    output: Optional[Dict[str, Any]] = Field(None, description="Task output with agent results (available after execution)")


class TaskExecutionResponse(BaseModel):
    """
    Task execution response
    
    Example:
        ```json
        {
            "task_id": "task_20250121_120000_abc12345",
            "status": "executing",
            "message": "Task execution started",
            "estimated_duration": 120.0,
            "progress_url": "/tasks/task_20250121_120000_abc12345/progress",
            "websocket_url": "ws://localhost:8000/ws"
        }
        ```
    """
    task_id: str = Field(..., description="Task ID", example="task_20250121_120000_abc12345")
    status: str = Field(..., description="Execution status", example="executing", enum=["executing", "completed", "failed"])
    message: str = Field(..., description="Status message", example="Task execution started")
    estimated_duration: Optional[float] = Field(None, description="Estimated duration in seconds", example=120.0)
    progress_url: Optional[str] = Field(None, description="URL to get task progress", example="/tasks/task_20250121_120000_abc12345/progress")
    websocket_url: Optional[str] = Field(None, description="WebSocket URL for real-time updates", example="ws://localhost:8000/ws")


class TaskListResponse(BaseModel):
    """
    Task list response with pagination
    
    Example:
        ```json
        {
            "tasks": [
                {
                    "id": "task_20250121_120000_abc12345",
                    "title": "Security Scan",
                    "status": "completed",
                    "task_type": "security_scan",
                    "created_at": "2025-01-21T12:00:00"
                }
            ],
            "total": 1
        }
        ```
    """
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks (before pagination)", example=1, ge=0)


class TaskProgressResponse(BaseModel):
    """
    Task progress response
    
    Example:
        ```json
        {
            "task_id": "task_20250121_120000_abc12345",
            "status": "executing",
            "progress": 45.5,
            "elapsed_time": 54.6,
            "estimated_remaining": 65.4
        }
        ```
    """
    task_id: str = Field(..., description="Task ID", example="task_20250121_120000_abc12345")
    status: str = Field(..., description="Task status", example="executing", enum=["pending", "executing", "completed", "failed"])
    progress: float = Field(..., description="Progress percentage (0-100)", example=45.5, ge=0.0, le=100.0)
    elapsed_time: Optional[float] = Field(None, description="Elapsed time in seconds", example=54.6, ge=0.0)
    estimated_remaining: Optional[float] = Field(None, description="Estimated remaining time in seconds", example=65.4, ge=0.0)


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user_optional if AUTH_AVAILABLE else get_current_user),
):
    """
    Create task with FULL AI orchestration integration
    
    ✅ ML predictions
    ✅ Intelligent agent selection
    ✅ Database persistence
    ✅ Real-time updates
    """
    
    # Get user ID from current_user if available
    user_id = current_user.id if current_user and hasattr(current_user, 'id') else "system"
    task_id = None
    
    # Get metrics and tracing services
    metrics_service = get_metrics_service() if METRICS_AVAILABLE else None
    tracing_service = get_tracing_service() if TRACING_AVAILABLE else None
    
    # Start tracing span for task creation
    span = None
    if tracing_service and tracing_service.enabled:
        try:
            span = tracing_service.tracer.start_as_current_span("task_creation")
            span.__enter__()
            tracing_service.set_attribute("task.type", task_data.task_type)
            tracing_service.set_attribute("user.id", user_id)
        except Exception:
            span = None
    
    creation_start_time = time.time()
    
    try:
        # STEP 1: Generate task ID
        task_id = await _generate_task_id()
        
        # STEP 2: Get ML prediction
        prediction = await _get_ml_prediction(task_data, task_id, user_id)
        
        # STEP 3: Select optimal agents
        selected_agents = await _select_agents(task_data, prediction, task_id, user_id)
        
        # STEP 4: Persist to database (primary storage)
        db_persisted = await _persist_task_to_db(task_id, task_data, prediction, user_id, db)
        
        # If database persistence failed and database is required, raise error
        if db is not None and not db_persisted:
            raise _handle_database_error(
                Exception("Task persistence failed"),
                task_id=task_id,
                operation="persist_task_to_db",
                user_id=user_id
            )
        
        # STEP 5: Cache task (memory + Redis/cache services)
        await _cache_task(task_id, task_data, prediction, selected_agents, redis, user_id)
        
        # STEP 6: Broadcast task created event
        await _broadcast_task_created(task_id, task_data, prediction, selected_agents)
        
        # STEP 7: Create task response
        task_response = TaskResponse(
            id=task_id,
            title=task_data.title,
            description=task_data.description,
            status="pending",
            task_type=task_data.task_type,
            target=task_data.target,
            priority=task_data.priority or 5,
            prediction=prediction,
            assigned_agents=selected_agents,
            created_at=datetime.now().isoformat(),
            created_by=user_id
        )
        
        # Update cache with complete task response
        _recently_accessed_tasks[task_id] = task_response.dict()
        _recently_accessed_tasks_timestamps[task_id] = time.time()
        
        # Cleanup old cache entries periodically (non-blocking)
        if len(_recently_accessed_tasks) > 1000:
            asyncio.create_task(_cleanup_old_cache())
        
        # STEP 8: Schedule auto-execution if needed
        _schedule_auto_execution(task_id, task_data, selected_agents, background_tasks, user_id)
        
        # Record task creation metrics
        creation_duration = time.time() - creation_start_time
        if metrics_service:
            metrics_service.record_task_creation(task_data.task_type, creation_duration, "success")
        
        # End tracing span
        if span:
            try:
                tracing_service.set_attribute("task.creation.success", True)
                span.__exit__(None, None, None)
            except Exception:
                pass
        
        # STEP 9: Return complete response
        return task_response
    
    except Exception as e:
        _log_error_with_context(
            e,
            level="error",
            task_id=task_id if 'task_id' in locals() else None,
            user_id=user_id if 'user_id' in locals() else (current_user.id if current_user and hasattr(current_user, 'id') else None),
            operation="create_task"
        )
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.post(
    "/tasks/{task_id}/execute",
    response_model=TaskExecutionResponse,
    summary="Execute a task",
    description="""
    Execute a task with full AI orchestration integration.
    
    This endpoint:
    - Fetches task details from database
    - Executes task via Unified Intelligence Orchestrator
    - Coordinates multiple specialized agents
    - Uses AI provider fallback chain (16 providers)
    - Broadcasts real-time progress updates via WebSocket
    - Persists execution results to database
    - Updates learning engine with execution feedback
    
    **Authentication**: Required (JWT token) or optional in development mode
    **Rate Limit**: 5 requests/minute per user (if rate limiting enabled)
    
    **Progress Tracking**: 
    - Use WebSocket endpoint `/ws` to receive real-time progress updates
    - Progress events: `task_progress`, `agent_started`, `agent_completed`, `task_completed`
    
    **Estimated Duration**: Retrieved from task's ML prediction metadata
    """,
    responses={
        200: {
            "description": "Task execution started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "task_id": "task_20250121_120000_abc12345",
                        "status": "executing",
                        "message": "Task execution started",
                        "estimated_duration": 120.0,
                        "progress_url": "/tasks/task_20250121_120000_abc12345/progress",
                        "websocket_url": "ws://localhost:8000/ws"
                    }
                }
            }
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "detail": "Task task_123 not found",
                            "status_code": 404,
                            "error_code": "TASK_NOT_FOUND",
                            "task_id": "task_123"
                        }
                    }
                }
            }
        },
        500: {
            "description": "Task execution failed",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "detail": "Failed to execute task. Please try again or contact support.",
                            "status_code": 500,
                            "error_code": "TASK_EXECUTION_FAILED",
                            "task_id": "task_20250121_120000_abc12345"
                        }
                    }
                }
            }
        }
    },
    tags=["tasks"]
)
async def execute_task(
    task_id: str,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional if AUTH_AVAILABLE else get_current_user),
):
    
    try:
        # Get user context for execution
        user_id = current_user.id if current_user and hasattr(current_user, 'id') else "system"
        
        # STEP 1: FETCH TASK from database
        task_data = {
            "task_id": task_id,
            "task_type": "security_scan",  # Default
            "target": "example.com",  # Default
            "parameters": {},
            "status": "pending"
        }
        
        # Try to get prediction from task metadata for estimated_duration
        estimated_duration = 120.0  # Default fallback
        
        if db is not None:
            try:
                result = await db.execute(
                    text("SELECT task_id, title, description, task_type, target, parameters, status, priority, execution_metadata "
                         "FROM tasks WHERE task_id = :task_id"),
                    {"task_id": task_id}
                )
                row = result.fetchone()
                if row:
                    task_data = {
                        "task_id": row.task_id,
                        "title": row.title,
                        "description": row.description,
                        "task_type": row.task_type,
                        "target": row.target,
                        "parameters": json.loads(row.parameters) if row.parameters else {},
                        "status": row.status,
                        "priority": row.priority,
                        "execution_metadata": json.loads(row.execution_metadata) if row.execution_metadata else {}
                    }
                    # Extract estimated_duration from prediction if available
                    if task_data.get("execution_metadata") and isinstance(task_data["execution_metadata"], dict):
                        prediction = task_data["execution_metadata"].get("prediction") or task_data["execution_metadata"]
                        if isinstance(prediction, dict) and "estimated_duration" in prediction:
                            estimated_duration = prediction["estimated_duration"]
            except Exception as db_error:
                _log_error_with_context(
                    db_error,
                    level="warning",
                    task_id=task_id,
                    user_id=user_id,
                    operation="fetch_task_from_db"
                )
        
        # STEP 2: UPDATE STATUS TO EXECUTING
        try:
            if db is not None:
                try:
                    await db.execute(
                        text("UPDATE tasks SET status = :status, started_at = :started_at WHERE task_id = :task_id"),
                        {
                            "status": "executing",
                            "started_at": datetime.now(),
                            "task_id": task_id
                        }
                    )
                    await db.commit()
                except Exception as db_error:
                    _log_error_with_context(
                        db_error,
                        level="warning",
                        task_id=task_id,
                        user_id=user_id,
                        operation="update_task_status"
                    )
                    await db.rollback()
            
            # Broadcast status change
            await websocket_manager.broadcast({
                "event": "task_status_changed",
                "task_id": task_id,
                "status": "executing",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            _log_error_with_context(
                e,
                level="warning",
                task_id=task_id,
                user_id=user_id,
                operation="update_task_status"
            )
        
        # STEP 3: EXECUTE VIA ORCHESTRATOR (NEW - CRITICAL)
        async def progress_callback_fn(progress: Dict[str, Any]):
            """Progress callback for WebSocket updates"""
            try:
                await websocket_manager.broadcast({
                    "event": "task_progress",
                    "task_id": task_id,
                    "progress": progress.get("percentage", 0),
                    "current_step": progress.get("current_step", ""),
                    "agent_activity": progress.get("agent_activity", {})
                })
            except Exception as e:
                _log_error_with_context(
                    e,
                    level="debug",
                    task_id=task_id,
                    operation="progress_callback_fn"
                )
        
        async def execute_task_async():
            """Background task execution with full orchestration"""
            
            execution_start = time.time()
            
            # Add tracing if available
            tracing = None
            if TRACING_AVAILABLE:
                try:
                    tracing = get_tracing_service()
                except Exception:
                    tracing = None
            
            # Create tracing span for task execution
            if tracing and tracing.enabled:
                try:
                    span = tracing.tracer.start_as_current_span("task_execution")
                    span.__enter__()
                    tracing.set_attribute("task.id", task_id)
                    tracing.set_attribute("task.type", task_data["task_type"])
                except Exception:
                    span = None
            else:
                span = None
            
            try:
                
                orchestrator = get_orchestrator_instance()
                
                # Get assigned agents from task data
                assigned_agents = []
                if task_data.get("execution_metadata"):
                    try:
                        metadata = json.loads(task_data["execution_metadata"]) if isinstance(task_data["execution_metadata"], str) else task_data["execution_metadata"]
                        assigned_agents = metadata.get("assigned_agents", [])
                    except Exception:
                        pass
                
                if tracing:
                    tracing.set_attribute("task.assigned_agents", ",".join(assigned_agents))
                
                # Execute via orchestrator.execute_task (PART_1 requirement)
                # Build user context from current_user if available
                user_context = {}
                if current_user and hasattr(current_user, 'id'):
                    user_context = {
                        "user_id": current_user.id,
                        "username": getattr(current_user, 'username', 'unknown'),
                        "email": getattr(current_user, 'email', ''),
                        "roles": getattr(current_user, 'roles', [])
                    }
                
                result = await orchestrator.execute_task(
                    task_id=task_id,
                    task_type=task_data["task_type"],
                    target=task_data.get("target", ""),
                    parameters=task_data.get("parameters", {}),
                    assigned_agents=assigned_agents,
                    user_context=user_context,
                    progress_callback=progress_callback_fn
                )
                
                execution_duration = time.time() - execution_start
                
                # Record execution metrics
                if metrics_service:
                    metrics_service.record_task_execution(
                        task_id=task_id,
                        task_type=task_data["task_type"],
                        status=final_status,
                        duration=execution_duration,
                        success_rate=1.0 if result.get("success", False) else 0.0,
                        quality_score=result.get("quality_score", 0.0)
                    )
                    # Record execution duration percentiles
                    metrics_service.metrics.get("amas_task_execution_duration_percentiles", None)
                    if "amas_task_execution_duration_percentiles" in metrics_service.metrics:
                        metrics_service.metrics["amas_task_execution_duration_percentiles"].labels(
                            task_type=task_data["task_type"]
                        ).observe(execution_duration)
                
                if tracing_service:
                    tracing_service.set_attribute("task.duration", execution_duration)
                    tracing_service.set_attribute("task.success", True)
                
                # STEP 4: PERSIST RESULTS
                # IMPORTANT: Save results even if success=False, as long as we have agent results
                has_agent_results = (
                    result and 
                    result.get("output") and 
                    result.get("output", {}).get("agent_results")
                )
                has_valuable_outputs = has_agent_results and (
                    result.get("quality_score", 0.0) > 0.0 or
                    len(result.get("output", {}).get("agent_results", {})) > 0
                )
                
                # Determine final status: completed if success OR if we have valuable outputs
                final_status = "completed" if (
                    result.get("success", False) or has_valuable_outputs
                ) else "failed"
                
                if db is not None:
                    try:
                        await db.execute(
                            text("""
                            UPDATE tasks SET 
                            status = :status,
                            result = :result,
                            output = :output,
                            summary = :summary,
                            completed_at = :completed_at,
                            duration_seconds = :duration_seconds,
                            success_rate = :success_rate,
                            quality_score = :quality_score
                            WHERE task_id = :task_id
                            """),
                            {
                                "status": final_status,
                                "result": json.dumps(result),  # Full result object
                                "output": json.dumps(result.get("output", {})),  # Agent results
                                "summary": result.get("summary", "") or result.get("insights", {}).get("summary", ""),
                                "completed_at": datetime.now(),
                                "duration_seconds": execution_duration,
                                "success_rate": result.get("success_rate", 0.0),
                                "quality_score": result.get("quality_score", 0.0),
                                "task_id": task_id
                            }
                        )
                        await db.commit()
                        logger.info(f"Task {task_id} results persisted to database: status={final_status}, quality={result.get('quality_score', 0.0)}",
                                   extra={"task_id": task_id, "operation": "persist_results", "status": final_status, "quality_score": result.get('quality_score', 0.0)})
                    except Exception as db_error:
                        _log_error_with_context(
                            db_error,
                            level="warning",
                            task_id=task_id,
                            user_id=user_id,
                            operation="persist_results_db"
                        )
                        await db.rollback()
                
                # Also update cache
                if task_id in _recently_accessed_tasks:
                    _recently_accessed_tasks[task_id]["status"] = final_status
                    _recently_accessed_tasks[task_id]["result"] = result
                    _recently_accessed_tasks[task_id]["output"] = result.get("output", {})
                    _recently_accessed_tasks[task_id]["summary"] = result.get("summary", "") or result.get("insights", {}).get("summary", "")
                    _recently_accessed_tasks[task_id]["quality_score"] = result.get("quality_score", 0.0)
                    _recently_accessed_tasks[task_id]["execution_time"] = execution_duration
                    _recently_accessed_tasks[task_id]["agent_results"] = result.get("output", {}).get("agent_results", {})
                    _recently_accessed_tasks_timestamps[task_id] = time.time()
                    logger.info(f"Task {task_id} results updated in cache: agents={list(result.get('output', {}).get('agent_results', {}).keys())}",
                               extra={"task_id": task_id, "operation": "update_cache", "agents": list(result.get('output', {}).get('agent_results', {}).keys())})
                
                # STEP 5: UPDATE LEARNING ENGINE (NEW - CRITICAL)
                try:
                    intelligence_manager = get_intelligence_manager()
                    await intelligence_manager.record_task_execution(
                        task_id=task_id,
                        task_type=task_data["task_type"],
                        agents_used=result.get("agents_used", []),
                        execution_time=execution_duration,
                        success=result.get("success", False),
                        quality_score=result.get("quality_score", 0.0),
                        user_feedback=None  # Will be added later
                    )
                    
                    # Trigger model retraining if threshold reached
                    task_count = await intelligence_manager.get_completed_task_count()
                    if task_count % 20 == 0:
                        logger.info(f"Triggering model retraining (completed tasks: {task_count})",
                                   extra={"task_id": task_id, "operation": "trigger_retraining", "task_count": task_count})
                        predictive_engine = get_predictive_engine()
                        background_tasks.add_task(predictive_engine._retrain_model, "task_outcome")
                except Exception as e:
                    _log_error_with_context(
                        e,
                        level="warning",
                        task_id=task_id,
                        user_id=user_id,
                        operation="learning_engine_update"
                    )
                
                # STEP 6: BROADCAST COMPLETION with full results
                has_agent_results = (
                    result and 
                    result.get("output") and 
                    result.get("output", {}).get("agent_results")
                )
                final_status = "completed" if (
                    result.get("success", False) or 
                    (has_agent_results and result.get("quality_score", 0.0) > 0.0)
                ) else "failed"
                
                await websocket_manager.broadcast({
                    "event": "task_completed",
                    "task_id": task_id,
                    "status": final_status,
                    "duration": execution_duration,
                    "success": result.get("success", False),
                    "quality_score": result.get("quality_score", 0.0),
                    "result": result,  # Full result with agent_results
                    "output": result.get("output", {}),
                    "agent_results": result.get("output", {}).get("agent_results", {}),
                    "result_summary": result.get("summary", "") or result.get("insights", {}).get("summary", ""),
                    "execution_time": execution_duration,
                    "total_cost_usd": result.get("output", {}).get("total_cost_usd", 0.0)
                })
                
                logger.info(f"Task {task_id} completed successfully in {execution_duration:.1f}s")
                
            except Exception as e:
                _log_error_with_context(
                    e,
                    level="error",
                    task_id=task_id,
                    user_id=user_id,
                    operation="execute_task_async"
                )
                
                if tracing:
                    tracing.record_exception(e)
                    tracing.set_attribute("task.success", False)
                
                # Update task status to failed
                if db is not None:
                    try:
                        await db.execute(
                            text("""
                            UPDATE tasks SET 
                            status = :status,
                            error_details = :error_details,
                            completed_at = :completed_at
                            WHERE task_id = :task_id
                            """),
                            {
                                "status": "failed",
                                "error_details": json.dumps({"error": str(e)}),
                                "completed_at": datetime.now(),
                                "task_id": task_id
                            }
                        )
                        await db.commit()
                    except Exception as db_error:
                        logger.warning(f"Database update failed: {db_error}")
                        await db.rollback()
                
                # Broadcast failure
                await websocket_manager.broadcast({
                    "event": "task_failed",
                    "task_id": task_id,
                    "error": str(e)
                })
        
        # Schedule background execution
        background_tasks.add_task(execute_task_async)
        
        # Return immediate response
        return TaskExecutionResponse(
            task_id=task_id,
            status="executing",
            message="Task execution started",
            estimated_duration=estimated_duration,
            progress_url=f"/api/v1/tasks/{task_id}/progress",
            websocket_url=f"ws://localhost:8000/ws?task_id={task_id}"
        )
    
    except Exception as e:
        logger.error(f"Task execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to execute task: {str(e)}")


@router.get(
    "/tasks",
    response_model=TaskListResponse,
    summary="List all tasks",
    description="""
    List all tasks with optional filtering and pagination.
    
    This endpoint:
    - Fetches tasks from database (primary source)
    - Falls back to Redis cache if database unavailable
    - Supports filtering by status and task_type
    - Supports pagination with skip and limit
    - Returns tasks sorted by created_at (newest first)
    
    **Authentication**: Required (JWT token) or optional in development mode
    **Rate Limit**: 30 requests/minute per user (if rate limiting enabled)
    
    **Query Parameters**:
    - `skip` (offset): Number of tasks to skip (default: 0)
    - `limit`: Maximum number of tasks to return (default: 100, max: 1000)
    - `status`: Filter by task status (pending, executing, completed, failed)
    - `task_type`: Filter by task type (security_scan, code_analysis, etc.)
    
    **Performance**: Optimized with database indexes for fast queries
    """,
    responses={
        200: {
            "description": "Tasks retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "tasks": [
                            {
                                "id": "task_20250121_120000_abc12345",
                                "title": "Security Scan",
                                "description": "Scan example.com",
                                "status": "completed",
                                "task_type": "security_scan",
                                "target": "example.com",
                                "priority": 5,
                                "created_at": "2025-01-21T12:00:00",
                                "created_by": "user_123"
                            }
                        ],
                        "total": 1
                    }
                }
            }
        },
        500: {
            "description": "Failed to list tasks",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "detail": "Failed to list tasks. Please try again or contact support.",
                            "status_code": 500,
                            "error_code": "LIST_TASKS_FAILED"
                        }
                    }
                }
            }
        }
    },
    tags=["tasks"]
)
async def list_tasks(
    skip: int = Query(0, ge=0, alias="offset", description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks to return"),
    status: Optional[str] = Query(None, description="Filter by task status (pending, executing, completed, failed)"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user_optional if AUTH_AVAILABLE else get_current_user),
):
    # Get metrics service
    metrics_service = get_metrics_service() if METRICS_AVAILABLE else None
    list_start_time = time.time()
    
    try:
        all_tasks = []
        
        # 1. Get tasks from database (primary source) - Optimized with indexes
        if db is not None:
            try:
                db_query_start = time.time()
                # Optimized query using composite indexes:
                # - ix_tasks_status_created_at for status + created_at queries
                # - ix_tasks_task_type_status for task_type + status queries
                # - ix_tasks_created_by_created_at for user-specific queries
                if status and task_type:
                    # Use composite index (task_type, status) + created_at
                    query = """
                    SELECT id, task_id, title, description, task_type, target, status, priority, created_at, created_by 
                    FROM tasks 
                    WHERE task_type = :task_type AND status = :status
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                    params = {
                        "task_type": task_type,
                        "status": status,
                        "limit": limit,
                        "offset": skip
                    }
                elif status:
                    # Use composite index (status, created_at)
                    query = """
                    SELECT id, task_id, title, description, task_type, target, status, priority, created_at, created_by 
                    FROM tasks 
                    WHERE status = :status
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                    params = {
                        "status": status,
                        "limit": limit,
                        "offset": skip
                    }
                elif task_type:
                    # Use index on task_type
                    query = """
                    SELECT id, task_id, title, description, task_type, target, status, priority, created_at, created_by 
                    FROM tasks 
                    WHERE task_type = :task_type
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                    params = {
                        "task_type": task_type,
                        "limit": limit,
                        "offset": skip
                    }
                else:
                    # No filters - use created_at index
                    query = """
                    SELECT id, task_id, title, description, task_type, target, status, priority, created_at, created_by 
                    FROM tasks 
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                    params = {
                        "limit": limit,
                        "offset": skip
                    }
                
                result = await db.execute(text(query), params)
                db_query_duration = time.time() - db_query_start
                
                # Record database query time
                if metrics_service:
                    metrics_service.record_db_query("select", "tasks", "success", db_query_duration)
                rows = result.fetchall()
                
                for row in rows:
                    task_id = row.id or row.task_id
                    # Add task from database (database is primary source)
                    all_tasks.append({
                            "id": task_id,
                            "title": row.title or "",
                            "description": row.description or "",
                            "status": row.status or "pending",
                            "task_type": row.task_type or "unknown",
                            "target": row.target or "",
                            "priority": row.priority or 5,
                            "created_at": row.created_at.isoformat() if hasattr(row.created_at, 'isoformat') else str(row.created_at),
                            "created_by": row.created_by
                        })
            except Exception as db_error:
                _log_error_with_context(
                    db_error,
                    level="debug",
                    operation="list_tasks_db_query",
                    user_id=current_user.id if current_user and hasattr(current_user, 'id') else None
                )
        
        # 3. Get tasks from Redis cache (if available)
        if redis is not None:
            try:
                # Get all task keys from Redis
                task_keys = await redis.keys("task:*")
                for key in task_keys:
                    task_id = key.decode().replace("task:", "") if isinstance(key, bytes) else key.replace("task:", "")
                    # Skip if already in our list
                    if not any(t.get("id") == task_id or t.get("task_id") == task_id for t in all_tasks):
                        cached_task = await redis.get(key)
                        if cached_task:
                            try:
                                task_data = json.loads(cached_task)
                                # Convert to TaskResponse format
                                all_tasks.append({
                                    "id": task_data.get("task_id", task_id),
                                    "title": task_data.get("title", ""),
                                    "description": task_data.get("description", ""),
                                    "status": task_data.get("status", "pending"),
                                    "task_type": task_data.get("task_type", "unknown"),
                                    "target": task_data.get("target", ""),
                                    "priority": task_data.get("priority", 5),
                                    "created_at": task_data.get("created_at", datetime.now().isoformat()),
                                    "prediction": task_data.get("prediction"),
                                    "assigned_agents": task_data.get("assigned_agents", [])
                                })
                            except Exception:
                                pass
            except Exception as cache_error:
                _log_error_with_context(
                    cache_error,
                    level="debug",
                    operation="list_tasks_cache_query",
                    user_id=current_user.id if current_user and hasattr(current_user, 'id') else None
                )
        
        # Remove duplicates (by task_id) - only needed if we have data from multiple sources
        seen_ids = set()
        unique_tasks = []
        for task in all_tasks:
            task_id = task.get("id") or task.get("task_id")
            if task_id and task_id not in seen_ids:
                seen_ids.add(task_id)
                unique_tasks.append(task)
        
        # If we got data from database with pagination, tasks are already paginated
        # Otherwise, apply pagination here
        if db is not None and (status or task_type):
            # Already paginated by database query
            paginated_tasks = unique_tasks
            total = total_count if 'total_count' in locals() else len(unique_tasks)
        else:
            # Apply filters (if not already filtered by DB query)
            if not status and not task_type:
                filtered_tasks = unique_tasks
            else:
                filtered_tasks = unique_tasks
                if status:
                    filtered_tasks = [t for t in filtered_tasks if t.get("status") == status]
                if task_type:
                    filtered_tasks = [t for t in filtered_tasks if t.get("task_type") == task_type]
            
            # Sort by created_at (newest first) - only if not already sorted by DB
            if db is None:
                filtered_tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
            else:
                filtered_tasks = unique_tasks
            
            # Get total count before pagination
            total = len(filtered_tasks)
            
            # Apply pagination
            paginated_tasks = filtered_tasks[skip : skip + limit]
        
        # Convert to TaskResponse format
        task_responses = []
        for task in paginated_tasks:
            try:
                task_responses.append(TaskResponse(
                    id=task.get("id") or task.get("task_id", ""),
                    title=task.get("title", ""),
                    description=task.get("description", ""),
                    status=task.get("status", "pending"),
                    task_type=task.get("task_type", "unknown"),
                    target=task.get("target", ""),
                    priority=task.get("priority", 5),
                    created_at=task.get("created_at", datetime.now().isoformat()),
                    created_by=task.get("created_by"),
                    prediction=task.get("prediction"),
                    assigned_agents=task.get("assigned_agents", [])
                ))
            except Exception as e:
                _log_error_with_context(
                    e,
                    level="debug",
                    operation="convert_task_to_response"
                )
                continue
        
        # Record list tasks metrics
        list_duration = time.time() - list_start_time
        if metrics_service:
            # Record cache hits/misses
            if redis is not None:
                metrics_service.record_cache_hit("redis")
            else:
                metrics_service.record_cache_miss("redis")
        
        return TaskListResponse(
            tasks=task_responses,
            total=total
        )
    
    except Exception as e:
        _log_error_with_context(
            e,
            level="error",
            operation="list_tasks",
            user_id=current_user.id if current_user and hasattr(current_user, 'id') else None
        )
        raise _create_error_response(
            status_code=500,
            detail="Failed to list tasks. Please try again or contact support.",
            error_code="LIST_TASKS_FAILED"
        )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get a specific task by ID",
    description="""
    Get detailed information about a specific task by its ID.
    
    This endpoint:
    - Checks memory cache first (for recently accessed tasks)
    - Falls back to Redis cache
    - Falls back to database
    - Falls back to orchestrator (if task was just created)
    
    **Authentication**: Required (JWT token) or optional in development mode
    **Rate Limit**: 60 requests/minute per user (if rate limiting enabled)
    
    **Response includes**:
    - Task metadata (title, description, status, type, target)
    - ML prediction results (if available)
    - Assigned agents
    - Execution results (if task completed)
    - Quality score and execution metrics
    """,
    responses={
        200: {
            "description": "Task retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "task_20250121_120000_abc12345",
                        "title": "Security Scan",
                        "description": "Scan example.com for vulnerabilities",
                        "status": "completed",
                        "task_type": "security_scan",
                        "target": "example.com",
                        "priority": 5,
                        "prediction": {
                            "success_probability": 0.85,
                            "estimated_duration": 120.0
                        },
                        "assigned_agents": ["security_expert", "osint_001"],
                        "result": {
                            "success": True,
                            "output": {
                                "agent_results": {
                                    "security_expert": {
                                        "status": "complete",
                                        "findings": []
                                    }
                                }
                            },
                            "quality_score": 0.9
                        },
                        "created_at": "2025-01-21T12:00:00",
                        "created_by": "user_123"
                    }
                }
            }
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "detail": "Task task_123 not found",
                            "status_code": 404,
                            "error_code": "TASK_NOT_FOUND",
                            "task_id": "task_123"
                        }
                    }
                }
            }
        },
        500: {
            "description": "Failed to get task",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "detail": "Failed to get task. Please try again or contact support.",
                            "status_code": 500,
                            "error_code": "GET_TASK_FAILED",
                            "task_id": "task_20250121_120000_abc12345"
                        }
                    }
                }
            }
        }
    },
    tags=["tasks"]
)
async def get_task(
    task_id: str = Path(..., description="Task ID to retrieve"),
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user_optional if AUTH_AVAILABLE else get_current_user),
):
    # Get metrics service
    metrics_service = get_metrics_service() if METRICS_AVAILABLE else None
    get_start_time = time.time()
    
    try:
        # Try cache first (for recently accessed tasks)
        if task_id in _recently_accessed_tasks:
            # Record cache hit
            if metrics_service:
                metrics_service.record_cache_hit("memory")
            logger.debug(f"Task {task_id} found in cache")
            task_data = _recently_accessed_tasks[task_id]
            # Update cache timestamp (LRU behavior)
            _recently_accessed_tasks_timestamps[task_id] = time.time()
            # Ensure result is included if available
            task_dict = dict(task_data)
            # Create TaskResponse with all available data including results
            return TaskResponse(
                id=task_dict.get("id") or task_dict.get("task_id", task_id),
                title=task_dict.get("title", ""),
                description=task_dict.get("description", ""),
                status=task_dict.get("status", "pending"),
                task_type=task_dict.get("task_type", "unknown"),
                target=task_dict.get("target", ""),
                priority=task_dict.get("priority", 5),
                created_at=task_dict.get("created_at", datetime.now().isoformat()),
                created_by=task_dict.get("created_by"),
                prediction=task_dict.get("prediction"),
                assigned_agents=task_dict.get("assigned_agents", []),
                result=task_dict.get("result"),  # Include execution results
                summary=task_dict.get("summary"),
                quality_score=task_dict.get("quality_score"),
                output=task_dict.get("output")
            )
        
        # Try cache second
        if redis is not None:
            try:
                from src.amas.services.task_cache_service import get_task_cache_service
                task_cache_service = get_task_cache_service()
                cached_task = await task_cache_service.get_task(task_id)
                if cached_task:
                    # Record cache hit
                    if metrics_service:
                        metrics_service.record_cache_hit("redis")
                    return TaskResponse(**cached_task)
                else:
                    # Record cache miss
                    if metrics_service:
                        metrics_service.record_cache_miss("redis")
            except Exception as cache_error:
                logger.debug(f"Cache fetch failed (non-critical): {cache_error}")
                pass
        
        # Try database
        if db is not None:
            try:
                db_query_start = time.time()
                result = await db.execute(
                    text("SELECT id, task_id, title, description, task_type, target, status, priority, created_at, created_by, "
                         "result, execution_metadata, quality_score "
                         "FROM tasks WHERE id = :task_id OR task_id = :task_id"),
                    {"task_id": task_id}
                )
                db_query_duration = time.time() - db_query_start
                
                # Record database query time
                if metrics_service:
                    metrics_service.record_db_query("select", "tasks", "success", db_query_duration)
                row = result.fetchone()
                if row:
                    # Parse result if it's JSON string
                    task_result = None
                    if row.result:
                        try:
                            task_result = json.loads(row.result) if isinstance(row.result, str) else row.result
                        except Exception:
                            pass
                    
                    # Parse execution_metadata for additional info (can be used for prediction data)
                    # execution_metadata = None
                    # if row.execution_metadata:
                    #     try:
                    #         execution_metadata = json.loads(row.execution_metadata) if isinstance(row.execution_metadata, str) else row.execution_metadata
                    #     except Exception:
                    #         pass
                    
                    return TaskResponse(
                        id=row.id or row.task_id or task_id,
                        title=row.title,
                        description=row.description or "",
                        status=row.status,
                        task_type=row.task_type,
                        target=row.target,
                        priority=row.priority,
                        created_at=row.created_at.isoformat() if hasattr(row.created_at, 'isoformat') else str(row.created_at),
                        created_by=row.created_by,
                        result=task_result,  # Include parsed result
                        quality_score=row.quality_score if hasattr(row, 'quality_score') else None
                    )
            except Exception as db_error:
                logger.debug(f"Database fetch failed: {db_error}")
        
        # Try to get from orchestrator or cache (if task was just created)
        try:
            # Check if task was recently created (might be in memory/cache)
            from src.amas.core.unified_intelligence_orchestrator import (
                get_unified_orchestrator,
            )
            orchestrator = get_unified_orchestrator()
            # Try to get task status from orchestrator
            task_status = await orchestrator.get_task_status(task_id)
            if task_status:
                # Return a basic task response from orchestrator data
                # Map orchestrator task fields to TaskResponse
                return TaskResponse(
                    id=task_id,
                    title=task_status.get("description", "Task") or "Task",
                    description=task_status.get("description", "") or "",
                    status=task_status.get("status", "pending"),
                    task_type=task_status.get("type", "unknown"),
                    target=task_status.get("parameters", {}).get("target", "") if isinstance(task_status.get("parameters"), dict) else "",
                    priority=task_status.get("priority", 5) if isinstance(task_status.get("priority"), int) else 5,
                    created_at=task_status.get("created_at", datetime.now().isoformat()),
                    created_by=None
                )
        except Exception as orch_error:
            logger.debug(f"Orchestrator fetch failed: {orch_error}")
        
        # Fallback: Return 404 if task not found anywhere
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    except HTTPException:
        raise
    except Exception as e:
        _log_error_with_context(
            e,
            level="error",
            task_id=task_id if 'task_id' in locals() else None,
            operation="get_task"
        )
        raise _create_error_response(
            status_code=500,
            detail="Failed to get task. Please try again or contact support.",
            error_code="GET_TASK_FAILED",
            task_id=task_id if 'task_id' in locals() else None
        )


@router.get("/tasks/{task_id}/progress", response_model=TaskProgressResponse)
async def get_task_progress(
    task_id: str,
    redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time task progress"""
    
    # Try cache first (faster) - PART_4: Task cache with 5 min TTL
    try:
        if redis is not None:
            cached_progress = await redis.get(f"task:progress:{task_id}")
            if cached_progress:
                return TaskProgressResponse(**json.loads(cached_progress))
    except Exception:
        pass
    
    # Fetch from database or orchestrator
    try:
        # Try orchestrator first
        try:
            orchestrator = get_orchestrator_instance()
            task_status = await orchestrator.get_task_status(task_id)
            if task_status:
                # Calculate progress based on status
                if task_status["status"] == "completed":
                    progress = 100.0
                elif task_status["status"] == "in_progress":
                    progress = 50.0  # Estimate
                else:
                    progress = 0.0
                
                return TaskProgressResponse(
                    task_id=task_id,
                    status=task_status["status"],
                    progress=progress,
                    elapsed_time=None,
                    estimated_remaining=None
                )
        except Exception:
            pass
        
        # Fallback to database
        if db is not None:
            try:
                result = await db.execute(
                    text("SELECT status, started_at, completed_at, duration_seconds "
                         "FROM tasks WHERE task_id = :task_id"),
                    {"task_id": task_id}
                )
                row = result.fetchone()
                if row:
                    if row.status == "completed":
                        progress = 100.0
                    elif row.status == "executing" and row.started_at:
                        elapsed = (datetime.now() - row.started_at).total_seconds()
                        estimated_total = 120.0  # Default estimate
                        progress = min(95.0, (elapsed / estimated_total) * 100)
                    else:
                        progress = 0.0
                    
                    return TaskProgressResponse(
                        task_id=task_id,
                        status=row.status,
                        progress=progress,
                        elapsed_time=row.duration_seconds,
                        estimated_remaining=None
                    )
            except Exception as db_error:
                logger.warning(f"Database fetch failed: {db_error}")
        
        # Default response
        return TaskProgressResponse(
            task_id=task_id,
            status="unknown",
            progress=0.0,
            elapsed_time=None,
            estimated_remaining=None
        )
    except Exception as e:
        _log_error_with_context(
            e,
            level="error",
            task_id=task_id if 'task_id' in locals() else None,
            operation="get_task_progress"
        )
        raise HTTPException(status_code=500, detail="Failed to fetch progress")


def _get_default_agents_for_task_type(task_type: str) -> List[str]:
    """Get default agents for task type"""
    agent_mapping = {
        "security_scan": ["security_expert", "osint_001"],
        "code_analysis": ["code_analysis"],
        "intelligence_gathering": ["osint_001"],
        "forensics": ["forensics_001"],
        "performance_analysis": ["performance_monitor"],
    }
    return agent_mapping.get(task_type, [])

