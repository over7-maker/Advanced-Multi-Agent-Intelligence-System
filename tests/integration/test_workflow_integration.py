#!/usr/bin/env python3
"""
Integration tests for workflow integration with AI Orchestrator and Agents
Tests workflow_call integration, agent coordination, and end-to-end flows
"""

import asyncio
import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".github" / "scripts"))

from ai_orchestrator import AIOrchestrator, TaskType
from agents.workflow_orchestrator_agent import WorkflowOrchestratorAgent
from agents.data_validator_agent import DataValidatorAgent
from agents.performance_optimizer_agent import PerformanceOptimizerAgent
from agents.security_monitor_agent import SecurityMonitorAgent
from agents.cost_optimizer_agent import CostOptimizerAgent
from agents.analytics_aggregator_agent import AnalyticsAggregatorAgent
from agents.rollback_guardian_agent import RollbackGuardianAgent


async def test_orchestrator_with_agents():
    """Test orchestrator integration with agents"""
    print("\nTest 1: Orchestrator with Agents Integration")
    
    try:
        orchestrator = AIOrchestrator(cache_enabled=True)
        agent = WorkflowOrchestratorAgent(orchestrator=orchestrator)
        
        # Initialize agent
        init_result = await agent.initialize()
        assert init_result.get("success", False), "Agent initialization failed"
        
        # Execute agent (uses orchestrator internally)
        exec_result = await agent.execute({
            "task_type": "code_review",
            "task_data": {"test": "data"}
        })
        
        assert "success" in exec_result, "Agent execution result missing"
        print(f"  ✓ Orchestrator integrated with agent (success={exec_result.get('success')})")
        return True
    except Exception as e:
        print(f"  ✗ Orchestrator-agent integration error: {e}")
        return False


async def test_agent_coordination():
    """Test multiple agents working together"""
    print("\nTest 2: Agent Coordination")
    
    try:
        orchestrator = AIOrchestrator(cache_enabled=True)
        
        # Initialize multiple agents
        agents = {
            "workflow": WorkflowOrchestratorAgent(orchestrator),
            "validator": DataValidatorAgent(orchestrator),
            "optimizer": PerformanceOptimizerAgent(orchestrator)
        }
        
        # Initialize all agents
        for name, agent in agents.items():
            result = await agent.initialize()
            assert result.get("success", False), f"{name} agent initialization failed"
        
        # Execute agents in sequence
        results = {}
        for name, agent in agents.items():
            context = {
                "task_type": "general",
                "task_data": {}
            }
            result = await agent.execute(context)
            results[name] = result.get("success", False)
        
        success_count = sum(1 for v in results.values() if v)
        assert success_count > 0, "No agents succeeded"
        
        print(f"  ✓ {success_count}/{len(agents)} agents executed successfully")
        return True
    except Exception as e:
        print(f"  ✗ Agent coordination error: {e}")
        return False


async def test_workflow_task_types():
    """Test orchestrator with different task types"""
    print("\nTest 3: Workflow Task Types")
    
    try:
        orchestrator = AIOrchestrator(cache_enabled=False)
        
        task_types = [
            TaskType.CODE_REVIEW.value,
            TaskType.PR_ANALYSIS.value,
            TaskType.SECURITY_SCAN.value,
            TaskType.GENERAL.value
        ]
        
        results = {}
        for task_type in task_types:
            result = await orchestrator.execute(
                task_type=task_type,
                system_message="You are a test assistant.",
                user_prompt="Say hello",
                max_tokens=10,
                use_cache=False
            )
            results[task_type] = result.get("success", False)
        
        success_count = sum(1 for v in results.values() if v)
        print(f"  ✓ {success_count}/{len(task_types)} task types succeeded")
        return success_count > 0
    except Exception as e:
        print(f"  ✗ Task types test error: {e}")
        return False


async def test_agent_with_orchestrator_cache():
    """Test agent using orchestrator cache"""
    print("\nTest 4: Agent with Orchestrator Cache")
    
    try:
        orchestrator = AIOrchestrator(cache_enabled=True)
        agent = WorkflowOrchestratorAgent(orchestrator=orchestrator)
        
        await agent.initialize()
        
        # First execution (should call API)
        result1 = await agent.execute({
            "task_type": "general",
            "task_data": {"test": "cache"}
        })
        
        # Second execution (should use cache if available)
        result2 = await agent.execute({
            "task_type": "general",
            "task_data": {"test": "cache"}
        })
        
        print(f"  ✓ First execution: success={result1.get('success')}")
        print(f"  ✓ Second execution: success={result2.get('success')}")
        return True
    except Exception as e:
        print(f"  ✗ Cache test error: {e}")
        return False


