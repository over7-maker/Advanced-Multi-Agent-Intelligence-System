"""
Persistent Background Task Scheduler

Provides cron-like scheduling capabilities for long-term AI task automation
with state persistence, priority management, and intelligent execution.
"""

import asyncio
import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import croniter

logger = logging.getLogger(__name__)

class ScheduleType(str, Enum):
    CRON = "cron"                    # Cron expression scheduling
    INTERVAL = "interval"            # Fixed interval scheduling  
    ONE_TIME = "one_time"            # Single execution at specific time
    EVENT_DRIVEN = "event_driven"    # Triggered by external events
    CONDITIONAL = "conditional"      # Execute when conditions are met

class TaskPriority(str, Enum):
    LOW = "low"                      # Background processing
    NORMAL = "normal"                # Standard automation tasks
    HIGH = "high"                    # Important recurring tasks
    URGENT = "urgent"                # Time-sensitive automation
    CRITICAL = "critical"            # System-critical tasks

class ScheduledTaskStatus(str, Enum):
    ACTIVE = "active"                # Task is active and will be scheduled
    PAUSED = "paused"                # Task is paused, won't be scheduled
    COMPLETED = "completed"          # One-time task completed
    FAILED = "failed"                # Task failed and needs attention
    CANCELLED = "cancelled"          # Task was cancelled
    EXPIRED = "expired"              # Task passed its end date

@dataclass
class ScheduledTask:
    """Represents a task scheduled for background execution"""
    id: str
    name: str
    description: str
    
    # Scheduling configuration
    schedule_type: ScheduleType
    schedule_expression: str         # Cron expression or interval specification
    timezone: str = "UTC"
    
    # Task configuration
    task_request: str               # The actual AI task to execute
    task_parameters: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    
    # Execution constraints
    max_duration_hours: float = 24.0
    max_retries: int = 3
    timeout_seconds: int = 86400    # 24 hours
    
    # Lifecycle management
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: ScheduledTaskStatus = ScheduledTaskStatus.ACTIVE
    
    # Execution tracking
    next_execution: Optional[datetime] = None
    last_execution: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    # Results and notifications
    last_result: Dict[str, Any] = field(default_factory=dict)
    notification_channels: List[str] = field(default_factory=list)
    notification_on_failure: bool = True
    notification_on_success: bool = False
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"
    tags: Set[str] = field(default_factory=set)
    
    def calculate_next_execution(self) -> Optional[datetime]:
        """Calculate next execution time based on schedule"""
        current_time = datetime.now(timezone.utc)
        
        # Check if task is active and within date range
        if self.status != ScheduledTaskStatus.ACTIVE:
            return None
        
        if self.start_date and current_time < self.start_date:
            return self.start_date
        
        if self.end_date and current_time > self.end_date:
            self.status = ScheduledTaskStatus.EXPIRED
            return None
        
        try:
            if self.schedule_type == ScheduleType.CRON:
                cron = croniter.croniter(self.schedule_expression, current_time)
                return cron.get_next(datetime)
            
            elif self.schedule_type == ScheduleType.INTERVAL:
                # Parse interval (e.g., "30m", "2h", "1d")
                if self.last_execution:
                    base_time = self.last_execution
                else:
                    base_time = current_time
                
                interval_seconds = self._parse_interval(self.schedule_expression)
                return base_time + timedelta(seconds=interval_seconds)
            
            elif self.schedule_type == ScheduleType.ONE_TIME:
                # Parse datetime string
                if self.last_execution:
                    return None  # One-time task already executed
                
                return datetime.fromisoformat(self.schedule_expression.replace('Z', '+00:00'))
            
            else:
                # EVENT_DRIVEN and CONDITIONAL don't have time-based scheduling
                return None
                
        except Exception as e:
            logger.error(f"Error calculating next execution for {self.id}: {e}")
            return None
    
    def _parse_interval(self, interval_str: str) -> int:
        """Parse interval string to seconds"""
        interval_str = interval_str.lower().strip()
        
        if interval_str.endswith('s'):
            return int(interval_str[:-1])
        elif interval_str.endswith('m'):
            return int(interval_str[:-1]) * 60
        elif interval_str.endswith('h'):
            return int(interval_str[:-1]) * 3600
        elif interval_str.endswith('d'):
            return int(interval_str[:-1]) * 86400
        elif interval_str.endswith('w'):
            return int(interval_str[:-1]) * 604800
        else:
            # Assume seconds if no unit
            return int(interval_str)
    
    def should_execute_now(self) -> bool:
        """Check if task should execute now"""
        if self.status != ScheduledTaskStatus.ACTIVE:
            return False
        
        if not self.next_execution:
            self.next_execution = self.calculate_next_execution()
        
        if not self.next_execution:
            return False
        
        current_time = datetime.now(timezone.utc)
        return current_time >= self.next_execution
    
    def record_execution(self, success: bool, result: Dict[str, Any], duration_seconds: float):
        """Record execution attempt and result"""
        self.execution_count += 1
        self.last_execution = datetime.now(timezone.utc)
        self.last_result = result
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        # Calculate next execution
        if self.schedule_type == ScheduleType.ONE_TIME:
            self.status = ScheduledTaskStatus.COMPLETED if success else ScheduledTaskStatus.FAILED
            self.next_execution = None
        else:
            self.next_execution = self.calculate_next_execution()
        
        logger.debug(f"Recorded execution for {self.id}: success={success}, duration={duration_seconds:.1f}s")

