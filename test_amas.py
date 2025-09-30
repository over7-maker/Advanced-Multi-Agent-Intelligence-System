#!/usr/bin/env python3
"""
Test script for AMAS Intelligence System
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from amas.main import AMASApplication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_amas():
    """Test AMAS system"""
    try:
        logger.info("Starting AMAS test...")
        
        # Initialize AMAS application
        app = AMASApplication()
        await app.initialize()
        
        logger.info("AMAS system initialized successfully")
        
        # Test system status
        status = await app.get_system_status()
        logger.info(f"System status: {status}")
        
        # Test submitting a task
        task_id = await app.submit_task({
            'type': 'osint',
            'description': 'Test OSINT task',
            'parameters': {'keywords': ['test', 'intelligence']},
            'priority': 2
        })
        logger.info(f"Task submitted: {task_id}")
        
        # Wait a bit for task processing
        await asyncio.sleep(2)
        
        # Get task result
        result = await app.get_task_result(task_id)
        logger.info(f"Task result: {result}")
        
        # Shutdown
        await app.shutdown()
        logger.info("AMAS test completed successfully")
        
    except Exception as e:
        logger.error(f"AMAS test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_amas())