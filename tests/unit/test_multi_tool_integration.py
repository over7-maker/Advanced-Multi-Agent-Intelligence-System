"""
Test Multi-Tool Agent Integration
Verifies that all components work together correctly
"""

import pytest
from src.amas.agents.tools.multi_tool_orchestrator import get_multi_tool_orchestrator
from src.amas.agents.tools.intelligent_tool_selector import get_intelligent_tool_selector
from src.amas.agents.tools.multi_tool_executor import get_multi_tool_executor
from src.amas.agents.tools.result_aggregator import get_result_aggregator
from src.amas.agents.tools.tool_performance_tracker import get_tool_performance_tracker
from src.amas.agents.tools import get_tool_registry
from src.amas.agents.base_agent import BaseAgent


class TestMultiToolIntegration:
    """Test multi-tool system integration"""
    
    def test_all_components_initialized(self):
        """Test that all components can be initialized"""
        orchestrator = get_multi_tool_orchestrator()
        selector = get_intelligent_tool_selector()
        executor = get_multi_tool_executor()
        aggregator = get_result_aggregator()
        tracker = get_tool_performance_tracker()
        registry = get_tool_registry()
        
        assert orchestrator is not None
        assert selector is not None
        assert executor is not None
        assert aggregator is not None
        assert tracker is not None
        assert registry is not None
    
    def test_tool_registry_has_tools(self):
        """Test that tool registry has all 53 tools"""
        registry = get_tool_registry()
        tools = registry.list_tools()
        
        assert len(tools) == 53, f"Expected 53 tools, found {len(tools)}"
        assert "web_scraper" in tools
        assert "dns_lookup" in tools
        assert "agenticseek" in tools
        assert "fofa" in tools
        assert "robin" in tools
    
    @pytest.mark.asyncio
    async def test_tool_selection(self):
        """Test intelligent tool selection"""
        selector = get_intelligent_tool_selector()
        
        recommendations = await selector.select_tools(
            task_type="web_research",
            task_description="Research Python best practices",
            parameters={"query": "Python best practices"},
            strategy="comprehensive",
            max_tools=5,
            agent_type="web_research"
        )
        
        assert len(recommendations) > 0
        assert all(hasattr(r, 'tool_name') for r in recommendations)
        assert all(hasattr(r, 'confidence') for r in recommendations)
    
    @pytest.mark.asyncio
    async def test_agent_preferences(self):
        """Test agent-specific tool preferences"""
        selector = get_intelligent_tool_selector()
        
        # Test security expert preferences
        security_recs = await selector.select_tools(
            task_type="security_scan",
            task_description="Scan for vulnerabilities",
            parameters={},
            strategy="comprehensive",
            max_tools=5,
            agent_type="security_expert"
        )
        
        # Should prefer security tools
        tool_names = [r.tool_name for r in security_recs]
        security_tools = ["virustotal", "shodan", "censys", "nmap", "semgrep"]
        assert any(tool in tool_names for tool in security_tools), \
            f"Security expert should prefer security tools, got: {tool_names}"
    
    def test_base_agent_has_multi_tool(self):
        """Test that BaseAgent has multi-tool methods"""
        # Create a test agent
        class TestAgent(BaseAgent):
            async def _prepare_prompt(self, target: str, parameters: dict) -> str:
                return f"Test prompt for {target}"
            
            async def _parse_response(self, response: str) -> dict:
                return {"result": response}
        
        agent = TestAgent(
            agent_id="test",
            name="Test Agent",
            agent_type="test",
            system_prompt="Test"
        )
        
        # Check that multi-tool methods exist
        assert hasattr(agent, '_execute_tools_multi_tool')
        assert hasattr(agent, '_execute_tools')
        assert hasattr(agent, '_select_tools')
    
    @pytest.mark.asyncio
    async def test_orchestrator_workflow(self):
        """Test complete orchestrator workflow"""
        orchestrator = get_multi_tool_orchestrator()
        
        # Get recommendations only (don't execute to avoid external dependencies)
        recommendations = await orchestrator.get_tool_recommendations(
            task_type="web_research",
            task_description="Search for information",
            parameters={"query": "test"},
            agent_type="web_research",
            strategy="comprehensive",
            max_tools=3
        )
        
        assert len(recommendations) > 0
        assert all(hasattr(r, 'tool_name') for r in recommendations)

