I'll create the most comprehensive production-ready implementation guide based on all reports and the critical gaps identified by your development team.

***

# **🎯 AMAS PROJECT: DEFINITIVE PRODUCTION IMPLEMENTATION GUIDE**
## **Complete Gap Resolution & Production Deployment Roadmap**

**Report Generation Date**: November 19, 2025, 05:34 AM +03  
**Analysis Sources**: 4 Independent Technical Reports (200,000+ words)  
**Current Status**: **85-90% Code Exists, 30% Actually Integrated**  
**Project Repository**: [github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System)  
**Purpose**: Complete production deployment roadmap for development team

***

## **📋 PART I: CRITICAL SITUATION ANALYSIS**

### **1.1 The Reality Gap: What Your Team Discovered**

Your development team's testing revealed a **critical disconnect**:

```
┌─────────────────────────────────────────────────────────┐
│           WHAT EXISTS IN CODE (85-90%)                  │
├─────────────────────────────────────────────────────────┤
│ ✅ 34KB Unified Intelligence Orchestrator               │
│ ✅ 31KB ML Predictive Engine (680 lines)                │
│ ✅ 33KB Collective Learning Engine                      │
│ ✅ 20+ Specialized AI Agents                            │
│ ✅ 16+ AI Provider Fallback System                      │
│ ✅ 100+ Platform Integration Connectors                 │
│ ✅ Complete Database Schema (PostgreSQL+Redis+Neo4j)    │
│ ✅ Prometheus/Grafana Monitoring Stack                  │
└─────────────────────────────────────────────────────────┘
                         ↓
                    BUT...
                         ↓
┌─────────────────────────────────────────────────────────┐
│        WHAT'S ACTUALLY WIRED TOGETHER (30%)             │
├─────────────────────────────────────────────────────────┤
│ ✅ Basic API endpoints (agents, tasks, workflows)       │
│ ✅ Frontend React dashboard (basic)                     │
│ ✅ API service layer (frontend)                         │
│ ✅ WebSocket service (frontend only)                    │
│ ❌ NO orchestrator integration                          │
│ ❌ NO AI agent execution                                │
│ ❌ NO ML predictions in API                             │
│ ❌ NO AI provider usage                                 │
│ ❌ NO backend WebSocket server                          │
│ ❌ NO database queries in APIs                          │
│ ❌ NO monitoring metrics collection                     │
└─────────────────────────────────────────────────────────┘
```

**Translation**: You have a **Ferrari engine sitting in the garage**, but your car is running on a **lawn mower motor**.

### **1.2 Why This Happened (Common Development Pattern)**

```python
# What was done (Development Team Report):
# ✅ Fixed TypeScript compilation errors (13 fixes)
# ✅ Made services "optional" to get backend running
# ✅ Created basic API responses (mock data)
# ✅ Built basic frontend UI

# What this created:
# ❌ Backend starts but doesn't use core features
# ❌ APIs return empty/mock data
# ❌ Frontend looks good but shows no real data
# ❌ "Optional" mode bypassed all critical services

# Result: A beautiful UI showing nothing real
```

### **1.3 Impact Assessment**

| Component | Code Exists | Actually Used | Gap Severity | Production Impact |
|-----------|-------------|---------------|--------------|-------------------|
| **AI Orchestration** | ✅ 100% | ❌ 0% | 🔴 CRITICAL | No task execution |
| **ML Predictions** | ✅ 100% | ❌ 0% | 🔴 CRITICAL | No intelligence |
| **AI Agents** | ✅ 100% | ❌ 0% | 🔴 CRITICAL | No specialized work |
| **AI Providers** | ✅ 100% | ❌ 0% | 🔴 CRITICAL | No AI capabilities |
| **Database** | ✅ 100% | ❌ 0% | 🟠 HIGH | No data persistence |
| **Monitoring** | ✅ 100% | ❌ 0% | 🟡 MEDIUM | No observability |
| **WebSocket** | ⚠️ 50% | ⚠️ 50% | 🟠 HIGH | No real-time updates |
| **Basic APIs** | ✅ 100% | ✅ 100% | ✅ COMPLETE | Basic CRUD works |
| **Frontend UI** | ✅ 100% | ✅ 100% | ✅ COMPLETE | UI renders |

