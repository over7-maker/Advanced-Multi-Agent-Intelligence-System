
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class OrchestratorTask:
    id: str
    description: str
    task_type: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    assigned_agent_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "assigned_agent_id": self.assigned_agent_id,
            "result": self.result,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            id=data["id"],
            description=data["description"],
            task_type=data["task_type"],
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            assigned_agent_id=data.get("assigned_agent_id"),
            result=data.get("result"),
            metadata=data.get("metadata", {}),
        )

@dataclass
class AgentConfig:
    agent_id: str
    agent_type: str
    config: Dict[str, Any]

    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "config": self.config,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            agent_id=data["agent_id"],
            agent_type=data["agent_type"],
            config=data["config"],
        )

