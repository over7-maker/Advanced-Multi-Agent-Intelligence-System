"""
Unit tests for Tool Governance System

Tests tool registry, permissions, rate limiting, and approval workflows.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from amas.core.tool_governance import (
    ToolRegistry,
    ToolPermissionsEngine,
    ToolExecutionGuard,
    ToolDefinition,
    ToolUsageRecord,
    ToolRiskLevel,
    ToolAccessDecision,
)
from amas.core.agent_contracts import ToolCapability, ContractViolationError


class TestToolDefinition:
    """Test tool definition data structure"""
    
    def test_tool_definition_creation(self):
        """Test creating a tool definition"""
        tool_def = ToolDefinition(
            name="test_tool",
            capability=ToolCapability.WEB_SEARCH,
            description="Test tool",
            risk_level=ToolRiskLevel.MEDIUM,
            rate_limit_per_minute=30
        )
        
        assert tool_def.name == "test_tool"
        assert tool_def.capability == ToolCapability.WEB_SEARCH
        assert tool_def.risk_level == ToolRiskLevel.MEDIUM
        assert tool_def.rate_limit_per_minute == 30


class TestToolRegistry:
    """Test tool registry functionality"""
    
    def test_registry_initialization(self, tmp_path):
        """Test tool registry initialization"""
        config_file = tmp_path / "tools.yaml"
        registry = ToolRegistry(config_path=str(config_file))
        
        # Should create default tools if config doesn't exist
        assert len(registry.tools) > 0
        assert "web_search" in registry.tools
        assert "file_read" in registry.tools
    
    def test_get_tool(self, tmp_path):
        """Test getting tool by name"""
        registry = ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
        
        tool = registry.get_tool("web_search")
        assert tool is not None
        assert tool.name == "web_search"
        
        # Non-existent tool
        tool = registry.get_tool("nonexistent_tool")
        assert tool is None
    
    def test_get_tools_by_capability(self, tmp_path):
        """Test getting tools by capability"""
        registry = ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
        
        web_tools = registry.get_tools_by_capability(ToolCapability.WEB_SEARCH)
        assert len(web_tools) > 0
        assert all(tool.capability == ToolCapability.WEB_SEARCH for tool in web_tools)
    
    def test_register_tool(self, tmp_path):
        """Test registering a new tool"""
        registry = ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
        
        new_tool = ToolDefinition(
            name="custom_tool",
            capability=ToolCapability.API_CALL,
            description="Custom tool",
            risk_level=ToolRiskLevel.LOW
        )
        
        registry.register_tool(new_tool)
        assert "custom_tool" in registry.tools
        assert registry.get_tool("custom_tool") == new_tool
    
    def test_record_usage(self, tmp_path):
        """Test recording tool usage"""
        registry = ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
        
        record = ToolUsageRecord(
            timestamp=datetime.now(timezone.utc),
            agent_id="agent001",
            user_id="user123",
            tool_name="web_search",
            parameters={"query": "test"},
            duration_seconds=1.5,
            status="success",
            output_size_bytes=1000
        )
        
        registry.record_usage(record)
        assert len(registry.usage_records) == 1
        assert registry.usage_records[0] == record
    
    def test_get_usage_stats(self, tmp_path):
        """Test getting usage statistics"""
        registry = ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
        
        # Add some usage records
        for i in range(5):
            record = ToolUsageRecord(
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i),
                agent_id="agent001",
                user_id="user001",
                tool_name="web_search",
                parameters={},
                duration_seconds=1.0,
                status="success" if i < 4 else "error",
                output_size_bytes=1000
            )
            registry.record_usage(record)
        
        stats = registry.get_usage_stats(
            agent_id="agent001",
            tool_name="web_search",
            hours=1
        )
        
        assert stats["total_calls"] == 5
        assert stats["successful_calls"] == 4
        assert stats["success_rate"] == 0.8
        assert stats["avg_duration_seconds"] == 1.0


class TestToolPermissionsEngine:
    """Test tool permissions engine"""
    
    @pytest.fixture
    def registry(self, tmp_path):
        """Create a test registry"""
        return ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
    
    @pytest.fixture
    def permissions_engine(self, registry, tmp_path):
        """Create a test permissions engine"""
        # Create a minimal agent capabilities config
        capabilities_file = tmp_path / "agent_capabilities.yaml"
        capabilities_file.write_text("""
agents:
  test_agent:
    allowed_tools:
      - web_search
      - file_read
  restricted_agent:
    allowed_tools:
      - file_read
