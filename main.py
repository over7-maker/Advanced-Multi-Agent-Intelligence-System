"""
AMAS - Advanced Multi-Agent Intelligence System
Main application entry point with new unified orchestrator

This file provides the main entry point for the AMAS system with all
critical improvements from the project audit implemented.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main application entry point with unified orchestrator"""
    try:
        # Import the unified orchestrator
        from amas.core.unified_orchestrator import UnifiedIntelligenceOrchestrator

        logger.info("🚀 Starting AMAS with Unified Orchestrator")

        # Initialize the orchestrator
        orchestrator = UnifiedIntelligenceOrchestrator()
        await orchestrator.initialize()

        logger.info("✅ AMAS initialized successfully")
        logger.info("📊 System Status:")

        # Get and display system status
        status = await orchestrator.get_system_status()
        logger.info(f"  - Available Agents: {len(status['available_agents'])}")
        logger.info(f"  - Active Tasks: {status['active_tasks']}")
        logger.info(f"  - Provider Health: {status['provider_health']}")

        # Example: Submit a test task
        logger.info("🧪 Submitting test task...")
        task_id = await orchestrator.submit_task(
            agent_type="osint",
            description="Test OSINT analysis of example.com",
            priority=1,
        )
        logger.info(f"✅ Test task submitted: {task_id}")

        # Get task result
        result = await orchestrator.get_task_result(task_id)
        logger.info(f"📋 Task result: {result['status']}")

        logger.info("🎉 AMAS test completed successfully!")

    except Exception as e:
        logger.error(f"❌ Error starting AMAS: {e}")
        sys.exit(1)

    finally:
        # Cleanup
        try:
            await orchestrator.shutdown()
            logger.info("🔄 AMAS shutdown complete")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
