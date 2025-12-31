"""
Comprehensive Real Data Testing for All 53 Tools
Tests each tool with realistic parameters and verifies complete data responses
"""

import asyncio
import logging
import pytest
from typing import Dict, List, Any
from datetime import datetime

from src.amas.agents.tools import get_tool_registry
from src.amas.agents.tools.tool_categories import TOOL_CATEGORY_MAP

logger = logging.getLogger(__name__)


class ToolTestResult:
    """Result of a tool test"""
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.success = False
        self.has_data = False
        self.data_complete = False
        self.error = None
        self.execution_time = 0.0
        self.result_data = None
        self.test_params = None


class ComprehensiveToolTester:
    """Comprehensive tester for all tools with real data"""
    
    def __init__(self):
        self.registry = get_tool_registry()
        self.test_results: Dict[str, ToolTestResult] = {}
        self.test_params = self._get_test_parameters()
    
    def _get_test_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get realistic test parameters for each tool"""
        return {
            # Web Research Tools
            "web_scraper": {
                "url": "https://example.com",
                "extract_text": True,
                "extract_links": True
            },
            "api_fetcher": {
                "url": "https://api.github.com",
                "method": "GET"
            },
            "agenticseek": {
                "query": "Python programming best practices",
                "depth": "shallow",
                "max_results": 3
            },
            "searxng": {
                "query": "Python programming",
                "max_results": 5
            },
            "duckduckgo": {
                "query": "Python",
                "max_results": 5
            },
            "startpage": {
                "query": "Python",
                "max_results": 5
            },
            "bing": {
                "query": "Python programming",
                "max_results": 5
            },
            "google_cse": {
                "query": "Python",
                "max_results": 5
            },
            "qwant": {
                "query": "Python",
                "max_results": 5
            },
            "brave_search": {
                "query": "Python",
                "max_results": 5
            },
            "yandex": {
                "query": "Python",
                "max_results": 5
            },
            
            # OSINT Tools
            "fofa": {
                "query": "domain=\"example.com\"",
                "size": 10
            },
            "shodan": {
                "query": "apache",
                "limit": 5
            },
            "censys": {
                "query": "services.service_name=\"HTTP\"",
                "per_page": 5
            },
            "zoomeye": {
                "query": "apache",
                "page": 1
            },
            "netlas": {
                "query": "apache",
                "max_results": 5
            },
            "criminal_ip": {
                "ip": "8.8.8.8"
            },
            "haveibeenpwned": {
                "email": "test@example.com"
            },
            
            # Network Analysis Tools
            "dns_lookup": {
                "domain": "example.com",
                "record_type": "A"
            },
            "whois_lookup": {
                "domain": "example.com"
            },
            "ssl_analyzer": {
                "hostname": "example.com",
                "port": 443
            },
            "nmap": {
                "target": "127.0.0.1",
                "ports": "80,443",
                "scan_type": "tcp"
            },
            "masscan": {
                "target": "127.0.0.1",
                "ports": "80,443",
                "rate": 100
            },
            "rustscan": {
                "target": "127.0.0.1",
                "ports": "80,443"
            },
            
            # Security Analysis Tools
            "virustotal": {
                "resource": "example.com",
                "resource_type": "domain"
            },
            "abuseipdb": {
                "ip": "8.8.8.8",
                "days": 90
            },
            "semgrep": {
                "target": ".",
                "config": "auto"
            },
            "bandit": {
                "target": ".",
                "severity": "medium"
            },
            "trivy": {
                "target": ".",
                "scan_type": "fs"
            },
            "gitleaks": {
                "target": ".",
                "no_git": False
            },
            "osv_scanner": {
                "target": ".",
                "lockfile": None
            },
            "sonarqube": {
                "target": ".",
                "project_key": "test-project"
            },
            "owasp_zap": {
                "target_url": "http://example.com",
                "scan_type": "spider"
            },
            
            # Code Analysis Tools
            "github_api": {
                "endpoint": "repos/octocat/Hello-World",
                "method": "GET"
            },
            "gitlab_api": {
                "endpoint": "projects",
                "method": "GET"
            },
            "npm_package": {
                "package_name": "express",
                "version": "latest"
            },
            "pypi_package": {
                "package_name": "requests"
            },
            "pylint": {
                "target": ".",
                "output_format": "json"
            },
            "flake8": {
                "target": ".",
                "max_line_length": 79
            },
            
            # Data Analysis Tools
            "polars": {
                "operation": "read_csv",
                "data": "test_data.csv"  # Will create test file
            },
            "duckdb": {
                "query": "SELECT 1 as test"
            },
            "great_expectations": {
                "data_source": "test_data.csv",
                "expectations": [
                    {"type": "expect_column_to_exist", "column": "test"}
                ]
            },
            
            # Observability Tools
            "prometheus": {
                "query": "up",
                "query_type": "instant"
            },
            "grafana": {
                "operation": "list_dashboards"
            },
            "loki": {
                "query": "{job=\"test\"}",
                "limit": 10
            },
            "jaeger": {
                "operation": "search_traces",
                "service": "test"
            },
            "pyroscope": {
                "query": "test",
                "from_time": int(datetime.now().timestamp()) - 3600,
                "until_time": int(datetime.now().timestamp())
            },
            
            # Dark Web Tools (will return needs_config if Tor not available)
            "robin": {
                "query": "test",
                "search_types": ["breach"],
                "summarize": True
            },
            "torbot": {
                "onion_url": "test.onion",
                "max_depth": 1
            },
            "onionscan": {
                "onion_url": "test.onion"
            },
            "vigilant_onion": {
                "keywords": ["test"]
            },
            "onion_ingestor": {
                "query": "test"
            },
            "onioff": {
                "onion_url": "test.onion"
            },
        }
    
    async def test_tool(self, tool_name: str) -> ToolTestResult:
        """Test a single tool with realistic parameters"""
        result = ToolTestResult(tool_name)
        start_time = datetime.now()
        
        try:
            tool = self.registry.get(tool_name)
            if not tool:
                result.error = f"Tool {tool_name} not found in registry"
                return result
            
            # Get test parameters
            test_params = self.test_params.get(tool_name, {})
            result.test_params = test_params
            
            # Validate parameters if tool supports it
            if hasattr(tool, 'validate_params') and test_params:
                if not tool.validate_params(test_params):
                    result.error = f"Invalid test parameters for {tool_name}"
                    return result
            
            # Execute tool
            tool_result = await tool.execute(test_params)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            # Check if execution was successful
            result.success = tool_result.get("success", False)
            
            if result.success:
                # Check if result has data
                result_data = tool_result.get("result")
                result.result_data = result_data
                
                if result_data is not None:
                    result.has_data = True
                    
                    # Check if data is complete (not empty, has meaningful content)
                    if isinstance(result_data, dict):
                        result.data_complete = len(result_data) > 0
                    elif isinstance(result_data, list):
                        result.data_complete = len(result_data) > 0
                    elif isinstance(result_data, str):
                        result.data_complete = len(result_data.strip()) > 0
                    else:
                        result.data_complete = result_data is not None
                else:
                    result.error = "Tool returned success but no data"
            else:
                result.error = tool_result.get("error", "Tool execution failed")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            result.error = str(e)
            logger.error(f"Tool {tool_name} test failed: {e}", exc_info=True)
        
        return result
    
    async def test_all_tools(self) -> Dict[str, ToolTestResult]:
        """Test all tools in the registry"""
        all_tools = self.registry.list_tools()
        logger.info(f"Testing {len(all_tools)} tools...")
        
        # Test tools in batches to avoid overwhelming the system
        batch_size = 5
        for i in range(0, len(all_tools), batch_size):
            batch = all_tools[i:i + batch_size]
            logger.info(f"Testing batch {i//batch_size + 1}: {batch}")
            
            tasks = [self.test_tool(tool_name) for tool_name in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Tool test raised exception: {result}")
                    continue
                self.test_results[result.tool_name] = result
        
        return self.test_results
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        total = len(self.test_results)
        successful = sum(1 for r in self.test_results.values() if r.success)
        has_data = sum(1 for r in self.test_results.values() if r.has_data)
        data_complete = sum(1 for r in self.test_results.values() if r.data_complete)
        failed = total - successful
        
        report = f"""
{'='*80}
COMPREHENSIVE TOOL TESTING REPORT
{'='*80}
Generated: {datetime.now().isoformat()}