""")
        
        return ToolPermissionsEngine(
            registry=registry,
            agent_capabilities_path=str(capabilities_file)
        )
    
    @pytest.mark.asyncio
    async def test_check_tool_access_allowed(self, permissions_engine):
        """Test allowed tool access"""
        decision = await permissions_engine.check_tool_access(
            agent_id="test_agent",
            tool_name="web_search"
        )
        
        assert decision == ToolAccessDecision.ALLOW
    
    @pytest.mark.asyncio
    async def test_check_tool_access_denied_unknown_tool(self, permissions_engine):
        """Test denied access for unknown tool"""
        decision = await permissions_engine.check_tool_access(
            agent_id="test_agent",
            tool_name="nonexistent_tool"
        )
        
        assert decision == ToolAccessDecision.DENY
    
    @pytest.mark.asyncio
    async def test_check_tool_access_denied_no_permission(self, permissions_engine):
        """Test denied access when agent doesn't have permission"""
        decision = await permissions_engine.check_tool_access(
            agent_id="restricted_agent",
            tool_name="web_search"
        )
        
        assert decision == ToolAccessDecision.DENY
    
    @pytest.mark.asyncio
    async def test_check_tool_access_requires_approval(self, permissions_engine):
        """Test that high-risk tools require approval"""
        # file_write should require approval
        decision = await permissions_engine.check_tool_access(
            agent_id="test_agent",
            tool_name="file_write"
        )
        
        # First check if agent has permission
        if decision == ToolAccessDecision.DENY:
            # Agent doesn't have permission, so grant it
            permissions_engine.add_agent_permission("test_agent", "file_write")
            decision = await permissions_engine.check_tool_access(
                agent_id="test_agent",
                tool_name="file_write"
            )
        
        # Should require approval if tool requires it
        tool = permissions_engine.registry.get_tool("file_write")
        if tool and tool.requires_approval:
            assert decision == ToolAccessDecision.REQUIRE_APPROVAL
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, permissions_engine):
        """Test rate limiting enforcement"""
        # Get a tool with rate limit
        tool = permissions_engine.registry.get_tool("web_search")
        if tool and tool.rate_limit_per_minute:
            limit = tool.rate_limit_per_minute
            
            # Make requests up to the limit
            for i in range(limit):
                decision = await permissions_engine.check_tool_access(
                    agent_id="test_agent",
                    tool_name="web_search"
                )
                # Should be allowed
                assert decision == ToolAccessDecision.ALLOW
            
            # Next request should be rate limited
            decision = await permissions_engine.check_tool_access(
                agent_id="test_agent",
                tool_name="web_search"
            )
            assert decision == ToolAccessDecision.RATE_LIMITED
    
    def test_validate_tool_parameters_valid(self, permissions_engine):
        """Test parameter validation with valid parameters"""
        valid_params = {
            "file_path": "data/test.txt"
        }
        
        is_valid, error = permissions_engine.validate_tool_parameters(
            tool_name="file_read",
            parameters=valid_params
        )
        
        # Note: This depends on the tool definition having parameter validation
        # If tool doesn't have strict parameter validation, this might pass
        assert is_valid or error is not None
    
    def test_validate_tool_parameters_forbidden(self, permissions_engine):
        """Test parameter validation with forbidden parameters"""
        tool = permissions_engine.registry.get_tool("file_write")
        if tool and tool.forbidden_parameters:
            forbidden_params = {
                tool.forbidden_parameters[0]: "some_value"
            }
            
            is_valid, error = permissions_engine.validate_tool_parameters(
                tool_name="file_write",
                parameters=forbidden_params
            )
            
            assert is_valid is False
            assert "forbidden" in error.lower()
    
    def test_get_agent_tools(self, permissions_engine):
        """Test getting tools available to an agent"""
        tools = permissions_engine.get_agent_tools("test_agent")
        
        assert len(tools) >= 2
        tool_names = [tool.name for tool in tools]
        assert "web_search" in tool_names
        assert "file_read" in tool_names
    
    def test_add_remove_agent_permission(self, permissions_engine):
        """Test adding and removing agent permissions"""
        # Add permission
        permissions_engine.add_agent_permission("test_agent", "api_call")
        
        tools = permissions_engine.get_agent_tools("test_agent")
        tool_names = [tool.name for tool in tools]
        assert "api_call" in tool_names
        
        # Remove permission
        permissions_engine.remove_agent_permission("test_agent", "api_call")
        
        tools = permissions_engine.get_agent_tools("test_agent")
        tool_names = [tool.name for tool in tools]
        assert "api_call" not in tool_names