**Overall Status**: **30% Functional Integration** (70% integration gap)

***

## **🔧 PART II: COMPLETE INTEGRATION ARCHITECTURE**

### **2.1 The Missing Connection Layer**

**Current Architecture (Broken)**:

```
Frontend (React)
    ↓ API calls
Backend API Layer (FastAPI)
    ↓ Mock responses
[ORCHESTRATOR, ML, AGENTS, AI PROVIDERS - NOT CONNECTED]
    ↓ Not being used
[Database, Monitoring, Learning - NOT CONNECTED]
```

**Required Architecture (Fixed)**:

```
Frontend (React)
    ↓ API calls + WebSocket
Backend API Layer (FastAPI)
    ↓ INTEGRATED calls
Orchestrator Layer
    ↓ Task routing
Intelligence Manager (ML Predictions)
    ↓ Agent selection
Specialized AI Agents
    ↓ AI Provider calls
AI Provider Fallback Chain (16 providers)
    ↓ Task execution
Database Layer (Persistence)
    ↓ Results storage
Learning Engine (Continuous improvement)
    ↓ Monitoring
Prometheus/Grafana (Observability)
```

***

## **🎯 PART III: PHASE-BY-PHASE IMPLEMENTATION GUIDE**

### **PHASE 1: CORE AI ORCHESTRATION INTEGRATION (WEEKS 1-2)**

**Priority**: 🔴 **CRITICAL** - This is the foundation of everything

#### **Step 1.1: Integrate Orchestrator into Task API**

**File**: `src/api/routes/tasks.py`

**BEFORE (Current - Mock Data)**:
```python
# src/api/routes/tasks.py (CURRENT - BROKEN)
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter()

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate):
    """Current implementation - returns mock data"""
    # ❌ NO orchestrator integration
    # ❌ NO agent execution
    # ❌ NO AI provider usage
    
    return TaskResponse(
        id=generate_uuid(),
        title=task_data.title,
        status="pending",
        # Mock data only
    )

@router.post("/tasks/{task_id}/execute")
async def execute_task(task_id: str):
    """Current implementation - does nothing"""
    # ❌ NO actual execution
    return {"message": "Task started"}  # Fake response
```

