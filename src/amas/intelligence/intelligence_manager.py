#!/usr/bin/env python3
"""
AMAS Intelligence Manager
Coordinates collective learning, adaptive personalities, and predictive intelligence
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..agents.adaptive_personality import PersonalityOrchestrator
from .collective_learning import CollectiveIntelligenceEngine
from .predictive_engine import PredictiveIntelligenceEngine


class AMASIntelligenceManager:
    """Central manager for all intelligence systems"""

    def __init__(self):
        self.collective_intelligence = CollectiveIntelligenceEngine()
        self.personality_orchestrator = PersonalityOrchestrator()
        self.predictive_engine = PredictiveIntelligenceEngine()
        self.logger = logging.getLogger(__name__)

        # Register default agents
        self._register_default_agents()

    def _register_default_agents(self):
        """Register default AMAS agents with personality system"""
        agents = [
            "security_expert",
            "code_analysis",
            "intelligence_gathering",
            "performance_monitor",
            "documentation_specialist",
            "testing_coordinator",
            "integration_manager",
        ]

        for agent in agents:
            self.personality_orchestrator.register_agent(agent)

        self.logger.info(f"✅ Registered {len(agents)} agents with intelligence systems")

    async def start_intelligence_systems(self):
        """Start all intelligence systems"""
        self.logger.info("🧠 Starting AMAS Intelligence Systems...")

        # Start collective learning cycle in background
        asyncio.create_task(self._collective_learning_cycle())

        self.logger.info("✅ Intelligence systems started")

    async def _collective_learning_cycle(self):
        """Background collective learning cycle"""
        while True:
            try:
                await self.collective_intelligence.cross_agent_knowledge_transfer()
                await asyncio.sleep(3600)  # Every hour
            except Exception as e:
                self.logger.error(f"❌ Error in learning cycle: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes

    async def record_task_execution(
        self,
        task_id: str,
        task_type: str,
        agents_used: List[str],
        execution_time: float,
        success: bool,
        quality_score: float,
        user_feedback: Optional[Dict] = None
    ):
        """
        Record task execution for learning (PART_2 requirement)
        
        This feeds data back into ML models for continuous improvement
        """
        try:
            # Prepare training data
            training_data = {
                "task_id": task_id,
                "task_type": task_type,
                "agents_used": agents_used,
                "execution_time": execution_time,
                "success_rate": 1.0 if success else 0.0,
                "quality_score": quality_score,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to predictive engine training data
            await self.predictive_engine.add_training_data(
                "task_outcome",
                training_data
            )
            
            # Also record for collective learning
            await self.collective_intelligence.record_task_execution(
                task_id=task_id,
                task_type=task_type,
                target="",  # Not available in this signature
                parameters={},  # Not available in this signature
                agents_used=agents_used,
                execution_time=execution_time,
                success_rate=1.0 if success else 0.0,
                error_patterns=[],
                solution_quality=quality_score,
            )
            
            self.logger.info(f"Recorded task execution for learning: {task_id}")
        
        except Exception as e:
            self.logger.error(f"Failed to record task execution: {e}")

    async def get_completed_task_count(self) -> int:
        """Get total completed tasks for retraining triggers"""
        import pandas as pd
        
        task_outcome_data = self.predictive_engine.training_data.get(
            "task_outcome",
            pd.DataFrame()
        )
        
        return len(task_outcome_data)

    async def process_task_completion(self, task_data: Dict[str, Any]):
        """Process completed task for all intelligence systems"""

        # Record for collective learning
        await self.collective_intelligence.record_task_execution(
            task_id=task_data["task_id"],
            task_type=task_data["task_type"],
            target=task_data["target"],
            parameters=task_data["parameters"],
            agents_used=task_data["agents_used"],
            execution_time=task_data["execution_time"],
            success_rate=task_data["success_rate"],
            error_patterns=task_data.get("error_patterns", []),
            solution_quality=task_data["solution_quality"],
        )

        # Add to predictive training data
        await self.predictive_engine.add_training_data("task_outcome", task_data)

        # Process user feedback for personality adaptation
        if "user_feedback" in task_data:
            for agent in task_data["agents_used"]:
                await self.personality_orchestrator.record_task_feedback(
                    agent,
                    task_data.get("user_id", "unknown"),
                    task_data["user_feedback"],
                    task_data,
                )

    async def optimize_task_before_execution(
        self, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize task using all intelligence systems before execution"""

        # Get optimal agent combination from collective intelligence
        optimal_agents = (
            await self.collective_intelligence.predict_optimal_agent_combination(
                task_data["task_type"], task_data["target"], task_data["parameters"]
            )
        )

        # Get task outcome prediction
        task_prediction = await self.predictive_engine.predict_task_outcome(
            task_data["task_type"],
            task_data["target"],
            task_data["parameters"],
            [agent for agent, _ in optimal_agents[:3]],
        )

        # Get optimization recommendations
        recommendations = (
            await self.collective_intelligence.recommend_task_optimizations(
                task_data["task_type"], task_data["target"], task_data["parameters"]
            )
        )

        # Adapt agent personalities for this task
        personality_prompts = {}
        for agent, _ in optimal_agents[:3]:
            prompt = await self.personality_orchestrator.adapt_agent_for_task(
                agent, task_data
            )
            personality_prompts[agent] = prompt

        return {
            "optimal_agents": [agent for agent, _ in optimal_agents[:3]],
            "agent_confidence_scores": dict(optimal_agents[:3]),
            "task_prediction": task_prediction,
            "optimization_recommendations": recommendations,
            "personality_prompts": personality_prompts,
        }

    async def get_intelligence_dashboard_data(self) -> Dict[str, Any]:
        """Get data for intelligence dashboard"""

        # Collective intelligence summary
        collective_summary = (
            await self.collective_intelligence.get_collective_insights_summary()
        )

        # Personality system summary
        personality_summary = (
            await self.personality_orchestrator.get_system_personality_report()
        )

        # Prediction accuracy report
        prediction_accuracy = (
            await self.predictive_engine.get_prediction_accuracy_report()
        )

        # Resource predictions
        resource_prediction = await self.predictive_engine.predict_system_resources(60)

        return {
            "collective_intelligence": collective_summary,
            "adaptive_personalities": personality_summary,
            "predictive_accuracy": prediction_accuracy,
            "resource_predictions": resource_prediction,
            "system_status": "operational",
            "intelligence_level": "advanced",
        }


# Global intelligence manager instance
_intelligence_manager_instance: Optional[AMASIntelligenceManager] = None


def get_intelligence_manager() -> AMASIntelligenceManager:
    """Get or create the global intelligence manager instance"""
    global _intelligence_manager_instance
    if _intelligence_manager_instance is None:
        _intelligence_manager_instance = AMASIntelligenceManager()
    return _intelligence_manager_instance


# Backward compatibility
intelligence_manager = get_intelligence_manager()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(intelligence_manager.start_intelligence_systems())