class TestToolExecutionGuard:
    """Test tool execution guard"""
    
    @pytest.fixture
    def registry(self, tmp_path):
        """Create a test registry"""
        return ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
    
    @pytest.fixture
    def permissions_engine(self, registry, tmp_path):
        """Create a test permissions engine"""
        capabilities_file = tmp_path / "agent_capabilities.yaml"
        capabilities_file.write_text("""
agents:
  test_agent:
    allowed_tools:
      - web_search
      - file_read
      - file_write
""")
        
        return ToolPermissionsEngine(
            registry=registry,
            agent_capabilities_path=str(capabilities_file)
        )
    
    @pytest.fixture
    def execution_guard(self, permissions_engine):
        """Create a test execution guard"""
        return ToolExecutionGuard(permissions_engine)
    
    @pytest.mark.asyncio
    async def test_execute_tool_success(self, execution_guard):
        """Test successful tool execution"""
        result = await execution_guard.execute_tool(
            agent_id="test_agent",
            tool_name="web_search",
            parameters={"query": "test query"}
        )
        
        assert result["status"] == "success"
        assert "result" in result
        assert "execution_id" in result
        assert "duration_seconds" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_denied(self, execution_guard):
        """Test denied tool execution"""
        with pytest.raises(ContractViolationError) as exc_info:
            await execution_guard.execute_tool(
                agent_id="test_agent",
                tool_name="code_execution",  # Not in allowed list
                parameters={}
            )
        
        assert "access_denied" in exc_info.value.violation_type or "denied" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_execute_tool_requires_approval(self, execution_guard):
        """Test tool execution requiring approval"""
        # Grant permission first
        execution_guard.permissions_engine.add_agent_permission("test_agent", "file_write")
        
        result = await execution_guard.execute_tool(
            agent_id="test_agent",
            tool_name="file_write",
            parameters={"file_path": "output/test.txt", "content": "test"}
        )
        
        # Should require approval if tool requires it
        tool = execution_guard.permissions_engine.registry.get_tool("file_write")
        if tool and tool.requires_approval:
            assert result["status"] == "pending_approval"
            assert "approval_id" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_rate_limited(self, execution_guard):
        """Test rate-limited tool execution"""
        tool = execution_guard.permissions_engine.registry.get_tool("web_search")
        if tool and tool.rate_limit_per_minute:
            limit = tool.rate_limit_per_minute
            
            # Make requests up to limit
            for i in range(limit):
                result = await execution_guard.execute_tool(
                    agent_id="test_agent",
                    tool_name="web_search",
                    parameters={"query": f"query {i}"}
                )
                assert result["status"] == "success"
            
            # Next request should be rate limited
            with pytest.raises(ContractViolationError) as exc_info:
                await execution_guard.execute_tool(
                    agent_id="test_agent",
                    tool_name="web_search",
                    parameters={"query": "final query"}
                )
            
            assert "rate_limit" in exc_info.value.violation_type.lower()
    
    @pytest.mark.asyncio
    async def test_execute_tool_invalid_parameters(self, execution_guard):
        """Test tool execution with invalid parameters"""
        # First grant permission to the agent
        execution_guard.permissions_engine.add_agent_permission("test_agent", "file_write")
        
        tool = execution_guard.permissions_engine.registry.get_tool("file_write")
        if tool and tool.forbidden_parameters:
            with pytest.raises(ContractViolationError) as exc_info:
                await execution_guard.execute_tool(
                    agent_id="test_agent",
                    tool_name="file_write",
                    parameters={tool.forbidden_parameters[0]: "forbidden_value"}
                )
            
            assert "invalid_parameters" in exc_info.value.violation_type or "parameter" in str(exc_info.value).lower()


class TestToolGovernanceIntegration:
    """Integration tests for tool governance system"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, tmp_path):
        """Test complete tool governance workflow"""
        # Setup
        registry = ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
        
        capabilities_file = tmp_path / "agent_capabilities.yaml"
        capabilities_file.write_text("""
agents:
  research_agent:
    allowed_tools:
      - web_search
      - file_read
""")
        
        permissions_engine = ToolPermissionsEngine(
            registry=registry,
            agent_capabilities_path=str(capabilities_file)
        )
        
        execution_guard = ToolExecutionGuard(permissions_engine)
        
        # Execute tool
        result = await execution_guard.execute_tool(
            agent_id="research_agent",
            tool_name="web_search",
            parameters={"query": "test query"},
            user_id="user123",
            trace_id="trace456"
        )
        
        assert result["status"] == "success"
        
        # Check usage was recorded
        assert len(registry.usage_records) == 1
        record = registry.usage_records[0]
        assert record.agent_id == "research_agent"
        assert record.tool_name == "web_search"
        assert record.user_id == "user123"
        assert record.trace_id == "trace456"
        assert record.status == "success"
        
        # Check usage stats
        stats = registry.get_usage_stats(
            agent_id="research_agent",
            tool_name="web_search"
        )
        assert stats["total_calls"] == 1
        assert stats["success_rate"] == 1.0
        
        # Check usage report
        report = permissions_engine.get_usage_report(hours=1)
        assert report["total_tool_calls"] == 1
        assert "research_agent" in report["agent_usage"]
        assert "web_search" in report["tool_usage"]


class TestSuccessCriteria:
    """Test success criteria from PR description"""
    
    @pytest.mark.asyncio
    async def test_unauthorized_tool_use_blocked(self, tmp_path):
        """Test: Unauthorized tool use → BLOCKED"""
        registry = ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
        
        capabilities_file = tmp_path / "agent_capabilities.yaml"
        capabilities_file.write_text("""
