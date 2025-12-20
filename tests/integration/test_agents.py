#!/usr/bin/env python3
"""
Integration tests for AI Agents
Tests agent execution, coordination, and error handling
"""

import asyncio
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".github" / "scripts"))

from agents.analytics_aggregator_agent import AnalyticsAggregatorAgent
from agents.cost_optimizer_agent import CostOptimizerAgent
from agents.data_validator_agent import DataValidatorAgent
from agents.performance_optimizer_agent import PerformanceOptimizerAgent
from agents.rollback_guardian_agent import RollbackGuardianAgent
from agents.security_monitor_agent import SecurityMonitorAgent
from agents.workflow_orchestrator_agent import WorkflowOrchestratorAgent


async def test_agent_initialization():
    """Test all agents initialize correctly"""
    print("Test 1: Agent Initialization")
    
    agents = [
        WorkflowOrchestratorAgent(),
        DataValidatorAgent(),
        PerformanceOptimizerAgent(),
        SecurityMonitorAgent(),
        CostOptimizerAgent(),
        AnalyticsAggregatorAgent(),
        RollbackGuardianAgent()
    ]
    
    for agent in agents:
        result = await agent.initialize()
        assert result.get("success", False), f"{agent.name} initialization failed"
        print(f"  ✓ {agent.name} initialized")
    
    return True


async def test_workflow_orchestrator_agent():
    """Test workflow orchestrator agent"""
    print("\nTest 2: Workflow Orchestrator Agent")
    
    agent = WorkflowOrchestratorAgent()
    result = await agent.run({
        "task_type": "code_review",
        "task_data": {"files": ["test.py"]}
    })
    
    assert "success" in result, "Result should have success field"
    print(f"  ✓ Workflow orchestrator executed: success={result.get('success')}")
    
    return True


async def test_data_validator_agent():
    """Test data validator agent"""
    print("\nTest 3: Data Validator Agent")
    
    agent = DataValidatorAgent()
    result = await agent.run({
        "data": {"field1": "value1", "field2": 123},
        "validation_type": "comprehensive"
    })
    
    assert "success" in result, "Result should have success field"
    print(f"  ✓ Data validator executed: success={result.get('success')}")
    
    return True


async def test_performance_optimizer_agent():
    """Test performance optimizer agent"""
    print("\nTest 4: Performance Optimizer Agent")
    
    agent = PerformanceOptimizerAgent()
    result = await agent.run({
        "metrics": {"execution_time": 1000, "memory_usage": 512},
        "target": "execution_time"
    })
    
    assert "success" in result, "Result should have success field"
    print(f"  ✓ Performance optimizer executed: success={result.get('success')}")
    
    return True


async def test_security_monitor_agent():
    """Test security monitor agent"""
    print("\nTest 5: Security Monitor Agent")
    
    agent = SecurityMonitorAgent()
    result = await agent.run({
        "target": "codebase",
        "scan_type": "comprehensive"
    })
    
    assert "success" in result, "Result should have success field"
    print(f"  ✓ Security monitor executed: success={result.get('success')}")
    
    return True


async def test_cost_optimizer_agent():
    """Test cost optimizer agent"""
    print("\nTest 6: Cost Optimizer Agent")
    
    agent = CostOptimizerAgent()
    result = await agent.run({
        "costs": {"api_calls": 100, "compute": 50},
        "budget_limit": 200
    })
    
    assert "success" in result, "Result should have success field"
    print(f"  ✓ Cost optimizer executed: success={result.get('success')}")
    
    return True


async def test_analytics_aggregator_agent():
    """Test analytics aggregator agent"""
    print("\nTest 7: Analytics Aggregator Agent")
    
    agent = AnalyticsAggregatorAgent()
    result = await agent.run({
        "time_range": "24h",
        "metrics_types": ["all"]
    })
    
    assert "success" in result, "Result should have success field"
    print(f"  ✓ Analytics aggregator executed: success={result.get('success')}")
    
    return True


async def test_rollback_guardian_agent():
    """Test rollback guardian agent"""
    print("\nTest 8: Rollback Guardian Agent")
    
    agent = RollbackGuardianAgent()
    result = await agent.run({
        "deployment_status": {"status": "deployed", "version": "1.0.0"},
        "metrics": {"error_rate": 0.01}
    })
    
    assert "success" in result, "Result should have success field"
    print(f"  ✓ Rollback guardian executed: success={result.get('success')}")
    
    return True


async def test_agent_monitoring():
    """Test agent monitoring functionality"""
    print("\nTest 9: Agent Monitoring")
    
    agent = WorkflowOrchestratorAgent()
    await agent.initialize()
    
    # Run agent once
    await agent.run({"task_type": "test"})
    
    # Check monitoring
    monitor_result = await agent.monitor()
    assert "metrics" in monitor_result, "Monitor should return metrics"
    assert monitor_result["metrics"]["execution_count"] > 0, "Should have execution count"
    print(f"  ✓ Monitoring works: {monitor_result['metrics']['execution_count']} executions")
    
    return True


async def test_agent_cleanup():
    """Test agent cleanup functionality"""
    print("\nTest 10: Agent Cleanup")
    
    agent = WorkflowOrchestratorAgent()
    await agent.initialize()
    
    cleanup_result = await agent.cleanup()
    assert cleanup_result.get("status") == "cleaned_up", "Cleanup should succeed"
    print("  ✓ Cleanup works correctly")
    
    return True


async def run_all_tests():
    """Run all agent integration tests"""
    print("=" * 60)
    print("AI Agents Integration Tests")
    print("=" * 60)
    
    tests = [
        test_agent_initialization,
        test_workflow_orchestrator_agent,
        test_data_validator_agent,
        test_performance_optimizer_agent,
        test_security_monitor_agent,
        test_cost_optimizer_agent,
        test_analytics_aggregator_agent,
        test_rollback_guardian_agent,
        test_agent_monitoring,
        test_agent_cleanup
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(("PASS", test.__name__))
        except AssertionError as e:
            results.append(("FAIL", test.__name__, str(e)))
        except Exception as e:
            results.append(("ERROR", test.__name__, str(e)))
    
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
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