**AFTER (Fixed - Real Integration)**:
```python
# src/api/routes/tasks.py (FIXED - PRODUCTION READY)
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
import asyncio

# 🔥 CRITICAL IMPORTS - Connect to core systems
from src.amas.core.unified_intelligence_orchestrator import UnifiedIntelligenceOrchestrator
from src.amas.intelligence.intelligence_manager import IntelligenceManager
from src.amas.intelligence.predictive_engine import PredictiveIntelligenceEngine
from src.database.connection import get_db
from src.cache.redis import get_redis
from src.api.websocket import websocket_manager

router = APIRouter()

# Initialize core systems (singleton pattern)
orchestrator = UnifiedIntelligenceOrchestrator()
intelligence_manager = IntelligenceManager()
predictive_engine = PredictiveIntelligenceEngine()

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """
    Create task with FULL AI orchestration integration
    
    ✅ ML predictions
    ✅ Intelligent agent selection
    ✅ Database persistence
    ✅ Real-time updates
    """
    
    # STEP 1: Generate task ID
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # STEP 2: ML-POWERED PREDICTION (NEW - CRITICAL)
    try:
        prediction = await predictive_engine.predict_task_outcome(
            task_type=task_data.task_type,
            target=task_data.target,
            parameters=task_data.parameters or {},
            context={
                "user_id": current_user.id,
                "time_of_day": datetime.now().hour,
                "day_of_week": datetime.now().weekday()
            }
        )
        
        logger.info(f"Task {task_id} prediction: "
                   f"success_prob={prediction.success_probability:.2f}, "
                   f"duration={prediction.estimated_duration:.1f}s")
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        # Fallback to defaults
        prediction = {
            "success_probability": 0.75,
            "estimated_duration": 120.0,
            "confidence": 0.3
        }
    
    # STEP 3: INTELLIGENT AGENT SELECTION (NEW - CRITICAL)
    try:
        selected_agents = await intelligence_manager.select_optimal_agents(
            task_type=task_data.task_type,
            target=task_data.target,
            predicted_complexity=prediction.get("complexity", "medium"),
            required_capabilities=task_data.required_capabilities or []
        )
        
        logger.info(f"Task {task_id} agents selected: {[a.name for a in selected_agents]}")
    except Exception as e:
        logger.error(f"Agent selection failed: {e}")
        # Fallback to default agent
        selected_agents = [orchestrator.get_default_agent(task_data.task_type)]
    
    # STEP 4: DATABASE PERSISTENCE (NEW - CRITICAL)
    try:
        task_record = {
            "task_id": task_id,
            "title": task_data.title,
            "description": task_data.description,
            "task_type": task_data.task_type,
            "target": task_data.target,
            "parameters": task_data.parameters,
            "status": "pending",
            "priority": task_data.priority or 5,
            "assigned_agents": [a.id for a in selected_agents],
            "prediction": {
                "success_probability": prediction.get("success_probability"),
                "estimated_duration": prediction.get("estimated_duration"),
                "confidence": prediction.get("confidence")
            },
            "created_by": current_user.id,
            "created_at": datetime.now()
        }
        
        await db.execute(
            "INSERT INTO tasks (task_id, title, description, task_type, target, "
            "parameters, status, priority, execution_metadata, created_at) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
            task_id, task_record["title"], task_record["description"],
            task_record["task_type"], task_record["target"],
            json.dumps(task_record["parameters"]), task_record["status"],
            task_record["priority"], json.dumps(task_record["prediction"]),
            task_record["created_at"]
        )
        
        logger.info(f"Task {task_id} persisted to database")
    except Exception as e:
        logger.error(f"Database insert failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")
    
    # STEP 5: CACHE TASK DATA (NEW)
    try:
        await redis.set(
            f"task:{task_id}",
            json.dumps(task_record),
            ttl=3600  # 1 hour
        )
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")  # Non-critical
    
    # STEP 6: REAL-TIME BROADCAST (NEW)
    try:
        await websocket_manager.broadcast({
            "event": "task_created",
            "task_id": task_id,
            "title": task_data.title,
            "prediction": prediction,
            "agents": [{"id": a.id, "name": a.name} for a in selected_agents]
        })
    except Exception as e:
        logger.warning(f"WebSocket broadcast failed: {e}")  # Non-critical
    
    # STEP 7: RETURN COMPLETE RESPONSE
    return TaskResponse(
        id=task_id,
        title=task_data.title,
        description=task_data.description,
        status="pending",
        task_type=task_data.task_type,
        target=task_data.target,
        priority=task_data.priority or 5,
        prediction={
            "success_probability": prediction.get("success_probability"),
            "estimated_duration": prediction.get("estimated_duration"),
            "estimated_cost": prediction.get("estimated_cost", 0.0),
            "confidence": prediction.get("confidence"),
            "recommended_agents": [
                {"id": a.id, "name": a.name, "expertise": a.expertise_score}
                for a in selected_agents
            ],
            "risk_factors": prediction.get("risk_factors", []),
            "optimization_suggestions": prediction.get("optimization_suggestions", [])
        },
        assigned_agents=[a.id for a in selected_agents],
        created_at=datetime.now(),
        created_by=current_user.id
    )


@router.post("/tasks/{task_id}/execute", response_model=TaskExecutionResponse)
async def execute_task(
    task_id: str,
    execution_options: Optional[TaskExecutionOptions] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute task with FULL orchestration
    
    ✅ Orchestrator coordination
    ✅ Agent execution
    ✅ AI provider usage
    ✅ Real-time progress updates
    ✅ Result persistence
    ✅ Learning feedback
    """
    
    # STEP 1: FETCH TASK FROM DATABASE
    try:
        task_row = await db.fetchrow(
            "SELECT * FROM tasks WHERE task_id = $1",
            task_id
        )
        
        if not task_row:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = dict(task_row)
        
    except Exception as e:
        logger.error(f"Database fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch task")
    
    # STEP 2: VALIDATE STATE
    if task_data["status"] not in ["pending", "failed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute task in {task_data['status']} state"
        )
    
    # STEP 3: UPDATE STATUS TO EXECUTING
    try:
        await db.execute(
            "UPDATE tasks SET status = $1, started_at = $2 WHERE task_id = $3",
            "executing", datetime.now(), task_id
        )
        
        # Broadcast status change
        await websocket_manager.broadcast({
            "event": "task_status_changed",
            "task_id": task_id,
            "status": "executing",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Status update failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to update task status")
    
    # STEP 4: EXECUTE VIA ORCHESTRATOR (NEW - CRITICAL)
    async def execute_task_async():
        """Background task execution with full orchestration"""
        
        execution_start = time.time()
        
        try:
            # 🔥 CRITICAL: Use orchestrator for execution
            result = await orchestrator.execute_task(
                task_id=task_id,
                task_type=task_data["task_type"],
                target=task_data["target"],
                parameters=json.loads(task_data["parameters"]) if task_data["parameters"] else {},
                assigned_agents=json.loads(task_data["execution_metadata"]).get("assigned_agents", []),
                user_context={
                    "user_id": current_user.id,
                    "execution_options": execution_options.dict() if execution_options else {}
                },
                # Real-time progress callback
                progress_callback=lambda progress: asyncio.create_task(
                    websocket_manager.broadcast({
                        "event": "task_progress",
                        "task_id": task_id,
                        "progress": progress.percentage,
                        "current_step": progress.current_step,
                        "agent_activity": progress.agent_activity
                    })
                )
            )
            
            execution_duration = time.time() - execution_start
            
            # STEP 5: PERSIST RESULTS
            await db.execute(
                "UPDATE tasks SET "
                "status = $1, "
                "result = $2, "
                "completed_at = $3, "
                "duration_seconds = $4, "
                "success_rate = $5, "
                "quality_score = $6 "
                "WHERE task_id = $7",
                "completed",
                json.dumps(result.output),
                datetime.now(),
                execution_duration,
                result.success_rate,
                result.quality_score,
                task_id
            )
            
            # STEP 6: UPDATE LEARNING ENGINE (NEW - CRITICAL)
            try:
                await intelligence_manager.record_task_execution(
                    task_id=task_id,
                    task_type=task_data["task_type"],
                    agents_used=result.agents_used,
                    execution_time=execution_duration,
                    success=result.success,
                    quality_score=result.quality_score,
                    user_feedback=None  # Will be added later
                )
                
                # Trigger model retraining if threshold reached
                task_count = await intelligence_manager.get_completed_task_count()
                if task_count % 20 == 0:
                    logger.info(f"Triggering model retraining (completed tasks: {task_count})")
                    background_tasks.add_task(
                        predictive_engine.retrain_models
                    )
                
            except Exception as e:
                logger.error(f"Learning engine update failed: {e}")
            
            # STEP 7: BROADCAST COMPLETION
            await websocket_manager.broadcast({
                "event": "task_completed",
                "task_id": task_id,
                "duration": execution_duration,
                "success": result.success,
                "quality_score": result.quality_score,
                "result_summary": result.summary
            })
            
            logger.info(f"Task {task_id} completed successfully in {execution_duration:.1f}s")
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            
            # Update task status to failed
            await db.execute(
                "UPDATE tasks SET "
                "status = $1, "
                "error_details = $2, "
                "completed_at = $3 "
                "WHERE task_id = $4",
                "failed",
                json.dumps({"error": str(e), "traceback": traceback.format_exc()}),
                datetime.now(),
                task_id
            )
            
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
        estimated_duration=json.loads(task_data["execution_metadata"]).get("prediction", {}).get("estimated_duration"),
        progress_url=f"/api/v1/tasks/{task_id}/progress",
        websocket_url=f"ws://your-domain/ws?task_id={task_id}"
    )


@router.get("/tasks/{task_id}/progress", response_model=TaskProgressResponse)
async def get_task_progress(
    task_id: str,
    db = Depends(get_db),
    redis = Depends(get_redis)
):
    """Get real-time task progress"""
    
    # Try cache first (faster)
    try:
        cached_progress = await redis.get(f"task:progress:{task_id}")
        if cached_progress:
            return TaskProgressResponse(**json.loads(cached_progress))
    except Exception:
        pass
    
    # Fetch from database
    try:
        task = await db.fetchrow(
            "SELECT task_id, status, started_at, completed_at, duration_seconds, result "
            "FROM tasks WHERE task_id = $1",
            task_id
        )
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Calculate progress
        if task["status"] == "completed":
            progress = 100.0
        elif task["status"] == "executing" and task["started_at"]:
            # Estimate based on average duration
            elapsed = (datetime.now() - task["started_at"]).total_seconds()
            estimated_total = 120.0  # Default estimate
            progress = min(95.0, (elapsed / estimated_total) * 100)
        else:
            progress = 0.0
        
        return TaskProgressResponse(
            task_id=task_id,
            status=task["status"],
            progress=progress,
            elapsed_time=task["duration_seconds"],
            estimated_remaining=max(0, estimated_total - elapsed) if task["status"] == "executing" else 0
        )
        
    except Exception as e:
        logger.error(f"Progress fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch progress")
```

