#!/usr/bin/env python3
"""Test AMAS Intelligence Systems"""

import asyncio
import os
import sys

sys.path.append("src")

# Add the src directory to Python path
sys.path.insert(0, "src")

from amas.intelligence.intelligence_manager import intelligence_manager


async def test_intelligence_systems():
    """Test all intelligence systems"""

    print("🧪 Testing AMAS Intelligence Systems...")
    print("=" * 50)

    # Start intelligence systems
    await intelligence_manager.start_intelligence_systems()

    # Test task optimization
    print("\n🎯 Testing Task Optimization...")
    task_data = {
        "task_type": "security_scan",
        "target": "example.com",
        "parameters": {"depth": "standard"},
        "user_id": "test_user",
    }

    optimization = await intelligence_manager.optimize_task_before_execution(task_data)
    print(f"✅ Optimal agents: {optimization['optimal_agents']}")
    print(
        f"✅ Task prediction confidence: {optimization['task_prediction'].confidence:.2f}"
    )
    print(f"✅ Recommendations: {len(optimization['optimization_recommendations'])}")

    # Test task completion processing
    print("\n📝 Testing Task Completion Processing...")
    completed_task = {
        "task_id": "test_001",
        "task_type": "security_scan",
        "target": "example.com",
        "parameters": {"depth": "standard"},
        "agents_used": optimization["optimal_agents"],
        "execution_time": 120.5,
        "success_rate": 0.9,
        "solution_quality": 0.85,
        "user_feedback": {"rating": 4, "comments": "Good results"},
        "user_id": "test_user",
    }

    await intelligence_manager.process_task_completion(completed_task)
    print("✅ Task completion processed")

    # Test dashboard data
    print("\n📊 Testing Dashboard Data...")
    dashboard_data = await intelligence_manager.get_intelligence_dashboard_data()
    print(
        f"✅ Collective insights: {dashboard_data['collective_intelligence']['total_insights']}"
    )
    print(
        f"✅ Personality adaptations: {dashboard_data['adaptive_personalities']['total_agents']}"
    )
    print(
        f"✅ Prediction models: {len(dashboard_data['predictive_accuracy']['model_accuracies'])}"
    )

    print("\n🎉 All intelligence systems working correctly!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_intelligence_systems())
