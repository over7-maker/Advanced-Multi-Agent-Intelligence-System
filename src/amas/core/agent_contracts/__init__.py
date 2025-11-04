"""
Agent Contracts Module

Provides typed contracts for all AMAS agents with JSONSchema validation.
"""

from .base_agent_contract import (
    AgentContract,
    AgentRole,
    ToolCapability,
    ExecutionStatus,
    ExecutionContext,
    AgentExecution,
    ContractViolationError,
)

from .research_agent_schema import (
    ResearchAgentContract,
    WEB_RESEARCH_AGENT,
    ACADEMIC_RESEARCH_AGENT,
    NEWS_RESEARCH_AGENT,
)

__all__ = [
    "AgentContract",
    "AgentRole",
    "ToolCapability",
    "ExecutionStatus",
    "ExecutionContext",
    "AgentExecution",
    "ContractViolationError",
    "ResearchAgentContract",
    "WEB_RESEARCH_AGENT",
    "ACADEMIC_RESEARCH_AGENT",
    "NEWS_RESEARCH_AGENT",
]
