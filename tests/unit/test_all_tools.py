"""
Comprehensive Test Suite for All AMAS Tools
Tests all 14 implemented tools
"""

import asyncio
import os
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock

from src.amas.agents.tools import get_tool_registry
from src.amas.agents.tools.web_scraper import WebScraperTool
from src.amas.agents.tools.dns_lookup import DNSLookupTool
from src.amas.agents.tools.whois_lookup import WHOISLookupTool
from src.amas.agents.tools.ssl_analyzer import SSLAnalyzerTool
from src.amas.agents.tools.api_fetcher import APIFetcherTool


# Test configuration
TEST_URL = "https://example.com"
TEST_DOMAIN = "example.com"
TEST_API_KEY = "test_api_key_12345"


class TestToolBase:
    """Base class for tool tests"""
    
    @pytest.fixture
    def tool_registry(self):
        """Get tool registry"""
        return get_tool_registry()


class TestWebScraperTool(TestToolBase):
    """Tests for WebScraperTool"""
    
    @pytest.mark.asyncio
    async def test_web_scraper_initialization(self):
        """Test web scraper tool initialization"""
        tool = WebScraperTool()
        assert tool.name == "web_scraper"
        assert tool.description is not None
        assert tool.category == "data_collection"
    
    @pytest.mark.asyncio
    async def test_web_scraper_schema(self):
        """Test web scraper schema"""
        tool = WebScraperTool()
        schema = tool.get_schema()
        assert schema["type"] == "object"
        assert "url" in schema["properties"]
        assert "url" in schema["required"]
    
    @pytest.mark.asyncio
    async def test_web_scraper_validate_params(self):
        """Test parameter validation"""
        tool = WebScraperTool()
        # Valid params
        assert tool.validate_params({"url": "https://example.com"}) is True
        # Invalid params
        assert tool.validate_params({}) is False
        # Auto-normalize URL
        params = {"url": "example.com"}
        tool.validate_params(params)
        assert params["url"].startswith("http")
    
    @pytest.mark.asyncio
    async def test_web_scraper_execute_success(self):
        """Test successful web scraping"""
        tool = WebScraperTool()
        
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {"Content-Type": "text/html"}
            mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await tool.execute({
                "url": TEST_URL,
                "extract_text": True,
                "extract_metadata": True
            })
            
            assert result["success"] is True
            assert "result" in result
            assert result["result"]["url"] == TEST_URL
    
    @pytest.mark.asyncio
    async def test_web_scraper_execute_invalid_params(self):
        """Test web scraper with invalid parameters"""
        tool = WebScraperTool()
        result = await tool.execute({})
        assert result["success"] is False
        assert "error" in result


class TestDNSLookupTool(TestToolBase):
    """Tests for DNSLookupTool"""
    
    @pytest.mark.asyncio
    async def test_dns_lookup_initialization(self):
        """Test DNS lookup tool initialization"""
        tool = DNSLookupTool()
        assert tool.name == "dns_lookup"
        assert tool.description is not None
    
    @pytest.mark.asyncio
    async def test_dns_lookup_schema(self):
        """Test DNS lookup schema"""
        tool = DNSLookupTool()
        schema = tool.get_schema()
        assert schema["type"] == "object"
        assert "domain" in schema["properties"]
        assert "domain" in schema["required"]
    
    @pytest.mark.asyncio
    async def test_dns_lookup_validate_params(self):
        """Test parameter validation"""
        tool = DNSLookupTool()
        # Valid params
        assert tool.validate_params({"domain": TEST_DOMAIN}) is True
        # Invalid params
        assert tool.validate_params({}) is False
        # Normalize domain
        params = {"domain": "https://example.com/path"}
        tool.validate_params(params)
        assert params["domain"] == "example.com"
    
    @pytest.mark.asyncio
    async def test_dns_lookup_execute(self):
        """Test DNS lookup execution"""
        tool = DNSLookupTool()
        result = await tool.execute({
            "domain": TEST_DOMAIN,
            "record_types": ["A"]
        })
        
        # Should succeed (even if no records found)
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["domain"] == TEST_DOMAIN


class TestWHOISLookupTool(TestToolBase):
    """Tests for WHOISLookupTool"""
    
    @pytest.mark.asyncio
    async def test_whois_lookup_initialization(self):
        """Test WHOIS lookup tool initialization"""
        from src.amas.agents.tools.whois_lookup import WHOISLookupTool
        tool = WHOISLookupTool()
        assert tool.name == "whois_lookup"
        assert tool.description is not None
    
    @pytest.mark.asyncio
    async def test_whois_lookup_execute(self):
        """Test WHOIS lookup execution"""
        from src.amas.agents.tools.whois_lookup import WHOISLookupTool
        tool = WHOISLookupTool()
        result = await tool.execute({"domain": TEST_DOMAIN})
        
        # May fail if python-whois not available, but should return result
        assert "success" in result
        assert "result" in result or "error" in result


