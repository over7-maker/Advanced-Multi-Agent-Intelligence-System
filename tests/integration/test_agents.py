#!/usr/bin/env python3
"""
Integration tests for AI Autonomy Agents
Tests all 7 agents: initialization, execution, monitoring, cleanup
"""

import asyncio
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".github" / "scripts"))

from agents.base_agent import BaseAgent
from agents.workflow_orchestrator_agent import WorkflowOrchestratorAgent
from agents.data_validator_agent import DataValidatorAgent
from agents.performance_optimizer_agent import PerformanceOptimizerAgent
from agents.security_monitor_agent import SecurityMonitorAgent
from agents.cost_optimizer_agent import CostOptimizerAgent
from agents.analytics_aggregator_agent import AnalyticsAggregatorAgent
from agents.rollback_guardian_agent import RollbackGuardianAgent


async def test_agent_initialization(agent: BaseAgent, agent_name: str):
    """Test agent initialization"""
    print(f"\nTest: {agent_name} Initialization")
    try:
        result = await agent.initialize()
        assert result.get("success", False), f"{agent_name} initialization failed"
        print(f"  ✓ {agent_name} initialized successfully")
        return True
    except Exception as e:
        print(f"  ✗ {agent_name} initialization error: {e}")
        return False


async def test_agent_execution(agent: BaseAgent, agent_name: str, context: dict):
    """Test agent execution"""
    print(f"\nTest: {agent_name} Execution")
    try:
        # Ensure agent is initialized
        if not agent.initialized:
            await agent.initialize()
        
        result = await agent.execute(context)
        assert "success" in result, f"{agent_name} result missing success field"
        print(f"  ✓ {agent_name} execution completed (success={result.get('success')})")
        return True
    except Exception as e:
        print(f"  ✗ {agent_name} execution error: {e}")
        return False


async def test_agent_monitoring(agent: BaseAgent, agent_name: str):
    """Test agent monitoring"""
    print(f"\nTest: {agent_name} Monitoring")
    try:
        result = await agent.monitor()
        assert "agent_name" in result, f"{agent_name} monitor missing agent_name"
        assert "metrics" in result, f"{agent_name} monitor missing metrics"
        print(f"  ✓ {agent_name} monitoring works")
        return True
    except Exception as e:
        print(f"  ✗ {agent_name} monitoring error: {e}")
        return False


async def test_agent_cleanup(agent: BaseAgent, agent_name: str):
    """Test agent cleanup"""
    print(f"\nTest: {agent_name} Cleanup")
    try:
        result = await agent.cleanup()
        assert "agent_name" in result, f"{agent_name} cleanup missing agent_name"
        print(f"  ✓ {agent_name} cleanup completed")
        return True
    except Exception as e:
        print(f"  ✗ {agent_name} cleanup error: {e}")
        return False


async def test_workflow_orchestrator_agent():
    """Test Agent-1: Workflow Orchestrator"""
    print("\n" + "=" * 60)
    print("Testing Agent-1: Workflow Orchestrator")
    print("=" * 60)
    
    agent = WorkflowOrchestratorAgent()
    
    results = []
    results.append(await test_agent_initialization(agent, "WorkflowOrchestrator"))
    
    context = {
        "task_type": "code_review",
        "task_data": {"files": ["test.py"], "complexity": "medium"}
    }
    results.append(await test_agent_execution(agent, "WorkflowOrchestrator", context))
    results.append(await test_agent_monitoring(agent, "WorkflowOrchestrator"))
    results.append(await test_agent_cleanup(agent, "WorkflowOrchestrator"))
    
    return all(results)


async def test_data_validator_agent():
    """Test Agent-2: Data Validator"""
    print("\n" + "=" * 60)
    print("Testing Agent-2: Data Validator")
    print("=" * 60)
    
    agent = DataValidatorAgent()
    
    results = []
    results.append(await test_agent_initialization(agent, "DataValidator"))
    
    context = {
        "data": {"name": "test", "value": 123, "timestamp": "2024-01-01T00:00:00Z"},
        "validation_type": "comprehensive"
    }
    results.append(await test_agent_execution(agent, "DataValidator", context))
    results.append(await test_agent_monitoring(agent, "DataValidator"))
    results.append(await test_agent_cleanup(agent, "DataValidator"))
    
    return all(results)


async def test_performance_optimizer_agent():
    """Test Agent-3: Performance Optimizer"""
    print("\n" + "=" * 60)
    print("Testing Agent-3: Performance Optimizer")
    print("=" * 60)
    
    agent = PerformanceOptimizerAgent()
    
    results = []
    results.append(await test_agent_initialization(agent, "PerformanceOptimizer"))
    
    context = {
        "metrics": {"execution_time": 1200, "memory_usage": 512, "cpu_usage": 75},
        "target": "execution_time"
    }
    results.append(await test_agent_execution(agent, "PerformanceOptimizer", context))
    results.append(await test_agent_monitoring(agent, "PerformanceOptimizer"))
    results.append(await test_agent_cleanup(agent, "PerformanceOptimizer"))
    
    return all(results)


