#!/usr/bin/env python3
"""
AMAS Intelligence System - Minimal Working Example
Demonstrates basic system functionality without external dependencies
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Import AMAS system
from main import AMASIntelligenceSystem


class MinimalAMASExample:
    """Minimal example demonstrating AMAS functionality"""

    def __init__(self):
        self.amas_system = None

    async def initialize_system(self):
        """Initialize the AMAS system with minimal configuration"""
        try:
            logger.info("Initializing AMAS Intelligence System (Minimal Mode)...")

            # Minimal configuration - no external services required
            config = {
                "llm_service_url": "http://localhost:11434",  # Will use fallback
                "vector_service_url": "http://localhost:8001",  # Will use fallback
                "graph_service_url": "bolt://localhost:7687",  # Will use fallback
                "postgres_host": "localhost",
                "postgres_port": 5432,
                "postgres_user": "amas",
                "postgres_password": "amas123",
                "postgres_db": "amas",
                "redis_host": "localhost",
                "redis_port": 6379,
                "redis_db": 0,
                "neo4j_username": "neo4j",
                "neo4j_password": "amas123",
                "neo4j_database": "neo4j",
                "jwt_secret": "amas_jwt_secret_key_2024_secure",
                "encryption_key": Fernet.generate_key(),
                "deepseek_api_key": "demo_key",
                "glm_api_key": "demo_key",
                "grok_api_key": "demo_key",
                "n8n_url": "http://localhost:5678",
                "n8n_api_key": "demo_key",
            }

            # Initialize AMAS system
            self.amas_system = AMASIntelligenceSystem(config)
            await self.amas_system.initialize()

            logger.info(
                "AMAS Intelligence System initialized successfully (Minimal Mode)"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize AMAS system: {e}")
            return False

    async def demonstrate_osint_task(self):
        """Demonstrate OSINT task execution"""
        try:
            logger.info("Demonstrating OSINT task execution...")

            # Create OSINT task
            task_data = {
                "type": "osint",
                "description": "Collect intelligence on emerging cyber threats",
                "parameters": {
                    "keywords": ["cyber", "threat", "security"],
                    "sources": ["news", "social_media"],
                    "time_range": "24h",
                },
                "priority": 2,
            }

            # Submit task
            task_id = await self.amas_system.submit_intelligence_task(task_data)
            logger.info(f"OSINT task submitted with ID: {task_id}")

            # Get system status
            status = await self.amas_system.get_system_status()
            logger.info(f"System status: {status}")

            return task_id

        except Exception as e:
            logger.error(f"Error demonstrating OSINT task: {e}")
            return None

    async def demonstrate_investigation_task(self):
        """Demonstrate investigation task execution"""
        try:
            logger.info("Demonstrating investigation task execution...")

            # Create investigation task
            task_data = {
                "type": "investigation",
                "description": "Investigate suspicious network activity",
                "parameters": {
                    "target": "suspicious_entity",
                    "analysis_type": "network",
                    "time_range": "7d",
                },
                "priority": 3,
            }

            # Submit task
            task_id = await self.amas_system.submit_intelligence_task(task_data)
            logger.info(f"Investigation task submitted with ID: {task_id}")

            return task_id

        except Exception as e:
            logger.error(f"Error demonstrating investigation task: {e}")
            return None

    async def demonstrate_system_capabilities(self):
        """Demonstrate system capabilities"""
        try:
            logger.info("Demonstrating system capabilities...")

            # Get system status
            status = await self.amas_system.get_system_status()
            logger.info(f"System Status: {status}")

            # Demonstrate agent registration
            logger.info("Available agents:")
            for agent_id, agent in self.amas_system.agents.items():
                logger.info(f"  - {agent_id}: {agent.name}")

            # Demonstrate task submission
            tasks = [
                {
                    "type": "osint",
                    "description": "Monitor social media for security threats",
                    "priority": 2,
                },
                {
                    "type": "investigation",
                    "description": "Analyze network traffic patterns",
                    "priority": 3,
                },
                {
                    "type": "forensics",
                    "description": "Examine digital evidence",
                    "priority": 4,
                },
            ]

            submitted_tasks = []
            for task_data in tasks:
                task_id = await self.amas_system.submit_intelligence_task(task_data)
                submitted_tasks.append(task_id)
                logger.info(f"Submitted task: {task_data['type']} (ID: {task_id})")

            return submitted_tasks

        except Exception as e:
            logger.error(f"Error demonstrating system capabilities: {e}")
            return []

    async def run_demonstration(self):
        """Run the complete demonstration"""
        try:
            logger.info("=" * 60)
            logger.info("AMAS Intelligence System - Minimal Working Example")
            logger.info("=" * 60)

            # Initialize system
            if not await self.initialize_system():
                logger.error("Failed to initialize system")
                return False

            # Demonstrate capabilities
            tasks = await self.demonstrate_system_capabilities()

            # Demonstrate specific task types
            osint_task = await self.demonstrate_osint_task()
            investigation_task = await self.demonstrate_investigation_task()

            # Final status
            final_status = await self.amas_system.get_system_status()
            logger.info(f"Final system status: {final_status}")

            logger.info("=" * 60)
            logger.info("Demonstration completed successfully!")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Error in demonstration: {e}")
            return False
        finally:
            # Cleanup
            if self.amas_system:
                await self.amas_system.shutdown()


async def main():
    """Main function"""
    try:
        example = MinimalAMASExample()
        success = await example.run_demonstration()

        if success:
            logger.info(
                "AMAS Intelligence System demonstration completed successfully!"
            )
            return 0
        else:
            logger.error("AMAS Intelligence System demonstration failed!")
            return 1

    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
