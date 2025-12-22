"""
Tool Governance System for AMAS

Provides centralized tool access control, permissions management,
and usage monitoring for all agent interactions.
"""

import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import jsonschema
import yaml

from ..agent_contracts.base_agent_contract import ContractViolationError, ToolCapability

logger = logging.getLogger(__name__)

class ToolRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ToolAccessDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    RATE_LIMITED = "rate_limited"

@dataclass
class ToolDefinition:
    """Definition of a tool available to agents"""
    name: str
    capability: ToolCapability
    description: str
    risk_level: ToolRiskLevel
    requires_approval: bool = False
    rate_limit_per_minute: Optional[int] = None
    allowed_parameters: Optional[Dict[str, Any]] = None
    forbidden_parameters: Optional[List[str]] = None
    output_size_limit_mb: Optional[float] = None
    network_access_required: bool = False
    
@dataclass
class ToolUsageRecord:
    """Record of tool usage by an agent"""
    timestamp: datetime
    agent_id: str
    user_id: Optional[str]
    tool_name: str
    parameters: Dict[str, Any]
    duration_seconds: float
    status: str
    output_size_bytes: int
    error_message: Optional[str] = None
    trace_id: Optional[str] = None

class ToolRegistry:
    """Registry of all available tools and their definitions"""
    
    def __init__(self, config_path: str = "config/tool_definitions.yaml"):
        self.config_path = Path(config_path)
        self.tools: Dict[str, ToolDefinition] = {}
        self.usage_records: List[ToolUsageRecord] = []
        self._load_tool_definitions()
    
    def _load_tool_definitions(self):
        """Load tool definitions from configuration"""
        if not self.config_path.exists():
            logger.warning(f"Tool definitions file not found: {self.config_path}")
            self._create_default_definitions()
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            for tool_data in config.get('tools', []):
                tool_def = ToolDefinition(**tool_data)
                self.tools[tool_def.name] = tool_def
                
            logger.info(f"Loaded {len(self.tools)} tool definitions")
            
        except Exception as e:
            logger.error(f"Failed to load tool definitions: {e}")
            self._create_default_definitions()
    
    def _create_default_definitions(self):
        """Create default tool definitions"""
        default_tools = [
            ToolDefinition(
                name="web_search",
                capability=ToolCapability.WEB_SEARCH,
                description="Search the web for information",
                risk_level=ToolRiskLevel.MEDIUM,
                rate_limit_per_minute=30,
                network_access_required=True,
                output_size_limit_mb=10.0
            ),
            ToolDefinition(
                name="file_read",
                capability=ToolCapability.FILE_READ,
                description="Read files from filesystem",
                risk_level=ToolRiskLevel.LOW,
                rate_limit_per_minute=100,
                allowed_parameters={
                    "file_path": {"type": "string", "pattern": "^[^/].*\\.(txt|json|csv|md)$"}
                },
                output_size_limit_mb=50.0
            ),
            ToolDefinition(
                name="file_write",
                capability=ToolCapability.FILE_WRITE,
                description="Write files to filesystem",
                risk_level=ToolRiskLevel.HIGH,
                requires_approval=True,
                rate_limit_per_minute=10,
                forbidden_parameters=["system_path", "config_path"],
                output_size_limit_mb=100.0
            ),
            ToolDefinition(
                name="api_call",
                capability=ToolCapability.API_CALL,
                description="Make API calls to external services",
                risk_level=ToolRiskLevel.MEDIUM,
                rate_limit_per_minute=60,
                network_access_required=True,
                allowed_parameters={
                    "method": {"type": "string", "enum": ["GET", "POST"]},
                    "url": {"type": "string", "format": "uri"}
                }
            ),
            ToolDefinition(
                name="database_query",
                capability=ToolCapability.DATABASE_QUERY,
                description="Query database for information",
                risk_level=ToolRiskLevel.HIGH,
                requires_approval=True,
                rate_limit_per_minute=20,
                allowed_parameters={
                    "query_type": {"type": "string", "enum": ["SELECT"]},
                    "table_whitelist": {"type": "array", "items": {"type": "string"}}
                }
            ),
            ToolDefinition(
                name="code_execution",
                capability=ToolCapability.CODE_EXECUTION,
                description="Execute code in sandboxed environment",
                risk_level=ToolRiskLevel.CRITICAL,
                requires_approval=True,
                rate_limit_per_minute=5,
                allowed_parameters={
                    "language": {"type": "string", "enum": ["python", "javascript"]},
                    "timeout_seconds": {"type": "integer", "maximum": 300}
                },
                output_size_limit_mb=1.0
            )
        ]
        
        for tool_def in default_tools:
            self.tools[tool_def.name] = tool_def
        
        # Save default definitions
        self.save_definitions()
    
    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name"""
        return self.tools.get(tool_name)
    
    def get_tools_by_capability(self, capability: ToolCapability) -> List[ToolDefinition]:
        """Get all tools with specified capability"""
        return [tool for tool in self.tools.values() if tool.capability == capability]
    
    def register_tool(self, tool_def: ToolDefinition):
        """Register a new tool"""
        self.tools[tool_def.name] = tool_def
        logger.info(f"Registered tool: {tool_def.name} ({tool_def.capability})")
    
    def record_usage(self, record: ToolUsageRecord):
        """Record tool usage"""
        self.usage_records.append(record)
        
        # Log usage for monitoring
        logger.info(f"Tool usage: {record.agent_id} used {record.tool_name} "
                   f"(status: {record.status}, duration: {record.duration_seconds:.2f}s)")
    
    def get_usage_stats(self, 
                       agent_id: Optional[str] = None,
                       tool_name: Optional[str] = None,
                       hours: int = 24) -> Dict[str, Any]:
        """Get usage statistics"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        filtered_records = [
            record for record in self.usage_records
            if record.timestamp >= cutoff_time
            and (not agent_id or record.agent_id == agent_id)
            and (not tool_name or record.tool_name == tool_name)
        ]
        
        if not filtered_records:
            return {"total_calls": 0, "success_rate": 0.0, "avg_duration": 0.0}
        
        successful_calls = [r for r in filtered_records if r.status == "success"]
        total_duration = sum(r.duration_seconds for r in filtered_records)
        
        return {
            "total_calls": len(filtered_records),
            "successful_calls": len(successful_calls),
            "success_rate": len(successful_calls) / len(filtered_records),
            "avg_duration_seconds": total_duration / len(filtered_records),
            "total_output_mb": sum(r.output_size_bytes for r in filtered_records) / (1024 * 1024)
        }
    
    def save_definitions(self):
        """Save tool definitions to config file"""
        def convert_enums(obj):
            """Recursively convert Enum objects to their string values"""
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            return obj
        
        config = {
            "tools": [convert_enums(asdict(tool)) for tool in self.tools.values()]
        }
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False)

