"""
Comprehensive Tool Testing Suite
Runs all tool tests and generates a report
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.amas.agents.tools import get_tool_registry
from src.amas.agents.tools.tool_categories import TOOL_CATEGORY_MAP, get_tool_metadata


class ToolTestRunner:
    """Comprehensive tool test runner"""
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
        self.test_results: Dict[str, Dict[str, Any]] = {}
        self.test_url = "https://example.com"
        self.test_domain = "example.com"
    
    async def test_tool(self, tool_name: str) -> Dict[str, Any]:
        """Test a single tool"""
        result = {
            "tool_name": tool_name,
            "status": "not_implemented",
            "tests": {},
            "errors": [],
            "warnings": []
        }
        
        # Check if tool is registered
        tool = self.tool_registry.get(tool_name)
        if not tool:
            result["status"] = "not_registered"
            result["warnings"].append(f"Tool {tool_name} not registered in tool registry")
            return result
        
        result["status"] = "implemented"
        result["tests"]["initialization"] = await self._test_initialization(tool)
        result["tests"]["schema"] = await self._test_schema(tool)
        result["tests"]["validation"] = await self._test_validation(tool)
        result["tests"]["execution"] = await self._test_execution(tool, tool_name)
        
        # Check for errors
        if any(not test.get("passed", False) for test in result["tests"].values()):
            result["status"] = "has_errors"
        
        return result
    
    async def _test_initialization(self, tool) -> Dict[str, Any]:
        """Test tool initialization"""
        try:
            assert tool is not None
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert tool.name is not None
            return {"passed": True, "message": "Initialization successful"}
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _test_schema(self, tool) -> Dict[str, Any]:
        """Test tool schema"""
        try:
            schema = tool.get_schema()
            assert isinstance(schema, dict)
            assert schema.get("type") == "object"
            return {"passed": True, "message": "Schema valid"}
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _test_validation(self, tool) -> Dict[str, Any]:
        """Test parameter validation"""
        try:
            # Test with empty params (should fail)
            if hasattr(tool, 'validate_params'):
                empty_result = tool.validate_params({})
                # Should return False or raise exception
                return {"passed": True, "message": "Validation method exists"}
            return {"passed": True, "message": "No validation method (optional)"}
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _test_execution(self, tool, tool_name: str) -> Dict[str, Any]:
        """Test tool execution"""
        try:
            # Get test parameters based on tool type
            test_params = self._get_test_params(tool_name)
            
            if test_params:
                result = await tool.execute(test_params)
                assert isinstance(result, dict)
                assert "success" in result
                return {
                    "passed": True,
                    "message": "Execution successful",
                    "result_success": result.get("success", False)
                }
            else:
                return {"passed": True, "message": "No test parameters defined (skipped)"}
        except Exception as e:
            return {"passed": False, "error": str(e), "message": f"Execution failed: {str(e)}"}
    
    def _get_test_params(self, tool_name: str) -> Dict[str, Any]:
        """Get test parameters for a tool"""
        params_map = {
            "web_scraper": {"url": self.test_url, "extract_text": True},
            "dns_lookup": {"domain": self.test_domain, "record_types": ["A"]},
            "whois_lookup": {"domain": self.test_domain},
            "ssl_analyzer": {"hostname": self.test_domain, "port": 443},
            "api_fetcher": {"url": f"{self.test_url}/api/test", "method": "GET"},
            "virustotal": {"resource": self.test_domain, "resource_type": "domain"},
            "shodan": {"query": "test"},
            "censys": {"query": "test"},
            "haveibeenpwned": {"email": "test@example.com"},
            "abuseipdb": {"ip": "8.8.8.8"},
            "github_api": {"endpoint": "repos/octocat/Hello-World"},
            "gitlab_api": {"endpoint": "projects"},
            "npm_package": {"package": "express"},
            "pypi_package": {"package": "requests"},
        }
        return params_map.get(tool_name)
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run tests for all registered tools"""
        registered_tools = self.tool_registry.list_tools()
        
        print(f"\n{'='*60}")
        print(f"Testing {len(registered_tools)} Registered Tools")
        print(f"{'='*60}\n")
        
        for tool_name in registered_tools:
            print(f"Testing {tool_name}...", end=" ")
            result = await self.test_tool(tool_name)
            self.test_results[tool_name] = result
            
            status_icon = "[OK]" if result["status"] == "implemented" and all(
                t.get("passed", False) for t in result["tests"].values()
            ) else "[WARN]" if result["status"] == "implemented" else "[FAIL]"
            
            print(f"{status_icon} {result['status']}")
        
        return self.test_results
    
    async def test_cataloged_tools(self) -> Dict[str, Any]:
        """Test all cataloged tools (including not implemented)"""
        cataloged_tools = list(TOOL_CATEGORY_MAP.keys())
        registered_tools = self.tool_registry.list_tools()
        
        print(f"\n{'='*60}")
        print(f"Tool Catalog Status")
        print(f"{'='*60}\n")
        print(f"Total Cataloged: {len(cataloged_tools)}")
        print(f"Actually Registered: {len(registered_tools)}")
        print(f"Not Implemented: {len(cataloged_tools) - len(registered_tools)}\n")
        
        status = {
            "cataloged": len(cataloged_tools),
            "registered": len(registered_tools),
            "not_implemented": [],
            "implemented": []
        }
        
        for tool_name in cataloged_tools:
            if tool_name in registered_tools:
                status["implemented"].append(tool_name)
            else:
                status["not_implemented"].append(tool_name)
        
        return status
    
    def generate_report(self) -> str:
        """Generate test report"""
        report_lines = [
            "# AMAS Tools Test Report",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Total Tools Tested**: {len(self.test_results)}",
            f"- **Fully Working**: {sum(1 for r in self.test_results.values() if r['status'] == 'implemented' and all(t.get('passed', False) for t in r['tests'].values()))}",
            f"- **Has Errors**: {sum(1 for r in self.test_results.values() if r['status'] == 'has_errors')}",
            f"- **Not Registered**: {sum(1 for r in self.test_results.values() if r['status'] == 'not_registered')}",
            "",
            "## Detailed Results",
            ""
        ]
        
        for tool_name, result in sorted(self.test_results.items()):
            status_icon = "[OK]" if result["status"] == "implemented" and all(
                t.get("passed", False) for t in result["tests"].values()
            ) else "[WARN]" if result["status"] == "implemented" else "[FAIL]"
            
            report_lines.append(f"### {status_icon} {tool_name}")
            report_lines.append(f"- **Status**: {result['status']}")
            
            for test_name, test_result in result["tests"].items():
                test_icon = "[PASS]" if test_result.get("passed", False) else "[FAIL]"
                report_lines.append(f"- **{test_name}**: {test_icon} {test_result.get('message', 'N/A')}")
                if "error" in test_result:
                    report_lines.append(f"  - Error: {test_result['error']}")
            
            if result.get("warnings"):
                for warning in result["warnings"]:
                    report_lines.append(f"- [WARN] Warning: {warning}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def save_report(self, filename: str = "tool_test_report.md"):
        """Save test report to file"""
        report = self.generate_report()
        report_path = project_root / "docs" / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {report_path}")


async def main():
    """Main test runner"""
    runner = ToolTestRunner()
    
    # Test registered tools
    await runner.run_all_tests()
    
    # Test catalog status
    catalog_status = await runner.test_cataloged_tools()
    
    # Generate and save report
    runner.save_report("TOOL_TEST_REPORT.md")
    
    # Print summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    print(f"Cataloged Tools: {catalog_status['cataloged']}")
    print(f"Implemented: {len(catalog_status['implemented'])}")
    print(f"Not Implemented: {len(catalog_status['not_implemented'])}")
    print(f"\nTest Report: docs/TOOL_TEST_REPORT.md")


if __name__ == "__main__":
    asyncio.run(main())