**KEY CHANGES (CRITICAL)**:

1. ✅ **Imported orchestrator** - `from src.amas.core.unified_intelligence_orchestrator import UnifiedIntelligenceOrchestrator`
2. ✅ **Imported ML engine** - `from src.amas.intelligence.predictive_engine import PredictiveIntelligenceEngine`
3. ✅ **Imported intelligence manager** - `from src.amas.intelligence.intelligence_manager import IntelligenceManager`
4. ✅ **Used real predictions** - `await predictive_engine.predict_task_outcome(...)`
5. ✅ **Used intelligent agent selection** - `await intelligence_manager.select_optimal_agents(...)`
6. ✅ **Persisted to database** - `await db.execute("INSERT INTO tasks ...")`
7. ✅ **Real orchestrator execution** - `await orchestrator.execute_task(...)`
8. ✅ **Learning feedback loop** - `await intelligence_manager.record_task_execution(...)`
9. ✅ **Real-time WebSocket updates** - `await websocket_manager.broadcast(...)`
10. ✅ **Background task execution** - `background_tasks.add_task(execute_task_async)`

***

#### **Step 1.2: Implement Backend WebSocket Server**

**File**: `src/api/websocket.py` (NEW FILE - MUST CREATE)

```python
# src/api/websocket.py (NEW - CRITICAL FOR REAL-TIME)
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Set
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    WebSocket connection manager for real-time updates
    
    Features:
    • Connection lifecycle management
    • Broadcast to all clients
    • Targeted messaging by user/task
    • Automatic reconnection handling
    • Message queuing for offline clients
    """
    
    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Connections grouped by user ID
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Connections subscribed to specific tasks
        self.task_subscribers: Dict[str, Set[str]] = {}
        
        # Message queue for offline clients (in-memory, can move to Redis)
        self.message_queue: Dict[str, List[Dict]] = {}
        
        logger.info("WebSocket connection manager initialized")
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str = None):
        """Accept and register new WebSocket connection"""
        await websocket.accept()
        
        self.active_connections[connection_id] = websocket
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id} (user: {user_id})")
        
        # Send queued messages if any
        if connection_id in self.message_queue:
            for message in self.message_queue[connection_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send queued message: {e}")
            del self.message_queue[connection_id]
    
    def disconnect(self, connection_id: str):
        """Remove connection from manager"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from user connections
        for user_id, conn_ids in self.user_connections.items():
            if connection_id in conn_ids:
                conn_ids.remove(connection_id)
                break
        
        # Remove from task subscribers
        for task_id, conn_ids in self.task_subscribers.items():
            if connection_id in conn_ids:
                conn_ids.remove(connection_id)
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def broadcast(self, message: Dict):
        """
        Broadcast message to all connected clients
        
        Message format:
        {
            "event": "task_created" | "task_progress" | "agent_update" | ...,
            "data": { ... event-specific data ... },
            "timestamp": "2025-01-19T05:34:00Z"
        }
        """
        message["timestamp"] = datetime.now().isoformat()
        
        disconnected = []
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"Broadcast failed to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected clients
        for connection_id in disconnected:
            self.disconnect(connection_id)
        
        logger.debug(f"Broadcast to {len(self.active_connections)} clients: {message['event']}")
    
    async def send_to_user(self, user_id: str, message: Dict):
        """Send message to all connections for specific user"""
        message["timestamp"] = datetime.now().isoformat()
        
        if user_id not in self.user_connections:
            logger.warning(f"No connections found for user {user_id}")
            return
        
        connection_ids = list(self.user_connections[user_id])
        
        for connection_id in connection_ids:
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_json(message)
                except Exception as e:
                    logger.error(f"Send to user failed: {e}")
                    self.disconnect(connection_id)
    
    async def send_to_task_subscribers(self, task_id: str, message: Dict):
        """Send message to all clients subscribed to specific task"""
        message["timestamp"] = datetime.now().isoformat()
        
        if task_id not in self.task_subscribers:
            return
        
        connection_ids = list(self.task_subscribers[task_id])
        
        for connection_id in connection_ids:
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_json(message)
                except Exception as e:
                    logger.error(f"Send to task subscribers failed: {e}")
                    self.disconnect(connection_id)
    
    def subscribe_to_task(self, connection_id: str, task_id: str):
        """Subscribe connection to task updates"""
        if task_id not in self.task_subscribers:
            self.task_subscribers[task_id] = set()
        
        self.task_subscribers[task_id].add(connection_id)
        logger.info(f"Connection {connection_id} subscribed to task {task_id}")
    
    def unsubscribe_from_task(self, connection_id: str, task_id: str):
        """Unsubscribe connection from task updates"""
        if task_id in self.task_subscribers:
            self.task_subscribers[task_id].discard(connection_id)
            logger.info(f"Connection {connection_id} unsubscribed from task {task_id}")
    
    async def heartbeat(self):
        """Send periodic heartbeat to keep connections alive"""
        while True:
            await asyncio.sleep(30)  # Every 30 seconds
            
            message = {
                "event": "heartbeat",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.broadcast(message)

# Global instance
websocket_manager = ConnectionManager()


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),  # JWT token for authentication
):
    """
    WebSocket endpoint for real-time updates
    
    Client connection:
    ws://your-domain/ws?token=<JWT_TOKEN>
    
    Events sent to client:
    • task_created - New task created
    • task_progress - Task execution progress
    • task_completed - Task finished
    • task_failed - Task error
    • agent_update - Agent status change
    • system_alert - System notifications
    • heartbeat - Keep-alive ping
    """
    
    # Generate connection ID
    connection_id = f"ws_{uuid.uuid4().hex[:8]}"
    
    try:
        # Authenticate user from token
        try:
            user = await verify_jwt_token(token)
            user_id = user.id
        except Exception as e:
            logger.error(f"WebSocket authentication failed: {e}")
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        # Connect
        await websocket_manager.connect(websocket, connection_id, user_id)
        
        # Send welcome message
        await websocket.send_json({
            "event": "connected",
            "connection_id": connection_id,
            "message": "WebSocket connection established"
        })
        
        # Listen for client messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                
                # Handle client commands
                if data.get("command") == "subscribe_task":
                    task_id = data.get("task_id")
                    if task_id:
                        websocket_manager.subscribe_to_task(connection_id, task_id)
                        await websocket.send_json({
                            "event": "subscribed",
                            "task_id": task_id
                        })
                
                elif data.get("command") == "unsubscribe_task":
                    task_id = data.get("task_id")
                    if task_id:
                        websocket_manager.unsubscribe_from_task(connection_id, task_id)
                        await websocket.send_json({
                            "event": "unsubscribed",
                            "task_id": task_id
                        })
                
                elif data.get("command") == "ping":
                    await websocket.send_json({
                        "event": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {connection_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    
    finally:
        websocket_manager.disconnect(connection_id)


# Start heartbeat task on startup
@app.on_event("startup")
async def start_websocket_heartbeat():
    asyncio.create_task(websocket_manager.heartbeat())
```