class ToolPermissionsEngine:
    """Engine for enforcing tool access permissions"""
    
    def __init__(self, 
                 registry: ToolRegistry,
                 agent_capabilities_path: str = "config/agent_capabilities.yaml"):
        self.registry = registry
        self.capabilities_path = Path(agent_capabilities_path)
        self.agent_permissions: Dict[str, Set[str]] = {}
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}  # agent_id -> tool_name -> limiter state
        self._load_agent_permissions()
    
    def _load_agent_permissions(self):
        """Load agent permissions from configuration"""
        if not self.capabilities_path.exists():
            logger.warning(f"Agent capabilities file not found: {self.capabilities_path}")
            return
        
        try:
            with open(self.capabilities_path, 'r') as f:
                config = yaml.safe_load(f)
            
            for agent_id, agent_config in config.get('agents', {}).items():
                self.agent_permissions[agent_id] = set(agent_config.get('allowed_tools', []))
                
            logger.info(f"Loaded permissions for {len(self.agent_permissions)} agents")
            
        except Exception as e:
            logger.error(f"Failed to load agent permissions: {e}")
    
    async def check_tool_access(self, 
                               agent_id: str, 
                               tool_name: str,
                               user_id: Optional[str] = None) -> ToolAccessDecision:
        """Check if agent can access the specified tool"""
        
        # Check if tool exists
        tool_def = self.registry.get_tool(tool_name)
        if not tool_def:
            logger.warning(f"Unknown tool requested: {tool_name}")
            return ToolAccessDecision.DENY
        
        # Check agent permissions
        agent_tools = self.agent_permissions.get(agent_id, set())
        if tool_name not in agent_tools:
            logger.warning(f"Agent {agent_id} denied access to {tool_name}")
            return ToolAccessDecision.DENY
        
        # Check if approval required
        if tool_def.requires_approval:
            return ToolAccessDecision.REQUIRE_APPROVAL
        
        # Check rate limiting
        if tool_def.rate_limit_per_minute:
            is_rate_limited = await self._check_rate_limit(
                agent_id, tool_name, tool_def.rate_limit_per_minute
            )
            if is_rate_limited:
                return ToolAccessDecision.RATE_LIMITED
        
        return ToolAccessDecision.ALLOW
    
    async def _check_rate_limit(self, 
                               agent_id: str, 
                               tool_name: str, 
                               limit_per_minute: int) -> bool:
        """Check if agent is rate limited for tool"""
        key = f"{agent_id}:{tool_name}"
        
        if key not in self.rate_limiters:
            self.rate_limiters[key] = {
                "requests": [],
                "last_reset": datetime.now(timezone.utc)
            }
        
        limiter = self.rate_limiters[key]
        now = datetime.now(timezone.utc)
        
        # Remove requests older than 1 minute
        cutoff_time = now - timedelta(minutes=1)
        limiter["requests"] = [
            req_time for req_time in limiter["requests"]
            if req_time > cutoff_time
        ]
        
        # Check if under limit
        if len(limiter["requests"]) >= limit_per_minute:
            logger.warning(f"Rate limit exceeded for {agent_id} using {tool_name}")
            return True
        
        # Add current request
        limiter["requests"].append(now)
        return False
    
    def validate_tool_parameters(self, 
                               tool_name: str, 
                               parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate tool parameters against tool definition"""
        tool_def = self.registry.get_tool(tool_name)
        if not tool_def:
            return False, f"Tool {tool_name} not found"
        
        # Check forbidden parameters
        if tool_def.forbidden_parameters:
            forbidden_found = set(parameters.keys()) & set(tool_def.forbidden_parameters)
            if forbidden_found:
                return False, f"Forbidden parameters: {', '.join(forbidden_found)}"
        
        # Validate against allowed parameter schema
        if tool_def.allowed_parameters:
            try:
                jsonschema.validate(parameters, {
                    "type": "object",
                    "properties": tool_def.allowed_parameters,
                    "additionalProperties": False
                })
            except jsonschema.ValidationError as e:
                return False, f"Parameter validation failed: {e.message}"
        
        return True, None
    
    def get_agent_tools(self, agent_id: str) -> List[ToolDefinition]:
        """Get all tools available to an agent"""
        agent_tool_names = self.agent_permissions.get(agent_id, set())
        return [self.registry.tools[name] for name in agent_tool_names if name in self.registry.tools]
    
    def add_agent_permission(self, agent_id: str, tool_name: str):
        """Grant tool permission to agent"""
        if agent_id not in self.agent_permissions:
            self.agent_permissions[agent_id] = set()
        self.agent_permissions[agent_id].add(tool_name)
        logger.info(f"Granted {tool_name} permission to agent {agent_id}")
    
    def remove_agent_permission(self, agent_id: str, tool_name: str):
        """Revoke tool permission from agent"""
        if agent_id in self.agent_permissions:
            self.agent_permissions[agent_id].discard(tool_name)
            logger.info(f"Revoked {tool_name} permission from agent {agent_id}")
    
    def get_usage_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive usage report"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_records = [
            record for record in self.registry.usage_records
            if record.timestamp >= cutoff_time
        ]
        
        # Group by agent and tool
        agent_usage = {}
        tool_usage = {}
        
        for record in recent_records:
            # Agent usage
            if record.agent_id not in agent_usage:
                agent_usage[record.agent_id] = {"total": 0, "tools": {}}
            agent_usage[record.agent_id]["total"] += 1
            
            if record.tool_name not in agent_usage[record.agent_id]["tools"]:
                agent_usage[record.agent_id]["tools"][record.tool_name] = 0
            agent_usage[record.agent_id]["tools"][record.tool_name] += 1
            
            # Tool usage
            if record.tool_name not in tool_usage:
                tool_usage[record.tool_name] = {"total": 0, "agents": {}}
            tool_usage[record.tool_name]["total"] += 1
            
            if record.agent_id not in tool_usage[record.tool_name]["agents"]:
                tool_usage[record.tool_name]["agents"][record.agent_id] = 0
            tool_usage[record.tool_name]["agents"][record.agent_id] += 1
        
        return {
            "time_range_hours": hours,
            "total_tool_calls": len(recent_records),
            "unique_agents": len(agent_usage),
            "unique_tools": len(tool_usage),
            "agent_usage": agent_usage,
            "tool_usage": tool_usage,
            "success_rate": len([r for r in recent_records if r.status == "success"]) / max(len(recent_records), 1)
        }

class ToolExecutionGuard:
    """Guards tool execution with safety checks"""
    
    def __init__(self, permissions_engine: ToolPermissionsEngine):
        self.permissions_engine = permissions_engine
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}  # execution_id -> approval_request
    
    async def execute_tool(self,
                          agent_id: str,
                          tool_name: str,
                          parameters: Dict[str, Any],
                          user_id: Optional[str] = None,
                          trace_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute tool with full safety checks"""
        
        execution_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)
        
        try:
            # Check access permissions
            access_decision = await self.permissions_engine.check_tool_access(
                agent_id, tool_name, user_id
            )
            
            # Hard denials and rate limits take precedence
            if access_decision == ToolAccessDecision.DENY:
                raise ContractViolationError(
                    agent_id, "tool_access_denied", f"Access denied to tool {tool_name}"
                )
            
            if access_decision == ToolAccessDecision.RATE_LIMITED:
                raise ContractViolationError(
                    agent_id, "rate_limit_exceeded", f"Rate limit exceeded for tool {tool_name}"
                )
            
            # Validate parameters BEFORE approval flow so invalid input is rejected
            params_valid, param_error = self.permissions_engine.validate_tool_parameters(
                tool_name, parameters
            )
            if not params_valid:
                raise ContractViolationError(
                    agent_id, "invalid_parameters", param_error or "Invalid parameters"
                )
            
            # High‑risk tools may require approval after validation
            if access_decision == ToolAccessDecision.REQUIRE_APPROVAL:
                approval_id = await self._request_approval(
                    execution_id, agent_id, tool_name, parameters, user_id
                )
                return {
                    "status": "pending_approval",
                    "approval_id": approval_id,
                    "message": f"Tool {tool_name} requires human approval"
                }
            
            # Execute the actual tool
            # In real implementation, this would dispatch to actual tool handlers
            result = await self._execute_tool_implementation(tool_name, parameters)
            
            # Record successful usage
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            usage_record = ToolUsageRecord(
                timestamp=start_time,
                agent_id=agent_id,
                user_id=user_id,
                tool_name=tool_name,
                parameters=parameters,
                duration_seconds=duration,
                status="success",
                output_size_bytes=len(str(result)),
                trace_id=trace_id
            )
            self.permissions_engine.registry.record_usage(usage_record)
            
            return {
                "status": "success",
                "result": result,
                "execution_id": execution_id,
                "duration_seconds": duration
            }
            
        except Exception as e:
            # Record failed usage
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            usage_record = ToolUsageRecord(
                timestamp=start_time,
                agent_id=agent_id,
                user_id=user_id,
                tool_name=tool_name,
                parameters=parameters,
                duration_seconds=duration,
                status="error",
                output_size_bytes=0,
                error_message=str(e),
                trace_id=trace_id
            )
            self.permissions_engine.registry.record_usage(usage_record)
            
            raise
    
    async def _request_approval(self,
                              execution_id: str,
                              agent_id: str,
                              tool_name: str,
                              parameters: Dict[str, Any],
                              user_id: Optional[str]) -> str:
        """Request human approval for tool usage"""
        approval_id = str(uuid.uuid4())
        
        approval_request = {
            "approval_id": approval_id,
            "execution_id": execution_id,
            "agent_id": agent_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "user_id": user_id,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending"
        }
        
        self.pending_approvals[approval_id] = approval_request
        
        # In real implementation, this would notify approvers
        logger.info(f"Approval requested: {approval_id} for {agent_id} to use {tool_name}")
        
        return approval_id
    
    async def _execute_tool_implementation(self, 
                                         tool_name: str, 
                                         parameters: Dict[str, Any]) -> Any:
        """Execute the actual tool (placeholder implementation)"""
        
        # This would dispatch to actual tool implementations
        # For now, return mock results based on tool type
        
        if tool_name == "web_search":
            return {
                "results": [
                    {"title": "Mock Result 1", "url": "https://example.com/1", "snippet": "Mock content 1"},
                    {"title": "Mock Result 2", "url": "https://example.com/2", "snippet": "Mock content 2"}
                ],
                "total_results": 2
            }
        elif tool_name == "file_read":
            return {
                "content": "Mock file content",
                "size_bytes": 100,
                "last_modified": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {"message": f"Mock result from {tool_name}", "parameters": parameters}

# Global instances
_tool_registry = None
_permissions_engine = None
_execution_guard = None

def get_tool_registry() -> ToolRegistry:
    """Get global tool registry instance"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry

def get_permissions_engine() -> ToolPermissionsEngine:
    """Get global permissions engine instance"""
    global _permissions_engine
    if _permissions_engine is None:
        _permissions_engine = ToolPermissionsEngine(get_tool_registry())
    return _permissions_engine

def get_execution_guard() -> ToolExecutionGuard:
    """Get global tool execution guard instance"""
    global _execution_guard
    if _execution_guard is None:
        _execution_guard = ToolExecutionGuard(get_permissions_engine())
    return _execution_guard
