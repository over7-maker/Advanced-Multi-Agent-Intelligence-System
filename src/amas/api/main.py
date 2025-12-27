"""
FastAPI Main Application for AMAS Intelligence System
"""

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

# Import AMAS system
from ..main import AMASApplication

# Import security components
from ..security import (
    SecureAuthenticationManager,
    SecurityHeadersMiddleware,
    get_audit_logger,
    initialize_audit_logger,
)
from ..security.middleware import AuditLoggingMiddleware, AuthenticationMiddleware

try:
    from ..observability.opentelemetry_setup import setup_opentelemetry
except ImportError:
    setup_opentelemetry = None
try:
    from ..governance.agent_contracts import validate_agent_action
except ImportError:
    validate_agent_action = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AMAS Intelligence System API",
    description="Advanced Multi-Agent Intelligence System API",
    version="1.0.0",
)

# Global security components
auth_manager: Optional[SecureAuthenticationManager] = None
security_headers_middleware: Optional[SecurityHeadersMiddleware] = None

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware wrapper (will be initialized in startup)
class SecurityHeadersMiddlewareWrapper(BaseHTTPMiddleware):
    """Wrapper to add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        global security_headers_middleware
        if security_headers_middleware:
            await security_headers_middleware.add_security_headers(request, response)
        return response

app.add_middleware(SecurityHeadersMiddlewareWrapper)

# Add audit logging middleware
app.add_middleware(AuditLoggingMiddleware)

# Add authentication middleware (protects /api/v1 routes)
app.add_middleware(
    AuthenticationMiddleware,
    exclude_paths=[
        "/",
        "/health",
        "/health/ready",
        "/health/live",
        "/health/detailed",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/metrics",
        "/api/v1/landing",  # Landing page endpoints are public
    ]
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
    response_size = len(response.body) if hasattr(response, "body") else 0

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
            response_size=response_size,
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
async def verify_auth(request: Request):
    """Verify authentication using JWT middleware"""
    if auth_manager:
        try:
            user_context = await auth_manager.authenticate_request(request)
            return user_context
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"}
            )
    else:
        # Fallback if auth manager not initialized
        logger.warning("Auth manager not initialized, using mock authentication")
        return {"user_id": "admin", "role": "admin"}


# Startup event
@app.on_event("startup")
async def startup_event():
    global auth_manager, security_headers_middleware, amas_app
    
    try:
        logger.info("Initializing AMAS Intelligence System...")

        # 1. Initialize OpenTelemetry for observability
        if setup_opentelemetry:
            try:
                otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
                setup_opentelemetry(
                    service_name="amas",
                    otlp_endpoint=otlp_endpoint if otlp_endpoint != "http://localhost:4317" else None,
                    enable_console=os.getenv("OTLP_ENABLE_CONSOLE", "false").lower() == "true"
                )
                logger.info("✅ OpenTelemetry initialized")
            except Exception as e:
                logger.warning(f"OpenTelemetry initialization failed (continuing): {e}")
        else:
            logger.info("OpenTelemetry skipped (components not available).")

        # 2. Initialize Audit Logger
        try:
            audit_log_file = os.getenv("AUDIT_LOG_FILE", "logs/audit.log")
            os.makedirs(os.path.dirname(audit_log_file) if os.path.dirname(audit_log_file) else ".", exist_ok=True)
            audit_config = {
                "audit": {
                    "log_file": audit_log_file,
                    "buffer_size": int(os.getenv("AUDIT_BUFFER_SIZE", "100")),
                    "redact_sensitive": os.getenv("AUDIT_REDACT_PII", "true").lower() == "true"
                }
            }
            initialize_audit_logger(audit_config)
            logger.info("✅ Audit logger initialized")
        except Exception as e:
            logger.warning(f"Audit logger initialization failed (continuing): {e}")

        # 3. Initialize Security Components
        try:
            # Load security configuration
            import yaml
            security_config_path = os.getenv("SECURITY_CONFIG", "config/security_config.yaml")
            if os.path.exists(security_config_path):
                with open(security_config_path, 'r') as f:
                    security_config = yaml.safe_load(f)
            else:
                # Use environment variables with defaults
                security_config = {
                    "authentication": {
                        "oidc": {
                            "issuer": os.getenv("OIDC_ISSUER", "https://your-oidc-provider.com"),
                            "audience": os.getenv("OIDC_AUDIENCE", "amas-api"),
                            "jwks_uri": os.getenv("OIDC_JWKS_URI", ""),
                            "cache_ttl": int(os.getenv("OIDC_CACHE_TTL", "3600")),
                        }
                    }
                }
            
            # Initialize authentication manager
            auth_manager = SecureAuthenticationManager(security_config)
            security_headers_middleware = auth_manager.security_headers
            
            logger.info("✅ Security components initialized")
        except Exception as e:
            logger.warning(f"Security components initialization failed (continuing): {e}")

        # 4. Initialize OPA Policy Engine
        try:
            opa_url = os.getenv("OPA_URL", "http://localhost:8181")
            from ..security.policies.opa_integration import configure_policy_engine
            configure_policy_engine(opa_url=opa_url)
            logger.info(f"✅ OPA Policy Engine initialized: {opa_url}")
        except Exception as e:
            logger.warning(f"OPA Policy Engine initialization failed (continuing): {e}")

        # 5. Initialize AMAS system
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

        amas_app = AMASApplication(config)
        await amas_app.initialize()

        logger.info("✅ AMAS Intelligence System initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize AMAS system: {e}")
        raise


# Include API routes
try:
    from src.api.routes import (
        agents,
        analytics,
        auth,
        health,
        integrations,
        landing,
        metrics,  # type: ignore
        predictions,
        system,
        tasks,
        users,
        workflows,
    )

    # Authentication routes - MUST be first
    app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
    logger.info("✅ Authentication routes registered at /api/v1")
    
    # System routes
    app.include_router(system.router, prefix="/api/v1", tags=["system"])
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    # Metrics router already has prefix="/metrics", so we add /api/v1 before it
    app.include_router(metrics.router, prefix="/api/v1", tags=["monitoring"])
    logger.info("✅ System routes registered at /api/v1")
    
    # Task management routes
    app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
    app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])
    logger.info("✅ Task routes registered at /api/v1")
    
    # Agent management routes
    app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
    logger.info("✅ Agent routes registered at /api/v1")
    
    # Analytics routes
    app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
    logger.info("✅ Analytics routes registered at /api/v1")
    
    # Integration routes (router already has prefix="/integrations")
    app.include_router(integrations.router, prefix="/api/v1", tags=["integrations"])
    logger.info("✅ Integration routes registered at /api/v1/integrations")
    
    # Workflow routes
    app.include_router(workflows.router, prefix="/api/v1", tags=["workflows"])
    logger.info("✅ Workflow routes registered at /api/v1")
    
    # User management routes
    app.include_router(users.router, prefix="/api/v1", tags=["users"])
    logger.info("✅ User routes registered at /api/v1")
    
    # Landing page routes (public endpoints)
    app.include_router(landing.router, prefix="/api/v1", tags=["landing"])
    logger.info("✅ Landing page routes registered at /api/v1/landing")
    
    logger.info("✅ All API routes registered successfully")
except Exception as e:
    import traceback
    logger.error(f"Could not register some API routes: {e}")
    logger.error(traceback.format_exc())

# Include WebSocket endpoint
try:
    from fastapi import WebSocket as FastAPIWebSocket

    from src.api.websocket import websocket_endpoint
    
    @app.websocket("/ws")
    async def websocket_route(websocket: FastAPIWebSocket):
        """WebSocket endpoint for real-time updates"""
        # Extract token from query parameters
        token = websocket.query_params.get("token") if websocket.query_params else None
        await websocket_endpoint(websocket, token)
    logger.info("✅ WebSocket endpoint registered at /ws")
except Exception as e:
    logger.warning(f"Could not register WebSocket endpoint: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    global auth_manager
    
    # Shutdown audit logger
    try:
        audit_logger = get_audit_logger()
        if audit_logger:
            await audit_logger.shutdown()
            logger.info("✅ Audit logger shutdown complete")
    except Exception as e:
        logger.warning(f"Audit logger shutdown error: {e}")
    
    # Shutdown AMAS system
    if amas_app:
        await amas_app.shutdown()
        logger.info("✅ AMAS Intelligence System shutdown complete")


# Enhanced health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Get comprehensive system health status"""
    try:
        # Use enhanced health check service if available
        try:
            from src.amas.services.health_check_service import check_health

            health_result = await check_health()

            # Ensure services is a dict, not a list
            services_data = health_result.get("services", {})
            if isinstance(services_data, list):
                # Convert list to dict if needed
                services_data = {f"service_{i}": service for i, service in enumerate(services_data)}
            elif not isinstance(services_data, dict):
                services_data = {"checks": services_data} if services_data else {}

            return HealthCheck(
                status=health_result.get("status", "unknown"),
                services=services_data,
                timestamp=health_result.get("timestamp", datetime.now(timezone.utc).isoformat()),
            )
        except ImportError:
            # Fallback to basic health check
            amas = await get_amas_system()
            if hasattr(amas, 'service_manager') and amas.service_manager:
                service_health = await amas.service_manager.health_check_all_services()
                return HealthCheck(
                    status=service_health.get("overall_status", "unknown"),
                    services=service_health.get("services", {}),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
            else:
                return HealthCheck(
                    status="unknown",
                    services={"error": "Service manager not available"},
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="unhealthy",
            services={"error": str(e)},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


# Readiness probe endpoint
@app.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe endpoint"""
    try:
        from src.amas.services.health_check_service import check_health

        health_result = await check_health()

        if health_result.get("status") == "healthy":
            return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}
        else:
            return {"status": "not_ready", "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Liveness probe endpoint
@app.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe endpoint"""
    try:
        # Basic liveness check - just ensure the service is responding
        return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        logger.error(f"Liveness probe failed: {e}")
        return {
            "status": "not_alive",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


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
            },
        }

        return detailed_info
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}