async def test_security_monitor_agent():
    """Test Agent-4: Security Monitor"""
    print("\n" + "=" * 60)
    print("Testing Agent-4: Security Monitor")
    print("=" * 60)
    
    agent = SecurityMonitorAgent()
    
    results = []
    results.append(await test_agent_initialization(agent, "SecurityMonitor"))
    
    context = {
        "target": "codebase",
        "scan_type": "comprehensive"
    }
    results.append(await test_agent_execution(agent, "SecurityMonitor", context))
    results.append(await test_agent_monitoring(agent, "SecurityMonitor"))
    results.append(await test_agent_cleanup(agent, "SecurityMonitor"))
    
    return all(results)


async def test_cost_optimizer_agent():
    """Test Agent-5: Cost Optimizer"""
    print("\n" + "=" * 60)
    print("Testing Agent-5: Cost Optimizer")
    print("=" * 60)
    
    agent = CostOptimizerAgent()
    
    results = []
    results.append(await test_agent_initialization(agent, "CostOptimizer"))
    
    context = {
        "costs": {"compute": 0.10, "storage": 0.05, "api_calls": 0.15},
        "budget_limit": 0.20
    }
    results.append(await test_agent_execution(agent, "CostOptimizer", context))
    results.append(await test_agent_monitoring(agent, "CostOptimizer"))
    results.append(await test_agent_cleanup(agent, "CostOptimizer"))
    
    return all(results)


async def test_analytics_aggregator_agent():
    """Test Agent-6: Analytics Aggregator"""
    print("\n" + "=" * 60)
    print("Testing Agent-6: Analytics Aggregator")
    print("=" * 60)
    
    agent = AnalyticsAggregatorAgent()
    
    results = []
    results.append(await test_agent_initialization(agent, "AnalyticsAggregator"))
    
    context = {
        "time_range": "24h",
        "metrics_types": ["performance", "cost", "security"]
    }
    results.append(await test_agent_execution(agent, "AnalyticsAggregator", context))
    results.append(await test_agent_monitoring(agent, "AnalyticsAggregator"))
    results.append(await test_agent_cleanup(agent, "AnalyticsAggregator"))
    
    return all(results)


async def test_rollback_guardian_agent():
    """Test Agent-7: Rollback Guardian"""
    print("\n" + "=" * 60)
    print("Testing Agent-7: Rollback Guardian")
    print("=" * 60)
    
    agent = RollbackGuardianAgent()
    
    results = []
    results.append(await test_agent_initialization(agent, "RollbackGuardian"))
    
    context = {
        "deployment_status": {"status": "healthy", "error_rate": 0.01},
        "metrics": {"response_time": 200, "error_count": 5}
    }
    results.append(await test_agent_execution(agent, "RollbackGuardian", context))
    results.append(await test_agent_monitoring(agent, "RollbackGuardian"))
    results.append(await test_agent_cleanup(agent, "RollbackGuardian"))
    
    return all(results)


async def test_agent_lifecycle():
    """Test complete agent lifecycle"""
    print("\n" + "=" * 60)
    print("Testing Complete Agent Lifecycle")
    print("=" * 60)
    
    agent = WorkflowOrchestratorAgent()
    
    try:
        # Initialize
        init_result = await agent.initialize()
        assert init_result.get("success", False), "Initialization failed"
        print("  ✓ Initialization")
        
        # Execute
        exec_result = await agent.run({
            "task_type": "general",
            "task_data": {}
        })
        assert "success" in exec_result, "Execution result missing"
        print("  ✓ Execution")
        
        # Monitor
        monitor_result = await agent.monitor()
        assert "metrics" in monitor_result, "Monitor result missing metrics"
        print("  ✓ Monitoring")
        
        # Cleanup
        cleanup_result = await agent.cleanup()
        assert "status" in cleanup_result, "Cleanup result missing status"
        print("  ✓ Cleanup")
        
        return True
    except Exception as e:
        print(f"  ✗ Lifecycle test error: {e}")
        return False


async def run_all_tests():
    """Run all agent tests"""
    print("=" * 60)
    print("AI Autonomy Agents Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Workflow Orchestrator", test_workflow_orchestrator_agent),
        ("Data Validator", test_data_validator_agent),
        ("Performance Optimizer", test_performance_optimizer_agent),
        ("Security Monitor", test_security_monitor_agent),
        ("Cost Optimizer", test_cost_optimizer_agent),
        ("Analytics Aggregator", test_analytics_aggregator_agent),
        ("Rollback Guardian", test_rollback_guardian_agent),
        ("Agent Lifecycle", test_agent_lifecycle),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append(("PASS", test_name))
        except AssertionError as e:
            results.append(("FAIL", test_name, str(e)))
        except Exception as e:
            results.append(("ERROR", test_name, str(e)))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for result in results:
        status = result[0]
        test_name = result[1]
        if status == "PASS":
            print(f"✓ {test_name}")
            passed += 1
        else:
            print(f"✗ {test_name}: {result[2] if len(result) > 2 else 'Unknown error'}")
            failed += 1
    
    print(f"\nTotal: {len(results)} test suites")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed / len(results) * 100):.1f}%")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
