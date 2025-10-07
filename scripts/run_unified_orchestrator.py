#!/usr/bin/env python3
"""
Run the Unified Multi-Agent Orchestrator
Demonstrates the consolidated system in action
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import logging

# Import after path setup
from amas.core.unified_orchestrator import AgentRole, get_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def demonstrate_orchestrator():
    """Demonstrate the unified orchestrator capabilities"""

    print("\n" + "=" * 80)
    print("🤖 AMAS Unified Multi-Agent Orchestrator Demonstration")
    print("=" * 80 + "\n")

    # Get orchestrator instance
    orchestrator = get_orchestrator()

    # Display status
    print("Current System Status:")
    print("-" * 40)
    status = orchestrator.get_status()
    print(f"Registered Agents: {status['orchestrator']['registered_agents']}")
    print(f"Available AI Models: {status['ai_router']['available_models']}")
    print(f"Active Tasks: {status['orchestrator']['active_tasks']}")

    # List all agents
    print("\nConfigured Agents:")
    for role in status["orchestrator"]["agent_roles"]:
        agent_info = status["agents"][role]
        print(f"  - {agent_info['name']}")
        print(f"    Capabilities: {', '.join(agent_info['capabilities'])}")

    # Test agents
    print("\n" + "=" * 80)
    print("Testing Agent Connectivity...")
    print("=" * 80 + "\n")

    test_results = await orchestrator.test_agents()
    working_agents = sum(1 for v in test_results.values() if v)

    print(f"\nWorking Agents: {working_agents}/{len(test_results)}")
    for role, working in test_results.items():
        status_icon = "✓" if working else "✗"
        print(f"  {status_icon} {role}")

    if working_agents == 0:
        print("\n❌ No working agents. Please check API configuration.")
        return

    # Demonstrate multi-agent coordination
    print("\n" + "=" * 80)
    print("Demonstrating Multi-Agent Coordination")
    print("=" * 80 + "\n")

    # Example 1: Code Analysis Task
    print("1. Code Quality Analysis Task")
    print("-" * 40)

    code_task = await orchestrator.execute_task(
        title="Analyze AMAS Codebase Quality",
        description="Analyze the code quality, architecture, and improvement opportunities in the AMAS system",
        required_agents=[
            AgentRole.CODE_ANALYST,
            AgentRole.CODE_IMPROVER,
            AgentRole.PERFORMANCE_OPTIMIZER,
        ],
        parameters={
            "focus_areas": ["architecture", "performance", "maintainability"],
            "project_path": "/workspace/src/amas",
        },
    )

    print(f"Task ID: {code_task.task_id}")
    print(f"Status: {code_task.status}")
    print(f"Agents involved: {len(code_task.results)}")

    # Show sample results
    for agent_role, result in code_task.results.items():
        if "response" in result:
            print(f"\n{agent_role}:")
            print(f"  {result['response'][:200]}...")

    # Example 2: Security Assessment
    print("\n\n2. Security Assessment Task")
    print("-" * 40)

    security_task = await orchestrator.execute_task(
        title="Security Vulnerability Assessment",
        description="Assess security vulnerabilities and recommend improvements for the AMAS system",
        required_agents=[AgentRole.SECURITY_EXPERT, AgentRole.INCIDENT_RESPONDER],
        parameters={
            "scan_type": "comprehensive",
            "focus": ["authentication", "api_security", "data_protection"],
        },
    )

    print(f"Task ID: {security_task.task_id}")
    print(f"Status: {security_task.status}")

    # Example 3: Project Planning
    print("\n\n3. Project Improvement Planning")
    print("-" * 40)

    planning_task = await orchestrator.execute_task(
        title="Create Improvement Roadmap",
        description="Based on the code and security analysis, create a prioritized improvement roadmap",
        required_agents=[AgentRole.PROJECT_MANAGER, AgentRole.DOCUMENTATION_SPECIALIST],
        parameters={
            "previous_analysis": {
                "code_quality": code_task.task_id,
                "security": security_task.task_id,
            },
            "timeline": "30_days",
        },
    )

    print(f"Task ID: {planning_task.task_id}")
    print(f"Status: {planning_task.status}")

    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("Generating Comprehensive Improvement Report")
    print("=" * 80 + "\n")

    # Collect all results
    all_results = {
        "code_quality": code_task.results,
        "security": security_task.results,
        "planning": planning_task.results,
    }

    # Save detailed results
    results_file = (
        f"orchestrator_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(results_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "tasks": {
                    "code_quality": {
                        "task_id": code_task.task_id,
                        "title": code_task.title,
                        "status": code_task.status,
                        "results": code_task.results,
                    },
                    "security": {
                        "task_id": security_task.task_id,
                        "title": security_task.title,
                        "status": security_task.status,
                        "results": security_task.results,
                    },
                    "planning": {
                        "task_id": planning_task.task_id,
                        "title": planning_task.title,
                        "status": planning_task.status,
                        "results": planning_task.results,
                    },
                },
                "system_status": orchestrator.get_status(),
            },
            f,
            indent=2,
        )

    print(f"✓ Detailed results saved to: {results_file}")

    # Generate human-readable report
    report = await orchestrator.generate_improvement_report(all_results)

    report_file = f"improvement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, "w") as f:
        f.write(f"# 🤖 AMAS Multi-Agent Improvement Report\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n")
        f.write(f"**Orchestrator Version:** Unified v1.0\n")
        f.write(f"**Working Agents:** {working_agents}\n\n")
        f.write(report)

    print(f"✓ Improvement report saved to: {report_file}")

    # Summary
    print("\n" + "=" * 80)
    print("Orchestration Complete!")
    print("=" * 80 + "\n")

    print("Summary:")
    print(f"  - Tasks executed: 3")
    print(f"  - Agents coordinated: {len(set(test_results.keys()))}")
    print(f"  - Reports generated: 2")
    print(f"  - Success rate: {working_agents}/{len(test_results)} agents operational")

    print("\nNext Steps:")
    print("  1. Review the improvement report")
    print("  2. Prioritize recommendations")
    print("  3. Implement changes systematically")
    print("  4. Re-run analysis to track progress")


async def main():
    """Main entry point"""
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    try:
        await demonstrate_orchestrator()
    except KeyboardInterrupt:
        print("\n\nOrchestration interrupted by user.")
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
