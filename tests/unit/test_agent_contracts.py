"""
Unit tests for Agent Contracts

Tests the base agent contract system, JSONSchema validation,
and contract enforcement.
"""

import pytest
import jsonschema
from datetime import datetime, timezone
from typing import Dict, Any

from amas.core.agent_contracts import (
    AgentContract,
    AgentRole,
    ToolCapability,
    ExecutionStatus,
    ExecutionContext,
    AgentExecution,
    ContractViolationError,
    ResearchAgentContract,
    WEB_RESEARCH_AGENT,
)


class TestAgentContract:
    """Test base agent contract functionality"""
    
    def test_contract_creation(self):
        """Test creating a basic contract"""
        contract = ResearchAgentContract(
            agent_id="test_agent_001",
            role=AgentRole.RESEARCH,
            allowed_tools=[ToolCapability.WEB_SEARCH, ToolCapability.FILE_READ]
        )
        
        assert contract.agent_id == "test_agent_001"
        assert contract.role == AgentRole.RESEARCH
        assert len(contract.allowed_tools) >= 2
        assert ToolCapability.WEB_SEARCH in contract.allowed_tools
    
    def test_contract_validation_empty_agent_id(self):
        """Test that empty agent ID is rejected"""
        with pytest.raises(ValueError, match="Agent ID cannot be empty"):
            ResearchAgentContract(
                agent_id="",
                role=AgentRole.RESEARCH,
                allowed_tools=[ToolCapability.WEB_SEARCH]
            )
    
    def test_contract_validation_no_tools(self):
        """Test that agent without tools is rejected"""
        with pytest.raises(ValueError, match="Agent must have at least one allowed tool"):
            ResearchAgentContract(
                agent_id="test_agent",
                role=AgentRole.RESEARCH,
                allowed_tools=[]
            )
    
    def test_can_use_tool(self):
        """Test tool permission checking"""
        contract = ResearchAgentContract(
            agent_id="test_agent",
            role=AgentRole.RESEARCH,
            allowed_tools=[ToolCapability.WEB_SEARCH, ToolCapability.FILE_READ]
        )
        
        assert contract.can_use_tool(ToolCapability.WEB_SEARCH) is True
        assert contract.can_use_tool("web_search") is True
        assert contract.can_use_tool(ToolCapability.FILE_WRITE) is False
    
    def test_contract_manifest(self):
        """Test contract manifest generation"""
        contract = ResearchAgentContract(
            agent_id="test_agent_manifest",
            role=AgentRole.RESEARCH,
            allowed_tools=[ToolCapability.WEB_SEARCH]
        )
        
        manifest = contract.to_manifest()
        
        assert manifest["agent_id"] == "test_agent_manifest"
        assert manifest["role"] == "research"
        assert "input_schema" in manifest
        assert "output_schema" in manifest
        assert "allowed_tools" in manifest
        assert "constraints" in manifest
        assert "quality_gates" in manifest


