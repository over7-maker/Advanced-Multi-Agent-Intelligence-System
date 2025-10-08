#!/usr/bin/env python3
"""
Code Generation Example
Demonstrates AI-powered code generation capabilities
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import AMASIntelligenceSystem

async def code_generation_example():
    """Code generation example"""
    print("💻 AMAS Code Generation Example")
    print("=" * 50)

    # Configuration
    config = {
        "llm_service_url": "http://localhost:11434",
        "vector_service_url": "http://localhost:8001",
        "graph_service_url": "http://localhost:7474",
        "n8n_url": "http://localhost:5678",
        "n8n_api_key": "your_api_key_here",
    }

    try:
        # Initialize AMAS system
        print("🚀 Initializing AMAS system...")
        amas = AMASIntelligenceSystem(config)
        await amas.initialize()
        print("✅ AMAS system initialized")

        # Code generation tasks
        code_tasks = [
            {
                "type": "code_generation",
                "description": "Generate a Python function for data encryption using AES",
                "priority": 2,
                "metadata": {
                    "language": "python",
                    "framework": "cryptography",
                    "function_type": "encryption",
                    "algorithm": "AES-GCM",
                },
            },
            {
                "type": "code_generation",
                "description": "Create a REST API endpoint for user authentication",
                "priority": 2,
                "metadata": {
                    "language": "python",
                    "framework": "fastapi",
                    "endpoint_type": "authentication",
                    "method": "POST",
                },
            },
            {
                "type": "code_generation",
                "description": "Generate a machine learning model for threat detection",
                "priority": 3,
                "metadata": {
                    "language": "python",
                    "framework": "scikit-learn",
                    "model_type": "classification",
                    "use_case": "threat_detection",
                },
            },
        ]

        print("\n💻 Code Generation Tasks:")
        task_ids = []

        for i, task in enumerate(code_tasks, 1):
            print(f"\n📝 Task {i}: {task['description']}")
            task_id = await amas.submit_intelligence_task(task)
            task_ids.append(task_id)
            print(f"✅ Task submitted: {task_id}")

        # Monitor code generation progress
        print("\n⏳ Monitoring code generation progress...")

        for i, (task_id, task) in enumerate(zip(task_ids, code_tasks), 1):
            status = await amas.orchestrator.get_task_status(task_id)
            print(f"  {i}. {task['description'][:50]}... - {status['status']}")

        # Demonstrate code analysis
        print("\n🔍 Code Analysis Example:")
        analysis_task = {
            "type": "code_analysis",
            "description": "Analyze security vulnerabilities in Python code",
            "priority": 2,
            "metadata": {
                "analysis_type": "security",
                "language": "python",
                "focus": "vulnerabilities",
            },
        }

        analysis_task_id = await amas.submit_intelligence_task(analysis_task)
        print(f"✅ Code analysis task submitted: {analysis_task_id}")

        # Demonstrate code optimization
        print("\n⚡ Code Optimization Example:")
        optimization_task = {
            "type": "code_optimization",
            "description": "Optimize Python code for performance",
            "priority": 2,
            "metadata": {
                "optimization_type": "performance",
                "language": "python",
                "target": "execution_speed",
            },
        }

        optimization_task_id = await amas.submit_intelligence_task(optimization_task)
        print(f"✅ Code optimization task submitted: {optimization_task_id}")

        # Get system status
        print("\n📈 System Status:")
        status = await amas.get_system_status()
        print(f"  Active Agents: {status['agents']}")
        print(f"  Active Tasks: {status['active_tasks']}")
        print(f"  Completed Tasks: {status['completed_tasks']}")

        # List all tasks
        print("\n📋 All Tasks:")
        tasks = await amas.orchestrator.list_tasks()
        for task in tasks:
            print(f"  - {task['id']}: {task['description']} ({task['status']})")

        print("\n🎉 Code generation example completed!")
        print("💻 Code generation demonstrates:")
        print("  - AI-powered code generation")
        print("  - Multiple programming languages")
        print("  - Security-focused development")
        print("  - Performance optimization")
        print("  - Code analysis and review")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    finally:
        # Shutdown
        print("\n🔄 Shutting down AMAS system...")
        await amas.shutdown()
        print("✅ AMAS system shutdown complete")

    return True

if __name__ == "__main__":
    asyncio.run(code_generation_example())