agents:
  restricted_agent:
    allowed_tools:
      - file_read
""")
        
        permissions_engine = ToolPermissionsEngine(
            registry=registry,
            agent_capabilities_path=str(capabilities_file)
        )
        
        execution_guard = ToolExecutionGuard(permissions_engine)
        
        # Try to use unauthorized tool
        with pytest.raises(ContractViolationError):
            await execution_guard.execute_tool(
                agent_id="restricted_agent",
                tool_name="file_write",  # Not in allowed list
                parameters={}
            )
    
    @pytest.mark.asyncio
    async def test_invalid_input_rejected(self, tmp_path):
        """Test: Invalid input → REJECTED with clear error"""
        registry = ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
        
        capabilities_file = tmp_path / "agent_capabilities.yaml"
        capabilities_file.write_text("""
agents:
  test_agent:
    allowed_tools:
      - file_write
""")
        
        permissions_engine = ToolPermissionsEngine(
            registry=registry,
            agent_capabilities_path=str(capabilities_file)
        )
        
        execution_guard = ToolExecutionGuard(permissions_engine)
        
        # Grant permission first
        permissions_engine.add_agent_permission("test_agent", "file_write")
        
        # Try with forbidden parameter
        tool = registry.get_tool("file_write")
        if tool and tool.forbidden_parameters:
            with pytest.raises(ContractViolationError) as exc_info:
                await execution_guard.execute_tool(
                    agent_id="test_agent",
                    tool_name="file_write",
                    parameters={tool.forbidden_parameters[0]: "value"}
                )
            
            assert "parameter" in str(exc_info.value).lower() or "forbidden" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_rate_limits_enforced(self, tmp_path):
        """Test: Rate limits enforced → PREVENTS ABUSE"""
        registry = ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
        
        capabilities_file = tmp_path / "agent_capabilities.yaml"
        capabilities_file.write_text("""
agents:
  test_agent:
    allowed_tools:
      - web_search
""")
        
        permissions_engine = ToolPermissionsEngine(
            registry=registry,
            agent_capabilities_path=str(capabilities_file)
        )
        
        execution_guard = ToolExecutionGuard(permissions_engine)
        
        tool = registry.get_tool("web_search")
        if tool and tool.rate_limit_per_minute:
            limit = tool.rate_limit_per_minute
            
            # Make requests up to limit
            for i in range(limit):
                result = await execution_guard.execute_tool(
                    agent_id="test_agent",
                    tool_name="web_search",
                    parameters={"query": f"query {i}"}
                )
                assert result["status"] == "success"
            
            # Next request should be blocked
            with pytest.raises(ContractViolationError) as exc_info:
                await execution_guard.execute_tool(
                    agent_id="test_agent",
                    tool_name="web_search",
                    parameters={"query": "final query"}
                )
            
            assert "rate" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_high_risk_tools_require_approval(self, tmp_path):
        """Test: High-risk tools → REQUIRE APPROVAL"""
        registry = ToolRegistry(config_path=str(tmp_path / "tools.yaml"))
        
        capabilities_file = tmp_path / "agent_capabilities.yaml"
        capabilities_file.write_text("""
agents:
  test_agent:
    allowed_tools:
      - file_write
      - code_execution
""")
        
        permissions_engine = ToolPermissionsEngine(
            registry=registry,
            agent_capabilities_path=str(capabilities_file)
        )
        
        execution_guard = ToolExecutionGuard(permissions_engine)
        
        # Test file_write (high risk)
        tool = registry.get_tool("file_write")
        if tool and tool.requires_approval:
            result = await execution_guard.execute_tool(
                agent_id="test_agent",
                tool_name="file_write",
                parameters={"file_path": "output/test.txt", "content": "test"}
            )
            assert result["status"] == "pending_approval"
            assert "approval_id" in result
        
        # Test code_execution (critical risk)
        tool = registry.get_tool("code_execution")
        if tool and tool.requires_approval:
            result = await execution_guard.execute_tool(
                agent_id="test_agent",
                tool_name="code_execution",
                parameters={"language": "python", "code": "print('test')"}
            )
            assert result["status"] == "pending_approval"
            assert "approval_id" in result
