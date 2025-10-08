"""
Knowledge Graph Service Implementation for AMAS
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    from neo4j import AsyncGraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logging.warning("Neo4j driver not available")

logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    """Knowledge Graph Service for AMAS Intelligence System"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.uri = config.get("graph_service_url", "bolt://localhost:7687")
        self.username = config.get("username", "neo4j")
        self.password = config.get("password", "amas123")
        self.database = config.get("database", "neo4j")
        self.driver = None

    async def initialize(self):
        """Initialize the knowledge graph service"""
        try:
            if NEO4J_AVAILABLE:
                # Create driver
                self.driver = AsyncGraphDatabase.driver(
                    self.uri, auth=(self.username, self.password)
                )

                # Test connection
                await self.health_check()

                # Initialize schema
                await self._initialize_schema()

                logger.info("Knowledge graph service initialized successfully")
            else:
                logger.warning("Neo4j driver not available, using fallback mode")

        except Exception as e:
            logger.error(f"Failed to initialize knowledge graph service: {e}")
            raise

    async def _initialize_schema(self):
        """Initialize knowledge graph schema"""
        try:
            if not self.driver:
                return

            async with self.driver.session(database=self.database) as session:
                # Create constraints and indexes
                constraints = [
                    "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
                    "CREATE CONSTRAINT relationship_id IF NOT EXISTS FOR (r:Relationship) REQUIRE r.id IS UNIQUE",
                    "CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
                ]

                for constraint in constraints:
                    try:
                        await session.run(constraint)
                    except Exception as e:
                        logger.warning(f"Constraint creation warning: {e}")

                logger.info("Knowledge graph schema initialized")

        except Exception as e:
            logger.error(f"Error initializing schema: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Check knowledge graph service health"""
        try:
            if not self.driver:
                return {
                    "status": "unhealthy",
                    "error": "Driver not initialized",
                    "timestamp": datetime.utcnow().isoformat(),
                    "service": "knowledge_graph",
                }

            async with self.driver.session(database=self.database) as session:
                result = await session.run("RETURN 1 as test")
                record = await result.single()

                if record and record["test"] == 1:
                    return {
                        "status": "healthy",
                        "timestamp": datetime.utcnow().isoformat(),
                        "service": "knowledge_graph",
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": "Connection test failed",
                        "timestamp": datetime.utcnow().isoformat(),
                        "service": "knowledge_graph",
                    }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "service": "knowledge_graph",
            }

    async def add_entity(
        self, entity_id: str, entity_type: str, properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add an entity to the knowledge graph"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver not initialized",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            async with self.driver.session(database=self.database) as session:
                query = """
                MERGE (e:Entity {id: $entity_id})
                SET e.type = $entity_type,
                    e.properties = $properties,
                    e.created_at = datetime(),
                    e.updated_at = datetime()
                RETURN e
                """

                result = await session.run(
                    query,
                    entity_id=entity_id,
                    entity_type=entity_type,
                    properties=properties,
                )

                record = await result.single()
                if record:
                    return {
                        "success": True,
                        "entity_id": entity_id,
                        "entity_type": entity_type,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to create entity",
                        "timestamp": datetime.utcnow().isoformat(),
                    }

        except Exception as e:
            logger.error(f"Error adding entity: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Add a relationship between entities"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver not initialized",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            async with self.driver.session(database=self.database) as session:
                query = """
                MATCH (source:Entity {id: $source_id})
                MATCH (target:Entity {id: $target_id})
                MERGE (source)-[r:RELATIONSHIP {type: $relationship_type}]->(target)
                SET r.properties = $properties,
                    r.created_at = datetime(),
                    r.updated_at = datetime()
                RETURN r
                """

                result = await session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=relationship_type,
                    properties=properties or {},
                )

                record = await result.single()
                if record:
                    return {
                        "success": True,
                        "source_id": source_id,
                        "target_id": target_id,
                        "relationship_type": relationship_type,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to create relationship",
                        "timestamp": datetime.utcnow().isoformat(),
                    }

        except Exception as e:
            logger.error(f"Error adding relationship: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def query_entities(
        self,
        entity_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Query entities from the knowledge graph"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver not initialized",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            async with self.driver.session(database=self.database) as session:
                if entity_type:
                    query = """
                    MATCH (e:Entity {type: $entity_type})
                    RETURN e
                    LIMIT $limit
                    """
                    result = await session.run(
                        query, entity_type=entity_type, limit=limit
                    )
                else:
                    query = """
                    MATCH (e:Entity)
                    RETURN e
                    LIMIT $limit
                    """
                    result = await session.run(query, limit=limit)

                entities = []
                async for record in result:
                    entity = dict(record["e"])
                    entities.append(entity)

                return {
                    "success": True,
                    "entities": entities,
                    "count": len(entities),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error querying entities: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def find_path(
        self, source_id: str, target_id: str, max_depth: int = 5
    ) -> Dict[str, Any]:
        """Find path between two entities"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver not initialized",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            async with self.driver.session(database=self.database) as session:
                query = """
                MATCH path = shortestPath((source:Entity {id: $source_id})-[*1..$max_depth]-(target:Entity {id: $target_id}))
                RETURN path
                """

                result = await session.run(
                    query, source_id=source_id, target_id=target_id, max_depth=max_depth
                )

                paths = []
                async for record in result:
                    path = record["path"]
                    paths.append(
                        {
                            "length": len(path.relationships),
                            "nodes": [dict(node) for node in path.nodes],
                            "relationships": [dict(rel) for rel in path.relationships],
                        }
                    )

                return {
                    "success": True,
                    "paths": paths,
                    "path_count": len(paths),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error finding path: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "Driver not initialized",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            async with self.driver.session(database=self.database) as session:
                # Get entity count
                entity_result = await session.run(
                    "MATCH (e:Entity) RETURN count(e) as entity_count"
                )
                entity_record = await entity_result.single()
                entity_count = entity_record["entity_count"] if entity_record else 0

                # Get relationship count
                rel_result = await session.run(
                    "MATCH ()-[r]->() RETURN count(r) as relationship_count"
                )
                rel_record = await rel_result.single()
                relationship_count = (
                    rel_record["relationship_count"] if rel_record else 0
                )

                return {
                    "success": True,
                    "entity_count": entity_count,
                    "relationship_count": relationship_count,
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def close(self):
        """Close the knowledge graph service"""
        if self.driver:
            await self.driver.close()
