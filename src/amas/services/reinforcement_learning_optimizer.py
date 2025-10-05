"""
Reinforcement Learning Performance Optimizer for AMAS Intelligence System
Provides adaptive performance optimization using RL algorithms
"""

import asyncio
import logging
import numpy as np
import json
import time
import random
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import threading
import queue
from collections import deque
import pickle
import os

# RL Libraries (would be installed in production)
try:
    import gym
    from stable_baselines3 import PPO, DQN, A2C
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.callbacks import EvalCallback
    from stable_baselines3.common.monitor import Monitor

    RL_AVAILABLE = True
except ImportError:
    RL_AVAILABLE = False

    # Mock classes for development
    class PPO:
        def __init__(self, *args, **kwargs):
            pass

        def learn(self, *args, **kwargs):
            pass

        def predict(self, *args, **kwargs):
            return [0], None

        def save(self, *args, **kwargs):
            pass

        def load(self, *args, **kwargs):
            pass


logger = logging.getLogger(__name__)


class OptimizationGoal(Enum):
    """Optimization goal enumeration"""

    MINIMIZE_RESPONSE_TIME = "minimize_response_time"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"
    MINIMIZE_RESOURCE_USAGE = "minimize_resource_usage"
    MAXIMIZE_AVAILABILITY = "maximize_availability"
    MINIMIZE_COST = "minimize_cost"
    BALANCED = "balanced"


class ActionType(Enum):
    """Action type enumeration"""

    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    ADJUST_CACHE = "adjust_cache"
    MODIFY_LOAD_BALANCING = "modify_load_balancing"
    OPTIMIZE_QUERIES = "optimize_queries"
    ADJUST_TIMEOUTS = "adjust_timeouts"
    ENABLE_COMPRESSION = "enable_compression"
    DISABLE_FEATURES = "disable_features"


