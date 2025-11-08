"""
Agent Role Contracts
Defines JSON schemas for agent inputs, outputs, and allowed tools
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ToolSchema(BaseModel):
    """Schema for an allowed tool"""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict = Field(default_factory=dict, description="Tool parameters schema")
    requires_approval: bool = Field(
        default=False, description="Whether tool requires human approval"
    )


class AgentRoleContract(BaseModel):
    """Contract defining an agent role's capabilities and constraints"""

    role_name: str = Field(..., description="Agent role identifier")
    description: str = Field(..., description="Role description")
    allowed_tools: List[str] = Field(
        default_factory=list, description="List of allowed tool names"
    )
    input_schema: Dict = Field(
        default_factory=dict, description="JSON schema for role inputs"
    )
    output_schema: Dict = Field(
        default_factory=dict, description="JSON schema for role outputs"
    )
    side_effect_bounds: Dict = Field(
        default_factory=dict,
        description="Constraints on side effects (e.g., max_file_writes)",
    )
    requires_approval_for: List[str] = Field(
        default_factory=list,
        description="Tool names that require approval",
    )


# Predefined agent role contracts
AGENT_CONTRACTS: Dict[str, AgentRoleContract] = {
    "code_reviewer": AgentRoleContract(
        role_name="code_reviewer",
        description="Reviews code changes for quality and security",
        allowed_tools=[
            "code_analyzer",
            "linter",
            "security_scanner",
            "documentation_generator",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "code": {"type": "string"},
                "language": {"type": "string"},
                "context": {"type": "object"},
            },
            "required": ["code"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "issues": {
                    "type": "array",
                    "items": {"type": "object"},
                },
                "score": {"type": "number"},
                "recommendations": {"type": "array", "items": {"type": "string"}},
            },
        },
        side_effect_bounds={"max_file_reads": 100, "read_only": True},
    ),
    "security_auditor": AgentRoleContract(
        role_name="security_auditor",
        description="Performs security analysis and vulnerability scanning",
        allowed_tools=[
            "vulnerability_scanner",
            "code_analyzer",
            "dependency_auditor",
            "threat_modeler",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "target": {"type": "string"},
                "scan_type": {"type": "string"},
            },
            "required": ["target"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "vulnerabilities": {
                    "type": "array",
                    "items": {"type": "object"},
                },
                "severity": {"type": "string"},
                "recommendations": {"type": "array"},
            },
        },
        side_effect_bounds={"max_file_reads": 500, "read_only": True},
        requires_approval_for=["penetration_test"],
    ),
    "orchestrator": AgentRoleContract(
        role_name="orchestrator",
        description="Coordinates multi-agent workflows",
        allowed_tools=[
            "agent_dispatcher",
            "workflow_engine",
            "task_scheduler",
            "result_aggregator",
        ],
        input_schema={
            "type": "object",
            "properties": {
                "workflow": {"type": "object"},
                "agents": {"type": "array"},
            },
            "required": ["workflow"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "results": {"type": "object"},
                "metrics": {"type": "object"},
            },
        },
        side_effect_bounds={"max_concurrent_agents": 10},
    ),
    "admin": AgentRoleContract(
        role_name="admin",
        description="Full system access with approval for dangerous operations",
        allowed_tools=["*"],  # All tools allowed
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        side_effect_bounds={},
        requires_approval_for=["system_executor", "database_migrator"],
    ),
}


def validate_agent_action(
    role_name: str, tool_name: str, action_data: Dict
) -> tuple[bool, Optional[str]]:
    """Validate that an agent action conforms to its contract"""

    contract = AGENT_CONTRACTS.get(role_name)
    if not contract:
        return False, f"Unknown agent role: {role_name}"

    # Check if tool is allowed
    if "*" not in contract.allowed_tools and tool_name not in contract.allowed_tools:
        return False, f"Tool {tool_name} not allowed for role {role_name}"

    # Validate input schema if provided
    if contract.input_schema:
        try:
            from jsonschema import validate, ValidationError

            validate(instance=action_data, schema=contract.input_schema)
        except ImportError:
            # jsonschema not available, skip validation
            pass
        except ValidationError as e:
            return False, f"Input validation failed: {e.message}"

    # Check side effect bounds
    if "max_file_reads" in contract.side_effect_bounds:
        file_reads = action_data.get("file_reads", 0)
        if file_reads > contract.side_effect_bounds["max_file_reads"]:
            return (
                False,
                f"File reads ({file_reads}) exceed limit ({contract.side_effect_bounds['max_file_reads']})",
            )

    return True, None


def get_contract_for_role(role_name: str) -> Optional[AgentRoleContract]:
    """Get contract for a specific role"""
    return AGENT_CONTRACTS.get(role_name)


def list_all_roles() -> List[str]:
    """List all defined agent roles"""
    return list(AGENT_CONTRACTS.keys())
