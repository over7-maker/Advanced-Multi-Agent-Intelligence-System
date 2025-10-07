"""
RAG Agent Implementation

This module implements the Retrieval-Augmented Generation (RAG) agent
for intelligent information retrieval and synthesis across multiple data sources.
It leverages the Universal AI Manager for LLM operations and interacts with
Vector and Knowledge Graph services through the orchestrator.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from amas.agents.base.intelligence_agent import IntelligenceAgent
from amas.common.models import OrchestratorTask, TaskPriority, TaskStatus
from amas.core.message_bus import MessageBus
from amas.services.knowledge_graph_service import KnowledgeGraphService
from amas.services.vector_service import VectorService

logger = logging.getLogger(__name__)


class QueryStrategy(Enum):
    """Query strategy types"""

    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    CONTEXTUAL = "contextual"


class SynthesisMethod(Enum):
    """Information synthesis methods"""

    CONCATENATION = "concatenation"
    SUMMARIZATION = "summarization"
    FUSION = "fusion"
    REASONING = "reasoning"


@dataclass
class QueryContext:
    """
    Query context information.

    Attributes:
        agent_id (str): The ID of the agent performing the query.
        task_type (str): The type of task being executed.
        information_need (str): The core information requirement.
        current_step (str): The current step in a multi-step process.
        previous_results (List[Dict[str, Any]]): Results from previous steps.
        constraints (Dict[str, Any]): Constraints for the query.
        preferences (Dict[str, Any]): User or system preferences for the query.
    """

    agent_id: str
    task_type: str
    information_need: str
    current_step: str
    previous_results: List[Dict[str, Any]]
    constraints: Dict[str, Any]
    preferences: Dict[str, Any]


@dataclass
class RetrievalResult:
    """
    Retrieval result from a data source.

    Attributes:
        source (str): The source of the retrieved content (e.g., 'vector_db', 'knowledge_graph').
        content (str): The actual content retrieved.
        relevance_score (float): A score indicating the relevance of the content.
        metadata (Dict[str, Any]): Additional metadata about the content.
        entities (List[str]): Key entities identified in the content.
        timestamp (datetime): When the content was retrieved.
    """

    source: str
    content: str
    relevance_score: float
    metadata: Dict[str, Any]
    entities: List[str]
    timestamp: datetime


@dataclass
class SynthesisResult:
    """
    Synthesis result from multiple sources.

    Attributes:
        synthesized_content (str): The final synthesized information.
        source_attributions (List[str]): List of sources used for synthesis.
        confidence_score (float): Confidence in the synthesized result.
        reasoning_trace (List[Dict[str, Any]]): Steps taken during reasoning/synthesis.
        metadata (Dict[str, Any]): Additional metadata about the synthesis.
    """

    synthesized_content: str
    source_attributions: List[str]
    confidence_score: float
    reasoning_trace: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class RAGAgent(IntelligenceAgent):
    """
    RAG Agent for intelligent information retrieval and synthesis.

    This agent extends the base IntelligenceAgent to provide RAG capabilities,
    leveraging vector and knowledge graph services, and the Universal AI Manager
    for advanced reasoning and synthesis.
    """

    def __init__(
        self,
        agent_id: str,
        config: Dict[str, Any],
        orchestrator: "UnifiedOrchestratorV2",
        message_bus: MessageBus,
    ):
        """
        Initialize the RAG Agent.

        Args:
            agent_id: Unique identifier for the agent
            config: Configuration for the agent (e.g., name, capabilities)
            orchestrator: The orchestrator managing this agent
            message_bus: The central message bus for communication
        """
        super().__init__(agent_id, config, orchestrator, message_bus)

        self.name = config.get("name", "RAG Agent")
        self.capabilities = config.get(
            "capabilities", ["information_retrieval", "data_synthesis", "qa"]
        )

        # Services are now accessed via the orchestrator's service manager
        self.vector_service: Optional[VectorService] = (
            self.orchestrator.get_service_manager().get_vector_service()
        )
        self.knowledge_graph: Optional[KnowledgeGraphService] = (
            self.orchestrator.get_service_manager().get_knowledge_graph_service()
        )

        if not self.vector_service or not self.vector_service.is_initialized:
            logger.warning(
                f"RAGAgent {self.agent_id}: VectorService not available or not initialized."
            )
        if not self.knowledge_graph or not self.knowledge_graph.is_initialized:
            logger.warning(
                f"RAGAgent {self.agent_id}: KnowledgeGraphService not available or not initialized."
            )

        # Query strategies
        self.query_strategies = {
            QueryStrategy.SEMANTIC: self._semantic_query,
            QueryStrategy.KEYWORD: self._keyword_query,
            QueryStrategy.HYBRID: self._hybrid_query,
            QueryStrategy.CONTEXTUAL: self._contextual_query,
        }

        # Synthesis methods
        self.synthesis_methods = {
            SynthesisMethod.CONCATENATION: self._concatenation_synthesis,
            SynthesisMethod.SUMMARIZATION: self._summarization_synthesis,
            SynthesisMethod.FUSION: self._fusion_synthesis,
            SynthesisMethod.REASONING: self._reasoning_synthesis,
        }

        # Query history for learning
        self.query_history = []
        self.feedback_history = []

        logger.info(
            f"RAGAgent {self.agent_id} initialized with capabilities: {self.capabilities}"
        )

    async def execute_task(self, task: OrchestratorTask) -> Dict[str, Any]:
        """
        Execute a RAG task.

        Args:
            task: The task to execute, expected to contain 'information_need' and 'context'.

        Returns:
            A dictionary containing the synthesized result.
        """
        information_need = task.parameters.get("information_need")
        agent_context_data = task.parameters.get("agent_context", {})

        if not information_need:
            raise ValueError("RAGAgent requires 'information_need' in task parameters.")

        # Reconstruct QueryContext from task parameters
        agent_context = QueryContext(
            agent_id=self.agent_id,
            task_type=task.task_type,
            information_need=information_need,
            current_step=agent_context_data.get("current_step", "initial"),
            previous_results=agent_context_data.get("previous_results", []),
            constraints=agent_context_data.get("constraints", {}),
            preferences=agent_context_data.get("preferences", {}),
        )

        try:
            synthesis_result = await self.intelligent_query(
                agent_context, information_need
            )
            return {"success": True, "result": synthesis_result.__dict__}
        except Exception as e:
            logger.error(
                f"RAGAgent {self.agent_id} failed to execute task {task.id}: {e}"
            )
            return {"success": False, "error": str(e)}

    async def intelligent_query(
        self, agent_context: QueryContext, information_need: str
    ) -> SynthesisResult:
        """
        Perform intelligent query with agent-based reasoning.

        Args:
            agent_context: Context of the querying agent
            information_need: Information need description

        Returns:
            Synthesized information result
        """
        try:
            logger.info(
                f"RAGAgent {agent_context.agent_id} processing intelligent query for: {information_need}"
            )

            # Analyze information need using Universal AI Manager
            query_analysis = await self._analyze_information_need(
                agent_context, information_need
            )

            # Determine query strategy
            strategy = await self._determine_query_strategy(
                agent_context, query_analysis
            )

            # Formulate queries for different sources
            queries = await self._formulate_queries(
                agent_context, query_analysis, strategy
            )

            # Execute queries across sources
            retrieval_results = await self._execute_queries(queries, agent_context)

            # Synthesize results
            synthesis_result = await self._synthesize_results(
                retrieval_results, agent_context, query_analysis
            )

            # Store query for learning
            self._store_query_for_learning(
                agent_context, query_analysis, synthesis_result
            )

            logger.info(
                f"RAGAgent {agent_context.agent_id} intelligent query completed."
            )
            return synthesis_result

        except Exception as e:
            logger.error(f"RAGAgent intelligent query failed: {e}")
            raise

    async def _analyze_information_need(
        self, agent_context: QueryContext, information_need: str
    ) -> Dict[str, Any]:
        """
        Analyze the information need to understand requirements using LLM.
        """
        if not self.universal_ai_manager:
            logger.warning(
                "Universal AI Manager not available for query analysis. Returning default."
            )
            return {
                "entities": [],
                "concepts": [],
                "intent": "information_retrieval",
                "complexity": "medium",
                "sources_needed": ["vector", "graph"],
            }

        try:
            prompt = f"""