@dataclass
class SystemState:
    """System state representation"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    response_time: float
    throughput: float
    error_rate: float
    active_connections: int
    queue_size: int
    cache_hit_rate: float
    availability: float
    cost: float


@dataclass
class OptimizationAction:
    """Optimization action"""

    action_type: ActionType
    parameters: Dict[str, Any]
    confidence: float
    expected_impact: float
    risk_level: str = "low"


@dataclass
class OptimizationResult:
    """Optimization result"""

    action: OptimizationAction
    reward: float
    new_state: SystemState
    success: bool
    metrics_improvement: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AMASOptimizationEnv:
    """
    Custom Gym environment for AMAS optimization
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.action_space = gym.spaces.Discrete(len(ActionType))
        self.observation_space = gym.spaces.Box(
            low=0, high=100, shape=(12,), dtype=np.float32
        )

        self.current_state = None
        self.initial_state = None
        self.episode_reward = 0
        self.episode_steps = 0
        self.max_steps = config.get("max_episode_steps", 1000)

        # Performance baselines
        self.baselines = {
            "response_time": 1.0,
            "throughput": 100,
            "cpu_usage": 50.0,
            "memory_usage": 60.0,
            "error_rate": 0.01,
        }

        # Action effects (simulated)
        self.action_effects = {
            ActionType.SCALE_UP: {"cpu_usage": -10, "memory_usage": -5, "cost": 20},
            ActionType.SCALE_DOWN: {"cpu_usage": 10, "memory_usage": 5, "cost": -20},
            ActionType.ADJUST_CACHE: {"response_time": -0.2, "memory_usage": 5},
            ActionType.MODIFY_LOAD_BALANCING: {"response_time": -0.1, "throughput": 10},
            ActionType.OPTIMIZE_QUERIES: {"response_time": -0.3, "cpu_usage": -5},
            ActionType.ADJUST_TIMEOUTS: {"response_time": 0.1, "error_rate": -0.005},
            ActionType.ENABLE_COMPRESSION: {"network_io": -20, "cpu_usage": 5},
            ActionType.DISABLE_FEATURES: {
                "cpu_usage": -15,
                "memory_usage": -10,
                "availability": -2,
            },
        }

    def reset(self):
        """Reset environment to initial state"""
        self.current_state = self._generate_initial_state()
        self.initial_state = self.current_state
        self.episode_reward = 0
        self.episode_steps = 0
        return self._state_to_observation(self.current_state)

    def step(self, action):
        """Execute action and return new state, reward, done, info"""
        if self.episode_steps >= self.max_steps:
            return self._state_to_observation(self.current_state), 0, True, {}

        # Execute action
        new_state = self._apply_action(action, self.current_state)

        # Calculate reward
        reward = self._calculate_reward(self.current_state, new_state, action)

        # Update state
        self.current_state = new_state
        self.episode_reward += reward
        self.episode_steps += 1

        # Check if done
        done = self.episode_steps >= self.max_steps

        # Generate info
        info = {
            "episode_reward": self.episode_reward,
            "episode_steps": self.episode_steps,
            "state_metrics": self._extract_metrics(new_state),
        }

        return self._state_to_observation(new_state), reward, done, info

    def _generate_initial_state(self) -> SystemState:
        """Generate initial system state"""
        return SystemState(
            timestamp=datetime.utcnow(),
            cpu_usage=random.uniform(30, 70),
            memory_usage=random.uniform(40, 80),
            disk_usage=random.uniform(20, 60),
            network_io=random.uniform(1000, 5000),
            response_time=random.uniform(0.5, 3.0),
            throughput=random.uniform(50, 150),
            error_rate=random.uniform(0.001, 0.05),
            active_connections=random.randint(10, 100),
            queue_size=random.randint(0, 50),
            cache_hit_rate=random.uniform(0.7, 0.95),
            availability=random.uniform(95, 100),
            cost=random.uniform(100, 500),
        )

    def _apply_action(self, action: int, state: SystemState) -> SystemState:
        """Apply action to current state"""
        action_type = list(ActionType)[action]
        effects = self.action_effects.get(action_type, {})

        # Create new state with applied effects
        new_state = SystemState(
            timestamp=datetime.utcnow(),
            cpu_usage=max(0, min(100, state.cpu_usage + effects.get("cpu_usage", 0))),
            memory_usage=max(
                0, min(100, state.memory_usage + effects.get("memory_usage", 0))
            ),
            disk_usage=state.disk_usage,
            network_io=max(0, state.network_io + effects.get("network_io", 0)),
            response_time=max(
                0.1, state.response_time + effects.get("response_time", 0)
            ),
            throughput=max(0, state.throughput + effects.get("throughput", 0)),
            error_rate=max(0, min(1, state.error_rate + effects.get("error_rate", 0))),
            active_connections=state.active_connections,
            queue_size=state.queue_size,
            cache_hit_rate=max(
                0, min(1, state.cache_hit_rate + effects.get("cache_hit_rate", 0))
            ),
            availability=max(
                0, min(100, state.availability + effects.get("availability", 0))
            ),
            cost=max(0, state.cost + effects.get("cost", 0)),
        )

        return new_state

    def _calculate_reward(
        self, old_state: SystemState, new_state: SystemState, action: int
    ) -> float:
        """Calculate reward for action"""
        reward = 0

        # Response time improvement
        if new_state.response_time < old_state.response_time:
            reward += 10 * (old_state.response_time - new_state.response_time)
        else:
            reward -= 5 * (new_state.response_time - old_state.response_time)

        # Throughput improvement
        if new_state.throughput > old_state.throughput:
            reward += 0.1 * (new_state.throughput - old_state.throughput)
        else:
            reward -= 0.05 * (old_state.throughput - new_state.throughput)

        # Resource usage optimization
        if new_state.cpu_usage < old_state.cpu_usage:
            reward += 2 * (old_state.cpu_usage - new_state.cpu_usage)
        else:
            reward -= 1 * (new_state.cpu_usage - old_state.cpu_usage)

        if new_state.memory_usage < old_state.memory_usage:
            reward += 2 * (old_state.memory_usage - new_state.memory_usage)
        else:
            reward -= 1 * (new_state.memory_usage - old_state.memory_usage)

        # Error rate reduction
        if new_state.error_rate < old_state.error_rate:
            reward += 100 * (old_state.error_rate - new_state.error_rate)
        else:
            reward -= 50 * (new_state.error_rate - old_state.error_rate)

        # Cost optimization
        if new_state.cost < old_state.cost:
            reward += 0.01 * (old_state.cost - new_state.cost)
        else:
            reward -= 0.005 * (new_state.cost - old_state.cost)

        # Availability maintenance
        if new_state.availability >= 99:
            reward += 5
        elif new_state.availability < 95:
            reward -= 20

        return reward

    def _state_to_observation(self, state: SystemState) -> np.ndarray:
        """Convert state to observation vector"""
        return np.array(
            [
                state.cpu_usage,
                state.memory_usage,
                state.disk_usage,
                state.network_io / 1000,  # Normalize
                state.response_time,
                state.throughput / 100,  # Normalize
                state.error_rate * 100,  # Convert to percentage
                state.active_connections / 100,  # Normalize
                state.queue_size / 100,  # Normalize
                state.cache_hit_rate * 100,  # Convert to percentage
                state.availability,
                state.cost / 1000,  # Normalize
            ],
            dtype=np.float32,
        )

    def _extract_metrics(self, state: SystemState) -> Dict[str, float]:
        """Extract key metrics from state"""
        return {
            "cpu_usage": state.cpu_usage,
            "memory_usage": state.memory_usage,
            "response_time": state.response_time,
            "throughput": state.throughput,
            "error_rate": state.error_rate,
            "availability": state.availability,
            "cost": state.cost,
        }


