#!/usr/bin/env python3
"""Monitor AMAS Intelligence Systems"""

import asyncio
import os
import sys
import time

sys.path.append("src")

from amas.intelligence.intelligence_manager import intelligence_manager

async def monitor_intelligence():
    """Monitor intelligence systems in real-time"""

    print("🧠 AMAS Intelligence Monitor")
    print("=" * 40)
    print("Press Ctrl+C to stop monitoring")
    print()

    try:
        # Start intelligence systems
        await intelligence_manager.start_intelligence_systems()

        while True:
            # Get current status
            dashboard_data = (
                await intelligence_manager.get_intelligence_dashboard_data()
            )

            # Clear screen and show status
            os.system("clear" if os.name == "posix" else "cls")

            print("🧠 AMAS Intelligence Monitor")
            print("=" * 40)
            print(f"Status: {dashboard_data['system_status']}")
            print(f"Intelligence Level: {dashboard_data['intelligence_level']}")
            print()

            # Collective Intelligence
            ci = dashboard_data["collective_intelligence"]
            print("📚 Collective Intelligence:")
            print(
                f"  Insights: {ci['total_insights']} (High confidence: {ci['high_confidence_insights']})"
            )
            print(f"  Knowledge Entries: {ci['knowledge_entries']}")
            print(
                f"  Learning Graph: {ci['learning_graph_nodes']} nodes, {ci['learning_graph_edges']} edges"
            )
            print()

            # Adaptive Personalities
            ap = dashboard_data["adaptive_personalities"]
            print("🎭 Adaptive Personalities:")
            print(f"  Active Agents: {ap['total_agents']}")
            print(f"  Total Interactions: {ap['total_interactions']}")
            print(f"  Average Satisfaction: {ap['average_satisfaction']:.2f}")
            print()

            # Predictive Intelligence
            pa = dashboard_data["predictive_accuracy"]
            print("🔮 Predictive Intelligence:")
            print(f"  Active Models: {len(pa['model_accuracies'])}")
            print(f"  Total Predictions: {pa['total_predictions']}")
            print()

            # Resource Predictions
            rp = dashboard_data["resource_predictions"]
            print("📊 Resource Predictions (60 min):")
            print(f"  CPU: {rp['predicted_cpu_usage']:.1f}%")
            print(f"  Memory: {rp['predicted_memory_usage']:.1f}%")
            print(f"  Task Load: {rp['predicted_task_load']}")
            if rp["bottleneck_predictions"]:
                print(f"  Bottlenecks: {', '.join(rp['bottleneck_predictions'])}")
            print()

            print(f"Last updated: {time.strftime('%H:%M:%S')}")
            print("Press Ctrl+C to stop")

            # Wait before next update
            await asyncio.sleep(10)

    except KeyboardInterrupt:
        print("\n👋 Intelligence monitoring stopped")

if __name__ == "__main__":
    asyncio.run(monitor_intelligence())