class TestResearchAgentContract:
    """Test research agent contract specifics"""
    
    def test_research_contract_defaults(self):
        """Test research agent default values"""
        contract = ResearchAgentContract(
            agent_id="research_test",
            role=AgentRole.RESEARCH,
            allowed_tools=[ToolCapability.WEB_SEARCH]
        )
        
        assert contract.max_iterations == 8
        assert contract.timeout_seconds == 600
        assert contract.cost_budget_tokens == 20000
        assert contract.fact_checking_enabled is True
        assert contract.source_diversity_required is True
    
    def test_research_input_schema(self):
        """Test research agent input schema validation"""
        contract = ResearchAgentContract(
            agent_id="research_schema_test",
            role=AgentRole.RESEARCH,
            allowed_tools=[ToolCapability.WEB_SEARCH]
        )
        
        schema = contract.get_input_schema()
        
        # Valid input
        valid_input = {
            "query": "What is artificial intelligence?",
            "research_scope": "broad",
            "max_sources": 10
        }
        is_valid, error = contract.validate_input(valid_input)
        assert is_valid is True
        assert error is None
        
        # Invalid input - missing required field
        invalid_input = {
            "research_scope": "broad"
        }
        is_valid, error = contract.validate_input(invalid_input)
        assert is_valid is False
        assert "query" in error.lower() or "required" in error.lower()
        
        # Invalid input - query too short
        invalid_input2 = {
            "query": "AI"  # Too short
        }
        is_valid, error = contract.validate_input(invalid_input2)
        assert is_valid is False
    
    def test_research_output_schema(self):
        """Test research agent output schema validation"""
        contract = ResearchAgentContract(
            agent_id="research_output_test",
            role=AgentRole.RESEARCH,
            allowed_tools=[ToolCapability.WEB_SEARCH]
        )
        
        schema = contract.get_output_schema()
        
        # Valid output
        valid_output = {
            "research_summary": "This is a comprehensive summary of research findings that contains at least 100 characters to meet the minimum length requirement.",
            "key_findings": [
                {
                    "finding": "Finding 1: Important discovery",
                    "confidence_level": "high",
                    "supporting_sources": ["https://example.com/source1"]
                }
            ],
            "sources": [
                {
                    "url": "https://example.com/source1",
                    "title": "Source Title",
                    "domain": "academic",
                    "credibility_score": 0.9,
                    "relevance_score": 0.8
                },
                {
                    "url": "https://example.com/source2",
                    "title": "Source Title 2",
                    "domain": "news",
                    "credibility_score": 0.85,
                    "relevance_score": 0.75
                },
                {
                    "url": "https://example.com/source3",
                    "title": "Source Title 3",
                    "domain": "industry",
                    "credibility_score": 0.8,
                    "relevance_score": 0.7
                }
            ],
            "confidence_assessment": {
                "overall_confidence": "high",
                "data_completeness": 0.9,
                "source_diversity": 0.85
            },
            "execution_metrics": {
                "search_queries_executed": 5,
                "api_calls_made": 3,
                "tokens_consumed": 5000,
                "processing_time_seconds": 120.5,
                "cache_hit_rate": 0.3
            }
        }
        
        is_valid, error = contract.validate_output(valid_output)
        assert is_valid is True
        assert error is None
        
        # Invalid output - missing required field
        invalid_output = {
            "research_summary": "Summary",
            "key_findings": []
        }
        is_valid, error = contract.validate_output(invalid_output)
        assert is_valid is False
        assert "sources" in error.lower() or "required" in error.lower()
    
    def test_preconfigured_agents(self):
        """Test pre-configured research agent instances"""
        assert WEB_RESEARCH_AGENT.agent_id == "web_research_v1"
        assert WEB_RESEARCH_AGENT.max_search_results == 25
        assert WEB_RESEARCH_AGENT.search_depth == "comprehensive"
        assert WEB_RESEARCH_AGENT.fact_checking_enabled is True


class TestExecutionContext:
    """Test execution context functionality"""
    
    def test_execution_context_creation(self):
        """Test creating execution context"""
        context = ExecutionContext(
            user_id="user123",
            trace_id="trace456",
            priority=7
        )
        
        assert context.user_id == "user123"
        assert context.trace_id == "trace456"
        assert context.priority == 7
        assert context.execution_id is not None
        assert isinstance(context.started_at, datetime)
    
    def test_execution_context_defaults(self):
        """Test execution context defaults"""
        context = ExecutionContext()
        
        assert context.priority == 5
        assert context.max_memory_mb == 512
        assert context.max_cpu_cores == 1.0
        assert context.environment == "production"


