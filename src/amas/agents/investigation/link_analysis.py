"""
Link Analysis Component

This module provides link analysis capabilities for the Investigation Agent,
enabling relationship discovery and network analysis.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class RelationshipType(Enum):
    """Types of relationships between entities"""

    DIRECT = "direct"
    INDIRECT = "indirect"
    ASSOCIATION = "association"
    COMMUNICATION = "communication"
    FINANCIAL = "financial"
    GEOGRAPHIC = "geographic"
    TEMPORAL = "temporal"


@dataclass
class Relationship:
    """Relationship between entities"""

    source_entity: str
    target_entity: str
    relationship_type: RelationshipType
    strength: float
    evidence: List[str]
    metadata: Dict[str, Any]
    discovered_at: datetime


@dataclass
class NetworkNode:
    """Node in the relationship network"""

    entity: str
    entity_type: str
    attributes: Dict[str, Any]
    connections: List[str]
    centrality_score: float


class LinkAnalysis:
    """
    Link analysis component for relationship discovery and network analysis.

    This component analyzes relationships between entities, discovers hidden
    connections, and performs network analysis for intelligence purposes.
    """

    def __init__(self):
        """Initialize the link analysis component."""
        self.logger = logging.getLogger("amas.link_analysis")

        # Analysis configuration
        self.config = {
            "max_relationship_depth": 3,
            "min_relationship_strength": 0.3,
            "max_entities_per_analysis": 1000,
            "relationship_types": [rt.value for rt in RelationshipType],
            "centrality_algorithms": [
                "degree",
                "betweenness",
                "closeness",
                "eigenvector",
            ],
        }

        # Analysis results cache
        self.analysis_cache = {}

        # Performance metrics
        self.metrics = {
            "analyses_performed": 0,
            "relationships_discovered": 0,
            "networks_analyzed": 0,
            "average_analysis_time": 0.0,
        }

    async def analyze_relationships(
        self,
        entities: List[Dict[str, Any]],
        depth: str,
        knowledge_graph: Any = None,
        llm_service: Any = None,
    ) -> List[Dict[str, Any]]:
        """
        Analyze relationships between entities.

        Args:
            entities: List of entities to analyze
            depth: Analysis depth (shallow, medium, deep)
            knowledge_graph: Knowledge graph service
            llm_service: LLM service for analysis

        Returns:
            List of discovered relationships
        """
        try:
            self.logger.info(f"Starting link analysis for {len(entities)} entities")
            start_time = datetime.utcnow()

            # Determine analysis parameters based on depth
            analysis_params = self._get_analysis_parameters(depth)

            # Extract entity information
            entity_list = [entity.get("entity", "") for entity in entities]

            # Perform relationship discovery
            relationships = await self._discover_relationships(
                entity_list, analysis_params, knowledge_graph, llm_service
            )

            # Perform network analysis
            network_analysis = await self._analyze_network(
                entity_list, relationships, analysis_params
            )

            # Generate insights
            insights = await self._generate_insights(
                relationships, network_analysis, llm_service
            )

            # Update metrics
            analysis_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(analysis_time, len(relationships))

            result = {
                "relationships": relationships,
                "network_analysis": network_analysis,
                "insights": insights,
                "analysis_parameters": analysis_params,
                "timestamp": datetime.utcnow().isoformat(),
            }

            self.logger.info(
                f"Link analysis completed: {len(relationships)} relationships discovered"
            )
            return result

        except Exception as e:
            self.logger.error(f"Link analysis failed: {e}")
            return []

    def _get_analysis_parameters(self, depth: str) -> Dict[str, Any]:
        """Get analysis parameters based on depth."""
        if depth == "shallow":
            return {
                "max_depth": 1,
                "min_strength": 0.7,
                "max_entities": 50,
                "include_indirect": False,
            }
        elif depth == "medium":
            return {
                "max_depth": 2,
                "min_strength": 0.5,
                "max_entities": 200,
                "include_indirect": True,
            }
        else:  # deep
            return {
                "max_depth": 3,
                "min_strength": 0.3,
                "max_entities": 500,
                "include_indirect": True,
            }

    async def _discover_relationships(
        self,
        entities: List[str],
        params: Dict[str, Any],
        knowledge_graph: Any = None,
        llm_service: Any = None,
    ) -> List[Dict[str, Any]]:
        """Discover relationships between entities."""
        try:
            relationships = []

            # Use knowledge graph if available
            if knowledge_graph:
                graph_relationships = await self._query_knowledge_graph(
                    entities, params, knowledge_graph
                )
                relationships.extend(graph_relationships)

            # Use LLM for relationship discovery if available
            if llm_service:
                llm_relationships = await self._discover_relationships_with_llm(
                    entities, params, llm_service
                )
                relationships.extend(llm_relationships)

            # Remove duplicates and filter by strength
            unique_relationships = self._deduplicate_relationships(relationships)
            filtered_relationships = [
                rel
                for rel in unique_relationships
                if rel.get("strength", 0) >= params["min_strength"]
            ]

            return filtered_relationships

        except Exception as e:
            self.logger.error(f"Relationship discovery failed: {e}")
            return []

    async def _query_knowledge_graph(
        self, entities: List[str], params: Dict[str, Any], knowledge_graph: Any
    ) -> List[Dict[str, Any]]:
        """Query knowledge graph for relationships."""
        try:
            relationships = []

            for entity in entities:
                # Query direct relationships
                direct_rels = await knowledge_graph.get_relationships(
                    entity, depth=1, limit=params["max_entities"]
                )

                for rel in direct_rels:
                    relationships.append(
                        {
                            "source_entity": entity,
                            "target_entity": rel.get("target"),
                            "relationship_type": rel.get("type", "association"),
                            "strength": rel.get("strength", 0.5),
                            "evidence": rel.get("evidence", []),
                            "metadata": rel.get("metadata", {}),
                            "source": "knowledge_graph",
                        }
                    )

                # Query indirect relationships if enabled
                if params["include_indirect"] and params["max_depth"] > 1:
                    indirect_rels = await knowledge_graph.get_relationships(
                        entity, depth=params["max_depth"], limit=params["max_entities"]
                    )

                    for rel in indirect_rels:
                        if rel.get("target") not in entities:
                            relationships.append(
                                {
                                    "source_entity": entity,
                                    "target_entity": rel.get("target"),
                                    "relationship_type": rel.get("type", "indirect"),
                                    "strength": rel.get("strength", 0.3),
                                    "evidence": rel.get("evidence", []),
                                    "metadata": rel.get("metadata", {}),
                                    "source": "knowledge_graph",
                                }
                            )

            return relationships

        except Exception as e:
            self.logger.error(f"Knowledge graph query failed: {e}")
            return []

    async def _discover_relationships_with_llm(
        self, entities: List[str], params: Dict[str, Any], llm_service: Any
    ) -> List[Dict[str, Any]]:
        """Discover relationships using LLM analysis."""
        try:
            # Create relationship discovery prompt
            prompt = f"""
