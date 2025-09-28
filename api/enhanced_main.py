"""
AMAS Intelligence System - Enhanced FastAPI Backend

Advanced Multi-Agent Intelligence System API with:
- JWT Authentication & Authorization
- Role-Based Access Control (RBAC)
- Comprehensive Security Headers
- Request/Response Validation
- Audit Logging
- Real-time WebSocket Support
- Health Monitoring
- Rate Limiting
"""

import asyncio
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager

import jwt
import json
from fastapi import (
    FastAPI, HTTPException, Depends, BackgroundTasks, Request,
    WebSocket, WebSocketDisconnect, status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
from passlib.context import CryptContext
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import AMAS system
from main import AMASIntelligenceSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate limiting
redis_client = redis.Redis(host='localhost', port=6379, db=1)
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379/1")

# Global AMAS instance
amas_system = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")

manager = ConnectionManager()

# Security middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

# Pydantic models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    role: str = Field(default="user")

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None

class TaskRequest(BaseModel):
    type: str = Field(..., description="Task type (osint, investigation, forensics, etc.)")
    description: str = Field(..., min_length=10, max_length=1000)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=2, ge=1, le=4)
    workflow_id: Optional[str] = None

    @validator('type')
    def validate_task_type(cls, v):
        allowed_types = ['osint', 'investigation', 'forensics', 'data_analysis', 
                        'reverse_engineering', 'metadata', 'reporting', 'technology_monitor']
        if v not in allowed_types:
            raise ValueError(f'Task type must be one of: {", ".join(allowed_types)}')
        return v

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_completion: Optional[datetime] = None

class SystemStatus(BaseModel):
    status: str
    agents: int
    active_tasks: int
    total_tasks: int
    timestamp: str
    version: str = "1.0.0"

class HealthCheck(BaseModel):
    status: str
    services: Dict[str, Any]
    timestamp: str
    uptime: str

class WorkflowRequest(BaseModel):
    workflow_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=2, ge=1, le=4)

class AuditLogEntry(BaseModel):
    id: str
    user_id: str
    event_type: str
    action: str
    details: str
    timestamp: str
    ip_address: str
    user_agent: str

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global amas_system
    try:
        logger.info("Initializing AMAS Intelligence System...")
        
        # Configuration with environment variables
        config = {
            'llm_service_url': os.getenv('AMAS_LLM_HOST', 'http://localhost:11434'),
            'vector_service_url': os.getenv('AMAS_VECTOR_HOST', 'http://localhost:8001'),
            'graph_service_url': os.getenv('AMAS_GRAPH_HOST', 'bolt://localhost:7687'),
            'postgres_host': os.getenv('AMAS_POSTGRES_HOST', 'localhost'),
            'postgres_port': int(os.getenv('AMAS_POSTGRES_PORT', '5432')),
            'postgres_user': os.getenv('AMAS_POSTGRES_USER', 'amas'),
            'postgres_password': os.getenv('AMAS_POSTGRES_PASSWORD', 'amas123'),
            'postgres_db': os.getenv('AMAS_POSTGRES_DB', 'amas'),
            'redis_host': os.getenv('AMAS_REDIS_HOST', 'localhost'),
            'redis_port': int(os.getenv('AMAS_REDIS_PORT', '6379')),
            'redis_db': int(os.getenv('AMAS_REDIS_DB', '0')),
            'neo4j_username': os.getenv('NEO4J_USERNAME', 'neo4j'),
            'neo4j_password': os.getenv('NEO4J_PASSWORD', 'amas123'),
            'neo4j_database': os.getenv('NEO4J_DATABASE', 'neo4j'),
            'jwt_secret': SECRET_KEY,
            'encryption_key': os.getenv('AMAS_ENCRYPTION_KEY', secrets.token_urlsafe(32)),
            # AI API Keys
            'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY', ''),
            'glm_api_key': os.getenv('GLM_API_KEY', ''),
            'grok_api_key': os.getenv('GROK_API_KEY', ''),
            'kimi_api_key': os.getenv('KIMI_API_KEY', ''),
            'qwen_api_key': os.getenv('QWEN_API_KEY', ''),
            'gptoss_api_key': os.getenv('GPTOSS_API_KEY', ''),
            'n8n_url': os.getenv('N8N_URL', 'http://localhost:5678'),
            'n8n_api_key': os.getenv('N8N_API_KEY', 'your_n8n_api_key_here')
        }
        
        # Initialize AMAS system
        amas_system = AMASIntelligenceSystem(config)
        await amas_system.initialize()
        
        logger.info("AMAS Intelligence System initialized successfully")
        
        # Start background tasks
        asyncio.create_task(system_monitor())
        
    except Exception as e:
        logger.error(f"Failed to initialize AMAS system: {e}")
        raise
    
    yield
    
    # Shutdown
    if amas_system:
        await amas_system.shutdown()
        logger.info("AMAS Intelligence System shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="AMAS Intelligence System API",
    description="Advanced Multi-Agent Intelligence System - Enterprise API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.amas.local"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security
security = HTTPBearer()

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        role: str = payload.get("role", "user")
        token_type: str = payload.get("type", "access")
        
        if username is None or token_type != "access":
            raise credentials_exception
            
        token_data = TokenData(username=username, user_id=user_id, role=role)
    except jwt.PyJWTError:
        raise credentials_exception
    
    return token_data

async def get_amas_system():
    global amas_system
    if amas_system is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AMAS system not initialized"
        )
    return amas_system

