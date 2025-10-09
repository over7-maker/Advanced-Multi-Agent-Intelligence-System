#!/usr/bin/env python3
"""
Collective Intelligence System for AMAS
Advanced multi-agent learning and knowledge sharing platform
"""

import asyncio
import hashlib
import json
import logging
import pickle
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class TaskPattern:
    task_id: str
    task_type: str
    target: str
    parameters: Dict[str, Any]
    agents_used: List[str]
    execution_time: float
    success_rate: float
    error_patterns: List[str]
    solution_quality: float
    timestamp: str
    context_hash: str


@dataclass
class AgentInsight:
    agent_id: str
    insight_type: str
    description: str
    confidence_score: float
    applicable_contexts: List[str]
    success_evidence: List[str]
    discovery_timestamp: str
    validation_count: int


@dataclass
class CollectiveKnowledge:
    knowledge_id: str
    category: str
    title: str
    description: str
    patterns: List[TaskPattern]
    insights: List[AgentInsight]
    effectiveness_score: float
    usage_count: int
    last_updated: str


class CollectiveIntelligenceEngine:
    """Advanced collective learning system for multi-agent coordination"""

    def __init__(self, knowledge_db_path: str = "data/collective_knowledge.pkl"):
        self.knowledge_db_path = knowledge_db_path
        self.shared_knowledge: Dict[str, CollectiveKnowledge] = {}
        self.agent_specializations: Dict[str, List[str]] = {}
        self.task_similarity_cache: Dict[str, List[Tuple[str, float]]] = {}
        self.learning_graph = nx.DiGraph()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        self.logger = logging.getLogger(__name__)

        # Load existing knowledge
        self.load_knowledge_base()

        # Initialize agent specializations
        self._initialize_agent_specializations()

    def _initialize_agent_specializations(self):
        """Initialize agent specialization mappings"""
        self.agent_specializations = {
            "security_expert": [
                "vulnerability_scanning",
                "penetration_testing",
                "threat_analysis",
                "security_audit",
                "compliance_checking",
                "risk_assessment",
            ],
            "code_analysis": [
                "static_analysis",
                "code_quality",
                "performance_optimization",
                "architectural_review",
                "dependency_analysis",
                "refactoring",
            ],
            "intelligence_gathering": [
                "osint_research",
                "social_media_analysis",
                "domain_investigation",
                "threat_intelligence",
                "competitive_analysis",
                "data_mining",
            ],
            "performance_monitor": [
                "system_monitoring",
                "performance_profiling",
                "resource_optimization",
                "bottleneck_identification",
                "capacity_planning",
                "sla_monitoring",
            ],
            "documentation_specialist": [
                "technical_writing",
                "api_documentation",
                "user_guides",
                "knowledge_management",
                "content_creation",
                "information_architecture",
            ],
            "testing_coordinator": [
                "test_planning",
                "quality_assurance",
                "automation_testing",
                "regression_testing",
                "performance_testing",
                "security_testing",
            ],
            "integration_manager": [
                "system_integration",
                "api_coordination",
                "workflow_orchestration",
                "service_mesh",
                "microservices",
                "event_driven_architecture",
            ],
        }

    def load_knowledge_base(self):
        """Load collective knowledge from persistent storage"""
        try:
            with open(self.knowledge_db_path, "rb") as f:
                self.shared_knowledge = pickle.load(f)
            self.logger.info(
                f"✅ Loaded {len(self.shared_knowledge)} knowledge entries"
            )
        except FileNotFoundError:
            self.logger.info("📝 Creating new collective knowledge base")
            self.shared_knowledge = {}
        except Exception as e:
            self.logger.error(f"❌ Error loading knowledge base: {e}")
            self.shared_knowledge = {}

    def save_knowledge_base(self):
        """Save collective knowledge to persistent storage"""
        try:
            # Ensure directory exists
            import os

            os.makedirs(os.path.dirname(self.knowledge_db_path), exist_ok=True)

            with open(self.knowledge_db_path, "wb") as f:
                pickle.dump(self.shared_knowledge, f)
            self.logger.info(f"💾 Saved {len(self.shared_knowledge)} knowledge entries")
        except Exception as e:
            self.logger.error(f"❌ Error saving knowledge base: {e}")

    def generate_context_hash(
        self, task_type: str, target: str, parameters: Dict[str, Any]
    ) -> str:
        """Generate a hash representing the task context"""
        # Input validation
        if not task_type or not isinstance(task_type, str):
            raise ValueError("task_type must be a non-empty string")
        if not target or not isinstance(target, str):
            raise ValueError("target must be a non-empty string")
        if not isinstance(parameters, dict):
            raise ValueError("parameters must be a dictionary")

        # Sanitize inputs
        task_type = task_type.strip().lower()
        target = target.strip()

        context_string = (
            f"{task_type}:{target}:{json.dumps(parameters, sort_keys=True)}"
        )
        return hashlib.sha256(context_string.encode("utf-8")).hexdigest()

    async def record_task_execution(
        self,
        task_id: str,
        task_type: str,
        target: str,
        parameters: Dict[str, Any],
        agents_used: List[str],
        execution_time: float,
        success_rate: float,
        error_patterns: List[str],
        solution_quality: float,
    ):
        """Record a completed task execution for learning"""

        # Input validation
        if not task_id or not isinstance(task_id, str):
            raise ValueError("task_id must be a non-empty string")
        if not isinstance(agents_used, list):
            raise ValueError("agents_used must be a list")
        if not (0 <= success_rate <= 1):
            raise ValueError("success_rate must be between 0 and 1")
        if not (0 <= solution_quality <= 1):
            raise ValueError("solution_quality must be between 0 and 1")
        if execution_time < 0:
            raise ValueError("execution_time must be non-negative")

        try:
            context_hash = self.generate_context_hash(task_type, target, parameters)
        except Exception as e:
            self.logger.error(f"❌ Error generating context hash: {e}")
            raise

        task_pattern = TaskPattern(
            task_id=task_id,
            task_type=task_type,
            target=target,
            parameters=parameters,
            agents_used=agents_used,
            execution_time=execution_time,
            success_rate=success_rate,
            error_patterns=error_patterns,
            solution_quality=solution_quality,
            timestamp=datetime.now().isoformat(),
            context_hash=context_hash,
        )

        # Find or create knowledge category
        knowledge_key = f"{task_type}_{context_hash[:8]}"

        if knowledge_key in self.shared_knowledge:
            # Update existing knowledge
            self.shared_knowledge[knowledge_key].patterns.append(task_pattern)
            self.shared_knowledge[knowledge_key].usage_count += 1
            self.shared_knowledge[knowledge_key].last_updated = (
                datetime.now().isoformat()
            )

            # Recalculate effectiveness score
            patterns = self.shared_knowledge[knowledge_key].patterns
            avg_success = sum(p.success_rate for p in patterns) / len(patterns)
            avg_quality = sum(p.solution_quality for p in patterns) / len(patterns)
            self.shared_knowledge[knowledge_key].effectiveness_score = (
                avg_success + avg_quality
            ) / 2
        else:
            # Create new knowledge entry
            self.shared_knowledge[knowledge_key] = CollectiveKnowledge(
                knowledge_id=knowledge_key,
                category=task_type,
                title=f"{task_type.replace('_', ' ').title()} - {target}",
                description=f"Collective knowledge for {task_type} tasks similar to {target}",
                patterns=[task_pattern],
                insights=[],
                effectiveness_score=solution_quality,
                usage_count=1,
                last_updated=datetime.now().isoformat(),
            )

        # Update learning graph
        self._update_learning_graph(task_pattern)

        # Extract insights from this execution
        await self._extract_insights_from_execution(task_pattern)

        # Save knowledge base
        self.save_knowledge_base()

        self.logger.info(f"📚 Recorded task execution: {task_id} -> {knowledge_key}")

    def _update_learning_graph(self, task_pattern: TaskPattern):
        """Update the learning graph with new task relationships"""

        # Add task node
        self.learning_graph.add_node(
            task_pattern.task_id,
            type=task_pattern.task_type,
            success_rate=task_pattern.success_rate,
            quality=task_pattern.solution_quality,
        )

        # Add agent nodes and connections
        for agent in task_pattern.agents_used:
            if not self.learning_graph.has_node(agent):
                self.learning_graph.add_node(agent, type="agent")

            # Add edge from agent to task
            self.learning_graph.add_edge(
                agent,
                task_pattern.task_id,
                weight=task_pattern.success_rate,
                execution_time=task_pattern.execution_time,
            )

        # Add connections between agents that worked together
        for i, agent1 in enumerate(task_pattern.agents_used):
            for agent2 in task_pattern.agents_used[i + 1 :]:
                if self.learning_graph.has_edge(agent1, agent2):
                    # Strengthen existing collaboration
                    current_weight = self.learning_graph[agent1][agent2]["weight"]
                    self.learning_graph[agent1][agent2]["weight"] = min(
                        1.0, current_weight + 0.1
                    )
                else:
                    # New collaboration
                    self.learning_graph.add_edge(
                        agent1, agent2, weight=0.1, type="collaboration"
                    )

    async def _extract_insights_from_execution(self, task_pattern: TaskPattern):
        """Extract actionable insights from task execution"""

        insights = []

        # High performance insight
        if task_pattern.success_rate > 0.9 and task_pattern.solution_quality > 0.8:
            insight = AgentInsight(
                agent_id="collective",
                insight_type="high_performance_pattern",
                description=f"Agent combination {', '.join(task_pattern.agents_used)} "
                f"achieved excellent results for {task_pattern.task_type}",
                confidence_score=0.9,
                applicable_contexts=[task_pattern.task_type],
                success_evidence=[task_pattern.task_id],
                discovery_timestamp=datetime.now().isoformat(),
                validation_count=1,
            )
            insights.append(insight)

        # Performance issue insight
        if task_pattern.execution_time > 300:  # 5 minutes
            insight = AgentInsight(
                agent_id="collective",
                insight_type="performance_concern",
                description=f"Tasks of type {task_pattern.task_type} with similar parameters "
                f"tend to take longer than expected",
                confidence_score=0.7,
                applicable_contexts=[task_pattern.task_type],
                success_evidence=[task_pattern.task_id],
                discovery_timestamp=datetime.now().isoformat(),
                validation_count=1,
            )
            insights.append(insight)

        # Error pattern insight
        if task_pattern.error_patterns:
            for error in task_pattern.error_patterns:
                insight = AgentInsight(
                    agent_id="collective",
                    insight_type="error_pattern",
                    description=f"Common error pattern detected: {error}",
                    confidence_score=0.8,
                    applicable_contexts=[task_pattern.task_type],
                    success_evidence=[],
                    discovery_timestamp=datetime.now().isoformat(),
                    validation_count=1,
                )
                insights.append(insight)

        # Store insights in the relevant knowledge entry
        knowledge_key = f"{task_pattern.task_type}_{task_pattern.context_hash[:8]}"
        if knowledge_key in self.shared_knowledge:
            self.shared_knowledge[knowledge_key].insights.extend(insights)

    async def predict_optimal_agent_combination(
        self, task_type: str, target: str, parameters: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """Predict the optimal agent combination for a given task"""

        # context_hash = self.generate_context_hash(task_type, target, parameters)

        # Find similar tasks from historical data
        similar_tasks = await self._find_similar_tasks(task_type, target, parameters)

        if not similar_tasks:
            # No historical data, use default specializations
            return self._get_default_agent_combination(task_type)

        # Analyze successful patterns
        agent_performance_scores = defaultdict(list)

        for task_pattern, similarity_score in similar_tasks:
            if task_pattern.success_rate > 0.7:  # Only consider successful tasks
                for agent in task_pattern.agents_used:
                    # Weight by similarity and success rate
                    score = (
                        similarity_score
                        * task_pattern.success_rate
                        * task_pattern.solution_quality
                    )
                    agent_performance_scores[agent].append(score)

        # Calculate average performance scores
        agent_averages = {}
        for agent, scores in agent_performance_scores.items():
            agent_averages[agent] = sum(scores) / len(scores)

        # Sort agents by performance score
        recommended_agents = sorted(
            agent_averages.items(), key=lambda x: x[1], reverse=True
        )

        # Ensure we have at least 2-3 agents
        if len(recommended_agents) < 2:
            default_agents = self._get_default_agent_combination(task_type)
            recommended_agents.extend(default_agents)

        return recommended_agents[:3]  # Return top 3 agents

    async def _find_similar_tasks(
        self, task_type: str, target: str, parameters: Dict[str, Any]
    ) -> List[Tuple[TaskPattern, float]]:
        """Find similar tasks from historical data"""

        cache_key = f"{task_type}_{target}_{hash(str(parameters))}"

        if cache_key in self.task_similarity_cache:
            return self.task_similarity_cache[cache_key]

        similar_tasks = []

        # Create feature vector for current task
        current_features = self._extract_task_features(task_type, target, parameters)

        # Compare with all historical tasks
        for knowledge in self.shared_knowledge.values():
            if knowledge.category == task_type:
                for pattern in knowledge.patterns:
                    historical_features = self._extract_task_features(
                        pattern.task_type, pattern.target, pattern.parameters
                    )

                    similarity = self._calculate_task_similarity(
                        current_features, historical_features
                    )

                    if similarity > 0.3:  # Similarity threshold
                        similar_tasks.append((pattern, similarity))

        # Sort by similarity
        similar_tasks.sort(key=lambda x: x[1], reverse=True)

        # Cache results
        self.task_similarity_cache[cache_key] = similar_tasks[
            :10
        ]  # Top 10 similar tasks

        return similar_tasks[:10]

    def _extract_task_features(
        self, task_type: str, target: str, parameters: Dict[str, Any]
    ) -> np.ndarray:
        """Extract feature vector from task characteristics"""

        features = []

        # Task type encoding (one-hot)
        task_types = [
            "security_scan",
            "code_analysis",
            "intelligence_gathering",
            "performance_analysis",
            "documentation",
            "testing",
            "integration",
        ]
        for tt in task_types:
            features.append(1.0 if task_type == tt else 0.0)

        # Target type features
        target_lower = target.lower()
        features.extend(
            [
                1.0 if "http" in target_lower else 0.0,  # URL
                1.0 if "github" in target_lower else 0.0,  # GitHub repo
                1.0 if ".com" in target_lower else 0.0,  # Domain
                1.0 if "/" in target else 0.0,  # Path
            ]
        )

        # Parameter features
        features.extend(
            [
                len(parameters),  # Number of parameters
                1.0 if "depth" in parameters else 0.0,
                1.0 if "comprehensive" in str(parameters) else 0.0,
                1.0 if "quick" in str(parameters) else 0.0,
            ]
        )

        return np.array(features)

    def _calculate_task_similarity(
        self, features1: np.ndarray, features2: np.ndarray
    ) -> float:
        """Calculate similarity between two task feature vectors"""

        # Use cosine similarity
        dot_product = np.dot(features1, features2)
        norms = np.linalg.norm(features1) * np.linalg.norm(features2)

        if norms == 0:
            return 0.0

        return dot_product / norms

    def _get_default_agent_combination(self, task_type: str) -> List[Tuple[str, float]]:
        """Get default agent combination based on task type"""

        defaults = {
            "security_scan": [
                ("security_expert", 0.9),
                ("intelligence_gathering", 0.7),
            ],
            "code_analysis": [("code_analysis", 0.9), ("security_expert", 0.6)],
            "intelligence_gathering": [
                ("intelligence_gathering", 0.9),
                ("security_expert", 0.5),
            ],
            "performance_analysis": [
                ("performance_monitor", 0.9),
                ("code_analysis", 0.6),
            ],
            "documentation": [
                ("documentation_specialist", 0.9),
                ("code_analysis", 0.5),
            ],
            "testing": [("testing_coordinator", 0.9), ("code_analysis", 0.7)],
            "integration": [("integration_manager", 0.9), ("performance_monitor", 0.6)],
        }

        return defaults.get(
            task_type, [("code_analysis", 0.5), ("security_expert", 0.5)]
        )

    async def get_agent_insights(self, agent_id: str) -> List[AgentInsight]:
        """Get all insights related to a specific agent"""

        insights = []

        for knowledge in self.shared_knowledge.values():
            for insight in knowledge.insights:
                if (
                    insight.agent_id == agent_id
                    or agent_id in insight.applicable_contexts
                ):
                    insights.append(insight)

        # Sort by confidence score and validation count
        insights.sort(
            key=lambda x: (x.confidence_score, x.validation_count), reverse=True
        )

        return insights

    async def get_collective_insights_summary(self) -> Dict[str, Any]:
        """Get a summary of all collective insights"""

        total_insights = 0
        insight_categories = defaultdict(int)
        high_confidence_insights = 0

        for knowledge in self.shared_knowledge.values():
            total_insights += len(knowledge.insights)
            for insight in knowledge.insights:
                insight_categories[insight.insight_type] += 1
                if insight.confidence_score > 0.8:
                    high_confidence_insights += 1

        return {
            "total_insights": total_insights,
            "high_confidence_insights": high_confidence_insights,
            "insight_categories": dict(insight_categories),
            "knowledge_entries": len(self.shared_knowledge),
            "learning_graph_nodes": self.learning_graph.number_of_nodes(),
            "learning_graph_edges": self.learning_graph.number_of_edges(),
        }

    async def recommend_task_optimizations(
        self, task_type: str, target: str, parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend optimizations for a given task based on collective knowledge"""

        recommendations = []

        # Find similar successful tasks
        similar_tasks = await self._find_similar_tasks(task_type, target, parameters)

        if similar_tasks:
            # Analyze patterns in successful executions
            successful_patterns = [
                pattern
                for pattern, similarity in similar_tasks
                if pattern.success_rate > 0.8 and similarity > 0.5
            ]

            if successful_patterns:
                # Agent combination optimization
                best_combinations = defaultdict(list)
                for pattern in successful_patterns:
                    combo_key = tuple(sorted(pattern.agents_used))
                    best_combinations[combo_key].append(pattern.solution_quality)

                best_combo = max(
                    best_combinations.items(), key=lambda x: sum(x[1]) / len(x[1])
                )

                recommendations.append(
                    {
                        "type": "agent_combination",
                        "description": f"Use agents: {', '.join(best_combo[0])}",
                        "confidence": 0.8,
                        "expected_improvement": "15-25% better success rate",
                    }
                )

                # Parameter optimization
                common_params = defaultdict(list)
                for pattern in successful_patterns:
                    for key, value in pattern.parameters.items():
                        common_params[key].append(value)

                for param, values in common_params.items():
                    if len(set(values)) == 1:  # All successful tasks used same value
                        recommendations.append(
                            {
                                "type": "parameter_optimization",
                                "description": f"Set {param} to '{values[0]}'",
                                "confidence": 0.7,
                                "expected_improvement": "10-15% better results",
                            }
                        )

        # Add insights-based recommendations
        relevant_insights = []
        for knowledge in self.shared_knowledge.values():
            if knowledge.category == task_type:
                relevant_insights.extend(knowledge.insights)

        for insight in relevant_insights:
            if insight.confidence_score > 0.7:
                recommendations.append(
                    {
                        "type": "insight_based",
                        "description": insight.description,
                        "confidence": insight.confidence_score,
                        "expected_improvement": "Based on collective learning",
                    }
                )

        return recommendations

    async def cross_agent_knowledge_transfer(self):
        """Facilitate knowledge transfer between agents"""

        self.logger.info("🔄 Initiating cross-agent knowledge transfer...")

        # Analyze agent collaboration patterns
        collaboration_strength = {}

        for agent1 in self.agent_specializations.keys():
            collaboration_strength[agent1] = {}
            for agent2 in self.agent_specializations.keys():
                if agent1 != agent2:
                    if self.learning_graph.has_edge(agent1, agent2):
                        strength = self.learning_graph[agent1][agent2]["weight"]
                    else:
                        strength = 0.0
                    collaboration_strength[agent1][agent2] = strength

        # Identify knowledge gaps and transfer opportunities
        transfer_opportunities = []

        for agent in self.agent_specializations.keys():
            # agent_insights = await self.get_agent_insights(agent)

            # Find agents with complementary knowledge
            for other_agent in self.agent_specializations.keys():
                if agent != other_agent:
                    # Check if other agent has high-confidence insights that could help this agent
                    other_insights = await self.get_agent_insights(other_agent)

                    for insight in other_insights:
                        if insight.confidence_score > 0.8 and any(
                            context in self.agent_specializations[agent]
                            for context in insight.applicable_contexts
                        ):

                            transfer_opportunities.append(
                                {
                                    "from_agent": other_agent,
                                    "to_agent": agent,
                                    "insight": insight,
                                    "transfer_value": insight.confidence_score,
                                }
                            )

        # Execute knowledge transfers
        for opportunity in transfer_opportunities[:5]:  # Top 5 opportunities
            await self._execute_knowledge_transfer(opportunity)

        self.logger.info(
            f"✅ Completed {len(transfer_opportunities[:5])} knowledge transfers"
        )

        return transfer_opportunities[:5]

    async def _execute_knowledge_transfer(self, transfer_opportunity: Dict[str, Any]):
        """Execute a specific knowledge transfer between agents"""

        from_agent = transfer_opportunity["from_agent"]
        to_agent = transfer_opportunity["to_agent"]
        insight = transfer_opportunity["insight"]

        # Create a new insight for the receiving agent
        transferred_insight = AgentInsight(
            agent_id=to_agent,
            insight_type=f"transferred_{insight.insight_type}",
            description=f"[Learned from {from_agent}] {insight.description}",
            confidence_score=insight.confidence_score
            * 0.8,  # Slightly reduce confidence
            applicable_contexts=insight.applicable_contexts,
            success_evidence=insight.success_evidence,
            discovery_timestamp=datetime.now().isoformat(),
            validation_count=0,  # Will be validated through future use
        )

        # Add to collective knowledge
        # Find relevant knowledge entries for the receiving agent
        for knowledge in self.shared_knowledge.values():
            if any(
                context in self.agent_specializations[to_agent]
                for context in transferred_insight.applicable_contexts
            ):
                knowledge.insights.append(transferred_insight)
                break

        self.logger.info(f"📚 Transferred insight from {from_agent} to {to_agent}")


# Utility functions for external use
class CollectiveIntelligenceManager:
    """High-level manager for collective intelligence operations"""

    def __init__(self):
        self.engine = CollectiveIntelligenceEngine()
        self.logger = logging.getLogger(__name__)

    async def start_learning_cycle(self):
        """Start continuous learning cycle"""
        self.logger.info("🧠 Starting collective intelligence learning cycle...")

        while True:
            try:
                # Perform cross-agent knowledge transfer
                await self.engine.cross_agent_knowledge_transfer()

                # Clean up old cache entries
                await self._cleanup_cache()

                # Generate learning report
                await self._generate_learning_report()

                # Wait before next cycle (every hour)
                await asyncio.sleep(3600)

            except Exception as e:
                self.logger.error(f"❌ Error in learning cycle: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    async def _cleanup_cache(self):
        """Clean up old cache entries"""
        # Clear similarity cache to prevent it from growing too large
        if len(self.engine.task_similarity_cache) > 1000:
            # Keep only the 500 most recent entries
            items = list(self.engine.task_similarity_cache.items())
            self.engine.task_similarity_cache = dict(items[-500:])

    async def _generate_learning_report(self):
        """Generate periodic learning report"""
        summary = await self.engine.get_collective_insights_summary()

        self.logger.info(
            f"📊 Learning Report: "
            f"{summary['total_insights']} insights, "
            f"{summary['knowledge_entries']} knowledge entries, "
            f"{summary['high_confidence_insights']} high-confidence insights"
        )


# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AMAS Collective Intelligence System")
    parser.add_argument("--test", action="store_true", help="Run test scenario")
    parser.add_argument(
        "--report", action="store_true", help="Generate insights report"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    engine = CollectiveIntelligenceEngine()

    async def test_scenario():
        """Test the collective intelligence system"""
        print("🧪 Testing Collective Intelligence System...")

        # Simulate some task executions
        await engine.record_task_execution(
            task_id="test_001",
            task_type="security_scan",
            target="example.com",
            parameters={"depth": "comprehensive", "include_ssl": True},
            agents_used=["security_expert", "intelligence_gathering"],
            execution_time=120.5,
            success_rate=0.95,
            error_patterns=[],
            solution_quality=0.9,
        )

        await engine.record_task_execution(
            task_id="test_002",
            task_type="security_scan",
            target="test.com",
            parameters={"depth": "quick", "include_ssl": False},
            agents_used=["security_expert"],
            execution_time=45.2,
            success_rate=0.8,
            error_patterns=["timeout_error"],
            solution_quality=0.7,
        )

        # Test predictions
        predictions = await engine.predict_optimal_agent_combination(
            "security_scan", "newsite.com", {"depth": "standard"}
        )
        print(f"🎯 Predicted agents: {predictions}")

        # Test recommendations
        recommendations = await engine.recommend_task_optimizations(
            "security_scan", "newsite.com", {"depth": "standard"}
        )
        print(f"💡 Recommendations: {recommendations}")

        # Test cross-agent learning
        transfers = await engine.cross_agent_knowledge_transfer()
        print(f"🔄 Knowledge transfers: {len(transfers)}")

        print("✅ Test completed!")

    async def generate_report():
        """Generate insights report"""
        summary = await engine.get_collective_insights_summary()

        print("\n" + "=" * 60)
        print("🧠 COLLECTIVE INTELLIGENCE REPORT")
        print("=" * 60)
        print(f"Total Insights: {summary['total_insights']}")
        print(f"High Confidence Insights: {summary['high_confidence_insights']}")
        print(f"Knowledge Entries: {summary['knowledge_entries']}")
        print(f"Learning Graph Nodes: {summary['learning_graph_nodes']}")
        print(f"Learning Graph Edges: {summary['learning_graph_edges']}")

        print("\nInsight Categories:")
        for category, count in summary["insight_categories"].items():
            print(f"  - {category}: {count}")
        print("=" * 60)

    if args.test:
        asyncio.run(test_scenario())
    elif args.report:
        asyncio.run(generate_report())
    else:
        # Start learning manager
        manager = CollectiveIntelligenceManager()
        try:
            asyncio.run(manager.start_learning_cycle())
        except KeyboardInterrupt:
            print("👋 Collective intelligence system stopped")
