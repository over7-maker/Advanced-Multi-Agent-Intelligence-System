"""
Service Manager for AMAS Intelligence System

This module provides centralized management of all AMAS services,
including initialization, health monitoring, and graceful shutdown.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from .knowledge_graph_service import KnowledgeGraphService
from .llm_service import LLMService
from .vector_service import VectorService

logger = logging.getLogger(__name__)


class ServiceManager:
    """
    Central service manager for AMAS Intelligence System.

    This class manages the lifecycle of all AMAS services, including
    initialization, health monitoring, and graceful shutdown.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize the service manager.

        Args:
            config: Configuration object or dictionary
        """
        self.config: Dict[str, Any] = (
            config.__dict__ if hasattr(config, "__dict__") else config
        )
        self.llm_service: Optional[LLMService] = None
        self.vector_service: Optional[VectorService] = None
        self.knowledge_graph_service: Optional[KnowledgeGraphService] = None
        self.database_service: Optional[DatabaseService] = None
        self.security_service: Optional[SecurityService] = None
        self.services_initialized: bool = False
        self._initialization_errors: List[str] = []

    async def initialize_all_services(self) -> None:
        """
        Initialize all services with proper error handling.

        Raises:
            RuntimeError: If critical services fail to initialize
        """
        if self.services_initialized:
            logger.warning("Services already initialized")
            return

        try:
            logger.info("Initializing all services...")
            self._initialization_errors.clear()

            # Initialize LLM service
            self.llm_service = LLMService(
                {
                    "llm_service_url": self.config.get(
                        "llm_service_url", "http://localhost:11434"
                    )
                }
            )
            await self.llm_service.initialize()
            logger.info("LLM service initialized")

            # Initialize Vector service
            self.vector_service = VectorService(
                {
                    "vector_service_url": self.config.get(
                        "vector_service_url", "http://localhost:8001"
                    ),
                    "embedding_model": self.config.get(
                        "embedding_model", "sentence-transformers/all-MiniLM-L6-v2"
                    ),
                    "index_path": self.config.get("index_path", "/app/faiss_index"),
                }
            )
            await self.vector_service.initialize()
            logger.info("Vector service initialized")

            # Initialize Knowledge Graph service
            self.knowledge_graph_service = KnowledgeGraphService(
                {
                    "graph_service_url": self.config.get(
                        "graph_service_url", "bolt://localhost:7687"
                    ),
                    "username": self.config.get("neo4j_username", "neo4j"),
                    "password": self.config.get("neo4j_password", "amas123"),
                    "database": self.config.get("neo4j_database", "neo4j"),
                }
            )
            await self.knowledge_graph_service.initialize()
            logger.info("Knowledge Graph service initialized")

            self.services_initialized = True
            logger.info("All services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            await self._cleanup_failed_services()
            raise RuntimeError(f"Service initialization failed: {e}") from e

    async def _initialize_llm_service(self) -> None:
        """Initialize LLM service."""
        try:
            self.llm_service = LLMService(
                {
                    "llm_service_url": self.config.get("llm", {}).get(
                        "url", "http://localhost:11434"
                    ),
                    "deepseek_api_key": self.config.get("deepseek_api_key"),
                    "glm_api_key": self.config.get("glm_api_key"),
                    "grok_api_key": self.config.get("grok_api_key"),
                }
            )
            await self.llm_service.initialize()
            logger.info("LLM service initialized")
        except Exception as e:
            error_msg = f"LLM service initialization failed: {e}"
            logger.error(error_msg)
            self._initialization_errors.append(error_msg)
            raise

    async def _initialize_vector_service(self) -> None:
        """Initialize Vector service."""
        try:
            self.vector_service = VectorService(
                {
                    "vector_service_url": self.config.get(
                        "vector_service_url", "/app/faiss_index"
                    ),
                    "embedding_model": self.config.get(
                        "embedding_model", "sentence-transformers/all-MiniLM-L6-v2"
                    ),
                    "index_path": self.config.get("index_path", "/app/faiss_index"),
                }
            )
            await self.vector_service.initialize()
            logger.info("Vector service initialized")
        except Exception as e:
            error_msg = f"Vector service initialization failed: {e}"
            logger.error(error_msg)
            self._initialization_errors.append(error_msg)
            raise

    async def _initialize_knowledge_graph_service(self) -> None:
        """Initialize Knowledge Graph service."""
        try:
            self.knowledge_graph_service = KnowledgeGraphService(
                {
                    "graph_service_url": self.config.get("neo4j", {}).get(
                        "uri", "bolt://localhost:7687"
                    ),
                    "username": self.config.get("neo4j", {}).get("user", "neo4j"),
                    "password": self.config.get("neo4j", {}).get("password", "amas123"),
                    "database": self.config.get("neo4j", {}).get("database", "neo4j"),
                }
            )
            await self.knowledge_graph_service.initialize()
            logger.info("Knowledge Graph service initialized")
        except Exception as e:
            error_msg = f"Knowledge Graph service initialization failed: {e}"
            logger.error(error_msg)
            self._initialization_errors.append(error_msg)
            raise

    async def _initialize_database_service(self) -> None:
        """Initialize Database service."""
        try:
            self.database_service = DatabaseService(self.config)
            await self.database_service.initialize()
            logger.info("Database service initialized")
        except Exception as e:
            error_msg = f"Database service initialization failed: {e}"
            logger.error(error_msg)
            self._initialization_errors.append(error_msg)
            raise

    async def _initialize_security_service(self) -> None:
        """Initialize Security service."""
        try:
            self.security_service = SecurityService(self.config)
            await self.security_service.initialize()
            logger.info("Security service initialized")
        except Exception as e:
            error_msg = f"Security service initialization failed: {e}"
            logger.error(error_msg)
            self._initialization_errors.append(error_msg)
            raise

    async def _cleanup_failed_services(self) -> None:
        """Cleanup services that were partially initialized."""
        services = [
            ("llm_service", self.llm_service),
            ("vector_service", self.vector_service),
            ("knowledge_graph_service", self.knowledge_graph_service),
            ("database_service", self.database_service),
            ("security_service", self.security_service),
        ]

        for service_name, service in services:
            if service:
                try:
                    await service.close()
                    logger.info(f"Cleaned up {service_name}")
                except Exception as e:
                    logger.error(f"Error cleaning up {service_name}: {e}")

    async def health_check_all_services(self) -> Dict[str, Any]:
        """Check health of all services"""
        try:
            health_status = {
                "timestamp": datetime.utcnow().isoformat(),
                "services": {},
                "overall_status": "healthy",
            }

            # Check LLM service
            if self.llm_service:
                llm_health = await self.llm_service.health_check()
                health_status["services"]["llm"] = llm_health
                if llm_health.get("status") != "healthy":
                    health_status["overall_status"] = "degraded"

            # Check Vector service
            if self.vector_service:
                vector_health = await self.vector_service.health_check()
                health_status["services"]["vector"] = vector_health
                if vector_health.get("status") != "healthy":
                    health_status["overall_status"] = "degraded"

            # Check Knowledge Graph service
            if self.knowledge_graph_service:
                kg_health = await self.knowledge_graph_service.health_check()
                health_status["services"]["knowledge_graph"] = kg_health
                if kg_health.get("status") != "healthy":
                    health_status["overall_status"] = "degraded"

            # Check Database service
            if self.database_service:
                db_health = await self.database_service.health_check()
                health_status["services"]["database"] = db_health
                if db_health.get("status") != "healthy":
                    health_status["overall_status"] = "degraded"

            # Check Security service
            if self.security_service:
                sec_health = await self.security_service.health_check()
                health_status["services"]["security"] = sec_health
                if sec_health.get("status") != "healthy":
                    health_status["overall_status"] = "degraded"

            return health_status

        except Exception as e:
            logger.error(f"Error checking service health: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "unhealthy",
                "error": str(e),
            }

    async def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics from all services"""
        try:
            stats = {"timestamp": datetime.utcnow().isoformat(), "services": {}}

            # Get LLM service stats
            if self.llm_service:
                stats["services"]["llm"] = {
                    "models": self.llm_service.models,
                    "current_model": self.llm_service.current_model,
                }

            # Get Vector service stats
            if self.vector_service:
                vector_stats = await self.vector_service.get_stats()
                stats["services"]["vector"] = vector_stats

            # Get Knowledge Graph service stats
            if self.knowledge_graph_service:
                kg_stats = await self.knowledge_graph_service.get_stats()
                stats["services"]["knowledge_graph"] = kg_stats

            return stats

        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            return {"timestamp": datetime.utcnow().isoformat(), "error": str(e)}

    async def close_all_services(self):
        """Close all services"""
        try:
            if self.llm_service:
                await self.llm_service.close()
                logger.info("LLM service closed")

            if self.vector_service:
                await self.vector_service.close()
                logger.info("Vector service closed")

            if self.knowledge_graph_service:
                await self.knowledge_graph_service.close()
                logger.info("Knowledge Graph service closed")

            if self.database_service:
                await self.database_service.close()
                logger.info("Database service closed")

            if self.security_service:
                await self.security_service.close()
                logger.info("Security service closed")

            logger.info("All services closed successfully")

        except Exception as e:
            logger.error(f"Error closing services: {e}")

    async def shutdown(self):
        """Shutdown all services"""
        await self.close_all_services()

    def get_llm_service(self) -> Optional[LLMService]:
        """Get LLM service instance"""
        return self.llm_service

    def get_vector_service(self) -> Optional[VectorService]:
        """Get Vector service instance"""
        return self.vector_service

    def get_knowledge_graph_service(self) -> Optional[KnowledgeGraphService]:
        """Get Knowledge Graph service instance"""
        return self.knowledge_graph_service

    def get_database_service(self) -> Optional[DatabaseService]:
        """Get Database service instance"""
        return self.database_service

    def get_security_service(self) -> Optional[SecurityService]:
        """Get Security service instance"""
        return self.security_service

    async def shutdown(self):
        """Shutdown all services"""
        try:
            await self.close_all_services()
            logger.info("All services shutdown successfully")
        except Exception as e:
            logger.error(f"Error during service shutdown: {e}")
