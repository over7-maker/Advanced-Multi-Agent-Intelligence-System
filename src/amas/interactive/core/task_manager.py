"""
AMAS Task Manager - Advanced Task Management System
Advanced Multi-Agent Intelligence System - Interactive Mode

This module provides comprehensive task management capabilities including
task queuing, scheduling, monitoring, and lifecycle management.
"""

import asyncio
import json
import logging
import time

# import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Rich for enhanced output
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table


class TaskStatus(Enum):
    """Task status enumeration"""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    SCHEDULED = "scheduled"


class TaskPriority(Enum):
    """Task priority enumeration"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Enhanced task data structure"""

    id: str
    command: str
    intent: str
    target: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    agents_involved: List[str] = None
    progress: float = 0.0
    results: Dict[str, Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    dependencies: List[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.agents_involved is None:
            self.agents_involved = []
        if self.results is None:
            self.results = {}
        if self.metadata is None:
            self.metadata = {}
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []

    @property
    def duration(self) -> float:
        """Calculate task duration in seconds"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return 0.0

    @property
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ]

    @property
    def is_running(self) -> bool:
        """Check if task is running"""
        return self.status == TaskStatus.RUNNING

    @property
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.retry_count < self.max_retries and self.status == TaskStatus.FAILED


@dataclass
class TaskFilter:
    """Task filter criteria"""

    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    intent: Optional[str] = None
    target: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    tags: Optional[List[str]] = None
    agents: Optional[List[str]] = None


class TaskManager:
    """Advanced Task Management System"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()
        self.logger = logging.getLogger(__name__)

        # Task storage
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.scheduled_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[str] = []

        # Task execution
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_executor = TaskExecutor()

        # Performance tracking
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0,
            "average_duration": 0.0,
            "success_rate": 0.0,
            "total_runtime": 0.0,
        }

        # Persistence
        self.data_dir = Path(config.get("data_directory", "data/tasks"))
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing tasks
        self._load_tasks()

        # Start background tasks
        self._start_background_tasks()

    def _load_tasks(self):
        """Load tasks from persistent storage"""
        try:
            tasks_file = self.data_dir / "tasks.json"
            if tasks_file.exists():
                with open(tasks_file, "r") as f:
                    data = json.load(f)

                for task_data in data.get("tasks", []):
                    # Convert datetime strings back to datetime objects
                    if task_data.get("created_at"):
                        task_data["created_at"] = datetime.fromisoformat(
                            task_data["created_at"]
                        )
                    if task_data.get("started_at"):
                        task_data["started_at"] = datetime.fromisoformat(
                            task_data["started_at"]
                        )
                    if task_data.get("completed_at"):
                        task_data["completed_at"] = datetime.fromisoformat(
                            task_data["completed_at"]
                        )

                    # Convert enums
                    task_data["status"] = TaskStatus(task_data["status"])
                    task_data["priority"] = TaskPriority(task_data["priority"])

                    task = Task(**task_data)
                    self.tasks[task.id] = task

                    # Update completed tasks list
                    if task.is_completed:
                        self.completed_tasks.append(task.id)

                self.logger.info(f"Loaded {len(self.tasks)} tasks from storage")

        except Exception as e:
            self.logger.error(f"Failed to load tasks: {e}")

    def _save_tasks(self):
        """Save tasks to persistent storage"""
        try:
            tasks_file = self.data_dir / "tasks.json"

            # Convert tasks to serializable format
            tasks_data = []
            for task in self.tasks.values():
                task_dict = asdict(task)

                # Convert datetime objects to strings
                for field in ["created_at", "started_at", "completed_at"]:
                    if task_dict.get(field):
                        task_dict[field] = task_dict[field].isoformat()

                # Convert enums to strings
                task_dict["status"] = task.status.value
                task_dict["priority"] = task.priority.value

                tasks_data.append(task_dict)

            # Save to file
            data = {
                "tasks": tasks_data,
                "stats": self.stats,
                "last_updated": datetime.now().isoformat(),
            }

            with open(tasks_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save tasks: {e}")

    def _start_background_tasks(self):
        """Start background task processing"""
        asyncio.create_task(self._process_task_queue())
        asyncio.create_task(self._process_scheduled_tasks())
        asyncio.create_task(self._cleanup_old_tasks())

    async def _process_task_queue(self):
        """Process task queue continuously"""
        while True:
            try:
                if self.task_queue:
                    task_id = self.task_queue.pop(0)
                    if task_id in self.tasks:
                        task = self.tasks[task_id]
                        if task.status == TaskStatus.QUEUED:
                            await self._execute_task(task)

                await asyncio.sleep(1)  # Check every second

            except Exception as e:
                self.logger.error(f"Error processing task queue: {e}")
                await asyncio.sleep(5)

    async def _process_scheduled_tasks(self):
        """Process scheduled tasks"""
        while True:
            try:
                now = datetime.now()
                ready_tasks = []

                for task_id, task in self.scheduled_tasks.items():
                    if task.created_at <= now:
                        ready_tasks.append(task_id)

                for task_id in ready_tasks:
                    task = self.scheduled_tasks.pop(task_id)
                    task.status = TaskStatus.QUEUED
                    self.task_queue.append(task_id)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error processing scheduled tasks: {e}")
                await asyncio.sleep(60)

    async def _cleanup_old_tasks(self):
        """Cleanup old completed tasks"""
        while True:
            try:
                cutoff_date = datetime.now() - timedelta(
                    days=30
                )  # Keep tasks for 30 days
                tasks_to_remove = []

                for task_id, task in self.tasks.items():
                    if (
                        task.is_completed
                        and task.completed_at
                        and task.completed_at < cutoff_date
                    ):
                        tasks_to_remove.append(task_id)

                for task_id in tasks_to_remove:
                    del self.tasks[task_id]
                    if task_id in self.completed_tasks:
                        self.completed_tasks.remove(task_id)

                if tasks_to_remove:
                    self.logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
                    self._save_tasks()

                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up old tasks: {e}")
                await asyncio.sleep(3600)

    def add_task(self, task: Task) -> str:
        """Add a new task to the manager"""
        self.tasks[task.id] = task
        self.stats["total_tasks"] += 1

        # Add to queue or schedule
        if task.status == TaskStatus.QUEUED:
            self.task_queue.append(task.id)
        elif task.status == TaskStatus.SCHEDULED:
            self.scheduled_tasks[task.id] = task

        self._save_tasks()
        self.logger.info(f"Added task {task.id}: {task.intent}")

        return task.id

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    def get_tasks(self, filter_criteria: Optional[TaskFilter] = None) -> List[Task]:
        """Get tasks with optional filtering"""
        tasks = list(self.tasks.values())

        if not filter_criteria:
            return tasks

        # Apply filters
        if filter_criteria.status:
            tasks = [t for t in tasks if t.status == filter_criteria.status]

        if filter_criteria.priority:
            tasks = [t for t in tasks if t.priority == filter_criteria.priority]

        if filter_criteria.intent:
            tasks = [
                t for t in tasks if filter_criteria.intent.lower() in t.intent.lower()
            ]

        if filter_criteria.target:
            tasks = [
                t for t in tasks if filter_criteria.target.lower() in t.target.lower()
            ]

        if filter_criteria.created_after:
            tasks = [t for t in tasks if t.created_at >= filter_criteria.created_after]

        if filter_criteria.created_before:
            tasks = [t for t in tasks if t.created_at <= filter_criteria.created_before]

        if filter_criteria.tags:
            tasks = [
                t for t in tasks if any(tag in t.tags for tag in filter_criteria.tags)
            ]

        if filter_criteria.agents:
            tasks = [
                t
                for t in tasks
                if any(agent in t.agents_involved for agent in filter_criteria.agents)
            ]

        return tasks

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task with new data"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        # Update fields
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        # Update status-specific logic
        if updates.get("status") == TaskStatus.RUNNING and not task.started_at:
            task.started_at = datetime.now()
        elif updates.get("status") in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ]:
            task.completed_at = datetime.now()
            if task_id not in self.completed_tasks:
                self.completed_tasks.append(task_id)

        self._save_tasks()
        return True

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        if task.is_completed:
            return False

        # Cancel active execution
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            del self.active_tasks[task_id]

        # Update task status
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()

        # Remove from queue
        if task_id in self.task_queue:
            self.task_queue.remove(task_id)

        self.stats["cancelled_tasks"] += 1
        self._save_tasks()

        self.logger.info(f"Cancelled task {task_id}")
        return True

    def retry_task(self, task_id: str) -> bool:
        """Retry a failed task"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        if not task.can_retry:
            return False

        # Reset task for retry
        task.status = TaskStatus.QUEUED
        task.started_at = None
        task.completed_at = None
        task.progress = 0.0
        task.error = None
        task.retry_count += 1

        # Add back to queue
        self.task_queue.append(task_id)

        self._save_tasks()
        self.logger.info(f"Retrying task {task_id} (attempt {task.retry_count})")
        return True

    async def _execute_task(self, task: Task):
        """Execute a task"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()

            # Create execution task
            execution_task = asyncio.create_task(self.task_executor.execute(task))
            self.active_tasks[task.id] = execution_task

            # Wait for completion
            result = await execution_task

            # Update task with results
            if result.get("success", False):
                task.status = TaskStatus.COMPLETED
                task.results = result.get("results", {})
                self.stats["completed_tasks"] += 1
            else:
                task.status = TaskStatus.FAILED
                task.error = result.get("error", "Unknown error")
                self.stats["failed_tasks"] += 1

            task.completed_at = datetime.now()

            # Update statistics
            self._update_stats()

        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            self.stats["cancelled_tasks"] += 1
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            self.stats["failed_tasks"] += 1
            self.logger.error(f"Task execution failed: {e}")
        finally:
            # Cleanup
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]

            self._save_tasks()

    def _update_stats(self):
        """Update performance statistics"""
        total_completed = (
            self.stats["completed_tasks"]
            + self.stats["failed_tasks"]
            + self.stats["cancelled_tasks"]
        )

        if total_completed > 0:
            self.stats["success_rate"] = self.stats["completed_tasks"] / total_completed

        # Calculate average duration
        completed_tasks = [
            t
            for t in self.tasks.values()
            if t.status == TaskStatus.COMPLETED and t.duration > 0
        ]
        if completed_tasks:
            total_duration = sum(t.duration for t in completed_tasks)
            self.stats["average_duration"] = total_duration / len(completed_tasks)
            self.stats["total_runtime"] = total_duration

    def get_stats(self) -> Dict[str, Any]:
        """Get task management statistics"""
        return self.stats.copy()

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            "queue_length": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "scheduled_tasks": len(self.scheduled_tasks),
            "completed_tasks": len(self.completed_tasks),
            "total_tasks": len(self.tasks),
        }

    def display_task_summary(self, task_id: str):
        """Display task summary"""
        task = self.get_task(task_id)
        if not task:
            self.console.print(f"❌ Task {task_id} not found", style="red")
            return

        # Create summary table
        table = Table(title=f"📋 Task Summary: {task_id}")
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="green")

        table.add_row("Command", task.command)
        table.add_row("Intent", task.intent)
        table.add_row("Target", task.target)
        table.add_row("Status", task.status.value.upper())
        table.add_row("Priority", task.priority.name)
        table.add_row("Progress", f"{task.progress:.1%}")
        table.add_row("Duration", f"{task.duration:.2f}s")
        table.add_row("Retry Count", str(task.retry_count))

        if task.agents_involved:
            table.add_row("Agents", ", ".join(task.agents_involved))

        if task.error:
            table.add_row("Error", task.error)

        self.console.print(table)

    def display_queue_status(self):
        """Display current queue status"""
        status = self.get_queue_status()

        table = Table(title="📊 Task Queue Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for metric, value in status.items():
            table.add_row(metric.replace("_", " ").title(), str(value))

        self.console.print(table)

    def export_tasks(
        self, file_path: str, filter_criteria: Optional[TaskFilter] = None
    ):
        """Export tasks to file"""
        tasks = self.get_tasks(filter_criteria)

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_tasks": len(tasks),
            "tasks": [],
        }

        for task in tasks:
            task_dict = asdict(task)

            # Convert datetime objects to strings
            for field in ["created_at", "started_at", "completed_at"]:
                if task_dict.get(field):
                    task_dict[field] = task_dict[field].isoformat()

            # Convert enums to strings
            task_dict["status"] = task.status.value
            task_dict["priority"] = task.priority.value

            export_data["tasks"].append(task_dict)

        with open(file_path, "w") as f:
            json.dump(export_data, f, indent=2)

        self.console.print(
            f"✅ Exported {len(tasks)} tasks to {file_path}", style="green"
        )


