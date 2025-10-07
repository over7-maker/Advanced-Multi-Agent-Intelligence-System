#!/usr/bin/env python3
"""
AMAS Main Application with Dashboard

This module provides the main entry point for the Advanced Multi-Agent Intelligence System,
integrating all components including the orchestrator, agents, services, and dashboard API.
"""

import asyncio
import logging
import signal
import sys
import threading
from typing import Dict, Any, Optional

from .core.unified_orchestrator_v2 import UnifiedOrchestratorV2
from .services.service_manager import ServiceManager
from .services.universal_ai_manager import get_universal_ai_manager
from .api.dashboard_api import create_dashboard_api
from .agents.rag_agent import RAGAgent
from .agents.tool_agent import ToolAgent
from .agents.planning_agent import PlanningAgent
from .agents.code_agent import CodeAgent
from .agents.data_agent import DataAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('amas.log')
    ]
)

logger = logging.getLogger(__name__)

class AMASApplicationWithDashboard:
    """
    Main AMAS Application class that orchestrates all system components with dashboard.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AMAS application.

        Args:
            config: Configuration dictionary for the application
        """
        self.config = config or self._get_default_config()
        self.orchestrator: Optional[UnifiedOrchestratorV2] = None
        self.service_manager: Optional[ServiceManager] = None
        self.dashboard_api = None
        self.api_thread: Optional[threading.Thread] = None
        self.running = False
        
        logger.info("AMAS Application with Dashboard initialized")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the application."""
        return {
            "orchestrator": {
                "max_concurrent_tasks": 10,
                "task_timeout": 300
            },
            "agents": {
                "rag_agent": {
                    "name": "RAG Agent Alpha",
                    "capabilities": ["information_retrieval", "data_synthesis", "qa"],
                    "initial_llm_temperature": 0.7,
                    "initial_llm_max_tokens": 1000
                },
                "tool_agent": {
                    "name": "Tool Agent Beta",
                    "capabilities": ["tool_execution"],
                    "tools": [
                        {"name": "web_search", "function_path": "tools.web_search"},
                        {"name": "file_processor", "function_path": "tools.file_processor"}
                    ]
                },
                "planning_agent": {
                    "name": "Planning Agent Gamma",
                    "capabilities": ["task_planning", "plan_refinement", "resource_allocation"]
                },
                "code_agent": {
                    "name": "Code Agent Delta",
                    "capabilities": ["code_generation", "code_execution", "code_debugging"]
                },
                "data_agent": {
                    "name": "Data Agent Epsilon",
                    "capabilities": ["data_analysis", "data_processing", "data_visualization"]
                }
            },
            "services": {
                "vector_service": {
                    "enabled": True,
                    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
                },
                "knowledge_graph_service": {
                    "enabled": True,
                    "graph_type": "networkx"
                }
            },
            "api": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False
            }
        }

    async def initialize(self):
        """Initialize all system components."""
        try:
            logger.info("Initializing AMAS system components...")

            # Initialize Universal AI Manager
            universal_ai_manager = get_universal_ai_manager()
            logger.info("Universal AI Manager initialized")

            # Initialize Service Manager
            self.service_manager = ServiceManager(self.config.get("services", {}))
            await self.service_manager.initialize()
            logger.info("Service Manager initialized")

            # Initialize Orchestrator
            self.orchestrator = UnifiedOrchestratorV2(
                universal_ai_manager=universal_ai_manager,
                vector_service=self.service_manager.get_vector_service(),
                knowledge_graph=self.service_manager.get_knowledge_graph_service(),
                security_service=None  # Placeholder for future security service
            )
            logger.info("Unified Orchestrator initialized")

            # Initialize and register agents
            await self._initialize_agents()
            logger.info("Agents initialized and registered")

            # Initialize Dashboard API
            self.dashboard_api = create_dashboard_api(self.orchestrator, self.service_manager)
            logger.info("Dashboard API initialized")

            logger.info("AMAS system initialization completed successfully")

        except Exception as e:
            logger.error(f"Failed to initialize AMAS system: {e}")
            raise

    async def _initialize_agents(self):
        """Initialize and register all agents with the orchestrator."""
        agent_configs = self.config.get("agents", {})
        message_bus = self.orchestrator.get_message_bus()

        # RAG Agent
        if "rag_agent" in agent_configs:
            rag_agent = RAGAgent(
                agent_id="rag_agent_001",
                config=agent_configs["rag_agent"],
                orchestrator=self.orchestrator,
                message_bus=message_bus
            )
            await self.orchestrator.register_agent(rag_agent)
            logger.info("RAG Agent registered")

        # Tool Agent
        if "tool_agent" in agent_configs:
            tool_agent = ToolAgent(
                agent_id="tool_agent_001",
                config=agent_configs["tool_agent"],
                orchestrator=self.orchestrator,
                message_bus=message_bus
            )
            await self.orchestrator.register_agent(tool_agent)
            logger.info("Tool Agent registered")

        # Planning Agent
        if "planning_agent" in agent_configs:
            planning_agent = PlanningAgent(
                agent_id="planning_agent_001",
                config=agent_configs["planning_agent"],
                orchestrator=self.orchestrator,
                message_bus=message_bus
            )
            await self.orchestrator.register_agent(planning_agent)
            logger.info("Planning Agent registered")

        # Code Agent
        if "code_agent" in agent_configs:
            code_agent = CodeAgent(
                agent_id="code_agent_001",
                config=agent_configs["code_agent"],
                orchestrator=self.orchestrator,
                message_bus=message_bus
            )
            await self.orchestrator.register_agent(code_agent)
            logger.info("Code Agent registered")

        # Data Agent
        if "data_agent" in agent_configs:
            data_agent = DataAgent(
                agent_id="data_agent_001",
                config=agent_configs["data_agent"],
                orchestrator=self.orchestrator,
                message_bus=message_bus
            )
            await self.orchestrator.register_agent(data_agent)
            logger.info("Data Agent registered")

    def start_api_server(self):
        """Start the Dashboard API server in a separate thread."""
        if self.dashboard_api:
            api_config = self.config.get("api", {})
            self.api_thread = threading.Thread(
                target=self.dashboard_api.run,
                kwargs={
                    "host": api_config.get("host", "0.0.0.0"),
                    "port": api_config.get("port", 5000),
                    "debug": api_config.get("debug", False)
                },
                daemon=True
            )
            self.api_thread.start()
            logger.info(f"Dashboard API server started on {api_config.get('host', '0.0.0.0')}:{api_config.get('port', 5000)}")

    async def run(self):
        """Run the AMAS application."""
        try:
            await self.initialize()
            self.running = True
            
            # Start the API server
            self.start_api_server()
            
            logger.info("AMAS system is now running...")
            logger.info("Dashboard available at: http://localhost:5000")
            logger.info("Press Ctrl+C to stop the system")

            # Keep the main loop running
            while self.running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            logger.error(f"Error running AMAS system: {e}")
            raise
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Shutdown the AMAS application gracefully."""
        logger.info("Shutting down AMAS system...")
        self.running = False

        try:
            # Unregister all agents
            if self.orchestrator:
                for agent_id in list(self.orchestrator.agents.keys()):
                    await self.orchestrator.unregister_agent(agent_id)
                logger.info("All agents unregistered")

            # Shutdown services
            if self.service_manager:
                await self.service_manager.shutdown()
                logger.info("Service Manager shut down")

            logger.info("AMAS system shutdown completed")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        logger.info(f"Received signal {signum}")
        self.running = False


async def main():
    """Main entry point for the AMAS application with dashboard."""
    app = AMASApplicationWithDashboard()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, app.signal_handler)
    signal.signal(signal.SIGTERM, app.signal_handler)
    
    try:
        await app.run()
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
