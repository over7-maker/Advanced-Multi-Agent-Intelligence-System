#!/usr/bin/env python3
"""
AMAS Unified Startup Script
Starts AMAS with the unified orchestrator and real agent implementations
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from amas.config.minimal_config import get_config_manager, validate_setup
from amas.core.unified_intelligence_orchestrator import (
    TaskPriority,
    get_task_status,
    get_unified_orchestrator,
    submit_intelligence_task,
)


async def demo_osint_analysis():
    """Demonstrate OSINT analysis capabilities"""
    print("\n🔍 OSINT Analysis Demo")
    print("-" * 30)

    # Email analysis
    print("Analyzing email: test@example.com")
    task_id = await submit_intelligence_task(
        task_type="email_analysis",
        description="Analyze test email address",
        parameters={"email": "test@example.com"},
        priority=TaskPriority.HIGH,
    )

    await asyncio.sleep(2)
    status = await get_task_status(task_id)

    if status and status["status"] == "completed":
        result = status["result"]
        print(f"✅ Analysis completed")
        print(f"   Email: {result.get('email', 'N/A')}")
        print(f"   Domain: {result.get('domain', 'N/A')}")
        print(f"   Valid: {result.get('is_valid', 'N/A')}")
        print(f"   Role-based: {result.get('is_role_based', 'N/A')}")
    else:
        print("❌ Analysis failed")


async def demo_forensics_analysis():
    """Demonstrate forensics analysis capabilities"""
    print("\n🔬 Forensics Analysis Demo")
    print("-" * 30)

    # Create a temporary test file
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("This is a test file for forensics analysis.\n")
        f.write("It contains some test data for hash calculation.\n")
        f.write("Forensics testing content here.\n")
        temp_file = f.name

    try:
        print(f"Analyzing file: {temp_file}")
        task_id = await submit_intelligence_task(
            task_type="file_analysis",
            description="Analyze test file",
            parameters={"files": [temp_file]},
            priority=TaskPriority.HIGH,
        )

        await asyncio.sleep(2)
        status = await get_task_status(task_id)

        if status and status["status"] == "completed":
            result = status["result"]
            print(f"✅ Analysis completed")
            print(f"   Files analyzed: {result.get('files_analyzed', 0)}")

            if result.get("results"):
                file_result = result["results"][0]
                print(f"   File size: {file_result.get('size_bytes', 0)} bytes")
                print(
                    f"   MD5 hash: {file_result.get('hashes', {}).get('md5', 'N/A')[:16]}..."
                )
                print(
                    f"   SHA256 hash: {file_result.get('hashes', {}).get('sha256', 'N/A')[:16]}..."
                )
        else:
            print("❌ Analysis failed")

    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)


async def demo_system_status():
    """Demonstrate system status and health check"""
    print("\n📊 System Status Demo")
    print("-" * 30)

    orchestrator = get_unified_orchestrator()

    # Get system status
    system_status = await orchestrator.get_system_status()
    print(f"Orchestrator Status: {system_status['orchestrator_status']}")
    print(f"Active Agents: {system_status['active_agents']}")
    print(f"Total Tasks: {system_status['total_tasks']}")

    # Get health check
    health = await orchestrator.health_check()
    print(f"System Health: {health['orchestrator_health']}")

    print("\nAgent Status:")
    for agent_id, agent_health in health["agents"].items():
        status_emoji = "✅" if agent_health["can_execute"] else "❌"
        print(f"  {status_emoji} {agent_health['name']} - {agent_health['status']}")


async def main():
    """Main demo function"""
    print("🚀 AMAS Unified Intelligence System")
    print("=" * 50)

    # Validate configuration
    print("🔍 Validating configuration...")
    validation = validate_setup()

    if not validation["valid"]:
        print("❌ Configuration validation failed!")
        print("Please check your API keys and configuration.")
        return 1

    print("✅ Configuration valid")

    # Show configuration level
    config_manager = get_config_manager()
    config = config_manager.get_config()
    print(f"Configuration Level: {config.config_level.value.upper()}")
    print(f"Available Providers: {len(config.available_providers)}")

    # Initialize orchestrator
    print("\n🔧 Initializing orchestrator...")
    orchestrator = get_unified_orchestrator()
    print("✅ Orchestrator initialized")

    # Run demos
    try:
        await demo_system_status()
        await demo_osint_analysis()
        await demo_forensics_analysis()

        print("\n🎉 All demos completed successfully!")
        print("\nAMAS is ready for intelligence operations.")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 AMAS shutdown requested")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