Analyze the following information need for an intelligence agent:

Agent Context:
- Agent ID: {agent_context.agent_id}
- Task Type: {agent_context.task_type}
- Current Step: {agent_context.current_step}
- Previous Results: {len(agent_context.previous_results)} items

Information Need: {information_need}

Provide analysis in JSON format:
{{
    "entities": ["entity1", "entity2"],
    "concepts": ["concept1", "concept2"],
    "intent": "information_retrieval|fact_checking|exploration|analysis",
    "complexity": "low|medium|high",
    "sources_needed": ["vector", "graph", "both"],
    "time_sensitivity": "low|medium|high",
    "precision_requirement": "low|medium|high"
}}
"""

            result = await self._call_ai_manager(
                prompt=prompt,
                max_tokens=300,
                temperature=0.3,
                task_type="text_analysis",
            )

            if result["success"]:
                try:
                    analysis = json.loads(result["content"])
                    return analysis
                except json.JSONDecodeError:
                    logger.error(
                        f"Failed to parse AI manager response for query analysis: {result['content']}"
                    )
                    return {
                        "entities": [],
                        "concepts": [],
                        "intent": "information_retrieval",
                        "complexity": "medium",
                        "sources_needed": ["vector", "graph"],
                    }
            else:
                logger.error(f"AI manager failed for query analysis: {result['error']}")
                return {
                    "entities": [],
                    "concepts": [],
                    "intent": "information_retrieval",
                    "complexity": "medium",
                    "sources_needed": ["vector", "graph"],
                }

        except Exception as e:
            logger.error(f"Information need analysis failed: {e}")
            return {
                "entities": [],
                "concepts": [],
                "intent": "information_retrieval",
                "complexity": "medium",
                "sources_needed": ["vector", "graph"],
            }

    async def _determine_query_strategy(
        self, agent_context: QueryContext, query_analysis: Dict[str, Any]
    ) -> QueryStrategy:
        """
        Determine the best query strategy based on context and analysis.
        """
        try:
            complexity = query_analysis.get("complexity", "medium")
            intent = query_analysis.get("intent", "information_retrieval")
            sources_needed = query_analysis.get("sources_needed", ["vector"])

            if complexity == "high" and "both" in sources_needed:
                return QueryStrategy.HYBRID
            elif intent == "exploration":
                return QueryStrategy.CONTEXTUAL
            elif len(query_analysis.get("entities", [])) > 0:
                return QueryStrategy.SEMANTIC
            else:
                return QueryStrategy.KEYWORD

        except Exception as e:
            logger.error(f"Strategy determination failed: {e}")
            return QueryStrategy.SEMANTIC

    async def _formulate_queries(
        self,
        agent_context: QueryContext,
        query_analysis: Dict[str, Any],
        strategy: QueryStrategy,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Formulate queries for different data sources.
        """
        try:
            queries = {}

            # Vector service query
            if self.vector_service and self.vector_service.is_initialized:
                vector_query = await self.query_strategies[strategy](
                    agent_context, query_analysis, "vector"
                )
                queries["vector"] = vector_query

            # Knowledge graph query
            if self.knowledge_graph and self.knowledge_graph.is_initialized:
                graph_query = await self.query_strategies[strategy](
                    agent_context, query_analysis, "graph"
                )
                queries["graph"] = graph_query

            return queries

        except Exception as e:
            logger.error(f"Query formulation failed: {e}")
            return {}

    async def _execute_queries(
        self, queries: Dict[str, Dict[str, Any]], agent_context: QueryContext
    ) -> List[RetrievalResult]:
        """
        Execute queries across data sources.
        """
        try:
            results = []

            # Execute vector service query
            if (
                "vector" in queries
                and self.vector_service
                and self.vector_service.is_initialized
            ):
                vector_results = await self._execute_vector_query(queries["vector"])
                results.extend(vector_results)

            # Execute knowledge graph query
            if (
                "graph" in queries
                and self.knowledge_graph
                and self.knowledge_graph.is_initialized
            ):
                graph_results = await self._execute_graph_query(queries["graph"])
                results.extend(graph_results)

            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)

            return results

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []

    async def _execute_vector_query(
        self, query: Dict[str, Any]
    ) -> List[RetrievalResult]:
        """
        Execute query on vector service.
        """
        if not self.vector_service or not self.vector_service.is_initialized:
            logger.warning(
                "Vector service not available or not initialized. Skipping vector query."
            )
            return []

        try:
            if query["type"] == "semantic":
                results = await self.vector_service.semantic_search(
                    query=query["query"],
                    limit=query["limit"],
                    threshold=query["threshold"],
                )
            elif query["type"] == "keyword":
                results = await self.vector_service.keyword_search(
                    query=query["query"],
                    limit=query["limit"],
                    threshold=query["threshold"],
                )
            elif query["type"] == "hybrid":
                results = await self.vector_service.hybrid_search(
                    semantic_query=query["semantic_query"],
                    keyword_query=query["keyword_query"],
                    limit=query["limit"],
                    alpha=query["alpha"],
                )
            else:
                return []

            return [
                RetrievalResult(
                    source="vector_db",
                    content=r["content"],
                    relevance_score=r["score"],
                    metadata=r["metadata"],
                    entities=r.get("entities", []),
                    timestamp=datetime.now(),
                )
                for r in results
            ]

        except Exception as e:
            logger.error(f"Vector query failed: {e}")
            return []

    async def _execute_graph_query(
        self, query: Dict[str, Any]
    ) -> List[RetrievalResult]:
        """
        Execute query on knowledge graph service.
        """
        if not self.knowledge_graph or not self.knowledge_graph.is_initialized:
            logger.warning(
                "Knowledge graph not available or not initialized. Skipping graph query."
            )
            return []

        try:
            results = await self.knowledge_graph.execute_query(query["query"])
            return [
                RetrievalResult(
                    source="knowledge_graph",
                    content=r["content"],
                    relevance_score=r["score"],
                    metadata=r["metadata"],
                    entities=r.get("entities", []),
                    timestamp=datetime.now(),
                )
                for r in results
            ]

        except Exception as e:
            logger.error(f"Graph query failed: {e}")
            return []

    async def _synthesize_results(
        self,
        retrieval_results: List[RetrievalResult],
        agent_context: QueryContext,
        query_analysis: Dict[str, Any],
    ) -> SynthesisResult:
        """
        Synthesize retrieved results into a coherent response.
        """
        try:
            if not retrieval_results:
                return SynthesisResult(
                    synthesized_content="No information found.",
                    source_attributions=[],
                    confidence_score=0.0,
                    reasoning_trace=[],
                    metadata={},
                )

            # Determine synthesis method
            synthesis_method = self._determine_synthesis_method(query_analysis)

            # Synthesize using the chosen method
            synthesis_result = await self.synthesis_methods[synthesis_method](
                retrieval_results, agent_context, query_analysis
            )

            return synthesis_result

        except Exception as e:
            logger.error(f"Result synthesis failed: {e}")
            return SynthesisResult(
                synthesized_content="Failed to synthesize information.",
                source_attributions=[],
                confidence_score=0.0,
                reasoning_trace=[],
                metadata={"error": str(e)},
            )

    def _determine_synthesis_method(
        self, query_analysis: Dict[str, Any]
    ) -> SynthesisMethod:
        """
        Determine the best synthesis method based on query analysis.
        """
        try:
            intent = query_analysis.get("intent", "information_retrieval")
            complexity = query_analysis.get("complexity", "medium")

            if intent == "fact_checking" or complexity == "high":
                return SynthesisMethod.REASONING
            elif intent == "analysis":
                return SynthesisMethod.FUSION
            elif complexity == "medium":
                return SynthesisMethod.SUMMARIZATION
            else:
                return SynthesisMethod.CONCATENATION

        except Exception as e:
            logger.error(f"Synthesis method determination failed: {e}")
            return SynthesisMethod.SUMMARIZATION

    async def _concatenation_synthesis(
        self,
        retrieval_results: List[RetrievalResult],
        agent_context: QueryContext,
        query_analysis: Dict[str, Any],
    ) -> SynthesisResult:
        """
        Simple concatenation of results.
        """
        content = "\n\n---\n".join([r.content for r in retrieval_results])
        return SynthesisResult(
            synthesized_content=content,
            source_attributions=[r.source for r in retrieval_results],
            confidence_score=(
                sum(r.relevance_score for r in retrieval_results)
                / len(retrieval_results)
                if retrieval_results
                else 0.0
            ),
            reasoning_trace=[],
            metadata={},
        )

    async def _summarization_synthesis(
        self,
        retrieval_results: List[RetrievalResult],
        agent_context: QueryContext,
        query_analysis: Dict[str, Any],
    ) -> SynthesisResult:
        """
        Summarize results using Universal AI Manager.
        """
        if not self.universal_ai_manager:
            logger.warning(
                "Universal AI Manager not available for summarization. Falling back to concatenation."
            )
            return await self._concatenation_synthesis(
                retrieval_results, agent_context, query_analysis
            )

        try:
            context = "\n\n---\n".join([r.content for r in retrieval_results])
            prompt = f"""
Summarize the following information to answer the query: '{query_analysis['information_need']}'

Context:
{context}

Provide a concise summary.
"""

            result = await self._call_ai_manager(
                prompt=prompt,
                max_tokens=500,
                temperature=0.5,
                task_type="summarization",
            )

            if result["success"]:
                return SynthesisResult(
                    synthesized_content=result["content"],
                    source_attributions=[r.source for r in retrieval_results],
                    confidence_score=result.get("confidence", 0.8),
                    reasoning_trace=[
                        {"step": "summarization", "details": "Used LLM to summarize."}
                    ],
                    metadata={},
                )
            else:
                logger.error(f"Summarization failed: {result['error']}")
                return await self._concatenation_synthesis(
                    retrieval_results, agent_context, query_analysis
                )

        except Exception as e:
            logger.error(f"Summarization synthesis failed: {e}")
            return await self._concatenation_synthesis(
                retrieval_results, agent_context, query_analysis
            )

    async def _fusion_synthesis(
        self,
        retrieval_results: List[RetrievalResult],
        agent_context: QueryContext,
        query_analysis: Dict[str, Any],
    ) -> SynthesisResult:
        """
        Fuse information from multiple sources using Universal AI Manager.
        """
        if not self.universal_ai_manager:
            logger.warning(
                "Universal AI Manager not available for fusion. Falling back to summarization."
            )
            return await self._summarization_synthesis(
                retrieval_results, agent_context, query_analysis
            )

        try:
            context = "\n\n---\n".join(
                [f"Source: {r.source}\nContent: {r.content}" for r in retrieval_results]
            )
            prompt = f"""
Fuse the following information from multiple sources to provide a comprehensive answer to the query: '{query_analysis['information_need']}'

Context:
{context}

Synthesize the information, resolve contradictions, and provide a single, coherent answer.
"""

            result = await self._call_ai_manager(
                prompt=prompt, max_tokens=1000, temperature=0.6, task_type="fusion"
            )

            if result["success"]:
                return SynthesisResult(
                    synthesized_content=result["content"],
                    source_attributions=[r.source for r in retrieval_results],
                    confidence_score=result.get("confidence", 0.85),
                    reasoning_trace=[
                        {"step": "fusion", "details": "Used LLM to fuse information."}
                    ],
                    metadata={},
                )
            else:
                logger.error(f"Fusion failed: {result['error']}")
                return await self._summarization_synthesis(
                    retrieval_results, agent_context, query_analysis
                )

        except Exception as e:
            logger.error(f"Fusion synthesis failed: {e}")
            return await self._summarization_synthesis(
                retrieval_results, agent_context, query_analysis
            )

    async def _reasoning_synthesis(
        self,
        retrieval_results: List[RetrievalResult],
        agent_context: QueryContext,
        query_analysis: Dict[str, Any],
    ) -> SynthesisResult:
        """
        Perform complex reasoning over retrieved information.
        """
        if not self.universal_ai_manager:
            logger.warning(
                "Universal AI Manager not available for reasoning. Falling back to fusion."
            )
            return await self._fusion_synthesis(
                retrieval_results, agent_context, query_analysis
            )

        try:
            context = "\n\n---\n".join(
                [f"Source: {r.source}\nContent: {r.content}" for r in retrieval_results]
            )
            prompt = f"""
Perform complex reasoning based on the following information to answer the query: '{query_analysis['information_need']}'

Context:
{context}

Provide a detailed, step-by-step reasoning process and a final answer.
"""

            result = await self._call_ai_manager(
                prompt=prompt, max_tokens=1500, temperature=0.7, task_type="reasoning"
            )

            if result["success"]:
                return SynthesisResult(
                    synthesized_content=result["content"],
                    source_attributions=[r.source for r in retrieval_results],
                    confidence_score=result.get("confidence", 0.9),
                    reasoning_trace=result.get(
                        "reasoning_trace",
                        [
                            {
                                "step": "reasoning",
                                "details": "Used LLM for complex reasoning.",
                            }
                        ],
                    ),
                    metadata={},
                )
            else:
                logger.error(f"Reasoning failed: {result['error']}")
                return await self._fusion_synthesis(
                    retrieval_results, agent_context, query_analysis
                )

        except Exception as e:
            logger.error(f"Reasoning synthesis failed: {e}")
            return await self._fusion_synthesis(
                retrieval_results, agent_context, query_analysis
            )

    async def _semantic_query(
        self, agent_context: QueryContext, query_analysis: Dict[str, Any], source: str
    ) -> Dict[str, Any]:
        """
        Formulate a semantic query.
        """
        query = f"Entities: {query_analysis.get('entities', [])}, Concepts: {query_analysis.get('concepts', [])}"
        return {"type": "semantic", "query": query, "limit": 10, "threshold": 0.7}

    async def _keyword_query(
        self, agent_context: QueryContext, query_analysis: Dict[str, Any], source: str
    ) -> Dict[str, Any]:
        """
        Formulate a keyword query.
        """
        query = " ".join(
            query_analysis.get("entities", []) + query_analysis.get("concepts", [])
        )
        return {"type": "keyword", "query": query, "limit": 10, "threshold": 0.5}

    async def _hybrid_query(
        self, agent_context: QueryContext, query_analysis: Dict[str, Any], source: str
    ) -> Dict[str, Any]:
        """
        Formulate a hybrid query.
        """
        semantic_query = f"Entities: {query_analysis.get('entities', [])}, Concepts: {query_analysis.get('concepts', [])}"
        keyword_query = " ".join(
            query_analysis.get("entities", []) + query_analysis.get("concepts", [])
        )
        return {
            "type": "hybrid",
            "semantic_query": semantic_query,
            "keyword_query": keyword_query,
            "limit": 10,
            "alpha": 0.6,
        }

    async def _contextual_query(
        self, agent_context: QueryContext, query_analysis: Dict[str, Any], source: str
    ) -> Dict[str, Any]:
        """
        Formulate a contextual query using LLM.
        """
        if not self.universal_ai_manager:
            logger.warning(
                "Universal AI Manager not available for contextual query. Falling back to semantic."
            )
            return await self._semantic_query(agent_context, query_analysis, source)

        try:
            prompt = f"""
Formulate a precise query for a {source} database based on the following context:

Agent Context: {agent_context}
Query Analysis: {query_analysis}

Provide the query string only.
"""

            result = await self._call_ai_manager(
                prompt=prompt,
                max_tokens=100,
                temperature=0.2,
                task_type="query_formulation",
            )

            if result["success"]:
                return {
                    "type": "semantic",
                    "query": result["content"],
                    "limit": 10,
                    "threshold": 0.75,
                }
            else:
                logger.error(f"Contextual query formulation failed: {result['error']}")
                return await self._semantic_query(agent_context, query_analysis, source)

        except Exception as e:
            logger.error(f"Contextual query failed: {e}")
            return await self._semantic_query(agent_context, query_analysis, source)

    def _store_query_for_learning(
        self,
        agent_context: QueryContext,
        query_analysis: Dict[str, Any],
        synthesis_result: SynthesisResult,
    ):
        """
        Store query and result for future learning.
        """
        self.query_history.append(
            {
                "context": agent_context,
                "analysis": query_analysis,
                "result": synthesis_result,
                "timestamp": datetime.now(),
            }
        )

    def receive_feedback(self, task_id: str, feedback: Dict[str, Any]):
        """
        Receive feedback on a completed task for learning.
        """
        self.feedback_history.append(
            {"task_id": task_id, "feedback": feedback, "timestamp": datetime.now()}
        )

    async def adapt_from_feedback(self):
        """
        Adapt agent strategies based on feedback.
        This is a placeholder for a more advanced learning mechanism.
        """
        if not self.universal_ai_manager:
            logger.warning("Universal AI Manager not available for adaptation.")
            return

        try:
            if len(self.feedback_history) > 0:
                feedback_summary = "\n".join([str(f) for f in self.feedback_history])
                prompt = f"""
Analyze the following feedback and suggest improvements to query strategies or synthesis methods:

{feedback_summary}

Provide suggestions in a structured format.
"""

                result = await self._call_ai_manager(
                    prompt=prompt,
                    max_tokens=500,
                    temperature=0.6,
                    task_type="adaptation",
                )

                if result["success"]:
                    logger.info(f"Adaptation suggestions: {result['content']}")
                    # In a real system, these suggestions would be parsed and applied
                    self.feedback_history.clear()  # Clear feedback after processing

        except Exception as e:
            logger.error(f"Adaptation from feedback failed: {e}")

    async def add_document_to_knowledge_base(
        self, document: str, metadata: Dict[str, Any]
    ) -> bool:
        """
        Add a document to the knowledge base (vector service).
        """
        if not self.vector_service or not self.vector_service.is_initialized:
            logger.error("Vector service not available for adding document.")
            return False

        try:
            # Use LLM to extract entities and concepts for metadata enrichment
            if self.universal_ai_manager:
                prompt = f"""
Extract key entities and concepts from the following document:

{document}

Provide output in JSON format: {{"entities": [], "concepts": []}}
"""
                result = await self._call_ai_manager(
                    prompt=prompt,
                    max_tokens=200,
                    temperature=0.3,
                    task_type="metadata_extraction",
                )
                if result["success"]:
                    try:
                        extracted_data = json.loads(result["content"])
                        metadata["entities"] = extracted_data.get("entities", [])
                        metadata["concepts"] = extracted_data.get("concepts", [])
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse metadata extraction response.")

            success = await self.vector_service.add_document(document, metadata)
            if success:
                logger.info(
                    f"Document added to knowledge base with metadata: {metadata}"
                )
            else:
                logger.error("Failed to add document to knowledge base.")
            return success

        except Exception as e:
            logger.error(f"Adding document to knowledge base failed: {e}")
            return False

    async def get_knowledge_graph_insights(
        self, entity: str, relation: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get insights from the knowledge graph for a given entity.
        """
        if not self.knowledge_graph or not self.knowledge_graph.is_initialized:
            logger.error("Knowledge graph not available for insights.")
            return []

        try:
            query = f"MATCH (e {{name: '{entity}'}})-[r]-(n) RETURN e, r, n"
            if relation:
                query = (
                    f"MATCH (e {{name: '{entity}'}})-[r:{relation}]-(n) RETURN e, r, n"
                )

            results = await self.knowledge_graph.execute_query(query)
            return results

        except Exception as e:
            logger.error(f"Knowledge graph insights retrieval failed: {e}")
            return []

    async def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the status of the RAG agent.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "capabilities": self.capabilities,
            "vector_service_status": (
                "available"
                if self.vector_service and self.vector_service.is_initialized
                else "unavailable"
            ),
            "knowledge_graph_status": (
                "available"
                if self.knowledge_graph and self.knowledge_graph.is_initialized
                else "unavailable"
            ),
            "query_history_count": len(self.query_history),
            "feedback_history_count": len(self.feedback_history),
        }

    async def _handle_feedback_message(self, message: Dict[str, Any]):
        """
        Handle feedback messages from the orchestrator.
        """
        task_id = message.get("task_id")
        feedback = message.get("feedback")
        if task_id and feedback:
            self.receive_feedback(task_id, feedback)
            logger.info(f"Received feedback for task {task_id}.")
            # Trigger adaptation based on feedback
            await self.adapt_from_feedback()

    async def _handle_system_message(self, message: Dict[str, Any]):
        """
        Handle system-level messages (e.g., service status changes).
        """
        message_type = message.get("type")
        if message_type == "service_status_update":
            service_name = message.get("service_name")
            status = message.get("status")
            if service_name == "vector_service":
                self.vector_service = (
                    self.orchestrator.get_service_manager().get_vector_service()
                    if status == "available"
                    else None
                )
                logger.info(f"Vector service status updated to: {status}")
            elif service_name == "knowledge_graph_service":
                self.knowledge_graph = (
                    self.orchestrator.get_service_manager().get_knowledge_graph_service()
                    if status == "available"
                    else None
                )
                logger.info(f"Knowledge graph service status updated to: {status}")

    async def start(self):
        """
        Start the RAG agent and subscribe to relevant topics.
        """
        await super().start()
        await self.message_bus.subscribe(
            f"system_messages", self._handle_system_message
        )
        logger.info(f"RAGAgent {self.agent_id} subscribed to system messages.")

    async def stop(self):
        """
        Stop the RAG agent and unsubscribe from topics.
        """
        await super().stop()
        await self.message_bus.unsubscribe(
            f"system_messages", self._handle_system_message
        )
        logger.info(f"RAGAgent {self.agent_id} unsubscribed from system messages.")


# Example Usage (for testing)


async def main():
    # This is a simplified setup for testing purposes.
    # In a real scenario, the orchestrator would manage agent and service lifecycles.

    from amas.services.service_manager import ServiceManager

    # Initialize services
    service_manager = ServiceManager()
    await service_manager.initialize_services()

    # Initialize orchestrator with service manager
    orchestrator = UnifiedOrchestratorV2(service_manager=service_manager)

    # Create and register RAG agent
    rag_agent_config = {
        "name": "Test RAG Agent",
        "capabilities": ["information_retrieval", "data_synthesis"],
    }
    rag_agent = RAGAgent(
        agent_id="rag_agent_001",
        config=rag_agent_config,
        orchestrator=orchestrator,
        message_bus=orchestrator.get_message_bus(),
    )
    await orchestrator.register_agent(rag_agent)

    # Add a document to the knowledge base
    await rag_agent.add_document_to_knowledge_base(
        "The capital of France is Paris.", {"source": "manual"}
    )

    # Create a task for the RAG agent
    task_id = await orchestrator.submit_task(
        title="Find Capital of France",
        description="What is the capital of France?",
        task_type="information_retrieval",
        priority=TaskPriority.HIGH,
        required_agent_roles=["information_retrieval"],
        parameters={"information_need": "capital of France"},
    )

    # Wait for the task to complete (in a real system, this would be asynchronous)
    await asyncio.sleep(5)

    # Check task status
    task_status = await orchestrator.get_task_status(task_id)
    print(f"Task status: {task_status}")

    # Shutdown
    await service_manager.shutdown_services()
    await orchestrator.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