class TestAgentExecution:
    """Test agent execution tracking"""
    
    def test_execution_creation(self):
        """Test creating execution record"""
        context = ExecutionContext(user_id="user123")
        execution = AgentExecution(
            execution_id="exec001",
            agent_id="agent001",
            context=context,
            input_data={"query": "test query"}
        )
        
        assert execution.execution_id == "exec001"
        assert execution.agent_id == "agent001"
        assert execution.status == ExecutionStatus.PENDING
        assert execution.input_data == {"query": "test query"}
    
    def test_execution_completion(self):
        """Test marking execution as completed"""
        context = ExecutionContext()
        execution = AgentExecution(
            execution_id="exec002",
            agent_id="agent001",
            context=context,
            input_data={}
        )
        
        execution.mark_completed(
            output_data={"result": "success"},
            tokens_used=5000
        )
        
        assert execution.status == ExecutionStatus.COMPLETED
        assert execution.output_data == {"result": "success"}
        assert execution.tokens_used == 5000
        assert execution.completed_at is not None
        assert execution.duration_seconds is not None
    
    def test_execution_failure(self):
        """Test marking execution as failed"""
        context = ExecutionContext()
        execution = AgentExecution(
            execution_id="exec003",
            agent_id="agent001",
            context=context,
            input_data={}
        )
        
        execution.mark_failed("Test error message")
        
        assert execution.status == ExecutionStatus.FAILED
        assert execution.error_message == "Test error message"
        assert execution.completed_at is not None
    
    def test_tool_call_tracking(self):
        """Test tracking tool calls"""
        context = ExecutionContext()
        execution = AgentExecution(
            execution_id="exec004",
            agent_id="agent001",
            context=context,
            input_data={}
        )
        
        execution.add_tool_call(
            tool_name="web_search",
            parameters={"query": "test"},
            result={"results": ["result1", "result2"]}
        )
        
        assert len(execution.tool_calls) == 1
        assert execution.tool_calls[0]["tool"] == "web_search"
        assert execution.tool_calls[0]["parameters"] == {"query": "test"}


class TestContractViolationError:
    """Test contract violation errors"""
    
    def test_contract_violation_error(self):
        """Test contract violation error creation"""
        error = ContractViolationError(
            agent_id="agent001",
            violation_type="tool_access_denied",
            details="Access denied to file_write"
        )
        
        assert error.agent_id == "agent001"
        assert error.violation_type == "tool_access_denied"
        assert error.details == "Access denied to file_write"
        assert "agent001" in str(error)
        assert "tool_access_denied" in str(error)


class TestContractIntegration:
    """Integration tests for contract system"""
    
    def test_full_contract_workflow(self):
        """Test complete contract validation workflow"""
        # Create contract
        contract = ResearchAgentContract(
            agent_id="integration_test",
            role=AgentRole.RESEARCH,
            allowed_tools=[ToolCapability.WEB_SEARCH]
        )
        
        # Create execution context
        context = ExecutionContext(
            user_id="test_user",
            trace_id="trace123"
        )
        
        # Create execution
        execution = AgentExecution(
            execution_id="exec_integration",
            agent_id="integration_test",
            context=context,
            input_data={
                "query": "Test integration query that is long enough to pass validation",
                "research_scope": "focused"
            }
        )
        
        # Validate input
        is_valid, error = contract.validate_input(execution.input_data)
        assert is_valid is True
        
        # Simulate tool call
        execution.add_tool_call(
            tool_name="web_search",
            parameters={"query": execution.input_data["query"]},
            result={"results": []}
        )
        
        # Validate output
        output_data = {
            "research_summary": "This is a test summary that meets the minimum length requirement of 100 characters to pass validation.",
            "key_findings": [
                {
                    "finding": "Finding 1: Test finding",
                    "confidence_level": "medium",
                    "supporting_sources": ["https://example.com"]
                }
            ],
            "sources": [
                {
                    "url": "https://example.com",
                    "title": "Example Source",
                    "domain": "academic",
                    "credibility_score": 0.8,
                    "relevance_score": 0.7
                },
                {
                    "url": "https://example2.com",
                    "title": "Example Source 2",
                    "domain": "news",
                    "credibility_score": 0.75,
                    "relevance_score": 0.65
                },
                {
                    "url": "https://example3.com",
                    "title": "Example Source 3",
                    "domain": "industry",
                    "credibility_score": 0.7,
                    "relevance_score": 0.6
                }
            ],
            "confidence_assessment": {
                "overall_confidence": "medium",
                "data_completeness": 0.8,
                "source_diversity": 0.75
            },
            "execution_metrics": {
                "search_queries_executed": 3,
                "api_calls_made": 2,
                "tokens_consumed": 3000,
                "processing_time_seconds": 60.0,
                "cache_hit_rate": 0.2
            }
        }
        
        is_valid, error = contract.validate_output(output_data)
        assert is_valid is True
        
        # Mark execution as completed
        execution.mark_completed(output_data, tokens_used=3000)
        
        assert execution.status == ExecutionStatus.COMPLETED
        assert len(execution.tool_calls) == 1