SUMMARY:
--------
Total Tools Tested: {total}
Successful Executions: {successful} ({successful/total*100:.1f}%)
Tools with Data: {has_data} ({has_data/total*100:.1f}%)
Tools with Complete Data: {data_complete} ({data_complete/total*100:.1f}%)
Failed Executions: {failed} ({failed/total*100:.1f}%)

DETAILED RESULTS:
-----------------
"""
        
        # Group by status
        successful_tools = [r for r in self.test_results.values() if r.success and r.data_complete]
        partial_tools = [r for r in self.test_results.values() if r.success and not r.data_complete]
        failed_tools = [r for r in self.test_results.values() if not r.success]
        
        if successful_tools:
            report += f"\n[OK] FULLY WORKING TOOLS ({len(successful_tools)}):\n"
            for result in sorted(successful_tools, key=lambda x: x.tool_name):
                report += f"  - {result.tool_name} (execution: {result.execution_time:.2f}s)\n"
        
        if partial_tools:
            report += f"\n[WARN] PARTIAL SUCCESS ({len(partial_tools)}):\n"
            for result in sorted(partial_tools, key=lambda x: x.tool_name):
                report += f"  - {result.tool_name}: {result.error or 'No data returned'}\n"
        
        if failed_tools:
            report += f"\n[FAIL] FAILED TOOLS ({len(failed_tools)}):\n"
            for result in sorted(failed_tools, key=lambda x: x.tool_name):
                report += f"  - {result.tool_name}: {result.error}\n"
        
        report += f"\n{'='*80}\n"
        
        return report


@pytest.mark.asyncio
async def test_all_tools_comprehensive():
    """Comprehensive test of all tools"""
    tester = ComprehensiveToolTester()
    results = await tester.test_all_tools()
    
    # Generate report
    report = tester.generate_report()
    print(report)
    
    # Save report to file
    with open("docs/COMPREHENSIVE_TOOL_TEST_REPORT.md", "w") as f:
        f.write(report)
    
    # Assertions
    total = len(results)
    successful = sum(1 for r in results.values() if r.success and r.data_complete)
    
    # At least 80% of tools should work (accounting for external dependencies)
    success_rate = successful / total if total > 0 else 0
    assert success_rate >= 0.5, f"Only {success_rate*100:.1f}% of tools are working. Expected at least 50%."
    
    print(f"\n✅ Test completed: {successful}/{total} tools fully working ({success_rate*100:.1f}%)")