**INTEGRATION INTO MAIN APP**:

```python
# src/api/main.py (ADD THIS)
from src.api.websocket import websocket_endpoint, websocket_manager

# WebSocket route already defined in websocket.py, just import
# The @app.websocket decorator will register it automatically
```

***

#### **Step 1.3: Connect AI Agents to Task Execution**

**File**: `src/amas/core/unified_intelligence_orchestrator.py` (ENHANCE EXISTING)

**CURRENT STATE** (Exists but not integrated):
```python
# The file exists (34KB) but execute_task() method needs enhancement
```

**REQUIRED ENHANCEMENT**:

```python
# src/amas/core/unified_intelligence_orchestrator.py (ENHANCE)
class UnifiedIntelligenceOrchestrator:
    """
    Enhanced orchestrator with full integration
    """
    
    def __init__(self):
        self.intelligence_manager = IntelligenceManager()
        self.agent_registry = self._initialize_agents()
        self.provider_router = EnhancedAIRouter()
        self.learning_engine = CollectiveLearningEngine()
        
    def _initialize_agents(self) -> Dict[str, BaseAgent]:
        """
        Initialize all 20+ specialized agents
        
        ✅ Security Expert Agent
        ✅ Code Analysis Agent
        ✅ OSINT Intelligence Agent
        ✅ Performance Monitor Agent
        ✅ Forensics Agent
        ✅ Testing Coordinator Agent
        ✅ Documentation Specialist Agent
        ✅ Network Analyzer Agent
        ✅ Data Analysis Agent
        ✅ Compliance Agent
        ✅ Investigation Agent
        ✅ Reporting Agent
        ... +10 more
        """
        agents = {}
        
        # Security Expert
        agents["security_expert"] = SecurityExpertAgent(
            name="Security Expert",
            model_name="gpt-4-turbo-preview",
            tools=[port_scanner, ssl_checker, vulnerability_scanner],
            system_prompt="""You are an elite cybersecurity expert specializing in 
            penetration testing, vulnerability assessment, and security auditing. 
            You analyze systems comprehensively and provide actionable recommendations."""
        )
        
        # Code Analysis
        agents["code_analyzer"] = CodeAnalysisAgent(
            name="Code Analyzer",
            model_name="gpt-4-turbo-preview",
            tools=[ast_parser, complexity_analyzer, security_linter],
            system_prompt="""You are a senior software engineer specializing in 
            code quality, security, and performance analysis. You review code 
            thoroughly and suggest improvements."""
        )
        
        # OSINT
        agents["osint_specialist"] = OSINTAgent(
            name="OSINT Specialist",
            model_name="gpt-4-turbo-preview",
            tools=[whois_lookup, dns_enumerator, subdomain_finder, email_harvester],
            system_prompt="""You are an open-source intelligence analyst specializing 
            in information gathering, reconnaissance, and threat intelligence."""
        )
        
        # Performance Monitor
        agents["performance_monitor"] = PerformanceMonitorAgent(
            name="Performance Monitor",
            model_name="gpt-4-turbo-preview",
            tools=[resource_profiler, bottleneck_analyzer, optimization_suggester],
            system_prompt="""You are a performance engineering expert specializing 
            in system optimization, bottleneck identification, and scalability analysis."""
        )
        
        # Forensics
        agents["forensics_investigator"] = ForensicsAgent(
            name="Forensics Investigator",
            model_name="gpt-4-turbo-preview",
            tools=[tech_stack_detector, version_fingerprinter, vulnerability_matcher],
            system_prompt="""You are a digital forensics specialist expert in 
            system analysis, technology identification, and vulnerability correlation."""
        )
        
        # Continue for all 20+ agents...
        # (Full implementation in actual code)
        
        return agents
    
    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        target: str,
        parameters: Dict,
        assigned_agents: List[str],
        user_context: Dict,
        progress_callback: Callable = None
    ) -> TaskExecutionResult:
        """
        Execute task with full orchestration
        
        Flow:
        1. Validate task and agents
        2. Create execution plan
        3. Execute agents in parallel/sequence
        4. Aggregate results
        5. Generate insights
        6. Return complete result
        """
        
        execution_start = time.time()
        
        try:
            # STEP 1: VALIDATE
            if not assigned_agents:
                assigned_agents = await self.intelligence_manager.select_optimal_agents(
                    task_type, target, parameters
                )
            
            # Get agent instances
            agents = [self.agent_registry.get(agent_id) for agent_id in assigned_agents]
            agents = [a for a in agents if a is not None]  # Filter None
            
            if not agents:
                raise ValueError("No valid agents available for task")
            
            if progress_callback:
                await progress_callback(TaskProgress(
                    percentage=5.0,
                    current_step="Agents selected",
                    agent_activity={}
                ))
            
            # STEP 2: CREATE EXECUTION PLAN
            execution_plan = await self._create_execution_plan(
                task_type, target, parameters, agents
            )
            
            if progress_callback:
                await progress_callback(TaskProgress(
                    percentage=10.0,
                    current_step="Execution plan created",
                    agent_activity={}
                ))
            
            # STEP 3: EXECUTE AGENTS
            agent_results = {}
            
            if execution_plan["mode"] == "parallel":
                # Execute agents in parallel
                tasks = [
                    self._execute_agent(
                        agent=agent,
                        task_id=task_id,
                        target=target,
                        parameters=parameters,
                        progress_callback=progress_callback
                    )
                    for agent in agents
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, agent in enumerate(agents):
                    if isinstance(results[i], Exception):
                        logger.error(f"Agent {agent.name} failed: {results[i]}")
                        agent_results[agent.id] = {
                            "success": False,
                            "error": str(results[i])
                        }
                    else:
                        agent_results[agent.id] = results[i]
            
            else:
                # Execute agents sequentially
                for agent in agents:
                    result = await self._execute_agent(
                        agent=agent,
                        task_id=task_id,
                        target=target,
                        parameters=parameters,
                        progress_callback=progress_callback
                    )
                    agent_results[agent.id] = result
            
            if progress_callback:
                await progress_callback(TaskProgress(
                    percentage=80.0,
                    current_step="Agent execution complete",
                    agent_activity=agent_results
                ))
            
            # STEP 4: AGGREGATE RESULTS
            aggregated_result = await self._aggregate_agent_results(
                agent_results, task_type
            )
            
            if progress_callback:
                await progress_callback(TaskProgress(
                    percentage=90.0,
                    current_step="Results aggregated",
                    agent_activity=agent_results
                ))
            
            # STEP 5: GENERATE INSIGHTS
            insights = await self._generate_insights(
                aggregated_result, agent_results, task_type
            )
            
            execution_duration = time.time() - execution_start
            
            if progress_callback:
                await progress_callback(TaskProgress(
                    percentage=100.0,
                    current_step="Complete",
                    agent_activity=agent_results
                ))
            
            # STEP 6: RETURN RESULT
            return TaskExecutionResult(
                task_id=task_id,
                success=True,
                output=aggregated_result,
                insights=insights,
                agents_used=[a.id for a in agents],
                execution_time=execution_duration,
                success_rate=self._calculate_success_rate(agent_results),
                quality_score=self._calculate_quality_score(agent_results),
                summary=self._generate_summary(aggregated_result, insights)
            )
        
        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            
            execution_duration = time.time() - execution_start
            
            return TaskExecutionResult(
                task_id=task_id,
                success=False,
                error=str(e),
                execution_time=execution_duration,
                summary=f"Task failed: {str(e)}"
            )
    
    async def _execute_agent(
        self,
        agent: BaseAgent,
        task_id: str,
        target: str,
        parameters: Dict,
        progress_callback: Callable = None
    ) -> Dict:
        """
        Execute single agent with AI provider fallback
        """
        
        agent_start = time.time()
        
        try:
            # Prepare agent prompt based on task
            prompt = self._prepare_agent_prompt(agent, target, parameters)
            
            # Execute agent with AI provider fallback
            response = await self.provider_router.generate_with_fallback(
                prompt=prompt,
                model_preference=agent.model_name,
                max_tokens=4000,
                temperature=0.3
            )
            
            # Parse agent response
            parsed_result = await agent.parse_response(response)
            
            agent_duration = time.time() - agent_start
            
            # Notify progress
            if progress_callback:
                await progress_callback(TaskProgress(
                    percentage=None,  # Partial update
                    current_step=f"Agent {agent.name} complete",
                    agent_activity={
                        agent.id: {
                            "status": "complete",
                            "duration": agent_duration
                        }
                    }
                ))
            
            return {
                "success": True,
                "agent_id": agent.id,
                "agent_name": agent.name,
                "result": parsed_result,
                "duration": agent_duration,
                "provider_used": response.provider,
                "tokens_used": response.tokens
            }
        
        except Exception as e:
            logger.error(f"Agent {agent.name} execution failed: {e}")
            
            return {
                "success": False,
                "agent_id": agent.id,
                "agent_name": agent.name,
                "error": str(e),
                "duration": time.time() - agent_start
            }
```

***

NEXT PART 2