Analyze relationships between the following entities for intelligence purposes:

Entities: {', '.join(entities)}

Look for:
1. Direct relationships (communication, association, financial)
2. Indirect relationships (through intermediaries)
3. Geographic connections
4. Temporal connections
5. Organizational connections

Provide analysis in JSON format:
{{
    "relationships": [
        {{
            "source_entity": "entity1",
            "target_entity": "entity2",
            "relationship_type": "direct|indirect|association|communication|financial|geographic|temporal",
            "strength": 0.0-1.0,
            "evidence": ["evidence1", "evidence2"],
            "description": "relationship description"
        }}
    ]
}}
"""

            result = await llm_service.generate(
                prompt=prompt, max_tokens=1500, temperature=0.3
            )

            # Parse result
            try:
                analysis = json.loads(result)
                relationships = analysis.get("relationships", [])

                # Add source information
                for rel in relationships:
                    rel["source"] = "llm_analysis"
                    rel["metadata"] = {"discovered_by": "llm"}

                return relationships

            except:
                return []

        except Exception as e:
            self.logger.error(f"LLM relationship discovery failed: {e}")
            return []

    def _deduplicate_relationships(
        self, relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate relationships."""
        try:
            unique_relationships = []
            seen = set()

            for rel in relationships:
                # Create unique key for relationship
                key = tuple(
                    sorted([rel.get("source_entity", ""), rel.get("target_entity", "")])
                )

                if key not in seen:
                    seen.add(key)
                    unique_relationships.append(rel)

            return unique_relationships

        except Exception as e:
            self.logger.error(f"Relationship deduplication failed: {e}")
            return relationships

    async def _analyze_network(
        self,
        entities: List[str],
        relationships: List[Dict[str, Any]],
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze the relationship network."""
        try:
            # Build network graph
            network = self._build_network_graph(entities, relationships)

            # Calculate centrality measures
            centrality_measures = self._calculate_centrality_measures(network)

            # Identify key nodes
            key_nodes = self._identify_key_nodes(network, centrality_measures)

            # Analyze network structure
            network_structure = self._analyze_network_structure(network)

            return {
                "network_size": len(network),
                "relationship_count": len(relationships),
                "centrality_measures": centrality_measures,
                "key_nodes": key_nodes,
                "network_structure": network_structure,
                "analysis_parameters": params,
            }

        except Exception as e:
            self.logger.error(f"Network analysis failed: {e}")
            return {}

    def _build_network_graph(
        self, entities: List[str], relationships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build network graph from entities and relationships."""
        try:
            network = {}

            # Initialize nodes
            for entity in entities:
                network[entity] = {
                    "entity": entity,
                    "connections": set(),
                    "incoming": set(),
                    "outgoing": set(),
                }

            # Add relationships
            for rel in relationships:
                source = rel.get("source_entity", "")
                target = rel.get("target_entity", "")

                if source in network and target in network:
                    network[source]["connections"].add(target)
                    network[source]["outgoing"].add(target)
                    network[target]["connections"].add(source)
                    network[target]["incoming"].add(source)

            return network

        except Exception as e:
            self.logger.error(f"Network graph building failed: {e}")
            return {}

    def _calculate_centrality_measures(
        self, network: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate centrality measures for network nodes."""
        try:
            centrality_measures = {}

            for node, data in network.items():
                # Degree centrality
                degree_centrality = len(data["connections"])

                # Betweenness centrality (simplified)
                betweenness_centrality = self._calculate_betweenness_centrality(
                    node, network
                )

                # Closeness centrality (simplified)
                closeness_centrality = self._calculate_closeness_centrality(
                    node, network
                )

                centrality_measures[node] = {
                    "degree": degree_centrality,
                    "betweenness": betweenness_centrality,
                    "closeness": closeness_centrality,
                }

            return centrality_measures

        except Exception as e:
            self.logger.error(f"Centrality calculation failed: {e}")
            return {}

    def _calculate_betweenness_centrality(
        self, node: str, network: Dict[str, Any]
    ) -> float:
        """Calculate betweenness centrality for a node."""
        try:
            # Simplified betweenness centrality calculation
            total_paths = 0
            paths_through_node = 0

            # This is a simplified implementation
            # In practice, you'd use a proper graph algorithm library
            for source in network:
                if source != node:
                    for target in network:
                        if target != node and target != source:
                            total_paths += 1
                            # Check if shortest path goes through node
                            if self._is_on_shortest_path(source, target, node, network):
                                paths_through_node += 1

            if total_paths == 0:
                return 0.0

            return paths_through_node / total_paths

        except Exception as e:
            self.logger.error(f"Betweenness centrality calculation failed: {e}")
            return 0.0

    def _calculate_closeness_centrality(
        self, node: str, network: Dict[str, Any]
    ) -> float:
        """Calculate closeness centrality for a node."""
        try:
            # Simplified closeness centrality calculation
            total_distance = 0
            reachable_nodes = 0

            for target in network:
                if target != node:
                    distance = self._calculate_shortest_path_distance(
                        node, target, network
                    )
                    if distance > 0:
                        total_distance += distance
                        reachable_nodes += 1

            if reachable_nodes == 0:
                return 0.0

            return reachable_nodes / total_distance

        except Exception as e:
            self.logger.error(f"Closeness centrality calculation failed: {e}")
            return 0.0

    def _is_on_shortest_path(
        self, source: str, target: str, node: str, network: Dict[str, Any]
    ) -> bool:
        """Check if node is on shortest path between source and target."""
        try:
            # Simplified shortest path check
            # In practice, you'd use BFS or Dijkstra's algorithm
            if (
                node in network[source]["connections"]
                and target in network[node]["connections"]
            ):
                return True

            return False

        except Exception as e:
            self.logger.error(f"Shortest path check failed: {e}")
            return False

    def _calculate_shortest_path_distance(
        self, source: str, target: str, network: Dict[str, Any]
    ) -> int:
        """Calculate shortest path distance between two nodes."""
        try:
            # Simplified BFS implementation
            if source == target:
                return 0

            if target in network[source]["connections"]:
                return 1

            # Simple 2-hop check
            for intermediate in network[source]["connections"]:
                if target in network[intermediate]["connections"]:
                    return 2

            return 3  # Default for unreachable nodes

        except Exception as e:
            self.logger.error(f"Shortest path distance calculation failed: {e}")
            return 0

    def _identify_key_nodes(
        self, network: Dict[str, Any], centrality_measures: Dict[str, Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Identify key nodes in the network."""
        try:
            key_nodes = []

            for node, measures in centrality_measures.items():
                # Calculate composite score
                composite_score = (
                    measures.get("degree", 0) * 0.4
                    + measures.get("betweenness", 0) * 0.3
                    + measures.get("closeness", 0) * 0.3
                )

                if composite_score > 0.5:  # Threshold for key nodes
                    key_nodes.append(
                        {
                            "node": node,
                            "composite_score": composite_score,
                            "measures": measures,
                            "connections": len(network[node]["connections"]),
                        }
                    )

            # Sort by composite score
            key_nodes.sort(key=lambda x: x["composite_score"], reverse=True)

            return key_nodes

        except Exception as e:
            self.logger.error(f"Key node identification failed: {e}")
            return []

    def _analyze_network_structure(self, network: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the structure of the network."""
        try:
            total_nodes = len(network)
            total_connections = sum(
                len(data["connections"]) for data in network.values()
            )

            # Calculate density
            max_possible_connections = total_nodes * (total_nodes - 1)
            density = (
                total_connections / max_possible_connections
                if max_possible_connections > 0
                else 0
            )

            # Identify clusters (simplified)
            clusters = self._identify_clusters(network)

            # Calculate average degree
            average_degree = total_connections / total_nodes if total_nodes > 0 else 0

            return {
                "total_nodes": total_nodes,
                "total_connections": total_connections,
                "density": density,
                "average_degree": average_degree,
                "clusters": clusters,
                "network_type": self._classify_network_type(density, average_degree),
            }

        except Exception as e:
            self.logger.error(f"Network structure analysis failed: {e}")
            return {}

    def _identify_clusters(self, network: Dict[str, Any]) -> List[List[str]]:
        """Identify clusters in the network."""
        try:
            clusters = []
            visited = set()

            for node in network:
                if node not in visited:
                    cluster = self._dfs_cluster(node, network, visited)
                    if len(cluster) > 1:  # Only include clusters with multiple nodes
                        clusters.append(cluster)

            return clusters

        except Exception as e:
            self.logger.error(f"Cluster identification failed: {e}")
            return []

    def _dfs_cluster(
        self, start_node: str, network: Dict[str, Any], visited: set
    ) -> List[str]:
        """DFS to find cluster starting from a node."""
        try:
            cluster = []
            stack = [start_node]

            while stack:
                node = stack.pop()
                if node not in visited:
                    visited.add(node)
                    cluster.append(node)

                    # Add connected nodes to stack
                    for connected in network[node]["connections"]:
                        if connected not in visited:
                            stack.append(connected)

            return cluster

        except Exception as e:
            self.logger.error(f"DFS cluster search failed: {e}")
            return []

    def _classify_network_type(self, density: float, average_degree: float) -> str:
        """Classify the type of network based on structure."""
        try:
            if density > 0.5:
                return "dense"
            elif density > 0.2:
                return "moderate"
            elif average_degree > 5:
                return "hub-based"
            else:
                return "sparse"

        except Exception as e:
            self.logger.error(f"Network type classification failed: {e}")
            return "unknown"

    async def _generate_insights(
        self,
        relationships: List[Dict[str, Any]],
        network_analysis: Dict[str, Any],
        llm_service: Any = None,
    ) -> List[str]:
        """Generate insights from relationship analysis."""
        try:
            if not llm_service:
                return ["Network analysis completed", "Relationships discovered"]

            # Create insights prompt
            prompt = f"""
Generate intelligence insights from the following relationship analysis:

Relationships discovered: {len(relationships)}
Network size: {network_analysis.get('total_nodes', 0)}
Network density: {network_analysis.get('density', 0):.2f}
Key nodes: {len(network_analysis.get('key_nodes', []))}

Provide insights in JSON format:
{{
    "insights": [
        "insight1",
        "insight2",
        "insight3"
    ],
    "recommendations": [
        "recommendation1",
        "recommendation2"
    ]
}}
"""

            result = await llm_service.generate(
                prompt=prompt, max_tokens=800, temperature=0.3
            )

            # Parse result
            try:
                insights_data = json.loads(result)
                return insights_data.get("insights", [])
            except:
                return ["Network analysis completed", "Relationships discovered"]

        except Exception as e:
            self.logger.error(f"Insights generation failed: {e}")
            return ["Network analysis completed", "Relationships discovered"]

    def _update_metrics(self, analysis_time: float, relationships_count: int):
        """Update performance metrics."""
        try:
            self.metrics["analyses_performed"] += 1
            self.metrics["relationships_discovered"] += relationships_count

            # Update average analysis time
            total_analyses = self.metrics["analyses_performed"]
            current_avg = self.metrics["average_analysis_time"]
            self.metrics["average_analysis_time"] = (
                current_avg * (total_analyses - 1) + analysis_time
            ) / total_analyses

        except Exception as e:
            self.logger.error(f"Metrics update failed: {e}")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {"metrics": self.metrics, "timestamp": datetime.utcnow().isoformat()}