def require_role(required_role: str):
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Background tasks
async def system_monitor():
    """Background task to monitor system health and broadcast updates"""
    while True:
        try:
            if amas_system:
                status = await amas_system.get_system_status()
                await manager.broadcast({
                    "type": "system_status",
                    "data": status
                })
            await asyncio.sleep(30)  # Update every 30 seconds
        except Exception as e:
            logger.error(f"System monitor error: {e}")
            await asyncio.sleep(60)  # Wait longer on error

# API Endpoints

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AMAS Intelligence System API",
        "version": "1.0.0",
        "status": "operational",
        "description": "Advanced Multi-Agent Intelligence System",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "Multi-Agent Orchestration",
            "Real-time Intelligence Collection",
            "Advanced Analytics",
            "Enterprise Security",
            "WebSocket Support"
        ]
    }

@app.get("/health", response_model=HealthCheck)
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Comprehensive health check endpoint"""
    try:
        amas = await get_amas_system()
        
        # Check all services
        service_health = await amas.service_manager.health_check_all_services()
        
        return HealthCheck(
            status=service_health.get('overall_status', 'unknown'),
            services=service_health.get('services', {}),
            timestamp=datetime.utcnow().isoformat(),
            uptime=service_health.get('uptime', 'unknown')
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="unhealthy",
            services={"error": str(e)},
            timestamp=datetime.utcnow().isoformat(),
            uptime="unknown"
        )

@app.post("/auth/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, user_credentials: UserLogin, background_tasks: BackgroundTasks):
    """User authentication endpoint"""
    try:
        # Mock authentication - in production, verify against database
        if user_credentials.username == "admin" and user_credentials.password == "admin123":
            user_data = {
                "sub": user_credentials.username,
                "user_id": "admin_001",
                "role": "admin"
            }
            
            access_token = create_access_token(data=user_data)
            refresh_token = create_refresh_token(data=user_data)
            
            # Log authentication event
            background_tasks.add_task(
                log_audit_event,
                "authentication",
                user_data["user_id"],
                "login",
                "User logged in successfully",
                request.client.host if request.client else "unknown",
                request.headers.get("user-agent", "unknown")
            )
            
            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@app.get("/status", response_model=SystemStatus)
@limiter.limit("60/minute")
async def get_system_status(
    request: Request,
    current_user: TokenData = Depends(get_current_user)
):
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system status"
        )

@app.post("/tasks", response_model=TaskResponse)
@limiter.limit("20/minute")
async def submit_task(
    request: Request,
    task_request: TaskRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    """Submit a new intelligence task"""
    try:
        amas = await get_amas_system()
        
        # Submit task
        task_id = await amas.submit_intelligence_task({
            'type': task_request.type,
            'description': task_request.description,
            'parameters': task_request.parameters,
            'priority': task_request.priority,
            'workflow_id': task_request.workflow_id
        })
        
        # Log audit event
        background_tasks.add_task(
            log_audit_event,
            "task_submission",
            current_user.user_id,
            "submit_task",
            f"Task submitted: {task_request.type} - {task_request.description[:50]}",
            request.client.host if request.client else "unknown",
            request.headers.get("user-agent", "unknown")
        )
        
        # Broadcast task submission
        await manager.broadcast({
            "type": "task_submitted",
            "data": {
                "task_id": task_id,
                "type": task_request.type,
                "user": current_user.username
            }
        })
        
        return TaskResponse(
            task_id=task_id,
            status="submitted",
            message="Task submitted successfully",
            estimated_completion=datetime.utcnow() + timedelta(minutes=30)
        )
        
    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit task"
        )

@app.get("/tasks/{task_id}")
@limiter.limit("100/minute")
async def get_task_status(
    task_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get task status"""
    try:
        amas = await get_amas_system()
        
        # Get task from database
        task = await amas.database_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return {
            'task_id': task_id,
            'status': task.get('status', 'unknown'),
            'type': task.get('task_type', 'unknown'),
            'description': task.get('description', ''),
            'priority': task.get('priority', 2),
            'assigned_agent': task.get('assigned_agent', ''),
            'created_at': task.get('created_at', ''),
            'started_at': task.get('started_at', ''),
            'completed_at': task.get('completed_at', ''),
            'result': task.get('result', {}),
            'error': task.get('error', ''),
            'progress': task.get('progress', 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task status"
        )

@app.get("/agents")
@limiter.limit("60/minute")
async def get_agents(
    request: Request,
    current_user: TokenData = Depends(get_current_user)
):
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
                'metrics': agent_status.get('metrics', {}),
                'current_task': agent_status.get('current_task', ''),
                'uptime': agent_status.get('uptime', '')
            })
        
        return {'agents': agents, 'total': len(agents)}
        
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agents"
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """Enhanced WebSocket endpoint for real-time updates"""
    from api.websocket_handler import websocket_manager
    
    try:
        # Set AMAS system reference
        websocket_manager.amas_system = amas_system
        
        # Connect client with authentication
        connection_id = await websocket_manager.connect_client(websocket, token)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    await websocket_manager.handle_message(connection_id, message)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from {connection_id}: {data}")
                    await websocket_manager._send_error_to_connection(
                        connection_id, "Invalid JSON format"
                    )
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")
                    await websocket_manager._send_error_to_connection(
                        connection_id, f"Message processing error: {str(e)}"
                    )
                    
        except WebSocketDisconnect:
            await websocket_manager.disconnect_client(connection_id, "Client disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket_manager.disconnect_client(connection_id, f"Server error: {str(e)}")
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close(code=1011, reason="Server error")
        except Exception:
            pass

async def log_audit_event(
    event_type: str,
    user_id: str,
    action: str,
    details: str,
    ip_address: str,
    user_agent: str
):
    """Log audit event"""
    try:
        if amas_system and amas_system.security_service:
            await amas_system.security_service.log_audit_event(
                event_type=event_type,
                user_id=user_id,
                action=action,
                details=details,
                classification='system',
                metadata={
                    'ip_address': ip_address,
                    'user_agent': user_agent
                }
            )
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "api.enhanced_main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        access_log=True
    )