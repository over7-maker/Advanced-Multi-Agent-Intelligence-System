#!/usr/bin/env python3
"""
Basic AMAS Orchestration Example
Demonstrates basic multi-agent orchestration
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import AMASIntelligenceSystem

async def basic_orchestration_example():
    """Basic orchestration example"""
    print("🤖 AMAS Basic Orchestration Example")
    print("=" * 50)

    # Configuration
    config = {
        'llm_service_url': 'http://localhost:11434',
        'vector_service_url': 'http://localhost:8001',
        'graph_service_url': 'http://localhost:7474',
        'n8n_url': 'http://localhost:5678',
        'n8n_api_key': 'your_api_key_here'
    }

    try:
        # Initialize AMAS system
        print("🚀 Initializing AMAS system...")
        amas = AMASIntelligenceSystem(config)
        await amas.initialize()
        print("✅ AMAS system initialized")

        # Submit OSINT task
        print("\n📊 Submitting OSINT task...")
        osint_task = {
            'type': 'osint',
            'description': 'Collect intelligence on emerging cyber threats',
            'priority': 2,
            'metadata': {
                'sources': ['news', 'social_media', 'forums'],
                'keywords': ['cyber', 'threat', 'security']
            }
        }

        task_id = await amas.submit_intelligence_task(osint_task)
        print(f"✅ OSINT task submitted: {task_id}")

        # Submit Investigation task
        print("\n🔍 Submitting Investigation task...")
        investigation_task = {
            'type': 'investigation',
            'description': 'Investigate suspicious network activity',
            'priority': 3,
            'metadata': {
                'target': 'suspicious_entity',
                'timeframe': 'last_7_days'
            }
        }

        task_id = await amas.submit_intelligence_task(investigation_task)
        print(f"✅ Investigation task submitted: {task_id}")

        # Submit Forensics task
        print("\n🔬 Submitting Forensics task...")
        forensics_task = {
            'type': 'forensics',
            'description': 'Analyze digital evidence from security incident',
            'priority': 4,
            'metadata': {
                'evidence_path': '/path/to/evidence',
                'incident_id': 'INC-2024-001'
            }
        }

        task_id = await amas.submit_intelligence_task(forensics_task)
        print(f"✅ Forensics task submitted: {task_id}")

        # Get system status
        print("\n📈 Getting system status...")
        status = await amas.get_system_status()
        print(f"System Status: {status}")

        # List agents
        print("\n👥 Available Agents:")
        agents = await amas.orchestrator.list_agents()
        for agent in agents:
            print(f"  - {agent['name']} ({agent['type']}) - {agent['status']}")

        # List tasks
        print("\n📋 Current Tasks:")
        tasks = await amas.orchestrator.list_tasks()
        for task in tasks:
            print(f"  - {task['id']}: {task['description']} ({task['status']})")

        print("\n🎉 Basic orchestration example completed!")

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
    asyncio.run(basic_orchestration_example())