# System status endpoint
@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status"""
    try:
        amas = await get_amas_system()
        
        # Try to get status from orchestrator
        status = {}
        if hasattr(amas, 'orchestrator') and amas.orchestrator:
            if hasattr(amas.orchestrator, 'get_system_status'):
                status = await amas.orchestrator.get_system_status()
            elif hasattr(amas.orchestrator, 'agents'):
                # Fallback: build status from orchestrator
                status = {
                    "status": "active",
                    "agents": len(amas.orchestrator.agents) if hasattr(amas.orchestrator, 'agents') else 0,
                    "active_tasks": len(amas.orchestrator.active_tasks) if hasattr(amas.orchestrator, 'active_tasks') else 0,
                    "total_tasks": len(amas.orchestrator.tasks) if hasattr(amas.orchestrator, 'tasks') else 0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            else:
                status = {
                    "status": "unknown",
                    "agents": 0,
                    "active_tasks": 0,
                    "total_tasks": 0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
        else:
            status = {
                "status": "initializing",
                "agents": 0,
                "active_tasks": 0,
                "total_tasks": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        return SystemStatus(
            status=status.get("status", status.get("orchestrator_status", "unknown")),
            agents=status.get("agents", status.get("active_agents", 0)),
            active_tasks=status.get("active_tasks", 0),
            total_tasks=status.get("total_tasks", 0),
            timestamp=status.get("timestamp", datetime.now(timezone.utc).isoformat()),
        )

    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Submit task endpoint
@app.post("/tasks", response_model=TaskResponse)
async def submit_task(
    task_request: TaskRequest,
    background_tasks: BackgroundTasks,
    request: Request,
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

        # Log audit event (try multiple ways)
        try:
            if hasattr(amas, 'service_manager') and amas.service_manager:
                security_service = amas.service_manager.get_security_service()
                if security_service:
                    await security_service.log_audit_event(
                        event_type="task_submission",
                        user_id=auth["user_id"],
                        action="submit_task",
                        details=f"Task submitted: {task_request.type}",
                        classification="system",
                    )
        except Exception as e:
            logger.warning(f"Failed to log audit event: {e}")

        return TaskResponse(
            task_id=task_id, status="submitted", message="Task submitted successfully"
        )

    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get task status endpoint
@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str, request: Request, auth: dict = Depends(verify_auth)):
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
async def get_agents(request: Request, auth: dict = Depends(verify_auth)):
    """Get list of agents"""
    try:
        amas = await get_amas_system()

        agents = []
        if hasattr(amas, "orchestrator") and amas.orchestrator:
            if hasattr(amas.orchestrator, 'agents'):
                for agent_id, agent in amas.orchestrator.agents.items():
                    # Try to get status from agent
                    agent_status = {}
                    if hasattr(agent, 'get_status'):
                        try:
                            agent_status = await agent.get_status()
                        except Exception:
                            pass
                    
                    # Fallback: build status from agent attributes
                    if not agent_status:
                        agent_status = {
                            "name": getattr(agent, 'name', getattr(agent, 'id', agent_id)),
                            "status": str(getattr(agent, 'status', 'unknown')),
                            "capabilities": getattr(agent, 'capabilities', []),
                            "last_activity": "",
                            "metrics": {},
                        }
                    
                    agents.append(
                        {
                            "agent_id": agent_id,
                            "name": agent_status.get("name", getattr(agent, 'name', agent_id)),
                            "status": agent_status.get("status", str(getattr(agent, 'status', 'unknown'))),
                            "capabilities": agent_status.get("capabilities", getattr(agent, 'capabilities', [])),
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
async def get_agent_status(agent_id: str, request: Request, auth: dict = Depends(verify_auth)):
    """Get specific agent status"""
    try:
        amas = await get_amas_system()

        if not hasattr(amas, "orchestrator") or not amas.orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not available")

        if not hasattr(amas.orchestrator, 'agents') or agent_id not in amas.orchestrator.agents:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = amas.orchestrator.agents[agent_id]
        
        # Try to get status from agent
        status = {}
        if hasattr(agent, 'get_status'):
            try:
                status = await agent.get_status()
            except Exception:
                pass
        
        # Fallback: build status from agent attributes
        if not status:
            status = {
                "agent_id": agent_id,
                "name": getattr(agent, 'name', getattr(agent, 'id', agent_id)),
                "status": str(getattr(agent, 'status', 'unknown')),
                "capabilities": getattr(agent, 'capabilities', []),
                "type": getattr(agent, 'type', 'unknown'),
                "metrics": {},
            }

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
    request: Request,
    auth: dict = Depends(verify_auth),
):
    """Execute a workflow"""
    try:
        amas = await get_amas_system()

        # Execute workflow
        if not hasattr(amas, 'orchestrator') or not amas.orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not available")
        
        if hasattr(amas.orchestrator, 'execute_workflow'):
            result = await amas.orchestrator.execute_workflow(workflow_id, parameters)
        else:
            raise HTTPException(status_code=501, detail="Workflow execution not supported by this orchestrator")

        # Log audit event (try multiple ways)
        try:
            if hasattr(amas, 'service_manager') and amas.service_manager:
                security_service = amas.service_manager.get_security_service()
                if security_service:
                    await security_service.log_audit_event(
                        event_type="workflow_execution",
                        user_id=auth["user_id"],
                        action="execute_workflow",
                        details=f"Workflow executed: {workflow_id}",
                        classification="system",
                    )
        except Exception as e:
            logger.warning(f"Failed to log audit event: {e}")

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
        audit_log = []
        if hasattr(amas, 'service_manager') and amas.service_manager:
            security_service = amas.service_manager.get_security_service()
            if security_service:
                # Build kwargs only for non-None values
                kwargs = {}
                if user_id is not None:
                    kwargs['user_id'] = user_id
                if event_type is not None:
                    kwargs['event_type'] = event_type
                audit_log = await security_service.get_audit_log(**kwargs)

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
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