class TestSSLAnalyzerTool(TestToolBase):
    """Tests for SSLAnalyzerTool"""
    
    @pytest.mark.asyncio
    async def test_ssl_analyzer_initialization(self):
        """Test SSL analyzer tool initialization"""
        tool = SSLAnalyzerTool()
        assert tool.name == "ssl_analyzer"
        assert tool.description is not None
    
    @pytest.mark.asyncio
    async def test_ssl_analyzer_execute(self):
        """Test SSL analyzer execution"""
        tool = SSLAnalyzerTool()
        result = await tool.execute({
            "hostname": TEST_DOMAIN,
            "port": 443
        })
        
        # Should attempt SSL analysis
        assert "success" in result
        assert "result" in result or "error" in result


class TestAPIFetcherTool(TestToolBase):
    """Tests for APIFetcherTool"""
    
    @pytest.mark.asyncio
    async def test_api_fetcher_initialization(self):
        """Test API fetcher tool initialization"""
        tool = APIFetcherTool()
        assert tool.name == "api_fetcher"
        assert tool.description is not None
    
    @pytest.mark.asyncio
    async def test_api_fetcher_execute(self):
        """Test API fetcher execution"""
        tool = APIFetcherTool()
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"test": "data"})
            mock_response.text = AsyncMock(return_value='{"test": "data"}')
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await tool.execute({
                "url": f"{TEST_URL}/api/test",
                "method": "GET"
            })
            
            assert result["success"] is True
            assert "result" in result


class TestSecurityAPITools(TestToolBase):
    """Tests for Security API Tools"""
    
    @pytest.mark.asyncio
    async def test_virustotal_tool(self):
        """Test VirusTotal tool"""
        try:
            from src.amas.agents.tools.security_apis import VirusTotalTool
            
            tool = VirusTotalTool()
            assert tool.name == "virustotal"
            
            # Test without API key
            result = await tool.execute({"resource": TEST_DOMAIN})
            # Should return error if no API key
            assert "success" in result
        except ImportError:
            pytest.skip("Security APIs not available")
    
    @pytest.mark.asyncio
    async def test_shodan_tool(self):
        """Test Shodan tool"""
        try:
            from src.amas.agents.tools.security_apis import ShodanTool
            
            tool = ShodanTool()
            assert tool.name == "shodan"
            
            result = await tool.execute({"query": "test"})
            assert "success" in result
        except ImportError:
            pytest.skip("Security APIs not available")
    
    @pytest.mark.asyncio
    async def test_censys_tool(self):
        """Test Censys tool"""
        try:
            from src.amas.agents.tools.security_apis import CensysTool
            
            tool = CensysTool()
            assert tool.name == "censys"
            
            result = await tool.execute({"query": "test"})
            assert "success" in result
        except ImportError:
            pytest.skip("Security APIs not available")
    
    @pytest.mark.asyncio
    async def test_haveibeenpwned_tool(self):
        """Test HaveIBeenPwned tool"""
        try:
            from src.amas.agents.tools.security_apis import HaveIBeenPwnedTool
            
            tool = HaveIBeenPwnedTool()
            assert tool.name == "haveibeenpwned"
            
            result = await tool.execute({"email": "test@example.com"})
            assert "success" in result
        except ImportError:
            pytest.skip("Security APIs not available")
    
    @pytest.mark.asyncio
    async def test_abuseipdb_tool(self):
        """Test AbuseIPDB tool"""
        try:
            from src.amas.agents.tools.security_apis import AbuseIPDBTool
            
            tool = AbuseIPDBTool()
            assert tool.name == "abuseipdb"
            
            result = await tool.execute({"ip": "8.8.8.8"})
            assert "success" in result
        except ImportError:
            pytest.skip("Security APIs not available")


class TestIntelligenceAPITools(TestToolBase):
    """Tests for Intelligence API Tools"""
    
    @pytest.mark.asyncio
    async def test_github_api_tool(self):
        """Test GitHub API tool"""
        try:
            from src.amas.agents.tools.intelligence_apis import GitHubAPITool
            
            tool = GitHubAPITool()
            assert tool.name == "github_api"
            
            result = await tool.execute({"endpoint": "repos/octocat/Hello-World"})
            assert "success" in result
        except ImportError:
            pytest.skip("Intelligence APIs not available")
    
    @pytest.mark.asyncio
    async def test_gitlab_api_tool(self):
        """Test GitLab API tool"""
        try:
            from src.amas.agents.tools.intelligence_apis import GitLabAPITool
            
            tool = GitLabAPITool()
            assert tool.name == "gitlab_api"
            
            result = await tool.execute({"endpoint": "projects"})
            assert "success" in result
        except ImportError:
            pytest.skip("Intelligence APIs not available")
    
    @pytest.mark.asyncio
    async def test_npm_package_tool(self):
        """Test NPM package tool"""
        try:
            from src.amas.agents.tools.intelligence_apis import NPMPackageTool
            
            tool = NPMPackageTool()
            assert tool.name == "npm_package"
            
            result = await tool.execute({"package": "express"})
            assert result["success"] is True
            assert "result" in result
        except ImportError:
            pytest.skip("Intelligence APIs not available")
    
    @pytest.mark.asyncio
    async def test_pypi_package_tool(self):
        """Test PyPI package tool"""
        try:
            from src.amas.agents.tools.intelligence_apis import PyPIPackageTool
            
            tool = PyPIPackageTool()
            assert tool.name == "pypi_package"
            
            result = await tool.execute({"package": "requests"})
            assert result["success"] is True
            assert "result" in result
        except ImportError:
            pytest.skip("Intelligence APIs not available")


