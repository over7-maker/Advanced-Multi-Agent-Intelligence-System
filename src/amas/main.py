"""
AMAS Intelligence System - Main Application Entry Point

This is the main entry point for the Advanced Multi-Agent Intelligence System.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from .config import get_settings
from .core.orchestrator import IntelligenceOrchestrator
from .services.service_manager import ServiceManager


class AMASApplication:
    """Main AMAS Application class"""

    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """Initialize the AMAS application"""
        self.config = get_settings()
        if config_override:
            # Update config with overrides
            for key, value in config_override.items():
                setattr(self.config, key, value)

        self.orchestrator: Optional[IntelligenceOrchestrator] = None
        self.service_manager: Optional[ServiceManager] = None
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup application logging"""
        # Ensure logs directory exists
        self.config.logs_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format=self.config.log_format,
            handlers=[
                logging.FileHandler(self.config.logs_dir / "amas.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )

        logger = logging.getLogger(__name__)
        logger.info(
            f"AMAS v{self.config.version} starting in {self.config.environment} mode"
        )
        return logger

    async def initialize(self) -> None:
        """Initialize all system components"""
        try:
            self.logger.info("Initializing AMAS Intelligence System...")

            # Initialize service manager
            self.service_manager = ServiceManager(self.config)
            await self.service_manager.initialize_all_services()

            # Initialize orchestrator
            self.orchestrator = IntelligenceOrchestrator(
                config=self.config, service_manager=self.service_manager
            )
            await self.orchestrator.initialize()

            self.logger.info("AMAS Intelligence System initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize AMAS system: {e}")
            raise

    async def start(self) -> None:
        """Start the AMAS system"""
        try:
            await self.initialize()

            self.logger.info("AMAS Intelligence System is ready and operational")

            # Keep the system running
            while True:
                await asyncio.sleep(10)
                # Perform health checks
                if self.orchestrator:
                    status = await self.orchestrator.get_system_status()
                    if status.get("status") != "operational":
                        self.logger.warning(f"System status: {status}")

        except KeyboardInterrupt:
            self.logger.info("Shutdown signal received")
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            raise
        finally:
            await self.shutdown()

    async def submit_task(self, task_data: Dict[str, Any]) -> str:
        """Submit a task to the system"""
        if not self.orchestrator:
            raise RuntimeError("System not initialized")

        return await self.orchestrator.submit_task(
            task_type=task_data.get("type", "general"),
            description=task_data.get("description", ""),
            parameters=task_data.get("parameters", {}),
            priority=task_data.get("priority", 2),
        )

    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """Get task result"""
        if not self.orchestrator:
            raise RuntimeError("System not initialized")

        return await self.orchestrator.get_task_result(task_id)

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        if not self.orchestrator:
            return {"status": "not_initialized"}

        return await self.orchestrator.get_system_status()

    async def shutdown(self) -> None:
        """Shutdown the system gracefully"""
        try:
            self.logger.info("Shutting down AMAS Intelligence System...")

            if self.orchestrator:
                await self.orchestrator.shutdown()

            if self.service_manager:
                await self.service_manager.shutdown()

            self.logger.info("AMAS Intelligence System shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


async def main():
    """Main application entry point"""
    app = AMASApplication()
    await app.start()


if __name__ == "__main__":
    asyncio.run(main())
