"""
Service Manager for AMAS Intelligence System
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .llm_service import LLMService
from .vector_service import VectorService
from .knowledge_graph_service import KnowledgeGraphService

logger = logging.getLogger(__name__)

class ServiceManager:
    """Central service manager for AMAS Intelligence System"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_service = None
        self.vector_service = None
        self.knowledge_graph_service = None
        self.services_initialized = False

    async def initialize_all_services(self):
        """Initialize all services"""
        try:
            logger.info("Initializing all services...")

            # Initialize LLM service
            self.llm_service = LLMService({
                'llm_service_url': self.config.get('llm_service_url', 'http://localhost:11434')
            })
            await self.llm_service.initialize()
            logger.info("LLM service initialized")

            # Initialize Vector service
            self.vector_service = VectorService({
                'vector_service_url': self.config.get('vector_service_url', 'http://localhost:8001'),
                'embedding_model': self.config.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2'),
                'index_path': self.config.get('index_path', '/app/faiss_index')
            })
            await self.vector_service.initialize()
            logger.info("Vector service initialized")

            # Initialize Knowledge Graph service
            self.knowledge_graph_service = KnowledgeGraphService({
                'graph_service_url': self.config.get('graph_service_url', 'bolt://localhost:7687'),
                'username': self.config.get('neo4j_username', 'neo4j'),
                'password': self.config.get('neo4j_password', 'amas123'),
                'database': self.config.get('neo4j_database', 'neo4j')
            })
            await self.knowledge_graph_service.initialize()
            logger.info("Knowledge Graph service initialized")

            self.services_initialized = True
            logger.info("All services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    async def health_check_all_services(self) -> Dict[str, Any]:
        """Check health of all services"""
        try:
            health_status = {
                'timestamp': datetime.utcnow().isoformat(),
                'services': {},
                'overall_status': 'healthy'
            }

            # Check LLM service
            if self.llm_service:
                llm_health = await self.llm_service.health_check()
                health_status['services']['llm'] = llm_health
                if llm_health.get('status') != 'healthy':
                    health_status['overall_status'] = 'degraded'

            # Check Vector service
            if self.vector_service:
                vector_health = await self.vector_service.health_check()
                health_status['services']['vector'] = vector_health
                if vector_health.get('status') != 'healthy':
                    health_status['overall_status'] = 'degraded'

            # Check Knowledge Graph service
            if self.knowledge_graph_service:
                kg_health = await self.knowledge_graph_service.health_check()
                health_status['services']['knowledge_graph'] = kg_health
                if kg_health.get('status') != 'healthy':
                    health_status['overall_status'] = 'degraded'

            return health_status

        except Exception as e:
            logger.error(f"Error checking service health: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': 'unhealthy',
                'error': str(e)
            }

    async def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics from all services"""
        try:
            stats = {
                'timestamp': datetime.utcnow().isoformat(),
                'services': {}
            }

            # Get LLM service stats
            if self.llm_service:
                stats['services']['llm'] = {
                    'models': self.llm_service.models,
                    'current_model': self.llm_service.current_model
                }

            # Get Vector service stats
            if self.vector_service:
                vector_stats = await self.vector_service.get_stats()
                stats['services']['vector'] = vector_stats

            # Get Knowledge Graph service stats
            if self.knowledge_graph_service:
                kg_stats = await self.knowledge_graph_service.get_stats()
                stats['services']['knowledge_graph'] = kg_stats

            return stats

        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }

    async def close_all_services(self):
        """Close all services"""
        try:
            if self.llm_service:
                await self.llm_service.close()
                logger.info("LLM service closed")

            if self.knowledge_graph_service:
                await self.knowledge_graph_service.close()
                logger.info("Knowledge Graph service closed")

            logger.info("All services closed successfully")

        except Exception as e:
            logger.error(f"Error closing services: {e}")

    def get_llm_service(self) -> Optional[LLMService]:
        """Get LLM service instance"""
        return self.llm_service

    def get_vector_service(self) -> Optional[VectorService]:
        """Get Vector service instance"""
        return self.vector_service

    def get_knowledge_graph_service(self) -> Optional[KnowledgeGraphService]:
        """Get Knowledge Graph service instance"""
        return self.knowledge_graph_service
