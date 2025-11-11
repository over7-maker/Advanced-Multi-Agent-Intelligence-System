"""
Base Agent Contract System for AMAS

Provides strict typing and validation for all agent interactions
to ensure predictable and safe multi-agent operations.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Type
from pydantic import BaseModel, Field, validator
from enum import Enum
import jsonschema
from abc import ABC, abstractmethod

class ToolCapability(str, Enum):
    """Enumeration of available tool capabilities"""
    WEB_SEARCH = "web_search"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    API_CALL = "api_call"
    DATABASE_QUERY = "database_query"
    EMAIL_SEND = "email_send"
    DATA_ANALYSIS = "data_analysis"
    VECTOR_SEARCH = "vector_search"
    CODE_EXECUTION = "code_execution"
    DOCUMENT_GENERATION = "document_generation"

class AgentRole(str, Enum):
    """Enumeration of agent roles"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    ORCHESTRATOR = "orchestrator"
    COMMUNICATION = "communication"
    VALIDATION = "validation"

class ExecutionStatus(str, Enum):
    """Status of agent execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class AgentContract(BaseModel, ABC):
    """Base contract for all AMAS agents"""
    
    # Agent Identity
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_version: str = Field(default="1.0.0", description="Agent version")
    role: AgentRole = Field(..., description="Agent's functional role")
    
    # Execution Constraints
    max_iterations: int = Field(default=10, ge=1, le=100, description="Maximum execution iterations")
    timeout_seconds: int = Field(default=300, ge=30, le=3600, description="Execution timeout")
    cost_budget_tokens: int = Field(default=10000, ge=100, le=1000000, description="Token budget")
    
    # Tool Permissions
    allowed_tools: List[ToolCapability] = Field(..., description="Permitted tool capabilities")
    
    # Quality Gates
    require_human_approval: bool = Field(default=False, description="Require human approval for risky actions")
    output_validation_required: bool = Field(default=True, description="Validate outputs against schema")
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = Field(None, description="Creator identifier")
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for input validation"""
        pass
    
    @abstractmethod 
    def get_output_schema(self) -> Dict[str, Any]:
        """Return JSON schema for output validation"""
        pass
    
    @validator('allowed_tools')
    def validate_tools(cls, v):
        if not v:
            raise ValueError("Agent must have at least one allowed tool")
        return v
    
    @validator('agent_id')
    def validate_agent_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Agent ID cannot be empty")
        return v.strip()
    
    def can_use_tool(self, tool: Union[str, ToolCapability]) -> bool:
        """Check if agent can use specified tool"""
        tool_capability = ToolCapability(tool) if isinstance(tool, str) else tool
        return tool_capability in self.allowed_tools
    
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate input data against contract schema"""
        try:
            jsonschema.validate(input_data, self.get_input_schema())
            return True, None
        except jsonschema.ValidationError as e:
            return False, f"Input validation failed: {e.message}"
    
    def validate_output(self, output_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate output data against contract schema"""
        if not self.output_validation_required:
            return True, None
        
        try:
            jsonschema.validate(output_data, self.get_output_schema())
            return True, None
        except jsonschema.ValidationError as e:
            return False, f"Output validation failed: {e.message}"
    
    def to_manifest(self) -> Dict[str, Any]:
        """Export contract as deployment manifest"""
        return {
            "agent_id": self.agent_id,
            "agent_version": self.agent_version,
            "role": self.role.value,
            "input_schema": self.get_input_schema(),
            "output_schema": self.get_output_schema(),
            "allowed_tools": [tool.value for tool in self.allowed_tools],
            "constraints": {
                "max_iterations": self.max_iterations,
                "timeout_seconds": self.timeout_seconds,
                "cost_budget_tokens": self.cost_budget_tokens
            },
            "quality_gates": {
                "require_human_approval": self.require_human_approval,
                "output_validation_required": self.output_validation_required
            },
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ExecutionContext(BaseModel):
    """Execution context for agent operations"""
    
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = Field(None, description="Requesting user")
    trace_id: Optional[str] = Field(None, description="Distributed tracing ID")
    parent_agent_id: Optional[str] = Field(None, description="Parent agent in chain")
    priority: int = Field(default=5, ge=1, le=10, description="Execution priority")
    
    # Resource limits
    max_memory_mb: int = Field(default=512, ge=64, le=4096)
    max_cpu_cores: float = Field(default=1.0, ge=0.1, le=4.0)
    
    # Environment
    environment: str = Field(default="production", description="Execution environment")
    region: Optional[str] = Field(None, description="Execution region")
    
    # Audit
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class AgentExecution(BaseModel):
    """Record of agent execution"""
    
    execution_id: str
    agent_id: str
    context: ExecutionContext
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Performance metrics
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    tokens_used: Optional[int] = None
    
    # Quality metrics
    error_message: Optional[str] = None
    validation_errors: List[str] = Field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    
    def mark_completed(self, output_data: Dict[str, Any], tokens_used: int = 0):
        """Mark execution as completed"""
        self.status = ExecutionStatus.COMPLETED
        self.output_data = output_data
        self.completed_at = datetime.now(timezone.utc)
        self.tokens_used = tokens_used
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def mark_failed(self, error_message: str):
        """Mark execution as failed"""
        self.status = ExecutionStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now(timezone.utc)
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def add_tool_call(self, tool_name: str, parameters: Dict[str, Any], result: Any):
        """Record a tool call"""
        self.tool_calls.append({
            "tool": tool_name,
            "parameters": parameters,
            "result_summary": str(result)[:200] + "..." if len(str(result)) > 200 else str(result),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

class ContractViolationError(Exception):
    """Raised when agent contract is violated"""
    
    def __init__(self, agent_id: str, violation_type: str, details: str):
        self.agent_id = agent_id
        self.violation_type = violation_type
        self.details = details
        super().__init__(f"Agent {agent_id} contract violation ({violation_type}): {details}")