class TaskScheduler:
    """Background task scheduler for long-term AI automation"""
    
    def __init__(self, db_path: str = "data/scheduler.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory task tracking
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.execution_futures: Dict[str, asyncio.Task] = {}
        
        # Scheduler state
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self.total_executions: int = 0
        self.successful_executions: int = 0
        self.failed_executions: int = 0
        
        # Initialize database
        self._init_database()
        
        # Load existing tasks from persistence
        asyncio.create_task(self._load_scheduled_tasks())
        
        logger.info(f"Task Scheduler initialized with database: {self.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database for task persistence"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    schedule_type TEXT NOT NULL,
                    schedule_expression TEXT NOT NULL,
                    timezone TEXT DEFAULT 'UTC',
                    task_request TEXT NOT NULL,
                    task_parameters TEXT,  -- JSON
                    priority TEXT DEFAULT 'normal',
                    max_duration_hours REAL DEFAULT 24.0,
                    max_retries INTEGER DEFAULT 3,
                    timeout_seconds INTEGER DEFAULT 86400,
                    start_date TEXT,
                    end_date TEXT,
                    status TEXT DEFAULT 'active',
                    next_execution TEXT,
                    last_execution TEXT,
                    execution_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    last_result TEXT,  -- JSON
                    notification_channels TEXT,  -- JSON list
                    notification_on_failure BOOLEAN DEFAULT 1,
                    notification_on_success BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL,
                    created_by TEXT DEFAULT 'system',
                    tags TEXT  -- JSON set
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS execution_history (
                    id TEXT PRIMARY KEY,
                    scheduled_task_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT NOT NULL,  -- 'running', 'completed', 'failed', 'timeout'
                    result TEXT,  -- JSON
                    error_message TEXT,
                    execution_duration_seconds REAL,
                    workflow_execution_id TEXT,
                    FOREIGN KEY (scheduled_task_id) REFERENCES scheduled_tasks (id)
                )
            """)
            
            conn.commit()
    
    async def _load_scheduled_tasks(self):
        """Load scheduled tasks from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM scheduled_tasks WHERE status = 'active'")
            
            for row in cursor.fetchall():
                task = self._row_to_scheduled_task(row)
                self.scheduled_tasks[task.id] = task
        
        logger.info(f"Loaded {len(self.scheduled_tasks)} active scheduled tasks")
    
    def _row_to_scheduled_task(self, row: sqlite3.Row) -> ScheduledTask:
        """Convert database row to ScheduledTask object"""
        return ScheduledTask(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            schedule_type=ScheduleType(row["schedule_type"]),
            schedule_expression=row["schedule_expression"],
            timezone=row["timezone"],
            task_request=row["task_request"],
            task_parameters=json.loads(row["task_parameters"]) if row["task_parameters"] else {},
            priority=TaskPriority(row["priority"]),
            max_duration_hours=row["max_duration_hours"],
            max_retries=row["max_retries"],
            timeout_seconds=row["timeout_seconds"],
            start_date=datetime.fromisoformat(row["start_date"]) if row["start_date"] else None,
            end_date=datetime.fromisoformat(row["end_date"]) if row["end_date"] else None,
            status=ScheduledTaskStatus(row["status"]),
            next_execution=datetime.fromisoformat(row["next_execution"]) if row["next_execution"] else None,
            last_execution=datetime.fromisoformat(row["last_execution"]) if row["last_execution"] else None,
            execution_count=row["execution_count"],
            success_count=row["success_count"],
            failure_count=row["failure_count"],
            last_result=json.loads(row["last_result"]) if row["last_result"] else {},
            notification_channels=json.loads(row["notification_channels"]) if row["notification_channels"] else [],
            notification_on_failure=bool(row["notification_on_failure"]),
            notification_on_success=bool(row["notification_on_success"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            created_by=row["created_by"],
            tags=set(json.loads(row["tags"])) if row["tags"] else set()
        )
    
    async def schedule_task(self, 
                          name: str,
                          task_request: str,
                          schedule_expression: str,
                          schedule_type: ScheduleType = ScheduleType.CRON,
                          priority: TaskPriority = TaskPriority.NORMAL,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          task_parameters: Dict[str, Any] = None,
                          notification_channels: List[str] = None,
                          tags: Set[str] = None) -> str:
        """Schedule a new background task"""
        
        task_id = f"sched_{uuid.uuid4().hex[:8]}"
        
        scheduled_task = ScheduledTask(
            id=task_id,
            name=name,
            description=f"Scheduled task: {task_request[:100]}...",
            schedule_type=schedule_type,
            schedule_expression=schedule_expression,
            task_request=task_request,
            task_parameters=task_parameters or {},
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            notification_channels=notification_channels or [],
            tags=tags or set()
        )
        
        # Calculate first execution
        scheduled_task.next_execution = scheduled_task.calculate_next_execution()
        
        # Store in database
        await self._persist_scheduled_task(scheduled_task)
        
        # Store in memory
        self.scheduled_tasks[task_id] = scheduled_task
        
        logger.info(f"Scheduled task created: {task_id} ({name}) - Next: {scheduled_task.next_execution}")
        return task_id
    
    async def _persist_scheduled_task(self, task: ScheduledTask):
        """Persist scheduled task to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO scheduled_tasks (
                    id, name, description, schedule_type, schedule_expression, timezone,
                    task_request, task_parameters, priority, max_duration_hours, max_retries,
                    timeout_seconds, start_date, end_date, status, next_execution, last_execution,
                    execution_count, success_count, failure_count, last_result,
                    notification_channels, notification_on_failure, notification_on_success,
                    created_at, created_by, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id, task.name, task.description, task.schedule_type.value,
                task.schedule_expression, task.timezone, task.task_request,
                json.dumps(task.task_parameters), task.priority.value,
                task.max_duration_hours, task.max_retries, task.timeout_seconds,
                task.start_date.isoformat() if task.start_date else None,
                task.end_date.isoformat() if task.end_date else None,
                task.status.value,
                task.next_execution.isoformat() if task.next_execution else None,
                task.last_execution.isoformat() if task.last_execution else None,
                task.execution_count, task.success_count, task.failure_count,
                json.dumps(task.last_result), json.dumps(task.notification_channels),
                task.notification_on_failure, task.notification_on_success,
                task.created_at.isoformat(), task.created_by, json.dumps(list(task.tags))
            ))
            conn.commit()
    
    async def start_scheduler(self):
        """Start the background task scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        logger.info("Task scheduler started")
    
    async def stop_scheduler(self):
        """Stop the background task scheduler"""
        self.running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all running executions
        for execution_future in list(self.execution_futures.values()):
            execution_future.cancel()
        
        self.execution_futures.clear()
        
        logger.info("Task scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Check all scheduled tasks
                ready_tasks = []
                for task_id, task in list(self.scheduled_tasks.items()):
                    
                    # Update next execution if needed
                    if not task.next_execution:
                        task.next_execution = task.calculate_next_execution()
                        await self._persist_scheduled_task(task)
                    
                    # Check if ready to execute
                    if task.should_execute_now():
                        # Don't start if already running
                        if task_id not in self.execution_futures:
                            ready_tasks.append(task)
                
                # Execute ready tasks (by priority)
                ready_tasks.sort(key=lambda t: self._get_priority_weight(t.priority), reverse=True)
                
                for task in ready_tasks:
                    # Start task execution
                    execution_future = asyncio.create_task(
                        self._execute_scheduled_task(task)
                    )
                    self.execution_futures[task.id] = execution_future
                    
                    logger.info(f"Started execution of scheduled task: {task.id} ({task.name})")
                
                # Clean up completed executions
                completed_executions = []
                for task_id, future in self.execution_futures.items():
                    if future.done():
                        completed_executions.append(task_id)
                
                for task_id in completed_executions:
                    future = self.execution_futures.pop(task_id)
                    try:
                        result = await future
                        logger.debug(f"Scheduled task execution completed: {task_id}")
                    except Exception as e:
                        logger.error(f"Scheduled task execution error: {task_id}: {e}")
                
                # Sleep before next check (adjust based on workload)
                check_interval = 30 if ready_tasks else 60  # More frequent when busy
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Back off on error
    
    def _get_priority_weight(self, priority: TaskPriority) -> int:
        """Get numeric weight for priority sorting"""
        weights = {
            TaskPriority.LOW: 1,
            TaskPriority.NORMAL: 5,
            TaskPriority.HIGH: 10,
            TaskPriority.URGENT: 20,
            TaskPriority.CRITICAL: 50
        }
        return weights.get(priority, 5)
    
    async def _execute_scheduled_task(self, scheduled_task: ScheduledTask) -> Dict[str, Any]:
        """Execute a scheduled task using the orchestration system"""
        execution_id = f"exec_{scheduled_task.id}_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now(timezone.utc)
        
        logger.info(f"Executing scheduled task: {scheduled_task.id} ({scheduled_task.name})")
        
        # Record execution start in database
        await self._record_execution_start(execution_id, scheduled_task.id)
        
        try:
            # Execute task using workflow executor
            try:
                from amas.orchestration.workflow_executor import get_workflow_executor
                workflow_executor = get_workflow_executor()
            except ImportError:
                from ..orchestration.workflow_executor import get_workflow_executor
                workflow_executor = get_workflow_executor()
            
            # Create task with parameters
            full_task_request = scheduled_task.task_request
            if scheduled_task.task_parameters:
                # Inject parameters into task request
                full_task_request += f" Parameters: {json.dumps(scheduled_task.task_parameters)}"
            
            # Execute with timeout
            workflow_execution_id = await asyncio.wait_for(
                workflow_executor.execute_workflow(full_task_request),
                timeout=scheduled_task.timeout_seconds
            )
            
            # Wait for workflow completion (with monitoring)
            await self._monitor_workflow_execution(workflow_execution_id, scheduled_task)
            
            # Get final workflow status
            execution_status = workflow_executor.get_execution_status(workflow_execution_id)
            
            # Calculate duration
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Determine success
            success = (execution_status and 
                      execution_status.get("status") == "completed" and
                      execution_status.get("progress_percentage", 0) >= 90)
            
            # Prepare result
            result = {
                "workflow_execution_id": workflow_execution_id,
                "execution_status": execution_status,
                "duration_seconds": duration,
                "success": success
            }
            
            # Record execution result
            scheduled_task.record_execution(success, result, duration)
            await self._persist_scheduled_task(scheduled_task)
            
            # Record in execution history
            await self._record_execution_completion(execution_id, scheduled_task.id, 
                                                   success, result, duration)
            
            # Send notifications if configured
            if ((success and scheduled_task.notification_on_success) or 
                (not success and scheduled_task.notification_on_failure)):
                await self._send_execution_notification(scheduled_task, result, success)
            
            # Update metrics
            self.total_executions += 1
            if success:
                self.successful_executions += 1
            else:
                self.failed_executions += 1
            
            logger.info(f"Scheduled task execution {'succeeded' if success else 'failed'}: "
                       f"{scheduled_task.id} (Duration: {duration:.1f}s)")
            
            return result
            
        except asyncio.TimeoutError:
            duration = scheduled_task.timeout_seconds
            result = {"error": "execution_timeout", "duration_seconds": duration}
            
            scheduled_task.record_execution(False, result, duration)
            await self._persist_scheduled_task(scheduled_task)
            
            await self._record_execution_completion(execution_id, scheduled_task.id, 
                                                   False, result, duration)
            
            self.total_executions += 1
            self.failed_executions += 1
            
            logger.error(f"Scheduled task timed out: {scheduled_task.id} after {duration}s")
            return result
            
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            result = {"error": str(e), "duration_seconds": duration}
            
            scheduled_task.record_execution(False, result, duration)
            await self._persist_scheduled_task(scheduled_task)
            
            await self._record_execution_completion(execution_id, scheduled_task.id, 
                                                   False, result, duration)
            
            self.total_executions += 1
            self.failed_executions += 1
            
            logger.error(f"Scheduled task execution failed: {scheduled_task.id}: {e}")
            return result
    
    async def _monitor_workflow_execution(self, 
                                        workflow_execution_id: str, 
                                        scheduled_task: ScheduledTask):
        """Monitor workflow execution with periodic status checks"""
        try:
            from amas.orchestration.workflow_executor import get_workflow_executor
            workflow_executor = get_workflow_executor()
        except ImportError:
            from ..orchestration.workflow_executor import get_workflow_executor
            workflow_executor = get_workflow_executor()
        
        max_wait_time = scheduled_task.max_duration_hours * 3600  # Convert to seconds
        start_time = datetime.now(timezone.utc)
        
        while (datetime.now(timezone.utc) - start_time).total_seconds() < max_wait_time:
            # Get execution status
            status = workflow_executor.get_execution_status(workflow_execution_id)
            
            if not status:
                logger.warning(f"Lost track of workflow execution: {workflow_execution_id}")
                break
            
            # Check if completed
            if status.get("status") in ["completed", "failed", "cancelled"]:
                logger.info(f"Workflow execution finished: {workflow_execution_id} - {status.get('status')}")
                break
            
            # Log progress periodically
            progress = status.get("progress_percentage", 0)
            if progress > 0:
                logger.debug(f"Workflow progress: {workflow_execution_id} - {progress:.1f}%")
            
            # Wait before next check
            await asyncio.sleep(60)  # Check every minute
        
        # Final status check
        final_status = workflow_executor.get_execution_status(workflow_execution_id)
        if final_status:
            logger.info(f"Final workflow status: {workflow_execution_id} - {final_status.get('status')}")
    
    async def _record_execution_start(self, execution_id: str, scheduled_task_id: str):
        """Record execution start in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO execution_history (
                    id, scheduled_task_id, started_at, status
                ) VALUES (?, ?, ?, ?)
            """, (
                execution_id, scheduled_task_id, 
                datetime.now(timezone.utc).isoformat(), "running"
            ))
            conn.commit()
    
    async def _record_execution_completion(self, 
                                         execution_id: str,
                                         scheduled_task_id: str,
                                         success: bool,
                                         result: Dict[str, Any],
                                         duration_seconds: float):
        """Record execution completion in database"""
        status = "completed" if success else "failed"
        workflow_execution_id = result.get("workflow_execution_id")
        error_message = result.get("error") if not success else None
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE execution_history SET
                    completed_at = ?, status = ?, result = ?, error_message = ?,
                    execution_duration_seconds = ?, workflow_execution_id = ?
                WHERE id = ?
            """, (
                datetime.now(timezone.utc).isoformat(), status, json.dumps(result),
                error_message, duration_seconds, workflow_execution_id, execution_id
            ))
            conn.commit()
    
    async def _send_execution_notification(self, 
                                         scheduled_task: ScheduledTask,
                                         result: Dict[str, Any],
                                         success: bool):
        """Send notification about task execution"""
        if not scheduled_task.notification_channels:
            return
        
        # Import notification system (will be implemented in PR-H continuation)
        try:
            from ..automation.notification_engine import (
                NotificationPriority,
                get_notification_engine,
            )
            notification_engine = get_notification_engine()
            
            notification_data = {
                "task_id": scheduled_task.id,
                "task_name": scheduled_task.name,
                "execution_result": "success" if success else "failure",
                "execution_time": result.get("duration_seconds", 0),
                "workflow_id": result.get("workflow_execution_id"),
                "error_details": result.get("error") if not success else None
            }
            
            await notification_engine.send_notification(
                notification_type="scheduled_task_result",
                data=notification_data,
                channels=scheduled_task.notification_channels,
                priority=NotificationPriority.HIGH if not success else NotificationPriority.NORMAL
            )
            
        except ImportError:
            # Notification system not yet implemented
            logger.info(f"Notification queued for {scheduled_task.id}: {success}")
    
    async def get_scheduled_tasks(self, 
                                status_filter: Optional[ScheduledTaskStatus] = None,
                                limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of scheduled tasks"""
        tasks = []
        
        for task in self.scheduled_tasks.values():
            if status_filter and task.status != status_filter:
                continue
            
            task_info = {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "schedule_type": task.schedule_type.value,
                "schedule_expression": task.schedule_expression,
                "priority": task.priority.value,
                "status": task.status.value,
                "next_execution": task.next_execution.isoformat() if task.next_execution else None,
                "last_execution": task.last_execution.isoformat() if task.last_execution else None,
                "execution_count": task.execution_count,
                "success_rate": (task.success_count / max(1, task.execution_count)) * 100,
                "tags": list(task.tags)
            }
            
            tasks.append(task_info)
            
            if len(tasks) >= limit:
                break
        
        return tasks
    
    async def pause_task(self, task_id: str) -> bool:
        """Pause a scheduled task"""
        task = self.scheduled_tasks.get(task_id)
        if not task:
            return False
        
        task.status = ScheduledTaskStatus.PAUSED
        await self._persist_scheduled_task(task)
        
        # Cancel running execution if any
        if task_id in self.execution_futures:
            self.execution_futures[task_id].cancel()
            del self.execution_futures[task_id]
        
        logger.info(f"Scheduled task paused: {task_id}")
        return True
    
    async def resume_task(self, task_id: str) -> bool:
        """Resume a paused scheduled task"""
        task = self.scheduled_tasks.get(task_id)
        if not task or task.status != ScheduledTaskStatus.PAUSED:
            return False
        
        task.status = ScheduledTaskStatus.ACTIVE
        task.next_execution = task.calculate_next_execution()
        await self._persist_scheduled_task(task)
        
        logger.info(f"Scheduled task resumed: {task_id}")
        return True
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a scheduled task"""
        task = self.scheduled_tasks.get(task_id)
        if not task:
            return False
        
        # Cancel running execution if any
        if task_id in self.execution_futures:
            self.execution_futures[task_id].cancel()
            del self.execution_futures[task_id]
        
        # Remove from memory
        del self.scheduled_tasks[task_id]
        
        # Remove from database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM scheduled_tasks WHERE id = ?", (task_id,))
            conn.execute("DELETE FROM execution_history WHERE scheduled_task_id = ?", (task_id,))
            conn.commit()
        
        logger.info(f"Scheduled task deleted: {task_id}")
        return True
    
    def get_scheduler_metrics(self) -> Dict[str, Any]:
        """Get scheduler performance metrics"""
        active_tasks = sum(1 for task in self.scheduled_tasks.values() 
                          if task.status == ScheduledTaskStatus.ACTIVE)
        
        running_executions = len(self.execution_futures)
        
        success_rate = (self.successful_executions / max(1, self.total_executions)) * 100
        
        # Calculate next execution times
        upcoming_executions = []
        for task in self.scheduled_tasks.values():
            if task.next_execution and task.status == ScheduledTaskStatus.ACTIVE:
                upcoming_executions.append(task.next_execution)
        
        upcoming_executions.sort()
        next_execution = upcoming_executions[0] if upcoming_executions else None
        
        return {
            "running": self.running,
            "total_scheduled_tasks": len(self.scheduled_tasks),
            "active_tasks": active_tasks,
            "running_executions": running_executions,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate_percent": round(success_rate, 2),
            "next_execution": next_execution.isoformat() if next_execution else None,
            "upcoming_24h": len([t for t in upcoming_executions 
                               if t < datetime.now(timezone.utc) + timedelta(hours=24)])
        }

# Global task scheduler instance
_global_task_scheduler: Optional[TaskScheduler] = None

def get_task_scheduler() -> TaskScheduler:
    """Get global task scheduler instance"""
    global _global_task_scheduler
    if _global_task_scheduler is None:
        _global_task_scheduler = TaskScheduler()
    return _global_task_scheduler

# Convenience functions for common scheduling patterns

async def schedule_daily_task(name: str, task_request: str, hour: int = 9, minute: int = 0) -> str:
    """Schedule a daily task at specific time"""
    scheduler = get_task_scheduler()
    cron_expression = f"{minute} {hour} * * *"
    
    return await scheduler.schedule_task(
        name=name,
        task_request=task_request,
        schedule_expression=cron_expression,
        schedule_type=ScheduleType.CRON,
        priority=TaskPriority.NORMAL
    )

async def schedule_weekly_task(name: str, task_request: str, day_of_week: int = 1, hour: int = 9) -> str:
    """Schedule a weekly task (0=Sunday, 6=Saturday)"""
    scheduler = get_task_scheduler()
    cron_expression = f"0 {hour} * * {day_of_week}"
    
    return await scheduler.schedule_task(
        name=name,
        task_request=task_request,
        schedule_expression=cron_expression,
        schedule_type=ScheduleType.CRON,
        priority=TaskPriority.NORMAL
    )

async def schedule_monthly_report(name: str, task_request: str, day_of_month: int = 1) -> str:
    """Schedule a monthly report"""
    scheduler = get_task_scheduler()
    cron_expression = f"0 9 {day_of_month} * *"  # 9 AM on specified day
    
    return await scheduler.schedule_task(
        name=name,
        task_request=task_request,
        schedule_expression=cron_expression,
        schedule_type=ScheduleType.CRON,
        priority=TaskPriority.HIGH,
        tags={"report", "monthly"}
    )

# Example usage
if __name__ == "__main__":
    async def test_scheduler():
        scheduler = TaskScheduler()
        
        # Test daily competitor monitoring
        daily_task_id = await schedule_daily_task(
            name="Daily Competitor Analysis",
            task_request="Monitor top 5 AI automation competitors, analyze pricing changes, identify new features or announcements",
            hour=8  # 8 AM daily
        )
        
        # Test weekly market report
        weekly_task_id = await schedule_weekly_task(
            name="Weekly Market Intelligence",
            task_request="Analyze AI automation market trends, compile industry news, create executive summary with key insights",
            day_of_week=1,  # Monday
            hour=9
        )
        
        # Test monthly comprehensive analysis
        monthly_task_id = await schedule_monthly_report(
            name="Monthly Strategic Analysis",
            task_request="Comprehensive competitive landscape analysis, market opportunity assessment, strategic recommendations for product roadmap"
        )
        
        print("Created scheduled tasks:")
        print(f"Daily: {daily_task_id}")
        print(f"Weekly: {weekly_task_id}")
        print(f"Monthly: {monthly_task_id}")
        
        # Start scheduler
        await scheduler.start_scheduler()
        
        # Get metrics
        metrics = scheduler.get_scheduler_metrics()
        print("\nScheduler metrics:")
        print(json.dumps(metrics, indent=2))
        
        # Let it run for a bit (in real usage, would run indefinitely)
        await asyncio.sleep(10)
        
        await scheduler.stop_scheduler()
    
    asyncio.run(test_scheduler())