class TaskExecutor:
    """Task execution engine"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a task"""
        try:
            # Simulate task execution based on intent
            await asyncio.sleep(
                min(task.timeout_seconds / 10, 10)
            )  # Scale down for demo

            # Generate results based on task type
            results = self._generate_results(task)

            return {
                "success": True,
                "results": results,
                "execution_time": task.duration,
            }

        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return {"success": False, "error": str(e), "execution_time": task.duration}

    def _generate_results(self, task: Task) -> Dict[str, Any]:
        """Generate results based on task type"""
        intent = task.intent
        target = task.target

        base_results = {
            "task_id": task.id,
            "intent": intent,
            "target": target,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "execution_time": task.duration,
        }

        # Generate specific results based on intent
        if "security" in intent.lower():
            base_results.update(
                {
                    "security_score": 85 + (hash(target) % 15),  # Random score 85-100
                    "vulnerabilities": {
                        "critical": 0,
                        "high": 1,
                        "medium": 2,
                        "low": 3,
                    },
                    "recommendations": [
                        "Update SSL configuration",
                        "Implement Content Security Policy",
                        "Enable HTTP Strict Transport Security",
                    ],
                }
            )
        elif "code" in intent.lower():
            base_results.update(
                {
                    "code_quality_score": 80
                    + (hash(target) % 20),  # Random score 80-100
                    "metrics": {
                        "lines_of_code": 1000 + (hash(target) % 5000),
                        "functions": 50 + (hash(target) % 100),
                        "classes": 10 + (hash(target) % 50),
                        "test_coverage": 70 + (hash(target) % 30),
                    },
                    "issues": {
                        "style": 3,
                        "performance": 1,
                        "security": 0,
                        "maintainability": 2,
                    },
                }
            )
        elif "intelligence" in intent.lower() or "research" in intent.lower():
            base_results.update(
                {
                    "sources_analyzed": 10 + (hash(target) % 20),
                    "data_points": 50 + (hash(target) % 100),
                    "confidence_level": 75 + (hash(target) % 25),
                    "threat_level": "low",
                    "key_findings": [
                        "Active development detected",
                        "Community engagement: Moderate",
                        "Security practices: Standard",
                    ],
                }
            )
        else:
            base_results.update(
                {
                    "analysis_complete": True,
                    "findings": f"Analysis of {target} completed successfully",
                    "recommendations": ["Review results", "Take appropriate action"],
                }
            )

        return base_results
