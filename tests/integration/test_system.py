"""
Test script for AMAS Intelligence System
"""

import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

async def test_amas_system():
    """Test the AMAS Intelligence System"""
    try:
        # Import the main system
        from main import AMASIntelligenceSystem

        # Configuration
        config = {
            "llm_service_url": "http://localhost:11434",
            "vector_service_url": "http://localhost:8001",
            "graph_service_url": "http://localhost:7474",
            "n8n_url": "http://localhost:5678",
            "n8n_api_key": "your_api_key_here",
        }

        # Initialize system
        logger.info("Initializing AMAS Intelligence System...")
        amas = AMASIntelligenceSystem(config)
        await amas.initialize()

        # Test system status
        logger.info("Getting system status...")
        status = await amas.get_system_status()
        logger.info(f"System status: {status}")

        # Test task submission
        logger.info("Submitting test task...")
        task_data = {
            "type": "osint",
            "description": "Collect intelligence on emerging cyber threats",
            "priority": 2,
            "parameters": {
                "sources": ["news", "social_media", "forums"],
                "keywords": ["cyber", "threat", "security"],
            },
        }

        task_id = await amas.submit_intelligence_task(task_data)
        logger.info(f"Submitted task {task_id}")

        # Wait a bit for task processing
        await asyncio.sleep(2)

        # Get updated status
        status = await amas.get_system_status()
        logger.info(f"Updated system status: {status}")

        # Shutdown
        await amas.shutdown()
        logger.info("AMAS Intelligence System test completed successfully")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_amas_system())