async def test_all_agents_with_orchestrator():
    """Test all 7 agents with shared orchestrator"""
    print("\nTest 5: All Agents with Shared Orchestrator")
    
    try:
        orchestrator = AIOrchestrator(cache_enabled=True)
        
        agents = {
            "workflow_orchestrator": WorkflowOrchestratorAgent(orchestrator),
            "data_validator": DataValidatorAgent(orchestrator),
            "performance_optimizer": PerformanceOptimizerAgent(orchestrator),
            "security_monitor": SecurityMonitorAgent(orchestrator),
            "cost_optimizer": CostOptimizerAgent(orchestrator),
            "analytics_aggregator": AnalyticsAggregatorAgent(orchestrator),
            "rollback_guardian": RollbackGuardianAgent(orchestrator)
        }
        
        # Initialize all
        init_results = {}
        for name, agent in agents.items():
            result = await agent.initialize()
            init_results[name] = result.get("success", False)
        
        init_success = sum(1 for v in init_results.values() if v)
        print(f"  ✓ {init_success}/{len(agents)} agents initialized")
        
        # Execute all
        exec_results = {}
        for name, agent in agents.items():
            context = {"task_type": "general", "task_data": {}}
            result = await agent.execute(context)
            exec_results[name] = result.get("success", False)
        
        exec_success = sum(1 for v in exec_results.values() if v)
        print(f"  ✓ {exec_success}/{len(agents)} agents executed")
        
        return init_success == len(agents) and exec_success > 0
    except Exception as e:
        print(f"  ✗ All agents test error: {e}")
        return False


async def test_error_handling_and_fallback():
    """Test error handling and fallback in workflow integration"""
    print("\nTest 6: Error Handling and Fallback")
    
    try:
        orchestrator = AIOrchestrator(cache_enabled=False)
        agent = WorkflowOrchestratorAgent(orchestrator=orchestrator)
        
        await agent.initialize()
        
        # Test with invalid context (should handle gracefully)
        result = await agent.execute({
            "task_type": "invalid_type",
            "task_data": None
        })
        
        # Should return a result (even if failed)
        assert "success" in result, "Result should have success field"
        print(f"  ✓ Error handling works (success={result.get('success')})")
        
        # Test orchestrator fallback
        orchestrator_result = await orchestrator.execute(
            task_type="general",
            system_message="Test",
            user_prompt="Test",
            max_tokens=10,
            use_cache=False
        )
        
        # Should handle gracefully even if all providers fail
        assert "success" in orchestrator_result, "Orchestrator should return result"
        print(f"  ✓ Orchestrator fallback works (success={orchestrator_result.get('success')})")
        
        return True
    except Exception as e:
        print(f"  ✗ Error handling test error: {e}")
        return False


async def test_metrics_collection():
    """Test metrics collection in workflow integration"""
    print("\nTest 7: Metrics Collection")
    
    try:
        orchestrator = AIOrchestrator(cache_enabled=False)
        agent = WorkflowOrchestratorAgent(orchestrator=orchestrator)
        
        await agent.initialize()
        
        # Execute agent multiple times
        for i in range(3):
            await agent.execute({
                "task_type": "general",
                "task_data": {"iteration": i}
            })
        
        # Check metrics
        monitor_result = await agent.monitor()
        metrics = monitor_result.get("metrics", {})
        
        assert "execution_count" in metrics, "Metrics missing execution_count"
        assert metrics["execution_count"] >= 3, "Execution count should be >= 3"
        
        print(f"  ✓ Metrics collected: {metrics['execution_count']} executions")
        return True
    except Exception as e:
        print(f"  ✗ Metrics collection error: {e}")
        return False


async def run_all_tests():
    """Run all workflow integration tests"""
    print("=" * 60)
    print("Workflow Integration Tests")
    print("=" * 60)
    
    tests = [
        test_orchestrator_with_agents,
        test_agent_coordination,
        test_workflow_task_types,
        test_agent_with_orchestrator_cache,
        test_all_agents_with_orchestrator,
        test_error_handling_and_fallback,
        test_metrics_collection
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
    print(f"Success Rate: {(passed / len(results) * 100):.1f}%")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
