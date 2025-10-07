"""
AMAS Intelligence System - Main Application Entry Point

This is the main entry point for the Advanced Multi-Agent Intelligence System.
It provides a clean, professional interface for initializing and managing the system.
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

from .config.settings import get_settings, AMASConfig
from .core.orchestrator import IntelligenceOrchestrator
from .services.service_manager import ServiceManager


class AMASApplication:
    """
    Main AMAS Application class.

    This class manages the lifecycle of the AMAS Intelligence System,
    including initialization, configuration, and graceful shutdown.
    """

    def __init__(self, config_override: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the AMAS application.

        Args:
            config_override: Optional configuration overrides to apply
        """
        self.config: AMASConfig = get_settings()
        if config_override:
            self._apply_config_overrides(config_override)

        self.orchestrator: Optional[IntelligenceOrchestrator] = None
        self.service_manager: Optional[ServiceManager] = None
        self.logger: logging.Logger = self._setup_logging()
        self._is_initialized: bool = False
        self._is_running: bool = False

    def _apply_config_overrides(self, overrides: Dict[str, Any]) -> None:
        """
        Apply configuration overrides to the current config.

        Args:
            overrides: Dictionary of configuration overrides
        """
        for key, value in overrides.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                self.logger.warning(f"Unknown configuration key: {key}")

    def _setup_logging(self) -> logging.Logger:
        """
        Setup application logging with proper configuration.

        Returns:
            Configured logger instance
        """
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
        """
        Initialize all system components.

        Raises:
            RuntimeError: If initialization fails
        """
        if self._is_initialized:
            self.logger.warning("System already initialized")
            return

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

            self._is_initialized = True
            self.logger.info("AMAS Intelligence System initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize AMAS system: {e}")
            await self._cleanup_on_failure()
            raise RuntimeError(f"System initialization failed: {e}") from e

    async def _cleanup_on_failure(self) -> None:
        """Cleanup resources when initialization fails."""
        try:
            if self.service_manager:
                await self.service_manager.shutdown()
            if self.orchestrator:
                await self.orchestrator.shutdown()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    async def start(self) -> None:
        """
        Start the AMAS system and begin operation.

        This method initializes the system and keeps it running until
        a shutdown signal is received.
        """
        if self._is_running:
            self.logger.warning("System is already running")
            return

        try:
            await self.initialize()
            self._is_running = True
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

    async def _run_main_loop(self) -> None:
        """Run the main application loop with health checks."""
        while self._is_running:
            try:
                await asyncio.sleep(10)
                await self._perform_health_check()
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _perform_health_check(self) -> None:
        """Perform periodic health checks on the system."""
        if not self.orchestrator:
            return

        try:
            status = await self.orchestrator.get_system_status()
            if status.get("status") != "operational":
                self.logger.warning(f"System status: {status}")
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

    async def submit_task(self, task_data: Dict[str, Any]) -> str:
        """
        Submit a task to the system.

        Args:
            task_data: Task definition containing type, description, parameters, and priority

        Returns:
            Task ID for tracking

        Raises:
            RuntimeError: If system is not initialized
            ValueError: If task data is invalid
        """
        if not self._is_initialized or not self.orchestrator:
            raise RuntimeError("System not initialized")

        if not isinstance(task_data, dict):
            raise ValueError("Task data must be a dictionary")

        required_fields = ["type", "description"]
        for field in required_fields:
            if field not in task_data:
                raise ValueError(f"Task data missing required field: {field}")

        return await self.orchestrator.submit_task(
            task_type=task_data.get("type", "general"),
            description=task_data.get("description", ""),
            parameters=task_data.get("parameters", {}),
            priority=task_data.get("priority", 2),
        )

    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Get task result by task ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task result data

        Raises:
            RuntimeError: If system is not initialized
            ValueError: If task_id is invalid
        """
        if not self._is_initialized or not self.orchestrator:
            raise RuntimeError("System not initialized")

        if not task_id or not isinstance(task_id, str):
            raise ValueError("Task ID must be a non-empty string")

        return await self.orchestrator.get_task_result(task_id)

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status.

        Returns:
            System status information
        """
        if not self._is_initialized or not self.orchestrator:
            return {"status": "not_initialized"}

        return await self.orchestrator.get_system_status()

    async def shutdown(self) -> None:
        """
        Shutdown the system gracefully.

        This method ensures all resources are properly cleaned up
        and all services are stopped in the correct order.
        """
        if not self._is_initialized:
            self.logger.warning("System not initialized, nothing to shutdown")
            return

        try:
            self.logger.info("Shutting down AMAS Intelligence System...")
            self._is_running = False

            # Shutdown orchestrator first
            if self.orchestrator:
                await self.orchestrator.shutdown()
                self.orchestrator = None

            # Shutdown service manager
            if self.service_manager:
                await self.service_manager.shutdown()
                self.service_manager = None

            self._is_initialized = False
            self.logger.info("AMAS Intelligence System shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    @asynccontextmanager
    async def context(self):
        """
        Context manager for AMAS application.

        Usage:
            async with AMASApplication().context() as app:
                # Use app here
                pass
        """
        try:
            await self.initialize()
            yield self
        finally:
            await self.shutdown()


async def main() -> None:
    """
    Main application entry point.

    This function creates and starts the AMAS application.
    """
    app = AMASApplication()
    await app.start()


if __name__ == "__main__":
    asyncio.run(main())