class ReinforcementLearningOptimizer:
    """
    Reinforcement Learning Performance Optimizer for AMAS Intelligence System

    Provides:
    - Adaptive performance optimization using RL
    - Multi-objective optimization
    - Continuous learning and adaptation
    - Real-time optimization decisions
    - Performance prediction and planning
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the RL optimizer"""
        self.config = config
        self.optimization_goal = OptimizationGoal(
            config.get("optimization_goal", "balanced")
        )

        # RL Models
        self.ppo_model = None
        self.dqn_model = None
        self.a2c_model = None
        self.current_model = None

        # Environment
        self.env = AMASOptimizationEnv(config)

        # Training data
        self.training_data = deque(maxlen=10000)
        self.optimization_history = []
        self.performance_metrics = []

        # Optimization state
        self.current_state = None
        self.last_action = None
        self.optimization_active = False

        # Learning parameters
        self.learning_rate = config.get("learning_rate", 0.0003)
        self.batch_size = config.get("batch_size", 64)
        self.epsilon = config.get("epsilon", 0.1)
        self.epsilon_decay = config.get("epsilon_decay", 0.995)
        self.epsilon_min = config.get("epsilon_min", 0.01)

        # Performance thresholds
        self.performance_thresholds = {
            "response_time": config.get("response_time_threshold", 2.0),
            "throughput": config.get("throughput_threshold", 100),
            "cpu_usage": config.get("cpu_usage_threshold", 80.0),
            "memory_usage": config.get("memory_usage_threshold", 85.0),
            "error_rate": config.get("error_rate_threshold", 0.05),
        }

        # Training control
        self.training_thread = None
        self.training_queue = queue.Queue()
        self.training_active = False

        logger.info("Reinforcement Learning Optimizer initialized")

    async def initialize(self):
        """Initialize the RL optimizer"""
        try:
            logger.info("Initializing Reinforcement Learning Optimizer...")

            if not RL_AVAILABLE:
                logger.warning("RL libraries not available, using mock implementation")

            # Initialize RL models
            await self._initialize_models()

            # Load existing models if available
            await self._load_models()

            # Start training thread
            await self._start_training_thread()

            # Start optimization loop
            await self._start_optimization_loop()

            logger.info("Reinforcement Learning Optimizer initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RL optimizer: {e}")
            raise

    async def _initialize_models(self):
        """Initialize RL models"""
        try:
            # PPO Model
            self.ppo_model = PPO(
                "MlpPolicy",
                self.env,
                learning_rate=self.learning_rate,
                n_steps=2048,
                batch_size=self.batch_size,
                verbose=0,
            )

            # DQN Model
            self.dqn_model = DQN(
                "MlpPolicy",
                self.env,
                learning_rate=self.learning_rate,
                buffer_size=10000,
                batch_size=self.batch_size,
                verbose=0,
            )

            # A2C Model
            self.a2c_model = A2C(
                "MlpPolicy",
                self.env,
                learning_rate=self.learning_rate,
                n_steps=5,
                verbose=0,
            )

            # Set current model
            self.current_model = self.ppo_model

            logger.info("RL models initialized")

        except Exception as e:
            logger.error(f"Failed to initialize RL models: {e}")
            raise

    async def _load_models(self):
        """Load existing trained models"""
        try:
            models_dir = "/app/models/rl"
            os.makedirs(models_dir, exist_ok=True)

            # Load PPO model
            ppo_path = os.path.join(models_dir, "ppo_model.zip")
            if os.path.exists(ppo_path):
                self.ppo_model.load(ppo_path)
                logger.info("PPO model loaded")

            # Load DQN model
            dqn_path = os.path.join(models_dir, "dqn_model.zip")
            if os.path.exists(dqn_path):
                self.dqn_model.load(dqn_path)
                logger.info("DQN model loaded")

            # Load A2C model
            a2c_path = os.path.join(models_dir, "a2c_model.zip")
            if os.path.exists(a2c_path):
                self.a2c_model.load(a2c_path)
                logger.info("A2C model loaded")

        except Exception as e:
            logger.error(f"Failed to load models: {e}")

    async def _start_training_thread(self):
        """Start training thread"""
        try:
            self.training_thread = threading.Thread(target=self._training_worker)
            self.training_thread.daemon = True
            self.training_thread.start()
            self.training_active = True

            logger.info("Training thread started")

        except Exception as e:
            logger.error(f"Failed to start training thread: {e}")

    def _training_worker(self):
        """Training worker thread"""
        while self.training_active:
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

    async def _start_optimization_loop(self):
        """Start optimization loop"""
        try:
            self.optimization_active = True

            # Start optimization task
            optimization_task = asyncio.create_task(self._optimization_loop())

            logger.info("Optimization loop started")

        except Exception as e:
            logger.error(f"Failed to start optimization loop: {e}")

    async def _optimization_loop(self):
        """Main optimization loop"""
        while self.optimization_active:
            try:
                # Get current system state
                current_state = await self._get_current_system_state()

                if current_state:
                    # Make optimization decision
                    action = await self._make_optimization_decision(current_state)

                    if action:
                        # Apply optimization action
                        result = await self._apply_optimization_action(
                            action, current_state
                        )

                        # Store result for learning
                        self.optimization_history.append(result)

                        # Trigger training if needed
                        if len(self.optimization_history) % 100 == 0:
                            self.training_queue.put("train")

                await asyncio.sleep(30)  # Optimize every 30 seconds

            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                await asyncio.sleep(60)

    async def _get_current_system_state(self) -> Optional[SystemState]:
        """Get current system state"""
        try:
            # In production, this would collect real system metrics
            # For now, we'll simulate the state

            current_state = SystemState(
                timestamp=datetime.utcnow(),
                cpu_usage=random.uniform(30, 80),
                memory_usage=random.uniform(40, 85),
                disk_usage=random.uniform(20, 70),
                network_io=random.uniform(1000, 6000),
                response_time=random.uniform(0.5, 4.0),
                throughput=random.uniform(50, 200),
                error_rate=random.uniform(0.001, 0.08),
                active_connections=random.randint(10, 150),
                queue_size=random.randint(0, 100),
                cache_hit_rate=random.uniform(0.6, 0.98),
                availability=random.uniform(90, 100),
                cost=random.uniform(100, 800),
            )

            self.current_state = current_state
            return current_state

        except Exception as e:
            logger.error(f"Failed to get current system state: {e}")
            return None

    async def _make_optimization_decision(
        self, state: SystemState
    ) -> Optional[OptimizationAction]:
        """Make optimization decision using RL model"""
        try:
            if not self.current_model:
                return None

            # Convert state to observation
            observation = self.env._state_to_observation(state)

            # Get action from model
            action, _ = self.current_model.predict(observation, deterministic=True)

            # Convert action to optimization action
            action_type = list(ActionType)[action[0]]

            # Calculate confidence based on model uncertainty
            confidence = random.uniform(
                0.6, 0.95
            )  # In production, use model uncertainty

            # Estimate expected impact
            expected_impact = self._estimate_action_impact(action_type, state)

            # Determine risk level
            risk_level = self._assess_action_risk(action_type, state)

            optimization_action = OptimizationAction(
                action_type=action_type,
                parameters=self._get_action_parameters(action_type),
                confidence=confidence,
                expected_impact=expected_impact,
                risk_level=risk_level,
            )

            self.last_action = optimization_action
            return optimization_action

        except Exception as e:
            logger.error(f"Failed to make optimization decision: {e}")
            return None

    async def _apply_optimization_action(
        self, action: OptimizationAction, state: SystemState
    ) -> OptimizationResult:
        """Apply optimization action and measure results"""
        try:
            # Simulate action application
            # In production, this would actually apply the optimization

            # Simulate new state after action
            new_state = self._simulate_action_effect(action, state)

            # Calculate reward
            reward = self._calculate_optimization_reward(state, new_state, action)

            # Measure metrics improvement
            metrics_improvement = self._calculate_metrics_improvement(state, new_state)

            # Determine success
            success = reward > 0 and self._is_performance_acceptable(new_state)

            result = OptimizationResult(
                action=action,
                reward=reward,
                new_state=new_state,
                success=success,
                metrics_improvement=metrics_improvement,
            )

            # Store training data
            self.training_data.append(
                {
                    "state": self.env._state_to_observation(state),
                    "action": list(ActionType).index(action.action_type),
                    "reward": reward,
                    "new_state": self.env._state_to_observation(new_state),
                    "done": False,
                }
            )

            logger.info(
                f"Applied optimization action: {action.action_type.value}, reward: {reward:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to apply optimization action: {e}")
            return OptimizationResult(
                action=action,
                reward=-10,
                new_state=state,
                success=False,
                metrics_improvement={},
            )

    def _simulate_action_effect(
        self, action: OptimizationAction, state: SystemState
    ) -> SystemState:
        """Simulate the effect of an action on system state"""
        try:
            effects = self.env.action_effects.get(action.action_type, {})

            # Apply effects with some randomness
            new_state = SystemState(
                timestamp=datetime.utcnow(),
                cpu_usage=max(
                    0,
                    min(
                        100,
                        state.cpu_usage
                        + effects.get("cpu_usage", 0)
                        + random.uniform(-2, 2),
                    ),
                ),
                memory_usage=max(
                    0,
                    min(
                        100,
                        state.memory_usage
                        + effects.get("memory_usage", 0)
                        + random.uniform(-2, 2),
                    ),
                ),
                disk_usage=state.disk_usage,
                network_io=max(
                    0,
                    state.network_io
                    + effects.get("network_io", 0)
                    + random.uniform(-100, 100),
                ),
                response_time=max(
                    0.1,
                    state.response_time
                    + effects.get("response_time", 0)
                    + random.uniform(-0.1, 0.1),
                ),
                throughput=max(
                    0,
                    state.throughput
                    + effects.get("throughput", 0)
                    + random.uniform(-5, 5),
                ),
                error_rate=max(
                    0,
                    min(
                        1,
                        state.error_rate
                        + effects.get("error_rate", 0)
                        + random.uniform(-0.001, 0.001),
                    ),
                ),
                active_connections=state.active_connections,
                queue_size=state.queue_size,
                cache_hit_rate=max(
                    0,
                    min(
                        1,
                        state.cache_hit_rate
                        + effects.get("cache_hit_rate", 0)
                        + random.uniform(-0.01, 0.01),
                    ),
                ),
                availability=max(
                    0,
                    min(
                        100,
                        state.availability
                        + effects.get("availability", 0)
                        + random.uniform(-1, 1),
                    ),
                ),
                cost=max(
                    0, state.cost + effects.get("cost", 0) + random.uniform(-10, 10)
                ),
            )

            return new_state

        except Exception as e:
            logger.error(f"Failed to simulate action effect: {e}")
            return state

    def _calculate_optimization_reward(
        self, old_state: SystemState, new_state: SystemState, action: OptimizationAction
    ) -> float:
        """Calculate reward for optimization action"""
        try:
            reward = 0

            # Response time improvement
            if new_state.response_time < old_state.response_time:
                reward += 20 * (old_state.response_time - new_state.response_time)
            else:
                reward -= 10 * (new_state.response_time - old_state.response_time)

            # Throughput improvement
            if new_state.throughput > old_state.throughput:
                reward += 0.2 * (new_state.throughput - old_state.throughput)
            else:
                reward -= 0.1 * (old_state.throughput - new_state.throughput)

            # Resource usage optimization
            cpu_improvement = old_state.cpu_usage - new_state.cpu_usage
            memory_improvement = old_state.memory_usage - new_state.memory_usage

            reward += 3 * cpu_improvement + 3 * memory_improvement

            # Error rate reduction
            error_improvement = old_state.error_rate - new_state.error_rate
            reward += 200 * error_improvement

            # Cost optimization
            cost_improvement = old_state.cost - new_state.cost
            reward += 0.02 * cost_improvement

            # Availability maintenance
            if new_state.availability >= 99:
                reward += 10
            elif new_state.availability < 95:
                reward -= 30

            # Penalty for risky actions
            if action.risk_level == "high":
                reward -= 5
            elif action.risk_level == "medium":
                reward -= 2

            return reward

        except Exception as e:
            logger.error(f"Failed to calculate optimization reward: {e}")
            return 0

    def _calculate_metrics_improvement(
        self, old_state: SystemState, new_state: SystemState
    ) -> Dict[str, float]:
        """Calculate metrics improvement"""
        try:
            return {
                "response_time": old_state.response_time - new_state.response_time,
                "throughput": new_state.throughput - old_state.throughput,
                "cpu_usage": old_state.cpu_usage - new_state.cpu_usage,
                "memory_usage": old_state.memory_usage - new_state.memory_usage,
                "error_rate": old_state.error_rate - new_state.error_rate,
                "cost": old_state.cost - new_state.cost,
                "availability": new_state.availability - old_state.availability,
            }

        except Exception as e:
            logger.error(f"Failed to calculate metrics improvement: {e}")
            return {}

    def _is_performance_acceptable(self, state: SystemState) -> bool:
        """Check if performance is acceptable"""
        try:
            return (
                state.response_time <= self.performance_thresholds["response_time"]
                and state.throughput >= self.performance_thresholds["throughput"]
                and state.cpu_usage <= self.performance_thresholds["cpu_usage"]
                and state.memory_usage <= self.performance_thresholds["memory_usage"]
                and state.error_rate <= self.performance_thresholds["error_rate"]
                and state.availability >= 95
            )

        except Exception as e:
            logger.error(f"Failed to check performance acceptability: {e}")
            return False

    def _estimate_action_impact(
        self, action_type: ActionType, state: SystemState
    ) -> float:
        """Estimate the impact of an action"""
        try:
            effects = self.env.action_effects.get(action_type, {})

            # Calculate weighted impact
            impact = 0
            impact += (
                effects.get("response_time", 0) * -10
            )  # Negative response time is good
            impact += effects.get("throughput", 0) * 0.1
            impact += effects.get("cpu_usage", 0) * -2
            impact += effects.get("memory_usage", 0) * -2
            impact += effects.get("error_rate", 0) * -100
            impact += effects.get("cost", 0) * -0.01

            return impact

        except Exception as e:
            logger.error(f"Failed to estimate action impact: {e}")
            return 0

    def _assess_action_risk(self, action_type: ActionType, state: SystemState) -> str:
        """Assess the risk level of an action"""
        try:
            # High risk actions
            if action_type in [ActionType.SCALE_DOWN, ActionType.DISABLE_FEATURES]:
                return "high"

            # Medium risk actions
            elif action_type in [
                ActionType.MODIFY_LOAD_BALANCING,
                ActionType.ADJUST_TIMEOUTS,
            ]:
                return "medium"

            # Low risk actions
            else:
                return "low"

        except Exception as e:
            logger.error(f"Failed to assess action risk: {e}")
            return "medium"

    def _get_action_parameters(self, action_type: ActionType) -> Dict[str, Any]:
        """Get parameters for an action"""
        try:
            parameters = {}

            if action_type == ActionType.SCALE_UP:
                parameters = {
                    "instances": 2,
                    "cpu_limit": "1000m",
                    "memory_limit": "2Gi",
                }
            elif action_type == ActionType.SCALE_DOWN:
                parameters = {
                    "instances": 1,
                    "cpu_limit": "500m",
                    "memory_limit": "1Gi",
                }
            elif action_type == ActionType.ADJUST_CACHE:
                parameters = {"ttl": 3600, "max_size": "1GB", "eviction_policy": "lru"}
            elif action_type == ActionType.MODIFY_LOAD_BALANCING:
                parameters = {"algorithm": "round_robin", "weight": 1.0}
            elif action_type == ActionType.OPTIMIZE_QUERIES:
                parameters = {"timeout": 30, "batch_size": 100, "index_hints": True}
            elif action_type == ActionType.ADJUST_TIMEOUTS:
                parameters = {
                    "read_timeout": 30,
                    "write_timeout": 60,
                    "connection_timeout": 10,
                }
            elif action_type == ActionType.ENABLE_COMPRESSION:
                parameters = {"algorithm": "gzip", "level": 6, "min_size": 1024}
            elif action_type == ActionType.DISABLE_FEATURES:
                parameters = {
                    "features": ["debug_mode", "verbose_logging"],
                    "graceful": True,
                }

            return parameters

        except Exception as e:
            logger.error(f"Failed to get action parameters: {e}")
            return {}

    async def _train_models(self):
        """Train RL models"""
        try:
            if len(self.training_data) < 100:
                logger.info("Insufficient training data")
                return

            logger.info("Starting model training...")

            # Convert training data to format expected by models
            training_data = list(self.training_data)

            # Train PPO model
            if self.ppo_model:
                self.ppo_model.learn(total_timesteps=10000)
                self.ppo_model.save("/app/models/rl/ppo_model")
                logger.info("PPO model trained")

            # Train DQN model
            if self.dqn_model:
                self.dqn_model.learn(total_timesteps=10000)
                self.dqn_model.save("/app/models/rl/dqn_model")
                logger.info("DQN model trained")

            # Train A2C model
            if self.a2c_model:
                self.a2c_model.learn(total_timesteps=10000)
                self.a2c_model.save("/app/models/rl/a2c_model")
                logger.info("A2C model trained")

            # Update epsilon for exploration
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

            logger.info("Model training completed")

        except Exception as e:
            logger.error(f"Failed to train models: {e}")

    async def get_optimization_status(self) -> Dict[str, Any]:
        """Get optimization status"""
        try:
            return {
                "optimization_active": self.optimization_active,
                "current_model": (
                    "PPO"
                    if self.current_model == self.ppo_model
                    else "DQN" if self.current_model == self.dqn_model else "A2C"
                ),
                "training_data_size": len(self.training_data),
                "optimization_history_size": len(self.optimization_history),
                "epsilon": self.epsilon,
                "current_state": (
                    {
                        "cpu_usage": (
                            self.current_state.cpu_usage if self.current_state else 0
                        ),
                        "memory_usage": (
                            self.current_state.memory_usage if self.current_state else 0
                        ),
                        "response_time": (
                            self.current_state.response_time
                            if self.current_state
                            else 0
                        ),
                        "throughput": (
                            self.current_state.throughput if self.current_state else 0
                        ),
                        "error_rate": (
                            self.current_state.error_rate if self.current_state else 0
                        ),
                        "availability": (
                            self.current_state.availability if self.current_state else 0
                        ),
                    }
                    if self.current_state
                    else None
                ),
                "last_action": (
                    {
                        "action_type": (
                            self.last_action.action_type.value
                            if self.last_action
                            else None
                        ),
                        "confidence": (
                            self.last_action.confidence if self.last_action else 0
                        ),
                        "expected_impact": (
                            self.last_action.expected_impact if self.last_action else 0
                        ),
                        "risk_level": (
                            self.last_action.risk_level if self.last_action else None
                        ),
                    }
                    if self.last_action
                    else None
                ),
                "performance_thresholds": self.performance_thresholds,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get optimization status: {e}")
            return {"error": str(e)}

    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        try:
            recommendations = []

            if not self.current_state:
                return recommendations

            # Analyze current state and generate recommendations
            if (
                self.current_state.response_time
                > self.performance_thresholds["response_time"]
            ):
                recommendations.append(
                    {
                        "type": "response_time",
                        "priority": "high",
                        "action": "Scale up resources or optimize queries",
                        "expected_improvement": "20-30% response time reduction",
                    }
                )

            if self.current_state.cpu_usage > self.performance_thresholds["cpu_usage"]:
                recommendations.append(
                    {
                        "type": "cpu_usage",
                        "priority": "high",
                        "action": "Scale up or optimize CPU-intensive operations",
                        "expected_improvement": "15-25% CPU usage reduction",
                    }
                )

            if (
                self.current_state.memory_usage
                > self.performance_thresholds["memory_usage"]
            ):
                recommendations.append(
                    {
                        "type": "memory_usage",
                        "priority": "medium",
                        "action": "Optimize memory usage or scale up",
                        "expected_improvement": "10-20% memory usage reduction",
                    }
                )

            if (
                self.current_state.error_rate
                > self.performance_thresholds["error_rate"]
            ):
                recommendations.append(
                    {
                        "type": "error_rate",
                        "priority": "critical",
                        "action": "Investigate and fix error sources",
                        "expected_improvement": "50-80% error rate reduction",
                    }
                )

            if self.current_state.availability < 95:
                recommendations.append(
                    {
                        "type": "availability",
                        "priority": "critical",
                        "action": "Check system health and implement redundancy",
                        "expected_improvement": "5-10% availability increase",
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {e}")
            return []

    async def shutdown(self):
        """Shutdown RL optimizer"""
        try:
            logger.info("Shutting down Reinforcement Learning Optimizer...")

            # Stop optimization
            self.optimization_active = False

            # Stop training
            self.training_active = False
            if self.training_thread:
                self.training_queue.put(None)
                self.training_thread.join(timeout=10)

            # Save models
            await self._save_models()

            logger.info("Reinforcement Learning Optimizer shutdown complete")

        except Exception as e:
            logger.error(f"Error during RL optimizer shutdown: {e}")

    async def _save_models(self):
        """Save trained models"""
        try:
            models_dir = "/app/models/rl"
            os.makedirs(models_dir, exist_ok=True)

            # Save models
            if self.ppo_model:
                self.ppo_model.save(os.path.join(models_dir, "ppo_model"))

            if self.dqn_model:
                self.dqn_model.save(os.path.join(models_dir, "dqn_model"))

            if self.a2c_model:
                self.a2c_model.save(os.path.join(models_dir, "a2c_model"))

            # Save training data
            training_data_path = os.path.join(models_dir, "training_data.pkl")
            with open(training_data_path, "wb") as f:
                pickle.dump(list(self.training_data), f)

            logger.info("Models saved successfully")

        except Exception as e:
            logger.error(f"Failed to save models: {e}")
