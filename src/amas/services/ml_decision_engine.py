"""
ML-Based Decision Engine for AMAS Intelligence System
Provides intelligent task allocation, resource optimization, and decision making
"""

import asyncio
import logging
import os
import queue
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Task type enumeration"""

    OSINT_COLLECTION = "osint_collection"
    INVESTIGATION = "investigation"
    FORENSICS = "forensics"
    DATA_ANALYSIS = "data_analysis"
    REVERSE_ENGINEERING = "reverse_engineering"
    METADATA_EXTRACTION = "metadata_extraction"
    REPORTING = "reporting"
    SECURITY_ANALYSIS = "security_analysis"
    COMPLIANCE_AUDIT = "compliance_audit"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class AgentType(Enum):
    """Agent type enumeration"""

    OSINT_AGENT = "osint_agent"
    INVESTIGATION_AGENT = "investigation_agent"
    FORENSICS_AGENT = "forensics_agent"
    DATA_ANALYSIS_AGENT = "data_analysis_agent"
    REVERSE_ENGINEERING_AGENT = "reverse_engineering_agent"
    METADATA_AGENT = "metadata_agent"
    REPORTING_AGENT = "reporting_agent"
    SECURITY_AGENT = "security_agent"
    COMPLIANCE_AGENT = "compliance_agent"
    PERFORMANCE_AGENT = "performance_agent"


class DecisionStrategy(Enum):
    """Decision strategy enumeration"""

    ML_OPTIMIZED = "ml_optimized"
    RULE_BASED = "rule_based"
    HYBRID = "hybrid"
    RANDOM = "random"
    ROUND_ROBIN = "round_robin"


@dataclass
class Task:
    """Task data structure"""

    id: str
    type: TaskType
    priority: int
    complexity: float
    estimated_duration: int  # minutes
    required_capabilities: List[str]
    resource_requirements: Dict[str, float]
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Agent:
    """Agent data structure"""

    id: str
    type: AgentType
    capabilities: List[str]
    current_load: float
    max_load: float
    performance_score: float
    availability: bool
    specializations: List[str] = field(default_factory=list)
    cost_per_hour: float = 0.0
    location: str = "default"
    last_activity: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AllocationDecision:
    """Task allocation decision"""

    task_id: str
    agent_id: str
    confidence: float
    estimated_completion_time: datetime
    cost_estimate: float
    reasoning: str
    alternative_agents: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)


@dataclass
class PerformanceMetrics:
    """Performance metrics for ML models"""

    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    last_updated: datetime
    training_samples: int


class MLDecisionEngine:
    """
    ML-Based Decision Engine for AMAS Intelligence System

    Provides:
    - Intelligent task allocation using ML models
    - Resource optimization and load balancing
    - Performance prediction and optimization
    - Adaptive learning from historical data
    - Multi-objective optimization
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the ML decision engine"""
        self.config = config

        # ML Models
        self.allocation_model = None
        self.performance_model = None
        self.cost_optimization_model = None
        self.load_balancing_model = None

        # Data storage
        self.tasks = {}
        self.agents = {}
        self.historical_data = []
        self.performance_history = []

        # Feature engineering
        self.scaler = StandardScaler()
        self.label_encoders = {}

        # ML configuration
        self.ml_config = {
            "retrain_interval": config.get("retrain_interval", 3600),  # seconds
            "min_training_samples": config.get("min_training_samples", 100),
            "model_accuracy_threshold": config.get("model_accuracy_threshold", 0.7),
            "feature_window": config.get("feature_window", 24),  # hours
            "prediction_horizon": config.get("prediction_horizon", 60),  # minutes
        }

        # Decision strategies
        self.decision_strategies = {
            DecisionStrategy.ML_OPTIMIZED: self._ml_optimized_allocation,
            DecisionStrategy.RULE_BASED: self._rule_based_allocation,
            DecisionStrategy.HYBRID: self._hybrid_allocation,
            DecisionStrategy.RANDOM: self._random_allocation,
            DecisionStrategy.ROUND_ROBIN: self._round_robin_allocation,
        }

        # Performance tracking
        self.model_performance = {}
        self.decision_history = deque(maxlen=10000)

        # Threading for model training
        self.training_queue = queue.Queue()
        self.training_thread = None
        self.training_active = False

        logger.info("ML Decision Engine initialized")

    async def initialize(self):
        """Initialize the ML decision engine"""
        try:
            logger.info("Initializing ML Decision Engine...")

            # Initialize ML models
            await self._initialize_ml_models()

            # Start background tasks
            await self._start_background_tasks()

            # Load historical data
            await self._load_historical_data()

            # Initialize feature engineering
            await self._initialize_feature_engineering()

            logger.info("ML Decision Engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize ML Decision Engine: {e}")
            raise

    async def _initialize_ml_models(self):
        """Initialize ML models"""
        try:
            # Task allocation model (classification)
            self.allocation_model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            )

            # Performance prediction model (regression)
            self.performance_model = GradientBoostingRegressor(
                n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
            )

            # Cost optimization model (regression)
            self.cost_optimization_model = xgb.XGBRegressor(
                n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
            )

            # Load balancing model (classification)
            self.load_balancing_model = MLPClassifier(
                hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42
            )

            logger.info("ML models initialized")

        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
            raise

    async def _start_background_tasks(self):
        """Start background tasks"""
        try:
            # Start model training thread
            self.training_thread = threading.Thread(target=self._training_worker)
            self.training_thread.daemon = True
            self.training_thread.start()

            # Start background tasks
            self.background_tasks = [
                asyncio.create_task(self._collect_performance_data()),
                asyncio.create_task(self._update_model_performance()),
                asyncio.create_task(self._optimize_allocations()),
                asyncio.create_task(self._cleanup_old_data()),
            ]

            logger.info("Background tasks started")

        except Exception as e:
            logger.error(f"Failed to start background tasks: {e}")
            raise

    async def _load_historical_data(self):
        """Load historical data for training"""
        try:
            # Generate sample historical data
            sample_data = await self._generate_sample_historical_data()
            self.historical_data.extend(sample_data)

            logger.info(f"Loaded {len(self.historical_data)} historical records")

        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")

    async def _generate_sample_historical_data(self) -> List[Dict[str, Any]]:
        """Generate sample historical data for training"""
        try:
            sample_data = []

            # Generate 1000 sample records
            for i in range(1000):
                # Random task
                task_type = np.random.choice(list(TaskType))
                task_complexity = np.random.uniform(0.1, 1.0)
                task_priority = np.random.randint(1, 6)

                # Random agent
                agent_type = np.random.choice(list(AgentType))
                agent_performance = np.random.uniform(0.5, 1.0)
                agent_load = np.random.uniform(0.0, 1.0)

                # Simulate allocation decision using secure random
                import secrets

                allocation_success = secrets.randbelow(100) > 20  # 80% success rate

                # Performance metrics
                completion_time = np.random.uniform(0.5, 5.0)  # hours
                cost = np.random.uniform(10, 100)
                quality_score = np.random.uniform(0.6, 1.0)

                record = {
                    "timestamp": datetime.utcnow()
                    - timedelta(days=np.random.randint(0, 30)),
                    "task_type": task_type.value,
                    "task_complexity": task_complexity,
                    "task_priority": task_priority,
                    "agent_type": agent_type.value,
                    "agent_performance": agent_performance,
                    "agent_load": agent_load,
                    "allocation_success": allocation_success,
                    "completion_time": completion_time,
                    "cost": cost,
                    "quality_score": quality_score,
                    "resource_utilization": np.random.uniform(0.3, 0.9),
                }

                sample_data.append(record)

            return sample_data

        except Exception as e:
            logger.error(f"Failed to generate sample data: {e}")
            return []

    async def _initialize_feature_engineering(self):
        """Initialize feature engineering components"""
        try:
            # Initialize label encoders for categorical features
            categorical_features = ["task_type", "agent_type"]

            for feature in categorical_features:
                self.label_encoders[feature] = LabelEncoder()

            logger.info("Feature engineering initialized")

        except Exception as e:
            logger.error(f"Failed to initialize feature engineering: {e}")

    def _training_worker(self):
        """Background worker for model training"""
        while True:
            try:
                # Wait for training request
                training_request = self.training_queue.get(timeout=60)

                if training_request is None:  # Shutdown signal
                    break

                # Perform training
                asyncio.run(self._train_models())

                self.training_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Training worker error: {e}")

    async def allocate_task(
        self, task: Task, strategy: DecisionStrategy = DecisionStrategy.ML_OPTIMIZED
    ) -> AllocationDecision:
        """Allocate a task to an agent using specified strategy"""
        try:
            # Store task
            self.tasks[task.id] = task

            # Get available agents
            available_agents = [
                agent
                for agent in self.agents.values()
                if agent.availability and agent.current_load < agent.max_load
            ]

            if not available_agents:
                raise Exception("No available agents for task allocation")

            # Apply decision strategy
            if strategy in self.decision_strategies:
                decision = await self.decision_strategies[strategy](
                    task, available_agents
                )
            else:
                decision = await self._ml_optimized_allocation(task, available_agents)

            # Store decision
            self.decision_history.append(
                {
                    "task_id": task.id,
                    "agent_id": decision.agent_id,
                    "strategy": strategy.value,
                    "confidence": decision.confidence,
                    "timestamp": datetime.utcnow(),
                }
            )

            # Update agent load
            if decision.agent_id in self.agents:
                self.agents[decision.agent_id].current_load += task.complexity

            logger.info(
                f"Task {task.id} allocated to agent {decision.agent_id} with confidence {decision.confidence:.3f}"
            )

            return decision

        except Exception as e:
            logger.error(f"Failed to allocate task {task.id}: {e}")
            raise

    async def _ml_optimized_allocation(
        self, task: Task, available_agents: List[Agent]
    ) -> AllocationDecision:
        """ML-optimized task allocation"""
        try:
            if (
                not self.allocation_model
                or len(self.historical_data) < self.ml_config["min_training_samples"]
            ):
                # Fallback to rule-based allocation
                return await self._rule_based_allocation(task, available_agents)

            # Prepare features for prediction
            features = await self._prepare_allocation_features(task, available_agents)

            if features is None:
                return await self._rule_based_allocation(task, available_agents)

            # Predict allocation probabilities
            probabilities = self.allocation_model.predict_proba(features)

            # Select best agent
            best_agent_idx = np.argmax(probabilities[:, 1])  # Probability of success
            best_agent = available_agents[best_agent_idx]
            confidence = probabilities[best_agent_idx, 1]

            # Generate decision
            decision = AllocationDecision(
                task_id=task.id,
                agent_id=best_agent.id,
                confidence=confidence,
                estimated_completion_time=datetime.utcnow()
                + timedelta(minutes=task.estimated_duration),
                cost_estimate=await self._estimate_cost(task, best_agent),
                reasoning=f"ML model selected agent {best_agent.id} with {confidence:.3f} confidence",
                alternative_agents=[
                    agent.id
                    for i, agent in enumerate(available_agents)
                    if i != best_agent_idx
                ],
                risk_factors=await self._assess_risks(task, best_agent),
            )

            return decision

        except Exception as e:
            logger.error(f"ML allocation failed: {e}")
            return await self._rule_based_allocation(task, available_agents)

    async def _rule_based_allocation(
        self, task: Task, available_agents: List[Agent]
    ) -> AllocationDecision:
        """Rule-based task allocation"""
        try:
            # Filter agents by capabilities
            suitable_agents = [
                agent
                for agent in available_agents
                if all(cap in agent.capabilities for cap in task.required_capabilities)
            ]

            if not suitable_agents:
                suitable_agents = available_agents  # Fallback to all agents

            # Score agents based on rules
            agent_scores = []
            for agent in suitable_agents:
                score = 0

                # Performance score
                score += agent.performance_score * 0.3

                # Load factor (prefer less loaded agents)
                load_factor = 1 - (agent.current_load / agent.max_load)
                score += load_factor * 0.3

                # Capability match
                capability_match = len(
                    set(task.required_capabilities) & set(agent.capabilities)
                ) / len(task.required_capabilities)
                score += capability_match * 0.2

                # Specialization match
                if task.type.value in agent.specializations:
                    score += 0.2

                agent_scores.append((agent, score))

            # Select best agent
            best_agent, best_score = max(agent_scores, key=lambda x: x[1])

            decision = AllocationDecision(
                task_id=task.id,
                agent_id=best_agent.id,
                confidence=min(1.0, best_score),
                estimated_completion_time=datetime.utcnow()
                + timedelta(minutes=task.estimated_duration),
                cost_estimate=await self._estimate_cost(task, best_agent),
                reasoning=f"Rule-based selection: agent {best_agent.id} scored {best_score:.3f}",
                alternative_agents=[
                    agent.id
                    for agent, _ in sorted(
                        agent_scores, key=lambda x: x[1], reverse=True
                    )[1:3]
                ],
                risk_factors=await self._assess_risks(task, best_agent),
            )

            return decision

        except Exception as e:
            logger.error(f"Rule-based allocation failed: {e}")
            # Emergency fallback
            return AllocationDecision(
                task_id=task.id,
                agent_id=available_agents[0].id,
                confidence=0.1,
                estimated_completion_time=datetime.utcnow()
                + timedelta(minutes=task.estimated_duration),
                cost_estimate=0.0,
                reasoning="Emergency fallback allocation",
                risk_factors=["Low confidence allocation"],
            )

    async def _hybrid_allocation(
        self, task: Task, available_agents: List[Agent]
    ) -> AllocationDecision:
        """Hybrid allocation combining ML and rule-based approaches"""
        try:
            # Get ML allocation
            ml_decision = await self._ml_optimized_allocation(task, available_agents)

            # Get rule-based allocation
            rule_decision = await self._rule_based_allocation(task, available_agents)

            # Combine decisions
            if ml_decision.confidence > 0.7:
                # High confidence ML decision
                return ml_decision
            elif rule_decision.confidence > 0.8:
                # High confidence rule-based decision
                return rule_decision
            else:
                # Use ML decision but with lower confidence
                ml_decision.confidence *= 0.8
                ml_decision.reasoning = (
                    "Hybrid: ML decision with reduced confidence due to uncertainty"
                )
                return ml_decision

        except Exception as e:
            logger.error(f"Hybrid allocation failed: {e}")
            return await self._rule_based_allocation(task, available_agents)

    async def _random_allocation(
        self, task: Task, available_agents: List[Agent]
    ) -> AllocationDecision:
        """Random task allocation"""
        try:
            agent = np.random.choice(available_agents)

            return AllocationDecision(
                task_id=task.id,
                agent_id=agent.id,
                confidence=0.5,
                estimated_completion_time=datetime.utcnow()
                + timedelta(minutes=task.estimated_duration),
                cost_estimate=await self._estimate_cost(task, agent),
                reasoning="Random allocation",
                risk_factors=["Random selection may not be optimal"],
            )

        except Exception as e:
            logger.error(f"Random allocation failed: {e}")
            raise

    async def _round_robin_allocation(
        self, task: Task, available_agents: List[Agent]
    ) -> AllocationDecision:
        """Round-robin task allocation"""
        try:
            # Simple round-robin based on task ID hash
            agent_index = hash(task.id) % len(available_agents)
            agent = available_agents[agent_index]

            return AllocationDecision(
                task_id=task.id,
                agent_id=agent.id,
                confidence=0.6,
                estimated_completion_time=datetime.utcnow()
                + timedelta(minutes=task.estimated_duration),
                cost_estimate=await self._estimate_cost(task, agent),
                reasoning="Round-robin allocation",
                risk_factors=[],
            )

        except Exception as e:
            logger.error(f"Round-robin allocation failed: {e}")
            raise

    async def _prepare_allocation_features(
        self, task: Task, available_agents: List[Agent]
    ) -> Optional[np.ndarray]:
        """Prepare features for ML allocation model"""
        try:
            if not self.historical_data:
                return None

            # Convert historical data to DataFrame
            # Prepare features for each agent
            features_list = []

            for agent in available_agents:
                # Create feature vector
                feature_vector = [
                    (
                        self.label_encoders["task_type"].transform([task.type.value])[0]
                        if hasattr(self.label_encoders["task_type"], "classes_")
                        else 0
                    ),
                    task.complexity,
                    task.priority,
                    (
                        self.label_encoders["agent_type"].transform([agent.type.value])[
                            0
                        ]
                        if hasattr(self.label_encoders["agent_type"], "classes_")
                        else 0
                    ),
                    agent.performance_score,
                    agent.current_load,
                    len(set(task.required_capabilities) & set(agent.capabilities))
                    / len(task.required_capabilities),
                    1 if task.type.value in agent.specializations else 0,
                ]

                features_list.append(feature_vector)

            return np.array(features_list)

        except Exception as e:
            logger.error(f"Failed to prepare allocation features: {e}")
            return None

    async def _estimate_cost(self, task: Task, agent: Agent) -> float:
        """Estimate cost for task allocation"""
        try:
            base_cost = agent.cost_per_hour * (task.estimated_duration / 60)
            complexity_multiplier = 1 + (task.complexity - 0.5) * 0.5
            priority_multiplier = 1 + (task.priority - 3) * 0.1

            return base_cost * complexity_multiplier * priority_multiplier

        except Exception as e:
            logger.error(f"Failed to estimate cost: {e}")
            return 0.0

    async def _assess_risks(self, task: Task, agent: Agent) -> List[str]:
        """Assess risks for task allocation"""
        try:
            risks = []

            # High load risk
            if agent.current_load > agent.max_load * 0.8:
                risks.append("Agent has high current load")

            # Capability mismatch risk
            missing_capabilities = set(task.required_capabilities) - set(
                agent.capabilities
            )
            if missing_capabilities:
                risks.append(f"Missing capabilities: {missing_capabilities}")

            # Performance risk
            if agent.performance_score < 0.7:
                risks.append("Agent has low performance score")

            # Deadline risk
            if task.deadline:
                estimated_completion = datetime.utcnow() + timedelta(
                    minutes=task.estimated_duration
                )
                if estimated_completion > task.deadline:
                    risks.append("Task may exceed deadline")

            return risks

        except Exception as e:
            logger.error(f"Failed to assess risks: {e}")
            return []

    async def register_agent(self, agent: Agent) -> bool:
        """Register an agent with the decision engine"""
        try:
            self.agents[agent.id] = agent
            logger.info(f"Agent {agent.id} registered")
            return True

        except Exception as e:
            logger.error(f"Failed to register agent {agent.id}: {e}")
            return False

    async def update_agent_status(self, agent_id: str, **updates) -> bool:
        """Update agent status"""
        try:
            if agent_id not in self.agents:
                return False

            agent = self.agents[agent_id]
            for key, value in updates.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)

            agent.last_activity = datetime.utcnow()
            return True

        except Exception as e:
            logger.error(f"Failed to update agent status: {e}")
            return False

    async def _collect_performance_data(self):
        """Collect performance data for model training"""
        while True:
            try:
                # Collect current system performance
                performance_data = {
                    "timestamp": datetime.utcnow(),
                    "active_tasks": len([t for t in self.tasks.values()]),
                    "active_agents": len(
                        [a for a in self.agents.values() if a.availability]
                    ),
                    "average_load": (
                        np.mean([a.current_load for a in self.agents.values()])
                        if self.agents
                        else 0
                    ),
                    "allocation_success_rate": await self._calculate_allocation_success_rate(),
                }

                self.performance_history.append(performance_data)

                # Keep only recent data
                cutoff_time = datetime.utcnow() - timedelta(
                    hours=self.ml_config["feature_window"]
                )
                self.performance_history = [
                    p for p in self.performance_history if p["timestamp"] > cutoff_time
                ]

                await asyncio.sleep(300)  # Collect every 5 minutes

            except Exception as e:
                logger.error(f"Performance data collection error: {e}")
                await asyncio.sleep(60)

    async def _calculate_allocation_success_rate(self) -> float:
        """Calculate allocation success rate"""
        try:
            if not self.decision_history:
                return 0.0

            # Calculate success rate from recent decisions
            recent_decisions = list(self.decision_history)[-100:]  # Last 100 decisions
            successful_allocations = len(
                [d for d in recent_decisions if d["confidence"] > 0.7]
            )

            return (
                successful_allocations / len(recent_decisions)
                if recent_decisions
                else 0.0
            )

        except Exception as e:
            logger.error(f"Failed to calculate allocation success rate: {e}")
            return 0.0

    async def _update_model_performance(self):
        """Update model performance metrics"""
        while True:
            try:
                if len(self.historical_data) >= self.ml_config["min_training_samples"]:
                    # Trigger model retraining
                    self.training_queue.put("retrain")

                await asyncio.sleep(self.ml_config["retrain_interval"])

            except Exception as e:
                logger.error(f"Model performance update error: {e}")
                await asyncio.sleep(60)

    async def _train_models(self):
        """Train ML models"""
        try:
            if len(self.historical_data) < self.ml_config["min_training_samples"]:
                logger.info("Insufficient data for model training")
                return

            logger.info("Starting model training...")

            # Prepare training data
            df = pd.DataFrame(self.historical_data)

            # Train allocation model
            await self._train_allocation_model(df)

            # Train performance model
            await self._train_performance_model(df)

            # Train cost optimization model
            await self._train_cost_optimization_model(df)

            # Train load balancing model
            await self._train_load_balancing_model(df)

            logger.info("Model training completed")

        except Exception as e:
            logger.error(f"Model training failed: {e}")

    async def _train_allocation_model(self, df: pd.DataFrame):
        """Train task allocation model"""
        try:
            # Prepare features and target
            X = df[
                [
                    "task_type",
                    "task_complexity",
                    "task_priority",
                    "agent_type",
                    "agent_performance",
                    "agent_load",
                ]
            ].copy()
            y = df["allocation_success"].astype(int)

            # Encode categorical features
            for feature in ["task_type", "agent_type"]:
                if feature not in self.label_encoders:
                    self.label_encoders[feature] = LabelEncoder()
                X[feature] = self.label_encoders[feature].fit_transform(X[feature])

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Train model
            self.allocation_model.fit(X_train, y_train)

            # Evaluate model
            y_pred = self.allocation_model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            # Update performance metrics
            self.model_performance["allocation_model"] = PerformanceMetrics(
                model_name="allocation_model",
                accuracy=accuracy,
                precision=0.0,  # Would calculate from classification_report
                recall=0.0,
                f1_score=0.0,
                last_updated=datetime.utcnow(),
                training_samples=len(X_train),
            )

            logger.info(f"Allocation model trained with accuracy: {accuracy:.3f}")

        except Exception as e:
            logger.error(f"Failed to train allocation model: {e}")

    async def _train_performance_model(self, df: pd.DataFrame):
        """Train performance prediction model"""
        try:
            # Prepare features and target
            X = df[
                ["task_type", "task_complexity", "agent_performance", "agent_load"]
            ].copy()
            y = df["completion_time"]

            # Encode categorical features
            X["task_type"] = self.label_encoders["task_type"].transform(X["task_type"])

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Train model
            self.performance_model.fit(X_train, y_train)

            # Evaluate model
            y_pred = self.performance_model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            accuracy = 1 - (mse / np.var(y_test))

            logger.info(f"Performance model trained with accuracy: {accuracy:.3f}")

        except Exception as e:
            logger.error(f"Failed to train performance model: {e}")

    async def _train_cost_optimization_model(self, df: pd.DataFrame):
        """Train cost optimization model"""
        try:
            # Prepare features and target
            X = df[
                ["task_type", "task_complexity", "agent_type", "agent_performance"]
            ].copy()
            y = df["cost"]

            # Encode categorical features
            X["task_type"] = self.label_encoders["task_type"].transform(X["task_type"])
            X["agent_type"] = self.label_encoders["agent_type"].transform(
                X["agent_type"]
            )

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Train model
            self.cost_optimization_model.fit(X_train, y_train)

            # Evaluate model
            y_pred = self.cost_optimization_model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            accuracy = 1 - (mse / np.var(y_test))

            logger.info(
                f"Cost optimization model trained with accuracy: {accuracy:.3f}"
            )

        except Exception as e:
            logger.error(f"Failed to train cost optimization model: {e}")

    async def _train_load_balancing_model(self, df: pd.DataFrame):
        """Train load balancing model"""
        try:
            # Prepare features and target
            X = df[
                [
                    "agent_type",
                    "agent_performance",
                    "agent_load",
                    "resource_utilization",
                ]
            ].copy()
            y = (df["agent_load"] > 0.8).astype(int)  # Binary: overloaded or not

            # Encode categorical features
            X["agent_type"] = self.label_encoders["agent_type"].transform(
                X["agent_type"]
            )

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Train model
            self.load_balancing_model.fit(X_train, y_train)

            # Evaluate model
            y_pred = self.load_balancing_model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            logger.info(f"Load balancing model trained with accuracy: {accuracy:.3f}")

        except Exception as e:
            logger.error(f"Failed to train load balancing model: {e}")

    async def _optimize_allocations(self):
        """Optimize current allocations"""
        while True:
            try:
                # Check for overloaded agents
                overloaded_agents = [
                    agent
                    for agent in self.agents.values()
                    if agent.current_load > agent.max_load * 0.9
                ]

                if overloaded_agents:
                    await self._rebalance_load(overloaded_agents)

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Allocation optimization error: {e}")
                await asyncio.sleep(60)

    async def _rebalance_load(self, overloaded_agents: List[Agent]):
        """Rebalance load among agents"""
        try:
            for agent in overloaded_agents:
                # Find tasks that can be reassigned
                # This would implement load balancing logic
                logger.info(f"Rebalancing load for agent {agent.id}")

        except Exception as e:
            logger.error(f"Failed to rebalance load: {e}")

    async def _cleanup_old_data(self):
        """Clean up old data"""
        while True:
            try:
                # Clean up old historical data
                cutoff_time = datetime.utcnow() - timedelta(days=30)
                self.historical_data = [
                    record
                    for record in self.historical_data
                    if record["timestamp"] > cutoff_time
                ]

                # Clean up old performance data
                self.performance_history = [
                    record
                    for record in self.performance_history
                    if record["timestamp"] > cutoff_time
                ]

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                logger.error(f"Data cleanup error: {e}")
                await asyncio.sleep(60)

    async def get_decision_engine_stats(self) -> Dict[str, Any]:
        """Get decision engine statistics"""
        try:
            return {
                "total_tasks": len(self.tasks),
                "total_agents": len(self.agents),
                "active_agents": len(
                    [a for a in self.agents.values() if a.availability]
                ),
                "historical_records": len(self.historical_data),
                "decision_history_size": len(self.decision_history),
                "model_performance": {
                    name: {
                        "accuracy": metrics.accuracy,
                        "last_updated": metrics.last_updated.isoformat(),
                        "training_samples": metrics.training_samples,
                    }
                    for name, metrics in self.model_performance.items()
                },
                "allocation_success_rate": await self._calculate_allocation_success_rate(),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get decision engine stats: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Shutdown decision engine"""
        try:
            logger.info("Shutting down ML Decision Engine...")

            # Stop background tasks
            for task in self.background_tasks:
                task.cancel()

            # Wait for tasks to complete
            await asyncio.gather(*self.background_tasks, return_exceptions=True)

            # Stop training thread
            self.training_queue.put(None)
            if self.training_thread:
                self.training_thread.join(timeout=10)

            # Save models
            await self._save_models()

            logger.info("ML Decision Engine shutdown complete")

        except Exception as e:
            logger.error(f"Error during decision engine shutdown: {e}")

    async def _save_models(self):
        """Save trained models to disk"""
        try:
            models_dir = "/app/models"
            os.makedirs(models_dir, exist_ok=True)

            # Save models
            if self.allocation_model:
                joblib.dump(
                    self.allocation_model,
                    os.path.join(models_dir, "allocation_model.joblib"),
                )

            if self.performance_model:
                joblib.dump(
                    self.performance_model,
                    os.path.join(models_dir, "performance_model.joblib"),
                )

            if self.cost_optimization_model:
                joblib.dump(
                    self.cost_optimization_model,
                    os.path.join(models_dir, "cost_optimization_model.joblib"),
                )

            if self.load_balancing_model:
                joblib.dump(
                    self.load_balancing_model,
                    os.path.join(models_dir, "load_balancing_model.joblib"),
                )

            # Save scaler and encoders
            joblib.dump(self.scaler, os.path.join(models_dir, "scaler.joblib"))
            joblib.dump(
                self.label_encoders, os.path.join(models_dir, "label_encoders.joblib")
            )

            logger.info("Models saved to disk")

        except Exception as e:
            logger.error(f"Failed to save models: {e}")