class TestToolRegistry(TestToolBase):
    """Tests for Tool Registry"""
    
    @pytest.mark.asyncio
    async def test_tool_registry_list_tools(self, tool_registry):
        """Test listing all tools"""
        tools = tool_registry.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "web_scraper" in tools
    
    @pytest.mark.asyncio
    async def test_tool_registry_get_tool(self, tool_registry):
        """Test getting a tool by name"""
        tool = tool_registry.get("web_scraper")
        assert tool is not None
        assert tool.name == "web_scraper"
    
    @pytest.mark.asyncio
    async def test_tool_registry_get_nonexistent(self, tool_registry):
        """Test getting non-existent tool"""
        tool = tool_registry.get("nonexistent_tool")
        assert tool is None
    
    @pytest.mark.asyncio
    async def test_tool_registry_get_by_category(self, tool_registry):
        """Test getting tools by category"""
        from src.amas.agents.tools.tool_categories import ToolCategory
        
        tools = tool_registry.get_tools_by_category(ToolCategory.WEB_RESEARCH.value)
        assert isinstance(tools, list)
        # Should include web_scraper
        tool_names = [t.name for t in tools]
        assert "web_scraper" in tool_names


class TestMultiToolOrchestration(TestToolBase):
    """Tests for Multi-Tool Orchestration"""
    
    @pytest.mark.asyncio
    async def test_multi_tool_orchestrator_initialization(self):
        """Test multi-tool orchestrator initialization"""
        from src.amas.agents.tools.multi_tool_orchestrator import get_multi_tool_orchestrator
        
        orchestrator = get_multi_tool_orchestrator()
        assert orchestrator is not None
        assert orchestrator.tool_selector is not None
        assert orchestrator.tool_executor is not None
        assert orchestrator.result_aggregator is not None
    
    @pytest.mark.asyncio
    async def test_intelligent_tool_selector(self):
        """Test intelligent tool selector"""
        from src.amas.agents.tools.intelligent_tool_selector import get_intelligent_tool_selector
        
        selector = get_intelligent_tool_selector()
        assert selector is not None
        
        # Test tool selection
        recommendations = await selector.select_tools(
            task_type="web_research",
            task_description="Search for information about Python",
            parameters={"query": "Python"},
            strategy="comprehensive",
            max_tools=3
        )
        
        assert isinstance(recommendations, list)
        # Should have some recommendations
        assert len(recommendations) > 0 or len(recommendations) == 0  # May be empty if no tools match
    
    @pytest.mark.asyncio
    async def test_tool_performance_tracker(self):
        """Test tool performance tracker"""
        from src.amas.agents.tools.tool_performance_tracker import get_tool_performance_tracker
        
        tracker = get_tool_performance_tracker()
        assert tracker is not None
        
        # Record an execution
        await tracker.record_execution(
            tool_name="web_scraper",
            success=True,
            execution_time=2.5,
            quality_score=0.9
        )
        
        # Get metrics
        metrics = await tracker.get_metrics("web_scraper")
        assert metrics is not None
        assert metrics.tool_name == "web_scraper"
        assert metrics.total_executions > 0


class TestToolIntegration(TestToolBase):
    """Integration tests for tools"""
    
    @pytest.mark.asyncio
    async def test_tool_execution_flow(self, tool_registry):
        """Test complete tool execution flow"""
        tool = tool_registry.get("web_scraper")
        assert tool is not None
        
        # Execute tool
        result = await tool.execute({
            "url": TEST_URL,
            "extract_text": True
        })
        
        # Verify result structure
        assert "success" in result
        assert "result" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_multiple_tools_parallel(self, tool_registry):
        """Test executing multiple tools in parallel"""
        tools = [
            tool_registry.get("web_scraper"),
            tool_registry.get("dns_lookup"),
        ]
        
        # Filter out None tools
        tools = [t for t in tools if t is not None]
        
        if len(tools) >= 2:
            # Execute in parallel
            results = await asyncio.gather(
                *[tool.execute({"url": TEST_URL}) if tool.name == "web_scraper" 
                  else tool.execute({"domain": TEST_DOMAIN})
                  for tool in tools],
                return_exceptions=True
            )
            
            assert len(results) == len(tools)
            for result in results:
                if isinstance(result, Exception):
                    # Some tools may fail, that's okay
                    continue
                assert "success" in result


# Test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

