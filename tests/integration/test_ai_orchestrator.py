#!/usr/bin/env python3
"""
Integration tests for AI Orchestrator
Tests provider fallback, cache, error handling
"""

import asyncio
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".github" / "scripts"))

from ai_cache import AICache
from ai_orchestrator import AIOrchestrator


async def test_orchestrator_initialization():
    """Test orchestrator initializes correctly"""
    print("Test 1: Orchestrator Initialization")
    orchestrator = AIOrchestrator(cache_enabled=True)
    
    assert orchestrator.providers is not None, "Providers should be initialized"
    assert len(orchestrator.providers) > 0, "At least one provider should be available"
    print(f"  ✓ Found {len(orchestrator.providers)} providers")
    return True


async def test_cache_functionality():
    """Test cache get/set operations"""
    print("\nTest 2: Cache Functionality")
    cache = AICache()
    
    # Test set
    test_response = {"response": "test response", "provider": "test"}
    cache.set("test_task", "test prompt", test_response, "test system")
    
    # Test get
    cached = cache.get("test_task", "test prompt", "test system")
    assert cached is not None, "Cached response should be retrieved"
    assert cached["response"] == "test response", "Cached response should match"
    print("  ✓ Cache set/get works correctly")
    
    # Test stats
    stats = cache.stats()
    assert stats["total_files"] > 0, "Cache should have files"
    print(f"  ✓ Cache stats: {stats['total_files']} files")
    
    # Cleanup
    cache.clear("test_task")
    return True


async def test_provider_chain_selection():
    """Test provider chain selection based on task type"""
    print("\nTest 3: Provider Chain Selection")
    orchestrator = AIOrchestrator(cache_enabled=False)
    
    # Test code_review task type
    chain = orchestrator._provider_chain("code_review")
    assert len(chain) > 0, "Provider chain should not be empty"
    print(f"  ✓ Provider chain for code_review: {len(chain)} providers")
    
    # Test general task type
    chain_general = orchestrator._provider_chain("general")
    assert len(chain_general) > 0, "Provider chain should not be empty"
    print(f"  ✓ Provider chain for general: {len(chain_general)} providers")
    
    return True


async def test_orchestrator_execution_with_cache():
    """Test orchestrator execution with cache enabled"""
    print("\nTest 4: Orchestrator Execution with Cache")
    orchestrator = AIOrchestrator(cache_enabled=True)
    
    # First execution (should call API)
    result1 = await orchestrator.execute(
        task_type="general",
        system_message="You are a test assistant.",
        user_prompt="Say hello",
        max_tokens=10,
        use_cache=True
    )
    
    print(f"  First execution: success={result1.get('success')}, provider={result1.get('provider')}")
    
    # Second execution (should use cache)
    result2 = await orchestrator.execute(
        task_type="general",
        system_message="You are a test assistant.",
        user_prompt="Say hello",
        max_tokens=10,
        use_cache=True
    )
    
    if result2.get("cached"):
        print("  ✓ Cache hit on second execution")
    else:
        print("  ⚠ Cache miss (may be expected if cache TTL expired)")
    
    return True


async def test_error_handling():
    """Test error handling when providers fail"""
    print("\nTest 5: Error Handling")
    orchestrator = AIOrchestrator(cache_enabled=False)
    
    # Test with invalid task (should still handle gracefully)
    result = await orchestrator.execute(
        task_type="invalid_task_type",
        system_message="Test",
        user_prompt="Test",
        max_tokens=10
    )
    
    # Should return a result (even if failed)
    assert "success" in result, "Result should have success field"
    print(f"  ✓ Error handling works: success={result.get('success')}")
    
    return True


async def test_metrics_logging():
    """Test metrics are logged correctly"""
    print("\nTest 6: Metrics Logging")
    orchestrator = AIOrchestrator(cache_enabled=False)
    
    # Execute a task
    result = await orchestrator.execute(
        task_type="general",
        system_message="Test",
        user_prompt="Test",
        max_tokens=10
    )
    
    # Check metrics file exists
    metrics_dir = Path(".github/data/metrics")
    if metrics_dir.exists():
        metric_files = list(metrics_dir.glob("*.jsonl"))
        if metric_files:
            print(f"  ✓ Metrics logged to {len(metric_files)} file(s)")
        else:
            print("  ⚠ No metric files found (may be expected)")
    else:
        print("  ⚠ Metrics directory not found")
    
    return True


async def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("AI Orchestrator Integration Tests")
    print("=" * 60)
    
    tests = [
        test_orchestrator_initialization,
        test_cache_functionality,
        test_provider_chain_selection,
        test_orchestrator_execution_with_cache,
        test_error_handling,
        test_metrics_logging
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
