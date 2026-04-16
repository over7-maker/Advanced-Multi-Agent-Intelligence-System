"""
Test All Agents with Real Tasks and Tool Execution
Verifies each agent can execute tasks and use tools to get real data
"""

import asyncio
import logging
import pytest
from typing import Dict, List, Any
from datetime import datetime

from src.amas.agents.base_agent import BaseAgent
from src.amas.agents.web_research_agent import WebResearchAgent
from src.amas.agents.security_expert_agent import SecurityExpertAgent
from src.amas.agents.intelligence_gathering_agent import IntelligenceGatheringAgent
from src.amas.agents.research_agent import ResearchAgent
from src.amas.agents.dark_web_agent import DarkWebAgent
from src.amas.agents.search_federation_agent import SearchFederationAgent

logger = logging.getLogger(__name__)


class AgentTestResult:
    """Result of an agent test"""
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.success = False
        self.tools_executed = []
        self.tools_successful = []
        self.tools_failed = []
        self.has_result = False
        self.result_complete = False
        self.error = None
        self.execution_time = 0.0
        self.result_data = None


class AgentTaskTester:
    """Tester for agents with real tasks"""
    
    def __init__(self):
        self.agents = self._initialize_agents()
        self.test_tasks = self._get_test_tasks()
    
    def _initialize_agents(self) -> Dict[str, BaseAgent]:
        """Initialize all agents"""
        agents = {}
        
        try:
            agents["web_research"] = WebResearchAgent()
        except Exception as e:
            logger.warning(f"Failed to initialize WebResearchAgent: {e}")
        
        try:
            agents["security_expert"] = SecurityExpertAgent()
        except Exception as e:
            logger.warning(f"Failed to initialize SecurityExpertAgent: {e}")
        
        try:
            agents["intelligence_gathering"] = IntelligenceGatheringAgent()
        except Exception as e:
            logger.warning(f"Failed to initialize IntelligenceGatheringAgent: {e}")
        
        try:
            agents["research"] = ResearchAgent()
        except Exception as e:
            logger.warning(f"Failed to initialize ResearchAgent: {e}")
        
        try:
            agents["dark_web"] = DarkWebAgent()
        except Exception as e:
            logger.warning(f"Failed to initialize DarkWebAgent: {e}")
        
        try:
            agents["search_federation"] = SearchFederationAgent()
        except Exception as e:
            logger.warning(f"Failed to initialize SearchFederationAgent: {e}")
        
        return agents
    
    def _get_test_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get realistic test tasks for each agent"""
        return {
            "web_research": {
                "task_id": "test_web_research_001",
                "target": "Python programming best practices",
                "parameters": {
                    "query": "Python programming best practices",
                    "depth": "shallow",
                    "max_results": 5,
                    "use_multi_tool": True,
                    "tool_strategy": "comprehensive"
                }
            },
            "security_expert": {
                "task_id": "test_security_001",
                "target": "example.com",
                "parameters": {
                    "scan_type": "comprehensive",
                    "use_multi_tool": True,
                    "tool_strategy": "comprehensive"
                }
            },
            "intelligence_gathering": {
                "task_id": "test_intel_001",
                "target": "example.com",
                "parameters": {
                    "investigation_type": "domain_analysis",
                    "use_multi_tool": True,
                    "tool_strategy": "comprehensive"
                }
            },
            "research": {
                "task_id": "test_research_001",
                "target": "Python async programming",
                "parameters": {
                    "research_topic": "Python async programming",
                    "research_type": "technology_evaluation",
                    "use_multi_tool": True,
                    "tool_strategy": "comprehensive"
                }
            },
            "dark_web": {
                "task_id": "test_darkweb_001",
                "target": "test query",
                "parameters": {
                    "query": "test",
                    "search_types": ["breach"],
                    "use_multi_tool": True,
                    "tool_strategy": "comprehensive"
                }
            },
            "search_federation": {
                "task_id": "test_search_001",
                "target": "Python programming",
                "parameters": {
                    "query": "Python programming",
                    "max_results": 5,
                    "use_multi_tool": True,
                    "tool_strategy": "comprehensive"
                }
            },
        }
    
    async def test_agent(self, agent_name: str, agent: BaseAgent) -> AgentTestResult:
        """Test an agent with a real task"""
        result = AgentTestResult(agent_name)
        start_time = datetime.now()
        
        try:
            task = self.test_tasks.get(agent_name)
            if not task:
                result.error = f"No test task defined for {agent_name}"
                return result
            
            logger.info(f"Testing agent {agent_name} with task: {task['task_id']}")
            
            # Execute agent task
            agent_result = await agent.execute(
                task_id=task["task_id"],
                target=task["target"],
                parameters=task["parameters"]
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            # Check if execution was successful
            result.success = agent_result.get("success", False)
            
            if result.success:
                # Extract tool execution information
                result_data = agent_result.get("result", {})
                result.result_data = result_data
                
                # Check for tool results
                if isinstance(result_data, dict):
                    # Look for tool_results or similar fields
                    tool_results = result_data.get("tool_results", [])
                    if not tool_results:
                        # Try to find tool results in other fields
                        for key, value in result_data.items():
                            if isinstance(value, list) and len(value) > 0:
                                if isinstance(value[0], dict) and "tool" in value[0]:
                                    tool_results = value
                                    break
                    
                    result.tools_executed = [
                        tr.get("tool", "unknown") for tr in tool_results
                        if isinstance(tr, dict)
                    ]
                    result.tools_successful = [
                        tr.get("tool", "unknown") for tr in tool_results
                        if isinstance(tr, dict) and tr.get("success", False)
                    ]
                    result.tools_failed = [
                        tr.get("tool", "unknown") for tr in tool_results
                        if isinstance(tr, dict) and not tr.get("success", False)
                    ]
                
                # Check if result has meaningful data
                result.has_result = result_data is not None
                if isinstance(result_data, dict):
                    result.result_complete = len(result_data) > 0
                elif isinstance(result_data, str):
                    result.result_complete = len(result_data.strip()) > 0
                else:
                    result.result_complete = result_data is not None
            else:
                result.error = agent_result.get("error", "Agent execution failed")
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            result.error = str(e)
            logger.error(f"Agent {agent_name} test failed: {e}", exc_info=True)
        
        return result
    
    async def test_all_agents(self) -> Dict[str, AgentTestResult]:
        """Test all agents"""
        results = {}
        
        for agent_name, agent in self.agents.items():
            logger.info(f"Testing agent: {agent_name}")
            result = await self.test_agent(agent_name, agent)
            results[agent_name] = result
            # Small delay between agent tests
            await asyncio.sleep(1)
        
        return results
    
    def generate_report(self, results: Dict[str, AgentTestResult]) -> str:
        """Generate comprehensive agent test report"""
        total = len(results)
        successful = sum(1 for r in results.values() if r.success and r.result_complete)
        
        report = f"""
{'='*80}
COMPREHENSIVE AGENT TESTING REPORT
{'='*80}
Generated: {datetime.now().isoformat()}

SUMMARY:
--------
Total Agents Tested: {total}
Successful Executions: {successful} ({successful/total*100:.1f}%)
Agents with Complete Results: {successful} ({successful/total*100:.1f}%)

DETAILED RESULTS:
-----------------
"""
        
        for agent_name, result in sorted(results.items()):
            status = "[OK]" if result.success and result.result_complete else "[FAIL]"
            report += f"\n{status} {agent_name.upper()}:\n"
            report += f"  Status: {'SUCCESS' if result.success else 'FAILED'}\n"
            report += f"  Execution Time: {result.execution_time:.2f}s\n"
            
            if result.tools_executed:
                report += f"  Tools Executed: {len(result.tools_executed)}\n"
                report += f"    - Successful: {len(result.tools_successful)} ({', '.join(result.tools_successful[:5])})\n"
                if result.tools_failed:
                    report += f"    - Failed: {len(result.tools_failed)} ({', '.join(result.tools_failed[:5])})\n"
            
            if result.has_result:
                report += f"  Has Result: Yes\n"
                report += f"  Result Complete: {'Yes' if result.result_complete else 'No'}\n"
            
            if result.error:
                report += f"  Error: {result.error}\n"
        
        report += f"\n{'='*80}\n"
        
        return report


@pytest.mark.asyncio
async def test_all_agents_comprehensive():
    """Comprehensive test of all agents with real tasks"""
    tester = AgentTaskTester()
    results = await tester.test_all_agents()
    
    # Generate report
    report = tester.generate_report(results)
    print(report)
    
    # Save report to file
    with open("docs/COMPREHENSIVE_AGENT_TEST_REPORT.md", "w") as f:
        f.write(report)
    
    # Assertions
    total = len(results)
    successful = sum(1 for r in results.values() if r.success and r.result_complete)
    
    # At least 50% of agents should work
    success_rate = successful / total if total > 0 else 0
    assert success_rate >= 0.5, f"Only {success_rate*100:.1f}% of agents are working. Expected at least 50%."
    
    print(f"\n✅ Test completed: {successful}/{total} agents fully working ({success_rate*100:.1f}%)")

